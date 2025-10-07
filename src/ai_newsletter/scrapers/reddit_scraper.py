"""
Reddit scraper implementation.
"""

import requests
from datetime import datetime
from typing import List, Dict, Any, Optional

from .base import BaseScraper
from ..models.content import ContentItem


class RedditScraper(BaseScraper):
    """
    Scraper for Reddit subreddits.
    
    Fetches posts from specified subreddits using Reddit's public JSON API.
    
    Example:
        scraper = RedditScraper()
        items = scraper.fetch_content(subreddit='AI_Agents', limit=25)
        df = scraper.to_dataframe(items)
    """
    
    def __init__(self, user_agent: str = "AINewsletterScraper/1.0", **kwargs):
        """
        Initialize the Reddit scraper.
        
        Args:
            user_agent: User agent string for requests
            **kwargs: Additional configuration options
        """
        super().__init__(source_name="reddit", source_type="social", **kwargs)
        
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': user_agent})
        self.base_url = "https://www.reddit.com"
    
    def fetch_content(
        self,
        limit: int = 25,
        subreddit: str = "AI_Agents",
        sort: str = "hot",
        time_filter: str = "all",
        **kwargs
    ) -> List[ContentItem]:
        """
        Fetch posts from a Reddit subreddit.
        
        Args:
            limit: Number of posts to fetch (max 100)
            subreddit: Name of the subreddit (without r/)
            sort: Sort method ('hot', 'new', 'top', 'rising')
            time_filter: Time filter for 'top' sort ('hour', 'day', 'week', 'month', 'year', 'all')
            **kwargs: Additional parameters
            
        Returns:
            List of ContentItem objects
        """
        url = f"{self.base_url}/r/{subreddit}/{sort}.json"
        params = {
            'limit': min(limit, 100),  # Reddit API limit
            't': time_filter if sort == 'top' else None
        }
        
        try:
            self.logger.info(f"Fetching {limit} posts from r/{subreddit}")
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            items = []
            
            for post_data in data['data']['children']:
                try:
                    item = self._parse_item(post_data['data'])
                    if self.validate_item(item):
                        items.append(item)
                except Exception as e:
                    self.logger.warning(f"Failed to parse item: {e}")
                    continue
            
            self.logger.info(f"Successfully fetched {len(items)} valid items")
            return items
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error fetching data from Reddit: {e}")
            return []
        except (KeyError, ValueError) as e:
            self.logger.error(f"Error parsing Reddit data: {e}")
            return []
    
    def _parse_item(self, raw_item: Dict[str, Any]) -> ContentItem:
        """
        Parse a Reddit post into a ContentItem.
        
        Args:
            raw_item: Raw post data from Reddit API
            
        Returns:
            ContentItem object
        """
        # Extract basic information
        title = raw_item.get('title', '')
        author = raw_item.get('author', '[deleted]')
        permalink = f"{self.base_url}{raw_item.get('permalink', '')}"
        created_utc = datetime.fromtimestamp(raw_item.get('created_utc', 0))
        
        # Extract content
        selftext = raw_item.get('selftext', '')
        url = raw_item.get('url', '')
        
        # Engagement metrics
        score = raw_item.get('score', 0)
        num_comments = raw_item.get('num_comments', 0)
        upvote_ratio = raw_item.get('upvote_ratio', 0.0)
        
        # Media
        thumbnail = raw_item.get('thumbnail', '')
        image_url = thumbnail if thumbnail and thumbnail.startswith('http') else None
        
        # Check for video
        video_url = None
        if 'media' in raw_item and raw_item['media']:
            if 'reddit_video' in raw_item['media']:
                video_url = raw_item['media']['reddit_video'].get('fallback_url')
        
        # Tags and categorization
        tags = []
        if raw_item.get('link_flair_text'):
            tags.append(raw_item['link_flair_text'])
        if raw_item.get('over_18'):
            tags.append('NSFW')
        if raw_item.get('spoiler'):
            tags.append('Spoiler')
        
        # Create ContentItem
        item = ContentItem(
            title=title,
            source=self.source_name,
            source_url=permalink,
            created_at=created_utc,
            content=selftext if selftext else None,
            summary=selftext[:200] + '...' if len(selftext) > 200 else selftext,
            author=author,
            author_url=f"{self.base_url}/user/{author}" if author != '[deleted]' else None,
            score=score,
            comments_count=num_comments,
            image_url=image_url,
            video_url=video_url,
            external_url=url if not raw_item.get('is_self') else None,
            tags=tags,
            category=raw_item.get('link_flair_text'),
            metadata={
                'subreddit': raw_item.get('subreddit'),
                'upvote_ratio': upvote_ratio,
                'is_self': raw_item.get('is_self', False),
                'domain': raw_item.get('domain', ''),
                'stickied': raw_item.get('stickied', False),
                'gilded': raw_item.get('gilded', 0),
                'awards': raw_item.get('total_awards_received', 0),
            }
        )
        
        return item
    
    def fetch_subreddit(self, subreddit: str, limit: int = 25, **kwargs) -> List[ContentItem]:
        """
        Convenience method to fetch from a specific subreddit.
        
        Args:
            subreddit: Subreddit name
            limit: Number of posts to fetch
            **kwargs: Additional parameters
            
        Returns:
            List of ContentItem objects
        """
        return self.fetch_content(subreddit=subreddit, limit=limit, **kwargs)
    
    def fetch_multiple_subreddits(
        self,
        subreddits: List[str],
        limit_per_subreddit: int = 10
    ) -> List[ContentItem]:
        """
        Fetch posts from multiple subreddits.
        
        Args:
            subreddits: List of subreddit names
            limit_per_subreddit: Number of posts to fetch per subreddit
            
        Returns:
            Combined list of ContentItem objects from all subreddits
        """
        all_items = []
        
        for subreddit in subreddits:
            self.logger.info(f"Fetching from r/{subreddit}")
            items = self.fetch_content(subreddit=subreddit, limit=limit_per_subreddit)
            all_items.extend(items)
        
        return all_items

