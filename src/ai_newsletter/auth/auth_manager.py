"""
Authentication manager for Supabase Auth.
"""

from typing import Optional, Dict, Any
from supabase import Client


class AuthManager:
    """Handle user authentication via Supabase."""

    def __init__(self, supabase_client: Client):
        """
        Initialize auth manager.

        Args:
            supabase_client: Initialized Supabase client
        """
        self.client = supabase_client

    def sign_up(self, email: str, password: str, **metadata) -> Dict[str, Any]:
        """
        Register a new user.

        Args:
            email: User email
            password: User password (min 6 characters)
            **metadata: Optional user metadata

        Returns:
            User data including access token

        Raises:
            Exception: If signup fails
        """
        result = self.client.auth.sign_up({
            'email': email,
            'password': password,
            'options': {
                'data': metadata
            }
        })

        return {
            'user': result.user,
            'session': result.session
        }

    def sign_in(self, email: str, password: str) -> Dict[str, Any]:
        """
        Sign in an existing user.

        Args:
            email: User email
            password: User password

        Returns:
            User data including access token

        Raises:
            Exception: If signin fails
        """
        result = self.client.auth.sign_in_with_password({
            'email': email,
            'password': password
        })

        return {
            'user': result.user,
            'session': result.session
        }

    def sign_in_with_magic_link(self, email: str) -> bool:
        """
        Send magic link to user's email.

        Args:
            email: User email

        Returns:
            True if magic link sent successfully
        """
        result = self.client.auth.sign_in_with_otp({
            'email': email
        })

        return result is not None

    def sign_in_with_provider(self, provider: str) -> str:
        """
        Get OAuth URL for social login.

        Args:
            provider: OAuth provider ('google', 'github', etc.)

        Returns:
            OAuth URL to redirect user to
        """
        result = self.client.auth.sign_in_with_oauth({
            'provider': provider
        })

        return result.url

    def sign_out(self) -> bool:
        """
        Sign out current user.

        Returns:
            True if signed out successfully
        """
        self.client.auth.sign_out()
        return True

    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """
        Get currently authenticated user.

        Returns:
            User data if authenticated, None otherwise
        """
        try:
            result = self.client.auth.get_user()
            return result.user
        except Exception:
            return None

    def get_session(self) -> Optional[Dict[str, Any]]:
        """
        Get current session.

        Returns:
            Session data if active, None otherwise
        """
        try:
            result = self.client.auth.get_session()
            return result
        except Exception:
            return None

    def refresh_session(self) -> Optional[Dict[str, Any]]:
        """
        Refresh authentication session.

        Returns:
            New session data
        """
        result = self.client.auth.refresh_session()
        return result.session

    def reset_password_email(self, email: str) -> bool:
        """
        Send password reset email.

        Args:
            email: User email

        Returns:
            True if email sent successfully
        """
        result = self.client.auth.reset_password_email(email)
        return result is not None

    def update_user(self, **attributes) -> Dict[str, Any]:
        """
        Update user attributes.

        Args:
            **attributes: User attributes to update

        Returns:
            Updated user data
        """
        result = self.client.auth.update_user(attributes)
        return result.user
