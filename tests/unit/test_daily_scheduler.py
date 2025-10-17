"""
Unit tests for daily scheduler.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import pytz

from ai_newsletter.scheduler.daily_scheduler import DailyScheduler


class TestDailyScheduler:
    """Test cases for DailyScheduler."""
    
    def test_init_with_config(self):
        """Test DailyScheduler initialization with config."""
        config = Mock()
        config.enabled = True
        config.time = "08:00"
        config.timezone = "UTC"
        config.max_retries = 3
        config.retry_delay = 300
        
        scheduler = DailyScheduler(config=config)
        
        assert scheduler.config == config
        assert scheduler.scheduler is not None
        assert scheduler._job_id == "newsletter_daily_job"
        assert scheduler._job_function is None
    
    def test_init_without_config(self):
        """Test DailyScheduler initialization without config."""
        with patch('ai_newsletter.scheduler.daily_scheduler.get_settings') as mock_settings:
            mock_settings.return_value.scheduler = Mock()
            mock_settings.return_value.scheduler.enabled = True
            mock_settings.return_value.scheduler.time = "08:00"
            mock_settings.return_value.scheduler.timezone = "UTC"
            mock_settings.return_value.scheduler.max_retries = 3
            mock_settings.return_value.scheduler.retry_delay = 300
            
            scheduler = DailyScheduler()
            
            assert scheduler.config == mock_settings.return_value.scheduler
    
    def test_schedule_newsletter_job_success(self):
        """Test successful newsletter job scheduling."""
        config = Mock()
        config.enabled = True
        config.time = "08:00"
        config.timezone = "UTC"
        config.max_retries = 3
        config.retry_delay = 300
        
        scheduler = DailyScheduler(config=config)
        
        def mock_job_function():
            return True
        
        result = scheduler.schedule_newsletter_job(mock_job_function, "09:00", "America/New_York")
        
        assert result == True
        assert scheduler._job_function == mock_job_function
        
        # Check if job was added to scheduler
        jobs = scheduler.scheduler.get_jobs()
        assert len(jobs) == 1
        assert jobs[0].id == "newsletter_daily_job"
        assert jobs[0].name == "Daily CreatorPulse Newsletter"
    
    def test_schedule_newsletter_job_disabled(self):
        """Test newsletter job scheduling when scheduler is disabled."""
        config = Mock()
        config.enabled = False
        config.time = "08:00"
        config.timezone = "UTC"
        config.max_retries = 3
        config.retry_delay = 300
        
        scheduler = DailyScheduler(config=config)
        
        def mock_job_function():
            return True
        
        result = scheduler.schedule_newsletter_job(mock_job_function)
        
        assert result == False
        assert scheduler._job_function is None
        
        # Check if no job was added to scheduler
        jobs = scheduler.scheduler.get_jobs()
        assert len(jobs) == 0
    
    def test_schedule_newsletter_job_invalid_time(self):
        """Test newsletter job scheduling with invalid time format."""
        config = Mock()
        config.enabled = True
        config.time = "08:00"
        config.timezone = "UTC"
        config.max_retries = 3
        config.retry_delay = 300
        
        scheduler = DailyScheduler(config=config)
        
        def mock_job_function():
            return True
        
        result = scheduler.schedule_newsletter_job(mock_job_function, "invalid_time")
        
        assert result == False
    
    def test_schedule_newsletter_job_invalid_timezone(self):
        """Test newsletter job scheduling with invalid timezone."""
        config = Mock()
        config.enabled = True
        config.time = "08:00"
        config.timezone = "UTC"
        config.max_retries = 3
        config.retry_delay = 300
        
        scheduler = DailyScheduler(config=config)
        
        def mock_job_function():
            return True
        
        result = scheduler.schedule_newsletter_job(mock_job_function, "08:00", "Invalid/Timezone")
        
        assert result == False
    
    def test_schedule_newsletter_job_replace_existing(self):
        """Test newsletter job scheduling when job already exists."""
        config = Mock()
        config.enabled = True
        config.time = "08:00"
        config.timezone = "UTC"
        config.max_retries = 3
        config.retry_delay = 300
        
        scheduler = DailyScheduler(config=config)
        
        def mock_job_function():
            return True
        
        # Schedule first job
        result1 = scheduler.schedule_newsletter_job(mock_job_function, "08:00")
        assert result1 == True
        
        # Schedule second job (should replace first)
        result2 = scheduler.schedule_newsletter_job(mock_job_function, "09:00")
        assert result2 == True
        
        # Check if only one job exists
        jobs = scheduler.scheduler.get_jobs()
        assert len(jobs) == 1
        assert jobs[0].id == "newsletter_daily_job"
    
    def test_run_job_with_retries_success(self):
        """Test running job with retries - success on first attempt."""
        config = Mock()
        config.enabled = True
        config.time = "08:00"
        config.timezone = "UTC"
        config.max_retries = 3
        config.retry_delay = 300
        
        scheduler = DailyScheduler(config=config)
        
        def mock_job_function():
            return True
        
        scheduler._job_function = mock_job_function
        
        scheduler._run_job_with_retries()
        
        # Should succeed on first attempt
        assert True  # No exception raised
    
    def test_run_job_with_retries_failure_then_success(self):
        """Test running job with retries - failure then success."""
        config = Mock()
        config.enabled = True
        config.time = "08:00"
        config.timezone = "UTC"
        config.max_retries = 3
        config.retry_delay = 300
        
        scheduler = DailyScheduler(config=config)
        
        call_count = 0
        def mock_job_function():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return False  # First attempt fails
            return True  # Second attempt succeeds
        
        scheduler._job_function = mock_job_function
        
        scheduler._run_job_with_retries()
        
        # Should succeed on second attempt
        assert call_count == 2
    
    def test_run_job_with_retries_all_failures(self):
        """Test running job with retries - all attempts fail."""
        config = Mock()
        config.enabled = True
        config.time = "08:00"
        config.timezone = "UTC"
        config.max_retries = 3
        config.retry_delay = 300
        
        scheduler = DailyScheduler(config=config)
        
        def mock_job_function():
            return False
        
        scheduler._job_function = mock_job_function
        
        scheduler._run_job_with_retries()
        
        # Should fail after max_retries attempts
        assert True  # No exception raised, but job failed
    
    def test_run_job_with_retries_exception(self):
        """Test running job with retries - exception raised."""
        config = Mock()
        config.enabled = True
        config.time = "08:00"
        config.timezone = "UTC"
        config.max_retries = 3
        config.retry_delay = 300
        
        scheduler = DailyScheduler(config=config)
        
        def mock_job_function():
            raise Exception("Job error")
        
        scheduler._job_function = mock_job_function
        
        scheduler._run_job_with_retries()
        
        # Should handle exception gracefully
        assert True  # No exception raised
    
    def test_start_scheduler(self):
        """Test starting the scheduler."""
        config = Mock()
        config.enabled = True
        config.time = "08:00"
        config.timezone = "UTC"
        config.max_retries = 3
        config.retry_delay = 300
        
        scheduler = DailyScheduler(config=config)
        
        with patch.object(scheduler.scheduler, 'start') as mock_start:
            scheduler.start()
            mock_start.assert_called_once()
    
    def test_start_scheduler_already_running(self):
        """Test starting the scheduler when already running."""
        config = Mock()
        config.enabled = True
        config.time = "08:00"
        config.timezone = "UTC"
        config.max_retries = 3
        config.retry_delay = 300
        
        scheduler = DailyScheduler(config=config)
        
        with patch.object(scheduler.scheduler, 'running', True):
            with patch.object(scheduler.scheduler, 'start') as mock_start:
                scheduler.start()
                mock_start.assert_not_called()
    
    def test_stop_scheduler(self):
        """Test stopping the scheduler."""
        config = Mock()
        config.enabled = True
        config.time = "08:00"
        config.timezone = "UTC"
        config.max_retries = 3
        config.retry_delay = 300
        
        scheduler = DailyScheduler(config=config)
        
        with patch.object(scheduler.scheduler, 'shutdown') as mock_shutdown:
            scheduler.stop()
            mock_shutdown.assert_called_once()
    
    def test_stop_scheduler_not_running(self):
        """Test stopping the scheduler when not running."""
        config = Mock()
        config.enabled = True
        config.time = "08:00"
        config.timezone = "UTC"
        config.max_retries = 3
        config.retry_delay = 300
        
        scheduler = DailyScheduler(config=config)
        
        with patch.object(scheduler.scheduler, 'running', False):
            with patch.object(scheduler.scheduler, 'shutdown') as mock_shutdown:
                scheduler.stop()
                mock_shutdown.assert_not_called()
    
    def test_get_scheduler_status(self):
        """Test getting scheduler status."""
        config = Mock()
        config.enabled = True
        config.time = "08:00"
        config.timezone = "UTC"
        config.max_retries = 3
        config.retry_delay = 300
        
        scheduler = DailyScheduler(config=config)
        
        # Mock job
        mock_job = Mock()
        mock_job.id = "newsletter_daily_job"
        mock_job.name = "Daily CreatorPulse Newsletter"
        mock_job.trigger = "cron[hour=8, minute=0]"
        mock_job.next_run_time = datetime.now()
        mock_job.pending = False
        
        with patch.object(scheduler.scheduler, 'get_jobs') as mock_get_jobs:
            mock_get_jobs.return_value = [mock_job]
            
            status = scheduler.get_scheduler_status()
            
            assert status['running'] == scheduler.scheduler.running
            assert status['job_count'] == 1
            assert len(status['jobs']) == 1
            assert status['jobs'][0]['id'] == "newsletter_daily_job"
            assert status['jobs'][0]['name'] == "Daily CreatorPulse Newsletter"
            assert status['jobs'][0]['trigger'] == "cron[hour=8, minute=0]"
            assert status['jobs'][0]['paused'] == False
            assert status['config'] == config