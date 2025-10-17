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
from src.ai_newsletter.database.supabase_client import SupabaseManager


class SchedulerService:
    """Service for managing scheduled jobs."""

    def __init__(self):
        self._db: Optional[SupabaseManager] = None

    @property
    def db(self) -> SupabaseManager:
        """Lazy-load Supabase client."""
        if self._db is None:
            self._db = SupabaseManager()
        return self._db

    async def create_job(self, user_id: str, request: SchedulerJobCreate) -> Dict[str, Any]:
        """
        Create a new scheduled job.

        Args:
            user_id: User ID creating the job
            request: Job creation request

        Returns:
            Dict with created job details

        Raises:
            Exception: If workspace access denied or creation fails
        """
        # Validate workspace access
        workspace = self.db.get_workspace(request.workspace_id)
        if not workspace:
            raise Exception(f"Workspace {request.workspace_id} not found")

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

        return job

    async def list_jobs(self, user_id: str, workspace_id: str) -> List[Dict[str, Any]]:
        """
        List all jobs for a workspace.

        Args:
            user_id: User ID requesting the list
            workspace_id: Workspace ID to filter jobs

        Returns:
            List of jobs
        """
        # RLS ensures user can only see their workspaces
        jobs = self.db.list_scheduler_jobs(workspace_id)
        return jobs

    async def get_job(self, user_id: str, job_id: str) -> Dict[str, Any]:
        """
        Get job details.

        Args:
            user_id: User ID requesting the job
            job_id: Job ID

        Returns:
            Job details

        Raises:
            Exception: If job not found or access denied
        """
        job = self.db.get_scheduler_job(job_id)
        if not job:
            raise Exception(f"Job {job_id} not found")

        # Verify user has access to this workspace
        workspace = self.db.get_workspace(job['workspace_id'])
        if not workspace:
            raise Exception("Access denied")

        return job

    async def update_job(
        self,
        user_id: str,
        job_id: str,
        request: SchedulerJobUpdate
    ) -> Dict[str, Any]:
        """
        Update existing job.

        Args:
            user_id: User ID updating the job
            job_id: Job ID to update
            request: Update request

        Returns:
            Updated job details

        Raises:
            Exception: If job not found or access denied
        """
        # Get existing job
        job = await self.get_job(user_id, job_id)

        # Prepare updates (only include non-None fields)
        updates = {}
        for field, value in request.model_dump(exclude_unset=True).items():
            if value is not None:
                updates[field] = value

        # Update job
        updated_job = self.db.update_scheduler_job(job_id, updates)

        return updated_job

    async def delete_job(self, user_id: str, job_id: str) -> bool:
        """
        Delete a job.

        Args:
            user_id: User ID deleting the job
            job_id: Job ID to delete

        Returns:
            True if deleted successfully

        Raises:
            Exception: If job not found or access denied
        """
        # Verify access
        await self.get_job(user_id, job_id)

        # Delete job (cascade deletes executions)
        success = self.db.delete_scheduler_job(job_id)

        return success

    async def pause_job(self, user_id: str, job_id: str) -> Dict[str, Any]:
        """
        Pause a job.

        Args:
            user_id: User ID pausing the job
            job_id: Job ID to pause

        Returns:
            Updated job details
        """
        # Verify access
        await self.get_job(user_id, job_id)

        # Pause job
        updates = {
            "status": "paused",
            "is_enabled": False
        }
        updated_job = self.db.update_scheduler_job(job_id, updates)

        return updated_job

    async def resume_job(self, user_id: str, job_id: str) -> Dict[str, Any]:
        """
        Resume a paused job.

        Args:
            user_id: User ID resuming the job
            job_id: Job ID to resume

        Returns:
            Updated job details
        """
        # Verify access
        await self.get_job(user_id, job_id)

        # Resume job
        updates = {
            "status": "active",
            "is_enabled": True
        }
        updated_job = self.db.update_scheduler_job(job_id, updates)

        return updated_job

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

    async def get_execution_history(
        self,
        user_id: str,
        job_id: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get execution history for a job.

        Args:
            user_id: User ID requesting history
            job_id: Job ID
            limit: Maximum number of executions to return

        Returns:
            List of executions ordered by started_at DESC
        """
        # Verify access
        await self.get_job(user_id, job_id)

        # Get execution history
        executions = self.db.get_scheduler_executions(job_id, limit)

        return executions

    async def get_execution_stats(
        self,
        user_id: str,
        job_id: str
    ) -> Dict[str, Any]:
        """
        Get execution statistics for a job.

        Args:
            user_id: User ID requesting stats
            job_id: Job ID

        Returns:
            Dict with execution statistics
        """
        # Verify access
        job = await self.get_job(user_id, job_id)

        # Calculate success rate
        total = job.get('total_runs', 0)
        successful = job.get('successful_runs', 0)
        failed = job.get('failed_runs', 0)
        success_rate = (successful / total * 100) if total > 0 else 0

        # Get recent executions for avg duration
        executions = await self.get_execution_history(user_id, job_id, limit=10)
        avg_duration = None
        if executions:
            durations = [e['duration_seconds'] for e in executions if e.get('duration_seconds')]
            if durations:
                avg_duration = sum(durations) / len(durations)

        stats = {
            "total_executions": total,
            "successful": successful,
            "failed": failed,
            "partial": total - successful - failed,
            "success_rate": round(success_rate, 2),
            "avg_duration_seconds": round(avg_duration, 2) if avg_duration else None,
            "last_execution_at": job.get('last_run_at')
        }

        return stats


# Singleton instance
scheduler_service = SchedulerService()
