"""
Workspaces API endpoints.
"""

from fastapi import APIRouter, HTTPException, status, Depends
from typing import List

from backend.models.workspace import (
    CreateWorkspaceRequest,
    UpdateWorkspaceRequest,
    WorkspaceResponse,
    WorkspaceConfigRequest,
    WorkspaceConfigResponse
)
from backend.models.responses import APIResponse
from backend.services.workspace_service import workspace_service
from backend.middleware.auth import get_current_user


router = APIRouter()


@router.get("", response_model=APIResponse)
async def list_workspaces(user_id: str = Depends(get_current_user)):
    """
    List all workspaces accessible to the current user.

    Requires: Authorization header with Bearer token

    Args:
        user_id: User ID from JWT token

    Returns:
        APIResponse with list of workspaces
    """
    try:
        workspaces = await workspace_service.list_workspaces(user_id)

        return APIResponse.success_response({
            "workspaces": workspaces,
            "count": len(workspaces)
        })

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("", response_model=APIResponse, status_code=status.HTTP_201_CREATED)
async def create_workspace(
    request: CreateWorkspaceRequest,
    user_id: str = Depends(get_current_user)
):
    """
    Create a new workspace.

    Requires: Authorization header with Bearer token

    Args:
        request: Workspace creation details
        user_id: User ID from JWT token

    Returns:
        APIResponse with created workspace data
    """
    try:
        workspace = await workspace_service.create_workspace(
            user_id=user_id,
            name=request.name,
            description=request.description or ""
        )

        return APIResponse.success_response(workspace)

    except Exception as e:
        error_msg = str(e)
        if "already exists" in error_msg.lower() or "unique" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Workspace with this name already exists"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_msg
        )


@router.get("/{workspace_id}", response_model=APIResponse)
async def get_workspace(
    workspace_id: str,
    user_id: str = Depends(get_current_user)
):
    """
    Get workspace details.

    Requires: Authorization header with Bearer token

    Args:
        workspace_id: Workspace ID
        user_id: User ID from JWT token

    Returns:
        APIResponse with workspace data
    """
    try:
        workspace = await workspace_service.get_workspace(user_id, workspace_id)
        return APIResponse.success_response(workspace)

    except Exception as e:
        error_msg = str(e).lower()
        if "not found" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found"
            )
        elif "don't have access" in error_msg or "no access" in error_msg or "permission" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this workspace"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put("/{workspace_id}", response_model=APIResponse)
async def update_workspace(
    workspace_id: str,
    request: UpdateWorkspaceRequest,
    user_id: str = Depends(get_current_user)
):
    """
    Update workspace details.

    Requires: Authorization header with Bearer token
    User must be workspace owner.

    Args:
        workspace_id: Workspace ID
        request: Update data
        user_id: User ID from JWT token

    Returns:
        APIResponse with updated workspace data
    """
    try:
        # Build updates dict (only include provided fields)
        updates = {}
        if request.name is not None:
            updates['name'] = request.name
        if request.description is not None:
            updates['description'] = request.description

        if not updates:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update"
            )

        workspace = await workspace_service.update_workspace(
            user_id=user_id,
            workspace_id=workspace_id,
            updates=updates
        )

        return APIResponse.success_response(workspace)

    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e).lower()
        if "not found" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found"
            )
        elif "don't have permission" in error_msg or "no permission" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to update this workspace"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/{workspace_id}", response_model=APIResponse)
async def delete_workspace(
    workspace_id: str,
    user_id: str = Depends(get_current_user)
):
    """
    Delete workspace.

    Requires: Authorization header with Bearer token
    User must be workspace owner.
    WARNING: This will delete all associated data (content, newsletters, etc.)

    Args:
        workspace_id: Workspace ID
        user_id: User ID from JWT token

    Returns:
        APIResponse with success message
    """
    try:
        await workspace_service.delete_workspace(user_id, workspace_id)

        return APIResponse.success_response({
            "message": "Workspace deleted successfully",
            "workspace_id": workspace_id
        })

    except Exception as e:
        error_msg = str(e).lower()
        if "not found" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found"
            )
        elif "don't have permission" in error_msg or "no permission" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to delete this workspace"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{workspace_id}/config", response_model=APIResponse)
async def get_workspace_config(
    workspace_id: str,
    user_id: str = Depends(get_current_user)
):
    """
    Get workspace configuration.

    Requires: Authorization header with Bearer token

    Args:
        workspace_id: Workspace ID
        user_id: User ID from JWT token

    Returns:
        APIResponse with configuration data
    """
    try:
        config = await workspace_service.get_workspace_config(user_id, workspace_id)
        return APIResponse.success_response({"config": config})

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put("/{workspace_id}/config", response_model=APIResponse)
async def save_workspace_config(
    workspace_id: str,
    request: WorkspaceConfigRequest,
    user_id: str = Depends(get_current_user)
):
    """
    Save workspace configuration.

    Requires: Authorization header with Bearer token
    User must have editor or owner role.

    Args:
        workspace_id: Workspace ID
        request: Configuration data
        user_id: User ID from JWT token

    Returns:
        APIResponse with saved configuration
    """
    try:
        result = await workspace_service.save_workspace_config(
            user_id=user_id,
            workspace_id=workspace_id,
            config=request.config
        )

        return APIResponse.success_response(result)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
