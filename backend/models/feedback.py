"""
Pydantic models for feedback and learning system.

These models handle:
- Content item feedback (ratings, edits)
- Newsletter feedback (overall ratings, time to finalize)
- Source quality scores (learned from feedback)
- Content preferences (extracted patterns)
- Feedback analytics and summaries
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from enum import Enum


# =============================================================================
# ENUMS
# =============================================================================

class FeedbackRating(str, Enum):
    """Feedback rating options"""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


class EngagementType(str, Enum):
    """Preferred engagement type"""
    HIGH_SCORE = "high_score"
    HIGH_COMMENTS = "high_comments"
    BALANCED = "balanced"


# =============================================================================
# FEEDBACK ITEM MODELS
# =============================================================================

class FeedbackItemBase(BaseModel):
    """Base model for content item feedback"""
    workspace_id: UUID
    user_id: UUID
    content_item_id: UUID
    newsletter_id: Optional[UUID] = None
    rating: FeedbackRating
    included_in_final: bool = False
    original_summary: Optional[str] = None
    edited_summary: Optional[str] = None
    edit_distance: float = Field(0.0, ge=0.0, le=1.0)
    feedback_notes: Optional[str] = None


class FeedbackItemCreate(BaseModel):
    """Create feedback on a content item"""
    content_item_id: UUID
    rating: FeedbackRating
    included_in_final: bool = False
    newsletter_id: Optional[UUID] = None
    original_summary: Optional[str] = None
    edited_summary: Optional[str] = None
    edit_distance: float = Field(0.0, ge=0.0, le=1.0)
    feedback_notes: Optional[str] = None

    @validator('edit_distance', always=True)
    def calculate_edit_distance(cls, v, values):
        """Calculate edit distance if summaries provided"""
        if 'original_summary' in values and 'edited_summary' in values:
            original = values.get('original_summary', '')
            edited = values.get('edited_summary', '')
            if original and edited:
                # Simple character-level distance (normalized)
                distance = sum(1 for a, b in zip(original, edited) if a != b)
                max_len = max(len(original), len(edited))
                return distance / max_len if max_len > 0 else 0.0
        return 0.0


class FeedbackItemUpdate(BaseModel):
    """Update feedback item"""
    rating: Optional[FeedbackRating] = None
    included_in_final: Optional[bool] = None
    edited_summary: Optional[str] = None
    feedback_notes: Optional[str] = None


class FeedbackItemResponse(FeedbackItemBase):
    """Feedback item response with metadata"""
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class FeedbackItemListResponse(BaseModel):
    """List of feedback items with pagination"""
    items: List[FeedbackItemResponse]
    total: int
    page: int = 1
    page_size: int = 50
    has_more: bool


# =============================================================================
# NEWSLETTER FEEDBACK MODELS
# =============================================================================

class NewsletterFeedbackBase(BaseModel):
    """Base model for newsletter feedback"""
    workspace_id: UUID
    user_id: UUID
    newsletter_id: UUID
    overall_rating: Optional[int] = Field(None, ge=1, le=5)
    time_to_finalize_minutes: Optional[int] = Field(None, ge=0)
    items_added: int = 0
    items_removed: int = 0
    items_edited: int = 0
    notes: Optional[str] = None
    would_recommend: Optional[bool] = None
    draft_acceptance_rate: Optional[float] = Field(None, ge=0.0, le=1.0)


class NewsletterFeedbackCreate(BaseModel):
    """Create newsletter feedback"""
    newsletter_id: UUID
    overall_rating: Optional[int] = Field(None, ge=1, le=5)
    time_to_finalize_minutes: Optional[int] = Field(None, ge=0)
    items_added: int = 0
    items_removed: int = 0
    items_edited: int = 0
    notes: Optional[str] = None
    would_recommend: Optional[bool] = None
    draft_acceptance_rate: Optional[float] = Field(None, ge=0.0, le=1.0)

    @validator('draft_acceptance_rate', always=True)
    def calculate_acceptance_rate(cls, v, values):
        """Calculate draft acceptance rate from items changes"""
        added = values.get('items_added', 0)
        removed = values.get('items_removed', 0)
        edited = values.get('items_edited', 0)

        total_changes = added + removed + edited
        if total_changes == 0:
            return 1.0  # No changes = 100% acceptance

        # Lower acceptance rate with more changes
        return max(0.0, 1.0 - (total_changes * 0.1))


class NewsletterFeedbackUpdate(BaseModel):
    """Update newsletter feedback"""
    overall_rating: Optional[int] = Field(None, ge=1, le=5)
    time_to_finalize_minutes: Optional[int] = Field(None, ge=0)
    items_added: Optional[int] = None
    items_removed: Optional[int] = None
    items_edited: Optional[int] = None
    notes: Optional[str] = None
    would_recommend: Optional[bool] = None


class NewsletterFeedbackResponse(NewsletterFeedbackBase):
    """Newsletter feedback response with metadata"""
    id: UUID
    created_at: datetime
    updated_at: datetime

    # Include related item feedback
    item_feedback_count: Optional[int] = None
    positive_items: Optional[int] = None
    negative_items: Optional[int] = None

    class Config:
        from_attributes = True


class NewsletterFeedbackListResponse(BaseModel):
    """List of newsletter feedback with pagination"""
    items: List[NewsletterFeedbackResponse]
    total: int
    page: int = 1
    page_size: int = 50
    has_more: bool


# =============================================================================
# SOURCE QUALITY SCORE MODELS
# =============================================================================

class SourceQualityScoreBase(BaseModel):
    """Base model for source quality scores"""
    workspace_id: UUID
    source_name: str
    quality_score: float = Field(0.5, ge=0.0, le=1.0)
    positive_count: int = 0
    negative_count: int = 0
    neutral_count: int = 0
    total_feedback_count: int = 0
    inclusion_rate: float = Field(0.5, ge=0.0, le=1.0)
    avg_edit_distance: float = Field(0.0, ge=0.0, le=1.0)
    trending_score: float = Field(0.5, ge=0.0, le=1.0)


class SourceQualityScoreResponse(SourceQualityScoreBase):
    """Source quality score response"""
    id: UUID
    last_calculated_at: datetime
    created_at: datetime
    updated_at: datetime

    # Derived metrics
    positive_rate: Optional[float] = None
    negative_rate: Optional[float] = None

    @validator('positive_rate', always=True)
    def calc_positive_rate(cls, v, values):
        total = values.get('total_feedback_count', 0)
        if total > 0:
            return values.get('positive_count', 0) / total
        return 0.0

    @validator('negative_rate', always=True)
    def calc_negative_rate(cls, v, values):
        total = values.get('total_feedback_count', 0)
        if total > 0:
            return values.get('negative_count', 0) / total
        return 0.0

    class Config:
        from_attributes = True


class SourceQualityScoreListResponse(BaseModel):
    """List of source quality scores"""
    items: List[SourceQualityScoreResponse]
    total: int


# =============================================================================
# CONTENT PREFERENCES MODELS
# =============================================================================

class ContentPreferencesBase(BaseModel):
    """Base model for content preferences"""
    workspace_id: UUID
    preferred_sources: List[str] = Field(default_factory=list)
    avoided_topics: List[str] = Field(default_factory=list)
    preferred_topics: List[str] = Field(default_factory=list)
    min_score_threshold: int = 0
    max_score_threshold: Optional[int] = None
    preferred_content_length_min: Optional[int] = None
    preferred_content_length_max: Optional[int] = None
    preferred_recency_hours: int = 24
    min_comments_threshold: int = 0
    preferred_engagement_type: Optional[EngagementType] = None
    total_feedback_count: int = 0
    confidence_level: float = Field(0.0, ge=0.0, le=1.0)


class ContentPreferencesResponse(ContentPreferencesBase):
    """Content preferences response"""
    id: UUID
    last_updated_at: datetime
    created_at: datetime

    # Confidence indicators
    confidence_label: Optional[str] = None
    is_reliable: Optional[bool] = None

    @validator('confidence_label', always=True)
    def get_confidence_label(cls, v, values):
        level = values.get('confidence_level', 0.0)
        if level >= 0.8:
            return "High"
        elif level >= 0.5:
            return "Medium"
        else:
            return "Low"

    @validator('is_reliable', always=True)
    def check_reliability(cls, v, values):
        return values.get('total_feedback_count', 0) >= 10

    class Config:
        from_attributes = True


# =============================================================================
# FEEDBACK ANALYTICS MODELS
# =============================================================================

class FeedbackAnalyticsSummary(BaseModel):
    """Summary of feedback analytics for a workspace"""
    workspace_id: UUID
    date_range: Dict[str, datetime]

    # Overall metrics
    total_feedback_items: int
    positive_count: int
    negative_count: int
    neutral_count: int

    # Rates
    positive_rate: float
    negative_rate: float
    inclusion_rate: float

    # Newsletter metrics
    total_newsletter_feedback: int
    avg_newsletter_rating: Optional[float] = None
    avg_time_to_finalize: Optional[float] = None
    avg_draft_acceptance_rate: Optional[float] = None

    # Source performance
    top_sources: List[Dict[str, Any]] = Field(default_factory=list)
    worst_sources: List[Dict[str, Any]] = Field(default_factory=list)

    # Learning status
    total_sources_tracked: int
    preferences_confidence: Optional[float] = None

    # Recommendations
    recommendations: List[str] = Field(default_factory=list)


class ApplyLearningRequest(BaseModel):
    """Request to apply learned preferences to content items"""
    content_item_ids: List[UUID]
    apply_source_quality: bool = True
    apply_preferences: bool = True


class ApplyLearningResponse(BaseModel):
    """Response after applying learning to content"""
    adjusted_items: List[Dict[str, Any]]
    adjustments_made: int
    quality_scores_applied: Dict[str, float]
    preferences_applied: bool


# =============================================================================
# FILTER & QUERY MODELS
# =============================================================================

class FeedbackItemFilter(BaseModel):
    """Filters for querying feedback items"""
    workspace_id: UUID
    content_item_id: Optional[UUID] = None
    newsletter_id: Optional[UUID] = None
    rating: Optional[FeedbackRating] = None
    included_in_final: Optional[bool] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    page: int = Field(1, ge=1)
    page_size: int = Field(50, ge=1, le=100)


class NewsletterFeedbackFilter(BaseModel):
    """Filters for querying newsletter feedback"""
    workspace_id: UUID
    newsletter_id: Optional[UUID] = None
    min_rating: Optional[int] = Field(None, ge=1, le=5)
    max_rating: Optional[int] = Field(None, ge=1, le=5)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    page: int = Field(1, ge=1)
    page_size: int = Field(50, ge=1, le=100)


class FeedbackAnalyticsRequest(BaseModel):
    """Request for feedback analytics"""
    workspace_id: UUID
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    include_source_breakdown: bool = True
    include_recommendations: bool = True
