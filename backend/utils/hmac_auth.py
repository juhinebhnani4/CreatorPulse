"""
HMAC-based authentication for analytics tracking endpoints.

This module provides utilities for generating and verifying HMAC tokens
used to authenticate analytics events from email tracking pixels and links.
"""

import hmac
import hashlib
import time
from typing import Optional
from fastapi import HTTPException, Header, status

from backend.config.constants import AnalyticsConstants


def generate_tracking_token(
    newsletter_id: str,
    workspace_id: str,
    secret_key: str,
    timestamp: Optional[int] = None
) -> str:
    """
    Generate HMAC token for analytics tracking.

    Args:
        newsletter_id: Newsletter ID
        workspace_id: Workspace ID
        secret_key: Secret key for HMAC
        timestamp: Optional timestamp (defaults to current time)

    Returns:
        HMAC token string
    """
    if timestamp is None:
        timestamp = int(time.time())

    # Create message to sign
    message = f"{newsletter_id}:{workspace_id}:{timestamp}"

    # Generate HMAC
    token = hmac.new(
        secret_key.encode(),
        message.encode(),
        hashlib.sha256
    ).hexdigest()

    return f"{timestamp}.{token}"


def verify_tracking_token(
    token: str,
    newsletter_id: str,
    workspace_id: str,
    secret_key: str,
    max_age_seconds: int = AnalyticsConstants.TOKEN_EXPIRY_SECONDS
) -> bool:
    """
    Verify HMAC token for analytics tracking.

    Args:
        token: HMAC token to verify (format: "timestamp.signature")
        newsletter_id: Newsletter ID
        workspace_id: Workspace ID
        secret_key: Secret key for HMAC
        max_age_seconds: Maximum token age in seconds (default: 30 days)

    Returns:
        True if token is valid

    Raises:
        ValueError: If token format is invalid or token is expired
    """
    try:
        # Parse token
        parts = token.split(".")
        if len(parts) != 2:
            raise ValueError("Invalid token format")

        timestamp_str, signature = parts
        timestamp = int(timestamp_str)

        # Check if token is expired
        current_time = int(time.time())
        if current_time - timestamp > max_age_seconds:
            raise ValueError(f"Token expired (age: {current_time - timestamp}s)")

        # Regenerate expected signature
        expected_token = generate_tracking_token(
            newsletter_id,
            workspace_id,
            secret_key,
            timestamp
        )
        expected_signature = expected_token.split(".")[1]

        # Compare signatures using constant-time comparison
        if not hmac.compare_digest(signature, expected_signature):
            raise ValueError("Invalid token signature")

        return True

    except (ValueError, IndexError) as e:
        raise ValueError(f"Invalid token: {str(e)}")


async def verify_tracking_token_dependency(
    newsletter_id: str,
    workspace_id: str,
    x_tracking_token: Optional[str] = Header(None, alias="X-Tracking-Token")
) -> bool:
    """
    FastAPI dependency for verifying tracking tokens.

    Usage:
        @router.post("/events")
        async def record_event(
            event: EventData,
            verified: bool = Depends(verify_tracking_token_dependency)
        ):
            # Process event

    Args:
        newsletter_id: Newsletter ID from request
        workspace_id: Workspace ID from request
        x_tracking_token: HMAC token from X-Tracking-Token header

    Returns:
        True if token is valid

    Raises:
        HTTPException: If token is missing or invalid
    """
    if not x_tracking_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing tracking token. Include X-Tracking-Token header."
        )

    # Get secret key from environment
    import os
    secret_key = os.getenv("ANALYTICS_SECRET_KEY")
    if not secret_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Analytics secret key not configured"
        )

    try:
        is_valid = verify_tracking_token(
            x_tracking_token,
            newsletter_id,
            workspace_id,
            secret_key
        )

        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid tracking token"
            )

        return True

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
