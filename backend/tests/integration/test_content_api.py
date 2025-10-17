"""
Integration tests for Content API.

Tests content scraping, listing, filtering, and statistics endpoints.
"""

import pytest
from datetime import datetime, timedelta
from backend.tests.factories import ContentItemFactory, create_content_items


class TestContentScraping:
    """Tests for POST /api/v1/content/scrape endpoint."""

    def test_trigger_scraping_successfully(self, test_client, auth_headers, test_workspace):
        """Test triggering content scraping returns 202 Accepted."""
        response = test_client.post(
            "/api/v1/content/scrape",
            json={
                "workspace_id": test_workspace["id"],
                "sources": ["reddit", "rss"],
                "limit_per_source": 10
            },
            headers=auth_headers
        )

        assert response.status_code == 202
        data = response.json()
        assert data["success"] is True
        assert "scraping completed" in data["data"]["message"].lower()
        assert "total_items" in data["data"]
        assert "items_by_source" in data["data"]

    def test_scraping_requires_authentication(self, test_client, test_workspace):
        """Test scraping endpoint requires authentication."""
        response = test_client.post(
            "/api/v1/content/scrape",
            json={"workspace_id": test_workspace["id"]}
        )

        assert response.status_code in [401, 403]  # FastAPI returns 403 for missing auth

    def test_scraping_validates_workspace_exists(self, test_client, auth_headers):
        """Test scraping validates workspace exists."""
        fake_workspace_id = "00000000-0000-0000-0000-000000000000"

        response = test_client.post(
            "/api/v1/content/scrape",
            json={"workspace_id": fake_workspace_id},
            headers=auth_headers
        )

        # Should return 404 or 403
        assert response.status_code in [403, 404]

    def test_scraping_requires_workspace_id(self, test_client, auth_headers):
        """Test scraping requires workspace_id in request."""
        response = test_client.post(
            "/api/v1/content/scrape",
            json={},
            headers=auth_headers
        )

        assert response.status_code == 422  # Validation error


class TestListContent:
    """Tests for GET /api/v1/content/workspaces/{workspace_id} endpoint."""

    def test_list_content_empty_workspace(self, test_client, auth_headers, test_workspace):
        """Test listing content returns empty array for new workspace."""
        response = test_client.get(
            f"/api/v1/content/workspaces/{test_workspace['id']}",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert isinstance(data["data"]["items"], list)
        # May or may not be empty depending on scraping

    def test_list_content_requires_authentication(self, test_client, test_workspace):
        """Test listing content requires authentication."""
        response = test_client.get(
            f"/api/v1/content/workspaces/{test_workspace['id']}"
        )

        assert response.status_code in [401, 403]  # FastAPI returns 403 for missing auth

    def test_list_content_unauthorized_workspace(self, test_client, auth_headers):
        """Test cannot list content from unauthorized workspace."""
        # Use a non-existent workspace ID
        fake_workspace_id = "00000000-0000-0000-0000-000000000000"

        response = test_client.get(
            f"/api/v1/content/workspaces/{fake_workspace_id}",
            headers=auth_headers
        )

        # Should return 403 or 404
        assert response.status_code in [403, 404]

    def test_filter_content_by_source(self, test_client, auth_headers, test_workspace):
        """Test filtering content by source type."""
        response = test_client.get(
            f"/api/v1/content/workspaces/{test_workspace['id']}",
            params={"source": "reddit"},
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        # If there's content, verify filtering worked
        for item in data["data"]["items"]:
            assert item["source_type"] == "reddit"

    def test_filter_content_by_days(self, test_client, auth_headers, test_workspace):
        """Test filtering content by number of days."""
        response = test_client.get(
            f"/api/v1/content/workspaces/{test_workspace['id']}",
            params={"days": 7},
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_limit_parameter(self, test_client, auth_headers, test_workspace):
        """Test limiting number of returned items."""
        response = test_client.get(
            f"/api/v1/content/workspaces/{test_workspace['id']}",
            params={"limit": 10},
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        # Result should have at most 10 items
        assert len(data["data"].get("items", [])) <= 10


class TestContentStatistics:
    """Tests for GET /api/v1/content/workspaces/{workspace_id}/stats endpoint."""

    def test_get_statistics_successfully(self, test_client, auth_headers, test_workspace):
        """Test getting content statistics."""
        response = test_client.get(
            f"/api/v1/content/workspaces/{test_workspace['id']}/stats",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

        stats = data["data"]
        assert "total_items" in stats
        assert "items_by_source" in stats
        assert isinstance(stats["total_items"], int)
        assert isinstance(stats["items_by_source"], dict)

    def test_statistics_requires_authentication(self, test_client, test_workspace):
        """Test statistics endpoint requires authentication."""
        response = test_client.get(
            f"/api/v1/content/workspaces/{test_workspace['id']}/stats"
        )

        assert response.status_code in [401, 403]  # FastAPI returns 403 for missing auth

    def test_statistics_unauthorized_workspace(self, test_client, auth_headers):
        """Test cannot get statistics from unauthorized workspace."""
        fake_workspace_id = "00000000-0000-0000-0000-000000000000"

        response = test_client.get(
            f"/api/v1/content/workspaces/{fake_workspace_id}/stats",
            headers=auth_headers
        )

        assert response.status_code in [403, 404]


class TestContentBySource:
    """Tests for GET /api/v1/content/workspaces/{workspace_id}/sources/{source} endpoint."""

    def test_get_content_by_source_successfully(self, test_client, auth_headers, test_workspace):
        """Test getting content filtered by specific source."""
        source = "reddit"

        response = test_client.get(
            f"/api/v1/content/workspaces/{test_workspace['id']}/sources/{source}",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

        # All returned items should be from the specified source
        for item in data["data"]["items"]:
            assert item["source_type"] == source

    def test_get_content_by_source_requires_authentication(self, test_client, test_workspace):
        """Test endpoint requires authentication."""
        response = test_client.get(
            f"/api/v1/content/workspaces/{test_workspace['id']}/sources/reddit"
        )

        assert response.status_code in [401, 403]  # FastAPI returns 403 for missing auth

    def test_invalid_source_type(self, test_client, auth_headers, test_workspace):
        """Test handling of invalid source type."""
        response = test_client.get(
            f"/api/v1/content/workspaces/{test_workspace['id']}/sources/invalid_source",
            headers=auth_headers
        )

        # Should return 200 with empty results or 400 for invalid source
        assert response.status_code in [200, 400]
        if response.status_code == 200:
            data = response.json()
            assert data["data"]["items"] == []


class TestContentIntegration:
    """Integration tests combining multiple content operations."""

    @pytest.mark.asyncio
    async def test_scrape_and_list_workflow(self, test_client, auth_headers, test_workspace):
        """Test complete workflow: trigger scraping, wait, then list content."""
        # Trigger scraping
        scrape_response = test_client.post(
            "/api/v1/content/scrape",
            json={"workspace_id": test_workspace["id"]},
            headers=auth_headers
        )
        assert scrape_response.status_code == 202

        # List content (may be empty if scraping still in progress)
        list_response = test_client.get(
            f"/api/v1/content/workspaces/{test_workspace['id']}",
            headers=auth_headers
        )
        assert list_response.status_code == 200

        # Get statistics
        stats_response = test_client.get(
            f"/api/v1/content/workspaces/{test_workspace['id']}/stats",
            headers=auth_headers
        )
        assert stats_response.status_code == 200

    def test_multiple_filters_combined(self, test_client, auth_headers, test_workspace):
        """Test combining multiple filter parameters."""
        response = test_client.get(
            f"/api/v1/content/workspaces/{test_workspace['id']}",
            params={
                "source": "reddit",
                "days": 7,
                "limit": 20
            },
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

        # Verify source filter applied
        for item in data["data"].get("items", []):
            if "source_type" in item:
                assert item["source_type"] == "reddit"
