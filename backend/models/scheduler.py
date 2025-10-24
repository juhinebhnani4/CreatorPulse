"""
Pydantic models for Scheduler API.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, time


# ========================================
# SCHEDULER JOB MODELS
# ========================================

class SchedulerJobCreate(BaseModel):
    """Request model for creating a scheduled job."""
    workspace_id: str = Field(..., description="Workspace ID (UUID format)")
    name: str = Field(..., min_length=1, max_length=200, description="Job name")
    # Note: description and config fields removed in migration 014 (unused)

    # Schedule configuration
    schedule_type: str = Field(..., description="Schedule type: daily, weekly, custom, cron")
    schedule_time: str = Field(default="08:00", description="Time of day (HH:MM format)")
    schedule_days: Optional[List[str]] = Field(None, description="Days for weekly schedule (monday, tuesday, etc.)")
    cron_expression: Optional[str] = Field(None, description="Cron expression for advanced scheduling")
    timezone: str = Field(default="UTC", description="Timezone (e.g., America/New_York, UTC)")

    # Actions
    actions: List[str] = Field(default=["scrape", "generate", "send"], description="Actions to perform: scrape, generate, send")

    # Status
    is_enabled: bool = Field(default=True, description="Whether job is enabled")

    class Config:
        json_schema_extra = {
            "example": {
                "workspace_id": "1839de43-ebf1-4cc0-bcb4-3f7a2cb37a7b",
                "name": "Daily AI Newsletter",
                "schedule_type": "cron",
                "cron_expression": "0 */6 * * *",  # Every 6 hours (12 AM, 6 AM, 12 PM, 6 PM UTC)
                "timezone": "UTC",
                "actions": ["scrape", "generate", "send"],
                "is_enabled": True
            },
            "note": "For content scraping, 6-hour intervals (4x daily) are recommended. Most sources (Reddit, YouTube, RSS feeds) don't update frequently enough for shorter intervals. This balances freshness with API efficiency and reduces duplicate content. For real-time news, consider 1-2 hour intervals."
        }


class SchedulerJobUpdate(BaseModel):
    """Request model for updating a scheduled job."""
    name: Optional[str] = Field(None, min_length=1, max_length=200, description="Job name")
    # Note: description and config fields removed in migration 014 (unused)

    # Schedule configuration
    schedule_type: Optional[str] = Field(None, description="Schedule type")
    schedule_time: Optional[str] = Field(None, description="Time of day (HH:MM format)")
    schedule_days: Optional[List[str]] = Field(None, description="Days for weekly schedule")
    cron_expression: Optional[str] = Field(None, description="Cron expression")
    timezone: Optional[str] = Field(None, description="Timezone")

    # Actions
    actions: Optional[List[str]] = Field(None, description="Actions to perform")

    # Status
    status: Optional[str] = Field(None, description="Job status: active, paused, disabled")
    is_enabled: Optional[bool] = Field(None, description="Whether job is enabled")

    class Config:
        json_schema_extra = {
            "example": {
                "schedule_time": "09:00",
                "is_enabled": True
            }
        }


class SchedulerJobResponse(BaseModel):
    """Response model for a scheduled job."""
    id: str
    workspace_id: str
    name: str
    # Note: description, config, and last_error fields removed in migration 014 (unused)

    # Schedule
    schedule_type: str
    schedule_time: str
    schedule_days: Optional[List[str]]
    cron_expression: Optional[str]
    timezone: str

    # Actions
    actions: List[str]

    # Status
    status: str
    is_enabled: bool

    # Execution tracking
    last_run_at: Optional[datetime]
    last_run_status: Optional[str]
    next_run_at: Optional[datetime]

    # Statistics
    total_runs: int
    successful_runs: int
    failed_runs: int

    # Metadata
    created_by: str
    created_at: datetime
    updated_at: datetime


class SchedulerJobListResponse(BaseModel):
    """Response model for list of scheduled jobs."""
    jobs: List[SchedulerJobResponse]
    count: int
    workspace_id: str


# ========================================
# SCHEDULER EXECUTION MODELS
# ========================================

class SchedulerExecutionResponse(BaseModel):
    """Response model for a job execution."""
    id: str
    job_id: str
    workspace_id: str

    # Execution details
    started_at: datetime
    completed_at: Optional[datetime]
    duration_seconds: Optional[int]

    # Status
    status: str

    # Results
    actions_performed: List[str]
    scrape_result: Optional[Dict[str, Any]]
    generate_result: Optional[Dict[str, Any]]
    send_result: Optional[Dict[str, Any]]

    # Error tracking
    error_message: Optional[str]
    # Note: error_details and execution_log fields removed in migration 014 (unused)

    # Metadata
    created_at: datetime


class SchedulerExecutionListResponse(BaseModel):
    """Response model for list of executions."""
    executions: List[SchedulerExecutionResponse]
    count: int
    job_id: str


class SchedulerExecutionStats(BaseModel):
    """Statistics for job executions."""
    total_executions: int
    successful: int
    failed: int
    partial: int
    success_rate: float
    avg_duration_seconds: Optional[float]
    last_execution_at: Optional[datetime]


# ========================================
# SCHEDULER ACTION MODELS
# ========================================

class RunJobNowRequest(BaseModel):
    """Request to trigger job execution immediately."""
    test_mode: bool = Field(default=False, description="Run in test mode (don't send emails)")

    class Config:
        json_schema_extra = {
            "example": {
                "test_mode": True
            }
        }


class RunJobNowResponse(BaseModel):
    """Response after triggering immediate job execution."""
    execution_id: str
    job_id: str
    status: str
    message: str
