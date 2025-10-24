export type ScheduleType = 'daily' | 'weekly' | 'custom' | 'cron';
export type JobStatus = 'active' | 'paused' | 'disabled';
export type JobAction = 'scrape' | 'generate' | 'send';
export type ExecutionStatus = 'pending' | 'running' | 'completed' | 'failed' | 'partial';

export interface SchedulerJobCreate {
  workspace_id: string;
  name: string;
  description?: string;
  schedule_type: ScheduleType;
  schedule_time: string; // HH:MM format
  schedule_days?: string[]; // For weekly: monday, tuesday, etc.
  cron_expression?: string;
  timezone: string;
  actions: JobAction[];
  config?: Record<string, any>;
  is_enabled: boolean;
}

export interface SchedulerJobUpdate {
  name?: string;
  description?: string;
  schedule_type?: ScheduleType;
  schedule_time?: string;
  schedule_days?: string[];
  cron_expression?: string;
  timezone?: string;
  actions?: JobAction[];
  config?: Record<string, any>;
  status?: JobStatus;
  is_enabled?: boolean;
}

export interface SchedulerJob {
  id: string;
  workspace_id: string;
  name: string;
  description?: string;
  schedule_type: ScheduleType;
  schedule_time: string;
  schedule_days?: string[];
  cron_expression?: string;
  timezone: string;
  actions: JobAction[];
  config: Record<string, any>;
  status: JobStatus;
  is_enabled: boolean;
  last_run_at?: string;
  last_run_status?: string;
  last_error?: string;
  next_run_at?: string;
  total_runs: number;
  successful_runs: number;
  failed_runs: number;
  created_by: string;
  created_at: string;
  updated_at: string;
}

export interface SchedulerJobListResponse {
  jobs: SchedulerJob[];
  count: number;
  workspace_id: string;
}

export interface SchedulerExecution {
  id: string;
  job_id: string;
  workspace_id: string;
  started_at: string;
  completed_at?: string;
  duration_seconds?: number;
  status: ExecutionStatus;
  actions_performed: string[];
  scrape_result?: Record<string, any>;
  generate_result?: Record<string, any>;
  send_result?: Record<string, any>;
  error_message?: string;
  // Note: error_details and execution_log removed in migration 014
  created_at: string;
}

export interface SchedulerExecutionListResponse {
  executions: SchedulerExecution[];
  count: number;
  job_id: string;
}

export interface SchedulerExecutionStats {
  total_executions: number;
  successful: number;
  failed: number;
  partial: number;
  success_rate: number;
  avg_duration_seconds?: number;
  last_execution_at?: string;
}

export interface RunJobNowRequest {
  test_mode: boolean;
}

export interface RunJobNowResponse {
  execution_id: string;
  job_id: string;
  status: string;
  message: string;
}

// Activity interface for dashboard activity feed
export interface Activity {
  id: string;
  type: 'scrape' | 'generate' | 'send' | 'schedule';
  title: string;
  description: string;
  timestamp: string;
  status: 'success' | 'pending' | 'scheduled';
}
