"""
Delivery service - handles newsletter sending to subscribers.
Integrates with existing EmailSender and SupabaseManager.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import sys
from pathlib import Path

# Add src to path to import existing modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from ai_newsletter.database.supabase_client import SupabaseManager
from ai_newsletter.delivery.email_sender import EmailSender
from ai_newsletter.config.settings import get_settings
from backend.services.tracking_service import TrackingService
from backend.services.analytics_service import AnalyticsService


class DeliveryService:
    """Service for newsletter delivery operations."""

    def __init__(self):
        """Initialize delivery service."""
        self._db = None
        self._email_sender = None
        self._tracking_service = None
        self._analytics_service = None

    @property
    def db(self):
        """Lazy-load SupabaseManager."""
        if self._db is None:
            self._db = SupabaseManager()
        return self._db

    @property
    def email_sender(self):
        """Lazy-load EmailSender."""
        if self._email_sender is None:
            settings = get_settings()
            self._email_sender = EmailSender(config=settings.email)
        return self._email_sender

    @property
    def tracking_service(self):
        """Lazy-load TrackingService."""
        if self._tracking_service is None:
            self._tracking_service = TrackingService()
        return self._tracking_service

    @property
    def analytics_service(self):
        """Lazy-load AnalyticsService."""
        if self._analytics_service is None:
            self._analytics_service = AnalyticsService()
        return self._analytics_service

    async def send_newsletter(
        self,
        user_id: str,
        newsletter_id: str,
        workspace_id: str,
        test_email: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send newsletter to subscribers.

        Args:
            user_id: User ID (for permission check)
            newsletter_id: Newsletter ID to send
            workspace_id: Workspace ID
            test_email: If provided, send only to this test email

        Returns:
            Delivery status dictionary

        Raises:
            Exception: If send fails
        """
        try:
            # Verify user has access to workspace
            if not self.db.user_has_workspace_access(user_id, workspace_id):
                raise Exception("Access denied: User not in workspace")

            # Get newsletter
            newsletter = self.db.get_newsletter(newsletter_id)
            if not newsletter:
                raise Exception("Newsletter not found")

            # Verify newsletter belongs to workspace
            if newsletter['workspace_id'] != workspace_id:
                raise Exception("Newsletter does not belong to workspace")

            # If test email, send only to that
            if test_email:
                return await self._send_test_newsletter(
                    newsletter=newsletter,
                    test_email=test_email
                )

            # Get active subscribers
            subscribers = self.db.list_subscribers(
                workspace_id=workspace_id,
                status='active'
            )

            if not subscribers:
                raise Exception("No active subscribers found")

            # Create delivery record
            delivery = self.db.create_delivery(
                newsletter_id=newsletter_id,
                workspace_id=workspace_id,
                total_subscribers=len(subscribers),
                started_at=datetime.now().isoformat()
            )

            # Update delivery status to sending
            self.db.update_delivery(delivery['id'], {
                'status': 'sending'
            })

            # Send to all subscribers
            sent_count = 0
            failed_count = 0
            errors = []

            for i, subscriber in enumerate(subscribers, 1):
                try:
                    print(f"\n📨 Sending to subscriber {i}/{len(subscribers)}: {subscriber['email']}")

                    # Add tracking pixel and click tracking to HTML (personalized per recipient)
                    print(f"   → Adding tracking to HTML...")
                    tracked_html = self.tracking_service.add_tracking_to_html(
                        html_content=newsletter['content_html'],
                        newsletter_id=newsletter_id,
                        recipient_email=subscriber['email'],
                        workspace_id=workspace_id,
                        content_items=newsletter.get('content_items', [])
                    )

                    # Add unsubscribe link (CAN-SPAM compliance)
                    print(f"   → Adding unsubscribe link...")
                    tracked_html = self.tracking_service.add_unsubscribe_link(
                        html_content=tracked_html,
                        workspace_id=workspace_id,
                        recipient_email=subscriber['email']
                    )

                    # Note: List-Unsubscribe headers will be added in future EmailSender enhancement
                    # For now, unsubscribe link in footer is sufficient for CAN-SPAM compliance

                    # Send email with tracked HTML
                    print(f"   → Calling email_sender.send_newsletter()...")
                    success = self.email_sender.send_newsletter(
                        to_email=subscriber['email'],
                        subject=newsletter.get('subject_line') or newsletter['title'],
                        html_content=tracked_html,
                        text_content=newsletter.get('content_text')
                    )

                    if success:
                        print(f"   ✅ Email sent successfully to {subscriber['email']}")

                        # Record 'sent' event in analytics
                        await self.analytics_service.record_event(
                            workspace_id=workspace_id,
                            newsletter_id=newsletter_id,
                            event_type='sent',
                            recipient_email=subscriber['email'],
                            subscriber_id=subscriber.get('id')
                        )

                        # Record 'delivered' event (assume immediate delivery for SMTP)
                        # Note: For SendGrid, this should come from webhook
                        await self.analytics_service.record_event(
                            workspace_id=workspace_id,
                            newsletter_id=newsletter_id,
                            event_type='delivered',
                            recipient_email=subscriber['email'],
                            subscriber_id=subscriber.get('id')
                        )

                        sent_count += 1
                        # Update subscriber last_sent_at
                        self.db.update_subscriber(subscriber['id'], {
                            'last_sent_at': datetime.now().isoformat()
                        })
                    else:
                        print(f"   ❌ email_sender.send_newsletter() returned False for {subscriber['email']}")
                        failed_count += 1
                        errors.append(f"Failed to send to {subscriber['email']}: SMTP returned False")

                except Exception as e:
                    failed_count += 1
                    error_msg = f"Error sending to {subscriber['email']}: {str(e)}"
                    errors.append(error_msg)
                    print(f"   ❌ Exception: {error_msg}")
                    import traceback
                    traceback.print_exc()

            # Update delivery record
            self.db.update_delivery(delivery['id'], {
                'sent_count': sent_count,
                'failed_count': failed_count,
                'status': 'completed' if failed_count == 0 else 'failed',
                'completed_at': datetime.now().isoformat(),
                'errors': errors
            })

            # Update newsletter status to sent
            if sent_count > 0:
                self.db.update_newsletter(newsletter_id, {
                    'status': 'sent',
                    'sent_at': datetime.now().isoformat()
                })

            return {
                'delivery_id': delivery['id'],
                'newsletter_id': newsletter_id,
                'total_subscribers': len(subscribers),
                'sent_count': sent_count,
                'failed_count': failed_count,
                'status': 'completed' if failed_count == 0 else 'failed',
                'errors': errors[:10]  # Return first 10 errors only
            }

        except Exception as e:
            raise Exception(f"Failed to send newsletter: {str(e)}")

    async def _send_test_newsletter(
        self,
        newsletter: Dict[str, Any],
        test_email: str
    ) -> Dict[str, Any]:
        """
        Send newsletter to test email with tracking enabled.

        Args:
            newsletter: Newsletter data
            test_email: Test email address

        Returns:
            Test send result
        """
        try:
            # Add tracking to test email as well
            tracked_html = self.tracking_service.add_tracking_to_html(
                html_content=newsletter['content_html'],
                newsletter_id=newsletter['id'],
                recipient_email=test_email,
                workspace_id=newsletter['workspace_id'],
                content_items=newsletter.get('content_items', [])
            )

            # Add unsubscribe link
            tracked_html = self.tracking_service.add_unsubscribe_link(
                html_content=tracked_html,
                workspace_id=newsletter['workspace_id'],
                recipient_email=test_email
            )

            # Note: List-Unsubscribe headers will be added in future EmailSender enhancement

            success = self.email_sender.send_newsletter(
                to_email=test_email,
                subject=f"[TEST] {newsletter.get('subject_line') or newsletter['title']}",
                html_content=tracked_html,
                text_content=newsletter.get('content_text')
            )

            if success:
                # Record test send in analytics (marked with test email)
                await self.analytics_service.record_event(
                    workspace_id=newsletter['workspace_id'],
                    newsletter_id=newsletter['id'],
                    event_type='sent',
                    recipient_email=test_email,
                    subscriber_id=None  # Test sends have no subscriber ID
                )

                return {
                    'delivery_id': None,
                    'newsletter_id': newsletter['id'],
                    'total_subscribers': 1,
                    'sent_count': 1,
                    'failed_count': 0,
                    'status': 'completed',
                    'test_mode': True,
                    'test_email': test_email,
                    'tracking_enabled': True
                }
            else:
                raise Exception("Failed to send test email")

        except Exception as e:
            raise Exception(f"Failed to send test newsletter: {str(e)}")

    async def get_delivery_status(
        self,
        user_id: str,
        delivery_id: str
    ) -> Dict[str, Any]:
        """
        Get delivery status.

        Args:
            user_id: User ID (for permission check)
            delivery_id: Delivery ID

        Returns:
            Delivery status dictionary
        """
        try:
            delivery = self.db.get_delivery(delivery_id)
            if not delivery:
                raise Exception("Delivery not found")

            # Verify user has access to delivery's workspace
            if not self.db.user_has_workspace_access(user_id, delivery['workspace_id']):
                raise Exception("Access denied: User not in workspace")

            return delivery

        except Exception as e:
            raise Exception(f"Failed to get delivery status: {str(e)}")

    async def list_deliveries(
        self,
        user_id: str,
        workspace_id: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        List deliveries for workspace.

        Args:
            user_id: User ID (for permission check)
            workspace_id: Workspace ID
            limit: Maximum deliveries to return

        Returns:
            List of delivery data
        """
        try:
            # Verify user has access to workspace
            if not self.db.user_has_workspace_access(user_id, workspace_id):
                raise Exception("Access denied: User not in workspace")

            deliveries = self.db.list_deliveries(
                workspace_id=workspace_id,
                limit=limit
            )

            return deliveries

        except Exception as e:
            raise Exception(f"Failed to list deliveries: {str(e)}")


# Global service instance
delivery_service = DeliveryService()
