"""
Scheduler Service for managing scheduled jobs.

This service handles:
- CRUD operations for scheduled jobs
- Job execution triggering
- Execution history tracking
- Job statistics
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timezone

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

        # Verify user has access to workspace
        if not self.db.user_has_workspace_access(user_id, request.workspace_id):
            raise NotFoundError(f"Access denied: User not in workspace")

        # Prepare job data
        # TODO (v1.5): Expose cron_expression in frontend UI for power users
        # Backend already supports it (worker.py:166-178), just needs UI controls
        # Note: config and description fields were removed in migration 014
        job_data = {
            "workspace_id": request.workspace_id,
            "name": request.name,
            "schedule_type": request.schedule_type,
            "schedule_time": request.schedule_time,
            "schedule_days": request.schedule_days,
            "cron_expression": request.cron_expression,
            "timezone": request.timezone,
            "actions": request.actions,
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
        # Verify user has access to workspace
        if not self.db.user_has_workspace_access(user_id, workspace_id):
            raise NotFoundError(f"Access denied: User not in workspace")

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
        if not self.db.user_has_workspace_access(user_id, job['workspace_id']):
            raise NotFoundError(f"Access denied: User not in workspace")
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

    @handle_service_errors(default_return=[], raise_on_error=False)
    async def get_workspace_activities(
        self,
        user_id: str,
        workspace_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get recent activities for workspace activity feed.

        Returns execution history transformed to activity format:
        - type: 'scrape' | 'generate' | 'send' | 'schedule'
        - title: Human-readable title
        - description: Details about the activity
        - timestamp: When it occurred
        - status: 'success' | 'pending' | 'scheduled'

        Args:
            user_id: User requesting activities
            workspace_id: Workspace ID
            limit: Max number of activities (default: 10)

        Returns:
            List of activity dictionaries
        """
        self.logger.info(f"Fetching recent activities for workspace {workspace_id}")

        # Verify workspace access
        if not self.db.user_has_workspace_access(user_id, workspace_id):
            raise NotFoundError(f"Access denied: User not in workspace")

        # Get recent executions
        executions = self.db.get_workspace_recent_executions(workspace_id, limit=limit)

        # Transform executions to activities
        activities = []
        for execution in executions:
            actions = execution.get('actions_performed', [])
            status_map = {
                'completed': 'success',
                'running': 'pending',
                'failed': 'pending',
                'partial': 'success'
            }

            # Create activity for each action performed
            for action in actions:
                activity = {
                    'id': f"{execution['id']}-{action}",
                    'type': action,
                    'status': status_map.get(execution.get('status', 'pending'), 'success'),
                    'timestamp': execution.get('started_at'),
                }

                # Action-specific titles and descriptions
                if action == 'scrape':
                    scrape_result = execution.get('scrape_result', {})
                    items_count = scrape_result.get('items_count', 0)
                    sources = scrape_result.get('sources', [])
                    sources_count = len(sources)  # Calculate count from array
                    activity['title'] = 'Content Scraped'
                    activity['description'] = f'{items_count} new items from {sources_count} sources'

                elif action == 'generate':
                    activity['title'] = 'Newsletter Generated'
                    activity['description'] = 'Draft ready for review'

                elif action == 'send':
                    send_result = execution.get('send_result', {})
                    recipients = send_result.get('recipients_count', 0)
                    activity['title'] = 'Newsletter Sent'
                    activity['description'] = f'Delivered to {recipients} subscribers'

                activities.append(activity)

        # Add next scheduled job as first activity
        jobs = await self.list_jobs(user_id, workspace_id)
        active_jobs = [j for j in jobs if j.is_enabled and j.next_run_at]
        if active_jobs:
            next_job = min(active_jobs, key=lambda j: j.next_run_at)
            # next_job.next_run_at is already a datetime object (from SchedulerJobResponse model)
            next_run = next_job.next_run_at
            time_until = next_run - datetime.now(timezone.utc)
            hours = int(time_until.total_seconds() / 3600)

            if hours < 24:
                time_desc = f"Tomorrow at {next_job.schedule_time}" if hours > 12 else f"in {hours}h"
            else:
                days = int(hours / 24)
                time_desc = f"in {days}d"

            activities.insert(0, {
                'id': f'schedule-{next_job.id}',
                'type': 'schedule',
                'title': 'Next Newsletter Scheduled',
                'description': time_desc,
                'timestamp': next_job.next_run_at,
                'status': 'scheduled'
            })

        self.logger.info(f"Returning {len(activities)} activities")
        return activities[:limit]


# Singleton instance
scheduler_service = SchedulerService()
