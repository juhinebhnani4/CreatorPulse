"""
Authentication API endpoints.
"""

from uuid import UUID
from fastapi import APIRouter, HTTPException, status, Depends

from backend.models.auth import SignupRequest, LoginRequest, AuthResponse, UserResponse
from backend.models.responses import APIResponse
from backend.services.auth_service import auth_service
from backend.middleware.auth import get_current_user
from backend.services.workspace_service import workspace_service


router = APIRouter()


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

async def verify_workspace_access(workspace_id: UUID, user_id: str):
    """
    Verify that a user has access to a workspace.

    Args:
        workspace_id: The workspace ID to check
        user_id: The user ID to verify

    Raises:
        HTTPException: If user doesn't have access to the workspace
    """
    try:
        from backend.database import get_supabase_service_client
        # Use service client to bypass RLS for access verification
        supabase = get_supabase_service_client()

        # Check if user has access via user_workspaces table
        response = supabase.table("user_workspaces").select("*").eq(
            "workspace_id", str(workspace_id)
        ).eq("user_id", user_id).execute()

        # Also check if user is the owner
        workspace_response = supabase.table("workspaces").select("owner_id").eq(
            "id", str(workspace_id)
        ).execute()

        has_membership = len(response.data) > 0
        is_owner = len(workspace_response.data) > 0 and workspace_response.data[0].get('owner_id') == user_id

        if not (has_membership or is_owner):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this workspace"
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to verify workspace access: {str(e)}"
        )


@router.post("/signup", response_model=APIResponse)
async def signup(request: SignupRequest):
    """
    Register a new user.

    Args:
        request: Signup details (email, password, username)

    Returns:
        APIResponse with user data and JWT token

    Raises:
        HTTPException: If user already exists or validation fails
    """
    try:
        result = await auth_service.signup(
            email=request.email,
            password=request.password,
            username=request.username
        )

        return APIResponse.success_response(result)

    except Exception as e:
        error_message = str(e)
        if "already exists" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_message
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_message
        )


@router.post("/login", response_model=APIResponse)
async def login(request: LoginRequest):
    """
    Login user and get JWT token.

    Args:
        request: Login credentials (email, password)

    Returns:
        APIResponse with user data and JWT token

    Raises:
        HTTPException: If credentials are invalid
    """
    try:
        result = await auth_service.login(
            email=request.email,
            password=request.password
        )

        return APIResponse.success_response(result)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )


@router.get("/me", response_model=APIResponse)
async def get_current_user_info(user_id: str = Depends(get_current_user)):
    """
    Get current authenticated user information.

    Requires: Authorization header with Bearer token

    Args:
        user_id: User ID from JWT token (injected by dependency)

    Returns:
        APIResponse with user information

    Raises:
        HTTPException: If user not found or token invalid
    """
    try:
        result = await auth_service.get_user(user_id)
        return APIResponse.success_response(result)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post("/logout", response_model=APIResponse)
async def logout(user_id: str = Depends(get_current_user)):
    """
    Logout user (client-side token deletion).

    Note: JWT tokens are stateless, so logout happens client-side by deleting the token.
    This endpoint is just for consistency and future server-side token invalidation.

    Args:
        user_id: User ID from JWT token

    Returns:
        APIResponse with success message
    """
    return APIResponse.success_response({
        "message": "Logged out successfully",
        "user_id": user_id
    })
