"""
Analytics data model for email tracking.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class EmailEvent:
    """
    Represents an email analytics event (open, click, etc.).
    """

    # Newsletter identification
    newsletter_id: str
    recipient: str

    # Event details
    event_type: str  # "sent", "opened", "clicked", "bounced"
    event_time: datetime

    # Click details (if event_type == "clicked")
    clicked_url: Optional[str] = None
    content_item_id: Optional[str] = None

    # Context
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None
    location: Optional[str] = None

    def to_dict(self):
        """Convert to dictionary for storage."""
        return {
            'newsletter_id': self.newsletter_id,
            'recipient': self.recipient,
            'event_type': self.event_type,
            'event_time': self.event_time.isoformat() if self.event_time else None,
            'clicked_url': self.clicked_url,
            'content_item_id': self.content_item_id,
            'user_agent': self.user_agent,
            'ip_address': self.ip_address,
            'location': self.location
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'EmailEvent':
        """Create from dictionary."""
        if isinstance(data.get('event_time'), str):
            data['event_time'] = datetime.fromisoformat(data['event_time'])
        return cls(**data)
