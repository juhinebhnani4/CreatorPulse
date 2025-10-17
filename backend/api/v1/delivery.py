"""
Delivery API endpoints for sending newsletters.
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks

from backend.models.subscriber import (
    DeliveryRequest,
    DeliveryResponse,
    DeliveryListResponse
)
from backend.models.responses import APIResponse
from backend.middleware.auth import get_current_user
from backend.services.delivery_service import delivery_service

router = APIRouter()


@router.post("/send", response_model=APIResponse, status_code=status.HTTP_202_ACCEPTED)
async def send_newsletter(
    request: DeliveryRequest,
    background_tasks: BackgroundTasks,
    user_id: str = Depends(get_current_user)
):
    """
    Send newsletter to subscribers.

    If test_email is provided, sends only to that email.
    Otherwise, sends to all active subscribers.

    Returns 202 Accepted and processes send in background.
    """
    try:
        # Start delivery in background
        background_tasks.add_task(
            delivery_service.send_newsletter,
            user_id=user_id,
            newsletter_id=request.newsletter_id,
            workspace_id=request.workspace_id,
            test_email=request.test_email
        )

        return APIResponse(
            success=True,
            data={
                'status': 'sending',
                'newsletter_id': request.newsletter_id,
                'workspace_id': request.workspace_id,
                'test_mode': request.test_email is not None,
                'message': 'Newsletter delivery started'
            },
            error=None
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start delivery: {str(e)}"
        )


@router.post("/send-sync", response_model=APIResponse)
async def send_newsletter_sync(
    request: DeliveryRequest,
    user_id: str = Depends(get_current_user)
):
    """
    Send newsletter synchronously (waits for completion).

    Use for test sends or small subscriber lists.
    For production with many subscribers, use /send (background).
    """
    try:
        result = await delivery_service.send_newsletter(
            user_id=user_id,
            newsletter_id=request.newsletter_id,
            workspace_id=request.workspace_id,
            test_email=request.test_email
        )

        return APIResponse(
            success=True,
            data=result,
            error=None
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send newsletter: {str(e)}"
        )


@router.get("/{delivery_id}/status", response_model=APIResponse)
async def get_delivery_status(
    delivery_id: str,
    user_id: str = Depends(get_current_user)
):
    """Get delivery status by ID."""
    try:
        delivery = await delivery_service.get_delivery_status(
            user_id=user_id,
            delivery_id=delivery_id
        )

        return APIResponse(
            success=True,
            data=delivery,
            error=None
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get delivery status: {str(e)}"
        )


@router.get("/workspaces/{workspace_id}", response_model=APIResponse)
async def list_deliveries(
    workspace_id: str,
    limit: int = 50,
    user_id: str = Depends(get_current_user)
):
    """List delivery history for workspace."""
    try:
        deliveries = await delivery_service.list_deliveries(
            user_id=user_id,
            workspace_id=workspace_id,
            limit=limit
        )

        return APIResponse(
            success=True,
            data={
                'deliveries': deliveries,
                'count': len(deliveries),
                'workspace_id': workspace_id
            },
            error=None
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list deliveries: {str(e)}"
        )
