"""
Scheduler API endpoints for managing automated jobs.
"""

from fastapi import APIRouter, Depends, HTTPException, status

from backend.models.scheduler import (
    SchedulerJobCreate,
    SchedulerJobUpdate,
    SchedulerJobResponse,
    SchedulerJobListResponse,
    SchedulerExecutionResponse,
    SchedulerExecutionListResponse,
    SchedulerExecutionStats,
    RunJobNowRequest,
    RunJobNowResponse
)
from backend.models.responses import APIResponse
from backend.middleware.auth import get_current_user
from backend.services.scheduler_service import scheduler_service

router = APIRouter()


# ========================================
# JOB MANAGEMENT ENDPOINTS
# ========================================

@router.post("", response_model=APIResponse, status_code=status.HTTP_201_CREATED)
async def create_scheduler_job(
    request: SchedulerJobCreate,
    user_id: str = Depends(get_current_user)
):
    """
    Create a new scheduled job.

    Creates a job that will automatically execute scraping, generating,
    and/or sending newsletters at the specified schedule.
    """
    try:
        job = await scheduler_service.create_job(user_id, request)

        return APIResponse(
            success=True,
            data=job,
            error=None
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create scheduled job: {str(e)}"
        )


@router.get("/workspaces/{workspace_id}", response_model=APIResponse)
async def list_scheduler_jobs(
    workspace_id: str,
    user_id: str = Depends(get_current_user)
):
    """
    List all scheduled jobs for a workspace.

    Returns all jobs with their current status, next run time,
    and execution statistics.
    """
    try:
        jobs = await scheduler_service.list_jobs(user_id, workspace_id)

        return APIResponse(
            success=True,
            data={
                'jobs': jobs,
                'count': len(jobs),
                'workspace_id': workspace_id
            },
            error=None
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list scheduled jobs: {str(e)}"
        )


@router.get("/{job_id}", response_model=APIResponse)
async def get_scheduler_job(
    job_id: str,
    user_id: str = Depends(get_current_user)
):
    """
    Get scheduler job details.

    Returns complete job configuration, schedule details,
    and execution statistics.
    """
    try:
        job = await scheduler_service.get_job(user_id, job_id)

        return APIResponse(
            success=True,
            data=job,
            error=None
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job not found: {str(e)}"
        )


@router.put("/{job_id}", response_model=APIResponse)
async def update_scheduler_job(
    job_id: str,
    request: SchedulerJobUpdate,
    user_id: str = Depends(get_current_user)
):
    """
    Update an existing scheduled job.

    Allows updating schedule configuration, actions, and settings.
    The next_run_at will be automatically recalculated.
    """
    try:
        job = await scheduler_service.update_job(user_id, job_id, request)

        return APIResponse(
            success=True,
            data=job,
            error=None
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update scheduled job: {str(e)}"
        )


@router.delete("/{job_id}", response_model=APIResponse)
async def delete_scheduler_job(
    job_id: str,
    user_id: str = Depends(get_current_user)
):
    """
    Delete a scheduled job.

    This will also delete all execution history for the job.
    """
    try:
        success = await scheduler_service.delete_job(user_id, job_id)

        return APIResponse(
            success=True,
            data={
                'deleted': success,
                'job_id': job_id
            },
            error=None
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete scheduled job: {str(e)}"
        )


# ========================================
# JOB CONTROL ENDPOINTS
# ========================================

@router.post("/{job_id}/pause", response_model=APIResponse)
async def pause_scheduler_job(
    job_id: str,
    user_id: str = Depends(get_current_user)
):
    """
    Pause a scheduled job.

    The job will not execute until resumed.
    """
    try:
        job = await scheduler_service.pause_job(user_id, job_id)

        return APIResponse(
            success=True,
            data=job,
            error=None
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to pause scheduled job: {str(e)}"
        )


@router.post("/{job_id}/resume", response_model=APIResponse)
async def resume_scheduler_job(
    job_id: str,
    user_id: str = Depends(get_current_user)
):
    """
    Resume a paused job.

    The job will be rescheduled and execute at the next scheduled time.
    """
    try:
        job = await scheduler_service.resume_job(user_id, job_id)

        return APIResponse(
            success=True,
            data=job,
            error=None
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to resume scheduled job: {str(e)}"
        )


@router.post("/{job_id}/run-now", response_model=APIResponse)
async def run_job_now(
    job_id: str,
    request: RunJobNowRequest,
    user_id: str = Depends(get_current_user)
):
    """
    Trigger immediate job execution.

    Runs the job immediately without waiting for the scheduled time.
    This does not affect the regular schedule.

    Use test_mode=true to prevent sending emails (useful for testing).
    """
    try:
        result = await scheduler_service.trigger_job_now(
            user_id=user_id,
            job_id=job_id,
            test_mode=request.test_mode
        )

        return APIResponse(
            success=True,
            data=result,
            error=None
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to trigger job execution: {str(e)}"
        )


# ========================================
# EXECUTION HISTORY ENDPOINTS
# ========================================

@router.get("/{job_id}/history", response_model=APIResponse)
async def get_job_execution_history(
    job_id: str,
    limit: int = 50,
    user_id: str = Depends(get_current_user)
):
    """
    Get execution history for a job.

    Returns recent executions with their results, duration,
    and any errors that occurred.
    """
    try:
        executions = await scheduler_service.get_execution_history(
            user_id=user_id,
            job_id=job_id,
            limit=limit
        )

        return APIResponse(
            success=True,
            data={
                'executions': executions,
                'count': len(executions),
                'job_id': job_id
            },
            error=None
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get execution history: {str(e)}"
        )


@router.get("/workspaces/{workspace_id}/activities", response_model=APIResponse)
async def get_workspace_activities(
    workspace_id: str,
    limit: int = 10,
    user_id: str = Depends(get_current_user)
):
    """
    Get recent activities for workspace dashboard.

    Returns recent execution history formatted as activity feed items.
    Includes scraping, generation, sending, and scheduled activities.

    Used by dashboard "Recent Activity" section.
    """
    try:
        activities = await scheduler_service.get_workspace_activities(
            user_id=user_id,
            workspace_id=workspace_id,
            limit=limit
        )

        return APIResponse(
            success=True,
            data={
                'activities': activities,
                'count': len(activities),
                'workspace_id': workspace_id
            },
            error=None
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get workspace activities: {str(e)}"
        )


@router.get("/{job_id}/stats", response_model=APIResponse)
async def get_job_execution_stats(
    job_id: str,
    user_id: str = Depends(get_current_user)
):
    """
    Get execution statistics for a job.

    Returns aggregated statistics including success rate,
    average duration, and execution counts.
    """
    try:
        stats = await scheduler_service.get_execution_stats(
            user_id=user_id,
            job_id=job_id
        )

        return APIResponse(
            success=True,
            data=stats,
            error=None
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get execution stats: {str(e)}"
        )
