"""
CORS middleware configuration.
Allows frontend (Streamlit, Next.js, etc.) to access the API.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.config import settings


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
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],  # GET, POST, PUT, DELETE, etc.
        allow_headers=["*"],  # Authorization, Content-Type, etc.
    )
