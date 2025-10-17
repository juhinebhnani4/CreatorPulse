"""
Content models (request/response schemas).
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, Dict, Any, List
from datetime import datetime


class ScrapeContentRequest(BaseModel):
    """Request to scrape content for a workspace."""
    workspace_id: str = Field(..., description="Workspace ID to scrape content for")
    sources: Optional[List[str]] = Field(
        default=None,
        description="Specific sources to scrape (reddit, rss, blog, x, youtube). If None, scrapes all enabled sources from config."
    )
    limit_per_source: Optional[int] = Field(
        default=None,
        description="Override limit per source (uses config limits if None)"
    )


class ContentItemResponse(BaseModel):
    """Content item response schema."""
    id: str
    workspace_id: str
    title: str
    source: str  # reddit, rss, blog, x, youtube
    source_type: str  # Same as source (for frontend compatibility)
    source_url: str
    content: Optional[str]
    summary: Optional[str]
    author: Optional[str]
    author_url: Optional[str]
    score: int = 0
    comments_count: int = 0
    shares_count: int = 0
    views_count: int = 0
    image_url: Optional[str]
    video_url: Optional[str]
    external_url: Optional[str]
    tags: List[str] = []
    category: Optional[str]
    created_at: datetime  # When content was originally created
    scraped_at: datetime  # When we scraped it
    metadata: Dict[str, Any] = {}


class ContentListResponse(BaseModel):
    """List content items response."""
    items: List[ContentItemResponse]
    count: int
    workspace_id: str
    filters: Dict[str, Any] = {}


class ContentStatsResponse(BaseModel):
    """Content statistics response."""
    workspace_id: str
    total_items: int
    items_by_source: Dict[str, int]
    items_last_24h: int
    items_last_7d: int
    latest_scrape: Optional[datetime]


class ScrapeJobResponse(BaseModel):
    """Scrape job response."""
    job_id: str
    workspace_id: str
    status: str  # pending, running, completed, failed
    sources: List[str]
    items_scraped: int
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    error: Optional[str]
