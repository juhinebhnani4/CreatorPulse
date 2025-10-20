"""
Scheduler Service for managing scheduled jobs.

This service handles:
- CRUD operations for scheduled jobs
- Job execution triggering
- Execution history tracking
- Job statistics
"""

from typing import Dict, List, Optional, Any
from datetime import datetime

from backend.models.scheduler import (
    SchedulerJobCreate,
    SchedulerJobUpdate,
    SchedulerJobResponse,
    SchedulerExecutionResponse,
    SchedulerExecutionStats
)
from backend.services.base_service import BaseService
from backend.utils.error_handling import handle_service_errors, NotFoundError
from backend.config.constants import SchedulerConstants


class SchedulerService(BaseService):
    """Service for managing scheduled jobs."""

    def __init__(self, db=None):
        """Initialize scheduler service with dependency injection."""
        super().__init__(db)

    @handle_service_errors(default_return=None, raise_on_error=True)
    async def create_job(self, user_id: str, request: SchedulerJobCreate) -> SchedulerJobResponse:
        """
        Create a new scheduled job.

        Args:
            user_id: User ID creating the job
            request: Job creation request

        Returns:
            SchedulerJobResponse with created job details

        Raises:
            NotFoundError: If workspace not found
            Exception: If creation fails
        """
        self.logger.info(f"Creating job '{request.name}' for workspace {request.workspace_id}")

        # Validate workspace access
        workspace = self.db.get_workspace(request.workspace_id)
        if not workspace:
            raise NotFoundError(f"Workspace {request.workspace_id} not found")

        # Prepare job data
        job_data = {
            "workspace_id": request.workspace_id,
            "name": request.name,
            "description": request.description,
            "schedule_type": request.schedule_type,
            "schedule_time": request.schedule_time,
            "schedule_days": request.schedule_days,
            "cron_expression": request.cron_expression,
            "timezone": request.timezone,
            "actions": request.actions,
            "config": request.config,
            "is_enabled": request.is_enabled,
            "created_by": user_id,
            "status": "active" if request.is_enabled else "disabled"
        }

        # Create job in database
        job = self.db.create_scheduler_job(job_data)
        self.logger.info(f"Job created successfully: {job.get('id')}")

        return SchedulerJobResponse(**job)

    @handle_service_errors(default_return=[], raise_on_error=False)
    async def list_jobs(self, user_id: str, workspace_id: str) -> List[SchedulerJobResponse]:
        """
        List all jobs for a workspace.

        Args:
            user_id: User ID requesting the list
            workspace_id: Workspace ID to filter jobs

        Returns:
            List of SchedulerJobResponse objects (empty list on error)
        """
        self.logger.info(f"Listing jobs for workspace {workspace_id}")
        # RLS ensures user can only see their workspaces
        jobs = self.db.list_scheduler_jobs(workspace_id)
        self.logger.info(f"Found {len(jobs)} jobs for workspace {workspace_id}")
        return [SchedulerJobResponse(**job) for job in jobs]

    @handle_service_errors(default_return=None, raise_on_error=True)
    async def get_job(self, user_id: str, job_id: str) -> SchedulerJobResponse:
        """
        Get job details.

        Args:
            user_id: User ID requesting the job
            job_id: Job ID

        Returns:
            SchedulerJobResponse with job details

        Raises:
            NotFoundError: If job not found or access denied
        """
        job = self.db.get_scheduler_job(job_id)
        if not job:
            raise NotFoundError(f"Job {job_id} not found")

        # Verify user has access to this workspace
        workspace = self.db.get_workspace(job['workspace_id'])
        if not workspace:
            raise NotFoundError("Access denied")

        return SchedulerJobResponse(**job)

    @handle_service_errors(default_return=None, raise_on_error=True)
    async def update_job(
        self,
        user_id: str,
        job_id: str,
        request: SchedulerJobUpdate
    ) -> SchedulerJobResponse:
        """
        Update existing job.

        Args:
            user_id: User ID updating the job
            job_id: Job ID to update
            request: Update request

        Returns:
            SchedulerJobResponse with updated job details

        Raises:
            NotFoundError: If job not found or access denied
        """
        # Get existing job (validates access)
        job = await self.get_job(user_id, job_id)

        # Prepare updates (only include non-None fields)
        updates = {}
        for field, value in request.model_dump(exclude_unset=True).items():
            if value is not None:
                updates[field] = value

        # Update job
        updated_job = self.db.update_scheduler_job(job_id, updates)

        return SchedulerJobResponse(**updated_job)

    @handle_service_errors(default_return=False, raise_on_error=True)
    async def delete_job(self, user_id: str, job_id: str) -> bool:
        """
        Delete a job.

        Args:
            user_id: User ID deleting the job
            job_id: Job ID to delete

        Returns:
            True if deleted successfully

        Raises:
            NotFoundError: If job not found or access denied
        """
        # Verify access
        await self.get_job(user_id, job_id)

        # Delete job (cascade deletes executions)
        success = self.db.delete_scheduler_job(job_id)

        return success

    @handle_service_errors(default_return=None, raise_on_error=True)
    async def pause_job(self, user_id: str, job_id: str) -> SchedulerJobResponse:
        """
        Pause a job.

        Args:
            user_id: User ID pausing the job
            job_id: Job ID to pause

        Returns:
            SchedulerJobResponse with updated job details
        """
        # Verify access
        await self.get_job(user_id, job_id)

        # Pause job
        updates = {
            "status": "paused",
            "is_enabled": False
        }
        updated_job = self.db.update_scheduler_job(job_id, updates)

        return SchedulerJobResponse(**updated_job)

    @handle_service_errors(default_return=None, raise_on_error=True)
    async def resume_job(self, user_id: str, job_id: str) -> SchedulerJobResponse:
        """
        Resume a paused job.

        Args:
            user_id: User ID resuming the job
            job_id: Job ID to resume

        Returns:
            SchedulerJobResponse with updated job details
        """
        # Verify access
        await self.get_job(user_id, job_id)

        # Resume job
        updates = {
            "status": "active",
            "is_enabled": True
        }
        updated_job = self.db.update_scheduler_job(job_id, updates)

        return SchedulerJobResponse(**updated_job)

    async def trigger_job_now(
        self,
        user_id: str,
        job_id: str,
        test_mode: bool = False
    ) -> Dict[str, Any]:
        """
        Trigger immediate job execution.

        Args:
            user_id: User ID triggering the job
            job_id: Job ID to execute
            test_mode: If True, run in test mode (don't send emails)

        Returns:
            Dict with execution_id and status

        Raises:
            Exception: If job not found or access denied
        """
        # Get job details
        job = await self.get_job(user_id, job_id)

        # Create execution record
        execution_data = {
            "job_id": job_id,
            "workspace_id": job['workspace_id'],
            "status": "running",
            "actions_performed": [],
            "started_at": datetime.utcnow().isoformat()
        }
        execution = self.db.create_scheduler_execution(execution_data)

        # TODO: Queue job for background worker
        # For now, we just create the execution record
        # The background worker will pick it up and execute it

        return {
            "execution_id": execution['id'],
            "job_id": job_id,
            "status": "queued",
            "message": "Job execution started" if not test_mode else "Job execution started in test mode"
        }

    @handle_service_errors(default_return=[], raise_on_error=False)
    async def get_execution_history(
        self,
        user_id: str,
        job_id: str,
        limit: int = None
    ) -> List[SchedulerExecutionResponse]:
        """
        Get execution history for a job.

        Args:
            user_id: User ID requesting history
            job_id: Job ID
            limit: Maximum number of executions to return (default from constants)

        Returns:
            List of SchedulerExecutionResponse objects ordered by started_at DESC
        """
        if limit is None:
            limit = SchedulerConstants.DEFAULT_EXECUTION_HISTORY_LIMIT

        # Verify access
        await self.get_job(user_id, job_id)

        # Get execution history
        executions = self.db.get_scheduler_executions(job_id, limit)

        return [SchedulerExecutionResponse(**execution) for execution in executions]

    @handle_service_errors(default_return=None, raise_on_error=True)
    async def get_execution_stats(
        self,
        user_id: str,
        job_id: str
    ) -> SchedulerExecutionStats:
        """
        Get execution statistics for a job.

        Args:
            user_id: User ID requesting stats
            job_id: Job ID

        Returns:
            SchedulerExecutionStats with execution statistics
        """
        # Verify access
        job = await self.get_job(user_id, job_id)

        # Calculate success rate
        total = job.total_runs or 0
        successful = job.successful_runs or 0
        failed = job.failed_runs or 0
        success_rate = (successful / total * 100) if total > 0 else 0

        # Get recent executions for avg duration
        executions = await self.get_execution_history(user_id, job_id, limit=10)
        avg_duration = None
        if executions:
            durations = [e.duration_seconds for e in executions if e.duration_seconds]
            if durations:
                avg_duration = sum(durations) / len(durations)

        stats = SchedulerExecutionStats(
            total_executions=total,
            successful=successful,
            failed=failed,
            partial=total - successful - failed,
            success_rate=round(success_rate, 2),
            avg_duration_seconds=round(avg_duration, 2) if avg_duration else None,
            last_execution_at=job.last_run_at
        )

        return stats


# Singleton instance
scheduler_service = SchedulerService()
