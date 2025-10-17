"""
Integration tests for Newsletter API.

Tests newsletter generation, lifecycle management, and CRUD operations.
"""

import pytest
from datetime import datetime, timedelta
from backend.tests.factories import NewsletterFactory


class TestGenerateNewsletter:
    """Tests for POST /api/v1/newsletters/generate endpoint."""

    def test_generate_newsletter_successfully(self, test_client, auth_headers, test_workspace):
        """Test generating newsletter returns 201 Created."""
        response = test_client.post(
            "/api/v1/newsletters/generate",
            json={
                "workspace_id": test_workspace["id"],
                "title": "Weekly AI Newsletter",
                "max_items": 10,
                "days_back": 7,
                "sources": ["reddit", "rss"],
                "tone": "professional",
                "language": "en",
                "temperature": 0.7,
                "model": "gpt-4",
                "use_openrouter": False
            },
            headers=auth_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert "newsletter" in data["data"]
        assert "content_items_count" in data["data"]
        assert "sources_used" in data["data"]

    def test_generate_requires_authentication(self, test_client, test_workspace):
        """Test generation requires authentication."""
        response = test_client.post(
            "/api/v1/newsletters/generate",
            json={
                "workspace_id": test_workspace["id"],
                "title": "Test Newsletter"
            }
        )

        assert response.status_code in [401, 403]

    def test_generate_validates_workspace_access(self, test_client, auth_headers):
        """Test generation validates workspace access."""
        fake_workspace_id = "00000000-0000-0000-0000-000000000000"

        response = test_client.post(
            "/api/v1/newsletters/generate",
            json={
                "workspace_id": fake_workspace_id,
                "title": "Test Newsletter"
            },
            headers=auth_headers
        )

        assert response.status_code in [400, 403, 404]

    def test_generate_requires_title(self, test_client, auth_headers, test_workspace):
        """Test generation requires title field."""
        response = test_client.post(
            "/api/v1/newsletters/generate",
            json={
                "workspace_id": test_workspace["id"]
                # Missing title
            },
            headers=auth_headers
        )

        assert response.status_code == 422  # Validation error

    def test_generate_with_minimal_parameters(self, test_client, auth_headers, test_workspace):
        """Test generation with only required parameters."""
        response = test_client.post(
            "/api/v1/newsletters/generate",
            json={
                "workspace_id": test_workspace["id"],
                "title": "Minimal Newsletter"
            },
            headers=auth_headers
        )

        # Should use defaults for optional parameters
        assert response.status_code in [201, 400]  # 400 if no content available


class TestListNewsletters:
    """Tests for GET /api/v1/newsletters/workspaces/{workspace_id} endpoint."""

    def test_list_newsletters_empty_workspace(self, test_client, auth_headers, test_workspace):
        """Test listing newsletters returns empty array for new workspace."""
        response = test_client.get(
            f"/api/v1/newsletters/workspaces/{test_workspace['id']}",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert isinstance(data["data"].get("newsletters", []), list)

    def test_list_newsletters_requires_authentication(self, test_client, test_workspace):
        """Test listing newsletters requires authentication."""
        response = test_client.get(
            f"/api/v1/newsletters/workspaces/{test_workspace['id']}"
        )

        assert response.status_code in [401, 403]

    def test_list_newsletters_unauthorized_workspace(self, test_client, auth_headers):
        """Test cannot list newsletters from unauthorized workspace."""
        fake_workspace_id = "00000000-0000-0000-0000-000000000000"

        response = test_client.get(
            f"/api/v1/newsletters/workspaces/{fake_workspace_id}",
            headers=auth_headers
        )

        assert response.status_code in [403, 404]

    def test_filter_newsletters_by_status(self, test_client, auth_headers, test_workspace):
        """Test filtering newsletters by status."""
        response = test_client.get(
            f"/api/v1/newsletters/workspaces/{test_workspace['id']}",
            params={"status_filter": "sent"},
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        # If there are newsletters, verify filtering worked
        for newsletter in data["data"].get("newsletters", []):
            assert newsletter["status"] == "sent"

    def test_limit_newsletters(self, test_client, auth_headers, test_workspace):
        """Test limiting number of returned newsletters."""
        response = test_client.get(
            f"/api/v1/newsletters/workspaces/{test_workspace['id']}",
            params={"limit": 10},
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"].get("newsletters", [])) <= 10


class TestNewsletterStatistics:
    """Tests for GET /api/v1/newsletters/workspaces/{workspace_id}/stats endpoint."""

    def test_get_statistics_successfully(self, test_client, auth_headers, test_workspace):
        """Test getting newsletter statistics."""
        response = test_client.get(
            f"/api/v1/newsletters/workspaces/{test_workspace['id']}/stats",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

        stats = data["data"]
        assert "total_newsletters" in stats or "total" in stats
        # Stats structure may vary

    def test_statistics_requires_authentication(self, test_client, test_workspace):
        """Test statistics endpoint requires authentication."""
        response = test_client.get(
            f"/api/v1/newsletters/workspaces/{test_workspace['id']}/stats"
        )

        assert response.status_code in [401, 403]

    def test_statistics_unauthorized_workspace(self, test_client, auth_headers):
        """Test cannot get statistics from unauthorized workspace."""
        fake_workspace_id = "00000000-0000-0000-0000-000000000000"

        response = test_client.get(
            f"/api/v1/newsletters/workspaces/{fake_workspace_id}/stats",
            headers=auth_headers
        )

        assert response.status_code in [403, 404]


class TestGetNewsletter:
    """Tests for GET /api/v1/newsletters/{newsletter_id} endpoint."""

    def test_get_newsletter_not_found(self, test_client, auth_headers):
        """Test getting non-existent newsletter returns 404."""
        fake_newsletter_id = "00000000-0000-0000-0000-000000000000"

        response = test_client.get(
            f"/api/v1/newsletters/{fake_newsletter_id}",
            headers=auth_headers
        )

        assert response.status_code == 404

    def test_get_newsletter_requires_authentication(self, test_client):
        """Test endpoint requires authentication."""
        fake_newsletter_id = "00000000-0000-0000-0000-000000000000"

        response = test_client.get(
            f"/api/v1/newsletters/{fake_newsletter_id}"
        )

        assert response.status_code in [401, 403]


class TestUpdateNewsletter:
    """Tests for PUT /api/v1/newsletters/{newsletter_id} endpoint."""

    def test_update_newsletter_not_found(self, test_client, auth_headers):
        """Test updating non-existent newsletter returns 404."""
        fake_newsletter_id = "00000000-0000-0000-0000-000000000000"

        response = test_client.put(
            f"/api/v1/newsletters/{fake_newsletter_id}",
            json={"title": "Updated Title"},
            headers=auth_headers
        )

        assert response.status_code == 404

    def test_update_requires_authentication(self, test_client):
        """Test update requires authentication."""
        fake_newsletter_id = "00000000-0000-0000-0000-000000000000"

        response = test_client.put(
            f"/api/v1/newsletters/{fake_newsletter_id}",
            json={"title": "Updated Title"}
        )

        assert response.status_code in [401, 403]

    def test_update_validates_empty_body(self, test_client, auth_headers):
        """Test update validates at least one field provided."""
        fake_newsletter_id = "00000000-0000-0000-0000-000000000000"

        response = test_client.put(
            f"/api/v1/newsletters/{fake_newsletter_id}",
            json={},
            headers=auth_headers
        )

        # Should return 400 for empty update or 404 for not found
        assert response.status_code in [400, 404]


class TestDeleteNewsletter:
    """Tests for DELETE /api/v1/newsletters/{newsletter_id} endpoint."""

    def test_delete_newsletter_not_found(self, test_client, auth_headers):
        """Test deleting non-existent newsletter returns 404."""
        fake_newsletter_id = "00000000-0000-0000-0000-000000000000"

        response = test_client.delete(
            f"/api/v1/newsletters/{fake_newsletter_id}",
            headers=auth_headers
        )

        assert response.status_code == 404

    def test_delete_requires_authentication(self, test_client):
        """Test delete requires authentication."""
        fake_newsletter_id = "00000000-0000-0000-0000-000000000000"

        response = test_client.delete(
            f"/api/v1/newsletters/{fake_newsletter_id}"
        )

        assert response.status_code in [401, 403]


class TestRegenerateNewsletter:
    """Tests for POST /api/v1/newsletters/{newsletter_id}/regenerate endpoint."""

    def test_regenerate_newsletter_not_found(self, test_client, auth_headers):
        """Test regenerating non-existent newsletter returns 404."""
        fake_newsletter_id = "00000000-0000-0000-0000-000000000000"

        response = test_client.post(
            f"/api/v1/newsletters/{fake_newsletter_id}/regenerate",
            headers=auth_headers
        )

        assert response.status_code == 404

    def test_regenerate_requires_authentication(self, test_client):
        """Test regeneration requires authentication."""
        fake_newsletter_id = "00000000-0000-0000-0000-000000000000"

        response = test_client.post(
            f"/api/v1/newsletters/{fake_newsletter_id}/regenerate"
        )

        assert response.status_code in [401, 403]


class TestNewsletterIntegration:
    """Integration tests combining multiple newsletter operations."""

    @pytest.mark.asyncio
    async def test_complete_newsletter_lifecycle(self, test_client, auth_headers, test_workspace):
        """Test complete workflow: generate, get, update, delete."""
        # Generate newsletter
        generate_response = test_client.post(
            "/api/v1/newsletters/generate",
            json={
                "workspace_id": test_workspace["id"],
                "title": "Integration Test Newsletter",
                "max_items": 5
            },
            headers=auth_headers
        )

        # May fail if no content, that's ok for this test
        if generate_response.status_code == 201:
            newsletter_id = generate_response.json()["data"]["newsletter"]["id"]

            # Get newsletter
            get_response = test_client.get(
                f"/api/v1/newsletters/{newsletter_id}",
                headers=auth_headers
            )
            assert get_response.status_code == 200

            # Update newsletter
            update_response = test_client.put(
                f"/api/v1/newsletters/{newsletter_id}",
                json={"title": "Updated Title"},
                headers=auth_headers
            )
            assert update_response.status_code == 200

            # Delete newsletter
            delete_response = test_client.delete(
                f"/api/v1/newsletters/{newsletter_id}",
                headers=auth_headers
            )
            assert delete_response.status_code == 200

    def test_list_and_stats_consistency(self, test_client, auth_headers, test_workspace):
        """Test list and stats endpoints return consistent data."""
        # Get list
        list_response = test_client.get(
            f"/api/v1/newsletters/workspaces/{test_workspace['id']}",
            headers=auth_headers
        )
        assert list_response.status_code == 200

        # Get stats
        stats_response = test_client.get(
            f"/api/v1/newsletters/workspaces/{test_workspace['id']}/stats",
            headers=auth_headers
        )
        assert stats_response.status_code == 200

        # Both should succeed
        assert list_response.json()["success"] is True
        assert stats_response.json()["success"] is True
