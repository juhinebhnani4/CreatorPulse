"""
Content data models for scraped items.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any, List


@dataclass
class ContentItem:
    """
    Standard data model for scraped content.
    
    This class provides a unified interface for all content items,
    regardless of source (Reddit, RSS, Blog, X, etc.).
    """
    
    # Core fields (required)
    title: str
    source: str  # e.g., 'reddit', 'rss', 'blog', 'twitter'
    source_url: str
    created_at: datetime
    
    # Content fields
    content: Optional[str] = None
    summary: Optional[str] = None
    
    # Author/Creator information
    author: Optional[str] = None
    author_url: Optional[str] = None
    
    # Engagement metrics
    score: int = 0
    comments_count: int = 0
    shares_count: int = 0
    views_count: int = 0
    
    # Media and links
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    external_url: Optional[str] = None
    
    # Categorization
    tags: List[str] = field(default_factory=list)
    category: Optional[str] = None
    
    # Source-specific metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Internal fields
    scraped_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert ContentItem to dictionary."""
        return {
            'title': self.title,
            'source': self.source,
            'source_url': self.source_url,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'content': self.content,
            'summary': self.summary,
            'author': self.author,
            'author_url': self.author_url,
            'score': self.score,
            'comments_count': self.comments_count,
            'shares_count': self.shares_count,
            'views_count': self.views_count,
            'image_url': self.image_url,
            'video_url': self.video_url,
            'external_url': self.external_url,
            'tags': self.tags,
            'category': self.category,
            'metadata': self.metadata,
            'scraped_at': self.scraped_at.isoformat() if self.scraped_at else None,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ContentItem':
        """Create ContentItem from dictionary."""
        # Convert ISO strings back to datetime objects
        if isinstance(data.get('created_at'), str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        if isinstance(data.get('scraped_at'), str):
            data['scraped_at'] = datetime.fromisoformat(data['scraped_at'])
        
        return cls(**data)
    
    def __repr__(self) -> str:
        """String representation of ContentItem."""
        return f"ContentItem(title='{self.title[:50]}...', source='{self.source}')"

