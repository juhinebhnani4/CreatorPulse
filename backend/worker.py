"""
Background Worker for Scheduler Job Execution.

This worker:
- Monitors active scheduled jobs
- Executes jobs at scheduled times
- Updates execution records with results
- Handles errors and retries
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
import traceback

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger

from src.ai_newsletter.database.supabase_client import SupabaseManager
from backend.services.content_service import content_service
from backend.services.newsletter_service import newsletter_service
from backend.services.delivery_service import delivery_service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class NewsletterWorker:
    """Background worker for executing scheduled newsletter jobs."""

    def __init__(self):
        self.scheduler = AsyncIOScheduler(timezone='UTC')
        self.db = SupabaseManager()
        self.running_jobs: Dict[str, bool] = {}  # Track running executions

    async def start(self):
        """Start the worker and load all active jobs."""
        logger.info("=" * 70)
        logger.info("Newsletter Worker Starting...")
        logger.info("=" * 70)

        # Start scheduler
        self.scheduler.start()
        logger.info("APScheduler started")

        # Load all active jobs
        await self.load_jobs()

        # Schedule periodic job reload (every 5 minutes)
        self.scheduler.add_job(
            self.load_jobs,
            trigger='interval',
            minutes=5,
            id='reload_jobs',
            replace_existing=True
        )
        logger.info("Scheduled periodic job reload (every 5 minutes)")

        logger.info("=" * 70)
        logger.info("Worker is ready and monitoring scheduled jobs")
        logger.info("=" * 70)

    async def load_jobs(self):
        """Load all active jobs from database and schedule them."""
        logger.info("Loading active jobs from database...")

        try:
            # Get all active jobs across all workspaces (using service client)
            result = self.db.service_client.table('scheduler_jobs') \
                .select('*') \
                .eq('is_enabled', True) \
                .in_('status', ['active', 'running']) \
                .execute()

            jobs = result.data
            logger.info(f"Found {len(jobs)} active job(s)")

            # Schedule each job
            for job in jobs:
                await self.schedule_job(job)

        except Exception as e:
            logger.error(f"Failed to load jobs: {e}")
            logger.error(traceback.format_exc())

    async def schedule_job(self, job: Dict[str, Any]):
        """Schedule a job with APScheduler."""
        job_id = job['id']
        job_name = job['name']
        schedule_type = job['schedule_type']

        # Remove existing job if it exists
        if self.scheduler.get_job(job_id):
            self.scheduler.remove_job(job_id)

        try:
            # Create trigger based on schedule type
            trigger = self._create_trigger(job)

            # Add job to scheduler
            self.scheduler.add_job(
                self.execute_job,
                trigger=trigger,
                args=[job_id],
                id=job_id,
                name=job_name,
                replace_existing=True,
                max_instances=1  # Prevent concurrent executions
            )

            next_run = self.scheduler.get_job(job_id).next_run_time
            logger.info(f"Scheduled job: {job_name} (next run: {next_run})")

        except Exception as e:
            logger.error(f"Failed to schedule job {job_name}: {e}")

    def _create_trigger(self, job: Dict[str, Any]):
        """Create APScheduler trigger from job configuration."""
        schedule_type = job['schedule_type']
        schedule_time = job['schedule_time']  # HH:MM:SS format
        timezone = job['timezone']

        # Parse time
        hour, minute = schedule_time.split(':')[:2]

        if schedule_type == 'daily':
            # Run every day at specified time
            return CronTrigger(
                hour=int(hour),
                minute=int(minute),
                timezone=timezone
            )

        elif schedule_type == 'weekly':
            # Run on specific days of week
            schedule_days = job.get('schedule_days', [])
            if not schedule_days:
                schedule_days = ['monday']

            # Convert day names to cron format
            day_map = {
                'monday': 'mon',
                'tuesday': 'tue',
                'wednesday': 'wed',
                'thursday': 'thu',
                'friday': 'fri',
                'saturday': 'sat',
                'sunday': 'sun'
            }
            days = ','.join([day_map[d.lower()] for d in schedule_days])

            return CronTrigger(
                day_of_week=days,
                hour=int(hour),
                minute=int(minute),
                timezone=timezone
            )

        elif schedule_type == 'cron':
            # Use custom cron expression
            cron_expr = job.get('cron_expression', '0 9 * * *')
            # Parse cron: minute hour day month day_of_week
            parts = cron_expr.split()
            return CronTrigger(
                minute=parts[0] if len(parts) > 0 else '0',
                hour=parts[1] if len(parts) > 1 else '9',
                day=parts[2] if len(parts) > 2 else '*',
                month=parts[3] if len(parts) > 3 else '*',
                day_of_week=parts[4] if len(parts) > 4 else '*',
                timezone=timezone
            )

        else:
            # Default: daily at specified time
            return CronTrigger(
                hour=int(hour),
                minute=int(minute),
                timezone=timezone
            )

    async def execute_job(self, job_id: str):
        """Execute a scheduled job."""
        # Prevent concurrent executions
        if self.running_jobs.get(job_id):
            logger.warning(f"Job {job_id} is already running, skipping")
            return

        self.running_jobs[job_id] = True
        execution_id = None

        try:
            # Get job details
            job = self.db.get_scheduler_job(job_id)
            if not job:
                logger.error(f"Job {job_id} not found")
                return

            logger.info(f"Executing job: {job['name']} ({job_id})")

            # Create execution record
            execution_data = {
                'job_id': job_id,
                'workspace_id': job['workspace_id'],
                'status': 'running',
                'actions_performed': [],
                'started_at': datetime.now(timezone.utc).isoformat()
            }
            execution = self.db.create_scheduler_execution(execution_data)
            execution_id = execution['id']

            # Update job status
            self.db.update_scheduler_job(job_id, {
                'status': 'running',
                'last_run_at': datetime.now(timezone.utc).isoformat()
            })

            # Execute actions
            actions = job.get('actions', [])
            config = job.get('config', {})
            workspace_id = job['workspace_id']

            results = {
                'scrape_result': None,
                'generate_result': None,
                'send_result': None
            }
            actions_performed = []

            # Action 1: Scrape content
            if 'scrape' in actions:
                logger.info(f"  [1/3] Scraping content...")
                scrape_result = await self._scrape_content(workspace_id, config)
                results['scrape_result'] = scrape_result
                actions_performed.append('scrape')
                logger.info(f"  Scraped {scrape_result.get('items_count', 0)} items")

            # Action 2: Generate newsletter
            newsletter_id = None
            if 'generate' in actions:
                logger.info(f"  [2/3] Generating newsletter...")
                generate_result = await self._generate_newsletter(workspace_id, config)
                results['generate_result'] = generate_result
                actions_performed.append('generate')
                newsletter_id = generate_result.get('newsletter_id')
                logger.info(f"  Generated newsletter: {newsletter_id}")

            # Action 3: Send newsletter
            if 'send' in actions and newsletter_id:
                test_mode = config.get('test_mode', False)
                logger.info(f"  [3/3] Sending newsletter (test_mode: {test_mode})...")
                send_result = await self._send_newsletter(
                    workspace_id,
                    newsletter_id,
                    test_mode
                )
                results['send_result'] = send_result
                actions_performed.append('send')
                logger.info(f"  Sent to {send_result.get('recipients_count', 0)} recipients")

            # Calculate duration
            completed_at = datetime.now(timezone.utc)
            started_at = datetime.fromisoformat(execution['started_at'].replace('Z', '+00:00'))
            duration = (completed_at - started_at).total_seconds()

            # Update execution record - SUCCESS
            self.db.update_scheduler_execution(execution_id, {
                'status': 'completed',
                'completed_at': completed_at.isoformat(),
                'duration_seconds': duration,
                'actions_performed': actions_performed,
                'scrape_result': results['scrape_result'],
                'generate_result': results['generate_result'],
                'send_result': results['send_result']
            })

            # Update job statistics
            self.db.update_scheduler_job(job_id, {
                'status': 'active',
                'last_run_status': 'completed',
                'total_runs': job.get('total_runs', 0) + 1,
                'successful_runs': job.get('successful_runs', 0) + 1
            })

            logger.info(f"Job completed successfully in {duration:.2f}s")

        except Exception as e:
            error_msg = str(e)
            error_trace = traceback.format_exc()
            logger.error(f"Job execution failed: {error_msg}")
            logger.error(error_trace)

            # Update execution record - FAILED
            if execution_id:
                completed_at = datetime.now(timezone.utc)
                started_at = datetime.fromisoformat(execution['started_at'].replace('Z', '+00:00'))
                duration = (completed_at - started_at).total_seconds()

                self.db.update_scheduler_execution(execution_id, {
                    'status': 'failed',
                    'completed_at': completed_at.isoformat(),
                    'duration_seconds': duration,
                    'error_message': error_msg,
                    'error_details': error_trace
                })

            # Update job statistics
            try:
                job = self.db.get_scheduler_job(job_id)
                if job:
                    self.db.update_scheduler_job(job_id, {
                        'status': 'failed',
                        'last_run_status': 'failed',
                        'last_error': error_msg,
                        'total_runs': job.get('total_runs', 0) + 1,
                        'failed_runs': job.get('failed_runs', 0) + 1
                    })
            except:
                pass

        finally:
            self.running_jobs[job_id] = False

    async def _scrape_content(self, workspace_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Scrape content for newsletter."""
        try:
            # Get workspace config
            workspace_config = self.db.get_workspace_config(workspace_id)

            # Extract scraping parameters from config
            days_back = config.get('days_back', 1)
            max_items = config.get('max_items', 10)
            sources = config.get('sources', ['reddit', 'rss'])

            # Scrape content using content service
            items = await content_service.scrape_all_sources(
                workspace_id=workspace_id,
                days_back=days_back,
                max_items=max_items
            )

            return {
                'items_count': len(items),
                'sources': sources,
                'days_back': days_back
            }

        except Exception as e:
            logger.error(f"Scraping failed: {e}")
            raise

    async def _generate_newsletter(self, workspace_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate newsletter from scraped content."""
        try:
            # Get recent content
            days_back = config.get('days_back', 1)
            max_items = config.get('max_items', 10)

            # Generate newsletter using newsletter service
            newsletter = await newsletter_service.generate_newsletter(
                workspace_id=workspace_id,
                days_back=days_back,
                max_items=max_items
            )

            return {
                'newsletter_id': newsletter['id'],
                'items_count': len(newsletter.get('items', []))
            }

        except Exception as e:
            logger.error(f"Newsletter generation failed: {e}")
            raise

    async def _send_newsletter(
        self,
        workspace_id: str,
        newsletter_id: str,
        test_mode: bool = False
    ) -> Dict[str, Any]:
        """Send newsletter to subscribers."""
        try:
            if test_mode:
                logger.info("Test mode enabled - skipping email sending")
                return {
                    'recipients_count': 0,
                    'test_mode': True,
                    'message': 'Test mode - no emails sent'
                }

            # Send newsletter using delivery service
            result = await delivery_service.send_newsletter(
                workspace_id=workspace_id,
                newsletter_id=newsletter_id
            )

            return {
                'recipients_count': result.get('total_recipients', 0),
                'sent_count': result.get('sent_count', 0),
                'failed_count': result.get('failed_count', 0)
            }

        except Exception as e:
            logger.error(f"Newsletter sending failed: {e}")
            raise

    async def stop(self):
        """Stop the worker gracefully."""
        logger.info("Stopping worker...")
        self.scheduler.shutdown(wait=True)
        logger.info("Worker stopped")

    async def run(self):
        """Run the worker indefinitely."""
        await self.start()

        try:
            # Keep running
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("Received shutdown signal")
        finally:
            await self.stop()


async def main():
    """Main entry point."""
    worker = NewsletterWorker()
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
