"""
Shared test fixtures for backend API tests.

Provides:
- FastAPI test client
- Test user creation/cleanup
- Authentication headers
- Test workspace creation
- Database cleanup utilities
"""

import pytest
import os
from datetime import datetime
from typing import Dict, Generator
from fastapi.testclient import TestClient
from supabase import create_client, Client

# Import your FastAPI app
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.main import app
from backend.database import get_supabase_service_client


# =============================================================================
# TEST CONFIGURATION
# =============================================================================

# Generate unique test identifiers
TEST_RUN_ID = int(datetime.now().timestamp())


def generate_test_email(prefix: str = "test") -> str:
    """Generate unique test email address."""
    import random
    random_id = random.randint(1000, 9999)
    return f"{prefix}-{TEST_RUN_ID}-{random_id}@example.com"


def generate_test_username(prefix: str = "user") -> str:
    """Generate unique test username."""
    import random
    random_id = random.randint(1000, 9999)
    return f"{prefix}{TEST_RUN_ID}{random_id}"


# =============================================================================
# CORE FIXTURES
# =============================================================================

@pytest.fixture(scope="session")
def test_client() -> Generator[TestClient, None, None]:
    """
    Create a FastAPI test client for making HTTP requests.

    Scope: session (one client for all tests)
    """
    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="session")
def supabase_client() -> Client:
    """
    Create a Supabase service client for database verification.

    Uses service key to bypass RLS for test verification.
    Scope: session (one client for all tests)
    """
    return get_supabase_service_client()


# =============================================================================
# AUTHENTICATION FIXTURES
# =============================================================================

@pytest.fixture
def test_user_credentials() -> Dict[str, str]:
    """
    Generate unique test user credentials.

    Returns:
        Dict with email, username, password
    """
    return {
        "email": generate_test_email("user"),
        "username": generate_test_username("testuser"),
        "password": "SecureTestPass123!"
    }


@pytest.fixture
def test_user(test_client: TestClient, test_user_credentials: Dict[str, str], supabase_client: Client):
    """
    Create a test user via API and return user data with token.

    Auto-cleanup: Deletes user after test completes.

    Returns:
        Dict with user_id, email, username, token
    """
    # Sign up the user
    response = test_client.post(
        "/api/v1/auth/signup",
        json=test_user_credentials
    )

    assert response.status_code == 200, f"Signup failed: {response.json()}"

    data = response.json()
    assert data["success"] is True, "Signup response should have success=True"

    user_data = data["data"]
    user_id = user_data["user_id"]

    # Return user data
    yield {
        "user_id": user_id,
        "email": user_data["email"],
        "username": user_data["username"],
        "token": user_data["token"]
    }

    # Cleanup: Delete user and related data
    try:
        # Delete from auth.users
        supabase_client.auth.admin.delete_user(user_id)

        # Delete from public.users (if exists)
        supabase_client.table("users").delete().eq("id", user_id).execute()

        # Delete workspaces owned by user (cascade should handle rest)
        supabase_client.table("workspaces").delete().eq("owner_id", user_id).execute()

    except Exception as e:
        print(f"Warning: Failed to cleanup test user {user_id}: {e}")


@pytest.fixture
def auth_headers(test_user: Dict[str, str]) -> Dict[str, str]:
    """
    Get authentication headers with Bearer token.

    Args:
        test_user: Test user fixture (depends on test_user)

    Returns:
        Dict with Authorization header
    """
    return {
        "Authorization": f"Bearer {test_user['token']}"
    }


@pytest.fixture
def second_test_user(test_client: TestClient, supabase_client: Client):
    """
    Create a second test user for isolation testing.

    Returns:
        Dict with user_id, email, username, token
    """
    credentials = {
        "email": generate_test_email("user2"),
        "username": generate_test_username("testuser2"),
        "password": "SecureTestPass123!"
    }

    response = test_client.post("/api/v1/auth/signup", json=credentials)
    assert response.status_code == 200

    data = response.json()
    user_data = data["data"]
    user_id = user_data["user_id"]

    yield {
        "user_id": user_id,
        "email": user_data["email"],
        "username": user_data["username"],
        "token": user_data["token"]
    }

    # Cleanup
    try:
        supabase_client.auth.admin.delete_user(user_id)
        supabase_client.table("users").delete().eq("id", user_id).execute()
        supabase_client.table("workspaces").delete().eq("owner_id", user_id).execute()
    except Exception as e:
        print(f"Warning: Failed to cleanup second test user {user_id}: {e}")


# =============================================================================
# WORKSPACE FIXTURES
# =============================================================================

@pytest.fixture
def test_workspace(test_client: TestClient, auth_headers: Dict[str, str], supabase_client: Client):
    """
    Create a test workspace for the authenticated user.

    Auto-cleanup: Deletes workspace after test completes.

    Returns:
        Dict with workspace data (id, name, description, etc.)
    """
    workspace_name = f"Test Workspace {TEST_RUN_ID}"

    response = test_client.post(
        "/api/v1/workspaces",
        headers=auth_headers,
        json={
            "name": workspace_name,
            "description": "Test workspace for integration tests"
        }
    )

    assert response.status_code == 201, f"Workspace creation failed: {response.json()}"

    data = response.json()
    workspace = data["data"]
    workspace_id = workspace["id"]

    yield workspace

    # Cleanup: Delete workspace (cascade should handle related data)
    try:
        supabase_client.table("workspaces").delete().eq("id", workspace_id).execute()
    except Exception as e:
        print(f"Warning: Failed to cleanup test workspace {workspace_id}: {e}")


# =============================================================================
# DATABASE VERIFICATION HELPERS
# =============================================================================

@pytest.fixture
def db_helpers(supabase_client: Client):
    """
    Helper functions for database verification.

    Returns:
        Object with helper methods for checking database state
    """
    class DBHelpers:
        def __init__(self, client: Client):
            self.client = client

        def user_exists(self, user_id: str) -> bool:
            """Check if user exists in database."""
            try:
                response = self.client.table("users").select("id").eq("id", user_id).execute()
                return len(response.data) > 0
            except:
                return False

        def workspace_exists(self, workspace_id: str) -> bool:
            """Check if workspace exists in database."""
            try:
                response = self.client.table("workspaces").select("id").eq("id", workspace_id).execute()
                return len(response.data) > 0
            except:
                return False

        def get_user_workspaces(self, user_id: str) -> list:
            """Get all workspaces for a user."""
            try:
                response = self.client.table("workspaces").select("*").eq("owner_id", user_id).execute()
                return response.data
            except:
                return []

        def workspace_belongs_to_user(self, workspace_id: str, user_id: str) -> bool:
            """Check if workspace belongs to user."""
            try:
                response = self.client.table("workspaces").select("owner_id").eq("id", workspace_id).execute()
                if len(response.data) > 0:
                    return response.data[0]["owner_id"] == user_id
                return False
            except:
                return False

    return DBHelpers(supabase_client)


# =============================================================================
# CLEANUP FIXTURES
# =============================================================================

@pytest.fixture(scope="session", autouse=True)
def cleanup_old_test_data(supabase_client: Client):
    """
    Clean up old test data before test session starts.

    Removes test users and workspaces older than 1 hour.
    Scope: session (runs once before all tests)
    """
    from datetime import datetime, timedelta

    cutoff_time = datetime.utcnow() - timedelta(hours=1)

    try:
        # Clean up old test workspaces
        supabase_client.table("workspaces").delete().like("name", "Test Workspace%").lt(
            "created_at", cutoff_time.isoformat()
        ).execute()

        # Clean up old test users
        supabase_client.table("users").delete().like("email", "%@example.com").lt(
            "created_at", cutoff_time.isoformat()
        ).execute()

        print(f"\nCleaned up test data older than {cutoff_time.isoformat()}")
    except Exception as e:
        print(f"\nWarning: Failed to cleanup old test data: {e}")

    yield

    # No cleanup after - individual fixtures handle their own cleanup
