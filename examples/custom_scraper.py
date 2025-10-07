"""
Example of creating a custom scraper.

This example shows how to create a scraper for Hacker News.
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
import requests

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ai_newsletter.scrapers.base import BaseScraper
from ai_newsletter.models.content import ContentItem


class HackerNewsScraper(BaseScraper):
    """
    Example scraper for Hacker News.
    
    Demonstrates how to create a custom scraper by extending BaseScraper.
    """
    
    def __init__(self, **kwargs):
        """Initialize the Hacker News scraper."""
        super().__init__(
            source_name="hackernews",
            source_type="news",
            **kwargs
        )
        self.api_base = "https://hacker-news.firebaseio.com/v0"
    
    def fetch_content(
        self,
        limit: int = 10,
        story_type: str = "top",
        **kwargs
    ) -> List[ContentItem]:
        """
        Fetch stories from Hacker News.
        
        Args:
            limit: Number of stories to fetch
            story_type: Type of stories (top, best, new)
            **kwargs: Additional parameters
            
        Returns:
            List of ContentItem objects
        """
        try:
            # Get story IDs
            url = f"{self.api_base}/{story_type}stories.json"
            self.logger.info(f"Fetching {story_type} stories from Hacker News")
            
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            story_ids = response.json()[:limit]
            
            # Fetch each story
            items = []
            for story_id in story_ids:
                try:
                    story = self._fetch_story(story_id)
                    if story:
                        item = self._parse_item(story)
                        if self.validate_item(item):
                            items.append(item)
                except Exception as e:
                    self.logger.warning(f"Failed to fetch story {story_id}: {e}")
                    continue
            
            self.logger.info(f"Successfully fetched {len(items)} stories")
            return items
            
        except Exception as e:
            self.logger.error(f"Error fetching from Hacker News: {e}")
            return []
    
    def _fetch_story(self, story_id: int) -> Dict[str, Any]:
        """Fetch a single story by ID."""
        url = f"{self.api_base}/item/{story_id}.json"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    
    def _parse_item(self, raw_item: Dict[str, Any]) -> ContentItem:
        """
        Parse a Hacker News story into a ContentItem.
        
        Args:
            raw_item: Raw story data from HN API
            
        Returns:
            ContentItem object
        """
        story_id = raw_item.get('id')
        title = raw_item.get('title', 'Untitled')
        url = raw_item.get('url', f"https://news.ycombinator.com/item?id={story_id}")
        author = raw_item.get('by', 'unknown')
        score = raw_item.get('score', 0)
        comments = raw_item.get('descendants', 0)
        timestamp = raw_item.get('time', 0)
        created_at = datetime.fromtimestamp(timestamp) if timestamp else datetime.now()
        
        # HN-specific URL
        hn_url = f"https://news.ycombinator.com/item?id={story_id}"
        
        item = ContentItem(
            title=title,
            source=self.source_name,
            source_url=hn_url,
            created_at=created_at,
            author=author,
            author_url=f"https://news.ycombinator.com/user?id={author}",
            score=score,
            comments_count=comments,
            external_url=url if url != hn_url else None,
            metadata={
                'story_id': story_id,
                'story_type': raw_item.get('type', 'story'),
            }
        )
        
        return item


def main():
    """Demonstrate the custom scraper."""
    print("=" * 60)
    print("Custom Hacker News Scraper Example")
    print("=" * 60)
    
    # Create scraper instance
    scraper = HackerNewsScraper()
    
    # Fetch top stories
    print("\nFetching top stories...")
    items = scraper.fetch_content(limit=10, story_type="top")
    
    print(f"\nFetched {len(items)} stories")
    print("\nTop 5 stories:")
    print("-" * 60)
    
    for i, item in enumerate(items[:5], 1):
        print(f"\n{i}. {item.title}")
        print(f"   Score: {item.score} | Comments: {item.comments_count}")
        print(f"   Author: {item.author}")
        print(f"   Posted: {item.created_at.strftime('%Y-%m-%d %H:%M')}")
        print(f"   HN: {item.source_url}")
        if item.external_url:
            print(f"   Link: {item.external_url}")
    
    # Convert to DataFrame
    print("\n" + "=" * 60)
    print("DataFrame Summary")
    print("=" * 60)
    
    df = scraper.to_dataframe(items)
    print(f"\nShape: {df.shape}")
    print(f"\nColumns: {list(df.columns)}")
    print(f"\nAverage score: {df['score'].mean():.1f}")
    print(f"Total comments: {df['comments_count'].sum()}")
    
    # Filter high-scoring items
    high_score = scraper.filter_items(items, min_score=100)
    print(f"\nStories with score >= 100: {len(high_score)}")
    
    # Test source info
    print("\n" + "=" * 60)
    print("Scraper Info")
    print("=" * 60)
    
    info = scraper.get_source_info()
    print(f"Name: {info['name']}")
    print(f"Type: {info['type']}")
    print(f"Class: {info['class']}")
    
    print("\n" + "=" * 60)
    print("Example completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()

