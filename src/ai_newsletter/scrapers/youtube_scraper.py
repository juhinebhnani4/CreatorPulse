"""
YouTube scraper implementation.
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
import logging

try:
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
except ImportError:
    build = None
    HttpError = None

from .base import BaseScraper
from ..models.content import ContentItem


class YouTubeScraper(BaseScraper):
    """
    Scraper for YouTube channels and videos.
    
    Fetches videos from specified YouTube channels using YouTube Data API v3.
    
    Example:
        scraper = YouTubeScraper(api_key="your_api_key")
        items = scraper.fetch_content(channel_id="UC_x5XG1OV2P6uZZ5FSM9Ttw", limit=25)
        df = scraper.to_dataframe(items)
    """
    
    def __init__(self, api_key: str, **kwargs):
        """
        Initialize the YouTube scraper.
        
        Args:
            api_key: YouTube Data API v3 key
            **kwargs: Additional configuration options
        """
        super().__init__(source_name="youtube", source_type="video", **kwargs)
        
        if not api_key:
            raise ValueError("YouTube API key is required")
        
        self.api_key = api_key
        self.youtube = None
        
        # Initialize YouTube API client
        try:
            self.youtube = build('youtube', 'v3', developerKey=api_key)
            self.logger.info("YouTube API client initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize YouTube API client: {e}")
            raise
    
    def fetch_content(
        self,
        limit: int = 25,
        channel_id: Optional[str] = None,
        channel_username: Optional[str] = None,
        playlist_id: Optional[str] = None,
        search_query: Optional[str] = None,
        order: str = "date",
        published_after: Optional[datetime] = None,
        **kwargs
    ) -> List[ContentItem]:
        """
        Fetch videos from YouTube.
        
        Args:
            limit: Number of videos to fetch (max 50 per request)
            channel_id: YouTube channel ID
            channel_username: YouTube channel username (without @)
            playlist_id: YouTube playlist ID
            search_query: Search query for videos
            order: Sort order ('date', 'relevance', 'rating', 'viewCount', 'title')
            published_after: Only fetch videos published after this date
            **kwargs: Additional parameters
            
        Returns:
            List of ContentItem objects
        """
        if not self.youtube:
            self.logger.error("YouTube API client not initialized")
            return []
        
        try:
            videos = []
            
            if channel_id:
                videos = self._fetch_channel_videos(
                    channel_id, limit, order, published_after
                )
            elif channel_username:
                videos = self._fetch_channel_by_username(
                    channel_username, limit, order, published_after
                )
            elif playlist_id:
                videos = self._fetch_playlist_videos(
                    playlist_id, limit, order
                )
            elif search_query:
                videos = self._search_videos(
                    search_query, limit, order, published_after
                )
            else:
                self.logger.error("Must specify channel_id, channel_username, playlist_id, or search_query")
                return []
            
            # Parse videos into ContentItems
            items = []
            for video in videos:
                try:
                    item = self._parse_item(video)
                    if self.validate_item(item):
                        items.append(item)
                except Exception as e:
                    self.logger.warning(f"Failed to parse video: {e}")
                    continue
            
            self.logger.info(f"Successfully fetched {len(items)} valid videos")
            return items
            
        except HttpError as e:
            self.logger.error(f"YouTube API error: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Error fetching YouTube data: {e}")
            return []
    
    def _fetch_channel_videos(
        self,
        channel_id: str,
        limit: int,
        order: str,
        published_after: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Fetch videos from a specific channel."""
        # Get uploads playlist ID
        channel_response = self.youtube.channels().list(
            part='contentDetails',
            id=channel_id
        ).execute()

        if 'items' not in channel_response or not channel_response['items']:
            self.logger.error(f"Channel not found: {channel_id}")
            return []

        uploads_playlist_id = channel_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
        
        # Fetch videos from uploads playlist
        return self._fetch_playlist_videos(uploads_playlist_id, limit, order)
    
    def _fetch_channel_by_username(
        self,
        username: str,
        limit: int,
        order: str,
        published_after: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Fetch videos from a channel by username with fallback to search."""

        # Method 1: Try forUsername (works for legacy usernames)
        try:
            self.logger.info(f"Trying forUsername lookup: {username}")
            channel_response = self.youtube.channels().list(
                part='id',
                forUsername=username
            ).execute()

            if channel_response.get('items'):
                channel_id = channel_response['items'][0]['id']
                self.logger.info(f"OK: Found by username: {username} → {channel_id}")
                return self._fetch_channel_videos(channel_id, limit, order, published_after)
        except Exception as e:
            self.logger.warning(f"forUsername failed for {username}: {e}")

        # Method 2: Search for channel (works for handles and names)
        try:
            self.logger.info(f"Searching YouTube for channel: {username}")
            search_response = self.youtube.search().list(
                part='snippet',
                q=username,
                type='channel',
                maxResults=5
            ).execute()

            if search_response.get('items'):
                # Find best match (exact name or handle match)
                for item in search_response['items']:
                    channel_title = item['snippet']['title'].lower()
                    channel_id = item['id']['channelId']

                    # Exact match or very close match
                    if username.lower() in channel_title or channel_title in username.lower():
                        self.logger.info(f"OK: Found by search: {username} → {channel_id} ({item['snippet']['title']})")
                        return self._fetch_channel_videos(channel_id, limit, order, published_after)

                # No exact match, use first result
                channel_id = search_response['items'][0]['id']['channelId']
                channel_title = search_response['items'][0]['snippet']['title']
                self.logger.warning(f"WARNING:  Using first search result for '{username}': {channel_title}")
                return self._fetch_channel_videos(channel_id, limit, order, published_after)

        except HttpError as e:
            self.logger.error(f"YouTube API search failed for {username}: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error searching for {username}: {e}")

        self.logger.error(f"ERROR: Channel not found: {username}")
        return []
    
    def _fetch_playlist_videos(
        self,
        playlist_id: str,
        limit: int,
        order: str
    ) -> List[Dict[str, Any]]:
        """Fetch videos from a playlist."""
        videos = []
        next_page_token = None
        
        while len(videos) < limit and next_page_token is not None or next_page_token is None:
            # Get playlist items
            # Ensure maxResults is at least 1
            playlist_response = self.youtube.playlistItems().list(
                part='snippet',
                playlistId=playlist_id,
                maxResults=max(1, min(50, limit - len(videos))),
                pageToken=next_page_token
            ).execute()

            if 'items' not in playlist_response:
                self.logger.error(f"No items in playlist response for playlist: {playlist_id}")
                break

            video_ids = [item['snippet']['resourceId']['videoId'] for item in playlist_response['items']]
            
            if not video_ids:
                break
            
            # Get detailed video information
            videos_response = self.youtube.videos().list(
                part='snippet,statistics,contentDetails',
                id=','.join(video_ids)
            ).execute()

            if 'items' in videos_response:
                videos.extend(videos_response['items'])
            next_page_token = playlist_response.get('nextPageToken')
            
            if not next_page_token:
                break
        
        return videos[:limit]
    
    def _search_videos(
        self,
        query: str,
        limit: int,
        order: str,
        published_after: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Search for videos."""
        search_params = {
            'part': 'snippet',
            'q': query,
            'type': 'video',
            'maxResults': min(50, limit),
            'order': order
        }
        
        if published_after:
            search_params['publishedAfter'] = published_after.isoformat() + 'Z'
        
        search_response = self.youtube.search().list(**search_params).execute()

        if 'items' not in search_response:
            self.logger.error("No items in search response")
            return []

        video_ids = [item['id']['videoId'] for item in search_response['items']]

        if not video_ids:
            return []

        # Get detailed video information
        videos_response = self.youtube.videos().list(
            part='snippet,statistics,contentDetails',
            id=','.join(video_ids)
        ).execute()

        if 'items' not in videos_response:
            self.logger.error("No items in videos response")
            return []

        return videos_response['items']
    
    def _parse_item(self, raw_item: Dict[str, Any]) -> ContentItem:
        """
        Parse a YouTube video into a ContentItem.
        
        Args:
            raw_item: Raw video data from YouTube API
            
        Returns:
            ContentItem object
        """
        snippet = raw_item['snippet']
        statistics = raw_item.get('statistics', {})
        content_details = raw_item.get('contentDetails', {})
        
        # Extract basic information
        title = snippet.get('title', '')
        channel_title = snippet.get('channelTitle', '')
        channel_id = snippet.get('channelId', '')
        video_id = raw_item['id']
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        channel_url = f"https://www.youtube.com/channel/{channel_id}"
        
        # Parse published date
        published_at = datetime.fromisoformat(
            snippet.get('publishedAt', '').replace('Z', '+00:00')
        )
        
        # Extract content
        description = snippet.get('description', '')
        summary = self._generate_summary(snippet, title)

        # Engagement metrics
        view_count = int(statistics.get('viewCount', 0))
        like_count = int(statistics.get('likeCount', 0))
        comment_count = int(statistics.get('commentCount', 0))
        
        # Media
        thumbnails = snippet.get('thumbnails', {})
        image_url = None
        if 'high' in thumbnails:
            image_url = thumbnails['high'].get('url')
        elif 'medium' in thumbnails:
            image_url = thumbnails['medium'].get('url')
        elif 'default' in thumbnails:
            image_url = thumbnails['default'].get('url')
        
        # Video duration
        duration = content_details.get('duration', '')
        
        # Tags and categorization
        tags = snippet.get('tags', [])
        category_id = snippet.get('categoryId', '')
        
        # Create ContentItem
        item = ContentItem(
            title=title,
            source=self.source_name,
            source_url=video_url,
            created_at=published_at,
            content=description,
            summary=summary,
            author=channel_title,
            author_url=channel_url,
            score=like_count,
            comments_count=comment_count,
            views_count=view_count,
            image_url=image_url,
            video_url=video_url,
            tags=tags,
            category=category_id,
            metadata={
                'video_id': video_id,
                'channel_id': channel_id,
                'duration': duration,
                'category_id': category_id,
                'live_broadcast_content': snippet.get('liveBroadcastContent', 'none'),
                'default_language': snippet.get('defaultLanguage', ''),
                'default_audio_language': snippet.get('defaultAudioLanguage', ''),
            }
        )
        
        return item

    def _generate_summary(self, snippet: Dict[str, Any], title: str) -> str:
        """
        Generate smart summary for YouTube video with intelligent fallbacks.

        Fallback chain:
        1. Description (if available)
        2. Channel name + video title
        3. Video title only

        Args:
            snippet: Video snippet data from YouTube API
            title: Video title

        Returns:
            Descriptive summary string (never empty)
        """
        description = snippet.get('description', '').strip()
        channel_title = snippet.get('channelTitle', '')

        # Priority 1: Use description if available
        if description:
            return description[:200] + '...' if len(description) > 200 else description

        # Priority 2: Channel + title
        if channel_title:
            title_preview = title[:150] + '...' if len(title) > 150 else title
            return f"{channel_title}: {title_preview}"

        # Fallback: Just title
        return title[:200] + '...' if len(title) > 200 else title if title else "YouTube video"

    def fetch_channel(self, channel_id: str, limit: int = 25, **kwargs) -> List[ContentItem]:
        """
        Convenience method to fetch from a specific channel.
        
        Args:
            channel_id: YouTube channel ID
            limit: Number of videos to fetch
            **kwargs: Additional parameters
            
        Returns:
            List of ContentItem objects
        """
        return self.fetch_content(channel_id=channel_id, limit=limit, **kwargs)
    
    def fetch_multiple_channels(
        self,
        channel_ids: List[str],
        limit_per_channel: int = 10
    ) -> List[ContentItem]:
        """
        Fetch videos from multiple channels.
        
        Args:
            channel_ids: List of YouTube channel IDs
            limit_per_channel: Number of videos to fetch per channel
            
        Returns:
            Combined list of ContentItem objects from all channels
        """
        all_items = []
        
        for channel_id in channel_ids:
            self.logger.info(f"Fetching from channel: {channel_id}")
            items = self.fetch_content(channel_id=channel_id, limit=limit_per_channel)
            all_items.extend(items)
        
        return all_items
    
    def search_videos(self, query: str, limit: int = 25, **kwargs) -> List[ContentItem]:
        """
        Search for videos on YouTube.
        
        Args:
            query: Search query
            limit: Number of videos to fetch
            **kwargs: Additional parameters
            
        Returns:
            List of ContentItem objects
        """
        return self.fetch_content(search_query=query, limit=limit, **kwargs)








