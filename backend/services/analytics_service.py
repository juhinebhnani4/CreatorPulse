"""
Analytics Service - Track and calculate email engagement metrics.

This service handles:
- Recording analytics events (sent, opened, clicked, bounced, etc.)
- Calculating newsletter metrics (open rate, CTR, engagement score)
- Aggregating workspace analytics
- Content performance tracking
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from uuid import UUID

from backend.database import get_supabase_client, get_supabase_service_client
from backend.config import settings


class AnalyticsService:
    """Service for tracking and analyzing email engagement."""

    def __init__(self):
        # Use service client to bypass RLS for analytics operations
        self.supabase = get_supabase_service_client()

    async def record_event(
        self,
        workspace_id: UUID,
        newsletter_id: UUID,
        event_type: str,
        recipient_email: str,
        subscriber_id: Optional[UUID] = None,
        clicked_url: Optional[str] = None,
        content_item_id: Optional[UUID] = None,
        bounce_type: Optional[str] = None,
        bounce_reason: Optional[str] = None,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> Dict:
        """
        Record an analytics event.

        Args:
            workspace_id: Workspace UUID
            newsletter_id: Newsletter UUID
            event_type: Event type ('sent', 'opened', 'clicked', 'bounced', 'unsubscribed')
            recipient_email: Recipient email address
            subscriber_id: Subscriber UUID (optional)
            clicked_url: URL clicked (for 'clicked' events)
            content_item_id: Content item UUID (for 'clicked' events)
            bounce_type: Bounce type ('hard' or 'soft' for 'bounced' events)
            bounce_reason: Reason for bounce (for 'bounced' events)
            user_agent: User agent string
            ip_address: IP address (anonymized for privacy)

        Returns:
            Created event record
        """
        # Parse location from IP if available
        location_data = await self._get_location_from_ip(ip_address) if ip_address else {}

        # Detect device type and email client from user agent
        device_data = self._parse_user_agent(user_agent) if user_agent else {}

        # Anonymize IP for privacy (mask last octet)
        anonymized_ip = self._anonymize_ip(ip_address) if ip_address else None

        event_data = {
            "workspace_id": str(workspace_id),
            "newsletter_id": str(newsletter_id),
            "subscriber_id": str(subscriber_id) if subscriber_id else None,
            "event_type": event_type,
            "event_time": datetime.utcnow().isoformat(),
            "recipient_email": recipient_email,
            "clicked_url": clicked_url,
            "content_item_id": str(content_item_id) if content_item_id else None,
            "bounce_type": bounce_type,
            "bounce_reason": bounce_reason,
            "user_agent": user_agent,
            "ip_address": anonymized_ip,
            "location_city": location_data.get("city"),
            "location_country": location_data.get("country"),
            "device_type": device_data.get("device_type"),
            "email_client": device_data.get("email_client"),
        }

        # Insert event (trigger will update summary automatically)
        response = self.supabase.table("email_analytics_events").insert(event_data).execute()

        if response.data:
            return response.data[0]
        else:
            raise Exception(f"Failed to record analytics event: {response}")

    async def get_newsletter_analytics(self, newsletter_id: UUID) -> Optional[Dict]:
        """
        Get analytics summary for a specific newsletter.

        Args:
            newsletter_id: Newsletter UUID

        Returns:
            Analytics summary with metrics
        """
        # Get summary from database
        response = (
            self.supabase.table("newsletter_analytics_summary")
            .select("*")
            .eq("newsletter_id", str(newsletter_id))
            .single()
            .execute()
        )

        if not response.data:
            return None

        summary = response.data

        # Get detailed events for additional insights
        events_response = (
            self.supabase.table("email_analytics_events")
            .select("*")
            .eq("newsletter_id", str(newsletter_id))
            .execute()
        )

        events = events_response.data if events_response.data else []

        # Get top clicked links
        top_links = await self._get_top_clicked_links(newsletter_id)

        # Format response
        return {
            "newsletter_id": summary["newsletter_id"],
            "workspace_id": summary["workspace_id"],
            "metrics": {
                "sent_count": summary["sent_count"],
                "delivered_count": summary["delivered_count"],
                "bounced_count": summary["bounced_count"],
                "hard_bounces": summary["hard_bounces"],
                "soft_bounces": summary["soft_bounces"],
                "opened_count": summary["opened_count"],
                "unique_opens": summary["unique_opens"],
                "clicked_count": summary["clicked_count"],
                "unique_clicks": summary["unique_clicks"],
                "unsubscribed_count": summary["unsubscribed_count"],
                "spam_reported_count": summary["spam_reported_count"],
            },
            "rates": {
                "delivery_rate": float(summary["delivery_rate"]),
                "open_rate": float(summary["open_rate"]),
                "click_rate": float(summary["click_rate"]),
                "click_to_open_rate": float(summary["click_to_open_rate"]),
                "bounce_rate": float(summary["bounce_rate"]),
                "unsubscribe_rate": float(summary["unsubscribe_rate"]),
            },
            "engagement_score": float(summary["engagement_score"]),
            "timing": {
                "avg_time_to_open_seconds": summary["avg_time_to_open_seconds"],
                "avg_time_to_click_seconds": summary["avg_time_to_click_seconds"],
                "peak_open_hour": summary["peak_open_hour"],
                "peak_click_hour": summary["peak_click_hour"],
            },
            "top_links": top_links,
            "total_events": len(events),
            "last_calculated_at": summary["last_calculated_at"],
        }

    async def get_workspace_analytics(
        self,
        workspace_id: UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict:
        """
        Get aggregate analytics for a workspace.

        Args:
            workspace_id: Workspace UUID
            start_date: Start date for filtering (default: 30 days ago)
            end_date: End date for filtering (default: now)

        Returns:
            Aggregate metrics and trends
        """
        # Default date range: last 30 days
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=30)
        if not end_date:
            end_date = datetime.utcnow()

        # Call database function for aggregate analytics
        response = (
            self.supabase.rpc(
                "get_workspace_analytics_summary",
                {
                    "workspace_uuid": str(workspace_id),
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                },
            )
            .execute()
        )

        if response.data:
            return response.data
        else:
            # Fallback: calculate manually if function not available
            return await self._calculate_workspace_analytics_manual(
                workspace_id, start_date, end_date
            )

    async def get_content_performance(
        self, workspace_id: UUID, limit: int = 20
    ) -> List[Dict]:
        """
        Get top performing content items.

        Args:
            workspace_id: Workspace UUID
            limit: Number of items to return

        Returns:
            List of content items with performance metrics
        """
        response = (
            self.supabase.table("content_performance")
            .select("*, content_items(id, title, source, source_url)")
            .eq("workspace_id", str(workspace_id))
            .order("engagement_score", desc=True)
            .limit(limit)
            .execute()
        )

        if not response.data:
            return []

        # Format results
        results = []
        for item in response.data:
            results.append({
                "content_item_id": item["content_item_id"],
                "title": item["content_items"]["title"] if item.get("content_items") else None,
                "source": item["content_items"]["source"] if item.get("content_items") else None,
                "source_url": item["content_items"]["source_url"] if item.get("content_items") else None,
                "times_included": item["times_included"],
                "times_clicked": item["times_clicked"],
                "unique_clickers": item["unique_clickers"],
                "avg_click_rate": float(item["avg_click_rate"]),
                "engagement_score": float(item["engagement_score"]),
                "first_included_at": item["first_included_at"],
                "last_included_at": item["last_included_at"],
            })

        return results

    async def export_analytics_data(
        self,
        workspace_id: UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        format: str = "csv",
    ) -> Tuple[List[Dict], str]:
        """
        Export analytics data for a workspace.

        Args:
            workspace_id: Workspace UUID
            start_date: Start date for filtering
            end_date: End date for filtering
            format: Export format ('csv' or 'json')

        Returns:
            Tuple of (data, content_type)
        """
        # Default date range: all time
        query = (
            self.supabase.table("email_analytics_events")
            .select("*")
            .eq("workspace_id", str(workspace_id))
        )

        if start_date:
            query = query.gte("event_time", start_date.isoformat())
        if end_date:
            query = query.lte("event_time", end_date.isoformat())

        response = query.order("event_time", desc=True).execute()

        if not response.data:
            return [], "text/csv" if format == "csv" else "application/json"

        events = response.data

        if format == "json":
            return events, "application/json"
        else:  # csv
            return events, "text/csv"

    async def recalculate_summary(self, newsletter_id: UUID) -> None:
        """
        Recalculate analytics summary for a newsletter.

        This is useful if data becomes inconsistent or needs to be reprocessed.

        Args:
            newsletter_id: Newsletter UUID
        """
        # Call database function to recalculate
        self.supabase.rpc(
            "recalculate_newsletter_analytics", {"newsletter_uuid": str(newsletter_id)}
        ).execute()

    # =============================================================================
    # PRIVATE HELPER METHODS
    # =============================================================================

    async def _get_top_clicked_links(self, newsletter_id: UUID, limit: int = 10) -> List[Dict]:
        """Get top clicked links for a newsletter."""
        response = (
            self.supabase.table("email_analytics_events")
            .select("clicked_url, content_item_id")
            .eq("newsletter_id", str(newsletter_id))
            .eq("event_type", "clicked")
            .execute()
        )

        if not response.data:
            return []

        # Count clicks per URL
        click_counts = {}
        for event in response.data:
            url = event["clicked_url"]
            if url:
                if url not in click_counts:
                    click_counts[url] = {
                        "url": url,
                        "content_item_id": event["content_item_id"],
                        "clicks": 0,
                        "unique_clicks": set(),
                    }
                click_counts[url]["clicks"] += 1

        # Sort by click count
        sorted_links = sorted(
            click_counts.values(), key=lambda x: x["clicks"], reverse=True
        )[:limit]

        # Format results
        return [
            {
                "url": link["url"],
                "content_item_id": link["content_item_id"],
                "clicks": link["clicks"],
            }
            for link in sorted_links
        ]

    async def _calculate_workspace_analytics_manual(
        self, workspace_id: UUID, start_date: datetime, end_date: datetime
    ) -> Dict:
        """Manually calculate workspace analytics (fallback)."""
        # Get all events in date range
        response = (
            self.supabase.table("email_analytics_events")
            .select("*")
            .eq("workspace_id", str(workspace_id))
            .gte("event_time", start_date.isoformat())
            .lte("event_time", end_date.isoformat())
            .execute()
        )

        events = response.data if response.data else []

        # Count by event type
        event_counts = {"sent": 0, "opened": 0, "clicked": 0, "bounced": 0}
        unique_opens = set()
        unique_clicks = set()
        newsletters = set()

        for event in events:
            event_type = event["event_type"]
            if event_type in event_counts:
                event_counts[event_type] += 1

            newsletters.add(event["newsletter_id"])

            if event_type == "opened":
                unique_opens.add((event["newsletter_id"], event["recipient_email"]))
            elif event_type == "clicked":
                unique_clicks.add((event["newsletter_id"], event["recipient_email"]))

        # Calculate rates
        delivered = event_counts["sent"] - event_counts["bounced"]
        open_rate = len(unique_opens) / delivered if delivered > 0 else 0
        click_rate = len(unique_clicks) / delivered if delivered > 0 else 0

        return {
            "workspace_id": str(workspace_id),
            "date_range": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
            },
            "total_newsletters": len(newsletters),
            "total_sent": event_counts["sent"],
            "total_delivered": delivered,
            "total_opened": len(unique_opens),
            "total_clicked": len(unique_clicks),
            "avg_open_rate": open_rate,
            "avg_click_rate": click_rate,
        }

    async def _get_location_from_ip(self, ip_address: str) -> Dict[str, str]:
        """
        Get location from IP address using ipapi.co.

        Args:
            ip_address: IP address

        Returns:
            Dict with city and country
        """
        # TODO: Implement IP geolocation using ipapi.co or similar service
        # For now, return empty dict
        return {"city": None, "country": None}

    def _parse_user_agent(self, user_agent: str) -> Dict[str, str]:
        """
        Parse user agent to detect device type and email client.

        Args:
            user_agent: User agent string

        Returns:
            Dict with device_type and email_client
        """
        user_agent_lower = user_agent.lower()

        # Detect device type
        if "mobile" in user_agent_lower or "android" in user_agent_lower:
            device_type = "mobile"
        elif "tablet" in user_agent_lower or "ipad" in user_agent_lower:
            device_type = "tablet"
        else:
            device_type = "desktop"

        # Detect email client
        email_client = "Unknown"
        if "gmail" in user_agent_lower:
            email_client = "Gmail"
        elif "outlook" in user_agent_lower or "microsoft" in user_agent_lower:
            email_client = "Outlook"
        elif "apple mail" in user_agent_lower or "webkit" in user_agent_lower:
            email_client = "Apple Mail"
        elif "thunderbird" in user_agent_lower:
            email_client = "Thunderbird"
        elif "yahoo" in user_agent_lower:
            email_client = "Yahoo Mail"

        return {"device_type": device_type, "email_client": email_client}

    def _anonymize_ip(self, ip_address: str) -> str:
        """
        Anonymize IP address for privacy (GDPR compliance).

        Masks the last octet for IPv4, last 80 bits for IPv6.

        Args:
            ip_address: Original IP address

        Returns:
            Anonymized IP address
        """
        if ":" in ip_address:  # IPv6
            parts = ip_address.split(":")
            return ":".join(parts[:4]) + ":0:0:0:0"
        else:  # IPv4
            parts = ip_address.split(".")
            return ".".join(parts[:3]) + ".0"
