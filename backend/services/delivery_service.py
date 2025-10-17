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


class DeliveryService:
    """Service for newsletter delivery operations."""

    def __init__(self):
        """Initialize delivery service."""
        self._db = None
        self._email_sender = None

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
                total_subscribers=len(subscribers)
            )

            # Update delivery status to sending
            self.db.update_delivery(delivery['id'], {
                'status': 'sending'
            })

            # Send to all subscribers
            sent_count = 0
            failed_count = 0
            errors = []

            for subscriber in subscribers:
                try:
                    success = self.email_sender.send_newsletter(
                        to_email=subscriber['email'],
                        subject=newsletter['title'],
                        html_content=newsletter['html_content'],
                        text_content=newsletter.get('plain_text_content')
                    )

                    if success:
                        sent_count += 1
                        # Update subscriber last_sent_at
                        self.db.update_subscriber(subscriber['id'], {
                            'last_sent_at': datetime.now().isoformat()
                        })
                    else:
                        failed_count += 1
                        errors.append(f"Failed to send to {subscriber['email']}")

                except Exception as e:
                    failed_count += 1
                    error_msg = f"Error sending to {subscriber['email']}: {str(e)}"
                    errors.append(error_msg)

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
        Send newsletter to test email.

        Args:
            newsletter: Newsletter data
            test_email: Test email address

        Returns:
            Test send result
        """
        try:
            success = self.email_sender.send_newsletter(
                to_email=test_email,
                subject=f"[TEST] {newsletter['title']}",
                html_content=newsletter['html_content'],
                text_content=newsletter.get('plain_text_content')
            )

            if success:
                return {
                    'delivery_id': None,
                    'newsletter_id': newsletter['id'],
                    'total_subscribers': 1,
                    'sent_count': 1,
                    'failed_count': 0,
                    'status': 'completed',
                    'test_mode': True,
                    'test_email': test_email
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
            deliveries = self.db.list_deliveries(
                workspace_id=workspace_id,
                limit=limit
            )

            return deliveries

        except Exception as e:
            raise Exception(f"Failed to list deliveries: {str(e)}")


# Global service instance
delivery_service = DeliveryService()
