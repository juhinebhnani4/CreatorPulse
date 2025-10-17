"""
Historical Content Service

Manages historical content storage for trend velocity calculations.
Implements a 7-day rolling window with automatic cleanup.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from uuid import UUID
from backend.models.trend import HistoricalContentCreate, HistoricalContentResponse
from src.ai_newsletter.database.supabase_client import SupabaseManager


class HistoricalContentService:
    """Service for managing historical content storage."""

    def __init__(self, retention_days: int = 7):
        self.db = SupabaseManager()
        self.retention_days = retention_days

    async def save_content_to_history(
        self,
        workspace_id: UUID,
        content_items: List[Dict[str, Any]]
    ) -> int:
        """
        Save content items to historical storage.

        Args:
            workspace_id: Workspace ID
            content_items: Content items to save

        Returns:
            Number of items saved
        """
        saved_count = 0

        for item in content_items:
            try:
                # Create historical content record
                historical_data = HistoricalContentCreate(
                    workspace_id=workspace_id,
                    content_item_id=UUID(item['id']) if item.get('id') else None,
                    title=item.get('title', ''),
                    summary=item.get('summary'),
                    content=item.get('content'),
                    source=item.get('source', 'unknown'),
                    source_url=item.get('source_url'),
                    score=item.get('score', 0),
                    created_at=self._parse_datetime(item.get('created_at')),
                    keywords=self._extract_simple_keywords(item.get('title', '')),
                    topic_cluster=None  # Will be set by clustering algorithm
                )

                # Save to database
                self.db.create_historical_content(historical_data.model_dump(mode='json'))
                saved_count += 1

            except Exception as e:
                print(f"Error saving historical content: {e}")
                continue

        return saved_count

    async def get_historical_content(
        self,
        workspace_id: UUID,
        days_back: int = 7,
        sources: Optional[List[str]] = None
    ) -> List[HistoricalContentResponse]:
        """
        Get historical content for analysis.

        Args:
            workspace_id: Workspace ID
            days_back: Number of days to retrieve
            sources: Filter by specific sources

        Returns:
            List of historical content
        """
        cutoff_date = datetime.now() - timedelta(days=days_back)

        historical_data = self.db.list_historical_content(
            str(workspace_id),
            start_date=cutoff_date,
            sources=sources
        )

        return [HistoricalContentResponse(**h) for h in historical_data]

    async def cleanup_expired_content(self, workspace_id: Optional[UUID] = None) -> int:
        """
        Remove expired historical content.

        Args:
            workspace_id: Optional workspace ID (None = all workspaces)

        Returns:
            Number of records deleted
        """
        if workspace_id:
            return self.db.cleanup_expired_historical_content(str(workspace_id))
        else:
            return self.db.cleanup_expired_historical_content()

    async def get_content_by_date_range(
        self,
        workspace_id: UUID,
        start_date: datetime,
        end_date: datetime,
        sources: Optional[List[str]] = None
    ) -> List[HistoricalContentResponse]:
        """
        Get historical content for specific date range.

        Args:
            workspace_id: Workspace ID
            start_date: Start of range
            end_date: End of range
            sources: Filter by sources

        Returns:
            List of historical content
        """
        historical_data = self.db.list_historical_content(
            str(workspace_id),
            start_date=start_date,
            end_date=end_date,
            sources=sources
        )

        return [HistoricalContentResponse(**h) for h in historical_data]

    async def get_storage_stats(self, workspace_id: UUID) -> Dict[str, Any]:
        """
        Get storage statistics for workspace.

        Args:
            workspace_id: Workspace ID

        Returns:
            Storage statistics
        """
        # Get all historical content
        all_content = await self.get_historical_content(
            workspace_id,
            days_back=self.retention_days
        )

        # Calculate stats
        total_items = len(all_content)

        # Group by source
        by_source = {}
        for item in all_content:
            source = item.source
            by_source[source] = by_source.get(source, 0) + 1

        # Group by date
        by_date = {}
        for item in all_content:
            date_key = item.created_at.date().isoformat()
            by_date[date_key] = by_date.get(date_key, 0) + 1

        # Calculate age range
        if all_content:
            oldest = min(item.created_at for item in all_content)
            newest = max(item.created_at for item in all_content)
            age_range_days = (newest - oldest).days
        else:
            oldest = None
            newest = None
            age_range_days = 0

        return {
            "total_items": total_items,
            "by_source": by_source,
            "by_date": by_date,
            "oldest_item": oldest.isoformat() if oldest else None,
            "newest_item": newest.isoformat() if newest else None,
            "age_range_days": age_range_days,
            "retention_days": self.retention_days
        }

    def _parse_datetime(self, dt_str: Any) -> datetime:
        """Parse datetime from string or return current time."""
        if isinstance(dt_str, datetime):
            return dt_str
        elif isinstance(dt_str, str):
            try:
                # Handle ISO format with Z
                if dt_str.endswith('Z'):
                    dt_str = dt_str[:-1] + '+00:00'
                return datetime.fromisoformat(dt_str)
            except:
                return datetime.now()
        else:
            return datetime.now()

    def _extract_simple_keywords(self, text: str, max_keywords: int = 5) -> List[str]:
        """
        Extract simple keywords from text.

        Args:
            text: Text to analyze
            max_keywords: Maximum keywords to return

        Returns:
            List of keywords
        """
        # Simple keyword extraction (could enhance with NLP)
        # Remove special characters and lowercase
        import re
        words = re.findall(r'\b[a-z]{3,}\b', text.lower())

        # Common stop words to remove
        stop_words = {
            'the', 'is', 'at', 'which', 'on', 'a', 'an', 'as', 'are', 'was',
            'were', 'been', 'be', 'have', 'has', 'had', 'do', 'does', 'did',
            'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can',
            'this', 'that', 'these', 'those', 'and', 'but', 'or', 'not', 'for',
            'with', 'from', 'about', 'into', 'through', 'during', 'before',
            'after', 'above', 'below', 'between', 'under', 'over'
        }

        # Filter and get most common
        keywords = [w for w in words if w not in stop_words]

        # Return unique keywords
        unique_keywords = []
        seen = set()
        for kw in keywords:
            if kw not in seen:
                unique_keywords.append(kw)
                seen.add(kw)
                if len(unique_keywords) >= max_keywords:
                    break

        return unique_keywords[:max_keywords]

    async def auto_save_new_content(
        self,
        workspace_id: UUID,
        check_interval_hours: int = 1
    ) -> int:
        """
        Automatically save new content to historical storage.

        This should be called periodically (e.g., by scheduler).

        Args:
            workspace_id: Workspace ID
            check_interval_hours: How far back to check for new content

        Returns:
            Number of items saved
        """
        # Get content from last N hours
        cutoff = datetime.now() - timedelta(hours=check_interval_hours)

        # Fetch recent content items that aren't already in historical storage
        recent_content = self.db.list_content_items(
            str(workspace_id),
            start_date=cutoff,
            limit=1000
        )

        # Check which items are already in historical storage
        existing_ids = set()
        existing_historical = await self.get_historical_content(
            workspace_id,
            days_back=1
        )

        for h in existing_historical:
            if h.content_item_id:
                existing_ids.add(str(h.content_item_id))

        # Filter out items already saved
        new_items = [
            item for item in recent_content
            if item.get('id') and str(item['id']) not in existing_ids
        ]

        # Save new items
        if new_items:
            return await self.save_content_to_history(workspace_id, new_items)
        else:
            return 0
