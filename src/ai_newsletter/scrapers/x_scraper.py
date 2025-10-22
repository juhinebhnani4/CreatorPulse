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
            # NOTE: wait_on_rate_limit=False to avoid blocking when rate limited
            # Instead, we'll catch the exception and return partial results
            self.client = tweepy.Client(
                bearer_token=self.bearer_token,
                consumer_key=self.api_key,
                consumer_secret=self.api_secret,
                access_token=self.access_token,
                access_token_secret=self.access_token_secret,
                wait_on_rate_limit=False
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
                tweet_fields=[
                    'created_at', 'public_metrics', 'entities', 'author_id',
                    'referenced_tweets',  # Get quoted tweets, RTs, replies
                    'conversation_id',    # Thread context
                    'attachments',        # Media references
                ],
                user_fields=['username', 'name'],
                expansions=[
                    'author_id',
                    'referenced_tweets.id',              # Get full quoted tweet content
                    'referenced_tweets.id.author_id',    # Get quoted tweet author
                    'attachments.media_keys',            # Get media details
                ],
                media_fields=['url', 'preview_image_url', 'type', 'duration_ms', 'alt_text'],
            )
            
            if not tweets.data:
                self.logger.warning("No tweets found")
                return []
            
            # Create user lookup and prepare includes data
            users = {user.id: user for user in tweets.includes.get('users', [])}
            includes = tweets.includes if hasattr(tweets, 'includes') else {}

            items = []
            for tweet in tweets.data:
                try:
                    item = self._parse_item(tweet, users, includes)
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
            # Check if it's a rate limit error
            error_msg = str(e).lower()
            if 'rate limit' in error_msg or '429' in error_msg:
                self.logger.warning(f"X API rate limit exceeded for query: {search_query}. Skipping this source.")
            else:
                self.logger.error(f"Error fetching from X: {e}")
            return []
    
    def _clean_tweet_text(self, text: str, strip_rt_prefix: bool = False) -> str:
        """
        Clean tweet text by removing URLs, extra whitespace, etc.

        Args:
            text: Raw tweet text
            strip_rt_prefix: If True, remove "RT @username:" prefix from retweets

        Returns:
            Cleaned text suitable for summary
        """
        import re

        # Remove "RT @username:" prefix if requested (for retweets)
        if strip_rt_prefix:
            text = re.sub(r'^RT\s+@\w+:\s*', '', text)

        # Remove URLs (both t.co shortlinks and full URLs)
        text = re.sub(r'https?://\S+', '', text)
        text = re.sub(r't\.co/\S+', '', text)

        # Remove extra whitespace (but preserve single spaces)
        text = re.sub(r'\s+', ' ', text)

        # Strip leading/trailing whitespace
        text = text.strip()

        return text

    def _extract_referenced_tweet(self, raw_item: Any, includes: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Extract quoted tweet, retweet source, or reply parent information.

        Args:
            raw_item: Tweet object from tweepy
            includes: Includes data from API response (tweets, users, media)

        Returns:
            Dict with referenced tweet info or None
            Format: {
                'type': 'quoted' | 'retweeted' | 'replied_to',
                'author': '@username',
                'author_name': 'Display Name',
                'text': 'Tweet text...',
                'url': 'https://twitter.com/user/status/123',
                'id': '123456789'
            }
        """
        if not hasattr(raw_item, 'referenced_tweets') or not raw_item.referenced_tweets:
            return None

        # Get the first referenced tweet (usually the most relevant)
        ref_tweet = raw_item.referenced_tweets[0]
        ref_type = ref_tweet.type  # 'quoted', 'retweeted', 'replied_to'

        # Find the full referenced tweet from includes
        if not includes or 'tweets' not in includes:
            return None

        referenced_tweets = {str(t.id): t for t in includes.get('tweets', [])}
        full_ref_tweet = referenced_tweets.get(str(ref_tweet.id))

        if not full_ref_tweet:
            return None

        # Find the author of the referenced tweet
        referenced_users = {str(u.id): u for u in includes.get('users', [])}
        ref_author = referenced_users.get(str(full_ref_tweet.author_id))

        if not ref_author:
            return None

        return {
            'type': ref_type,
            'author': f"@{ref_author.username}",
            'author_name': ref_author.name,
            'text': full_ref_tweet.text,
            'url': f"https://twitter.com/{ref_author.username}/status/{full_ref_tweet.id}",
            'id': str(full_ref_tweet.id)
        }

    def _extract_media_info(self, raw_item: Any, includes: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract media attachment information (photos, videos, GIFs).

        Args:
            raw_item: Tweet object from tweepy
            includes: Includes data from API response

        Returns:
            List of media info dicts
            Format: [{
                'type': 'photo' | 'video' | 'animated_gif',
                'url': 'https://...',
                'preview_url': 'https://...',
                'duration_ms': 12000,  # for videos
                'alt_text': 'Description'
            }]
        """
        if not hasattr(raw_item, 'attachments') or not raw_item.attachments:
            return []

        media_keys = raw_item.attachments.get('media_keys', [])
        if not media_keys or not includes or 'media' not in includes:
            return []

        # Create media lookup
        media_lookup = {m.media_key: m for m in includes.get('media', [])}

        media_info = []
        for key in media_keys:
            media = media_lookup.get(key)
            if not media:
                continue

            info = {
                'type': media.type,
                'alt_text': getattr(media, 'alt_text', None),
            }

            # Add URLs based on type
            if media.type == 'photo':
                info['url'] = getattr(media, 'url', None)
                info['preview_url'] = getattr(media, 'url', None)
            elif media.type in ('video', 'animated_gif'):
                info['preview_url'] = getattr(media, 'preview_image_url', None)
                info['url'] = getattr(media, 'url', None)  # May not be available
                if hasattr(media, 'duration_ms'):
                    info['duration_ms'] = media.duration_ms

            media_info.append(info)

        return media_info

    def _generate_summary(
        self,
        text: str,
        entities: Dict[str, Any],
        metrics: Dict[str, Any],
        referenced_tweet: Optional[Dict[str, Any]] = None,
        media_info: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """
        Generate intelligent summary for a tweet.

        Args:
            text: Tweet text
            entities: Tweet entities (hashtags, mentions, urls)
            metrics: Public metrics (likes, retweets, etc.)
            referenced_tweet: Optional referenced tweet info (quoted, retweeted, replied_to)
            media_info: Optional list of media attachments

        Returns:
            Intelligent summary string
        """
        # STEP 1: Clean the text first (remove URLs, etc.)
        # For retweets, also strip the "RT @username:" prefix
        is_retweet = referenced_tweet and referenced_tweet['type'] == 'retweeted'
        cleaned_text = self._clean_tweet_text(text, strip_rt_prefix=is_retweet)

        # If cleaning removed everything, use original text
        if not cleaned_text or len(cleaned_text) < 10:
            cleaned_text = self._clean_tweet_text(text, strip_rt_prefix=False)

        # Count entities
        hashtag_count = len(entities.get('hashtags', []))
        mention_count = len(entities.get('mentions', []))
        url_count = len(entities.get('urls', []))

        # Get engagement metrics
        likes = metrics.get('like_count', 0)
        retweets = metrics.get('retweet_count', 0)

        # STEP 2: Truncate cleaned text intelligently at sentence boundary
        max_length = 150
        if len(cleaned_text) <= max_length:
            summary = cleaned_text
        else:
            # Try to break at sentence boundary
            import re
            sentences = re.split(r'(?<=[.!?])\s+', cleaned_text)
            summary = ''
            for sentence in sentences:
                if len(summary) + len(sentence) + 1 <= max_length:
                    summary += sentence + ' '
                else:
                    break

            # If no complete sentences fit, truncate at word boundary
            if not summary.strip():
                words = cleaned_text[:max_length].rsplit(' ', 1)
                summary = words[0] + '...'
            else:
                summary = summary.strip()

        # STEP 3: Add quoted tweet context (if this is a quote tweet)
        if referenced_tweet and referenced_tweet['type'] == 'quoted':
            # Clean the quoted tweet text and truncate to ~80 chars
            quoted_text = self._clean_tweet_text(referenced_tweet['text'])
            if len(quoted_text) > 80:
                quoted_text = quoted_text[:77] + '...'

            summary += f" → Quoting {referenced_tweet['author']}: \"{quoted_text}\""

        # STEP 4: Add reply context (if this is a reply)
        elif referenced_tweet and referenced_tweet['type'] == 'replied_to':
            summary = f"→ Reply to {referenced_tweet['author']}: {summary}"

        # STEP 5: Add retweet context (if this is a retweet)
        elif referenced_tweet and referenced_tweet['type'] == 'retweeted':
            # For retweets, strip the "RT @user:" prefix and add clean context
            summary = f"→ Retweeted {referenced_tweet['author']}: {summary}"

        # STEP 6: Add media context
        context_parts = []

        if media_info and len(media_info) > 0:
            media_types = [m['type'] for m in media_info]
            if len(media_info) == 1:
                media_type = media_info[0]['type']
                if media_type == 'animated_gif':
                    context_parts.append('GIF')
                else:
                    context_parts.append(media_type)
            else:
                # Count by type
                photo_count = media_types.count('photo')
                video_count = media_types.count('video') + media_types.count('animated_gif')
                if photo_count > 0:
                    context_parts.append(f"{photo_count} image{'s' if photo_count > 1 else ''}")
                if video_count > 0:
                    context_parts.append(f"{video_count} video{'s' if video_count > 1 else ''}")

        # STEP 7: Add engagement metrics (only if significant)
        if likes > 100 or retweets > 50:
            context_parts.append(f"{likes} likes, {retweets} RT")

        # Only append context if we have something meaningful
        if context_parts:
            summary += f" [{', '.join(context_parts)}]"

        return summary

    def _parse_item(self, raw_item: Any, users: Dict[str, Any], includes: Dict[str, Any]) -> ContentItem:
        """
        Parse an X post into a ContentItem.

        Args:
            raw_item: Tweet object from tweepy
            users: Dictionary mapping user IDs to user objects
            includes: Includes data from API response (tweets, users, media)

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

        # Extract media URLs if present (for backward compatibility)
        image_url = None
        if 'urls' in entities:
            for url_entity in entities['urls']:
                if 'images' in url_entity:
                    image_url = url_entity['images'][0]['url']
                    break

        # Extract referenced tweet (quoted, retweeted, replied_to)
        referenced_tweet = self._extract_referenced_tweet(raw_item, includes)

        # Extract media attachments (photos, videos, GIFs)
        media_info = self._extract_media_info(raw_item, includes)

        # If we have media but no image_url from entities, use first media preview
        if not image_url and media_info and len(media_info) > 0:
            image_url = media_info[0].get('preview_url') or media_info[0].get('url')

        # Determine tweet type
        tweet_type = 'original'
        if referenced_tweet:
            tweet_type = referenced_tweet['type']  # 'quoted', 'retweeted', 'replied_to'

        # Get conversation_id if available (for thread context)
        conversation_id = getattr(raw_item, 'conversation_id', None)

        # Generate intelligent summary with rich context
        summary = self._generate_summary(text, entities, metrics, referenced_tweet, media_info)

        # Create ContentItem
        # Clean title text (remove URLs and RT prefix for retweets) and truncate intelligently
        clean_title = self._clean_tweet_text(text, strip_rt_prefix=(tweet_type == 'retweeted'))

        # Debug log to verify RT stripping is working
        if tweet_type == 'retweeted':
            self.logger.info(f"[DEBUG] RT detected - Original: '{text[:50]}...' -> Clean: '{clean_title[:50]}...'")

        if len(clean_title) > 100:
            # Truncate at word boundary
            clean_title = clean_title[:97].rsplit(' ', 1)[0] + '...'

        item = ContentItem(
            title=clean_title,
            source=self.source_name,
            source_url=tweet_url,
            created_at=created_at,
            content=text,
            summary=summary,
            author=author,  # Just username without @
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
                'tweet_type': tweet_type,
                'conversation_id': str(conversation_id) if conversation_id else None,
                'referenced_tweet': referenced_tweet,  # Full referenced tweet data
                'media_attachments': media_info,  # List of media attachments
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

