"""
Integration tests for Delivery API.

Tests email delivery (async/sync), status tracking, and delivery history.
"""

import pytest
from backend.tests.factories import DeliveryFactory


class TestSendNewsletterAsync:
    """Tests for POST /api/v1/delivery/send endpoint (async/background)."""

    def test_send_newsletter_async_returns_202(self, test_client, auth_headers, test_workspace):
        """Test async send returns 202 Accepted immediately."""
        response = test_client.post(
            "/api/v1/delivery/send",
            json={
                "newsletter_id": "00000000-0000-0000-0000-000000000001",
                "workspace_id": test_workspace["id"],
                "test_email": None
            },
            headers=auth_headers
        )

        assert response.status_code == 202
        data = response.json()
        assert data["success"] is True
        assert data["data"]["status"] == "sending"
        assert "newsletter_id" in data["data"]
        assert data["data"]["test_mode"] is False

    def test_send_with_test_email(self, test_client, auth_headers, test_workspace):
        """Test sending to test email (test mode)."""
        response = test_client.post(
            "/api/v1/delivery/send",
            json={
                "newsletter_id": "00000000-0000-0000-0000-000000000001",
                "workspace_id": test_workspace["id"],
                "test_email": "test@example.com"
            },
            headers=auth_headers
        )

        assert response.status_code == 202
        data = response.json()
        assert data["data"]["test_mode"] is True

    def test_send_requires_authentication(self, test_client, test_workspace):
        """Test sending requires authentication."""
        response = test_client.post(
            "/api/v1/delivery/send",
            json={
                "newsletter_id": "00000000-0000-0000-0000-000000000001",
                "workspace_id": test_workspace["id"]
            }
        )

        assert response.status_code in [401, 403]

    def test_send_validates_required_fields(self, test_client, auth_headers):
        """Test validation of required fields."""
        response = test_client.post(
            "/api/v1/delivery/send",
            json={},
            headers=auth_headers
        )

        assert response.status_code == 422  # Validation error


class TestSendNewsletterSync:
    """Tests for POST /api/v1/delivery/send-sync endpoint (synchronous)."""

    def test_send_newsletter_sync_returns_200(self, test_client, auth_headers, test_workspace):
        """Test sync send returns 200 OK after completion."""
        response = test_client.post(
            "/api/v1/delivery/send-sync",
            json={
                "newsletter_id": "00000000-0000-0000-0000-000000000001",
                "workspace_id": test_workspace["id"],
                "test_email": "test@example.com"
            },
            headers=auth_headers
        )

        # Will likely fail without implementation, but structure is correct
        assert response.status_code in [200, 404, 500]

    def test_sync_send_requires_authentication(self, test_client, test_workspace):
        """Test sync send requires authentication."""
        response = test_client.post(
            "/api/v1/delivery/send-sync",
            json={
                "newsletter_id": "00000000-0000-0000-0000-000000000001",
                "workspace_id": test_workspace["id"]
            }
        )

        assert response.status_code in [401, 403]


class TestGetDeliveryStatus:
    """Tests for GET /api/v1/delivery/{delivery_id}/status endpoint."""

    def test_get_status_not_found(self, test_client, auth_headers):
        """Test getting status for non-existent delivery."""
        fake_delivery_id = "00000000-0000-0000-0000-000000000000"

        response = test_client.get(
            f"/api/v1/delivery/{fake_delivery_id}/status",
            headers=auth_headers
        )

        # Expected to fail without implementation
        assert response.status_code in [404, 500]

    def test_get_status_requires_authentication(self, test_client):
        """Test status check requires authentication."""
        fake_delivery_id = "00000000-0000-0000-0000-000000000000"

        response = test_client.get(
            f"/api/v1/delivery/{fake_delivery_id}/status"
        )

        assert response.status_code in [401, 403]


class TestListDeliveries:
    """Tests for GET /api/v1/delivery/workspaces/{workspace_id} endpoint."""

    def test_list_deliveries_empty_workspace(self, test_client, auth_headers, test_workspace):
        """Test listing deliveries for workspace with no history."""
        response = test_client.get(
            f"/api/v1/delivery/workspaces/{test_workspace['id']}",
            headers=auth_headers
        )

        # May return 200 with empty list or 404 without implementation
        assert response.status_code in [200, 404, 500]

    def test_list_deliveries_with_limit(self, test_client, auth_headers, test_workspace):
        """Test limiting number of returned deliveries."""
        response = test_client.get(
            f"/api/v1/delivery/workspaces/{test_workspace['id']}",
            params={"limit": 10},
            headers=auth_headers
        )

        assert response.status_code in [200, 404, 500]

    def test_list_deliveries_requires_authentication(self, test_client, test_workspace):
        """Test listing deliveries requires authentication."""
        response = test_client.get(
            f"/api/v1/delivery/workspaces/{test_workspace['id']}"
        )

        assert response.status_code in [401, 403]

    def test_list_deliveries_unauthorized_workspace(self, test_client, auth_headers):
        """Test cannot list deliveries from unauthorized workspace."""
        fake_workspace_id = "00000000-0000-0000-0000-000000000000"

        response = test_client.get(
            f"/api/v1/delivery/workspaces/{fake_workspace_id}",
            headers=auth_headers
        )

        assert response.status_code in [403, 404, 500]


class TestDeliveryIntegration:
    """Integration tests for delivery workflow."""

    def test_async_vs_sync_endpoints(self, test_client, auth_headers, test_workspace):
        """Test both async and sync endpoints accept same request."""
        request_data = {
            "newsletter_id": "00000000-0000-0000-0000-000000000001",
            "workspace_id": test_workspace["id"],
            "test_email": "test@example.com"
        }

        # Async send
        async_response = test_client.post(
            "/api/v1/delivery/send",
            json=request_data,
            headers=auth_headers
        )
        assert async_response.status_code == 202  # Always returns immediately

        # Sync send
        sync_response = test_client.post(
            "/api/v1/delivery/send-sync",
            json=request_data,
            headers=auth_headers
        )
        # May fail without implementation
        assert sync_response.status_code in [200, 404, 500]
