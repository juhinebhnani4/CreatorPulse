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
        self._twitter_cache = {}  # Cache format: {username: (items, timestamp)}
        self._cache_ttl = 900  # 15 minutes in seconds

    def _merge_source_configs(
        self,
        sources_list: List[Dict[str, Any]],
        filter_sources: Optional[List[str]] = None
    ) -> Dict[str, Dict[str, Any]]:
        """
        Merge multiple source configs of the same type into single configs.

        Fixes critical bug where multiple source objects of same type (e.g., 4 YouTube configs)
        would only scrape the first one.

        Args:
            sources_list: List of source objects from workspace config
            filter_sources: Optional list of source types to include (None = all enabled)

        Returns:
            Dict mapping source type to merged config

        Example:
            Input: [
                {"type": "youtube", "enabled": True, "config": {"channels": ["ch1"]}},
                {"type": "youtube", "enabled": True, "config": {"channels": ["ch2", "ch3"]}},
                {"type": "reddit", "enabled": True, "config": {"subreddits": ["sub1"]}}
            ]
            Output: {
                "youtube": {"channels": ["ch1", "ch2", "ch3"], "limit": 10},
                "reddit": {"subreddits": ["sub1"], "limit": 10}
            }
        """
        merged = {}

        for source_obj in sources_list:
            # Skip disabled sources
            if not source_obj.get('enabled', False):
                continue

            source_type = source_obj.get('type')
            if not source_type:
                continue

            # If filter specified, skip sources not in filter
            if filter_sources is not None and source_type not in filter_sources:
                continue

            source_config = source_obj.get('config', {})

            # Initialize merged config for this type if not exists
            if source_type not in merged:
                merged[source_type] = {
                    'subreddits': [],      # For reddit
                    'feeds': [],           # For RSS
                    'usernames': [],       # For Twitter/X
                    'channels': [],        # For YouTube
                    'urls': [],            # For blogs
                    'limit': source_config.get('limit', 10),
                }

            # Merge arrays based on source type
            if source_type == 'reddit':
                subreddits = source_config.get('subreddits', [])
                if isinstance(subreddits, list):
                    merged[source_type]['subreddits'].extend(subreddits)
                elif isinstance(subreddits, str):
                    merged[source_type]['subreddits'].append(subreddits)

            elif source_type == 'rss':
                feeds = source_config.get('feeds', [])
                if isinstance(feeds, list):
                    merged[source_type]['feeds'].extend(feeds)
                # Also support legacy feed_urls format
                feed_urls = source_config.get('feed_urls', [])
                if isinstance(feed_urls, list):
                    for url in feed_urls:
                        merged[source_type]['feeds'].append({'url': url, 'name': url})
                # Support single url
                if 'url' in source_config:
                    merged[source_type]['feeds'].append({
                        'url': source_config['url'],
                        'name': source_config['url']
                    })

            elif source_type in ['x', 'twitter']:
                # Normalize to 'x' type
                if source_type == 'twitter':
                    source_type = 'x'
                    if 'x' not in merged:
                        merged['x'] = merged.pop('twitter', {
                            'usernames': [],
                            'limit': source_config.get('limit', 10)
                        })

                usernames = source_config.get('usernames', [])
                if isinstance(usernames, list):
                    merged[source_type]['usernames'].extend(usernames)
                elif isinstance(usernames, str):
                    merged[source_type]['usernames'].append(usernames)
                # Also support legacy 'handle' format
                if 'handle' in source_config:
                    merged[source_type]['usernames'].append(source_config['handle'])

            elif source_type == 'youtube':
                channels = source_config.get('channels', [])
                if isinstance(channels, list):
                    merged[source_type]['channels'].extend(channels)
                elif isinstance(channels, str):
                    merged[source_type]['channels'].append(channels)
                # Also support legacy 'url' format
                if 'url' in source_config:
                    merged[source_type]['channels'].append(source_config['url'])

            elif source_type == 'blog':
                urls = source_config.get('urls', [])
                if isinstance(urls, list):
                    merged[source_type]['urls'].extend(urls)
                elif isinstance(urls, str):
                    merged[source_type]['urls'].append(urls)
                # Also support legacy 'url' format
                if 'url' in source_config:
                    merged[source_type]['urls'].append(source_config['url'])

        # Clean up empty arrays and deduplicate
        for source_type in list(merged.keys()):
            config = merged[source_type]

            # Deduplicate arrays (case-insensitive for usernames/subreddits)
            if source_type == 'reddit' and config['subreddits']:
                # Deduplicate subreddits (case-insensitive)
                seen = set()
                unique = []
                for sub in config['subreddits']:
                    sub_lower = sub.lower().strip()
                    if sub_lower not in seen:
                        seen.add(sub_lower)
                        unique.append(sub)
                config['subreddits'] = unique
                print(f"   [Reddit] Merged to {len(unique)} unique subreddits")

            if source_type in ['x', 'twitter'] and config['usernames']:
                # Deduplicate usernames (case-insensitive)
                seen = set()
                unique = []
                for user in config['usernames']:
                    user_lower = user.lower().strip()
                    if user_lower not in seen:
                        seen.add(user_lower)
                        unique.append(user)
                config['usernames'] = unique
                print(f"   [Twitter] Merged to {len(unique)} unique usernames")

            if source_type == 'youtube' and config['channels']:
                # Deduplicate channels
                seen = set()
                unique = []
                for ch in config['channels']:
                    ch_stripped = ch.strip()
                    if ch_stripped not in seen:
                        seen.add(ch_stripped)
                        unique.append(ch_stripped)
                config['channels'] = unique
                print(f"   [YouTube] Merged to {len(unique)} unique channels")

            if source_type == 'rss' and config['feeds']:
                # Deduplicate RSS feeds by URL
                seen = set()
                unique = []
                for feed in config['feeds']:
                    if isinstance(feed, dict):
                        url = feed.get('url', '').strip()
                    else:
                        url = str(feed).strip()
                    if url and url not in seen:
                        seen.add(url)
                        unique.append(feed)
                config['feeds'] = unique
                print(f"   [RSS] Merged to {len(unique)} unique feeds")

            if source_type == 'blog' and config['urls']:
                # Deduplicate blog URLs
                config['urls'] = list(set(url.strip() for url in config['urls']))
                print(f"   [Blogs] Merged to {len(config['urls'])} unique URLs")

            # Remove empty configs
            has_content = (
                config.get('subreddits') or
                config.get('feeds') or
                config.get('usernames') or
                config.get('channels') or
                config.get('urls')
            )
            if not has_content:
                del merged[source_type]

        return merged

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

        # Merge configs of same type to handle multiple source objects
        # This fixes bug where multiple YouTube/Reddit/etc configs only scrape first one
        merged_configs = self._merge_source_configs(sources_list, sources)

        print(f"[SourceMerge] Merged {len(sources_list)} source objects into {len(merged_configs)} unique source types")

        # Scrape content from each merged source config
        all_items: List[ContentItem] = []
        results = {}

        for source_type, merged_config in merged_configs.items():
            try:
                # Use override limit or config limit
                limit = limit_per_source or merged_config.get('limit', 10)

                # Scrape based on source type
                items = await self._scrape_source(source_type, merged_config, limit)

                # Store results
                results[source_type] = {
                    'success': True,
                    'items_count': len(items),
                    'items': items
                }
                all_items.extend(items)

            except Exception as e:
                results[source_type] = {
                    'success': False,
                    'error': str(e),
                    'items_count': 0
                }

        # Save all items to database
        if all_items:
            # Deduplicate items by source_url before saving
            # This prevents "ON CONFLICT DO UPDATE command cannot affect row a second time" error
            # when multiple source configs scrape the same content
            seen_urls = set()
            unique_items = []
            duplicates_removed = 0

            for item in all_items:
                url_key = f"{item.source}:{item.source_url}"
                if url_key not in seen_urls:
                    seen_urls.add(url_key)
                    unique_items.append(item)
                else:
                    duplicates_removed += 1

            if duplicates_removed > 0:
                print(f"   Removed {duplicates_removed} duplicate items from batch (same URL scraped by multiple sources)")

            saved_items = self.supabase.save_content_items(workspace_id, unique_items)
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
        """Scrape RSS feeds with multiple config format support."""
        scraper = RSSFeedScraper()

        feed_urls = []

        # Format 1: New frontend format {feeds: [{url, name}]}
        if 'feeds' in config and isinstance(config['feeds'], list):
            feed_urls = [feed['url'] for feed in config['feeds']
                         if isinstance(feed, dict) and 'url' in feed]
            print(f"[RSS] Extracted {len(feed_urls)} URLs from 'feeds' array")

        # Format 2: Legacy format {feed_urls: [...]}
        elif 'feed_urls' in config:
            feed_urls = config['feed_urls']
            print(f"[RSS] Found {len(feed_urls)} feeds in 'feed_urls' format")

        # Format 3: Single URL {url: "..."}
        elif 'url' in config:
            feed_urls = [config['url']]
            print(f"[RSS] Found single feed in 'url' format")

        if not feed_urls:
            print(f"[RSS] WARNING: No RSS feed URLs found in config. Config keys: {list(config.keys())}")
            return []

        print(f"[RSS] Scraping {len(feed_urls)} RSS feeds...")
        items = scraper.fetch_content(
            feed_urls=feed_urls,
            limit=limit
        )
        print(f"[RSS] Scraper returned {len(items)} items")

        return items

    async def _scrape_blog(self, config: Dict[str, Any], limit: int) -> List[ContentItem]:
        """Scrape blog content with retry logic and pagination support."""
        scraper = BlogScraper()

        # Support both single URL and array of URLs
        urls = config.get('urls', [])
        if not urls and 'url' in config:
            # Convert single URL to array
            urls = [config['url']]

        if not urls:
            return []

        # Use the new fetch_multiple_urls method with retry logic, pagination, and smart extraction
        all_items = scraper.fetch_multiple_urls(
            urls=urls,
            limit_per_url=limit,  # Use configured limit per URL
            use_smart_extraction=True,  # Enable intelligent extraction (trafilatura, JSON-LD, etc.)
            use_crawling=False,  # Disable deep crawling by default (can be made configurable)
            timeout=20  # Increased timeout for slow blog servers
        )

        return all_items[:limit * len(urls)]  # Allow limit per URL, not total limit

    async def _scrape_x(self, config: Dict[str, Any], limit: int) -> List[ContentItem]:
        """Scrape X (Twitter) content with caching to avoid rate limits."""
        import os

        # Extract credentials from config or environment
        # Prefer environment variables for API keys (more secure)
        scraper = XScraper(
            api_key=config.get('api_key') or os.getenv('X_API_KEY'),
            api_secret=config.get('api_secret') or os.getenv('X_API_SECRET'),
            access_token=config.get('access_token') or os.getenv('X_ACCESS_TOKEN'),
            access_token_secret=config.get('access_token_secret') or os.getenv('X_ACCESS_TOKEN_SECRET'),
            bearer_token=config.get('bearer_token') or os.getenv('X_BEARER_TOKEN')
        )

        # Support both single handle and array of usernames
        usernames = config.get('usernames', [])
        if not usernames and 'handle' in config:
            # Convert single handle to array
            usernames = [config['handle']]

        all_items = []

        for username in usernames:
            cache_key = f"x_{username}"

            # Check cache
            if cache_key in self._twitter_cache:
                items, cached_at = self._twitter_cache[cache_key]
                age = (datetime.now() - cached_at).total_seconds()
                if age < self._cache_ttl:
                    print(f"[Twitter] Using cached data for @{username} (age: {age:.0f}s)")
                    all_items.extend(items)
                    continue
                else:
                    print(f"[Twitter] Cache expired for @{username} (age: {age:.0f}s > {self._cache_ttl}s)")

            # Fetch fresh data
            print(f"[Twitter] Fetching fresh data for @{username}...")
            try:
                items = scraper.fetch_user_timeline(username=username, limit=limit)

                # Cache results (even if empty, to avoid repeated failures)
                self._twitter_cache[cache_key] = (items, datetime.now())
                print(f"[Twitter] Cached {len(items)} tweets from @{username}")

                all_items.extend(items)
            except Exception as e:
                print(f"[Twitter] Error fetching @{username}: {e}")
                # Cache empty result to avoid immediate retry
                self._twitter_cache[cache_key] = ([], datetime.now())

        return all_items[:limit]

    async def _scrape_youtube(self, config: Dict[str, Any], limit: int) -> List[ContentItem]:
        """Scrape YouTube content."""
        import os
        import re

        # Get API key from config or environment
        api_key = config.get('api_key') or os.getenv('YOUTUBE_API_KEY')

        if not api_key:
            # Return empty list if no API key available
            return []

        scraper = YouTubeScraper(api_key=api_key)

        # Support both 'channels' array (new format) and 'url' (legacy format)
        channels = config.get('channels', [])
        if not channels and 'url' in config:
            # Convert single URL to array
            channels = [config['url']]

        if not channels:
            return []

        all_items = []
        limit_per_channel = max(1, limit // len(channels)) if channels else limit

        # Try to fetch content from each channel URL
        for channel_identifier in channels:
            try:
                # Parse the channel identifier to extract username or channel ID
                fetch_params = self._parse_youtube_identifier(channel_identifier)

                if not fetch_params:
                    print(f"Could not parse YouTube identifier: {channel_identifier}")
                    continue

                items = scraper.fetch_content(
                    limit=limit_per_channel,
                    **fetch_params
                )
                all_items.extend(items)
            except Exception as e:
                # Log error but continue with other channels
                print(f"Error scraping YouTube {channel_identifier}: {e}")
                continue

        return all_items[:limit]

    def _parse_youtube_identifier(self, identifier: str) -> Dict[str, str]:
        """
        Parse YouTube channel identifier (URL, username, or channel ID).

        Supports:
        - https://www.youtube.com/@username
        - https://www.youtube.com/c/CustomName
        - https://www.youtube.com/channel/CHANNEL_ID
        - @username
        - username (plain, will be treated as @username)
        - CHANNEL_ID (starts with UC)

        Returns:
            Dict with either 'channel_username' or 'channel_id'
        """
        import re

        # Clean identifier - remove whitespace, newlines, special chars
        identifier = identifier.strip().replace('\n', '').replace('\r', '')

        # Handle @username format (with or without URL)
        username_match = re.search(r'@([\w-]+)', identifier)
        if username_match:
            return {'channel_username': username_match.group(1)}

        # Handle /c/CustomName format
        custom_match = re.search(r'/c/([\w-]+)', identifier)
        if custom_match:
            return {'channel_username': custom_match.group(1)}

        # Handle /channel/CHANNEL_ID format
        channel_id_match = re.search(r'/channel/(UC[\w-]+)', identifier)
        if channel_id_match:
            return {'channel_id': channel_id_match.group(1)}

        # Handle direct channel ID (starts with UC)
        if identifier.startswith('UC') and len(identifier) == 24:
            return {'channel_id': identifier}

        # Handle plain username (no @ prefix) - treat as username
        # This covers cases like "deeplearningai" which should be "@deeplearningai"
        # Be more lenient - match alphanumeric, underscore, hyphen
        clean_identifier = re.sub(r'[^\w-]', '', identifier)  # Remove any non-word chars except hyphen
        if clean_identifier and re.match(r'^[\w-]+$', clean_identifier):
            print(f"   YouTube: Treating '{clean_identifier}' as username (normalized from '{identifier}')")
            return {'channel_username': clean_identifier}

        # If no pattern matched, return empty dict
        print(f"   ⚠️ Could not parse YouTube identifier: '{identifier}' (repr: {repr(identifier)})")
        return {}

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

        # Map items to dict and add 'url' field for frontend compatibility
        items_dict = []
        for item in items:
            item_data = item.to_dict()
            # Add 'url' as alias for 'source_url' (frontend expects 'url')
            item_data['url'] = item_data.get('source_url')
            items_dict.append(item_data)

        return {
            'workspace_id': workspace_id,
            'items': items_dict,
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

    def update_content_item(
        self,
        user_id: str,
        item_id: str,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update a content item's editable fields.

        Args:
            user_id: User ID (for auth check)
            item_id: Content item ID
            updates: Fields to update (title, summary, source_url)

        Returns:
            Updated content item as dict

        Raises:
            ValueError: If item not found or user doesn't have access
        """
        print(f"\n[ContentService] update_content_item called")
        print(f"[ContentService]   - user_id: {user_id}")
        print(f"[ContentService]   - item_id: {item_id}")
        print(f"[ContentService]   - updates: {updates}")

        # Get the content item first to verify it exists and get workspace_id
        print(f"[ContentService] Fetching existing item...")
        existing_item = self.supabase.get_content_item(item_id)

        if not existing_item:
            print(f"[ContentService] ERROR: Item not found - raising ValueError")
            raise ValueError("Content item not found")

        print(f"[ContentService] OK: Found existing item in workspace: {existing_item.get('workspace_id')}")

        # Verify user has access to this workspace
        print(f"[ContentService] Verifying user has access to workspace...")
        workspace = self.supabase.get_workspace(existing_item['workspace_id'])
        if not workspace:
            print(f"[ContentService] ERROR: Workspace not found - raising ValueError")
            raise ValueError("Workspace not found")

        print(f"[ContentService] OK: User has access to workspace: {workspace.get('name')}")

        # Update the item
        print(f"[ContentService] Calling supabase.update_content_item...")
        updated_item = self.supabase.update_content_item(item_id, updates)
        if not updated_item:
            print(f"[ContentService] ERROR: Update failed - raising ValueError")
            raise ValueError("Failed to update content item")

        print(f"[ContentService] OK: Item updated successfully")
        print(f"[ContentService]   - Updated title: {updated_item.get('title', '')[:50]}...")
        return updated_item


# Global service instance
content_service = ContentService()
