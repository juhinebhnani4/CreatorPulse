"""
Response models for newsletter service with type validation.

Provides Pydantic models for all newsletter service method responses
to ensure type safety and data validation.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime


class NewsletterGenerationResponse(BaseModel):
    """Response model for newsletter generation."""

    newsletter: Dict[str, Any] = Field(..., description="Generated newsletter data")
    content_items_count: int = Field(..., ge=0, description="Number of content items included")
    sources_used: List[str] = Field(default_factory=list, description="List of content sources used")
    trends_applied: int = Field(default=0, ge=0, description="Number of trends applied")
    trend_boosted_items: int = Field(default=0, ge=0, description="Number of items boosted by trends")
    style_profile_applied: bool = Field(default=False, description="Whether style profile was applied")
    feedback_adjusted_items: int = Field(default=0, ge=0, description="Number of items adjusted by feedback")

    @validator('content_items_count')
    def validate_content_count(cls, v):
        """Validate content items count is reasonable."""
        if v > 1000:
            raise ValueError("Content items count exceeds maximum (1000)")
        return v

    @validator('sources_used')
    def validate_sources(cls, v):
        """Validate sources list."""
        if len(v) > 100:
            raise ValueError("Too many sources (max 100)")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "newsletter": {"id": "123", "title": "Weekly Newsletter"},
                "content_items_count": 15,
                "sources_used": ["reddit", "hackernews"],
                "trends_applied": 3,
                "trend_boosted_items": 5,
                "style_profile_applied": True,
                "feedback_adjusted_items": 8
            }
        }


class NewsletterListResponse(BaseModel):
    """Response model for newsletter list."""

    workspace_id: str = Field(..., description="Workspace ID")
    newsletters: List[Dict[str, Any]] = Field(default_factory=list, description="List of newsletters")
    count: int = Field(..., ge=0, description="Total count of newsletters")
    filters: Dict[str, Any] = Field(default_factory=dict, description="Applied filters")

    @validator('count')
    def validate_count_matches_list(cls, v, values):
        """Ensure count matches newsletter list length."""
        if 'newsletters' in values and v != len(values['newsletters']):
            raise ValueError("Count does not match newsletters list length")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "workspace_id": "workspace-123",
                "newsletters": [
                    {"id": "1", "title": "Newsletter 1"},
                    {"id": "2", "title": "Newsletter 2"}
                ],
                "count": 2,
                "filters": {"status": "sent", "limit": 50}
            }
        }


class NewsletterDetailResponse(BaseModel):
    """Response model for newsletter details."""

    id: str = Field(..., description="Newsletter ID")
    workspace_id: str = Field(..., description="Workspace ID")
    title: str = Field(..., description="Newsletter title")
    content_html: Optional[str] = Field(None, description="HTML content", alias="html_content")
    content_text: Optional[str] = Field(None, description="Plain text content")
    status: str = Field(..., description="Newsletter status")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    sent_at: Optional[datetime] = Field(None, description="Sent timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    class Config:
        populate_by_name = True  # Allow both content_html and html_content

    @validator('status')
    def validate_status(cls, v):
        """Validate newsletter status."""
        valid_statuses = ['draft', 'sent', 'scheduled', 'failed']
        if v not in valid_statuses:
            raise ValueError(f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
        return v

    class Config:
        populate_by_name = True  # Allow both content_html and html_content
        json_schema_extra = {
            "example": {
                "id": "newsletter-123",
                "workspace_id": "workspace-456",
                "title": "Weekly AI Newsletter",
                "content_html": "<html>...</html>",
                "content_text": "Plain text version...",
                "status": "sent",
                "created_at": "2025-01-20T10:00:00Z",
                "sent_at": "2025-01-20T11:00:00Z",
                "metadata": {
                    "trends_used": ["AI Safety", "GPT-5"],
                    "style_profile_applied": True
                }
            }
        }


class NewsletterStatsResponse(BaseModel):
    """Response model for newsletter statistics."""

    workspace_id: str = Field(..., description="Workspace ID")
    total_newsletters: int = Field(..., ge=0, description="Total newsletters created")
    sent_count: int = Field(default=0, ge=0, description="Number of sent newsletters")
    draft_count: int = Field(default=0, ge=0, description="Number of draft newsletters")
    scheduled_count: int = Field(default=0, ge=0, description="Number of scheduled newsletters")
    avg_content_items: float = Field(default=0.0, ge=0.0, description="Average content items per newsletter")
    most_used_sources: List[str] = Field(default_factory=list, description="Most frequently used sources")

    @validator('avg_content_items')
    def validate_avg_items(cls, v):
        """Validate average content items is reasonable."""
        if v > 100:
            raise ValueError("Average content items exceeds reasonable limit")
        return round(v, 2)

    class Config:
        json_schema_extra = {
            "example": {
                "workspace_id": "workspace-123",
                "total_newsletters": 50,
                "sent_count": 45,
                "draft_count": 3,
                "scheduled_count": 2,
                "avg_content_items": 12.5,
                "most_used_sources": ["reddit", "hackernews", "youtube"]
            }
        }


class NewsletterUpdateResponse(BaseModel):
    """Response model for newsletter updates."""

    id: str = Field(..., description="Newsletter ID")
    updated_fields: List[str] = Field(default_factory=list, description="Fields that were updated")
    success: bool = Field(..., description="Whether update was successful")
    message: Optional[str] = Field(None, description="Optional message")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "newsletter-123",
                "updated_fields": ["status", "sent_at"],
                "success": True,
                "message": "Newsletter status updated to 'sent'"
            }
        }


# Export all response models
__all__ = [
    'NewsletterGenerationResponse',
    'NewsletterListResponse',
    'NewsletterDetailResponse',
    'NewsletterStatsResponse',
    'NewsletterUpdateResponse'
]
