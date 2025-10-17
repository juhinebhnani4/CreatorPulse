-- Migration 005: Create Scheduler Tables
-- Purpose: Enable scheduled automation of scraping, generation, and delivery
-- Created: 2025-01-16

-- =====================================================
-- Table: scheduler_jobs
-- Purpose: Store scheduled job definitions
-- =====================================================

CREATE TABLE IF NOT EXISTS scheduler_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,

    -- Job identification
    name TEXT NOT NULL,
    description TEXT,

    -- Schedule configuration
    schedule_type TEXT NOT NULL CHECK (schedule_type IN ('daily', 'weekly', 'custom', 'cron')),
    schedule_time TIME NOT NULL DEFAULT '08:00:00',  -- Time of day to run
    schedule_days TEXT[] DEFAULT NULL,  -- For weekly: ['monday', 'wednesday', 'friday']
    cron_expression TEXT,  -- For advanced scheduling
    timezone TEXT NOT NULL DEFAULT 'UTC',

    -- Actions to perform (in order)
    actions TEXT[] NOT NULL DEFAULT ARRAY['scrape', 'generate', 'send'],  -- ['scrape', 'generate', 'send']

    -- Configuration
    config JSONB DEFAULT '{}',  -- Job-specific config (max_items, days_back, etc.)

    -- Status
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'paused', 'disabled', 'failed')),
    is_enabled BOOLEAN NOT NULL DEFAULT true,

    -- Execution tracking
    last_run_at TIMESTAMPTZ,
    last_run_status TEXT,  -- 'success', 'failed', 'partial'
    last_error TEXT,
    next_run_at TIMESTAMPTZ,  -- Calculated next execution time

    -- Statistics
    total_runs INTEGER NOT NULL DEFAULT 0,
    successful_runs INTEGER NOT NULL DEFAULT 0,
    failed_runs INTEGER NOT NULL DEFAULT 0,

    -- Metadata
    created_by UUID NOT NULL REFERENCES auth.users(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Constraints
    CONSTRAINT unique_job_name_per_workspace UNIQUE(workspace_id, name)
);

-- Index for faster queries
CREATE INDEX idx_scheduler_jobs_workspace ON scheduler_jobs(workspace_id);
CREATE INDEX idx_scheduler_jobs_status ON scheduler_jobs(status) WHERE is_enabled = true;
CREATE INDEX idx_scheduler_jobs_next_run ON scheduler_jobs(next_run_at) WHERE is_enabled = true AND status = 'active';

-- RLS Policies for scheduler_jobs
ALTER TABLE scheduler_jobs ENABLE ROW LEVEL SECURITY;

-- Users can view jobs in their workspaces
CREATE POLICY scheduler_jobs_select_policy ON scheduler_jobs
    FOR SELECT
    USING (
        workspace_id IN (
            SELECT workspace_id FROM user_workspaces
            WHERE user_id = auth.uid()
        )
    );

-- Users with editor/owner role can create jobs
CREATE POLICY scheduler_jobs_insert_policy ON scheduler_jobs
    FOR INSERT
    WITH CHECK (
        workspace_id IN (
            SELECT workspace_id FROM user_workspaces
            WHERE user_id = auth.uid()
            AND role IN ('owner', 'editor')
        )
    );

-- Users with editor/owner role can update jobs
CREATE POLICY scheduler_jobs_update_policy ON scheduler_jobs
    FOR UPDATE
    USING (
        workspace_id IN (
            SELECT workspace_id FROM user_workspaces
            WHERE user_id = auth.uid()
            AND role IN ('owner', 'editor')
        )
    );

-- Only owners can delete jobs
CREATE POLICY scheduler_jobs_delete_policy ON scheduler_jobs
    FOR DELETE
    USING (
        workspace_id IN (
            SELECT workspace_id FROM user_workspaces
            WHERE user_id = auth.uid()
            AND role = 'owner'
        )
    );

-- =====================================================
-- Table: scheduler_executions
-- Purpose: Track execution history for jobs
-- =====================================================

CREATE TABLE IF NOT EXISTS scheduler_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID NOT NULL REFERENCES scheduler_jobs(id) ON DELETE CASCADE,
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,

    -- Execution details
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    duration_seconds INTEGER,

    -- Status
    status TEXT NOT NULL DEFAULT 'running' CHECK (status IN ('running', 'success', 'failed', 'partial')),

    -- Results
    actions_performed TEXT[] DEFAULT ARRAY[]::TEXT[],  -- ['scrape', 'generate', 'send']

    -- Action-specific results
    scrape_result JSONB,  -- {items_scraped: 10, sources: ['reddit', 'rss'], ...}
    generate_result JSONB,  -- {newsletter_id: 'uuid', items_used: 8, ...}
    send_result JSONB,  -- {delivery_id: 'uuid', sent_count: 100, ...}

    -- Error tracking
    error_message TEXT,
    error_details JSONB,

    -- Logs
    execution_log TEXT[],  -- Array of log messages

    -- Metadata
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for faster queries
CREATE INDEX idx_scheduler_executions_job ON scheduler_executions(job_id);
CREATE INDEX idx_scheduler_executions_workspace ON scheduler_executions(workspace_id);
CREATE INDEX idx_scheduler_executions_status ON scheduler_executions(status);
CREATE INDEX idx_scheduler_executions_started_at ON scheduler_executions(started_at DESC);

-- RLS Policies for scheduler_executions
ALTER TABLE scheduler_executions ENABLE ROW LEVEL SECURITY;

-- Users can view execution history for jobs in their workspaces
CREATE POLICY scheduler_executions_select_policy ON scheduler_executions
    FOR SELECT
    USING (
        workspace_id IN (
            SELECT workspace_id FROM user_workspaces
            WHERE user_id = auth.uid()
        )
    );

-- Service role can insert executions (backend worker)
CREATE POLICY scheduler_executions_insert_policy ON scheduler_executions
    FOR INSERT
    WITH CHECK (true);  -- Service key bypasses RLS

-- Service role can update executions
CREATE POLICY scheduler_executions_update_policy ON scheduler_executions
    FOR UPDATE
    USING (true);  -- Service key bypasses RLS

-- =====================================================
-- Function: Update next_run_at automatically
-- =====================================================

CREATE OR REPLACE FUNCTION calculate_next_run_time(
    p_schedule_type TEXT,
    p_schedule_time TIME,
    p_schedule_days TEXT[],
    p_timezone TEXT,
    p_last_run_at TIMESTAMPTZ
) RETURNS TIMESTAMPTZ AS $$
DECLARE
    v_base_time TIMESTAMPTZ;
    v_next_run TIMESTAMPTZ;
    v_current_day TEXT;
    v_days_to_add INTEGER;
BEGIN
    -- Get current time in specified timezone
    v_base_time := COALESCE(p_last_run_at, NOW() AT TIME ZONE p_timezone);

    CASE p_schedule_type
        WHEN 'daily' THEN
            -- Run every day at specified time
            v_next_run := (DATE(v_base_time AT TIME ZONE p_timezone) + INTERVAL '1 day' + p_schedule_time) AT TIME ZONE p_timezone;

            -- If scheduled time hasn't passed today, use today
            IF p_last_run_at IS NULL AND (NOW() AT TIME ZONE p_timezone)::TIME < p_schedule_time THEN
                v_next_run := (DATE(NOW() AT TIME ZONE p_timezone) + p_schedule_time) AT TIME ZONE p_timezone;
            END IF;

        WHEN 'weekly' THEN
            -- Run on specified days of week
            IF p_schedule_days IS NULL OR array_length(p_schedule_days, 1) = 0 THEN
                -- Default to Monday if no days specified
                v_next_run := (DATE(v_base_time AT TIME ZONE p_timezone) + INTERVAL '1 week' + p_schedule_time) AT TIME ZONE p_timezone;
            ELSE
                -- Find next occurrence of specified day
                v_current_day := LOWER(TO_CHAR(v_base_time AT TIME ZONE p_timezone, 'Day'));
                v_days_to_add := 1;

                -- Simple implementation: check next 7 days
                WHILE v_days_to_add <= 7 LOOP
                    IF LOWER(TO_CHAR((v_base_time + (v_days_to_add || ' days')::INTERVAL) AT TIME ZONE p_timezone, 'Day')) = ANY(p_schedule_days) THEN
                        EXIT;
                    END IF;
                    v_days_to_add := v_days_to_add + 1;
                END LOOP;

                v_next_run := (DATE(v_base_time AT TIME ZONE p_timezone) + (v_days_to_add || ' days')::INTERVAL + p_schedule_time) AT TIME ZONE p_timezone;
            END IF;

        ELSE
            -- Default: run tomorrow
            v_next_run := (DATE(v_base_time AT TIME ZONE p_timezone) + INTERVAL '1 day' + p_schedule_time) AT TIME ZONE p_timezone;
    END CASE;

    RETURN v_next_run;
END;
$$ LANGUAGE plpgsql;

-- Trigger to automatically calculate next_run_at
CREATE OR REPLACE FUNCTION update_scheduler_job_next_run()
RETURNS TRIGGER AS $$
BEGIN
    -- Calculate next run time whenever job is created or updated
    IF TG_OP = 'INSERT' OR (TG_OP = 'UPDATE' AND (
        NEW.schedule_type != OLD.schedule_type OR
        NEW.schedule_time != OLD.schedule_time OR
        NEW.schedule_days IS DISTINCT FROM OLD.schedule_days OR
        NEW.timezone != OLD.timezone OR
        NEW.last_run_at IS DISTINCT FROM OLD.last_run_at
    )) THEN
        NEW.next_run_at := calculate_next_run_time(
            NEW.schedule_type,
            NEW.schedule_time,
            NEW.schedule_days,
            NEW.timezone,
            NEW.last_run_at
        );
    END IF;

    -- Update updated_at
    NEW.updated_at := NOW();

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_scheduler_job_next_run
    BEFORE INSERT OR UPDATE ON scheduler_jobs
    FOR EACH ROW
    EXECUTE FUNCTION update_scheduler_job_next_run();

-- =====================================================
-- Comments
-- =====================================================

COMMENT ON TABLE scheduler_jobs IS 'Scheduled automation jobs for scraping, generating, and sending newsletters';
COMMENT ON TABLE scheduler_executions IS 'Execution history and logs for scheduled jobs';
COMMENT ON COLUMN scheduler_jobs.actions IS 'Array of actions to perform in order: [scrape, generate, send]';
COMMENT ON COLUMN scheduler_jobs.config IS 'Job-specific configuration (max_items, days_back, test_mode, etc.)';
COMMENT ON COLUMN scheduler_jobs.schedule_days IS 'For weekly schedules: array of day names (monday, tuesday, etc.)';
COMMENT ON COLUMN scheduler_executions.execution_log IS 'Array of timestamped log messages during execution';

-- =====================================================
-- Grant permissions (if using service role)
-- =====================================================

-- Grant service role full access (for background worker)
-- Note: Adjust role name as needed for your Supabase project
-- GRANT ALL ON scheduler_jobs TO service_role;
-- GRANT ALL ON scheduler_executions TO service_role;
