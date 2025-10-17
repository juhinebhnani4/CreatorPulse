"""
Content service - Business logic for content scraping and management.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.ai_newsletter.database.supabase_client import SupabaseManager
from src.ai_newsletter.scrapers.reddit_scraper import RedditScraper
from src.ai_newsletter.scrapers.rss_scraper import RSSFeedScraper
from src.ai_newsletter.scrapers.blog_scraper import BlogScraper
from src.ai_newsletter.scrapers.x_scraper import XScraper
from src.ai_newsletter.scrapers.youtube_scraper import YouTubeScraper
from src.ai_newsletter.models.content import ContentItem


class ContentService:
    """Service for content scraping and management."""

    def __init__(self):
        """Initialize content service."""
        self.supabase = SupabaseManager()

    async def scrape_content(
        self,
        user_id: str,
        workspace_id: str,
        sources: Optional[List[str]] = None,
        limit_per_source: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Scrape content for a workspace.

        Args:
            user_id: User ID (for auth check)
            workspace_id: Workspace ID
            sources: Specific sources to scrape (None = all enabled)
            limit_per_source: Override limit per source

        Returns:
            Dict with scraped content summary
        """
        # Verify user has access to workspace
        workspace = self.supabase.get_workspace(workspace_id)
        if not workspace:
            raise ValueError("Workspace not found")

        # Get workspace config
        config = self.supabase.get_workspace_config(workspace_id)

        # Parse config structure - handle both formats (legacy dict and new array)
        sources_list = []
        if isinstance(config.get('sources'), list):
            # New format: sources is an array of {type, enabled, config}
            sources_list = config['sources']
        else:
            # Legacy format: flat dict with source keys
            for source_name, settings in config.items():
                if isinstance(settings, dict) and settings.get('enabled'):
                    sources_list.append({
                        'type': source_name,
                        'enabled': True,
                        'config': settings
                    })

        # Determine which sources to scrape
        if sources is None:
            # Scrape all enabled sources
            sources = [
                s['type'] for s in sources_list
                if s.get('enabled', False)
            ]

        # Scrape content from each source
        all_items: List[ContentItem] = []
        results = {}

        for source in sources:
            try:
                # Find source config from sources_list
                source_config = None
                for s in sources_list:
                    if s.get('type') == source:
                        source_config = s.get('config', {})
                        break

                if not source_config:
                    # Source not found in config, skip
                    results[source] = {
                        'success': False,
                        'error': f'Source {source} not found in workspace config',
                        'items_count': 0
                    }
                    continue

                # Use override limit or config limit
                limit = limit_per_source or source_config.get('limit', 10)

                # Scrape based on source type
                items = await self._scrape_source(source, source_config, limit)

                # Store results
                results[source] = {
                    'success': True,
                    'items_count': len(items),
                    'items': items
                }
                all_items.extend(items)

            except Exception as e:
                results[source] = {
                    'success': False,
                    'error': str(e),
                    'items_count': 0
                }

        # Save all items to database
        if all_items:
            saved_items = self.supabase.save_content_items(workspace_id, all_items)
        else:
            saved_items = []

        return {
            'workspace_id': workspace_id,
            'sources_scraped': sources,
            'total_items': len(saved_items),
            'items_by_source': {
                source: data['items_count']
                for source, data in results.items()
            },
            'results': results,
            'scraped_at': datetime.now().isoformat()
        }

    async def _scrape_source(
        self,
        source: str,
        config: Dict[str, Any],
        limit: int
    ) -> List[ContentItem]:
        """
        Scrape content from a specific source.

        Args:
            source: Source name (reddit, rss, blog, x, youtube)
            config: Source configuration
            limit: Number of items to scrape

        Returns:
            List of ContentItem objects
        """
        if source == 'reddit':
            return await self._scrape_reddit(config, limit)
        elif source == 'rss':
            return await self._scrape_rss(config, limit)
        elif source == 'blog':
            return await self._scrape_blog(config, limit)
        elif source == 'x':
            return await self._scrape_x(config, limit)
        elif source == 'youtube':
            return await self._scrape_youtube(config, limit)
        else:
            raise ValueError(f"Unknown source: {source}")

    async def _scrape_reddit(self, config: Dict[str, Any], limit: int) -> List[ContentItem]:
        """Scrape Reddit content."""
        scraper = RedditScraper()

        # Support both single subreddit and array of subreddits
        subreddits = config.get('subreddits', [])
        if not subreddits and 'subreddit' in config:
            # Convert single subreddit to array
            subreddits = [config['subreddit']]
        if not subreddits:
            subreddits = ['AI_Agents']  # Default fallback

        sort = config.get('sort', 'hot')
        time_filter = config.get('time_filter', 'all')

        all_items = []
        limit_per_sub = max(1, limit // len(subreddits)) if subreddits else limit

        for subreddit in subreddits:
            items = scraper.fetch_content(
                subreddit=subreddit,
                limit=limit_per_sub,
                sort=sort,
                time_filter=time_filter
            )
            all_items.extend(items)

        return all_items[:limit]

    async def _scrape_rss(self, config: Dict[str, Any], limit: int) -> List[ContentItem]:
        """Scrape RSS feeds."""
        scraper = RSSFeedScraper()

        # Support both single URL and array of URLs
        feed_urls = config.get('feed_urls', [])
        if not feed_urls and 'url' in config:
            # Convert single URL to array
            feed_urls = [config['url']]

        if not feed_urls:
            return []

        items = scraper.fetch_content(
            feed_urls=feed_urls,
            limit=limit
        )
        return items

    async def _scrape_blog(self, config: Dict[str, Any], limit: int) -> List[ContentItem]:
        """Scrape blog content."""
        scraper = BlogScraper()

        # Support both single URL and array of URLs
        urls = config.get('urls', [])
        if not urls and 'url' in config:
            # Convert single URL to array
            urls = [config['url']]

        if not urls:
            return []

        all_items = []
        for url in urls:
            items = scraper.fetch_content_smart(url=url, limit=limit)
            all_items.extend(items)

        return all_items[:limit]

    async def _scrape_x(self, config: Dict[str, Any], limit: int) -> List[ContentItem]:
        """Scrape X (Twitter) content."""
        # Extract credentials from config or environment
        scraper = XScraper(
            api_key=config.get('api_key'),
            api_secret=config.get('api_secret'),
            access_token=config.get('access_token'),
            access_token_secret=config.get('access_token_secret'),
            bearer_token=config.get('bearer_token')
        )

        # Support both single handle and array of usernames
        usernames = config.get('usernames', [])
        if not usernames and 'handle' in config:
            # Convert single handle to array
            usernames = [config['handle']]

        all_items = []

        for username in usernames:
            items = scraper.fetch_user_timeline(username=username, limit=limit)
            all_items.extend(items)

        return all_items[:limit]

    async def _scrape_youtube(self, config: Dict[str, Any], limit: int) -> List[ContentItem]:
        """Scrape YouTube content."""
        import os

        # Get API key from config or environment
        api_key = config.get('api_key') or os.getenv('YOUTUBE_API_KEY')

        if not api_key:
            # Return empty list if no API key available
            return []

        scraper = YouTubeScraper(api_key=api_key)

        # Support channel URL extraction
        url = config.get('url', '')
        if not url:
            return []

        # Try to fetch content from the URL
        # The YouTube scraper can handle channel URLs, usernames, etc.
        try:
            items = scraper.fetch_content(
                channel_url=url,
                limit=limit
            )
            return items
        except Exception as e:
            # Log error but return empty list to not break the flow
            print(f"Error scraping YouTube {url}: {e}")
            return []

    async def list_content(
        self,
        user_id: str,
        workspace_id: str,
        days: int = 7,
        source: Optional[str] = None,
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        List content items for a workspace.

        Args:
            user_id: User ID (for auth check)
            workspace_id: Workspace ID
            days: Number of days to look back
            source: Optional source filter
            limit: Maximum items to return

        Returns:
            Dict with content items
        """
        # Verify user has access
        workspace = self.supabase.get_workspace(workspace_id)
        if not workspace:
            raise ValueError("Workspace not found")

        # Load content items
        items = self.supabase.load_content_items(
            workspace_id=workspace_id,
            days=days,
            source=source,
            limit=limit
        )

        return {
            'workspace_id': workspace_id,
            'items': [item.to_dict() for item in items],
            'count': len(items),
            'filters': {
                'days': days,
                'source': source,
                'limit': limit
            }
        }

    async def get_content_stats(
        self,
        user_id: str,
        workspace_id: str
    ) -> Dict[str, Any]:
        """
        Get content statistics for a workspace.

        Args:
            user_id: User ID (for auth check)
            workspace_id: Workspace ID

        Returns:
            Dict with content statistics
        """
        # Verify user has access
        workspace = self.supabase.get_workspace(workspace_id)
        if not workspace:
            raise ValueError("Workspace not found")

        # Get all content items (last 30 days)
        all_items = self.supabase.load_content_items(
            workspace_id=workspace_id,
            days=30,
            limit=10000
        )

        # Calculate stats
        items_by_source = {}
        for item in all_items:
            source = item.source
            items_by_source[source] = items_by_source.get(source, 0) + 1

        # Items in last 24h (use timezone-aware datetime)
        from datetime import timezone
        cutoff_24h = datetime.now(timezone.utc) - timedelta(hours=24)
        items_24h = sum(1 for item in all_items if item.scraped_at and item.scraped_at >= cutoff_24h)

        # Items in last 7d
        cutoff_7d = datetime.now(timezone.utc) - timedelta(days=7)
        items_7d = sum(1 for item in all_items if item.scraped_at and item.scraped_at >= cutoff_7d)

        # Latest scrape time
        latest_scrape = max(
            (item.scraped_at for item in all_items),
            default=None
        )

        return {
            'workspace_id': workspace_id,
            'total_items': len(all_items),
            'items_by_source': items_by_source,
            'items_last_24h': items_24h,
            'items_last_7d': items_7d,
            'latest_scrape': latest_scrape.isoformat() if latest_scrape else None
        }


# Global service instance
content_service = ContentService()
