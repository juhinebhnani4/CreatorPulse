"""
Unit tests for base scraper.
"""

import pytest
from datetime import datetime
from typing import List, Any

from src.ai_newsletter.scrapers.base import BaseScraper
from src.ai_newsletter.models.content import ContentItem


class MockScraper(BaseScraper):
    """Mock scraper for testing."""
    
    def __init__(self):
        super().__init__(source_name="mock", source_type="test")
    
    def fetch_content(self, limit: int = 10, **kwargs) -> List[ContentItem]:
        """Mock fetch implementation."""
        items = []
        for i in range(limit):
            item = ContentItem(
                title=f"Test Item {i}",
                source=self.source_name,
                source_url=f"https://example.com/{i}",
                created_at=datetime.now(),
                score=i * 10,
                comments_count=i * 2
            )
            items.append(item)
        return items
    
    def _parse_item(self, raw_item: Any) -> ContentItem:
        """Mock parse implementation."""
        return ContentItem(
            title="Parsed Item",
            source=self.source_name,
            source_url="https://example.com",
            created_at=datetime.now()
        )


class TestBaseScraper:
    """Tests for BaseScraper class."""
    
    def test_scraper_initialization(self):
        """Test scraper initialization."""
        scraper = MockScraper()
        
        assert scraper.source_name == "mock"
        assert scraper.source_type == "test"
        assert scraper.logger is not None
    
    def test_fetch_content(self):
        """Test fetching content."""
        scraper = MockScraper()
        items = scraper.fetch_content(limit=5)
        
        assert len(items) == 5
        assert all(isinstance(item, ContentItem) for item in items)
        assert all(item.source == "mock" for item in items)
    
    def test_to_dataframe(self):
        """Test converting items to DataFrame."""
        scraper = MockScraper()
        items = scraper.fetch_content(limit=3)
        df = scraper.to_dataframe(items)
        
        assert len(df) == 3
        assert 'title' in df.columns
        assert 'source' in df.columns
        assert 'score' in df.columns
    
    def test_to_dataframe_empty(self):
        """Test converting empty list to DataFrame."""
        scraper = MockScraper()
        df = scraper.to_dataframe([])
        
        assert len(df) == 0
    
    def test_validate_item_valid(self):
        """Test validating a valid item."""
        scraper = MockScraper()
        item = ContentItem(
            title="Valid Item",
            source="test",
            source_url="https://example.com",
            created_at=datetime.now()
        )
        
        assert scraper.validate_item(item) is True
    
    def test_validate_item_missing_title(self):
        """Test validating item with missing title."""
        scraper = MockScraper()
        item = ContentItem(
            title="",
            source="test",
            source_url="https://example.com",
            created_at=datetime.now()
        )
        
        assert scraper.validate_item(item) is False
    
    def test_filter_items_by_score(self):
        """Test filtering items by score."""
        scraper = MockScraper()
        items = scraper.fetch_content(limit=10)
        filtered = scraper.filter_items(items, min_score=50)
        
        assert all(item.score >= 50 for item in filtered)
        assert len(filtered) < len(items)
    
    def test_filter_items_by_comments(self):
        """Test filtering items by comments."""
        scraper = MockScraper()
        items = scraper.fetch_content(limit=10)
        filtered = scraper.filter_items(items, min_comments=10)
        
        assert all(item.comments_count >= 10 for item in filtered)
    
    def test_get_source_info(self):
        """Test getting source information."""
        scraper = MockScraper()
        info = scraper.get_source_info()
        
        assert info['name'] == 'mock'
        assert info['type'] == 'test'
        assert 'MockScraper' in info['class']
    
    def test_scraper_repr(self):
        """Test scraper string representation."""
        scraper = MockScraper()
        repr_str = repr(scraper)
        
        assert 'MockScraper' in repr_str
        assert 'mock' in repr_str

