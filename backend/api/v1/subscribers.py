"""
Subscriber API endpoints.

TODO (v2+): Add name field for personalized email greetings
To implement personalization:
1. Run migration: ALTER TABLE subscribers ADD COLUMN name TEXT;
2. Update SubscriberCreate model to include 'name' field
3. Update subscriber forms to collect name
4. Update email templates with {{ subscriber.name or 'there' }}
Decision: Skipped in MVP to focus on content quality (core differentiator)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from backend.models.subscriber import (
    SubscriberCreate,
    SubscriberBulkCreate,
    SubscriberUpdate,
    SubscriberResponse,
    SubscriberListResponse,
    SubscriberStatsResponse
)
from backend.models.responses import APIResponse
from backend.middleware.auth import get_current_user
from backend.api.v1.auth import verify_workspace_access
from ai_newsletter.database.supabase_client import SupabaseManager

router = APIRouter()


def get_db():
    """Get database instance."""
    return SupabaseManager()


@router.post("", response_model=APIResponse, status_code=status.HTTP_201_CREATED)
async def create_subscriber(
    request: SubscriberCreate,
    user_id: str = Depends(get_current_user)
):
    """
    Add a subscriber to workspace.

    Requires editor or owner role.
    """
    try:
        # SECURITY: Verify workspace access before creating subscriber
        await verify_workspace_access(request.workspace_id, user_id)

        db = get_db()

        # Create subscriber
        subscriber = db.add_subscriber(
            workspace_id=request.workspace_id,
            email=request.email,
            metadata=request.metadata
        )

        return APIResponse(
            success=True,
            data=subscriber,
            error=None
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create subscriber: {str(e)}"
        )


@router.post("/bulk", response_model=APIResponse)
async def create_subscribers_bulk(
    request: SubscriberBulkCreate,
    user_id: str = Depends(get_current_user)
):
    """
    Bulk add subscribers to workspace.

    Requires editor or owner role.
    """
    try:
        # SECURITY: Verify workspace access before bulk creating subscribers
        await verify_workspace_access(request.workspace_id, user_id)

        db = get_db()

        created = []
        failed = []

        for sub_data in request.subscribers:
            try:
                subscriber = db.add_subscriber(
                    workspace_id=request.workspace_id,
                    email=sub_data.get('email'),
                    metadata=sub_data.get('metadata', {})
                )
                created.append(subscriber)
            except Exception as e:
                failed.append({
                    'email': sub_data.get('email'),
                    'error': str(e)
                })

        return APIResponse(
            success=True,
            data={
                'created_count': len(created),
                'failed_count': len(failed),
                'created': created,
                'failed': failed
            },
            error=None
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to bulk create subscribers: {str(e)}"
        )


@router.get("/workspaces/{workspace_id}", response_model=APIResponse)
async def list_subscribers(
    workspace_id: str,
    status: str = None,
    limit: int = 1000,
    user_id: str = Depends(get_current_user)
):
    """List subscribers for workspace."""
    try:
        db = get_db()

        subscribers = db.list_subscribers(
            workspace_id=workspace_id,
            status=status,
            limit=limit
        )

        return APIResponse(
            success=True,
            data={
                'subscribers': subscribers,
                'count': len(subscribers),
                'workspace_id': workspace_id
            },
            error=None
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list subscribers: {str(e)}"
        )


@router.get("/workspaces/{workspace_id}/stats", response_model=APIResponse)
async def get_subscriber_stats(
    workspace_id: str,
    user_id: str = Depends(get_current_user)
):
    """Get subscriber statistics for workspace."""
    try:
        db = get_db()

        stats = db.get_subscriber_stats(workspace_id)

        return APIResponse(
            success=True,
            data=stats,
            error=None
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get subscriber stats: {str(e)}"
        )


@router.get("/{subscriber_id}", response_model=APIResponse)
async def get_subscriber(
    subscriber_id: str,
    user_id: str = Depends(get_current_user)
):
    """Get subscriber by ID."""
    try:
        db = get_db()

        subscriber = db.get_subscriber(subscriber_id)

        if not subscriber:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subscriber not found"
            )

        return APIResponse(
            success=True,
            data=subscriber,
            error=None
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get subscriber: {str(e)}"
        )


@router.put("/{subscriber_id}", response_model=APIResponse)
async def update_subscriber(
    subscriber_id: str,
    request: SubscriberUpdate,
    user_id: str = Depends(get_current_user)
):
    """Update subscriber."""
    try:
        db = get_db()

        # Build updates dict (only include provided fields)
        updates = {}
        if request.status is not None:
            updates['status'] = request.status
        if request.metadata is not None:
            updates['metadata'] = request.metadata

        subscriber = db.update_subscriber(subscriber_id, updates)

        return APIResponse(
            success=True,
            data=subscriber,
            error=None
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update subscriber: {str(e)}"
        )


@router.delete("/{subscriber_id}", response_model=APIResponse)
async def delete_subscriber(
    subscriber_id: str,
    user_id: str = Depends(get_current_user)
):
    """Delete subscriber."""
    try:
        db = get_db()

        success = db.delete_subscriber(subscriber_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subscriber not found"
            )

        return APIResponse(
            success=True,
            data={'deleted': True, 'subscriber_id': subscriber_id},
            error=None
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete subscriber: {str(e)}"
        )


@router.post("/{subscriber_id}/unsubscribe", response_model=APIResponse)
async def unsubscribe_subscriber(
    subscriber_id: str,
    user_id: str = Depends(get_current_user)
):
    """Mark subscriber as unsubscribed."""
    try:
        db = get_db()

        subscriber = db.unsubscribe(subscriber_id)

        return APIResponse(
            success=True,
            data=subscriber,
            error=None
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to unsubscribe: {str(e)}"
        )
