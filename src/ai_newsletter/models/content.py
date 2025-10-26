"""
Content data models for scraped items.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
import logging

# P2 #5: Add logging for from_dict() field removal warnings
logger = logging.getLogger(__name__)


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
    scraped_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert ContentItem to dictionary.

        Automatically extracts database ID from metadata if present.
        This ensures API responses always include the 'id' field.
        """
        created_at_iso = self.created_at.isoformat() if self.created_at else None
        result = {
            'title': self.title,
            'source': self.source,
            'source_type': self.source,  # Added for frontend compatibility (same as source)
            'source_url': self.source_url,
            'created_at': created_at_iso,
            'published_at': created_at_iso,  # Frontend expects this field
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

        # Extract database ID from metadata if present (stored there by database layer)
        # This ensures the API response includes 'id' as a top-level field
        if 'id' in self.metadata:
            result['id'] = self.metadata['id']

        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ContentItem':
        """Create ContentItem from dictionary."""
        # Create a copy to avoid modifying original
        data = data.copy()

        # P2 #5: Log when removing fields (helps debug data loss issues)
        # Remove frontend-specific fields that aren't in the dataclass
        removed_fields = []

        if 'source_type' in data:
            removed_fields.append(f"source_type={data['source_type']}")
        data.pop('source_type', None)  # Added by to_dict() for frontend

        if 'url' in data:
            removed_fields.append(f"url={data['url'][:50]}...")
        data.pop('url', None)  # Added by backend for frontend

        if 'published_at' in data:
            removed_fields.append(f"published_at={data['published_at']}")
        data.pop('published_at', None)  # Alias for created_at

        if 'adjusted_score' in data:
            removed_fields.append(f"adjusted_score={data['adjusted_score']}")
        data.pop('adjusted_score', None)  # Added by feedback service

        if 'original_score' in data:
            removed_fields.append(f"original_score={data['original_score']}")
        data.pop('original_score', None)  # Added by feedback/trend boosting

        if 'adjustments' in data:
            removed_fields.append("adjustments=<dict>")
        data.pop('adjustments', None)  # Added by feedback service

        if 'trend_boosted' in data:
            removed_fields.append(f"trend_boosted={data['trend_boosted']}")
        data.pop('trend_boosted', None)  # Added by trend boosting

        if 'id' in data:
            removed_fields.append(f"id={data['id']}")
        data.pop('id', None)  # Database ID, not part of ContentItem dataclass

        # Log if we removed any fields (debug level - not a warning unless unexpected)
        if removed_fields:
            logger.debug(f"from_dict() removed expected alias fields: {', '.join(removed_fields)}")

        # Check for unexpected fields (these might indicate data model mismatch)
        expected_fields = set(cls.__dataclass_fields__.keys())
        unexpected = set(data.keys()) - expected_fields
        if unexpected:
            logger.warning(
                f"from_dict() received unexpected fields that will be IGNORED: {unexpected}. "
                f"This may indicate a data model mismatch between frontend and backend."
            )

        # Convert ISO strings back to datetime objects
        if isinstance(data.get('created_at'), str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        if isinstance(data.get('scraped_at'), str):
            data['scraped_at'] = datetime.fromisoformat(data['scraped_at'])

        return cls(**data)
    
    def __repr__(self) -> str:
        """String representation of ContentItem."""
        return f"ContentItem(title='{self.title[:50]}...', source='{self.source}')"

