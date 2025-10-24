"""
Delivery API endpoints for sending newsletters.
"""

from typing import Optional
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


# Error logging wrapper for background tasks
async def _send_with_error_logging(
    user_id: str,
    newsletter_id: str,
    workspace_id: str,
    test_email: Optional[str]
):
    """Wrapper to catch and log background task errors."""
    try:
        print(f"\n📧 ===== STARTING NEWSLETTER DELIVERY =====")
        print(f"   Newsletter ID: {newsletter_id}")
        print(f"   Workspace ID: {workspace_id}")
        print(f"   Test Email: {test_email or 'ALL SUBSCRIBERS'}")

        result = await delivery_service.send_newsletter(
            user_id=user_id,
            newsletter_id=newsletter_id,
            workspace_id=workspace_id,
            test_email=test_email
        )

        print(f"\n✅ ===== DELIVERY COMPLETED SUCCESSFULLY =====")
        print(f"   Sent: {result.get('sent_count', 0)}")
        print(f"   Failed: {result.get('failed_count', 0)}")

        if result.get('errors'):
            print(f"\n⚠️  ERRORS ENCOUNTERED:")
            for i, error in enumerate(result['errors'][:5], 1):
                print(f"   {i}. {error}")

        print(f"========================================\n")
        return result

    except Exception as e:
        print(f"\n❌ ===== BACKGROUND TASK FAILED =====")
        print(f"   Error: {str(e)}")
        print(f"   Type: {type(e).__name__}")
        print(f"\n📋 FULL TRACEBACK:")
        import traceback
        traceback.print_exc()
        print(f"=====================================\n")
        raise


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
        # Start delivery in background with error logging
        background_tasks.add_task(
            _send_with_error_logging,
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
                'message': 'Newsletter delivery started (check backend logs for progress)'
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


@router.get("/test-smtp", response_model=APIResponse)
async def test_smtp_connection(user_id: str = Depends(get_current_user)):
    """
    Test SMTP configuration and send test email.
    Returns detailed diagnostic information.
    """
    try:
        from ai_newsletter.delivery.email_sender import EmailSender
        from ai_newsletter.config.settings import get_settings

        settings = get_settings()
        sender = EmailSender(config=settings.email)

        # Test connection
        connection_ok = sender.test_connection()
        config_status = sender.get_config_status()

        # Try sending test email
        if connection_ok:
            test_result = sender.send_newsletter(
                to_email=settings.email.from_email,  # Send to self
                subject="CreatorPulse SMTP Test",
                html_content="<h1>Test Email</h1><p>If you see this, SMTP is working!</p>",
                text_content="Test Email - If you see this, SMTP is working!"
            )
            config_status['test_send'] = test_result

        return APIResponse(
            success=connection_ok,
            data=config_status,
            error=None if connection_ok else "SMTP connection failed"
        )

    except Exception as e:
        return APIResponse(
            success=False,
            data=None,
            error=f"SMTP test error: {str(e)}"
        )
