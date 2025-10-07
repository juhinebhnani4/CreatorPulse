"""
RSS Feed scraper implementation.
"""

import feedparser
from datetime import datetime
from typing import List, Dict, Any, Optional
from time import mktime

from .base import BaseScraper
from ..models.content import ContentItem


class RSSFeedScraper(BaseScraper):
    """
    Scraper for RSS/Atom feeds.
    
    Fetches content from RSS feeds, commonly used by blogs, news sites, and podcasts.
    
    Example:
        scraper = RSSFeedScraper()
        items = scraper.fetch_content(
            feed_url='https://blog.example.com/feed.xml',
            limit=10
        )
        df = scraper.to_dataframe(items)
    """
    
    def __init__(self, **kwargs):
        """
        Initialize the RSS feed scraper.
        
        Args:
            **kwargs: Additional configuration options
        """
        super().__init__(source_name="rss", source_type="feed", **kwargs)
    
    def fetch_content(
        self,
        limit: int = 10,
        feed_url: Optional[str] = None,
        feed_urls: Optional[List[str]] = None,
        **kwargs
    ) -> List[ContentItem]:
        """
        Fetch entries from RSS/Atom feeds.
        
        Args:
            limit: Number of entries to fetch per feed
            feed_url: Single feed URL to fetch from
            feed_urls: List of feed URLs to fetch from
            **kwargs: Additional parameters
            
        Returns:
            List of ContentItem objects
        """
        urls = []
        if feed_url:
            urls.append(feed_url)
        if feed_urls:
            urls.extend(feed_urls)
        
        if not urls:
            self.logger.warning("No feed URLs provided")
            return []
        
        all_items = []
        
        for url in urls:
            try:
                self.logger.info(f"Fetching feed from {url}")
                feed = feedparser.parse(url)
                
                if feed.bozo:
                    self.logger.warning(f"Feed parsing warning for {url}: {feed.bozo_exception}")
                
                entries = feed.entries[:limit]
                
                for entry in entries:
                    try:
                        item = self._parse_item(entry)
                        item.metadata['feed_url'] = url
                        item.metadata['feed_title'] = feed.feed.get('title', '')
                        
                        if self.validate_item(item):
                            all_items.append(item)
                    except Exception as e:
                        self.logger.warning(f"Failed to parse entry: {e}")
                        continue
                
                self.logger.info(f"Successfully fetched {len(entries)} entries from {url}")
                
            except Exception as e:
                self.logger.error(f"Error fetching feed {url}: {e}")
                continue
        
        return all_items
    
    def _parse_item(self, raw_item: Any) -> ContentItem:
        """
        Parse an RSS entry into a ContentItem.
        
        Args:
            raw_item: feedparser entry object
            
        Returns:
            ContentItem object
        """
        # Extract basic information
        title = raw_item.get('title', 'Untitled')
        link = raw_item.get('link', '')
        
        # Parse published date
        created_at = datetime.now()
        if hasattr(raw_item, 'published_parsed') and raw_item.published_parsed:
            created_at = datetime.fromtimestamp(mktime(raw_item.published_parsed))
        elif hasattr(raw_item, 'updated_parsed') and raw_item.updated_parsed:
            created_at = datetime.fromtimestamp(mktime(raw_item.updated_parsed))
        
        # Extract content
        content = ''
        summary = ''
        
        if hasattr(raw_item, 'content') and raw_item.content:
            content = raw_item.content[0].get('value', '')
        elif hasattr(raw_item, 'description'):
            content = raw_item.get('description', '')
        
        if hasattr(raw_item, 'summary'):
            summary = raw_item.get('summary', '')
        else:
            summary = content[:200] + '...' if len(content) > 200 else content
        
        # Extract author
        author = None
        author_url = None
        if hasattr(raw_item, 'author'):
            author = raw_item.get('author', '')
        elif hasattr(raw_item, 'author_detail'):
            author_detail = raw_item.get('author_detail', {})
            author = author_detail.get('name', '')
            author_url = author_detail.get('href', '')
        
        # Extract media
        image_url = None
        if hasattr(raw_item, 'media_content') and raw_item.media_content:
            image_url = raw_item.media_content[0].get('url', '')
        elif hasattr(raw_item, 'media_thumbnail') and raw_item.media_thumbnail:
            image_url = raw_item.media_thumbnail[0].get('url', '')
        elif hasattr(raw_item, 'enclosures') and raw_item.enclosures:
            for enclosure in raw_item.enclosures:
                if 'image' in enclosure.get('type', ''):
                    image_url = enclosure.get('href', '')
                    break
        
        # Extract tags
        tags = []
        if hasattr(raw_item, 'tags') and raw_item.tags:
            tags = [tag.get('term', '') for tag in raw_item.tags if tag.get('term')]
        
        # Category
        category = tags[0] if tags else None
        
        # Create ContentItem
        item = ContentItem(
            title=title,
            source=self.source_name,
            source_url=link,
            created_at=created_at,
            content=content,
            summary=summary,
            author=author,
            author_url=author_url,
            image_url=image_url,
            external_url=link,
            tags=tags,
            category=category,
            metadata={
                'guid': raw_item.get('id', raw_item.get('guid', '')),
                'comments_url': raw_item.get('comments', ''),
            }
        )
        
        return item
    
    def fetch_ai_feeds(self, limit: int = 10) -> List[ContentItem]:
        """
        Convenience method to fetch from popular AI-related RSS feeds.
        
        Args:
            limit: Number of entries per feed
            
        Returns:
            List of ContentItem objects
        """
        ai_feeds = [
            'https://blog.openai.com/rss/',
            'https://www.anthropic.com/rss.xml',
            'https://ai.googleblog.com/feeds/posts/default',
            'https://blogs.microsoft.com/ai/feed/',
        ]
        
        return self.fetch_content(feed_urls=ai_feeds, limit=limit)

