"""
Rate limiting middleware for FastAPI endpoints.

Provides rate limiting to protect resource-intensive endpoints from abuse.
Uses slowapi (FastAPI-compatible rate limiting library).

Installation:
    pip install slowapi

Usage:
    from backend.middleware.rate_limiter import limiter, get_remote_address

    @router.post("/generate")
    @limiter.limit("5/minute")
    async def generate_newsletter(request: Request):
        # Endpoint implementation
"""

import os
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, Response
from fastapi.responses import JSONResponse


# Rate limit configuration from environment variables
DEFAULT_RATE_LIMIT = os.getenv("DEFAULT_RATE_LIMIT", "100/minute")
NEWSLETTER_GENERATION_LIMIT = os.getenv("NEWSLETTER_GENERATION_LIMIT", "5/minute")
TREND_DETECTION_LIMIT = os.getenv("TREND_DETECTION_LIMIT", "10/minute")
STYLE_TRAINING_LIMIT = os.getenv("STYLE_TRAINING_LIMIT", "10/minute")
ANALYTICS_EVENT_LIMIT = os.getenv("ANALYTICS_EVENT_LIMIT", "1000/minute")


# Initialize rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[DEFAULT_RATE_LIMIT],
    storage_uri=os.getenv("RATE_LIMIT_STORAGE_URI", "memory://"),
    strategy="fixed-window"
)


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> Response:
    """
    Custom handler for rate limit exceeded errors.

    Args:
        request: FastAPI request object
        exc: Rate limit exceeded exception

    Returns:
        JSON response with rate limit error
    """
    return JSONResponse(
        status_code=429,
        content={
            "success": False,
            "error": "RateLimitExceeded",
            "message": "Too many requests. Please try again later.",
            "detail": str(exc.detail),
            "retry_after": getattr(exc, 'retry_after', None)
        },
        headers={
            "Retry-After": str(getattr(exc, 'retry_after', 60))
        }
    )


# Rate limit decorators for common use cases
class RateLimits:
    """Predefined rate limits for different endpoint types."""

    # Resource-intensive operations
    NEWSLETTER_GENERATION = NEWSLETTER_GENERATION_LIMIT  # 5/minute
    TREND_DETECTION = TREND_DETECTION_LIMIT  # 10/minute
    STYLE_TRAINING = STYLE_TRAINING_LIMIT  # 10/minute

    # High-volume operations
    ANALYTICS_EVENT = ANALYTICS_EVENT_LIMIT  # 1000/minute

    # Standard CRUD operations
    CREATE = "20/minute"
    READ = "100/minute"
    UPDATE = "30/minute"
    DELETE = "10/minute"

    # Authentication
    LOGIN = "5/minute"
    SIGNUP = "3/minute"


# Export key functions and classes
__all__ = [
    'limiter',
    'get_remote_address',
    'rate_limit_exceeded_handler',
    'RateLimits'
]
