"""
Content API endpoints.
"""

from fastapi import APIRouter, HTTPException, status, Depends, BackgroundTasks
from typing import Optional

from backend.models.content import (
    ScrapeContentRequest,
    ContentListResponse,
    ContentStatsResponse,
    ScrapeJobResponse
)
from backend.models.responses import APIResponse
from backend.services.content_service import content_service
from backend.middleware.auth import get_current_user


router = APIRouter()


@router.post("/scrape", response_model=APIResponse, status_code=status.HTTP_202_ACCEPTED)
async def scrape_content(
    request: ScrapeContentRequest,
    background_tasks: BackgroundTasks,
    user_id: str = Depends(get_current_user)
):
    """
    Scrape content for a workspace.

    This endpoint triggers content scraping from configured sources.
    The scraping happens in the background and returns immediately.

    Requires: Authorization header with Bearer token

    Args:
        request: Scrape configuration
        background_tasks: FastAPI background tasks
        user_id: User ID from JWT token

    Returns:
        APIResponse with scrape job information
    """
    try:
        # TODO: In production, use a proper job queue (Celery, Redis Queue, etc.)
        # For now, we'll run synchronously for simplicity
        result = await content_service.scrape_content(
            user_id=user_id,
            workspace_id=request.workspace_id,
            sources=request.sources,
            limit_per_source=request.limit_per_source
        )

        return APIResponse.success_response({
            "message": "Content scraping completed",
            "workspace_id": request.workspace_id,
            "total_items": result['total_items'],
            "items_by_source": result['items_by_source'],
            "scraped_at": result['scraped_at']
        })

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Scraping failed: {str(e)}"
        )


@router.get("/workspaces/{workspace_id}", response_model=APIResponse)
async def list_workspace_content(
    workspace_id: str,
    days: int = 7,
    source: Optional[str] = None,
    limit: int = 100,
    user_id: str = Depends(get_current_user)
):
    """
    List content items for a workspace.

    Requires: Authorization header with Bearer token

    Args:
        workspace_id: Workspace ID
        days: Number of days to look back (default: 7)
        source: Optional source filter (reddit, rss, blog, x, youtube)
        limit: Maximum items to return (default: 100)
        user_id: User ID from JWT token

    Returns:
        APIResponse with list of content items
    """
    try:
        result = await content_service.list_content(
            user_id=user_id,
            workspace_id=workspace_id,
            days=days,
            source=source,
            limit=limit
        )

        return APIResponse.success_response(result)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/workspaces/{workspace_id}/stats", response_model=APIResponse)
async def get_workspace_content_stats(
    workspace_id: str,
    user_id: str = Depends(get_current_user)
):
    """
    Get content statistics for a workspace.

    Provides overview of scraped content including:
    - Total items count
    - Items by source
    - Recent activity (24h, 7d)
    - Latest scrape time

    Requires: Authorization header with Bearer token

    Args:
        workspace_id: Workspace ID
        user_id: User ID from JWT token

    Returns:
        APIResponse with content statistics
    """
    try:
        stats = await content_service.get_content_stats(
            user_id=user_id,
            workspace_id=workspace_id
        )

        return APIResponse.success_response(stats)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/workspaces/{workspace_id}/sources/{source}", response_model=APIResponse)
async def list_content_by_source(
    workspace_id: str,
    source: str,
    days: int = 7,
    limit: int = 100,
    user_id: str = Depends(get_current_user)
):
    """
    List content items for a specific source in a workspace.

    Requires: Authorization header with Bearer token

    Args:
        workspace_id: Workspace ID
        source: Source name (reddit, rss, blog, x, youtube)
        days: Number of days to look back (default: 7)
        limit: Maximum items to return (default: 100)
        user_id: User ID from JWT token

    Returns:
        APIResponse with list of content items from specified source
    """
    return await list_workspace_content(
        workspace_id=workspace_id,
        days=days,
        source=source,
        limit=limit,
        user_id=user_id
    )
