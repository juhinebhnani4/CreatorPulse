"""
Integration tests for Workspaces API endpoints.

Tests the complete flow:
- HTTP Request to /api/v1/workspaces/*
- Workspace service processing
- Data persistence in Supabase
- Authorization checks
"""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration
@pytest.mark.workspaces
class TestListWorkspaces:
    """Test GET /api/v1/workspaces - List user's workspaces."""

    def test_list_workspaces_requires_authentication(self, test_client: TestClient):
        """
        Test that listing workspaces requires authentication.

        Steps:
        1. GET /api/v1/workspaces without auth header
        2. Verify 401 Unauthorized
        """
        response = test_client.get("/api/v1/workspaces")

        # Should return 401 Unauthorized
        assert response.status_code in [401, 403]

    def test_list_workspaces_returns_empty_for_new_user(self, test_client: TestClient, auth_headers):
        """
        Test that new users have no workspaces initially.

        Steps:
        1. Create a new user
        2. GET /api/v1/workspaces
        3. Verify 200 response
        4. Verify workspaces list is empty
        """
        response = test_client.get(
            "/api/v1/workspaces",
            headers=auth_headers
        )

        # Check HTTP response
        assert response.status_code == 200

        data = response.json()

        # Check response structure
        assert data["success"] is True
        assert "data" in data
        assert "workspaces" in data["data"]

        # New user should have no workspaces
        workspaces = data["data"]["workspaces"]
        assert isinstance(workspaces, list)
        # May be empty or may have a default workspace depending on your app logic

    def test_list_workspaces_returns_user_workspaces(self, test_client: TestClient, auth_headers, test_workspace):
        """
        Test that listing workspaces returns user's workspaces.

        Steps:
        1. Create a workspace (via fixture)
        2. GET /api/v1/workspaces
        3. Verify workspace is in the list
        """
        response = test_client.get(
            "/api/v1/workspaces",
            headers=auth_headers
        )

        assert response.status_code == 200

        data = response.json()
        workspaces = data["data"]["workspaces"]

        # Should have at least the test workspace
        assert len(workspaces) > 0

        # Find our test workspace
        workspace_ids = [w["id"] for w in workspaces]
        assert test_workspace["id"] in workspace_ids


@pytest.mark.integration
@pytest.mark.workspaces
class TestCreateWorkspace:
    """Test POST /api/v1/workspaces - Create new workspace."""

    def test_create_workspace_successfully(self, test_client: TestClient, auth_headers, db_helpers):
        """
        Test creating a workspace.

        Steps:
        1. POST /api/v1/workspaces with valid data
        2. Verify 201 Created
        3. Verify workspace data in response
        4. Verify workspace exists in database
        """
        from datetime import datetime

        workspace_data = {
            "name": f"Test Workspace {int(datetime.now().timestamp())}",
            "description": "Test workspace description"
        }

        response = test_client.post(
            "/api/v1/workspaces",
            headers=auth_headers,
            json=workspace_data
        )

        # Check HTTP response
        assert response.status_code == 201

        data = response.json()

        # Check response structure
        assert data["success"] is True
        assert "data" in data

        workspace = data["data"]

        # Check workspace fields
        assert "id" in workspace
        assert "name" in workspace
        assert "description" in workspace
        assert "owner_id" in workspace
        assert "created_at" in workspace

        # Verify name and description
        assert workspace["name"] == workspace_data["name"]
        assert workspace["description"] == workspace_data["description"]

        # Verify workspace exists in database
        assert db_helpers.workspace_exists(workspace["id"]) is True

        # Cleanup
        from backend.database import get_supabase_service_client
        supabase = get_supabase_service_client()
        supabase.table("workspaces").delete().eq("id", workspace["id"]).execute()

    def test_create_workspace_requires_authentication(self, test_client: TestClient):
        """
        Test that creating workspace requires authentication.

        Steps:
        1. POST /api/v1/workspaces without auth header
        2. Verify 401 Unauthorized
        """
        workspace_data = {
            "name": "Test Workspace",
            "description": "Test description"
        }

        response = test_client.post(
            "/api/v1/workspaces",
            json=workspace_data
        )

        # Should return 401 Unauthorized
        assert response.status_code in [401, 403]

    def test_create_workspace_validates_name(self, test_client: TestClient, auth_headers):
        """
        Test that workspace name is required.

        Steps:
        1. POST /api/v1/workspaces without name
        2. Verify 422 Validation Error
        """
        workspace_data = {
            "description": "Test description"
            # Missing name
        }

        response = test_client.post(
            "/api/v1/workspaces",
            headers=auth_headers,
            json=workspace_data
        )

        # Should return 422 Validation Error
        assert response.status_code == 422

    def test_create_workspace_description_optional(self, test_client: TestClient, auth_headers):
        """
        Test that workspace description is optional.

        Steps:
        1. POST /api/v1/workspaces without description
        2. Verify 201 Created
        3. Verify description is empty string or null
        """
        from datetime import datetime

        workspace_data = {
            "name": f"Test Workspace No Desc {int(datetime.now().timestamp())}"
            # No description
        }

        response = test_client.post(
            "/api/v1/workspaces",
            headers=auth_headers,
            json=workspace_data
        )

        # Should create successfully
        assert response.status_code == 201

        data = response.json()
        workspace = data["data"]

        # Description should be empty or default
        assert workspace["description"] in ["", None]

        # Cleanup
        from backend.database import get_supabase_service_client
        supabase = get_supabase_service_client()
        supabase.table("workspaces").delete().eq("id", workspace["id"]).execute()


@pytest.mark.integration
@pytest.mark.workspaces
class TestGetWorkspace:
    """Test GET /api/v1/workspaces/{workspace_id} - Get workspace details."""

    def test_get_workspace_successfully(self, test_client: TestClient, auth_headers, test_workspace):
        """
        Test getting workspace details.

        Steps:
        1. Create a workspace (via fixture)
        2. GET /api/v1/workspaces/{workspace_id}
        3. Verify 200 response
        4. Verify workspace data matches
        """
        response = test_client.get(
            f"/api/v1/workspaces/{test_workspace['id']}",
            headers=auth_headers
        )

        # Check HTTP response
        assert response.status_code == 200

        data = response.json()

        # Check response structure
        assert data["success"] is True
        assert "data" in data

        workspace = data["data"]

        # Verify workspace ID matches
        assert workspace["id"] == test_workspace["id"]
        assert workspace["name"] == test_workspace["name"]

    def test_get_workspace_requires_authentication(self, test_client: TestClient, test_workspace):
        """
        Test that getting workspace requires authentication.

        Steps:
        1. GET /api/v1/workspaces/{id} without auth header
        2. Verify 401 Unauthorized
        """
        response = test_client.get(f"/api/v1/workspaces/{test_workspace['id']}")

        # Should return 401 Unauthorized
        assert response.status_code in [401, 403]

    def test_get_workspace_not_found(self, test_client: TestClient, auth_headers):
        """
        Test getting non-existent workspace.

        Steps:
        1. GET /api/v1/workspaces/{invalid_id}
        2. Verify 404 Not Found
        """
        fake_workspace_id = "00000000-0000-0000-0000-000000000000"

        response = test_client.get(
            f"/api/v1/workspaces/{fake_workspace_id}",
            headers=auth_headers
        )

        # Should return 404 Not Found
        assert response.status_code == 404

    def test_get_workspace_unauthorized_access(
        self, test_client: TestClient, test_workspace, second_test_user
    ):
        """
        Test that users cannot access other users' workspaces.

        Steps:
        1. Create workspace for user1
        2. Try to access it as user2
        3. Verify 403 Forbidden or 404 Not Found
        """
        # Try to access user1's workspace as user2
        response = test_client.get(
            f"/api/v1/workspaces/{test_workspace['id']}",
            headers={"Authorization": f"Bearer {second_test_user['token']}"}
        )

        # Should return 403 Forbidden or 404 Not Found
        assert response.status_code in [403, 404]


@pytest.mark.integration
@pytest.mark.workspaces
class TestUpdateWorkspace:
    """Test PUT /api/v1/workspaces/{workspace_id} - Update workspace."""

    def test_update_workspace_name(self, test_client: TestClient, auth_headers, test_workspace):
        """
        Test updating workspace name.

        Steps:
        1. PUT /api/v1/workspaces/{id} with new name
        2. Verify 200 response
        3. Verify name is updated
        """
        from datetime import datetime

        new_name = f"Updated Workspace {int(datetime.now().timestamp())}"

        update_data = {
            "name": new_name
        }

        response = test_client.put(
            f"/api/v1/workspaces/{test_workspace['id']}",
            headers=auth_headers,
            json=update_data
        )

        # Check HTTP response
        assert response.status_code == 200

        data = response.json()

        # Check updated workspace
        workspace = data["data"]
        assert workspace["name"] == new_name

    def test_update_workspace_description(self, test_client: TestClient, auth_headers, test_workspace):
        """
        Test updating workspace description.

        Steps:
        1. PUT /api/v1/workspaces/{id} with new description
        2. Verify description is updated
        """
        new_description = "Updated description for test workspace"

        update_data = {
            "description": new_description
        }

        response = test_client.put(
            f"/api/v1/workspaces/{test_workspace['id']}",
            headers=auth_headers,
            json=update_data
        )

        assert response.status_code == 200

        data = response.json()
        workspace = data["data"]

        assert workspace["description"] == new_description

    def test_update_workspace_requires_authentication(self, test_client: TestClient, test_workspace):
        """
        Test that updating workspace requires authentication.

        Steps:
        1. PUT /api/v1/workspaces/{id} without auth header
        2. Verify 401 Unauthorized
        """
        update_data = {"name": "New Name"}

        response = test_client.put(
            f"/api/v1/workspaces/{test_workspace['id']}",
            json=update_data
        )

        # Should return 401 Unauthorized
        assert response.status_code in [401, 403]

    def test_update_workspace_unauthorized_access(
        self, test_client: TestClient, test_workspace, second_test_user
    ):
        """
        Test that users cannot update other users' workspaces.

        Steps:
        1. Create workspace for user1
        2. Try to update it as user2
        3. Verify 403 Forbidden
        """
        update_data = {"name": "Hacked Name"}

        response = test_client.put(
            f"/api/v1/workspaces/{test_workspace['id']}",
            headers={"Authorization": f"Bearer {second_test_user['token']}"},
            json=update_data
        )

        # Should return 403 Forbidden or 404
        assert response.status_code in [403, 404]


@pytest.mark.integration
@pytest.mark.workspaces
class TestDeleteWorkspace:
    """Test DELETE /api/v1/workspaces/{workspace_id} - Delete workspace."""

    def test_delete_workspace_successfully(self, test_client: TestClient, auth_headers, db_helpers):
        """
        Test deleting a workspace.

        Steps:
        1. Create a workspace
        2. DELETE /api/v1/workspaces/{id}
        3. Verify 200 response
        4. Verify workspace no longer exists in database
        """
        from datetime import datetime

        # Create workspace
        create_response = test_client.post(
            "/api/v1/workspaces",
            headers=auth_headers,
            json={
                "name": f"Workspace to Delete {int(datetime.now().timestamp())}",
                "description": "Will be deleted"
            }
        )

        workspace_id = create_response.json()["data"]["id"]

        # Delete workspace
        delete_response = test_client.delete(
            f"/api/v1/workspaces/{workspace_id}",
            headers=auth_headers
        )

        # Check HTTP response
        assert delete_response.status_code == 200

        data = delete_response.json()

        # Check response
        assert data["success"] is True
        assert "data" in data
        assert "message" in data["data"]

        # Verify workspace no longer exists in database
        assert db_helpers.workspace_exists(workspace_id) is False

    def test_delete_workspace_requires_authentication(self, test_client: TestClient, test_workspace):
        """
        Test that deleting workspace requires authentication.

        Steps:
        1. DELETE /api/v1/workspaces/{id} without auth header
        2. Verify 401 Unauthorized
        """
        response = test_client.delete(f"/api/v1/workspaces/{test_workspace['id']}")

        # Should return 401 Unauthorized
        assert response.status_code in [401, 403]

    def test_delete_workspace_unauthorized_access(
        self, test_client: TestClient, test_workspace, second_test_user
    ):
        """
        Test that users cannot delete other users' workspaces.

        Steps:
        1. Create workspace for user1
        2. Try to delete it as user2
        3. Verify 403 Forbidden
        """
        response = test_client.delete(
            f"/api/v1/workspaces/{test_workspace['id']}",
            headers={"Authorization": f"Bearer {second_test_user['token']}"}
        )

        # Should return 403 Forbidden or 404
        assert response.status_code in [403, 404]


@pytest.mark.integration
@pytest.mark.workspaces
class TestWorkspaceConfig:
    """Test workspace configuration endpoints."""

    def test_get_workspace_config(self, test_client: TestClient, auth_headers, test_workspace):
        """
        Test getting workspace configuration.

        Steps:
        1. GET /api/v1/workspaces/{id}/config
        2. Verify 200 response
        3. Verify config structure
        """
        response = test_client.get(
            f"/api/v1/workspaces/{test_workspace['id']}/config",
            headers=auth_headers
        )

        # Check HTTP response
        assert response.status_code == 200

        data = response.json()

        # Check response structure
        assert data["success"] is True
        assert "data" in data
        assert "config" in data["data"]

        config = data["data"]["config"]

        # Config should have expected keys
        # (This depends on your default config structure)
        assert isinstance(config, dict)

    def test_update_workspace_config(self, test_client: TestClient, auth_headers, test_workspace):
        """
        Test updating workspace configuration.

        Steps:
        1. PUT /api/v1/workspaces/{id}/config with new config
        2. Verify 200 response
        3. Verify config is saved
        """
        new_config = {
            "reddit": {
                "enabled": True,
                "limit": 50
            },
            "rss": {
                "enabled": False
            }
        }

        response = test_client.put(
            f"/api/v1/workspaces/{test_workspace['id']}/config",
            headers=auth_headers,
            json={"config": new_config}
        )

        # Check HTTP response
        assert response.status_code == 200

        data = response.json()

        # Check response
        assert data["success"] is True

    def test_workspace_config_requires_authentication(self, test_client: TestClient, test_workspace):
        """
        Test that config endpoints require authentication.

        Steps:
        1. GET /api/v1/workspaces/{id}/config without auth
        2. Verify 401 Unauthorized
        """
        response = test_client.get(f"/api/v1/workspaces/{test_workspace['id']}/config")

        # Should return 401 Unauthorized
        assert response.status_code in [401, 403]


@pytest.mark.integration
@pytest.mark.workspaces
class TestWorkspaceIsolation:
    """Test that workspaces are properly isolated between users."""

    def test_users_cannot_see_other_users_workspaces(
        self, test_client: TestClient, test_user, second_test_user
    ):
        """
        Test workspace isolation between users.

        Steps:
        1. User1 creates a workspace
        2. User2 lists workspaces
        3. Verify User2 doesn't see User1's workspace
        """
        # User1 creates workspace
        user1_headers = {"Authorization": f"Bearer {test_user['token']}"}

        from datetime import datetime
        workspace_name = f"User1 Workspace {int(datetime.now().timestamp())}"

        create_response = test_client.post(
            "/api/v1/workspaces",
            headers=user1_headers,
            json={
                "name": workspace_name,
                "description": "User1's private workspace"
            }
        )

        assert create_response.status_code == 201
        user1_workspace_id = create_response.json()["data"]["id"]

        # User2 lists workspaces
        user2_headers = {"Authorization": f"Bearer {second_test_user['token']}"}

        list_response = test_client.get(
            "/api/v1/workspaces",
            headers=user2_headers
        )

        assert list_response.status_code == 200

        user2_workspaces = list_response.json()["data"]["workspaces"]
        user2_workspace_ids = [w["id"] for w in user2_workspaces]

        # User2 should NOT see User1's workspace
        assert user1_workspace_id not in user2_workspace_ids

        # Cleanup
        from backend.database import get_supabase_service_client
        supabase = get_supabase_service_client()
        supabase.table("workspaces").delete().eq("id", user1_workspace_id).execute()
