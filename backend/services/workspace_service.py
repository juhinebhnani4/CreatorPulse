"""
Workspace service - handles workspace CRUD and configuration.
Integrates with existing SupabaseManager.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import sys
from pathlib import Path

# Add src to path to import existing SupabaseManager
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from ai_newsletter.database.supabase_client import SupabaseManager


class WorkspaceService:
    """Service for workspace operations."""

    def __init__(self):
        """Initialize SupabaseManager."""
        self._db = None

    @property
    def db(self):
        """Lazy-load SupabaseManager."""
        if self._db is None:
            self._db = SupabaseManager()
        return self._db

    def _verify_workspace_access(self, user_id: str, workspace_id: str) -> bool:
        """
        Verify that user has access to workspace.

        Args:
            user_id: User ID
            workspace_id: Workspace ID

        Returns:
            True if user has access, False otherwise
        """
        try:
            # Check if user is owner
            workspace = self.db.get_workspace(workspace_id)
            if workspace and workspace.get('owner_id') == user_id:
                return True

            # Check if user has membership
            result = self.db.service_client.table('user_workspaces').select('*').eq(
                'user_id', user_id
            ).eq('workspace_id', workspace_id).execute()

            return len(result.data) > 0

        except Exception:
            return False

    async def create_workspace(
        self,
        user_id: str,
        name: str,
        description: str = ""
    ) -> Dict[str, Any]:
        """
        Create new workspace.

        Args:
            user_id: Owner user ID
            name: Workspace name
            description: Optional description

        Returns:
            Workspace data with role

        Raises:
            Exception: If creation fails
        """
        try:
            workspace = self.db.create_workspace(
                name=name,
                description=description,
                user_id=user_id
            )

            # Add role (user is owner)
            workspace['role'] = 'owner'

            return workspace

        except Exception as e:
            raise Exception(f"Failed to create workspace: {str(e)}")

    async def list_workspaces(self, user_id: str) -> List[Dict[str, Any]]:
        """
        List user's workspaces.

        Args:
            user_id: User ID

        Returns:
            List of workspaces with roles
        """
        try:
            workspaces = self.db.list_workspaces(user_id)
            return workspaces

        except Exception as e:
            raise Exception(f"Failed to list workspaces: {str(e)}")

    async def get_workspace(
        self,
        user_id: str,
        workspace_id: str
    ) -> Dict[str, Any]:
        """
        Get workspace by ID.

        Args:
            user_id: User ID (for permission check)
            workspace_id: Workspace ID

        Returns:
            Workspace data

        Raises:
            Exception: If not found or no access
        """
        try:
            workspace = self.db.get_workspace(workspace_id)

            if not workspace:
                raise Exception("Workspace not found")

            # Check if user has access
            if not self._verify_workspace_access(user_id, workspace_id):
                raise Exception("You don't have access to this workspace")

            return workspace

        except Exception as e:
            error_str = str(e).lower()
            # Handle different error cases
            if "not acceptable" in error_str or "406" in error_str or "single()" in error_str:
                raise Exception("Workspace not found")
            raise Exception(f"Failed to get workspace: {str(e)}")

    async def update_workspace(
        self,
        user_id: str,
        workspace_id: str,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update workspace.

        Args:
            user_id: User ID (for permission check)
            workspace_id: Workspace ID
            updates: Fields to update

        Returns:
            Updated workspace data

        Raises:
            Exception: If not found or no permission
        """
        try:
            # Check if workspace exists
            workspace = self.db.get_workspace(workspace_id)
            if not workspace:
                raise Exception("Workspace not found")

            # Check if user is owner (only owner can update)
            if workspace.get('owner_id') != user_id:
                raise Exception("You don't have permission to update this workspace")

            workspace = self.db.update_workspace(workspace_id, updates)
            return workspace

        except Exception as e:
            raise Exception(f"Failed to update workspace: {str(e)}")

    async def delete_workspace(
        self,
        user_id: str,
        workspace_id: str
    ) -> bool:
        """
        Delete workspace.

        Args:
            user_id: User ID (must be owner)
            workspace_id: Workspace ID

        Returns:
            True if deleted

        Raises:
            Exception: If not found or not owner
        """
        try:
            # Check if workspace exists
            workspace = self.db.get_workspace(workspace_id)
            if not workspace:
                raise Exception("Workspace not found")

            # Check if user is owner (only owner can delete)
            if workspace.get('owner_id') != user_id:
                raise Exception("You don't have permission to delete this workspace")

            success = self.db.delete_workspace(workspace_id)

            if not success:
                raise Exception("Failed to delete workspace")

            return True

        except Exception as e:
            raise Exception(f"Failed to delete workspace: {str(e)}")

    async def get_workspace_config(
        self,
        user_id: str,
        workspace_id: str
    ) -> Dict[str, Any]:
        """
        Get workspace configuration.

        Args:
            user_id: User ID
            workspace_id: Workspace ID

        Returns:
            Config data
        """
        try:
            config = self.db.get_workspace_config(workspace_id)
            return config

        except Exception as e:
            raise Exception(f"Failed to get config: {str(e)}")

    async def save_workspace_config(
        self,
        user_id: str,
        workspace_id: str,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Save workspace configuration.

        Args:
            user_id: User ID
            workspace_id: Workspace ID
            config: Configuration data

        Returns:
            Saved config data
        """
        try:
            result = self.db.save_workspace_config(
                workspace_id=workspace_id,
                config=config,
                user_id=user_id
            )
            return result

        except Exception as e:
            raise Exception(f"Failed to save config: {str(e)}")


# Global service instance
workspace_service = WorkspaceService()
