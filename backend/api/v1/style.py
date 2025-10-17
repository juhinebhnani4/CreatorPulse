"""
Style Training API Endpoints

Endpoints for training and managing writing style profiles.
"""

from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID

from backend.models.style_profile import (
    TrainStyleRequest,
    TrainStyleResponse,
    StyleProfileResponse,
    StyleProfileUpdate,
    StyleProfileSummary,
    GeneratePromptRequest,
    GeneratePromptResponse
)
from backend.models.responses import APIResponse
from backend.middleware.auth import get_current_user
from backend.services.style_service import StyleAnalysisService
from backend.api.v1.auth import verify_workspace_access

router = APIRouter()


def get_style_service() -> StyleAnalysisService:
    """Dependency: Get style analysis service."""
    return StyleAnalysisService()




# =============================================================================
# STYLE PROFILE ENDPOINTS
# =============================================================================

@router.post("/train", response_model=APIResponse)
async def train_style_profile(
    request: TrainStyleRequest,
    current_user: str = Depends(get_current_user),
    style_service: StyleAnalysisService = Depends(get_style_service)
):
    """
    Train a writing style profile from newsletter samples.

    Analyzes 5+ newsletter samples to extract writing patterns including:
    - Tone and formality level
    - Sentence structure preferences
    - Vocabulary choices
    - Common phrases and avoided words
    - Structural patterns (intro style, emoji usage)

    **Requirements:**
    - Minimum 5 samples (recommended 20+ for best results)
    - Each sample should be at least 50 words
    - Set retrain=true to overwrite existing profile

    **Returns:**
    - Trained style profile with confidence scores
    - Analysis summary with detected patterns
    """
    try:
        # Verify workspace access
        await verify_workspace_access(request.workspace_id, current_user)

        # Analyze samples and create profile
        profile_data, analysis_summary = style_service.analyze_samples(
            request.samples,
            request.workspace_id
        )

        # Create or update profile
        profile = await style_service.create_or_update_profile(
            request.workspace_id,
            profile_data,
            retrain=request.retrain
        )

        response = TrainStyleResponse(
            success=True,
            message=f"Style profile trained successfully on {len(request.samples)} samples",
            profile=profile,
            analysis_summary=analysis_summary
        )

        return APIResponse.success_response(response)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to train style profile: {str(e)}"
        )


@router.get("/{workspace_id}", response_model=APIResponse)
async def get_style_profile(
    workspace_id: UUID,
    current_user: str = Depends(get_current_user),
    style_service: StyleAnalysisService = Depends(get_style_service)
):
    """
    Get the style profile for a workspace.

    Returns the complete style profile including:
    - Voice characteristics (tone, formality)
    - Sentence patterns
    - Vocabulary preferences
    - Example sentences for reference

    **Returns:**
    - Complete style profile if exists
    - 404 if no profile has been trained yet
    """
    try:
        # Verify workspace access
        await verify_workspace_access(workspace_id, current_user)

        # Get profile
        profile = await style_service.get_style_profile(workspace_id)

        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No style profile found. Train a profile first using POST /train"
            )

        return APIResponse.success_response(profile)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get style profile: {str(e)}"
        )


@router.get("/{workspace_id}/summary", response_model=APIResponse)
async def get_style_profile_summary(
    workspace_id: UUID,
    current_user: str = Depends(get_current_user),
    style_service: StyleAnalysisService = Depends(get_style_service)
):
    """
    Get a summary of the style profile for a workspace.

    Lighter endpoint that returns only key information:
    - Whether profile exists
    - Number of training samples
    - Basic tone and formality info
    - Last update timestamp

    Useful for checking profile status without fetching all details.

    **Returns:**
    - Profile summary (even if profile doesn't exist)
    """
    try:
        # Verify workspace access
        await verify_workspace_access(workspace_id, current_user)

        # Get summary
        summary = await style_service.get_style_summary(workspace_id)

        return APIResponse.success_response(summary)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get style summary: {str(e)}"
        )


@router.put("/{workspace_id}", response_model=APIResponse)
async def update_style_profile(
    workspace_id: UUID,
    updates: StyleProfileUpdate,
    current_user: str = Depends(get_current_user),
    style_service: StyleAnalysisService = Depends(get_style_service)
):
    """
    Update specific fields in a style profile.

    Allows manual adjustment of style parameters without retraining.
    Only provided fields will be updated.

    **Use cases:**
    - Fine-tune formality level
    - Add/remove favorite phrases
    - Adjust emoji usage
    - Modify section count preference

    **Returns:**
    - Updated style profile
    """
    try:
        # Verify workspace access
        await verify_workspace_access(workspace_id, current_user)

        # Check if profile exists
        existing = await style_service.get_style_profile(workspace_id)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No style profile found. Train a profile first using POST /train"
            )

        # Update profile
        update_dict = updates.model_dump(exclude_none=True)
        if not update_dict:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields provided for update"
            )

        updated_profile = style_service.db.update_style_profile(
            str(workspace_id),
            update_dict
        )

        profile_response = StyleProfileResponse(**updated_profile)

        return APIResponse.success_response(profile_response)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update style profile: {str(e)}"
        )


@router.delete("/{workspace_id}", response_model=APIResponse)
async def delete_style_profile(
    workspace_id: UUID,
    current_user: str = Depends(get_current_user),
    style_service: StyleAnalysisService = Depends(get_style_service)
):
    """
    Delete the style profile for a workspace.

    Completely removes the trained style profile.
    The workspace will revert to using default writing style.

    **Use cases:**
    - Start fresh with new training samples
    - Remove customization and use defaults
    - Clean up after testing

    **Returns:**
    - Deletion confirmation
    """
    try:
        # Verify workspace access
        await verify_workspace_access(workspace_id, current_user)

        # Delete profile
        deleted = await style_service.delete_profile(workspace_id)

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No style profile found to delete"
            )

        return APIResponse.success_response({
            "deleted": True,
            "workspace_id": str(workspace_id),
            "message": "Style profile deleted successfully"
        })

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete style profile: {str(e)}"
        )


@router.post("/prompt", response_model=APIResponse)
async def generate_style_prompt(
    request: GeneratePromptRequest,
    current_user: str = Depends(get_current_user),
    style_service: StyleAnalysisService = Depends(get_style_service)
):
    """
    Generate a style-specific prompt for AI newsletter generation.

    Converts the style profile into instructions that can be used with
    OpenAI/OpenRouter to generate newsletters matching your writing voice.

    **Use cases:**
    - Get prompt to use with newsletter generator
    - Preview how style will be applied
    - Debug style training results

    **Returns:**
    - Generated style prompt string
    - Profile summary
    - Indicator if profile exists
    """
    try:
        # Verify workspace access
        await verify_workspace_access(request.workspace_id, current_user)

        # Get profile
        profile = await style_service.get_style_profile(request.workspace_id)

        if not profile:
            # Return default prompt if no profile exists
            return APIResponse.success_response(GeneratePromptResponse(
                has_profile=False,
                prompt="Write in a clear, professional tone.",
                profile_summary=None
            ))

        # Generate style prompt
        style_prompt = style_service.generate_style_prompt(profile)

        # Get summary
        summary = await style_service.get_style_summary(request.workspace_id)

        response = GeneratePromptResponse(
            has_profile=True,
            prompt=style_prompt,
            profile_summary=summary
        )

        return APIResponse.success_response(response)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate style prompt: {str(e)}"
        )
