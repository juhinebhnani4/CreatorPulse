'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  Calendar,
  Clock,
  Play,
  Pause,
  Trash2,
  Loader2,
  Plus,
  CheckCircle2,
  XCircle,
  AlertCircle,
  Zap
} from 'lucide-react';
import { useToast } from '@/lib/hooks/use-toast';
import { AppHeader } from '@/components/layout/app-header';
import { useAuthStore } from '@/lib/stores/auth-store';
import { useWorkspaceStore } from '@/lib/stores/workspace-store';
import { schedulerApi } from '@/lib/api/scheduler';
import { SchedulerJob } from '@/types/scheduler';

export default function SchedulePage() {
  const router = useRouter();
  const { toast } = useToast();
  const { isAuthenticated, _hasHydrated } = useAuthStore();
  const { currentWorkspace } = useWorkspaceStore();
  const [isMounted, setIsMounted] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [jobs, setJobs] = useState<SchedulerJob[]>([]);
  const [processingJobId, setProcessingJobId] = useState<string | null>(null);

  useEffect(() => {
    setIsMounted(true);
  }, []);

  useEffect(() => {
    if (!isMounted || !_hasHydrated) return;

    if (!isAuthenticated) {
      router.push('/login');
      return;
    }

    if (!currentWorkspace) {
      return;
    }

    fetchJobs();
  }, [isAuthenticated, isMounted, _hasHydrated, currentWorkspace, router]);

  const fetchJobs = async () => {
    if (!currentWorkspace) return;

    try {
      setIsLoading(true);
      const response = await schedulerApi.listJobs(currentWorkspace.id);
      setJobs(response.jobs || []);
    } catch (error: any) {
      console.error('Failed to fetch scheduled jobs:', error);
      toast({
        title: 'Error',
        description: error.message || 'Failed to load scheduled jobs',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handlePause = async (jobId: string) => {
    try {
      setProcessingJobId(jobId);
      const updatedJob = await schedulerApi.pauseJob(jobId);

      toast({
        title: '⏸ Job Paused',
        description: 'The scheduled job has been paused',
      });

      setJobs(jobs.map(j => j.id === jobId ? updatedJob : j));
    } catch (error: any) {
      toast({
        title: 'Failed to Pause',
        description: error.message || 'Could not pause job',
        variant: 'destructive',
      });
    } finally {
      setProcessingJobId(null);
    }
  };

  const handleResume = async (jobId: string) => {
    try {
      setProcessingJobId(jobId);
      const updatedJob = await schedulerApi.resumeJob(jobId);

      toast({
        title: '▶ Job Resumed',
        description: 'The scheduled job has been resumed',
      });

      setJobs(jobs.map(j => j.id === jobId ? updatedJob : j));
    } catch (error: any) {
      toast({
        title: 'Failed to Resume',
        description: error.message || 'Could not resume job',
        variant: 'destructive',
      });
    } finally {
      setProcessingJobId(null);
    }
  };

  const handleRunNow = async (jobId: string) => {
    try {
      setProcessingJobId(jobId);
      const result = await schedulerApi.runJobNow(jobId, { test_mode: false });

      toast({
        title: '⚡ Job Triggered',
        description: result.message || 'Job execution started',
        className: 'animate-celebration',
      });

      // Refresh to update stats
      await fetchJobs();
    } catch (error: any) {
      toast({
        title: 'Failed to Trigger',
        description: error.message || 'Could not trigger job',
        variant: 'destructive',
      });
    } finally {
      setProcessingJobId(null);
    }
  };

  const handleDelete = async (jobId: string) => {
    if (!confirm('Are you sure you want to delete this scheduled job? This action cannot be undone.')) {
      return;
    }

    try {
      setProcessingJobId(jobId);
      await schedulerApi.deleteJob(jobId);

      toast({
        title: '✓ Job Deleted',
        description: 'The scheduled job has been removed',
      });

      setJobs(jobs.filter(j => j.id !== jobId));
    } catch (error: any) {
      toast({
        title: 'Failed to Delete',
        description: error.message || 'Could not delete job',
        variant: 'destructive',
      });
    } finally {
      setProcessingJobId(null);
    }
  };

  if (!isMounted || !_hasHydrated || !isAuthenticated) {
    return null;
  }

  const activeJobs = jobs.filter(j => j.status === 'active' && j.is_enabled);
  const pausedJobs = jobs.filter(j => j.status === 'paused' || !j.is_enabled);

  return (
    <div className="min-h-screen bg-muted/20">
      <AppHeader />

      <main className="container mx-auto px-4 py-8 max-w-7xl">
        {/* Header */}
        <div className="mb-10 animate-slide-up flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold mb-3 bg-gradient-to-r from-primary to-primary/60 bg-clip-text text-transparent">
              Scheduled Automations
            </h1>
            <p className="text-lg text-muted-foreground">Automate your newsletter workflow with scheduled jobs</p>
          </div>
          <Button
            onClick={() => toast({ title: 'Create Schedule', description: 'Coming soon!' })}
            className="rounded-xl bg-gradient-hero hover:opacity-90"
          >
            <Plus className="h-4 w-4 mr-2" />
            New Schedule
          </Button>
        </div>

        {/* Stats Row */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8 animate-slide-up" style={{ animationDelay: '50ms' }}>
          <Card className="p-4 bg-gradient-warm/10 border-none shadow-md hover:-translate-y-1 transition-transform">
            <div className="flex items-center gap-3 mb-2">
              <Calendar className="h-5 w-5 text-primary" />
              <p className="text-xs uppercase tracking-wide text-muted-foreground">Total Jobs</p>
            </div>
            <p className="text-3xl font-bold">{jobs.length}</p>
          </Card>

          <Card className="p-4 bg-green-500/10 border-none shadow-md hover:-translate-y-1 transition-transform">
            <div className="flex items-center gap-3 mb-2">
              <Play className="h-5 w-5 text-green-600" />
              <p className="text-xs uppercase tracking-wide text-muted-foreground">Active</p>
            </div>
            <p className="text-3xl font-bold text-green-600">{activeJobs.length}</p>
          </Card>

          <Card className="p-4 bg-yellow-500/10 border-none shadow-md hover:-translate-y-1 transition-transform">
            <div className="flex items-center gap-3 mb-2">
              <Pause className="h-5 w-5 text-yellow-600" />
              <p className="text-xs uppercase tracking-wide text-muted-foreground">Paused</p>
            </div>
            <p className="text-3xl font-bold text-yellow-600">{pausedJobs.length}</p>
          </Card>

          <Card className="p-4 bg-blue-500/10 border-none shadow-md hover:-translate-y-1 transition-transform">
            <div className="flex items-center gap-3 mb-2">
              <CheckCircle2 className="h-5 w-5 text-blue-600" />
              <p className="text-xs uppercase tracking-wide text-muted-foreground">Success Rate</p>
            </div>
            <p className="text-3xl font-bold text-blue-600">
              {jobs.length > 0
                ? Math.round(
                    (jobs.reduce((acc, j) => acc + j.successful_runs, 0) /
                      Math.max(jobs.reduce((acc, j) => acc + j.total_runs, 0), 1)) *
                      100
                  )
                : 0}%
            </p>
          </Card>
        </div>

        {/* Loading State */}
        {isLoading && (
          <div className="flex items-center justify-center py-20">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
          </div>
        )}

        {/* Jobs List */}
        {!isLoading && jobs.length > 0 && (
          <div className="space-y-5">
            {jobs.map((job, index) => {
              const nextRun = job.next_run_at ? new Date(job.next_run_at) : null;
              const lastRun = job.last_run_at ? new Date(job.last_run_at) : null;
              const isProcessing = processingJobId === job.id;

              return (
                <Card
                  key={job.id}
                  className="border-0 shadow-lg hover:shadow-xl transition-all duration-300 animate-slide-up"
                  style={{ animationDelay: `${(index + 2) * 50}ms` }}
                >
                  <CardContent className="pt-6 pb-6">
                    <div className="space-y-4">
                      {/* Header */}
                      <div className="flex items-start justify-between gap-4">
                        <div className="flex-1">
                          <div className="flex items-center gap-3 mb-2">
                            <h3 className="text-xl font-bold">{job.name}</h3>
                            <Badge
                              className={`border-0 ${
                                job.status === 'active' && job.is_enabled
                                  ? 'bg-green-500/10 text-green-600'
                                  : 'bg-yellow-500/10 text-yellow-600'
                              }`}
                            >
                              {job.status === 'active' && job.is_enabled ? '▶ Active' : '⏸ Paused'}
                            </Badge>
                            {job.last_run_status && (
                              <Badge
                                className={`border-0 ${
                                  job.last_run_status === 'completed'
                                    ? 'bg-success/10 text-success'
                                    : job.last_run_status === 'failed'
                                    ? 'bg-destructive/10 text-destructive'
                                    : 'bg-muted'
                                }`}
                              >
                                {job.last_run_status === 'completed' ? (
                                  <CheckCircle2 className="h-3 w-3 mr-1 inline" />
                                ) : job.last_run_status === 'failed' ? (
                                  <XCircle className="h-3 w-3 mr-1 inline" />
                                ) : (
                                  <AlertCircle className="h-3 w-3 mr-1 inline" />
                                )}
                                Last: {job.last_run_status}
                              </Badge>
                            )}
                          </div>
                          {job.description && (
                            <p className="text-sm text-muted-foreground mb-3">{job.description}</p>
                          )}
                        </div>
                      </div>

                      {/* Schedule Info */}
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 p-4 bg-muted/30 rounded-xl">
                        <div>
                          <p className="text-xs text-muted-foreground mb-1">Schedule</p>
                          <p className="font-semibold capitalize">{job.schedule_type}</p>
                        </div>
                        <div>
                          <p className="text-xs text-muted-foreground mb-1">Time</p>
                          <p className="font-semibold flex items-center gap-1">
                            <Clock className="h-3 w-3" />
                            {job.schedule_time}
                          </p>
                        </div>
                        <div>
                          <p className="text-xs text-muted-foreground mb-1">Next Run</p>
                          <p className="font-semibold text-sm">
                            {nextRun ? nextRun.toLocaleString() : 'Not scheduled'}
                          </p>
                        </div>
                        <div>
                          <p className="text-xs text-muted-foreground mb-1">Last Run</p>
                          <p className="font-semibold text-sm">
                            {lastRun ? lastRun.toLocaleString() : 'Never'}
                          </p>
                        </div>
                      </div>

                      {/* Actions */}
                      <div className="flex items-center gap-2">
                        {job.actions.map((action) => (
                          <Badge key={action} variant="outline" className="capitalize">
                            {action}
                          </Badge>
                        ))}
                      </div>

                      {/* Stats */}
                      <div className="flex items-center gap-6 text-sm">
                        <div>
                          <span className="text-muted-foreground">Total Runs:</span>{' '}
                          <span className="font-semibold">{job.total_runs}</span>
                        </div>
                        <div>
                          <span className="text-muted-foreground">Successful:</span>{' '}
                          <span className="font-semibold text-success">{job.successful_runs}</span>
                        </div>
                        <div>
                          <span className="text-muted-foreground">Failed:</span>{' '}
                          <span className="font-semibold text-destructive">{job.failed_runs}</span>
                        </div>
                      </div>

                      {/* Control Buttons */}
                      <div className="flex gap-3 pt-2">
                        {job.status === 'active' && job.is_enabled ? (
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handlePause(job.id)}
                            disabled={isProcessing}
                            className="rounded-xl"
                          >
                            <Pause className="h-4 w-4 mr-2" />
                            Pause
                          </Button>
                        ) : (
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleResume(job.id)}
                            disabled={isProcessing}
                            className="rounded-xl"
                          >
                            <Play className="h-4 w-4 mr-2" />
                            Resume
                          </Button>
                        )}

                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleRunNow(job.id)}
                          disabled={isProcessing}
                          className="rounded-xl hover:bg-purple-500 hover:text-white"
                        >
                          {isProcessing && processingJobId === job.id ? (
                            <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                          ) : (
                            <Zap className="h-4 w-4 mr-2" />
                          )}
                          Run Now
                        </Button>

                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleDelete(job.id)}
                          disabled={isProcessing}
                          className="rounded-xl hover:bg-destructive hover:text-destructive-foreground"
                        >
                          <Trash2 className="h-4 w-4 mr-2" />
                          Delete
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        )}

        {/* Empty State */}
        {!isLoading && jobs.length === 0 && (
          <Card>
            <CardContent className="py-12 text-center">
              <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-muted mb-4">
                <Calendar className="h-8 w-8 text-muted-foreground" />
              </div>
              <h3 className="text-lg font-semibold mb-2">No Scheduled Jobs Yet</h3>
              <p className="text-sm text-muted-foreground mb-4">
                Create your first automated schedule to streamline your newsletter workflow
              </p>
              <Button onClick={() => toast({ title: 'Create Schedule', description: 'Coming soon!' })}>
                <Plus className="h-4 w-4 mr-2" />
                Create Your First Schedule
              </Button>
            </CardContent>
          </Card>
        )}
      </main>
    </div>
  );
}
