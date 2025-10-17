"""
Feedback API endpoints for learning from user preferences.

Endpoints:
- POST /feedback/items - Record content item feedback
- GET /feedback/items/{workspace_id} - List feedback items
- POST /feedback/newsletters - Record newsletter feedback
- GET /feedback/newsletters/{newsletter_id} - Get newsletter feedback
- GET /feedback/sources/{workspace_id} - Get source quality scores
- GET /feedback/preferences/{workspace_id} - Get content preferences
- GET /feedback/analytics/{workspace_id} - Get analytics summary
- POST /feedback/apply-learning/{workspace_id} - Apply learned preferences to content
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List, Optional
from datetime import datetime
from uuid import UUID

from backend.middleware.auth import get_current_user
from backend.models.responses import APIResponse
from backend.models.feedback import (
    FeedbackItemCreate,
    FeedbackItemResponse,
    FeedbackItemListResponse,
    FeedbackItemFilter,
    NewsletterFeedbackCreate,
    NewsletterFeedbackUpdate,
    NewsletterFeedbackResponse,
    NewsletterFeedbackListResponse,
    NewsletterFeedbackFilter,
    SourceQualityScoreResponse,
    SourceQualityScoreListResponse,
    ContentPreferencesResponse,
    FeedbackAnalyticsSummary,
    ApplyLearningRequest,
    ApplyLearningResponse,
    FeedbackAnalyticsRequest,
)
from backend.services.feedback_service import FeedbackService
from src.ai_newsletter.database.supabase_client import SupabaseManager

router = APIRouter()


def get_feedback_service() -> FeedbackService:
    """Dependency to get feedback service instance."""
    supabase = SupabaseManager()
    return FeedbackService(supabase)


# =============================================================================
# CONTENT ITEM FEEDBACK ENDPOINTS
# =============================================================================

@router.post("/items", response_model=APIResponse)
async def create_item_feedback(
    feedback: FeedbackItemCreate,
    current_user: dict = Depends(get_current_user),
    service: FeedbackService = Depends(get_feedback_service)
):
    """
    Record feedback on a content item.

    Accepts:
    - Content item ID
    - Rating (positive, negative, neutral)
    - Whether item was included in final newsletter
    - Optional newsletter ID
    - Optional summaries for edit distance calculation

    Returns:
    - Created feedback with ID and metadata
    """
    try:
        # Get workspace_id from current user context (assumed to be available)
        workspace_id = current_user.get('workspace_id')
        if not workspace_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Workspace ID not found in user context"
            )

        result = service.record_item_feedback(
            workspace_id=str(workspace_id),
            user_id=str(current_user['user_id']),
            content_item_id=str(feedback.content_item_id),
            rating=feedback.rating.value,
            included_in_final=feedback.included_in_final,
            newsletter_id=str(feedback.newsletter_id) if feedback.newsletter_id else None,
            original_summary=feedback.original_summary,
            edited_summary=feedback.edited_summary,
            feedback_notes=feedback.feedback_notes
        )

        return APIResponse.success_response(data=result)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to record feedback: {str(e)}"
        )


@router.get("/items/{workspace_id}", response_model=APIResponse)
async def list_item_feedback(
    workspace_id: UUID,
    content_item_id: Optional[UUID] = Query(None),
    newsletter_id: Optional[UUID] = Query(None),
    rating: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    service: FeedbackService = Depends(get_feedback_service)
):
    """
    List feedback items for a workspace with optional filters.

    Query parameters:
    - content_item_id: Filter by specific content item
    - newsletter_id: Filter by newsletter
    - rating: Filter by rating (positive, negative, neutral)
    - start_date: Filter by created_at >= start_date
    - end_date: Filter by created_at < end_date
    - page: Page number (default: 1)
    - page_size: Items per page (default: 50, max: 100)

    Returns:
    - List of feedback items with pagination
    """
    try:
        supabase = service.db

        # Get feedback items
        feedback_items = supabase.list_feedback_items(
            workspace_id=str(workspace_id),
            content_item_id=str(content_item_id) if content_item_id else None,
            newsletter_id=str(newsletter_id) if newsletter_id else None,
            rating=rating,
            start_date=start_date,
            end_date=end_date,
            limit=page_size * 2  # Get extra for has_more check
        )

        # Pagination
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        page_items = feedback_items[start_idx:end_idx]
        has_more = len(feedback_items) > end_idx

        response = FeedbackItemListResponse(
            items=[FeedbackItemResponse(**item) for item in page_items],
            total=len(feedback_items),
            page=page,
            page_size=page_size,
            has_more=has_more
        )

        return APIResponse.success_response(data=response.dict())

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list feedback: {str(e)}"
        )


# =============================================================================
# NEWSLETTER FEEDBACK ENDPOINTS
# =============================================================================

@router.post("/newsletters", response_model=APIResponse)
async def create_newsletter_feedback(
    feedback: NewsletterFeedbackCreate,
    current_user: dict = Depends(get_current_user),
    service: FeedbackService = Depends(get_feedback_service)
):
    """
    Record feedback on a newsletter.

    Accepts:
    - Newsletter ID
    - Overall rating (1-5 stars)
    - Time to finalize (minutes)
    - Number of items added/removed/edited
    - Optional notes
    - Whether user would recommend

    Returns:
    - Created feedback with ID and calculated metrics
    """
    try:
        workspace_id = current_user.get('workspace_id')
        if not workspace_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Workspace ID not found in user context"
            )

        result = service.record_newsletter_feedback(
            workspace_id=str(workspace_id),
            user_id=str(current_user['user_id']),
            newsletter_id=str(feedback.newsletter_id),
            overall_rating=feedback.overall_rating,
            time_to_finalize_minutes=feedback.time_to_finalize_minutes,
            items_added=feedback.items_added,
            items_removed=feedback.items_removed,
            items_edited=feedback.items_edited,
            notes=feedback.notes,
            would_recommend=feedback.would_recommend
        )

        return APIResponse.success_response(data=result)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to record newsletter feedback: {str(e)}"
        )


@router.get("/newsletters/{newsletter_id}", response_model=APIResponse)
async def get_newsletter_feedback(
    newsletter_id: UUID,
    current_user: dict = Depends(get_current_user),
    service: FeedbackService = Depends(get_feedback_service)
):
    """
    Get feedback for a specific newsletter.

    Includes:
    - Overall feedback (rating, time to finalize, etc.)
    - Linked content item feedback counts
    - Positive/negative item counts

    Returns:
    - Complete newsletter feedback with related data
    """
    try:
        supabase = service.db
        feedback = supabase.get_newsletter_feedback(str(newsletter_id))

        if not feedback:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Newsletter feedback not found for ID: {newsletter_id}"
            )

        return APIResponse.success_response(data=feedback)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get newsletter feedback: {str(e)}"
        )


@router.get("/newsletters/workspace/{workspace_id}", response_model=APIResponse)
async def list_newsletter_feedback(
    workspace_id: UUID,
    min_rating: Optional[int] = Query(None, ge=1, le=5),
    max_rating: Optional[int] = Query(None, ge=1, le=5),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    service: FeedbackService = Depends(get_feedback_service)
):
    """
    List newsletter feedback for a workspace.

    Query parameters:
    - min_rating: Filter by overall_rating >= min_rating
    - max_rating: Filter by overall_rating <= max_rating
    - start_date: Filter by created_at >= start_date
    - end_date: Filter by created_at < end_date
    - page: Page number
    - page_size: Items per page

    Returns:
    - List of newsletter feedback with pagination
    """
    try:
        supabase = service.db

        feedback_items = supabase.list_newsletter_feedback(
            workspace_id=str(workspace_id),
            min_rating=min_rating,
            max_rating=max_rating,
            start_date=start_date,
            end_date=end_date,
            limit=page_size * 2
        )

        # Pagination
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        page_items = feedback_items[start_idx:end_idx]
        has_more = len(feedback_items) > end_idx

        response = NewsletterFeedbackListResponse(
            items=[NewsletterFeedbackResponse(**item) for item in page_items],
            total=len(feedback_items),
            page=page,
            page_size=page_size,
            has_more=has_more
        )

        return APIResponse.success_response(data=response.dict())

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list newsletter feedback: {str(e)}"
        )


# =============================================================================
# LEARNING ENDPOINTS
# =============================================================================

@router.get("/sources/{workspace_id}", response_model=APIResponse)
async def get_source_quality_scores(
    workspace_id: UUID,
    current_user: dict = Depends(get_current_user),
    service: FeedbackService = Depends(get_feedback_service)
):
    """
    Get source quality scores for a workspace.

    Returns quality metrics for each content source:
    - Quality score (0.0 to 1.0)
    - Positive/negative/neutral counts
    - Inclusion rate (% of items kept in final newsletters)
    - Average edit distance
    - Quality label (Excellent, Good, Average, Poor)

    Returns:
    - List of source quality scores sorted by quality
    """
    try:
        scores = service.get_source_quality_scores(str(workspace_id))

        response = SourceQualityScoreListResponse(
            items=[SourceQualityScoreResponse(**score) for score in scores],
            total=len(scores)
        )

        return APIResponse.success_response(data=response.dict())

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get source quality scores: {str(e)}"
        )


@router.get("/preferences/{workspace_id}", response_model=APIResponse)
async def get_content_preferences(
    workspace_id: UUID,
    current_user: dict = Depends(get_current_user),
    service: FeedbackService = Depends(get_feedback_service)
):
    """
    Get learned content preferences for a workspace.

    Returns extracted preferences including:
    - Preferred sources (high quality)
    - Avoided topics
    - Preferred topics
    - Score thresholds
    - Content length preferences
    - Recency preferences
    - Confidence level and reliability

    Returns:
    - Content preferences with confidence indicators
    """
    try:
        preferences = service.get_content_preferences(str(workspace_id))

        if not preferences:
            # Extract preferences if not yet created
            pref_id = service.extract_content_preferences(str(workspace_id))
            if pref_id:
                preferences = service.get_content_preferences(str(workspace_id))

        if not preferences:
            return APIResponse.success_response(data=None)

        response = ContentPreferencesResponse(**preferences)

        return APIResponse.success_response(data=response.dict())

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get content preferences: {str(e)}"
        )


@router.get("/analytics/{workspace_id}", response_model=APIResponse)
async def get_feedback_analytics(
    workspace_id: UUID,
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    current_user: dict = Depends(get_current_user),
    service: FeedbackService = Depends(get_feedback_service)
):
    """
    Get comprehensive feedback analytics for a workspace.

    Query parameters:
    - start_date: Start of date range (default: 30 days ago)
    - end_date: End of date range (default: now)

    Returns extensive metrics including:
    - Total feedback counts by rating
    - Positive/negative/inclusion rates
    - Average newsletter rating and time to finalize
    - Top performing and worst performing sources
    - Learning status and confidence
    - Personalized recommendations

    Returns:
    - Complete analytics summary with insights
    """
    try:
        analytics = service.get_feedback_analytics(
            workspace_id=str(workspace_id),
            start_date=start_date,
            end_date=end_date
        )

        # Get learning summary
        learning_summary = service.get_learning_summary(str(workspace_id))

        # Combine analytics and learning summary
        combined_data = {
            **analytics,
            'learning_summary': learning_summary
        }

        return APIResponse.success_response(data=combined_data)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get feedback analytics: {str(e)}"
        )


@router.post("/apply-learning/{workspace_id}", response_model=APIResponse)
async def apply_learning_to_content(
    workspace_id: UUID,
    request: ApplyLearningRequest,
    current_user: dict = Depends(get_current_user),
    service: FeedbackService = Depends(get_feedback_service)
):
    """
    Apply learned preferences to adjust content item scores.

    Accepts:
    - List of content item IDs
    - Flags to enable/disable source quality and preferences application

    Adjusts scores based on:
    - Source quality scores (multiplier based on feedback)
    - Preferred sources (20% boost)
    - Score thresholds (30% reduction if below minimum)

    Returns:
    - Adjusted content items with new scores
    - List of adjustments made
    - Quality scores applied by source
    """
    try:
        supabase = service.db

        # Fetch content items
        content_items = []
        for content_id in request.content_item_ids:
            item = supabase.get_content_item(str(content_id))
            if item:
                content_items.append(item)

        if not content_items:
            return APIResponse.success_response(
                data={
                    'adjusted_items': [],
                    'adjustments_made': 0,
                    'quality_scores_applied': {},
                    'preferences_applied': False
                }
            )

        # Apply learning
        adjusted_items = service.adjust_content_scoring(
            workspace_id=str(workspace_id),
            content_items=content_items,
            apply_source_quality=request.apply_source_quality,
            apply_preferences=request.apply_preferences
        )

        # Count adjustments
        adjustments_made = sum(1 for item in adjusted_items if item.get('adjustments'))

        # Get quality scores that were applied
        quality_scores = {}
        for item in adjusted_items:
            source = item.get('source', '')
            if source and 'source_quality' in str(item.get('adjustments', [])):
                for adj in item.get('adjustments', []):
                    if 'source_quality:' in adj:
                        score_str = adj.split(':')[1]
                        quality_scores[source] = float(score_str)

        response = ApplyLearningResponse(
            adjusted_items=adjusted_items,
            adjustments_made=adjustments_made,
            quality_scores_applied=quality_scores,
            preferences_applied=request.apply_preferences
        )

        return APIResponse.success_response(data=response.dict())

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to apply learning: {str(e)}"
        )


# =============================================================================
# UTILITY ENDPOINTS
# =============================================================================

@router.post("/recalculate/{workspace_id}", response_model=APIResponse)
async def recalculate_source_quality(
    workspace_id: UUID,
    current_user: dict = Depends(get_current_user),
    service: FeedbackService = Depends(get_feedback_service)
):
    """
    Manually trigger recalculation of source quality scores.

    Note: Scores are automatically recalculated when feedback is added,
    but this endpoint allows manual recalculation if needed.

    Returns:
    - Number of sources recalculated
    """
    try:
        count = service.recalculate_source_quality(str(workspace_id))

        return APIResponse.success_response(data={'sources_recalculated': count})

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to recalculate source quality: {str(e)}"
        )


@router.post("/extract-preferences/{workspace_id}", response_model=APIResponse)
async def extract_preferences(
    workspace_id: UUID,
    current_user: dict = Depends(get_current_user),
    service: FeedbackService = Depends(get_feedback_service)
):
    """
    Manually trigger extraction of content preferences from feedback.

    Analyzes all feedback to identify:
    - Preferred sources (quality > 0.6)
    - Content patterns
    - Optimal settings

    Returns:
    - Preferences ID if successful
    - Confidence level based on feedback volume
    """
    try:
        pref_id = service.extract_content_preferences(str(workspace_id))

        if not pref_id:
            return APIResponse.error_response(
                code="INSUFFICIENT_DATA",
                message="Not enough feedback to extract preferences. Provide more ratings."
            )

        preferences = service.get_content_preferences(str(workspace_id))

        return APIResponse.success_response(data=preferences)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to extract preferences: {str(e)}"
        )
