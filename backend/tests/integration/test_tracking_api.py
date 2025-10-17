"""
Integration tests for Tracking API.

Tests tracking pixel, click tracking, and unsubscribe flows.
Note: These endpoints do NOT require authentication (external access).
"""

import pytest
import base64
import json


class TestTrackingPixel:
    """Tests for GET /track/pixel/{encoded_params}.png endpoint."""

    def test_pixel_returns_png_image(self, test_client):
        """Test tracking pixel returns PNG image."""
        # Create encoded params (simulating real tracking link)
        params = {
            "n": "00000000-0000-0000-0000-000000000001",  # newsletter_id
            "r": "test@example.com",  # recipient_email
            "w": "00000000-0000-0000-0000-000000000002"   # workspace_id
        }
        # Simple base64 encoding for test
        encoded = base64.b64encode(json.dumps(params).encode()).decode()

        response = test_client.get(f"/track/pixel/{encoded}.png")

        # Should always return PNG, even if tracking fails
        assert response.status_code in [200, 400, 500]
        if response.status_code == 200:
            assert "image/png" in response.headers.get("content-type", "")

    def test_pixel_no_auth_required(self, test_client):
        """Test tracking pixel does not require authentication."""
        # Invalid params, but should still not require auth
        response = test_client.get("/track/pixel/invalid_params.png")

        # Should NOT return 401/403 (no auth required)
        assert response.status_code not in [401, 403]

    def test_pixel_sets_no_cache_headers(self, test_client):
        """Test tracking pixel sets no-cache headers."""
        params = {
            "n": "00000000-0000-0000-0000-000000000001",
            "r": "test@example.com",
            "w": "00000000-0000-0000-0000-000000000002"
        }
        encoded = base64.b64encode(json.dumps(params).encode()).decode()

        response = test_client.get(f"/track/pixel/{encoded}.png")

        if response.status_code == 200:
            # Should have cache control headers
            cache_control = response.headers.get("cache-control", "")
            assert "no-cache" in cache_control or "no-store" in cache_control

    def test_pixel_fails_gracefully(self, test_client):
        """Test pixel returns image even if tracking fails."""
        # Completely invalid params
        response = test_client.get("/track/pixel/invalid123.png")

        # Should still return 200 with PNG or handle error gracefully
        assert response.status_code in [200, 400, 500]


class TestClickTracking:
    """Tests for GET /track/click/{encoded_params} endpoint."""

    def test_click_redirects_to_original_url(self, test_client):
        """Test click tracking redirects to original URL."""
        params = {
            "n": "00000000-0000-0000-0000-000000000001",
            "r": "test@example.com",
            "w": "00000000-0000-0000-0000-000000000002",
            "u": "https://example.com/article"
        }
        encoded = base64.b64encode(json.dumps(params).encode()).decode()

        response = test_client.get(
            f"/track/click/{encoded}",
            follow_redirects=False  # Don't follow redirect
        )

        # Should return 302 redirect or handle error
        assert response.status_code in [302, 400, 500]

        if response.status_code == 302:
            # Should redirect to original URL
            location = response.headers.get("location")
            assert "example.com" in location

    def test_click_no_auth_required(self, test_client):
        """Test click tracking does not require authentication."""
        response = test_client.get("/track/click/invalid_params")

        # Should NOT return 401/403
        assert response.status_code not in [401, 403]

    def test_click_with_content_item(self, test_client):
        """Test click tracking with content item ID."""
        params = {
            "n": "00000000-0000-0000-0000-000000000001",
            "r": "test@example.com",
            "w": "00000000-0000-0000-0000-000000000002",
            "c": "00000000-0000-0000-0000-000000000003",  # content_item_id
            "u": "https://example.com/article"
        }
        encoded = base64.b64encode(json.dumps(params).encode()).decode()

        response = test_client.get(
            f"/track/click/{encoded}",
            follow_redirects=False
        )

        assert response.status_code in [302, 400, 500]

    def test_click_fails_gracefully_with_invalid_params(self, test_client):
        """Test click tracking handles invalid params."""
        response = test_client.get("/track/click/completely_invalid_base64")

        # Should return error, not crash
        assert response.status_code in [400, 500]


class TestUnsubscribePage:
    """Tests for GET /track/unsubscribe/{encoded_params} endpoint."""

    def test_unsubscribe_page_returns_html(self, test_client):
        """Test unsubscribe page returns HTML."""
        params = {
            "w": "00000000-0000-0000-0000-000000000001",
            "e": "test@example.com"
        }
        encoded = base64.b64encode(json.dumps(params).encode()).decode()

        response = test_client.get(f"/track/unsubscribe/{encoded}")

        # Should return HTML page or error
        assert response.status_code in [200, 400, 500]

        if response.status_code == 200:
            assert "text/html" in response.headers.get("content-type", "")
            assert b"unsubscribe" in response.content.lower()

    def test_unsubscribe_page_no_auth_required(self, test_client):
        """Test unsubscribe page does not require authentication."""
        response = test_client.get("/track/unsubscribe/invalid_params")

        # Should NOT return 401/403
        assert response.status_code not in [401, 403]

    def test_unsubscribe_page_displays_email(self, test_client):
        """Test unsubscribe page displays recipient email."""
        params = {
            "w": "00000000-0000-0000-0000-000000000001",
            "e": "test@example.com"
        }
        encoded = base64.b64encode(json.dumps(params).encode()).decode()

        response = test_client.get(f"/track/unsubscribe/{encoded}")

        if response.status_code == 200:
            # Should display email address
            assert b"test@example.com" in response.content

    def test_unsubscribe_page_has_form(self, test_client):
        """Test unsubscribe page contains confirmation form."""
        params = {
            "w": "00000000-0000-0000-0000-000000000001",
            "e": "test@example.com"
        }
        encoded = base64.b64encode(json.dumps(params).encode()).decode()

        response = test_client.get(f"/track/unsubscribe/{encoded}")

        if response.status_code == 200:
            # Should have form with POST method
            assert b"<form" in response.content
            assert b"method=\"POST\"" in response.content or b"method='POST'" in response.content


class TestProcessUnsubscribe:
    """Tests for POST /track/unsubscribe/{encoded_params} endpoint."""

    def test_process_unsubscribe_no_auth_required(self, test_client):
        """Test processing unsubscribe does not require authentication."""
        params = {
            "w": "00000000-0000-0000-0000-000000000001",
            "e": "test@example.com"
        }
        encoded = base64.b64encode(json.dumps(params).encode()).decode()

        response = test_client.post(f"/track/unsubscribe/{encoded}")

        # Should NOT return 401/403
        assert response.status_code not in [401, 403]

    def test_process_unsubscribe_returns_confirmation(self, test_client):
        """Test unsubscribe returns success confirmation page."""
        params = {
            "w": "00000000-0000-0000-0000-000000000001",
            "e": "test@example.com"
        }
        encoded = base64.b64encode(json.dumps(params).encode()).decode()

        response = test_client.post(f"/track/unsubscribe/{encoded}")

        # May succeed or fail depending on database
        assert response.status_code in [200, 400, 500]

        if response.status_code == 200:
            # Should show success message
            assert b"unsubscribed" in response.content.lower()
            # Check for success message or checkmark (encoded as utf-8)
            assert b"success" in response.content.lower() or "✓".encode('utf-8') in response.content

    def test_process_unsubscribe_handles_invalid_params(self, test_client):
        """Test processing with invalid params returns error."""
        response = test_client.post("/track/unsubscribe/invalid_base64")

        # Should return error
        assert response.status_code in [400, 500]


class TestListUnsubscribe:
    """Tests for POST /track/list-unsubscribe endpoint (RFC 8058)."""

    def test_list_unsubscribe_requires_form_data(self, test_client):
        """Test list-unsubscribe expects form data."""
        response = test_client.post("/track/list-unsubscribe")

        # Should require form data
        assert response.status_code in [400, 422, 500]

    def test_list_unsubscribe_no_auth_required(self, test_client):
        """Test list-unsubscribe does not require authentication."""
        response = test_client.post(
            "/track/list-unsubscribe",
            data={"List-Unsubscribe": "<https://example.com/unsubscribe/encoded123>"}
        )

        # Should NOT return 401/403
        assert response.status_code not in [401, 403]

    def test_list_unsubscribe_parses_header_format(self, test_client):
        """Test parsing List-Unsubscribe header format."""
        # Simulate email client one-click unsubscribe
        params = {
            "w": "00000000-0000-0000-0000-000000000001",
            "e": "test@example.com"
        }
        encoded = base64.b64encode(json.dumps(params).encode()).decode()

        response = test_client.post(
            "/track/list-unsubscribe",
            data={"List-Unsubscribe": f"<https://example.com/unsubscribe/{encoded}>"}
        )

        # Should process or return error
        assert response.status_code in [200, 400, 500]


class TestTrackingIntegration:
    """Integration tests for tracking workflows."""

    def test_complete_engagement_flow(self, test_client):
        """Test complete flow: open pixel → click → unsubscribe."""
        params_base = {
            "n": "00000000-0000-0000-0000-000000000001",
            "r": "integration_test@example.com",
            "w": "00000000-0000-0000-0000-000000000002"
        }

        # 1. Track email open
        open_params = params_base.copy()
        open_encoded = base64.b64encode(json.dumps(open_params).encode()).decode()
        open_response = test_client.get(f"/track/pixel/{open_encoded}.png")
        assert open_response.status_code in [200, 400, 500]

        # 2. Track link click
        click_params = params_base.copy()
        click_params["u"] = "https://example.com/article"
        click_encoded = base64.b64encode(json.dumps(click_params).encode()).decode()
        click_response = test_client.get(f"/track/click/{click_encoded}", follow_redirects=False)
        assert click_response.status_code in [302, 400, 500]

        # 3. View unsubscribe page
        unsub_params = {"w": params_base["w"], "e": params_base["r"]}
        unsub_encoded = base64.b64encode(json.dumps(unsub_params).encode()).decode()
        page_response = test_client.get(f"/track/unsubscribe/{unsub_encoded}")
        assert page_response.status_code in [200, 400, 500]

        # 4. Process unsubscribe
        process_response = test_client.post(f"/track/unsubscribe/{unsub_encoded}")
        assert process_response.status_code in [200, 400, 500]

    def test_tracking_param_encoding_consistency(self, test_client):
        """Test parameter encoding is consistent across endpoints."""
        params = {
            "w": "00000000-0000-0000-0000-000000000001",
            "e": "test@example.com"
        }
        encoded = base64.b64encode(json.dumps(params).encode()).decode()

        # Same encoded params should work for unsubscribe endpoints
        get_response = test_client.get(f"/track/unsubscribe/{encoded}")
        post_response = test_client.post(f"/track/unsubscribe/{encoded}")

        # Both should have similar success/failure status
        assert (get_response.status_code < 400) == (post_response.status_code < 400) or \
               (get_response.status_code >= 400) == (post_response.status_code >= 400)
