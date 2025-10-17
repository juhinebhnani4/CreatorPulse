"""
Tracking API Endpoints - Handle tracking pixel and click tracking redirects.

Endpoints:
- GET /track/pixel/{encoded_params}.png - Tracking pixel for opens
- GET /track/click/{encoded_params} - Click tracking redirect
- GET /unsubscribe/{encoded_params} - Unsubscribe page
- POST /unsubscribe/{encoded_params} - Process unsubscribe
"""

import base64
from uuid import UUID

from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import Response, RedirectResponse, HTMLResponse

from backend.models.analytics_models import TrackingPixelParams, TrackingClickParams
from backend.services.analytics_service import AnalyticsService
from backend.services.tracking_service import TrackingService
from backend.database import get_supabase_client

router = APIRouter()


# 1×1 transparent PNG (base64)
TRACKING_PIXEL_PNG = base64.b64decode(
    'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII='
)


# =============================================================================
# TRACKING PIXEL (EMAIL OPENS)
# =============================================================================

@router.get(
    "/pixel/{encoded_params}.png",
    summary="Tracking Pixel",
    description="1×1 transparent PNG for tracking email opens",
    response_class=Response,
)
async def track_email_open(
    encoded_params: str,
    request: Request,
):
    """
    Tracking pixel endpoint for email opens.

    When an email is opened, the email client loads this image, which:
    1. Records an 'opened' event in the database
    2. Returns a 1×1 transparent PNG

    The encoded_params contains:
    - n: newsletter_id
    - r: recipient_email
    - w: workspace_id
    """
    try:
        # Decode parameters
        tracking_service = TrackingService()
        params = tracking_service.decode_tracking_params(encoded_params)

        # Extract parameters
        newsletter_id = UUID(params["n"])
        recipient_email = params["r"]
        workspace_id = UUID(params["w"])

        # Get user agent and IP from request
        user_agent = request.headers.get("user-agent")
        # Get IP from X-Forwarded-For if behind proxy, else from client
        ip_address = request.headers.get("x-forwarded-for", request.client.host)

        # Record 'opened' event
        analytics_service = AnalyticsService()
        await analytics_service.record_event(
            workspace_id=workspace_id,
            newsletter_id=newsletter_id,
            event_type="opened",
            recipient_email=recipient_email,
            user_agent=user_agent,
            ip_address=ip_address,
        )

    except Exception as e:
        # Silently fail - don't break email display if tracking fails
        print(f"Tracking pixel error: {e}")

    # Always return tracking pixel (even if recording failed)
    return Response(
        content=TRACKING_PIXEL_PNG,
        media_type="image/png",
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
        }
    )


# =============================================================================
# CLICK TRACKING (LINK CLICKS)
# =============================================================================

@router.get(
    "/click/{encoded_params}",
    summary="Click Tracking Redirect",
    description="Track link clicks and redirect to original URL",
)
async def track_link_click(
    encoded_params: str,
    request: Request,
):
    """
    Click tracking endpoint.

    When a tracked link is clicked:
    1. Records a 'clicked' event in the database
    2. Redirects to the original URL

    The encoded_params contains:
    - n: newsletter_id
    - r: recipient_email
    - w: workspace_id
    - c: content_item_id (optional)
    - u: original_url
    """
    try:
        # Decode parameters
        tracking_service = TrackingService()
        params = tracking_service.decode_tracking_params(encoded_params)

        # Extract parameters
        newsletter_id = UUID(params["n"])
        recipient_email = params["r"]
        workspace_id = UUID(params["w"])
        content_item_id = UUID(params["c"]) if params.get("c") else None
        original_url = params["u"]

        # Get user agent and IP from request
        user_agent = request.headers.get("user-agent")
        ip_address = request.headers.get("x-forwarded-for", request.client.host)

        # Record 'clicked' event (async, don't block redirect)
        analytics_service = AnalyticsService()
        await analytics_service.record_event(
            workspace_id=workspace_id,
            newsletter_id=newsletter_id,
            event_type="clicked",
            recipient_email=recipient_email,
            clicked_url=original_url,
            content_item_id=content_item_id,
            user_agent=user_agent,
            ip_address=ip_address,
        )

        # Redirect to original URL
        return RedirectResponse(url=original_url, status_code=302)

    except Exception as e:
        # If tracking fails, still try to redirect
        print(f"Click tracking error: {e}")

        # Try to extract original URL from params
        try:
            params = tracking_service.decode_tracking_params(encoded_params)
            original_url = params.get("u")
            if original_url:
                return RedirectResponse(url=original_url, status_code=302)
        except:
            pass

        # If all else fails, return error
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid tracking parameters"
        )


# =============================================================================
# UNSUBSCRIBE
# =============================================================================

@router.get(
    "/unsubscribe/{encoded_params}",
    summary="Unsubscribe Page",
    description="Display unsubscribe confirmation page",
    response_class=HTMLResponse,
)
async def unsubscribe_page(encoded_params: str):
    """
    Display unsubscribe confirmation page.

    The encoded_params contains:
    - w: workspace_id
    - e: recipient_email
    """
    try:
        # Decode parameters
        tracking_service = TrackingService()
        params = tracking_service.decode_tracking_params(encoded_params)

        workspace_id = params["w"]
        recipient_email = params["e"]

        # Return HTML page
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Unsubscribe</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    max-width: 600px;
                    margin: 50px auto;
                    padding: 20px;
                    text-align: center;
                }}
                h1 {{ color: #333; }}
                p {{ color: #666; line-height: 1.6; }}
                button {{
                    background-color: #dc3545;
                    color: white;
                    border: none;
                    padding: 12px 30px;
                    font-size: 16px;
                    border-radius: 5px;
                    cursor: pointer;
                    margin-top: 20px;
                }}
                button:hover {{ background-color: #c82333; }}
                .secondary {{
                    background-color: #6c757d;
                    margin-left: 10px;
                }}
                .secondary:hover {{ background-color: #5a6268; }}
            </style>
        </head>
        <body>
            <h1>Unsubscribe from Newsletter</h1>
            <p>Email: <strong>{recipient_email}</strong></p>
            <p>Are you sure you want to unsubscribe from this newsletter?</p>
            <p>You will no longer receive emails from this newsletter.</p>

            <form method="POST" action="/unsubscribe/{encoded_params}">
                <button type="submit">Yes, Unsubscribe Me</button>
                <button type="button" class="secondary" onclick="window.close()">Cancel</button>
            </form>
        </body>
        </html>
        """

        return HTMLResponse(content=html_content)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid unsubscribe link: {str(e)}"
        )


@router.post(
    "/unsubscribe/{encoded_params}",
    summary="Process Unsubscribe",
    description="Process unsubscribe request",
    response_class=HTMLResponse,
)
async def process_unsubscribe(encoded_params: str):
    """
    Process unsubscribe request.

    Marks the subscriber as unsubscribed in the database.
    """
    try:
        # Decode parameters
        tracking_service = TrackingService()
        params = tracking_service.decode_tracking_params(encoded_params)

        workspace_id = UUID(params["w"])
        recipient_email = params["e"]

        # Update subscriber status in database
        supabase = get_supabase_client()

        # Find subscriber
        subscriber_response = (
            supabase.table("subscribers")
            .select("*")
            .eq("workspace_id", str(workspace_id))
            .eq("email", recipient_email)
            .single()
            .execute()
        )

        if subscriber_response.data:
            subscriber = subscriber_response.data

            # Update status to unsubscribed
            supabase.table("subscribers").update({
                "status": "unsubscribed",
                "unsubscribed_at": "now()"
            }).eq("id", subscriber["id"]).execute()

            # Record 'unsubscribed' event (if there was a recent newsletter)
            # This requires knowing the newsletter_id - skip for now or implement newsletter lookup

        # Return success page
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Unsubscribed</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    max-width: 600px;
                    margin: 50px auto;
                    padding: 20px;
                    text-align: center;
                }}
                h1 {{ color: #28a745; }}
                p {{ color: #666; line-height: 1.6; }}
                .checkmark {{
                    font-size: 64px;
                    color: #28a745;
                }}
            </style>
        </head>
        <body>
            <div class="checkmark">✓</div>
            <h1>Successfully Unsubscribed</h1>
            <p>You have been unsubscribed from the newsletter.</p>
            <p>Email: <strong>{recipient_email}</strong></p>
            <p>You will no longer receive emails from us.</p>
            <p>If this was a mistake, please contact the newsletter administrator to resubscribe.</p>
        </body>
        </html>
        """

        return HTMLResponse(content=html_content)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process unsubscribe: {str(e)}"
        )


# =============================================================================
# LIST-UNSUBSCRIBE (ONE-CLICK)
# =============================================================================

@router.post(
    "/list-unsubscribe",
    summary="List-Unsubscribe (One-Click)",
    description="Handle one-click unsubscribe from email header",
)
async def list_unsubscribe(request: Request):
    """
    Handle one-click unsubscribe from List-Unsubscribe header.

    This is triggered by email clients when the user clicks "Unsubscribe"
    in the email header (improves deliverability).
    """
    try:
        # Get form data
        form = await request.form()
        list_unsubscribe = form.get("List-Unsubscribe")

        if not list_unsubscribe:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing List-Unsubscribe parameter"
            )

        # Extract encoded params from URL
        # Format: List-Unsubscribe: <https://domain.com/unsubscribe/{encoded_params}>
        import re
        match = re.search(r'/unsubscribe/([^>]+)', list_unsubscribe)
        if not match:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid List-Unsubscribe format"
            )

        encoded_params = match.group(1)

        # Process unsubscribe
        return await process_unsubscribe(encoded_params)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process list-unsubscribe: {str(e)}"
        )
