import { apiClient } from './client';
import {
  SchedulerJob,
  SchedulerJobCreate,
  SchedulerJobUpdate,
  SchedulerJobListResponse,
  SchedulerExecution,
  SchedulerExecutionListResponse,
  SchedulerExecutionStats,
  RunJobNowRequest,
  RunJobNowResponse,
  Activity
} from '@/types/scheduler';

export const schedulerApi = {
  // Job Management
  async createJob(data: SchedulerJobCreate): Promise<SchedulerJob> {
    const response = await apiClient.post<SchedulerJob>('/api/v1/scheduler', data);

    if (response.success && response.data) {
      return response.data;
    }
    throw new Error(response.error || 'Failed to create scheduled job');
  },

  async listJobs(workspaceId: string): Promise<SchedulerJobListResponse> {
    const response = await apiClient.get<SchedulerJobListResponse>(
      `/api/v1/scheduler/workspaces/${workspaceId}`
    );

    if (response.success && response.data) {
      return response.data;
    }
    throw new Error(response.error || 'Failed to list scheduled jobs');
  },

  async getJob(jobId: string): Promise<SchedulerJob> {
    const response = await apiClient.get<SchedulerJob>(`/api/v1/scheduler/${jobId}`);

    if (response.success && response.data) {
      return response.data;
    }
    throw new Error(response.error || 'Failed to get scheduled job');
  },

  async updateJob(jobId: string, data: SchedulerJobUpdate): Promise<SchedulerJob> {
    const response = await apiClient.put<SchedulerJob>(`/api/v1/scheduler/${jobId}`, data);

    if (response.success && response.data) {
      return response.data;
    }
    throw new Error(response.error || 'Failed to update scheduled job');
  },

  async deleteJob(jobId: string): Promise<void> {
    const response = await apiClient.delete(`/api/v1/scheduler/${jobId}`);

    if (!response.success) {
      throw new Error(response.error || 'Failed to delete scheduled job');
    }
  },

  // Job Control
  async pauseJob(jobId: string): Promise<SchedulerJob> {
    const response = await apiClient.post<SchedulerJob>(
      `/api/v1/scheduler/${jobId}/pause`,
      {}
    );

    if (response.success && response.data) {
      return response.data;
    }
    throw new Error(response.error || 'Failed to pause scheduled job');
  },

  async resumeJob(jobId: string): Promise<SchedulerJob> {
    const response = await apiClient.post<SchedulerJob>(
      `/api/v1/scheduler/${jobId}/resume`,
      {}
    );

    if (response.success && response.data) {
      return response.data;
    }
    throw new Error(response.error || 'Failed to resume scheduled job');
  },

  async runJobNow(jobId: string, request: RunJobNowRequest): Promise<RunJobNowResponse> {
    const response = await apiClient.post<RunJobNowResponse>(
      `/api/v1/scheduler/${jobId}/run-now`,
      request
    );

    if (response.success && response.data) {
      return response.data;
    }
    throw new Error(response.error || 'Failed to trigger job execution');
  },

  // Execution History
  async getExecutionHistory(jobId: string, limit?: number): Promise<SchedulerExecutionListResponse> {
    const params = new URLSearchParams();
    if (limit) params.append('limit', limit.toString());

    const queryString = params.toString();
    const url = `/api/v1/scheduler/${jobId}/history${queryString ? `?${queryString}` : ''}`;
    const response = await apiClient.get<SchedulerExecutionListResponse>(url);

    if (response.success && response.data) {
      return response.data;
    }
    throw new Error(response.error || 'Failed to get execution history');
  },

  async getExecutionStats(jobId: string): Promise<SchedulerExecutionStats> {
    const response = await apiClient.get<SchedulerExecutionStats>(
      `/api/v1/scheduler/${jobId}/stats`
    );

    if (response.success && response.data) {
      return response.data;
    }
    throw new Error(response.error || 'Failed to get execution stats');
  },

  // Workspace Activities
  async getWorkspaceActivities(workspaceId: string, limit: number = 10): Promise<Activity[]> {
    const params = new URLSearchParams();
    if (limit) params.append('limit', limit.toString());

    const queryString = params.toString();
    const url = `/api/v1/scheduler/workspaces/${workspaceId}/activities${queryString ? `?${queryString}` : ''}`;
    const response = await apiClient.get<{ activities: Activity[]; count: number; workspace_id: string }>(url);

    if (response.success && response.data) {
      return response.data.activities;
    }
    throw new Error(response.error || 'Failed to get workspace activities');
  },
};
