"""
AI Newsletter Scraper Package
A modular and extensible content scraping framework for AI-related news sources.
"""

__version__ = "1.0.0"
__author__ = "AI Newsletter Team"

from .scrapers.base import BaseScraper
from .scrapers.reddit_scraper import RedditScraper
from .scrapers.rss_scraper import RSSFeedScraper
from .scrapers.blog_scraper import BlogScraper
from .models.content import ContentItem

__all__ = [
    "BaseScraper",
    "RedditScraper",
    "RSSFeedScraper",
    "BlogScraper",
    "ContentItem",
]

