"""
Feedback data model for learning from user preferences.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class FeedbackItem:
    """
    Represents user feedback on newsletter content.

    This is used to improve future content selection and generation.
    """

    # Content identification
    title: str
    source: str
    source_url: str

    # Feedback
    rating: str  # "positive", "negative", "neutral"
    included_in_final: bool = True

    # Edit tracking
    original_summary: Optional[str] = None
    edited_summary: Optional[str] = None
    edit_distance: float = 0.0  # 0-1, how much it changed

    # Context
    newsletter_date: datetime = None
    feedback_date: datetime = None

    # Learning signals
    engagement_prediction: Optional[float] = None
    actual_engagement: Optional[float] = None

    def to_dict(self):
        """Convert to dictionary for storage."""
        return {
            'title': self.title,
            'source': self.source,
            'source_url': self.source_url,
            'rating': self.rating,
            'included_in_final': self.included_in_final,
            'original_summary': self.original_summary,
            'edited_summary': self.edited_summary,
            'edit_distance': self.edit_distance,
            'newsletter_date': self.newsletter_date.isoformat() if self.newsletter_date else None,
            'feedback_date': self.feedback_date.isoformat() if self.feedback_date else None,
            'engagement_prediction': self.engagement_prediction,
            'actual_engagement': self.actual_engagement
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'FeedbackItem':
        """Create from dictionary."""
        # Convert ISO strings to datetime
        for field in ['newsletter_date', 'feedback_date']:
            if isinstance(data.get(field), str):
                data[field] = datetime.fromisoformat(data[field])
        return cls(**data)
