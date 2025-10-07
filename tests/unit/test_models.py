"""
Unit tests for data models.
"""

import pytest
from datetime import datetime
from src.ai_newsletter.models.content import ContentItem


class TestContentItem:
    """Tests for ContentItem model."""
    
    def test_create_content_item(self):
        """Test creating a basic ContentItem."""
        item = ContentItem(
            title="Test Title",
            source="test",
            source_url="https://example.com/test",
            created_at=datetime.now()
        )
        
        assert item.title == "Test Title"
        assert item.source == "test"
        assert item.source_url == "https://example.com/test"
        assert isinstance(item.created_at, datetime)
    
    def test_content_item_to_dict(self):
        """Test converting ContentItem to dictionary."""
        item = ContentItem(
            title="Test",
            source="test",
            source_url="https://example.com",
            created_at=datetime(2024, 1, 1, 12, 0, 0),
            score=100,
            tags=["ai", "ml"]
        )
        
        data = item.to_dict()
        
        assert data['title'] == "Test"
        assert data['source'] == "test"
        assert data['score'] == 100
        assert data['tags'] == ["ai", "ml"]
        assert isinstance(data['created_at'], str)
    
    def test_content_item_from_dict(self):
        """Test creating ContentItem from dictionary."""
        data = {
            'title': 'Test',
            'source': 'test',
            'source_url': 'https://example.com',
            'created_at': '2024-01-01T12:00:00',
            'score': 50,
            'tags': ['test']
        }
        
        item = ContentItem.from_dict(data)
        
        assert item.title == 'Test'
        assert item.score == 50
        assert isinstance(item.created_at, datetime)
    
    def test_content_item_defaults(self):
        """Test ContentItem default values."""
        item = ContentItem(
            title="Test",
            source="test",
            source_url="https://example.com",
            created_at=datetime.now()
        )
        
        assert item.score == 0
        assert item.comments_count == 0
        assert item.tags == []
        assert item.metadata == {}
        assert item.content is None
    
    def test_content_item_repr(self):
        """Test ContentItem string representation."""
        item = ContentItem(
            title="This is a very long title that should be truncated",
            source="test",
            source_url="https://example.com",
            created_at=datetime.now()
        )
        
        repr_str = repr(item)
        assert "ContentItem" in repr_str
        assert "test" in repr_str

