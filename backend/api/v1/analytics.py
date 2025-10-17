"""
Analytics API Endpoints - Email engagement tracking and analytics.

Endpoints:
- POST /analytics/events - Record analytics event
- GET /analytics/newsletters/{newsletter_id} - Get newsletter analytics
- GET /analytics/workspaces/{workspace_id}/summary - Get workspace analytics
- GET /analytics/workspaces/{workspace_id}/content-performance - Get content performance
- GET /analytics/workspaces/{workspace_id}/export - Export analytics data
- POST /analytics/newsletters/{newsletter_id}/recalculate - Recalculate analytics
"""

import csv
import io
import json
from datetime import datetime, timedelta
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from fastapi.responses import StreamingResponse

from backend.models.analytics_models import (
    EmailEventCreate,
    EmailEventResponse,
    NewsletterAnalyticsResponse,
    WorkspaceAnalyticsResponse,
    ContentPerformanceResponse,
)
from backend.models.responses import APIResponse
from backend.services.analytics_service import AnalyticsService
from backend.api.v1.auth import get_current_user, verify_workspace_access

router = APIRouter()


# =============================================================================
# EVENT RECORDING
# =============================================================================

@router.post(
    "/events",
    response_model=APIResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Record Analytics Event",
    description="Record an email analytics event (sent, opened, clicked, etc.)",
)
async def record_analytics_event(
    event: EmailEventCreate,
    # Note: No auth required for tracking events (called by email clients)
):
    """
    Record an analytics event.

    This endpoint is called by:
    - Email delivery service (for 'sent' events)
    - Tracking pixel (for 'opened' events)
    - Click tracking (for 'clicked' events)
    - Email service providers (for 'bounced', 'unsubscribed' events)
    """
    try:
        analytics_service = AnalyticsService()

        result = await analytics_service.record_event(
            workspace_id=event.workspace_id,
            newsletter_id=event.newsletter_id,
            event_type=event.event_type,
            recipient_email=event.recipient_email,
            subscriber_id=event.subscriber_id,
            clicked_url=event.clicked_url,
            content_item_id=event.content_item_id,
            bounce_type=event.bounce_type,
            bounce_reason=event.bounce_reason,
            user_agent=event.user_agent,
            ip_address=event.ip_address,
        )

        return APIResponse.success_response(data=result)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to record analytics event: {str(e)}"
        )


# =============================================================================
# NEWSLETTER ANALYTICS
# =============================================================================

@router.get(
    "/newsletters/{newsletter_id}",
    response_model=APIResponse,
    summary="Get Newsletter Analytics",
    description="Get detailed analytics for a specific newsletter",
)
async def get_newsletter_analytics(
    newsletter_id: UUID,
    current_user: dict = Depends(get_current_user),
):
    """
    Get analytics summary for a specific newsletter.

    Returns:
    - Delivery metrics (sent, delivered, bounced)
    - Engagement metrics (opens, clicks)
    - Calculated rates (open rate, CTR, CTOR)
    - Top clicked links
    - Timing analytics
    """
    try:
        analytics_service = AnalyticsService()

        # Get analytics
        analytics = await analytics_service.get_newsletter_analytics(newsletter_id)

        if not analytics:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Newsletter analytics not found"
            )

        # Verify user has access to this workspace
        await verify_workspace_access(
            UUID(analytics["workspace_id"]),
            current_user["id"]
        )

        return APIResponse.success_response(data=analytics)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get newsletter analytics: {str(e)}"
        )


@router.post(
    "/newsletters/{newsletter_id}/recalculate",
    response_model=APIResponse,
    summary="Recalculate Newsletter Analytics",
    description="Recalculate analytics summary for a newsletter",
)
async def recalculate_newsletter_analytics(
    newsletter_id: UUID,
    current_user: dict = Depends(get_current_user),
):
    """
    Recalculate analytics summary for a newsletter.

    This is useful if:
    - Data becomes inconsistent
    - Manual event corrections were made
    - You want to rebuild analytics from scratch
    """
    try:
        analytics_service = AnalyticsService()

        # Get newsletter to verify workspace access
        analytics = await analytics_service.get_newsletter_analytics(newsletter_id)
        if not analytics:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Newsletter not found"
            )

        # Verify access
        await verify_workspace_access(
            UUID(analytics["workspace_id"]),
            current_user["id"]
        )

        # Recalculate
        await analytics_service.recalculate_summary(newsletter_id)

        return APIResponse.success_response(data={"status": "recalculated"})

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to recalculate analytics: {str(e)}"
        )


# =============================================================================
# WORKSPACE ANALYTICS
# =============================================================================

@router.get(
    "/workspaces/{workspace_id}/summary",
    response_model=APIResponse,
    summary="Get Workspace Analytics Summary",
    description="Get aggregate analytics for a workspace",
)
async def get_workspace_analytics_summary(
    workspace_id: UUID,
    start_date: Optional[datetime] = Query(None, description="Start date for filtering"),
    end_date: Optional[datetime] = Query(None, description="End date for filtering"),
    current_user: dict = Depends(get_current_user),
):
    """
    Get aggregate analytics for a workspace.

    Query parameters:
    - start_date: Start date for filtering (default: 30 days ago)
    - end_date: End date for filtering (default: now)

    Returns:
    - Total newsletters sent
    - Aggregate metrics across all newsletters
    - Average open rate, click rate
    - Engagement trends
    - Top performing content
    """
    try:
        # Verify access
        await verify_workspace_access(workspace_id, current_user["id"])

        analytics_service = AnalyticsService()

        # Get analytics
        analytics = await analytics_service.get_workspace_analytics(
            workspace_id, start_date, end_date
        )

        return APIResponse.success_response(data=analytics)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get workspace analytics: {str(e)}"
        )


# =============================================================================
# CONTENT PERFORMANCE
# =============================================================================

@router.get(
    "/workspaces/{workspace_id}/content-performance",
    response_model=APIResponse,
    summary="Get Content Performance",
    description="Get top performing content items",
)
async def get_content_performance(
    workspace_id: UUID,
    limit: int = Query(20, ge=1, le=100, description="Number of items to return"),
    current_user: dict = Depends(get_current_user),
):
    """
    Get top performing content items for a workspace.

    Returns content items ranked by:
    - Engagement score
    - Click-through rate
    - Times included in newsletters
    """
    try:
        # Verify access
        await verify_workspace_access(workspace_id, current_user["id"])

        analytics_service = AnalyticsService()

        # Get content performance
        content_performance = await analytics_service.get_content_performance(
            workspace_id, limit
        )

        return APIResponse.success_response(data=content_performance)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get content performance: {str(e)}"
        )


# =============================================================================
# ANALYTICS EXPORT
# =============================================================================

@router.get(
    "/workspaces/{workspace_id}/export",
    summary="Export Analytics Data",
    description="Export analytics data as CSV or JSON",
)
async def export_analytics_data(
    workspace_id: UUID,
    format: str = Query("csv", description="Export format: csv or json"),
    start_date: Optional[datetime] = Query(None, description="Start date for filtering"),
    end_date: Optional[datetime] = Query(None, description="End date for filtering"),
    current_user: dict = Depends(get_current_user),
):
    """
    Export analytics data for a workspace.

    Query parameters:
    - format: 'csv' or 'json' (default: csv)
    - start_date: Start date for filtering
    - end_date: End date for filtering

    Returns:
    - CSV file with all analytics events
    - JSON file with all analytics events
    """
    try:
        # Verify access
        await verify_workspace_access(workspace_id, current_user["id"])

        analytics_service = AnalyticsService()

        # Get export data
        events, content_type = await analytics_service.export_analytics_data(
            workspace_id, start_date, end_date, format
        )

        if not events:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No analytics data found for the specified criteria"
            )

        # Generate filename
        date_str = datetime.now().strftime("%Y%m%d")
        filename = f"analytics_{workspace_id}_{date_str}.{format}"

        # Format data based on format
        if format == "json":
            output = json.dumps(events, indent=2, default=str)
            return Response(
                content=output,
                media_type="application/json",
                headers={"Content-Disposition": f"attachment; filename={filename}"}
            )
        else:  # csv
            # Create CSV
            output = io.StringIO()
            if events:
                fieldnames = events[0].keys()
                writer = csv.DictWriter(output, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(events)

            return StreamingResponse(
                iter([output.getvalue()]),
                media_type="text/csv",
                headers={"Content-Disposition": f"attachment; filename={filename}"}
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export analytics data: {str(e)}"
        )


# =============================================================================
# ANALYTICS DASHBOARD DATA
# =============================================================================

@router.get(
    "/workspaces/{workspace_id}/dashboard",
    response_model=APIResponse,
    summary="Get Dashboard Analytics",
    description="Get all analytics data for dashboard display",
)
async def get_dashboard_analytics(
    workspace_id: UUID,
    period: str = Query("30d", description="Time period: 7d, 30d, 90d, 1y"),
    current_user: dict = Depends(get_current_user),
):
    """
    Get comprehensive analytics for dashboard display.

    Combines:
    - Workspace summary metrics
    - Recent newsletter performance
    - Content performance
    - Trends and insights

    Query parameters:
    - period: Time period for filtering (7d, 30d, 90d, 1y)
    """
    try:
        # Verify access
        await verify_workspace_access(workspace_id, current_user["id"])

        # Parse period
        period_map = {
            "7d": 7,
            "30d": 30,
            "90d": 90,
            "1y": 365,
        }
        days = period_map.get(period, 30)
        start_date = datetime.utcnow() - timedelta(days=days)

        analytics_service = AnalyticsService()

        # Get all analytics data
        workspace_analytics = await analytics_service.get_workspace_analytics(
            workspace_id, start_date, None
        )

        content_performance = await analytics_service.get_content_performance(
            workspace_id, limit=10
        )

        dashboard_data = {
            "workspace_analytics": workspace_analytics,
            "content_performance": content_performance,
            "period": period,
        }

        return APIResponse.success_response(data=dashboard_data)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get dashboard analytics: {str(e)}"
        )
