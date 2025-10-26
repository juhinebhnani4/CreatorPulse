"""
Trend detection model.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional


@dataclass
class Trend:
    """
    Represents a detected trend across content sources.
    """

    # Trend identification
    topic: str
    keywords: List[str] = field(default_factory=list)

    # Metrics
    strength_score: float = 0.0  # 0-1, how strong the trend is
    mention_count: int = 0
    velocity: float = 0.0  # Rate of growth

    # Sources
    sources: List[str] = field(default_factory=list)  # ['reddit', 'rss', etc.]
    source_count: int = 0

    # Evidence
    key_items: List = field(default_factory=list)  # ContentItem objects

    # Temporal data
    first_seen: Optional[datetime] = None
    peak_time: Optional[datetime] = None
    detected_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    # Context
    explanation: str = ""
    related_topics: List[str] = field(default_factory=list)

    # Classification
    confidence_level: str = "medium"  # "low", "medium", "high"

    def to_dict(self):
        """Convert to dictionary for storage."""
        return {
            'topic': self.topic,
            'keywords': self.keywords,
            'strength_score': self.strength_score,
            'mention_count': self.mention_count,
            'velocity': self.velocity,
            'sources': self.sources,
            'source_count': self.source_count,
            'first_seen': self.first_seen.isoformat() if self.first_seen else None,
            'peak_time': self.peak_time.isoformat() if self.peak_time else None,
            'detected_at': self.detected_at.isoformat() if self.detected_at else None,
            'explanation': self.explanation,
            'related_topics': self.related_topics,
            'confidence_level': self.confidence_level
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Trend':
        """Create from dictionary."""
        # Convert ISO strings to datetime
        for field in ['first_seen', 'peak_time', 'detected_at']:
            if isinstance(data.get(field), str):
                data[field] = datetime.fromisoformat(data[field])
        return cls(**data)

    def __repr__(self):
        return f"Trend(topic='{self.topic}', strength={self.strength_score:.2f}, sources={self.source_count})"
