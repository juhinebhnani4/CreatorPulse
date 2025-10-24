"""
Authentication service - handles user signup, login, and token management.
Integrates with Supabase Auth.
"""

from typing import Dict, Any
from datetime import datetime, timedelta
from passlib.context import CryptContext
from supabase import create_client, Client

from backend.settings import settings
from backend.middleware.auth import create_access_token
from backend.database import get_supabase_service_client


# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """Service for authentication operations."""

    def __init__(self):
        """Initialize Supabase client."""
        self._supabase = None
        self._service_client = None

    @property
    def supabase(self) -> Client:
        """Lazy-load Supabase client."""
        if self._supabase is None:
            if not settings.supabase_url or not settings.supabase_key:
                raise ValueError("Supabase credentials not configured. Set SUPABASE_URL and SUPABASE_KEY in .env")

            self._supabase = create_client(
                settings.supabase_url,
                settings.supabase_key
            )
        return self._supabase

    @property
    def service_client(self) -> Client:
        """Lazy-load Supabase service client (bypasses RLS)."""
        if self._service_client is None:
            self._service_client = get_supabase_service_client()
        return self._service_client

    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt."""
        return pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash."""
        return pwd_context.verify(plain_password, hashed_password)

    async def signup(self, email: str, password: str, username: str) -> Dict[str, Any]:
        """
        Register new user using Supabase Auth.

        Args:
            email: User email
            password: User password
            username: Username

        Returns:
            {
                "user_id": "...",
                "email": "...",
                "username": "...",
                "token": "...",
                "expires_at": "..."
            }

        Raises:
            Exception: If user already exists or signup fails
        """
        try:
            # Sign up with Supabase Auth
            response = self.supabase.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": {
                        "username": username
                    }
                }
            })

            if not response.user:
                raise Exception("Signup failed")

            user = response.user

            # Create entry in public.users table using service client (bypasses RLS)
            try:
                # Explicitly convert UUID to string for PostgreSQL compatibility
                user_data = {
                    "id": str(user.id),  # Ensure UUID is string format
                    "email": str(user.email),
                    "username": str(username)
                }

                insert_response = self.service_client.table("users").insert(user_data).execute()

                # Verify insertion was successful
                if not insert_response.data:
                    raise Exception("Failed to create user record - no data returned")

                print(f"✓ User created in public.users table: {user.email}")

                # Create default workspace for new user
                try:
                    workspace_result = self.service_client.table('workspaces').insert({
                        'name': f"{username}'s Workspace",
                        'description': "Your default workspace",
                        'owner_id': str(user.id)
                    }).execute()

                    if workspace_result.data:
                        workspace_id = workspace_result.data[0]['id']

                        # Add user to user_workspaces table with owner role
                        self.service_client.table('user_workspaces').insert({
                            'user_id': str(user.id),
                            'workspace_id': workspace_id,
                            'role': 'owner',
                            'accepted_at': datetime.now().isoformat()
                        }).execute()

                        # Create default workspace config
                        self.service_client.table('workspace_configs').insert({
                            'workspace_id': workspace_id,
                            'config': {
                                'sources': [],  # User will add sources later
                                'generation': {
                                    'model': 'openai',
                                    'temperature': 0.7,
                                    'tone': 'professional',
                                    'language': 'en',
                                    'max_items': 10
                                },
                                'delivery': {
                                    'method': 'smtp',
                                    'from_name': username
                                }
                            },
                            'updated_by': str(user.id)
                        }).execute()

                        print(f"✓ Created default workspace: {workspace_id} for user {username}")

                except Exception as workspace_error:
                    # Don't fail signup if workspace creation fails
                    # User can create workspace manually later
                    print(f"⚠️ WARNING: Could not create default workspace: {workspace_error}")
                    # Continue with signup - user still gets account

            except Exception as user_table_error:
                # Critical error - rollback auth user and fail signup
                print(f"ERROR: Could not create user in public.users table: {user_table_error}")

                # Attempt to rollback by deleting the auth user
                try:
                    self.service_client.auth.admin.delete_user(user.id)
                    print(f"✓ Rolled back auth user: {user.id}")
                except Exception as rollback_error:
                    print(f"WARNING: Could not rollback auth user: {rollback_error}")

                # Raise the original error to fail the signup
                raise Exception(f"User creation failed: {str(user_table_error)}")

            # Create JWT token
            token_data = {"sub": user.id}
            expires_delta = timedelta(minutes=settings.access_token_expire_minutes)
            token = create_access_token(token_data, expires_delta)
            expires_at = datetime.utcnow() + expires_delta

            return {
                "user_id": user.id,
                "email": user.email,
                "username": username,
                "token": token,
                "expires_at": expires_at
            }

        except Exception as e:
            if "already registered" in str(e).lower():
                raise Exception("User with this email already exists")
            raise Exception(f"Signup failed: {str(e)}")

    async def login(self, email: str, password: str) -> Dict[str, Any]:
        """
        Login user using Supabase Auth.

        Args:
            email: User email
            password: User password

        Returns:
            {
                "user_id": "...",
                "email": "...",
                "username": "...",
                "token": "...",
                "expires_at": "..."
            }

        Raises:
            Exception: If credentials are invalid
        """
        try:
            # Sign in with Supabase Auth
            response = self.supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })

            if not response.user:
                raise Exception("Invalid credentials")

            user = response.user

            # Get username from user metadata
            username = user.user_metadata.get("username", email.split("@")[0])

            # Create JWT token
            token_data = {"sub": user.id}
            expires_delta = timedelta(minutes=settings.access_token_expire_minutes)
            token = create_access_token(token_data, expires_delta)
            expires_at = datetime.utcnow() + expires_delta

            return {
                "user_id": user.id,
                "email": user.email,
                "username": username,
                "token": token,
                "expires_at": expires_at
            }

        except Exception as e:
            raise Exception("Invalid email or password")

    async def get_user(self, user_id: str) -> Dict[str, Any]:
        """
        Get user information.

        Args:
            user_id: User ID

        Returns:
            {
                "user_id": "...",
                "email": "...",
                "username": "...",
                "created_at": "..."
            }

        Raises:
            Exception: If user not found
        """
        try:
            # Try to get user from public.users table first (more reliable)
            response = self.service_client.table("users").select("*").eq("id", user_id).execute()

            if response.data and len(response.data) > 0:
                user_data = response.data[0]
                return {
                    "user_id": user_data["id"],
                    "email": user_data["email"],
                    "username": user_data["username"],
                    "created_at": user_data["created_at"]
                }

            # Fallback: Get user from auth.users via admin API (requires service role)
            try:
                auth_response = self.service_client.auth.admin.get_user_by_id(user_id)

                if not auth_response.user:
                    raise Exception("User not found")

                user = auth_response.user
                username = user.user_metadata.get("username", user.email.split("@")[0])

                return {
                    "user_id": user.id,
                    "email": user.email,
                    "username": username,
                    "created_at": user.created_at
                }
            except Exception:
                raise Exception("User not found")

        except Exception as e:
            if "not found" in str(e).lower():
                raise Exception("User not found")
            raise Exception(f"Failed to get user: {str(e)}")


# Global service instance
auth_service = AuthService()
