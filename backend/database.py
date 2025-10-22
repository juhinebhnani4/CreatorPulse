"""
Database utilities - Supabase client initialization.
"""

from supabase import create_client, Client
from backend.settings import settings


def get_supabase_client() -> Client:
    """
    Get Supabase client instance.

    Returns:
        Configured Supabase client

    Raises:
        ValueError: If Supabase credentials are not configured
    """
    if not settings.supabase_url or not settings.supabase_key:
        raise ValueError(
            "Supabase credentials not configured. "
            "Set SUPABASE_URL and SUPABASE_KEY in .env file"
        )

    return create_client(
        settings.supabase_url,
        settings.supabase_key
    )


def get_supabase_service_client() -> Client:
    """
    Get Supabase service client instance (bypasses RLS).

    This should be used for:
    - Admin operations
    - Workspace access verification
    - Operations that need to bypass Row Level Security

    Returns:
        Configured Supabase service client

    Raises:
        ValueError: If Supabase credentials are not configured
    """
    if not settings.supabase_url or not settings.supabase_service_key:
        # Fallback to regular key if service key not available
        if settings.supabase_key:
            return get_supabase_client()

        raise ValueError(
            "Supabase credentials not configured. "
            "Set SUPABASE_URL and SUPABASE_SERVICE_KEY in .env file"
        )

    return create_client(
        settings.supabase_url,
        settings.supabase_service_key
    )
