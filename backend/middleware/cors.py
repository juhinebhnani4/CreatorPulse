"""
CORS middleware configuration.
Allows frontend (Streamlit, Next.js, etc.) to access the API.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.settings import settings


def setup_cors(app: FastAPI) -> None:
    """
    Configure CORS middleware.

    Allows requests from:
    - Streamlit (localhost:8501)
    - Next.js (localhost:3000)
    - Production frontend domains

    Args:
        app: FastAPI application instance
    """
    # SECURITY: Explicitly list allowed methods and headers instead of wildcards
    # Wildcards can expose the API to security risks
    allowed_methods = [
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE",
        "OPTIONS",  # Required for preflight requests
    ]

    allowed_headers = [
        "Authorization",  # JWT tokens
        "Content-Type",   # JSON, form data
        "Accept",         # Response format
        "Origin",         # CORS origin
        "X-Requested-With",  # AJAX requests
        "X-Tracking-Token",  # HMAC tracking
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=allowed_methods,
        allow_headers=allowed_headers,
        expose_headers=["Content-Disposition"],  # For file downloads
    )
