# Sprint 4B: Scheduler Backend - IN PROGRESS

## Overview
Implementing automated scheduling for scraping, generating, and sending newsletters at scheduled intervals.

---

## Progress Status

### ✅ Completed (40%)
- [x] Database migration (`005_create_scheduler_tables.sql`)
- [x] Pydantic models (`backend/models/scheduler.py`)

### 🔄 In Progress (0%)
- [ ] Scheduler service
- [ ] Background worker
- [ ] API endpoints
- [ ] Integration with existing services

### ⏳ Pending (60%)
- [ ] Testing
- [ ] Documentation

---

## What Was Built So Far

### 1. Database Schema (`005_create_scheduler_tables.sql`)

**Tables Created:**

#### `scheduler_jobs`
Stores scheduled job definitions with:
- **Schedule Configuration:** daily, weekly, custom, or cron
- **Actions:** Array of actions to perform (scrape, generate, send)
- **Configuration:** JSON config for job-specific settings
- **Status Tracking:** active, paused, disabled, failed
- **Statistics:** total_runs, successful_runs, failed_runs
- **Smart Triggers:** Automatically calculates `next_run_at` based on schedule

**Key Features:**
- Timezone-aware scheduling
- Flexible schedule types (daily at 8 AM, weekly on Mon/Wed/Fri, cron expressions)
- RLS policies for multi-workspace isolation
- Automatic next_run_at calculation via PostgreSQL triggers

#### `scheduler_executions`
Tracks execution history with:
- **Execution Details:** started_at, completed_at, duration
- **Action Results:** Separate JSONB columns for scrape/generate/send results
- **Error Tracking:** error_message, error_details
- **Logs:** Array of timestamped log messages

**Key Features:**
- Detailed result tracking for each action
- Performance metrics (duration)
- Complete audit trail

**PostgreSQL Functions:**
- `calculate_next_run_time()` - Smart scheduling logic
- `update_scheduler_job_next_run()` - Trigger function

### 2. Pydantic Models (`backend/models/scheduler.py`)

**Created Models:**
- `SchedulerJobCreate` - Create new scheduled job
- `SchedulerJobUpdate` - Update existing job
- `SchedulerJobResponse` - Job data with full details
- `SchedulerJobListResponse` - List of jobs
- `SchedulerExecutionResponse` - Execution details
- `SchedulerExecutionListResponse` - List of executions
- `SchedulerExecutionStats` - Execution statistics
- `RunJobNowRequest` - Trigger immediate execution
- `RunJobNowResponse` - Immediate execution response

**Example Job Configuration:**
```json
{
  "workspace_id": "uuid",
  "name": "Daily AI Newsletter",
  "schedule_type": "daily",
  "schedule_time": "08:00",
  "timezone": "America/New_York",
  "actions": ["scrape", "generate", "send"],
  "config": {
    "max_items": 15,
    "days_back": 1,
    "sources": ["reddit", "rss"],
    "test_mode": false
  }
}
```

---

## Implementation Remaining

### 3. Scheduler Service (`backend/services/scheduler_service.py`)

**Service Class:** `SchedulerService`

**Methods to Implement:**

```python
class SchedulerService:
    def __init__(self):
        self._db = None  # Lazy-load SupabaseManager

    async def create_job(self, user_id: str, request: SchedulerJobCreate) -> Dict:
        """Create a new scheduled job."""
        # 1. Validate workspace access
        # 2. Insert job into scheduler_jobs table
        # 3. Return created job with calculated next_run_at

    async def list_jobs(self, user_id: str, workspace_id: str) -> List[Dict]:
        """List all jobs for a workspace."""
        # 1. Query scheduler_jobs filtered by workspace_id
        # 2. RLS ensures user can only see their workspaces
        # 3. Return list of jobs

    async def get_job(self, user_id: str, job_id: str) -> Dict:
        """Get job details."""
        # 1. Query scheduler_jobs by ID
        # 2. Check workspace access
        # 3. Return job details

    async def update_job(self, user_id: str, job_id: str, request: SchedulerJobUpdate) -> Dict:
        """Update existing job."""
        # 1. Validate ownership/permissions
        # 2. Update job fields
        # 3. Trigger recalculates next_run_at
        # 4. Return updated job

    async def delete_job(self, user_id: str, job_id: str) -> bool:
        """Delete a job."""
        # 1. Validate ownership
        # 2. Delete job (cascade deletes executions)
        # 3. Return success

    async def pause_job(self, user_id: str, job_id: str) -> Dict:
        """Pause a job."""
        # 1. Update status to 'paused'
        # 2. Set is_enabled = false
        # 3. Return updated job

    async def resume_job(self, user_id: str, job_id: str) -> Dict:
        """Resume a paused job."""
        # 1. Update status to 'active'
        # 2. Set is_enabled = true
        # 3. Recalculate next_run_at
        # 4. Return updated job

    async def trigger_job_now(self, user_id: str, job_id: str, test_mode: bool = False) -> Dict:
        """Trigger immediate execution."""
        # 1. Get job details
        # 2. Create execution record (status='running')
        # 3. Queue job for background worker
        # 4. Return execution_id

    async def get_execution_history(self, user_id: str, job_id: str, limit: int = 50) -> List[Dict]:
        """Get execution history for a job."""
        # 1. Query scheduler_executions
        # 2. Order by started_at DESC
        # 3. Limit results
        # 4. Return list

    async def get_execution_stats(self, user_id: str, job_id: str) -> Dict:
        """Get execution statistics."""
        # 1. Query scheduler_executions
        # 2. Calculate success rate, avg duration
        # 3. Return stats
```

**Integration:** Uses `SupabaseManager` for database operations.

---

### 4. Background Worker (`backend/worker.py`)

**Purpose:** Separate process that executes scheduled jobs.

**Core Components:**

```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import asyncio

class NewsletterWorker:
    """Background worker for executing scheduled jobs."""

    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.db = SupabaseManager()

    async def start(self):
        """Start the background worker."""
        # 1. Load all active jobs from database
        # 2. Schedule each job with APScheduler
        # 3. Start scheduler
        # 4. Monitor for new/updated jobs

    async def execute_job(self, job_id: str):
        """Execute a scheduled job."""
        # 1. Load job details
        # 2. Create execution record (status='running')
        # 3. Execute actions in order:
        #    - scrape: Use ContentService
        #    - generate: Use NewsletterGenerator
        #    - send: Use DeliveryService
        # 4. Update execution record with results
        # 5. Update job.last_run_at, statistics

    async def _execute_scrape(self, job: Dict, execution_id: str) -> Dict:
        """Execute scrape action."""
        # Use existing ContentService
        # Return: {items_scraped: 10, sources: ['reddit'], ...}

    async def _execute_generate(self, job: Dict, execution_id: str) -> Dict:
        """Execute generate action."""
        # Use existing NewsletterGenerator
        # Return: {newsletter_id: 'uuid', items_used: 8, ...}

    async def _execute_send(self, job: Dict, execution_id: str, newsletter_id: str) -> Dict:
        """Execute send action."""
        # Use existing DeliveryService
        # Return: {delivery_id: 'uuid', sent_count: 100, ...}

    def stop(self):
        """Stop the background worker."""
        self.scheduler.shutdown()
```

**Running the Worker:**
```bash
# Separate process from FastAPI
python backend/worker.py
```

**Dependencies:**
```bash
pip install apscheduler
```

---

### 5. API Endpoints (`backend/api/v1/scheduler.py`)

**Router:** `router = APIRouter()`

**Endpoints to Implement:**

```python
# Create job
@router.post("", response_model=APIResponse, status_code=status.HTTP_201_CREATED)
async def create_scheduler_job(
    request: SchedulerJobCreate,
    user_id: str = Depends(get_current_user)
):
    """Create a new scheduled job."""

# List jobs
@router.get("/workspaces/{workspace_id}", response_model=APIResponse)
async def list_scheduler_jobs(
    workspace_id: str,
    user_id: str = Depends(get_current_user)
):
    """List all scheduled jobs for a workspace."""

# Get job
@router.get("/{job_id}", response_model=APIResponse)
async def get_scheduler_job(
    job_id: str,
    user_id: str = Depends(get_current_user)
):
    """Get scheduler job details."""

# Update job
@router.put("/{job_id}", response_model=APIResponse)
async def update_scheduler_job(
    job_id: str,
    request: SchedulerJobUpdate,
    user_id: str = Depends(get_current_user)
):
    """Update an existing scheduled job."""

# Delete job
@router.delete("/{job_id}", response_model=APIResponse)
async def delete_scheduler_job(
    job_id: str,
    user_id: str = Depends(get_current_user)
):
    """Delete a scheduled job."""

# Pause job
@router.post("/{job_id}/pause", response_model=APIResponse)
async def pause_scheduler_job(
    job_id: str,
    user_id: str = Depends(get_current_user)
):
    """Pause a scheduled job."""

# Resume job
@router.post("/{job_id}/resume", response_model=APIResponse)
async def resume_scheduler_job(
    job_id: str,
    user_id: str = Depends(get_current_user)
):
    """Resume a paused job."""

# Run job now
@router.post("/{job_id}/run-now", response_model=APIResponse)
async def run_job_now(
    job_id: str,
    request: RunJobNowRequest,
    user_id: str = Depends(get_current_user)
):
    """Trigger immediate job execution."""

# Get execution history
@router.get("/{job_id}/history", response_model=APIResponse)
async def get_job_execution_history(
    job_id: str,
    limit: int = 50,
    user_id: str = Depends(get_current_user)
):
    """Get execution history for a job."""

# Get execution stats
@router.get("/{job_id}/stats", response_model=APIResponse)
async def get_job_execution_stats(
    job_id: str,
    user_id: str = Depends(get_current_user)
):
    """Get execution statistics for a job."""
```

**Total Endpoints:** 10

---

### 6. Integration Points

**Update `backend/main.py`:**
```python
from backend.api.v1 import auth, workspaces, content, newsletters, subscribers, delivery, scheduler

# Register scheduler router
app.include_router(
    scheduler.router,
    prefix=f"{settings.api_v1_prefix}/scheduler",
    tags=["Scheduler"]
)
```

**Update `src/ai_newsletter/database/supabase_client.py`:**

Add scheduler methods:
```python
def create_scheduler_job(self, job_data: Dict) -> Dict:
    """Create a scheduled job."""

def get_scheduler_job(self, job_id: str) -> Dict:
    """Get job by ID."""

def list_scheduler_jobs(self, workspace_id: str) -> List[Dict]:
    """List jobs for workspace."""

def update_scheduler_job(self, job_id: str, updates: Dict) -> Dict:
    """Update job."""

def delete_scheduler_job(self, job_id: str) -> bool:
    """Delete job."""

def create_scheduler_execution(self, execution_data: Dict) -> Dict:
    """Create execution record."""

def update_scheduler_execution(self, execution_id: str, updates: Dict) -> Dict:
    """Update execution record."""

def get_scheduler_executions(self, job_id: str, limit: int = 50) -> List[Dict]:
    """Get execution history."""
```

---

## Testing Plan

### 1. Database Migration
```bash
# Run migration in Supabase SQL Editor
# Copy contents of 005_create_scheduler_tables.sql
# Verify tables created with: \dt scheduler_*
```

### 2. API Testing (Swagger UI)

**Step 1:** Create a job
```bash
POST /api/v1/scheduler
{
  "workspace_id": "uuid",
  "name": "Test Daily Job",
  "schedule_type": "daily",
  "schedule_time": "09:00",
  "actions": ["scrape", "generate", "send"]
}
```

**Step 2:** List jobs
```bash
GET /api/v1/scheduler/workspaces/{workspace_id}
```

**Step 3:** Trigger immediate execution
```bash
POST /api/v1/scheduler/{job_id}/run-now
{
  "test_mode": true
}
```

**Step 4:** Check execution history
```bash
GET /api/v1/scheduler/{job_id}/history
```

### 3. Background Worker Testing
```bash
# Start worker in separate terminal
python backend/worker.py

# Check logs for:
# - Job scheduling
# - Execution start/complete
# - Error handling
```

---

## Dependencies

**New Packages Required:**
```bash
pip install apscheduler
```

Add to `requirements.txt`:
```
apscheduler>=3.10.0  # Background job scheduling
```

---

## File Structure

```
backend/
├── migrations/
│   └── 005_create_scheduler_tables.sql  ✅ DONE
├── models/
│   └── scheduler.py  ✅ DONE
├── services/
│   └── scheduler_service.py  ⏳ TODO
├── api/
│   └── v1/
│       └── scheduler.py  ⏳ TODO
├── worker.py  ⏳ TODO
└── main.py  ⏳ UPDATE NEEDED
```

---

## Timeline Estimate

| Task | Estimated Time | Status |
|------|---------------|--------|
| Database migration | 30 min | ✅ Done |
| Pydantic models | 30 min | ✅ Done |
| Scheduler service | 1 hour | ⏳ Pending |
| Background worker | 1.5 hours | ⏳ Pending |
| API endpoints | 1 hour | ⏳ Pending |
| Supabase client methods | 30 min | ⏳ Pending |
| Testing | 1 hour | ⏳ Pending |
| **Total** | **~6 hours** | **33% Complete** |

---

## Next Steps

1. ✅ Run database migration in Supabase
2. Implement `scheduler_service.py`
3. Implement `backend/worker.py`
4. Implement `scheduler.py` API endpoints
5. Update `supabase_client.py` with scheduler methods
6. Update `main.py` to register router
7. Test all endpoints in Swagger UI
8. Test background worker execution
9. Create Sprint 4B completion document

---

## Use Cases

### Use Case 1: Daily Newsletter
```json
{
  "name": "Daily AI Digest",
  "schedule_type": "daily",
  "schedule_time": "08:00",
  "timezone": "America/New_York",
  "actions": ["scrape", "generate", "send"],
  "config": {
    "max_items": 10,
    "days_back": 1,
    "sources": ["reddit", "rss"]
  }
}
```
**Result:** Every day at 8 AM EST, scrape yesterday's content, generate newsletter, send to subscribers.

### Use Case 2: Weekly Roundup
```json
{
  "name": "Weekly AI Roundup",
  "schedule_type": "weekly",
  "schedule_days": ["monday"],
  "schedule_time": "10:00",
  "timezone": "UTC",
  "actions": ["scrape", "generate", "send"],
  "config": {
    "max_items": 20,
    "days_back": 7,
    "tone": "professional"
  }
}
```
**Result:** Every Monday at 10 AM UTC, scrape last week's content, generate roundup, send.

### Use Case 3: Test Mode
```json
{
  "name": "Test Newsletter",
  "schedule_type": "daily",
  "schedule_time": "12:00",
  "actions": ["scrape", "generate"],
  "config": {
    "max_items": 5,
    "test_mode": true
  }
}
```
**Result:** Generate but don't send (test mode).

---

## Success Criteria

- [x] Database tables created with RLS
- [x] Pydantic models with examples
- [ ] All 10 API endpoints working
- [ ] Background worker executes jobs
- [ ] Jobs can be paused/resumed
- [ ] Execution history tracked
- [ ] Integration with existing services (scrape, generate, send)
- [ ] Test mode works (generate without sending)
- [ ] Timezone-aware scheduling
- [ ] Error handling and retry logic

---

**Status:** 33% Complete (2/6 tasks done)
**Next Action:** Implement `scheduler_service.py`
**Estimated Completion:** 4-5 more hours of work
