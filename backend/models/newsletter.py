"""
Newsletter models (request/response schemas).
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class GenerateNewsletterRequest(BaseModel):
    """Request to generate a newsletter."""
    workspace_id: str = Field(..., description="Workspace ID")
    title: str = Field(..., min_length=1, max_length=200, description="Newsletter title")
    max_items: int = Field(default=15, ge=1, le=100, description="Maximum content items to include")
    days_back: int = Field(default=7, ge=1, le=90, description="Number of days to look back for content")
    sources: Optional[List[str]] = Field(default=None, description="Filter by sources (reddit, rss, blog, x, youtube)")
    tone: str = Field(default="professional", description="Newsletter tone")
    language: str = Field(default="en", description="Newsletter language")
    temperature: float = Field(default=0.7, ge=0.0, le=1.0, description="AI creativity level")
    model: Optional[str] = Field(default=None, description="AI model to use (overrides config)")
    use_openrouter: bool = Field(default=False, description="Use OpenRouter instead of OpenAI")


class NewsletterResponse(BaseModel):
    """Newsletter response schema."""
    id: str
    workspace_id: str
    title: str
    content_html: str  # Changed from html_content to match frontend
    content_text: Optional[str]  # Changed from plain_text_content to match frontend
    content_item_ids: List[str] = []
    content_items_count: int
    model_used: str
    temperature: Optional[float]
    tone: Optional[str]
    language: Optional[str]
    status: str
    generated_at: datetime
    sent_at: Optional[datetime]
    metadata: Dict[str, Any] = {}
    created_at: datetime
    updated_at: datetime


class NewsletterListResponse(BaseModel):
    """List newsletters response."""
    newsletters: List[NewsletterResponse]
    count: int
    workspace_id: str
    filters: Dict[str, Any] = {}


class NewsletterStatsResponse(BaseModel):
    """Newsletter statistics response."""
    workspace_id: str
    total_newsletters: int
    drafts_count: int
    sent_count: int
    scheduled_count: int
    total_content_items_used: int
    latest_newsletter: Optional[datetime]


class UpdateNewsletterRequest(BaseModel):
    """Update newsletter request."""
    model_config = {"extra": "ignore"}  # Pydantic v2 syntax - ignore extra fields like 'items' from frontend

    title: Optional[str] = Field(None, min_length=1, max_length=200)
    subject_line: Optional[str] = Field(None, max_length=200, description="Newsletter subject line (mapped to title)")  # Removed min_length to allow empty
    status: Optional[str] = Field(None, pattern="^(draft|sent|scheduled)$")
    sent_at: Optional[datetime] = None


class UpdateNewsletterHtmlRequest(BaseModel):
    """Request to update newsletter HTML after user edits."""
    html_content: str = Field(..., min_length=1, description="Updated HTML content")

