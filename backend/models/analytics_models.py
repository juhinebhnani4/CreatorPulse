"""
Pydantic models for analytics API requests and responses.
"""

from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


# =============================================================================
# EVENT MODELS
# =============================================================================

class EmailEventBase(BaseModel):
    """Base model for email analytics events."""
    workspace_id: UUID
    newsletter_id: UUID
    event_type: str = Field(..., description="Event type: sent, delivered, opened, clicked, bounced, unsubscribed, spam_reported")
    recipient_email: str

    class Config:
        json_schema_extra = {
            "example": {
                "workspace_id": "123e4567-e89b-12d3-a456-426614174000",
                "newsletter_id": "123e4567-e89b-12d3-a456-426614174001",
                "event_type": "opened",
                "recipient_email": "user@example.com"
            }
        }


class EmailEventCreate(EmailEventBase):
    """Model for creating email analytics events."""
    subscriber_id: Optional[UUID] = None
    clicked_url: Optional[str] = None
    content_item_id: Optional[UUID] = None
    bounce_type: Optional[str] = Field(None, description="Bounce type: hard or soft")
    bounce_reason: Optional[str] = None
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None


class EmailEventResponse(EmailEventBase):
    """Model for email event responses."""
    id: UUID
    subscriber_id: Optional[UUID] = None
    event_time: datetime
    clicked_url: Optional[str] = None
    content_item_id: Optional[UUID] = None
    bounce_type: Optional[str] = None
    bounce_reason: Optional[str] = None
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None
    location_city: Optional[str] = None
    location_country: Optional[str] = None
    device_type: Optional[str] = None
    email_client: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# =============================================================================
# NEWSLETTER ANALYTICS MODELS
# =============================================================================

class NewsletterMetrics(BaseModel):
    """Detailed metrics for a newsletter."""
    sent_count: int = 0
    delivered_count: int = 0
    bounced_count: int = 0
    hard_bounces: int = 0
    soft_bounces: int = 0
    opened_count: int = 0
    unique_opens: int = 0
    clicked_count: int = 0
    unique_clicks: int = 0
    unsubscribed_count: int = 0
    spam_reported_count: int = 0


class NewsletterRates(BaseModel):
    """Calculated rates for a newsletter."""
    delivery_rate: float = Field(0.0, ge=0, le=1, description="Delivered / Sent")
    open_rate: float = Field(0.0, ge=0, le=1, description="Unique opens / Delivered")
    click_rate: float = Field(0.0, ge=0, le=1, description="Unique clicks / Delivered")
    click_to_open_rate: float = Field(0.0, ge=0, le=1, description="Unique clicks / Unique opens")
    bounce_rate: float = Field(0.0, ge=0, le=1, description="Bounced / Sent")
    unsubscribe_rate: float = Field(0.0, ge=0, le=1, description="Unsubscribed / Delivered")


class NewsletterTiming(BaseModel):
    """Timing analytics for a newsletter."""
    avg_time_to_open_seconds: Optional[int] = None
    avg_time_to_click_seconds: Optional[int] = None
    peak_open_hour: Optional[int] = Field(None, ge=0, le=23)
    peak_click_hour: Optional[int] = Field(None, ge=0, le=23)


class TopClickedLink(BaseModel):
    """Top clicked link in a newsletter."""
    url: str
    content_item_id: Optional[UUID] = None
    clicks: int


class NewsletterAnalyticsResponse(BaseModel):
    """Complete analytics for a single newsletter."""
    newsletter_id: UUID
    workspace_id: UUID
    metrics: NewsletterMetrics
    rates: NewsletterRates
    engagement_score: float = Field(0.0, ge=0, le=1, description="Composite engagement metric")
    timing: NewsletterTiming
    top_links: List[TopClickedLink] = []
    total_events: int = 0
    last_calculated_at: Optional[datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "newsletter_id": "123e4567-e89b-12d3-a456-426614174001",
                "workspace_id": "123e4567-e89b-12d3-a456-426614174000",
                "metrics": {
                    "sent_count": 1000,
                    "delivered_count": 980,
                    "bounced_count": 20,
                    "opened_count": 450,
                    "unique_opens": 420,
                    "clicked_count": 120,
                    "unique_clicks": 110
                },
                "rates": {
                    "open_rate": 0.4286,
                    "click_rate": 0.1122,
                    "click_to_open_rate": 0.2619
                },
                "engagement_score": 0.85
            }
        }


# =============================================================================
# WORKSPACE ANALYTICS MODELS
# =============================================================================

class DateRange(BaseModel):
    """Date range for analytics queries."""
    start: datetime
    end: datetime


class WorkspaceAggregateMetrics(BaseModel):
    """Aggregate metrics across all newsletters in a workspace."""
    total_newsletters: int = 0
    total_sent: int = 0
    total_delivered: int = 0
    total_opened: int = 0
    total_clicked: int = 0
    avg_open_rate: float = 0.0
    avg_click_rate: float = 0.0
    avg_engagement_score: float = 0.0


class WorkspaceTrends(BaseModel):
    """Trend data for workspace."""
    open_rate_trend: Optional[str] = Field(None, description="e.g., '+12.5%' or '-5.2%'")
    click_rate_trend: Optional[str] = Field(None, description="e.g., '+8.3%' or '-3.1%'")


class WorkspaceAnalyticsResponse(BaseModel):
    """Aggregate analytics for a workspace."""
    workspace_id: UUID
    date_range: DateRange
    aggregate_metrics: WorkspaceAggregateMetrics
    trends: Optional[WorkspaceTrends] = None
    top_performing_content: List[Dict] = []

    class Config:
        json_schema_extra = {
            "example": {
                "workspace_id": "123e4567-e89b-12d3-a456-426614174000",
                "date_range": {
                    "start": "2025-01-01T00:00:00Z",
                    "end": "2025-01-31T23:59:59Z"
                },
                "aggregate_metrics": {
                    "total_newsletters": 4,
                    "total_sent": 4000,
                    "avg_open_rate": 0.4592,
                    "avg_click_rate": 0.1224
                }
            }
        }


# =============================================================================
# CONTENT PERFORMANCE MODELS
# =============================================================================

class ContentPerformanceResponse(BaseModel):
    """Performance metrics for a content item."""
    content_item_id: UUID
    title: Optional[str] = None
    source: Optional[str] = None
    source_url: Optional[str] = None
    times_included: int = 0
    times_clicked: int = 0
    unique_clickers: int = 0
    avg_click_rate: float = 0.0
    engagement_score: float = 0.0
    first_included_at: Optional[datetime] = None
    last_included_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# =============================================================================
# EXPORT MODELS
# =============================================================================

class AnalyticsExportRequest(BaseModel):
    """Request model for analytics export."""
    workspace_id: UUID
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    format: str = Field("csv", description="Export format: csv or json")

    class Config:
        json_schema_extra = {
            "example": {
                "workspace_id": "123e4567-e89b-12d3-a456-426614174000",
                "start_date": "2025-01-01T00:00:00Z",
                "end_date": "2025-01-31T23:59:59Z",
                "format": "csv"
            }
        }


# =============================================================================
# TRACKING MODELS
# =============================================================================

class TrackingPixelParams(BaseModel):
    """Parameters for tracking pixel."""
    newsletter_id: UUID = Field(..., alias="n")
    recipient_email: str = Field(..., alias="r")
    workspace_id: UUID = Field(..., alias="w")

    class Config:
        populate_by_name = True


class TrackingClickParams(BaseModel):
    """Parameters for click tracking."""
    newsletter_id: UUID = Field(..., alias="n")
    recipient_email: str = Field(..., alias="r")
    workspace_id: UUID = Field(..., alias="w")
    content_item_id: Optional[UUID] = Field(None, alias="c")
    original_url: str = Field(..., alias="u")

    class Config:
        populate_by_name = True
