"""
Trends API Endpoints

Endpoints for detecting and managing content trends.
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Request
from uuid import UUID

from backend.models.trend import (
    DetectTrendsRequest,
    DetectTrendsResponse,
    TrendResponse,
    TrendListResponse,
    TrendHistoryResponse,
    TrendAnalysisSummary
)
from backend.models.responses import APIResponse
from backend.middleware.auth import get_current_user
from backend.middleware.rate_limiter import limiter, RateLimits
from backend.services.trend_service import TrendDetectionService
from backend.api.v1.auth import verify_workspace_access

router = APIRouter()


def get_trend_service() -> TrendDetectionService:
    """Dependency: Get trend detection service."""
    return TrendDetectionService()


# =============================================================================
# TREND DETECTION ENDPOINTS
# =============================================================================

@router.post("/detect", response_model=APIResponse)
@limiter.limit(RateLimits.TREND_DETECTION)
async def detect_trends(
    request: Request,
    detect_request: DetectTrendsRequest,
    current_user: str = Depends(get_current_user),
    trend_service: TrendDetectionService = Depends(get_trend_service)
):
    """
    Detect trends from recent content.

    Rate limit: 10 requests per minute per IP

    Analyzes content using a 5-stage pipeline:
    1. **Topic Extraction** - TF-IDF + K-means clustering
    2. **Velocity Calculation** - Compare to historical data
    3. **Cross-Source Validation** - Require 2+ sources
    4. **Scoring** - Multi-factor strength calculation
    5. **Explanation Generation** - AI-powered descriptions

    **Parameters:**
    - `days_back`: Analyze content from last N days (1-30)
    - `max_trends`: Maximum trends to return (1-20)
    - `min_confidence`: Minimum confidence threshold (0.0-1.0)
    - `sources`: Filter by specific sources (optional)

    **Returns:**
    - Detected trends with strength scores
    - Analysis summary with statistics
    - Key content items for each trend

    **Example:**
    ```json
    {
      "workspace_id": "uuid",
      "days_back": 7,
      "max_trends": 5,
      "min_confidence": 0.6,
      "sources": ["reddit", "rss"]
    }
    ```
    """
    try:
        # Verify workspace access
        await verify_workspace_access(detect_request.workspace_id, current_user)

        # Detect trends
        trends, analysis_summary = await trend_service.detect_trends(
            detect_request.workspace_id,
            days_back=detect_request.days_back,
            max_trends=detect_request.max_trends,
            min_confidence=detect_request.min_confidence,
            sources=detect_request.sources
        )

        response = DetectTrendsResponse(
            success=True,
            message=f"Detected {len(trends)} trends from {analysis_summary['content_items_analyzed']} content items",
            trends=trends,
            analysis_summary=analysis_summary
        )

        return APIResponse.success_response(response)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to detect trends: {str(e)}"
        )


@router.get("/{workspace_id}", response_model=APIResponse)
async def get_active_trends(
    workspace_id: UUID,
    limit: int = 5,
    current_user: str = Depends(get_current_user),
    trend_service: TrendDetectionService = Depends(get_trend_service)
):
    """
    Get active trends for workspace.

    Returns currently active trends sorted by strength score.

    **Parameters:**
    - `limit`: Maximum trends to return (default: 5)

    **Returns:**
    - List of active trends with full details
    - Total count of trends
    - Detection timestamp

    **Use cases:**
    - Display trending topics in dashboard
    - Filter content by trending topics
    - Newsletter trend sections
    """
    try:
        # Verify workspace access
        await verify_workspace_access(workspace_id, current_user)

        # Get active trends
        trends = await trend_service.get_active_trends(workspace_id, limit)

        response = TrendListResponse(
            trends=trends,
            count=len(trends),
            workspace_id=workspace_id
        )

        return APIResponse.success_response(response)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get active trends: {str(e)}"
        )


@router.get("/{workspace_id}/history", response_model=APIResponse)
async def get_trend_history(
    workspace_id: UUID,
    days_back: int = 30,
    current_user: str = Depends(get_current_user),
    trend_service: TrendDetectionService = Depends(get_trend_service)
):
    """
    Get trend history for workspace.

    Returns historical trend data showing how topics have evolved over time.

    **Parameters:**
    - `days_back`: Number of days to look back (default: 30)

    **Returns:**
    - Historical trend data points
    - Trends grouped by date
    - Strength scores over time

    **Use cases:**
    - Trend evolution charts
    - Topic lifecycle analysis
    - Historical comparisons
    """
    try:
        # Verify workspace access
        await verify_workspace_access(workspace_id, current_user)

        # Get trend history
        history = await trend_service.get_trend_history(workspace_id, days_back)

        return APIResponse.success_response(history)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get trend history: {str(e)}"
        )


@router.get("/{workspace_id}/summary", response_model=APIResponse)
async def get_trend_summary(
    workspace_id: UUID,
    days_back: int = 7,
    current_user: str = Depends(get_current_user),
    trend_service: TrendDetectionService = Depends(get_trend_service)
):
    """
    Get trend analysis summary for workspace.

    Returns aggregated statistics about trends over time.

    **Parameters:**
    - `days_back`: Analysis period in days (default: 7)

    **Returns:**
    - Total trends detected
    - Active vs inactive trends
    - Top sources by trend count
    - Average strength score
    - Total content analyzed

    **Use cases:**
    - Dashboard statistics
    - Trend health monitoring
    - Source performance analysis
    """
    try:
        # Verify workspace access
        await verify_workspace_access(workspace_id, current_user)

        # Get summary
        summary = await trend_service.get_trend_summary(workspace_id, days_back)

        return APIResponse.success_response(summary)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get trend summary: {str(e)}"
        )


@router.get("/trend/{trend_id}", response_model=APIResponse)
async def get_specific_trend(
    trend_id: UUID,
    current_user: str = Depends(get_current_user),
    trend_service: TrendDetectionService = Depends(get_trend_service)
):
    """
    Get specific trend by ID.

    Returns complete details for a single trend including all metadata.

    **Returns:**
    - Complete trend details
    - Keywords and related topics
    - Source information
    - Time tracking (first seen, peak time)
    - Key content items

    **Use cases:**
    - Trend detail pages
    - Deep dive analysis
    - Content exploration by trend
    """
    try:
        # Get trend
        trend_data = trend_service.db.get_trend(str(trend_id))

        if not trend_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Trend not found"
            )

        # Verify workspace access
        from uuid import UUID as UUID_converter
        await verify_workspace_access(UUID_converter(trend_data['workspace_id']), current_user)

        trend = TrendResponse(**trend_data)

        return APIResponse.success_response(trend)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get trend: {str(e)}"
        )


@router.delete("/trend/{trend_id}", response_model=APIResponse)
async def delete_trend(
    trend_id: UUID,
    current_user: str = Depends(get_current_user),
    trend_service: TrendDetectionService = Depends(get_trend_service)
):
    """
    Delete a trend.

    Permanently removes a trend from the database.

    **Returns:**
    - Deletion confirmation
    - Deleted trend ID

    **Use cases:**
    - Remove false positives
    - Clean up old trends
    - Manual trend management
    """
    try:
        # Get trend to verify workspace access
        trend_data = trend_service.db.get_trend(str(trend_id))

        if not trend_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Trend not found"
            )

        # Verify workspace access (owner/admin only for deletion)
        from uuid import UUID as UUID_converter
        await verify_workspace_access(UUID_converter(trend_data['workspace_id']), current_user)

        # Delete trend
        deleted = trend_service.db.delete_trend(str(trend_id))

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete trend"
            )

        return APIResponse.success_response({
            "deleted": True,
            "trend_id": str(trend_id),
            "message": "Trend deleted successfully"
        })

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete trend: {str(e)}"
        )
