"""
Integration tests for Authentication API endpoints.

Tests the complete flow:
- HTTP Request to /api/v1/auth/*
- Auth service processing
- User creation/validation in Supabase
- JWT token generation
"""

import pytest
from fastapi.testclient import TestClient
from supabase import Client


@pytest.mark.integration
@pytest.mark.auth
class TestSignup:
    """Test user signup endpoint."""

    def test_signup_creates_user_successfully(self, test_client: TestClient, test_user_credentials, db_helpers):
        """
        Test that signup creates a user in the database.

        Steps:
        1. POST /api/v1/auth/signup with valid credentials
        2. Verify 200 response
        3. Verify user data in response
        4. Verify JWT token is returned
        5. Verify user exists in Supabase database
        """
        response = test_client.post(
            "/api/v1/auth/signup",
            json=test_user_credentials
        )

        # Check HTTP response
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.json()}"

        data = response.json()

        # Check response structure
        assert data["success"] is True
        assert data["error"] is None
        assert "data" in data

        user_data = data["data"]

        # Check user fields
        assert "user_id" in user_data
        assert "email" in user_data
        assert "username" in user_data
        assert "token" in user_data
        assert "expires_at" in user_data

        # Verify email and username match
        assert user_data["email"] == test_user_credentials["email"]
        assert user_data["username"] == test_user_credentials["username"]

        # Verify token is not empty
        assert len(user_data["token"]) > 0

        # Verify user exists in database
        assert db_helpers.user_exists(user_data["user_id"]) is True

        # Cleanup
        from backend.database import get_supabase_service_client
        supabase = get_supabase_service_client()
        supabase.auth.admin.delete_user(user_data["user_id"])

    def test_signup_rejects_duplicate_email(self, test_client: TestClient, test_user):
        """
        Test that signup rejects duplicate email addresses.

        Steps:
        1. Create a user (via test_user fixture)
        2. Try to signup with same email
        3. Verify 400 Bad Request
        4. Verify error message mentions duplicate/exists
        """
        duplicate_credentials = {
            "email": test_user["email"],  # Same email as existing user
            "username": "differentuser123",
            "password": "NewPassword123!"
        }

        response = test_client.post(
            "/api/v1/auth/signup",
            json=duplicate_credentials
        )

        # Should return 400 Bad Request
        assert response.status_code == 400

        data = response.json()
        assert "detail" in data
        assert "already exists" in data["detail"].lower() or "duplicate" in data["detail"].lower()

    def test_signup_validates_email_format(self, test_client: TestClient):
        """
        Test that signup validates email format.

        Steps:
        1. POST with invalid email
        2. Verify 422 Validation Error
        3. Verify error mentions email validation
        """
        invalid_email_data = {
            "email": "not-an-email",
            "username": "testuser123",
            "password": "SecurePass123!"
        }

        response = test_client.post(
            "/api/v1/auth/signup",
            json=invalid_email_data
        )

        # Should return 422 Unprocessable Entity (validation error)
        assert response.status_code == 422

        data = response.json()
        assert data["success"] is False
        assert "error" in data
        assert "VALIDATION_ERROR" in data["error"]["code"]

    def test_signup_validates_password_length(self, test_client: TestClient):
        """
        Test that signup validates password minimum length.

        Steps:
        1. POST with short password (< 8 chars)
        2. Verify 422 Validation Error
        """
        short_password_data = {
            "email": "test@example.com",
            "username": "testuser123",
            "password": "short"  # Only 5 characters
        }

        response = test_client.post(
            "/api/v1/auth/signup",
            json=short_password_data
        )

        # Should return 422 Validation Error
        assert response.status_code == 422

        data = response.json()
        assert data["success"] is False

    def test_signup_validates_username_length(self, test_client: TestClient):
        """
        Test that signup validates username length.

        Steps:
        1. POST with username < 3 characters
        2. Verify 422 Validation Error
        """
        short_username_data = {
            "email": "test@example.com",
            "username": "ab",  # Only 2 characters
            "password": "SecurePass123!"
        }

        response = test_client.post(
            "/api/v1/auth/signup",
            json=short_username_data
        )

        # Should return 422 Validation Error
        assert response.status_code == 422

    def test_signup_requires_all_fields(self, test_client: TestClient):
        """
        Test that signup requires all mandatory fields.

        Steps:
        1. POST with missing email
        2. Verify 422 Validation Error
        """
        incomplete_data = {
            "username": "testuser123",
            "password": "SecurePass123!"
            # Missing email
        }

        response = test_client.post(
            "/api/v1/auth/signup",
            json=incomplete_data
        )

        # Should return 422 Validation Error
        assert response.status_code == 422


@pytest.mark.integration
@pytest.mark.auth
class TestLogin:
    """Test user login endpoint."""

    def test_login_with_valid_credentials(self, test_client: TestClient, test_user, test_user_credentials):
        """
        Test login with correct email and password.

        Steps:
        1. Create a user (via test_user fixture)
        2. POST /api/v1/auth/login with correct credentials
        3. Verify 200 response
        4. Verify JWT token is returned
        5. Verify user data matches
        """
        # The test_user fixture already created the user
        # Now login with the original credentials

        login_data = {
            "email": test_user_credentials["email"],
            "password": test_user_credentials["password"]
        }

        response = test_client.post(
            "/api/v1/auth/login",
            json=login_data
        )

        # Check HTTP response
        assert response.status_code == 200

        data = response.json()

        # Check response structure
        assert data["success"] is True
        assert "data" in data

        user_data = data["data"]

        # Verify token is returned
        assert "token" in user_data
        assert len(user_data["token"]) > 0

        # Verify user info matches
        assert user_data["email"] == test_user["email"]
        assert user_data["user_id"] == test_user["user_id"]

    def test_login_with_invalid_email(self, test_client: TestClient):
        """
        Test login with non-existent email.

        Steps:
        1. POST /api/v1/auth/login with email that doesn't exist
        2. Verify 401 Unauthorized
        3. Verify error message about invalid credentials
        """
        login_data = {
            "email": "nonexistent@example.com",
            "password": "SomePassword123!"
        }

        response = test_client.post(
            "/api/v1/auth/login",
            json=login_data
        )

        # Should return 401 Unauthorized
        assert response.status_code == 401

        data = response.json()
        assert "detail" in data
        assert "invalid" in data["detail"].lower()

    def test_login_with_wrong_password(self, test_client: TestClient, test_user_credentials):
        """
        Test login with correct email but wrong password.

        Steps:
        1. Create a user
        2. POST /api/v1/auth/login with wrong password
        3. Verify 401 Unauthorized
        """
        # First create the user
        signup_response = test_client.post(
            "/api/v1/auth/signup",
            json=test_user_credentials
        )
        assert signup_response.status_code == 200
        user_data = signup_response.json()["data"]

        # Try to login with wrong password
        login_data = {
            "email": test_user_credentials["email"],
            "password": "WrongPassword123!"
        }

        response = test_client.post(
            "/api/v1/auth/login",
            json=login_data
        )

        # Should return 401 Unauthorized
        assert response.status_code == 401

        # Cleanup
        from backend.database import get_supabase_service_client
        supabase = get_supabase_service_client()
        supabase.auth.admin.delete_user(user_data["user_id"])

    def test_login_validates_email_format(self, test_client: TestClient):
        """
        Test that login validates email format.

        Steps:
        1. POST with invalid email format
        2. Verify 422 Validation Error
        """
        invalid_login_data = {
            "email": "not-an-email",
            "password": "SomePassword123!"
        }

        response = test_client.post(
            "/api/v1/auth/login",
            json=invalid_login_data
        )

        # Should return 422 Validation Error
        assert response.status_code == 422


@pytest.mark.integration
@pytest.mark.auth
class TestGetCurrentUser:
    """Test /me endpoint for getting current user info."""

    def test_get_current_user_with_valid_token(self, test_client: TestClient, test_user, auth_headers):
        """
        Test getting current user info with valid JWT token.

        Steps:
        1. Create a user and get token (via fixtures)
        2. GET /api/v1/auth/me with Authorization header
        3. Verify 200 response
        4. Verify user data is returned
        """
        response = test_client.get(
            "/api/v1/auth/me",
            headers=auth_headers
        )

        # Check HTTP response
        assert response.status_code == 200

        data = response.json()

        # Check response structure
        assert data["success"] is True
        assert "data" in data

        user_data = data["data"]

        # Verify user info matches
        assert user_data["user_id"] == test_user["user_id"]
        assert user_data["email"] == test_user["email"]

    def test_get_current_user_without_token(self, test_client: TestClient):
        """
        Test /me endpoint without Authorization header.

        Steps:
        1. GET /api/v1/auth/me without auth header
        2. Verify 401 Unauthorized or 403 Forbidden
        """
        response = test_client.get("/api/v1/auth/me")

        # Should return 401 or 403
        assert response.status_code in [401, 403]

    def test_get_current_user_with_invalid_token(self, test_client: TestClient):
        """
        Test /me endpoint with invalid JWT token.

        Steps:
        1. GET /api/v1/auth/me with fake token
        2. Verify 401 Unauthorized
        """
        response = test_client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid-token-12345"}
        )

        # Should return 401 Unauthorized
        assert response.status_code == 401


@pytest.mark.integration
@pytest.mark.auth
class TestLogout:
    """Test logout endpoint."""

    def test_logout_with_valid_token(self, test_client: TestClient, auth_headers):
        """
        Test logout with valid token.

        Note: JWT logout is client-side (just delete the token).
        This endpoint is for future server-side token invalidation.

        Steps:
        1. POST /api/v1/auth/logout with valid token
        2. Verify 200 response
        3. Verify success message
        """
        response = test_client.post(
            "/api/v1/auth/logout",
            headers=auth_headers
        )

        # Check HTTP response
        assert response.status_code == 200

        data = response.json()

        # Check response
        assert data["success"] is True
        assert "data" in data
        assert "message" in data["data"]

    def test_logout_without_token(self, test_client: TestClient):
        """
        Test logout without Authorization header.

        Steps:
        1. POST /api/v1/auth/logout without token
        2. Verify 401 Unauthorized
        """
        response = test_client.post("/api/v1/auth/logout")

        # Should return 401 Unauthorized
        assert response.status_code in [401, 403]
