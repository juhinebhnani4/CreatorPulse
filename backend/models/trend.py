"""
Trend Models

Pydantic models for trend detection and analysis.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from uuid import UUID


class TrendBase(BaseModel):
    """Base trend attributes."""

    topic: str = Field(
        description="Main topic/theme of the trend",
        examples=["AI Agents", "LLM Fine-tuning", "Vector Databases"]
    )
    keywords: List[str] = Field(
        default_factory=list,
        description="Related keywords and phrases",
        examples=[["ai", "agents", "automation"]]
    )
    strength_score: float = Field(
        ge=0.0,
        le=1.0,
        description="Trend strength score (0.0 to 1.0)",
        examples=[0.85, 0.62]
    )
    mention_count: int = Field(
        default=0,
        description="Total number of mentions",
        examples=[15, 42]
    )
    velocity: float = Field(
        default=0.0,
        description="Mention velocity (percentage increase or mentions per hour)",
        examples=[25.5, 120.0]
    )
    sources: List[str] = Field(
        default_factory=list,
        description="Sources where trend appears",
        examples=[["reddit", "rss", "youtube"]]
    )
    source_count: int = Field(
        default=0,
        description="Number of different sources",
        examples=[3, 5]
    )
    explanation: Optional[str] = Field(
        None,
        description="AI-generated explanation of why it's trending",
        examples=["This topic is gaining traction due to increased discussion about AI automation..."]
    )
    related_topics: List[str] = Field(
        default_factory=list,
        description="Related trending topics",
        examples=[["Machine Learning", "OpenAI"]]
    )
    confidence_level: str = Field(
        default="medium",
        description="Confidence level (low, medium, high)",
        examples=["high", "medium", "low"]
    )
    is_active: bool = Field(
        default=True,
        description="Whether trend is currently active",
        examples=[True, False]
    )


class TrendCreate(TrendBase):
    """Create new trend."""

    workspace_id: UUID = Field(
        description="Workspace ID",
        examples=["3353d8f1-4bec-465c-9518-91ccc35d2898"]
    )
    key_content_item_ids: List[UUID] = Field(
        default_factory=list,
        description="IDs of key content items evidencing this trend",
        examples=[["a1b2c3d4-5678-90ab-cdef-1234567890ab"]]
    )
    first_seen: Optional[datetime] = Field(
        None,
        description="When trend was first detected"
    )
    peak_time: Optional[datetime] = Field(
        None,
        description="When trend peaked"
    )


class TrendUpdate(BaseModel):
    """Update existing trend."""

    strength_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    mention_count: Optional[int] = Field(None, ge=0)
    velocity: Optional[float] = Field(None)
    sources: Optional[List[str]] = Field(None)
    source_count: Optional[int] = Field(None, ge=0)
    explanation: Optional[str] = Field(None)
    related_topics: Optional[List[str]] = Field(None)
    confidence_level: Optional[str] = Field(None)
    is_active: Optional[bool] = Field(None)
    peak_time: Optional[datetime] = Field(None)


class TrendResponse(TrendBase):
    """Complete trend response."""

    id: UUID = Field(description="Trend ID")
    workspace_id: UUID = Field(description="Workspace ID")
    key_content_item_ids: List[UUID] = Field(
        default_factory=list,
        description="Key content item IDs"
    )
    first_seen: Optional[datetime] = Field(None, description="First seen timestamp")
    peak_time: Optional[datetime] = Field(None, description="Peak time timestamp")
    detected_at: datetime = Field(description="Detection timestamp")
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: datetime = Field(description="Last update timestamp")

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": "a1b2c3d4-5678-90ab-cdef-1234567890ab",
                "workspace_id": "3353d8f1-4bec-465c-9518-91ccc35d2898",
                "topic": "AI Agents",
                "keywords": ["ai", "agents", "automation"],
                "strength_score": 0.85,
                "mention_count": 15,
                "velocity": 25.5,
                "sources": ["reddit", "rss", "youtube"],
                "source_count": 3,
                "explanation": "This topic is trending due to increased discussion...",
                "related_topics": ["Machine Learning", "LLMs"],
                "confidence_level": "high",
                "is_active": True,
                "key_content_item_ids": [],
                "first_seen": "2025-01-15T08:00:00Z",
                "peak_time": "2025-01-16T14:30:00Z",
                "detected_at": "2025-01-16T10:00:00Z",
                "created_at": "2025-01-16T10:00:00Z",
                "updated_at": "2025-01-16T10:00:00Z"
            }
        }
    }


class TrendListResponse(BaseModel):
    """List of trends with metadata."""

    trends: List[TrendResponse] = Field(description="List of trends")
    count: int = Field(description="Total count")
    workspace_id: UUID = Field(description="Workspace ID")
    detected_at: datetime = Field(
        default_factory=datetime.now,
        description="When this list was generated"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "trends": [
                    {
                        "id": "uuid",
                        "topic": "AI Agents",
                        "strength_score": 0.85,
                        "mention_count": 15
                    }
                ],
                "count": 1,
                "workspace_id": "3353d8f1-4bec-465c-9518-91ccc35d2898",
                "detected_at": "2025-01-16T10:00:00Z"
            }
        }
    }


class TrendHistoryItem(BaseModel):
    """Historical trend data point."""

    detected_date: datetime = Field(description="Date trend was detected")
    topic: str = Field(description="Trend topic")
    strength_score: float = Field(description="Strength score at that time")
    mention_count: int = Field(description="Mention count at that time")

    model_config = {
        "json_schema_extra": {
            "example": {
                "detected_date": "2025-01-15",
                "topic": "AI Agents",
                "strength_score": 0.85,
                "mention_count": 15
            }
        }
    }


class TrendHistoryResponse(BaseModel):
    """Trend history over time."""

    workspace_id: UUID = Field(description="Workspace ID")
    history: List[TrendHistoryItem] = Field(description="Historical trend data")
    days_back: int = Field(description="Number of days included")
    count: int = Field(description="Total data points")

    model_config = {
        "json_schema_extra": {
            "example": {
                "workspace_id": "3353d8f1-4bec-465c-9518-91ccc35d2898",
                "history": [
                    {
                        "detected_date": "2025-01-15",
                        "topic": "AI Agents",
                        "strength_score": 0.85,
                        "mention_count": 15
                    }
                ],
                "days_back": 30,
                "count": 1
            }
        }
    }


class DetectTrendsRequest(BaseModel):
    """Request to detect trends from content."""

    workspace_id: UUID = Field(description="Workspace ID")
    days_back: int = Field(
        default=1,
        ge=1,
        le=30,
        description="Number of days to analyze",
        examples=[1, 7, 30]
    )
    max_trends: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Maximum number of trends to return",
        examples=[5, 10]
    )
    min_confidence: float = Field(
        default=0.6,
        ge=0.0,
        le=1.0,
        description="Minimum confidence threshold",
        examples=[0.6, 0.75]
    )
    sources: Optional[List[str]] = Field(
        None,
        description="Filter by specific sources (None = all sources)",
        examples=[["reddit", "rss"]]
    )


class DetectTrendsResponse(BaseModel):
    """Response from trend detection."""

    success: bool = Field(description="Whether detection succeeded")
    message: str = Field(description="Status message")
    trends: List[TrendResponse] = Field(description="Detected trends")
    analysis_summary: Dict[str, Any] = Field(
        description="Analysis summary",
        examples=[
            {
                "content_items_analyzed": 150,
                "topics_found": 12,
                "trends_detected": 5,
                "confidence_threshold": 0.6,
                "time_range_days": 7
            }
        ]
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "success": True,
                "message": "Detected 5 trends from 150 content items",
                "trends": [
                    {
                        "id": "uuid",
                        "topic": "AI Agents",
                        "strength_score": 0.85,
                        "mention_count": 15
                    }
                ],
                "analysis_summary": {
                    "content_items_analyzed": 150,
                    "topics_found": 12,
                    "trends_detected": 5,
                    "confidence_threshold": 0.6
                }
            }
        }
    }


class HistoricalContentCreate(BaseModel):
    """Create historical content record."""

    workspace_id: UUID = Field(description="Workspace ID")
    content_item_id: Optional[UUID] = Field(None, description="Original content item ID")
    title: str = Field(description="Content title")
    summary: Optional[str] = Field(None, description="Content summary")
    content: Optional[str] = Field(None, description="Full content text")
    source: str = Field(description="Content source")
    source_url: Optional[str] = Field(None, description="Source URL")
    score: int = Field(default=0, description="Engagement score")
    created_at: datetime = Field(description="Original content creation time")
    keywords: List[str] = Field(default_factory=list, description="Extracted keywords")
    topic_cluster: Optional[int] = Field(None, description="Topic cluster ID")


class HistoricalContentResponse(BaseModel):
    """Historical content response."""

    id: UUID = Field(description="Historical content ID")
    workspace_id: UUID = Field(description="Workspace ID")
    content_item_id: Optional[UUID] = Field(None, description="Original content item ID")
    title: str = Field(description="Title")
    summary: Optional[str] = Field(None, description="Summary")
    source: str = Field(description="Source")
    source_url: Optional[str] = Field(None, description="Source URL")
    score: int = Field(description="Score")
    created_at: datetime = Field(description="Original creation time")
    scraped_at: datetime = Field(description="When we saved it")
    expires_at: datetime = Field(description="Expiration time")
    keywords: List[str] = Field(description="Keywords")
    topic_cluster: Optional[int] = Field(None, description="Cluster ID")

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": "uuid",
                "workspace_id": "3353d8f1-4bec-465c-9518-91ccc35d2898",
                "content_item_id": "uuid",
                "title": "AI Agents Are Transforming Workflows",
                "summary": "Discussion of how AI agents...",
                "source": "reddit",
                "source_url": "https://reddit.com/...",
                "score": 125,
                "created_at": "2025-01-15T10:00:00Z",
                "scraped_at": "2025-01-15T11:00:00Z",
                "expires_at": "2025-01-22T11:00:00Z",
                "keywords": ["ai", "agents", "automation"],
                "topic_cluster": 3
            }
        }
    }


class TrendAnalysisSummary(BaseModel):
    """Summary of trend analysis."""

    workspace_id: UUID = Field(description="Workspace ID")
    total_trends: int = Field(description="Total trends detected")
    active_trends: int = Field(description="Currently active trends")
    top_sources: List[Dict[str, Any]] = Field(
        description="Top sources by trend count",
        examples=[[{"source": "reddit", "count": 5}]]
    )
    avg_strength_score: float = Field(description="Average trend strength")
    total_content_analyzed: int = Field(description="Total content items analyzed")
    analysis_period_days: int = Field(description="Analysis period in days")

    model_config = {
        "json_schema_extra": {
            "example": {
                "workspace_id": "3353d8f1-4bec-465c-9518-91ccc35d2898",
                "total_trends": 12,
                "active_trends": 5,
                "top_sources": [
                    {"source": "reddit", "count": 5},
                    {"source": "rss", "count": 4}
                ],
                "avg_strength_score": 0.72,
                "total_content_analyzed": 150,
                "analysis_period_days": 7
            }
        }
    }
