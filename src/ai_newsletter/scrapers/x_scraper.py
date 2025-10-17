"""
X (Twitter) scraper implementation.

Note: This is a template/placeholder implementation.
X (Twitter) requires authentication and has strict API rate limits.
For production use, you'll need to:
1. Register for X API access at https://developer.twitter.com/
2. Obtain API keys and access tokens
3. Install tweepy: pip install tweepy
4. Configure authentication in the config file

This implementation shows the structure and can be extended with actual API calls.
"""

from datetime import datetime
from typing import List, Dict, Any, Optional

from .base import BaseScraper
from ..models.content import ContentItem


class XScraper(BaseScraper):
    """
    Scraper for X (formerly Twitter) posts.
    
    This is a template implementation showing how to structure an X scraper.
    Requires X API credentials to function.
    
    Example (with credentials configured):
        scraper = XScraper(
            api_key='your_api_key',
            api_secret='your_api_secret',
            access_token='your_access_token',
            access_token_secret='your_access_token_secret'
        )
        items = scraper.fetch_content(query='#AI', limit=10)
        df = scraper.to_dataframe(items)
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        access_token: Optional[str] = None,
        access_token_secret: Optional[str] = None,
        bearer_token: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize the X scraper.
        
        Args:
            api_key: X API key
            api_secret: X API secret
            access_token: Access token
            access_token_secret: Access token secret
            bearer_token: Bearer token (for v2 API)
            **kwargs: Additional configuration options
        """
        super().__init__(source_name="x", source_type="social", **kwargs)
        
        self.api_key = api_key
        self.api_secret = api_secret
        self.access_token = access_token
        self.access_token_secret = access_token_secret
        self.bearer_token = bearer_token
        
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the X API client if credentials are provided."""
        if not all([self.api_key, self.api_secret, self.access_token, self.access_token_secret]):
            self.logger.warning(
                "X API credentials not provided. "
                "This scraper requires API access. "
                "Visit https://developer.twitter.com/ to get credentials."
            )
            return
        
        try:
            import tweepy
            
            # Initialize tweepy client
            self.client = tweepy.Client(
                bearer_token=self.bearer_token,
                consumer_key=self.api_key,
                consumer_secret=self.api_secret,
                access_token=self.access_token,
                access_token_secret=self.access_token_secret,
                wait_on_rate_limit=True
            )
            
            self.logger.info("X API client initialized successfully")
            
        except ImportError:
            self.logger.error(
                "tweepy not installed. Install it with: pip install tweepy"
            )
        except Exception as e:
            self.logger.error(f"Failed to initialize X API client: {e}")
    
    def fetch_content(
        self,
        limit: int = 10,
        query: Optional[str] = None,
        username: Optional[str] = None,
        hashtag: Optional[str] = None,
        **kwargs
    ) -> List[ContentItem]:
        """
        Fetch posts from X.
        
        Args:
            limit: Number of posts to fetch (max 100 per request)
            query: Search query
            username: Username to fetch posts from
            hashtag: Hashtag to search for
            **kwargs: Additional parameters
            
        Returns:
            List of ContentItem objects
        """
        if not self.client:
            self.logger.error("X API client not initialized. Cannot fetch content.")
            return []
        
        try:
            import tweepy
            
            # Build query
            search_query = query
            if hashtag:
                search_query = f"#{hashtag.lstrip('#')}"
            elif username:
                search_query = f"from:{username.lstrip('@')}"
            
            if not search_query:
                self.logger.warning("No query, username, or hashtag provided")
                return []
            
            self.logger.info(f"Searching X for: {search_query}")
            
            # Fetch tweets using API v2
            # X API requires max_results between 10-100
            tweets = self.client.search_recent_tweets(
                query=search_query,
                max_results=max(10, min(limit, 100)),
                tweet_fields=['created_at', 'public_metrics', 'entities', 'author_id'],
                user_fields=['username', 'name'],
                expansions=['author_id'],
            )
            
            if not tweets.data:
                self.logger.warning("No tweets found")
                return []
            
            # Create user lookup
            users = {user.id: user for user in tweets.includes.get('users', [])}
            
            items = []
            for tweet in tweets.data:
                try:
                    item = self._parse_item(tweet, users)
                    if self.validate_item(item):
                        items.append(item)
                except Exception as e:
                    self.logger.warning(f"Failed to parse tweet: {e}")
                    continue
            
            self.logger.info(f"Successfully fetched {len(items)} tweets")
            return items
            
        except ImportError:
            self.logger.error("tweepy not installed")
            return []
        except Exception as e:
            self.logger.error(f"Error fetching from X: {e}")
            return []
    
    def _parse_item(self, raw_item: Any, users: Dict[str, Any]) -> ContentItem:
        """
        Parse an X post into a ContentItem.
        
        Args:
            raw_item: Tweet object from tweepy
            users: Dictionary mapping user IDs to user objects
            
        Returns:
            ContentItem object
        """
        # Get author info
        author_id = raw_item.author_id
        user = users.get(author_id)
        author = user.username if user else 'unknown'
        author_name = user.name if user else 'Unknown'
        
        # Extract tweet data
        tweet_id = raw_item.id
        text = raw_item.text
        created_at = raw_item.created_at
        
        # Public metrics
        metrics = raw_item.public_metrics
        likes = metrics.get('like_count', 0)
        retweets = metrics.get('retweet_count', 0)
        replies = metrics.get('reply_count', 0)
        
        # Calculate engagement score
        score = likes + (retweets * 2) + (replies * 3)
        
        # Extract hashtags and mentions
        tags = []
        entities = raw_item.entities or {}
        
        if 'hashtags' in entities:
            tags.extend([tag['tag'] for tag in entities['hashtags']])
        
        # URLs
        tweet_url = f"https://twitter.com/{author}/status/{tweet_id}"
        
        # Extract media URLs if present
        image_url = None
        if 'urls' in entities:
            for url_entity in entities['urls']:
                if 'images' in url_entity:
                    image_url = url_entity['images'][0]['url']
                    break
        
        # Create ContentItem
        item = ContentItem(
            title=text[:100] + ('...' if len(text) > 100 else ''),
            source=self.source_name,
            source_url=tweet_url,
            created_at=created_at,
            content=text,
            summary=text,
            author=f"@{author}",
            author_url=f"https://twitter.com/{author}",
            score=score,
            comments_count=replies,
            shares_count=retweets,
            image_url=image_url,
            tags=tags,
            metadata={
                'tweet_id': str(tweet_id),
                'likes': likes,
                'retweets': retweets,
                'replies': replies,
                'author_name': author_name,
            }
        )
        
        return item
    
    def fetch_user_timeline(self, username: str, limit: int = 10) -> List[ContentItem]:
        """
        Convenience method to fetch posts from a specific user.
        
        Args:
            username: X username (with or without @)
            limit: Number of posts to fetch
            
        Returns:
            List of ContentItem objects
        """
        return self.fetch_content(username=username, limit=limit)
    
    def fetch_hashtag(self, hashtag: str, limit: int = 10) -> List[ContentItem]:
        """
        Convenience method to fetch posts with a specific hashtag.
        
        Args:
            hashtag: Hashtag to search for (with or without #)
            limit: Number of posts to fetch
            
        Returns:
            List of ContentItem objects
        """
        return self.fetch_content(hashtag=hashtag, limit=limit)

