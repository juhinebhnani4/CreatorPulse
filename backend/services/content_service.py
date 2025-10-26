"""
Content service - Business logic for content scraping and management.
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import sys
import asyncio
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
from backend.config.constants import ContentConstants
from backend.utils.serializers import serialize_content_list  # P2 #4: Null handling


class ContentService:
    """Service for content scraping and management."""

    def __init__(self):
        """Initialize content service."""
        self.supabase = SupabaseManager()
        # P2 #16: Extended caching to Reddit and RSS (previously only Twitter)
        self._twitter_cache = {}  # Cache format: {username: (items, timestamp)}
        self._reddit_cache = {}   # Cache format: {subreddit: (items, timestamp)}
        self._rss_cache = {}      # Cache format: {feed_url: (items, timestamp)}
        self._cache_ttl = 900  # 15 minutes in seconds

        # P2 #15: Circuit breaker for external APIs
        # Format: {source_name: {'failures': count, 'first_failure': timestamp, 'circuit_open': bool}}
        self._circuit_breaker = {}
        self._circuit_failure_threshold = 3  # Open circuit after 3 failures
        self._circuit_timeout = 300  # 5 minutes in seconds

    def _is_circuit_open(self, source_name: str) -> bool:
        """
        P2 #15: Check if circuit breaker is open for a source.

        Returns True if circuit is open (too many failures), False otherwise.
        """
        if source_name not in self._circuit_breaker:
            return False

        state = self._circuit_breaker[source_name]

        # Check if circuit should be reset (timeout elapsed)
        if state.get('circuit_open'):
            time_since_first_failure = (datetime.now() - state['first_failure']).total_seconds()
            if time_since_first_failure > self._circuit_timeout:
                print(f"[Circuit Breaker] Resetting circuit for {source_name} (timeout elapsed: {time_since_first_failure:.0f}s)")
                del self._circuit_breaker[source_name]
                return False

        return state.get('circuit_open', False)

    def _record_failure(self, source_name: str):
        """
        P2 #15: Record a failure for a source and potentially open circuit.
        """
        if source_name not in self._circuit_breaker:
            self._circuit_breaker[source_name] = {
                'failures': 1,
                'first_failure': datetime.now(),
                'circuit_open': False
            }
        else:
            self._circuit_breaker[source_name]['failures'] += 1

        state = self._circuit_breaker[source_name]
        if state['failures'] >= self._circuit_failure_threshold:
            state['circuit_open'] = True
            print(f"[Circuit Breaker] ⚠️ CIRCUIT OPENED for {source_name} ({state['failures']} failures). Will retry in {self._circuit_timeout}s")

    def _record_success(self, source_name: str):
        """
        P2 #15: Record a success for a source and reset failure count.
        """
        if source_name in self._circuit_breaker:
            print(f"[Circuit Breaker] Success for {source_name}, resetting failure count")
            del self._circuit_breaker[source_name]

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
        # Store workspace_id for use in helper methods (e.g., sort rotation)
        self._current_workspace_id = workspace_id

        # Verify user has access to workspace
        workspace = self.supabase.get_workspace(workspace_id)
        if not workspace:
            raise ValueError("Workspace not found")

        # Verify user has access to this workspace
        if not self.supabase.user_has_workspace_access(user_id, workspace_id):
            raise ValueError("Access denied: User not in workspace")

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

        if ContentConstants.SCRAPE_CONCURRENT:
            # Concurrent scraping (3-5x faster)
            print(f"[ContentService] Scraping {len(merged_configs)} sources concurrently...")

            scrape_tasks = [
                self._scrape_source_safe(source_type, config, limit_per_source or config.get('limit', 10))
                for source_type, config in merged_configs.items()
            ]

            # Execute all scrapes in parallel
            results_raw = await asyncio.gather(*scrape_tasks, return_exceptions=True)

            # Process results
            for i, (source_type, _) in enumerate(merged_configs.items()):
                result = results_raw[i]

                if isinstance(result, Exception):
                    results[source_type] = {
                        'success': False,
                        'error': f"Unexpected error: {result}",
                        'items_count': 0
                    }
                else:
                    items, success, error = result
                    results[source_type] = {
                        'success': success,
                        'items_count': len(items),
                        'items': items,
                        'error': error
                    }
                    all_items.extend(items)
        else:
            # Sequential scraping (backward compatibility / debugging)
            print(f"[ContentService] Scraping {len(merged_configs)} sources sequentially (SCRAPE_CONCURRENT=false)...")

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
        print(f"\n{'='*80}")
        print(f"[Scrape Debug] CONTENT SCRAPING RESULTS")
        print(f"{'='*80}")
        print(f"[Scrape] Workspace ID: {workspace_id}")
        print(f"[Scrape] Total items fetched from sources: {len(all_items)}")

        if all_items:
            # CRITICAL FIX #8: Intelligent deduplication with data merging
            # Instead of just dropping duplicates, merge them to keep the best data from each
            # This prevents losing better content/metadata when multiple scrapers fetch same URL
            from src.ai_newsletter.models.content import ContentItem

            def merge_content_items(item1: ContentItem, item2: ContentItem) -> ContentItem:
                """
                Merge two ContentItem objects, keeping the best data from each.
                Priority: Longer/richer content wins, more metadata wins.
                """
                return ContentItem(
                    # Keep longer title (often more descriptive)
                    title=item1.title if len(item1.title) > len(item2.title) else item2.title,

                    # Keep richer content (longer is usually better for content)
                    content=item1.content if (len(item1.content or '') > len(item2.content or '')) else item2.content,

                    # Keep longer summary (more informative)
                    summary=item1.summary if (len(item1.summary or '') > len(item2.summary or '')) else item2.summary,

                    # Prefer item with author info
                    author=item1.author or item2.author,
                    author_url=item1.author_url or item2.author_url,

                    # Keep highest engagement score
                    score=max(item1.score or 0, item2.score or 0) if (item1.score or item2.score) else None,
                    comments_count=max(item1.comments_count or 0, item2.comments_count or 0) if (item1.comments_count or item2.comments_count) else None,
                    shares_count=max(item1.shares_count or 0, item2.shares_count or 0) if (item1.shares_count or item2.shares_count) else None,
                    views_count=max(item1.views_count or 0, item2.views_count or 0) if (item1.views_count or item2.views_count) else None,

                    # Prefer item with media
                    image_url=item1.image_url or item2.image_url,
                    video_url=item1.video_url or item2.video_url,
                    external_url=item1.external_url or item2.external_url,

                    # Merge tags (union, deduplicate)
                    tags=list(set((item1.tags or []) + (item2.tags or []))),

                    # Prefer item with category
                    category=item1.category or item2.category,

                    # Keep earlier created_at (original publication date)
                    created_at=min(item1.created_at, item2.created_at) if (item1.created_at and item2.created_at) else (item1.created_at or item2.created_at),

                    # Prefer first source (indicates primary source for this content)
                    source=item1.source,
                    source_url=item1.source_url,

                    # Merge metadata (combine both dictionaries)
                    metadata={
                        **item1.metadata,
                        **item2.metadata,
                        'merged_from_sources': [item1.source, item2.source],
                        'merge_note': 'Merged from multiple scrapers to preserve best data'
                    },

                    # Keep most recent scrape time
                    scraped_at=max(item1.scraped_at, item2.scraped_at) if (item1.scraped_at and item2.scraped_at) else (item1.scraped_at or item2.scraped_at)
                )

            # Deduplicate items by source_url with intelligent merging
            # This prevents "ON CONFLICT DO UPDATE command cannot affect row a second time" error
            # when multiple source configs scrape the same content
            seen_urls = {}  # Map url_key -> ContentItem
            duplicates_merged = 0

            for item in all_items:
                url_key = f"{item.source}:{item.source_url}"
                if url_key not in seen_urls:
                    seen_urls[url_key] = item
                else:
                    # Merge with existing item
                    print(f"[Scrape] 🔄 Merging duplicate: {item.title[:50]}... (from {item.source})")
                    seen_urls[url_key] = merge_content_items(seen_urls[url_key], item)
                    duplicates_merged += 1

            unique_items = list(seen_urls.values())

            if duplicates_merged > 0:
                print(f"[Scrape] ✅ Merged {duplicates_merged} duplicate items (same URL from multiple sources) to preserve best data")

            # Items are already validated during scraping by each individual scraper
            # No need to re-validate after deduplication (merging preserves valid items)
            print(f"[Scrape] Attempting to save {len(unique_items)} deduplicated items to database...")
            saved_items = self.supabase.save_content_items(workspace_id, unique_items)
            print(f"[Scrape] Items successfully saved to database: {len(saved_items)}")
            print(f"[Scrape] Items skipped (duplicates in DB): {len(unique_items) - len(saved_items)}")

            # Show sample of what was scraped
            print(f"\n[Scrape] Sample of items attempted to save:")
            for idx, item in enumerate(unique_items[:5]):
                status = "✅ SAVED" if idx < len(saved_items) else "⚠️ SKIPPED"
                print(f"  {idx+1}. [{status}] Source: {item.source:8} | Title: {item.title[:50]:50} | URL: {item.source_url[:60]}")
        else:
            saved_items = []
            print(f"[Scrape] No items fetched from sources!")

        # Get current total count
        current_total_result = self.supabase.service_client.table('content_items').select('id', count='exact').eq('workspace_id', workspace_id).execute()
        current_total = current_total_result.count if hasattr(current_total_result, 'count') else 0
        print(f"[Scrape] Current total items in database for this workspace: {current_total}")
        print(f"{'='*80}\n")

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

    async def _scrape_source_safe(
        self,
        source: str,
        config: Dict[str, Any],
        limit: int
    ) -> Tuple[List[ContentItem], bool, Optional[str]]:
        """
        Scrape source with timeout, error handling, and circuit breaker (P2 #15).

        Args:
            source: Source type (reddit, rss, youtube, x, blog)
            config: Source configuration
            limit: Max items to scrape

        Returns:
            Tuple of (items, success, error_message)
        """
        # P2 #15: Check circuit breaker before attempting scrape
        if self._is_circuit_open(source):
            error_msg = f"Circuit breaker OPEN for {source} (too many recent failures). Skipping scrape."
            print(f"[Circuit Breaker] {error_msg}")
            return [], False, error_msg

        try:
            # Use asyncio.timeout (Python 3.11+) or asyncio.wait_for (fallback)
            try:
                async with asyncio.timeout(ContentConstants.SCRAPE_TIMEOUT_SECONDS):
                    items = await self._scrape_source(source, config, limit)
                    # P2 #15: Record success to reset failure count
                    self._record_success(source)
                    return items, True, None
            except AttributeError:
                # Fallback for Python < 3.11
                items = await asyncio.wait_for(
                    self._scrape_source(source, config, limit),
                    timeout=ContentConstants.SCRAPE_TIMEOUT_SECONDS
                )
                # P2 #15: Record success to reset failure count
                self._record_success(source)
                return items, True, None
        except asyncio.TimeoutError:
            error_msg = f"Scraping {source} timed out after {ContentConstants.SCRAPE_TIMEOUT_SECONDS}s"
            print(f"[ContentService] {error_msg}")
            # P2 #15: Record failure for circuit breaker
            self._record_failure(source)
            return [], False, error_msg
        except Exception as e:
            error_msg = str(e)
            print(f"[ContentService] Error scraping {source}: {error_msg}")
            # P2 #15: Record failure for circuit breaker
            self._record_failure(source)
            return [], False, error_msg

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

    def _get_reddit_sort(self, config: Dict[str, Any]) -> str:
        """
        Determine Reddit sort method using time-based rotation with optional override.

        Industry standard: Rotate sorts throughout the day to maximize content diversity.
        Different sorts return completely different posts, reducing duplicates even when
        scraping frequently.

        Time-based schedule (default):
        - Morning (0-6 UTC): 'new' - Fresh overnight content
        - Midday (6-12 UTC): 'hot' - Trending morning content
        - Afternoon (12-18 UTC): 'rising' - Emerging discussions
        - Evening (18-24 UTC): 'top' - Quality content of the day

        Configuration options (optional, in workspace config):
        1. Manual override: {"sort": "hot"} - Always use specified sort
        2. Custom rotation: {"sort_rotation": ["hot", "new"]} - Cycle through list
        3. Disable rotation: {"sort_rotation": "disabled"} - Always use 'hot'

        Args:
            config: Source config from workspace (may contain sort overrides)

        Returns:
            Sort method: 'hot', 'new', 'rising', or 'top'

        Examples:
            >>> _get_reddit_sort({"sort": "new"})  # Manual override
            'new'

            >>> _get_reddit_sort({"sort_rotation": ["hot", "new", "top"]})  # Custom
            'new'  # Based on workspace_id hash

            >>> _get_reddit_sort({})  # Default - uses time of day
            'hot'  # If called between 6-12 UTC
        """
        from datetime import datetime

        # Option 1: Manual override (existing behavior - backward compatible)
        if 'sort' in config:
            sort = config['sort']
            print(f"[Reddit Sort] Using manual override: {sort}")
            return sort

        # Option 2: Disable rotation (opt-out)
        if config.get('sort_rotation') == 'disabled':
            print(f"[Reddit Sort] Rotation disabled, using default: hot")
            return 'hot'

        # Option 3: Custom rotation (advanced users)
        if 'sort_rotation' in config and isinstance(config['sort_rotation'], list):
            sorts = config['sort_rotation']
            if sorts:  # Check list is not empty
                # Use workspace_id hash for stateless round-robin
                # This ensures same workspace gets same sort across restarts
                workspace_id = getattr(self, '_current_workspace_id', 'default')
                index = int(workspace_id[:8], 16) % len(sorts)
                sort = sorts[index]
                print(f"[Reddit Sort] Using custom rotation: {sort} (index {index} of {sorts})")
                return sort

        # Option 4: Time-based rotation (default - industry standard)
        hour = datetime.utcnow().hour

        if 0 <= hour < 6:
            sort = 'new'      # Morning: fresh overnight content
        elif 6 <= hour < 12:
            sort = 'hot'      # Midday: trending content
        elif 12 <= hour < 18:
            sort = 'rising'   # Afternoon: emerging trends
        else:
            sort = 'top'      # Evening: quality content

        print(f"[Reddit Sort] Time-based rotation (hour {hour} UTC): {sort}")
        return sort

    async def _scrape_reddit(self, config: Dict[str, Any], limit: int) -> List[ContentItem]:
        """
        Scrape Reddit content with caching (P2 #16).

        Caching strategy: 15-minute TTL per subreddit to reduce Reddit API calls.
        """
        scraper = RedditScraper()

        # Support both single subreddit and array of subreddits
        subreddits = config.get('subreddits', [])
        if not subreddits and 'subreddit' in config:
            # Convert single subreddit to array
            subreddits = [config['subreddit']]
        if not subreddits:
            subreddits = ['AI_Agents']  # Default fallback

        # Use intelligent sort rotation (time-based by default, configurable)
        sort = self._get_reddit_sort(config)
        time_filter = config.get('time_filter', 'all')

        all_items = []
        limit_per_sub = max(1, limit // len(subreddits)) if subreddits else limit

        for subreddit in subreddits:
            # P2 #16: Check cache first
            cache_key = f"reddit_{subreddit}_{sort}_{time_filter}"
            if cache_key in self._reddit_cache:
                items, cached_at = self._reddit_cache[cache_key]
                age = (datetime.now() - cached_at).total_seconds()
                if age < self._cache_ttl:
                    print(f"[Reddit] Using cached data for r/{subreddit} (age: {age:.0f}s)")
                    all_items.extend(items[:limit_per_sub])
                    continue
                else:
                    print(f"[Reddit] Cache expired for r/{subreddit} (age: {age:.0f}s > {self._cache_ttl}s)")

            # Cache miss or expired - fetch fresh data
            print(f"[Reddit] Fetching fresh data for r/{subreddit}")
            items = scraper.fetch_content(
                subreddit=subreddit,
                limit=limit_per_sub,
                sort=sort,
                time_filter=time_filter
            )

            # Store in cache
            self._reddit_cache[cache_key] = (items, datetime.now())
            all_items.extend(items)

        return all_items[:limit]

    async def _scrape_rss(self, config: Dict[str, Any], limit: int) -> List[ContentItem]:
        """
        Scrape RSS feeds with caching (P2 #16).

        Caching strategy: 15-minute TTL per feed URL to reduce network calls.
        RSS feeds typically update every 15-60 minutes, so 15-min cache is safe.
        """
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

        # P2 #16: Check cache for each feed individually
        all_items = []
        uncached_urls = []

        for feed_url in feed_urls:
            cache_key = f"rss_{feed_url}"
            if cache_key in self._rss_cache:
                items, cached_at = self._rss_cache[cache_key]
                age = (datetime.now() - cached_at).total_seconds()
                if age < self._cache_ttl:
                    print(f"[RSS] Using cached data for {feed_url[:60]}... (age: {age:.0f}s)")
                    all_items.extend(items)
                    continue
                else:
                    print(f"[RSS] Cache expired for {feed_url[:60]}... (age: {age:.0f}s > {self._cache_ttl}s)")

            uncached_urls.append(feed_url)

        # Fetch fresh data for uncached/expired feeds
        if uncached_urls:
            print(f"[RSS] Fetching fresh data for {len(uncached_urls)} feeds...")
            fresh_items = scraper.fetch_content(
                feed_urls=uncached_urls,
                limit=limit
            )

            # Store in cache (one entry per feed URL)
            # Note: scraper returns mixed items from all URLs, we cache per-URL for better granularity
            for feed_url in uncached_urls:
                # Filter items for this specific feed URL
                feed_items = [item for item in fresh_items if feed_url in item.source_url]
                cache_key = f"rss_{feed_url}"
                self._rss_cache[cache_key] = (feed_items, datetime.now())
                print(f"[RSS] Cached {len(feed_items)} items for {feed_url[:60]}...")

            all_items.extend(fresh_items)

        print(f"[RSS] Total items: {len(all_items)} ({len(all_items) - len([i for urls in uncached_urls for i in []])} from cache, {len(uncached_urls)} feeds fetched fresh)")

        return all_items[:limit]

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
        """Scrape X (Twitter) content with batch API calls to avoid N+1 queries."""
        import os
        import asyncio

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

        # Batch usernames (configurable batch size to respect Twitter rate limits: 300 req/15min)
        batch_size = ContentConstants.TWITTER_BATCH_SIZE

        for i in range(0, len(usernames), batch_size):
            batch = usernames[i:i+batch_size]
            cache_key_prefix = "x_"

            # Check cache for entire batch first
            cached_items = []
            uncached_usernames = []

            for username in batch:
                cache_key = f"{cache_key_prefix}{username}"
                if cache_key in self._twitter_cache:
                    items, cached_at = self._twitter_cache[cache_key]
                    age = (datetime.now() - cached_at).total_seconds()
                    if age < self._cache_ttl:
                        print(f"[Twitter] Using cached data for @{username} (age: {age:.0f}s)")
                        cached_items.extend(items)
                    else:
                        print(f"[Twitter] Cache expired for @{username} (age: {age:.0f}s > {self._cache_ttl}s)")
                        uncached_usernames.append(username)
                else:
                    uncached_usernames.append(username)

            all_items.extend(cached_items)

            # Fetch uncached usernames concurrently
            if uncached_usernames:
                print(f"[Twitter] Fetching {len(uncached_usernames)} usernames concurrently...")

                # Define async function to fetch with caching
                async def fetch_with_cache(username):
                    cache_key = f"{cache_key_prefix}{username}"
                    try:
                        print(f"[Twitter] Fetching fresh data for @{username}...")
                        items = scraper.fetch_user_timeline(username=username, limit=limit)

                        # Cache results (even if empty, to avoid repeated failures)
                        self._twitter_cache[cache_key] = (items, datetime.now())
                        print(f"[Twitter] Cached {len(items)} tweets from @{username}")

                        return items
                    except Exception as e:
                        print(f"[Twitter] Error fetching @{username}: {e}")
                        # Cache empty result to avoid immediate retry
                        self._twitter_cache[cache_key] = ([], datetime.now())
                        return []

                # Execute batch concurrently
                tasks = [fetch_with_cache(username) for username in uncached_usernames]
                batch_results = await asyncio.gather(*tasks, return_exceptions=True)

                # Collect results (filter out exceptions)
                for result in batch_results:
                    if isinstance(result, Exception):
                        print(f"[Twitter] Batch fetch exception: {result}")
                        continue
                    all_items.extend(result)

            # Rate limit pause between batches (Twitter: 300 requests/15min = 1 request/3sec)
            if i + batch_size < len(usernames):
                pause_seconds = ContentConstants.TWITTER_RATE_LIMIT_PAUSE_SECONDS
                print(f"[Twitter] Pausing {pause_seconds}s before next batch (rate limit protection)...")
                await asyncio.sleep(pause_seconds)

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

        # Verify user has access to this workspace
        if not self.supabase.user_has_workspace_access(user_id, workspace_id):
            raise ValueError("Access denied: User not in workspace")

        # Load content items
        items = self.supabase.load_content_items(
            workspace_id=workspace_id,
            days=days,
            source=source,
            limit=limit
        )

        # Map items to dict and add field aliases for backward compatibility
        # P2 #3: Enhanced documentation explaining why aliases exist and deprecation plan
        items_dict = []
        for item in items:
            item_data = item.to_dict()

            # FIELD ALIASES (for backward compatibility with older frontend versions):
            # These aliases are DEPRECATED and will be removed in API v2.
            # - 'url' → canonical field is 'source_url'
            # - 'source_type' → canonical field is 'source' (added by to_dict())
            # - 'published_at' → canonical field is 'created_at' (added by to_dict())
            #
            # Deprecation Timeline:
            # - 2025-01-25: Documented as deprecated (this comment)
            # - 2025-07-01: Add deprecation warnings to API responses (6 months)
            # - 2026-01-01: Remove aliases in API v2 (12 months total)
            #
            # Migration Guide: Frontend should use canonical field names now to prepare.
            item_data['url'] = item_data.get('source_url')
            items_dict.append(item_data)

        # P2 #4: Serialize response to omit None values (reduces payload size)
        serialized_items = serialize_content_list(items_dict)

        return {
            'workspace_id': workspace_id,
            'items': serialized_items,
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

        # Verify user has access to this workspace
        if not self.supabase.user_has_workspace_access(user_id, workspace_id):
            raise ValueError("Access denied: User not in workspace")

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

        # Verify user has access to this workspace
        if not self.supabase.user_has_workspace_access(user_id, existing_item['workspace_id']):
            print(f"[ContentService] ERROR: User does not have access to workspace - raising ValueError")
            raise ValueError("Access denied: User not in workspace")

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

    async def get_top_stories(
        self,
        user_id: str,
        workspace_id: str,
        limit: int = 5,
        hours: int = 24
    ) -> Dict[str, Any]:
        """
        Get top stories for carousel display.

        Fetches highest-scoring content from recent hours.
        Sorts by score DESC, then by created_at DESC.
        Optimized for carousel (minimal data).

        Args:
            user_id: User ID (for auth check)
            workspace_id: Workspace ID
            limit: Number of stories to return (default 5, max 10)
            hours: Time window in hours (default 24, max 168)

        Returns:
            Dict with top stories
        """
        # Verify user has access
        workspace = self.supabase.get_workspace(workspace_id)
        if not workspace:
            raise ValueError("Workspace not found")

        # Verify user has access to this workspace
        if not self.supabase.user_has_workspace_access(user_id, workspace_id):
            raise ValueError("Access denied: User not in workspace")

        # Cap limits to prevent abuse
        limit = min(limit, 10)
        hours = min(hours, 168)  # Max 1 week

        # Calculate cutoff time
        from datetime import timezone
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)

        # Load content items within time window (query slightly larger window for precision)
        days_to_query = max(1, (hours + 23) // 24)  # Round up to include full time window
        all_items = self.supabase.load_content_items(
            workspace_id=workspace_id,
            days=days_to_query,
            limit=1000  # Large limit for filtering
        )

        # Filter by scraped_at within time window
        filtered_items = [
            item for item in all_items
            if item.scraped_at and item.scraped_at >= cutoff
        ]

        # Apply recency boost (same algorithm as newsletter generation)
        now = datetime.now(timezone.utc)
        for item in filtered_items:
            age_hours = (now - item.scraped_at).total_seconds() / 3600

            # Boost multipliers (matching newsletter_service.py _apply_freshness_decay)
            if age_hours < 1:
                multiplier = 3.0    # 300% - Breaking news (< 1 hour)
            elif age_hours < 6:
                multiplier = 2.0    # 200% - Recent content (1-6 hours)
            elif age_hours < 24:
                multiplier = 1.0    # 100% - Current content (6-24 hours)
            elif age_hours < 168:  # 7 days
                multiplier = 0.5    # 50% - Aging content (1-7 days)
            else:
                multiplier = 0.1    # 10% - Stale content (> 7 days)

            # Calculate boosted score
            original_score = item.score or 0
            boosted_score = int(original_score * multiplier)

            # Store as temporary attribute for sorting
            item._boosted_score = boosted_score

            # Log for debugging
            boost_type = "BOOST" if multiplier > 1.0 else "DECAY" if multiplier < 1.0 else "NEUTRAL"
            print(f"[TopStories] [{boost_type}] '{item.title[:50]}...' - {age_hours:.1f}h old, {multiplier}x, Score: {original_score} → {boosted_score}")

        # Sort by boosted_score DESC, then by created_at DESC
        sorted_items = sorted(
            filtered_items,
            key=lambda x: (getattr(x, '_boosted_score', x.score or 0), x.created_at or datetime.min.replace(tzinfo=timezone.utc)),
            reverse=True
        )[:limit]

        # Convert to response format with time_ago
        stories = []
        for item in sorted_items:
            # Calculate human-readable time ago
            time_ago = self._calculate_time_ago(item.scraped_at)

            stories.append({
                'id': item.metadata.get('id'),  # ID is stored in metadata by database layer
                'title': item.title,
                'source': item.source,
                'source_url': item.source_url,
                'image_url': item.image_url,
                'score': item.score or 0,
                'created_at': item.created_at.isoformat() if item.created_at else None,
                'scraped_at': item.scraped_at.isoformat() if item.scraped_at else None,
                'time_ago': time_ago
            })

        return {
            'workspace_id': workspace_id,
            'stories': stories,
            'count': len(stories)
        }

    def _calculate_time_ago(self, dt: Optional[datetime]) -> str:
        """
        Calculate human-readable time ago string.

        Args:
            dt: Datetime to calculate from

        Returns:
            Human-readable string like "2 hours ago", "3 days ago"
        """
        if not dt:
            return "unknown"

        from datetime import timezone
        now = datetime.now(timezone.utc)

        # Ensure dt is timezone-aware
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)

        diff = now - dt
        seconds = diff.total_seconds()

        if seconds < 60:
            return "just now"
        elif seconds < 3600:
            minutes = int(seconds / 60)
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        elif seconds < 86400:
            hours = int(seconds / 3600)
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        elif seconds < 604800:
            days = int(seconds / 86400)
            return f"{days} day{'s' if days != 1 else ''} ago"
        else:
            weeks = int(seconds / 604800)
            return f"{weeks} week{'s' if weeks != 1 else ''} ago"


# Global service instance
content_service = ContentService()
