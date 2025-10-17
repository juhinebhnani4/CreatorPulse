"""
Daily scheduler for automated newsletter delivery.
"""

import logging
from datetime import datetime, time
from typing import Callable, Optional, Dict, Any, List
import threading
import time as time_module

try:
    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.triggers.cron import CronTrigger
    from apscheduler.executors.pool import ThreadPoolExecutor
    from apscheduler.jobstores.memory import MemoryJobStore
except ImportError:
    BackgroundScheduler = None
    CronTrigger = None
    ThreadPoolExecutor = None
    MemoryJobStore = None

from ..config.settings import SchedulerConfig


class DailyScheduler:
    """
    Daily scheduler for automated newsletter delivery.
    
    Uses APScheduler to schedule daily newsletter generation and delivery.
    
    Example:
        scheduler = DailyScheduler(config=scheduler_config)
        scheduler.schedule_newsletter_job(newsletter_callback, "08:00", "UTC")
        scheduler.start()
    """
    
    def __init__(self, config: Optional[SchedulerConfig] = None):
        """
        Initialize the daily scheduler.
        
        Args:
            config: Scheduler configuration
        """
        self.config = config or SchedulerConfig()
        self.logger = self._setup_logger()
        
        if not BackgroundScheduler:
            raise ImportError("APScheduler package is required. Install with: pip install apscheduler")
        
        # Initialize scheduler
        self.scheduler = None
        self._initialize_scheduler()
        
        # Job tracking
        self.jobs: Dict[str, Any] = {}
        self.job_callbacks: Dict[str, Callable] = {}
    
    def _setup_logger(self) -> logging.Logger:
        """Set up logger for the scheduler."""
        logger = logging.getLogger(f"{self.__class__.__name__}")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def _initialize_scheduler(self):
        """Initialize the APScheduler instance."""
        jobstores = {
            'default': MemoryJobStore()
        }
        
        executors = {
            'default': ThreadPoolExecutor(max_workers=3)
        }
        
        job_defaults = {
            'coalesce': True,
            'max_instances': 1,
            'misfire_grace_time': 300  # 5 minutes
        }
        
        self.scheduler = BackgroundScheduler(
            jobstores=jobstores,
            executors=executors,
            job_defaults=job_defaults,
            timezone=self.config.timezone
        )
    
    def schedule_newsletter_job(
        self,
        callback: Callable,
        job_id: str = "daily_newsletter",
        schedule_time: Optional[str] = None,
        timezone: Optional[str] = None
    ) -> bool:
        """
        Schedule a daily newsletter job.
        
        Args:
            callback: Function to call when job runs
            job_id: Unique identifier for the job
            schedule_time: Time to run (HH:MM format, defaults to config)
            timezone: Timezone (defaults to config)
            
        Returns:
            True if scheduled successfully, False otherwise
        """
        if not self.config.enabled:
            self.logger.warning("Scheduler is disabled")
            return False
        
        schedule_time = schedule_time or self.config.time
        timezone = timezone or self.config.timezone
        
        try:
            # Parse time
            hour, minute = map(int, schedule_time.split(':'))
            
            # Create cron trigger
            trigger = CronTrigger(
                hour=hour,
                minute=minute,
                timezone=timezone
            )
            
            # Add job to scheduler
            job = self.scheduler.add_job(
                func=self._run_newsletter_job,
                trigger=trigger,
                id=job_id,
                name=f"Daily Newsletter - {schedule_time}",
                args=[job_id],
                replace_existing=True
            )
            
            # Store callback
            self.job_callbacks[job_id] = callback
            self.jobs[job_id] = job
            
            self.logger.info(f"Scheduled newsletter job '{job_id}' for {schedule_time} {timezone}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to schedule newsletter job: {e}")
            return False
    
    def _run_newsletter_job(self, job_id: str):
        """
        Internal method to run newsletter job with retry logic.
        
        Args:
            job_id: Job identifier
        """
        callback = self.job_callbacks.get(job_id)
        if not callback:
            self.logger.error(f"No callback found for job {job_id}")
            return
        
        retries = 0
        max_retries = self.config.max_retries
        
        while retries <= max_retries:
            try:
                self.logger.info(f"Running newsletter job {job_id} (attempt {retries + 1})")
                
                # Call the callback function
                result = callback()
                
                if result:
                    self.logger.info(f"Newsletter job {job_id} completed successfully")
                    return
                else:
                    self.logger.warning(f"Newsletter job {job_id} returned False")
                    
            except Exception as e:
                self.logger.error(f"Newsletter job {job_id} failed: {e}")
            
            retries += 1
            
            if retries <= max_retries:
                delay = self.config.retry_delay * retries
                self.logger.info(f"Retrying newsletter job {job_id} in {delay} seconds")
                time_module.sleep(delay)
        
        self.logger.error(f"Newsletter job {job_id} failed after {max_retries} retries")
    
    def start(self) -> bool:
        """
        Start the scheduler.
        
        Returns:
            True if started successfully, False otherwise
        """
        if not self.config.enabled:
            self.logger.warning("Scheduler is disabled")
            return False
        
        try:
            if not self.scheduler.running:
                self.scheduler.start()
                self.logger.info("Scheduler started successfully")
                return True
            else:
                self.logger.info("Scheduler is already running")
                return True
        except Exception as e:
            self.logger.error(f"Failed to start scheduler: {e}")
            return False
    
    def stop(self) -> bool:
        """
        Stop the scheduler.
        
        Returns:
            True if stopped successfully, False otherwise
        """
        try:
            if self.scheduler.running:
                self.scheduler.shutdown()
                self.logger.info("Scheduler stopped successfully")
                return True
            else:
                self.logger.info("Scheduler is not running")
                return True
        except Exception as e:
            self.logger.error(f"Failed to stop scheduler: {e}")
            return False
    
    def pause_job(self, job_id: str) -> bool:
        """
        Pause a specific job.
        
        Args:
            job_id: Job identifier
            
        Returns:
            True if paused successfully, False otherwise
        """
        try:
            if job_id in self.jobs:
                self.scheduler.pause_job(job_id)
                self.logger.info(f"Job {job_id} paused")
                return True
            else:
                self.logger.warning(f"Job {job_id} not found")
                return False
        except Exception as e:
            self.logger.error(f"Failed to pause job {job_id}: {e}")
            return False
    
    def resume_job(self, job_id: str) -> bool:
        """
        Resume a specific job.
        
        Args:
            job_id: Job identifier
            
        Returns:
            True if resumed successfully, False otherwise
        """
        try:
            if job_id in self.jobs:
                self.scheduler.resume_job(job_id)
                self.logger.info(f"Job {job_id} resumed")
                return True
            else:
                self.logger.warning(f"Job {job_id} not found")
                return False
        except Exception as e:
            self.logger.error(f"Failed to resume job {job_id}: {e}")
            return False
    
    def remove_job(self, job_id: str) -> bool:
        """
        Remove a specific job.
        
        Args:
            job_id: Job identifier
            
        Returns:
            True if removed successfully, False otherwise
        """
        try:
            if job_id in self.jobs:
                self.scheduler.remove_job(job_id)
                del self.jobs[job_id]
                if job_id in self.job_callbacks:
                    del self.job_callbacks[job_id]
                self.logger.info(f"Job {job_id} removed")
                return True
            else:
                self.logger.warning(f"Job {job_id} not found")
                return False
        except Exception as e:
            self.logger.error(f"Failed to remove job {job_id}: {e}")
            return False
    
    def run_job_now(self, job_id: str) -> bool:
        """
        Run a job immediately.
        
        Args:
            job_id: Job identifier
            
        Returns:
            True if started successfully, False otherwise
        """
        try:
            if job_id in self.jobs:
                self.scheduler.modify_job(job_id, next_run_time=datetime.now())
                self.logger.info(f"Job {job_id} scheduled to run now")
                return True
            else:
                self.logger.warning(f"Job {job_id} not found")
                return False
        except Exception as e:
            self.logger.error(f"Failed to run job {job_id} now: {e}")
            return False
    
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Get status of a specific job.
        
        Args:
            job_id: Job identifier
            
        Returns:
            Job status dictionary or None if not found
        """
        try:
            if job_id in self.jobs:
                job = self.jobs[job_id]
                return {
                    'id': job.id,
                    'name': job.name,
                    'next_run_time': job.next_run_time.isoformat() if job.next_run_time else None,
                    'trigger': str(job.trigger),
                    'active': job.next_run_time is not None
                }
            else:
                return None
        except Exception as e:
            self.logger.error(f"Failed to get job status for {job_id}: {e}")
            return None
    
    def get_all_jobs(self) -> List[Dict[str, Any]]:
        """
        Get status of all jobs.
        
        Returns:
            List of job status dictionaries
        """
        jobs = []
        for job_id in self.jobs.keys():
            status = self.get_job_status(job_id)
            if status:
                jobs.append(status)
        return jobs
    
    def get_scheduler_status(self) -> Dict[str, Any]:
        """
        Get the current status of the scheduler.
        
        Returns:
            Dictionary with scheduler status information
        """
        status = {
            'running': False,
            'jobs_count': 0,
            'jobs': [],
            'next_run': None,
            'last_run': None,
            'errors': []
        }
        
        if not self.scheduler:
            status['errors'].append("Scheduler not initialized")
            return status
        
        try:
            status['running'] = self.scheduler.running
            status['jobs_count'] = len(self.scheduler.get_jobs())
            
            # Get job details
            for job in self.scheduler.get_jobs():
                job_info = {
                    'id': job.id,
                    'name': job.name,
                    'next_run': job.next_run_time.isoformat() if job.next_run_time else None,
                    'trigger': str(job.trigger)
                }
                status['jobs'].append(job_info)
            
            # Find next run time
            if status['jobs']:
                next_runs = [job['next_run'] for job in status['jobs'] if job['next_run']]
                if next_runs:
                    status['next_run'] = min(next_runs)
            
        except Exception as e:
            status['errors'].append(f"Error getting scheduler status: {e}")
        
        return status
