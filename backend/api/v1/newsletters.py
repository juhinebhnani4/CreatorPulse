"""
Newsletter API endpoints.
"""

from fastapi import APIRouter, HTTPException, status, Depends, Request
from typing import Optional

from backend.models.newsletter import (
    GenerateNewsletterRequest,
    NewsletterResponse,
    NewsletterListResponse,
    NewsletterStatsResponse,
    UpdateNewsletterRequest
)
from backend.models.responses import APIResponse
from backend.services.newsletter_service import newsletter_service
from backend.middleware.auth import get_current_user
from backend.middleware.rate_limiter import limiter, RateLimits


router = APIRouter()


@router.post("/generate", response_model=APIResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit(RateLimits.NEWSLETTER_GENERATION)
async def generate_newsletter(
    http_request: Request,
    request: GenerateNewsletterRequest,
    user_id: str = Depends(get_current_user)
):
    """
    Generate newsletter from workspace content.

    Rate limit: 5 requests per minute per IP

    This endpoint generates a newsletter using content from the workspace database
    (not live scraping). Content must be scraped first using the Content API.

    Requires: Authorization header with Bearer token

    Args:
        request: Newsletter generation parameters
        user_id: User ID from JWT token

    Returns:
        APIResponse with generated newsletter
    """
    try:
        result = await newsletter_service.generate_newsletter(
            user_id=user_id,
            workspace_id=request.workspace_id,
            title=request.title,
            max_items=request.max_items,
            days_back=request.days_back,
            sources=request.sources,
            tone=request.tone,
            language=request.language,
            temperature=request.temperature,
            model=request.model,
            use_openrouter=request.use_openrouter
        )

        return APIResponse.success_response({
            "message": "Newsletter generated successfully",
            "newsletter": result['newsletter'],
            "content_items_count": result['content_items_count'],
            "sources_used": result['sources_used']
        })

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Newsletter generation failed: {str(e)}"
        )


@router.get("/workspaces/{workspace_id}", response_model=APIResponse)
async def list_workspace_newsletters(
    workspace_id: str,
    status_filter: Optional[str] = None,
    limit: int = 50,
    user_id: str = Depends(get_current_user)
):
    """
    List newsletters for a workspace.

    Requires: Authorization header with Bearer token

    Args:
        workspace_id: Workspace ID
        status_filter: Optional filter by status (draft, sent, scheduled)
        limit: Maximum newsletters to return (default: 50)
        user_id: User ID from JWT token

    Returns:
        APIResponse with list of newsletters
    """
    try:
        result = await newsletter_service.list_newsletters(
            user_id=user_id,
            workspace_id=workspace_id,
            status=status_filter,
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
async def get_workspace_newsletter_stats(
    workspace_id: str,
    user_id: str = Depends(get_current_user)
):
    """
    Get newsletter statistics for a workspace.

    Provides overview including:
    - Total newsletters count
    - Count by status (draft, sent, scheduled)
    - Total content items used
    - Latest newsletter timestamp

    Requires: Authorization header with Bearer token

    Args:
        workspace_id: Workspace ID
        user_id: User ID from JWT token

    Returns:
        APIResponse with newsletter statistics
    """
    try:
        stats = await newsletter_service.get_newsletter_stats(
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


@router.get("/{newsletter_id}", response_model=APIResponse)
async def get_newsletter(
    newsletter_id: str,
    user_id: str = Depends(get_current_user)
):
    """
    Get newsletter details.

    Requires: Authorization header with Bearer token

    Args:
        newsletter_id: Newsletter ID
        user_id: User ID from JWT token

    Returns:
        APIResponse with newsletter data
    """
    try:
        newsletter = await newsletter_service.get_newsletter(
            user_id=user_id,
            newsletter_id=newsletter_id
        )

        return APIResponse.success_response(newsletter)

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


@router.delete("/{newsletter_id}", response_model=APIResponse)
async def delete_newsletter(
    newsletter_id: str,
    user_id: str = Depends(get_current_user)
):
    """
    Delete newsletter.

    Requires: Authorization header with Bearer token
    User must be workspace owner.

    Args:
        newsletter_id: Newsletter ID
        user_id: User ID from JWT token

    Returns:
        APIResponse with success message
    """
    try:
        success = await newsletter_service.delete_newsletter(
            user_id=user_id,
            newsletter_id=newsletter_id
        )

        if success:
            return APIResponse.success_response({
                "message": "Newsletter deleted successfully",
                "newsletter_id": newsletter_id
            })
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete newsletter"
            )

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


@router.post("/{newsletter_id}/regenerate", response_model=APIResponse)
@limiter.limit(RateLimits.NEWSLETTER_GENERATION)
async def regenerate_newsletter(
    http_request: Request,
    newsletter_id: str,
    user_id: str = Depends(get_current_user)
):
    """
    Regenerate newsletter with same or updated settings.

    Rate limit: 5 requests per minute per IP

    Creates a new newsletter based on the original's settings.
    The original newsletter is not modified.

    Requires: Authorization header with Bearer token

    Args:
        newsletter_id: Original newsletter ID
        user_id: User ID from JWT token

    Returns:
        APIResponse with new newsletter
    """
    try:
        result = await newsletter_service.regenerate_newsletter(
            user_id=user_id,
            newsletter_id=newsletter_id
        )

        return APIResponse.success_response({
            "message": "Newsletter regenerated successfully",
            "newsletter": result['newsletter'],
            "content_items_count": result['content_items_count'],
            "sources_used": result['sources_used']
        })

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Newsletter regeneration failed: {str(e)}"
        )


@router.put("/{newsletter_id}", response_model=APIResponse)
async def update_newsletter(
    newsletter_id: str,
    request: UpdateNewsletterRequest,
    user_id: str = Depends(get_current_user)
):
    """
    Update newsletter details.

    Allows updating title, status, and sent_at timestamp.

    Requires: Authorization header with Bearer token

    Args:
        newsletter_id: Newsletter ID
        request: Update data
        user_id: User ID from JWT token

    Returns:
        APIResponse with updated newsletter
    """
    try:
        # Get newsletter to verify access
        await newsletter_service.get_newsletter(user_id, newsletter_id)

        # Build updates dict
        updates = {}
        if request.title is not None:
            updates['title'] = request.title
        if request.status is not None:
            updates['status'] = request.status
        if request.sent_at is not None:
            updates['sent_at'] = request.sent_at.isoformat()

        if not updates:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update"
            )

        # Update via service
        newsletter = await newsletter_service.update_newsletter_status(
            user_id=user_id,
            newsletter_id=newsletter_id,
            status=request.status if request.status else None,
            sent_at=request.sent_at,
            title=request.title if request.title else None
        )

        return APIResponse.success_response(newsletter)

    except HTTPException:
        raise
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
