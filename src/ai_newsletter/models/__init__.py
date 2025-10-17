"""Data models for the AI Newsletter scraper."""

from .content import ContentItem
from .style_profile import StyleProfile
from .trend import Trend
from .feedback import FeedbackItem
from .analytics import EmailEvent

__all__ = ["ContentItem", "StyleProfile", "Trend", "FeedbackItem", "EmailEvent"]

