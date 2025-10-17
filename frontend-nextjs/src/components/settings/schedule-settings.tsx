'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { useToast } from '@/lib/hooks/use-toast';
import { useWorkspace } from '@/lib/hooks/use-workspace';
import { Badge } from '@/components/ui/badge';
import { Switch } from '@/components/ui/switch';
import { Trash2, Play, Pause, Clock, Calendar, Plus } from 'lucide-react';

interface SchedulerJob {
  id: string;
  name: string;
  description?: string;
  schedule_type: string;
  schedule_time: string;
  schedule_days?: string[];
  timezone: string;
  actions: string[];
  status: string;
  is_enabled: boolean;
  next_run_at?: string;
  last_run_at?: string;
  total_runs?: number;
  successful_runs?: number;
  failed_runs?: number;
}

export function ScheduleSettings() {
  const { toast } = useToast();
  const { workspace } = useWorkspace();

  const [jobs, setJobs] = useState<SchedulerJob[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  // Form state for new job
  const [showNewJobForm, setShowNewJobForm] = useState(false);
  const [jobName, setJobName] = useState('Daily Newsletter');
  const [time, setTime] = useState('08:00');
  const [timezone, setTimezone] = useState('America/New_York');
  const [frequency, setFrequency] = useState('daily');
  const [selectedDays, setSelectedDays] = useState<string[]>(['monday']);
  const [actions, setActions] = useState<string[]>(['scrape', 'generate', 'send']);

  useEffect(() => {
    if (workspace?.id) {
      loadJobs();
    }
  }, [workspace?.id]);

  const loadJobs = async () => {
    if (!workspace?.id) return;

    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:8000/api/v1/scheduler/workspaces/${workspace.id}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const result = await response.json();
        setJobs(result.data?.jobs || []);
      } else {
        throw new Error('Failed to load schedules');
      }
    } catch (error) {
      console.error('Error loading schedules:', error);
      toast({
        title: 'Error',
        description: 'Failed to load schedules',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleCreateJob = async () => {
    if (!workspace?.id || !jobName.trim()) {
      toast({
        title: 'Validation Error',
        description: 'Please provide a job name',
        variant: 'destructive',
      });
      return;
    }

    setSaving(true);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:8000/api/v1/scheduler', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          workspace_id: workspace.id,
          name: jobName,
          description: `Automated ${frequency} newsletter`,
          schedule_type: frequency,
          schedule_time: time,
          schedule_days: frequency === 'weekly' ? selectedDays : null,
          timezone: timezone,
          actions: actions,
          is_enabled: true,
        }),
      });

      if (response.ok) {
        toast({
          title: 'Schedule Created',
          description: 'Your schedule has been created successfully',
        });
        setShowNewJobForm(false);
        loadJobs();
      } else {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to create schedule');
      }
    } catch (error) {
      console.error('Error creating schedule:', error);
      toast({
        title: 'Error',
        description: error instanceof Error ? error.message : 'Failed to create schedule',
        variant: 'destructive',
      });
    } finally {
      setSaving(false);
    }
  };

  const handleToggleJob = async (jobId: string, currentlyEnabled: boolean) => {
    try {
      const token = localStorage.getItem('token');
      const endpoint = currentlyEnabled
        ? `http://localhost:8000/api/v1/scheduler/${jobId}/pause`
        : `http://localhost:8000/api/v1/scheduler/${jobId}/resume`;

      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        toast({
          title: 'Success',
          description: `Schedule ${currentlyEnabled ? 'paused' : 'resumed'}`,
        });
        loadJobs();
      } else {
        throw new Error('Failed to update schedule');
      }
    } catch (error) {
      console.error('Error toggling schedule:', error);
      toast({
        title: 'Error',
        description: 'Failed to update schedule',
        variant: 'destructive',
      });
    }
  };

  const handleDeleteJob = async (jobId: string) => {
    if (!confirm('Are you sure you want to delete this schedule?')) return;

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:8000/api/v1/scheduler/${jobId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        toast({
          title: 'Success',
          description: 'Schedule deleted',
        });
        loadJobs();
      } else {
        throw new Error('Failed to delete schedule');
      }
    } catch (error) {
      console.error('Error deleting schedule:', error);
      toast({
        title: 'Error',
        description: 'Failed to delete schedule',
        variant: 'destructive',
      });
    }
  };

  const formatNextRun = (nextRunAt?: string) => {
    if (!nextRunAt) return 'Not scheduled';
    const date = new Date(nextRunAt);
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
      hour12: true,
    });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold">Scheduled Jobs</h3>
          <p className="text-sm text-muted-foreground">
            Automate your newsletter generation and delivery
          </p>
        </div>
        <Button onClick={() => setShowNewJobForm(!showNewJobForm)}>
          <Plus className="h-4 w-4 mr-2" />
          New Schedule
        </Button>
      </div>

      {/* New Job Form */}
      {showNewJobForm && (
        <div className="p-6 border rounded-lg bg-muted/50 space-y-4">
          <h4 className="font-semibold">Create New Schedule</h4>

          <div>
            <label className="text-sm font-medium mb-2 block">Schedule Name</label>
            <Input
              value={jobName}
              onChange={(e) => setJobName(e.target.value)}
              placeholder="e.g., Daily Newsletter"
              className="max-w-md"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-medium mb-2 block">Frequency</label>
              <Select value={frequency} onValueChange={setFrequency}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="daily">Daily</SelectItem>
                  <SelectItem value="weekly">Weekly</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div>
              <label className="text-sm font-medium mb-2 block">Time</label>
              <Input
                type="time"
                value={time}
                onChange={(e) => setTime(e.target.value)}
              />
            </div>
          </div>

          {frequency === 'weekly' && (
            <div>
              <label className="text-sm font-medium mb-2 block">Days</label>
              <Select value={selectedDays[0]} onValueChange={(day) => setSelectedDays([day])}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="monday">Monday</SelectItem>
                  <SelectItem value="tuesday">Tuesday</SelectItem>
                  <SelectItem value="wednesday">Wednesday</SelectItem>
                  <SelectItem value="thursday">Thursday</SelectItem>
                  <SelectItem value="friday">Friday</SelectItem>
                  <SelectItem value="saturday">Saturday</SelectItem>
                  <SelectItem value="sunday">Sunday</SelectItem>
                </SelectContent>
              </Select>
            </div>
          )}

          <div>
            <label className="text-sm font-medium mb-2 block">Timezone</label>
            <Select value={timezone} onValueChange={setTimezone}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="America/New_York">Eastern Time (ET)</SelectItem>
                <SelectItem value="America/Chicago">Central Time (CT)</SelectItem>
                <SelectItem value="America/Denver">Mountain Time (MT)</SelectItem>
                <SelectItem value="America/Los_Angeles">Pacific Time (PT)</SelectItem>
                <SelectItem value="Europe/London">London (GMT)</SelectItem>
                <SelectItem value="Europe/Paris">Paris (CET)</SelectItem>
                <SelectItem value="Asia/Tokyo">Tokyo (JST)</SelectItem>
                <SelectItem value="UTC">UTC</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div>
            <label className="text-sm font-medium mb-2 block">Actions</label>
            <div className="flex flex-wrap gap-2">
              {['scrape', 'generate', 'send'].map((action) => (
                <Button
                  key={action}
                  variant={actions.includes(action) ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => {
                    if (actions.includes(action)) {
                      setActions(actions.filter(a => a !== action));
                    } else {
                      setActions([...actions, action]);
                    }
                  }}
                >
                  {action.charAt(0).toUpperCase() + action.slice(1)}
                </Button>
              ))}
            </div>
          </div>

          <div className="flex gap-2 pt-2">
            <Button onClick={handleCreateJob} disabled={saving}>
              {saving ? 'Creating...' : 'Create Schedule'}
            </Button>
            <Button variant="outline" onClick={() => setShowNewJobForm(false)}>
              Cancel
            </Button>
          </div>
        </div>
      )}

      {/* Jobs List */}
      {jobs.length === 0 ? (
        <div className="text-center py-8 border rounded-lg bg-muted/50">
          <Calendar className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
          <p className="text-sm text-muted-foreground">
            No scheduled jobs yet. Create one to automate your newsletters.
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {jobs.map((job) => (
            <div key={job.id} className="p-4 border rounded-lg">
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <h4 className="font-semibold">{job.name}</h4>
                    <Badge variant={job.is_enabled ? 'default' : 'secondary'}>
                      {job.status}
                    </Badge>
                  </div>
                  {job.description && (
                    <p className="text-sm text-muted-foreground">{job.description}</p>
                  )}
                </div>
                <div className="flex items-center gap-2">
                  <Switch
                    checked={job.is_enabled}
                    onCheckedChange={() => handleToggleJob(job.id, job.is_enabled)}
                  />
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => handleDeleteJob(job.id)}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div>
                  <div className="flex items-center gap-1 text-muted-foreground mb-1">
                    <Clock className="h-3 w-3" />
                    <span>Schedule</span>
                  </div>
                  <p className="font-medium">
                    {job.schedule_type === 'daily'
                      ? `Daily at ${job.schedule_time}`
                      : `${job.schedule_days?.join(', ')} at ${job.schedule_time}`
                    }
                  </p>
                  <p className="text-xs text-muted-foreground">{job.timezone}</p>
                </div>

                <div>
                  <div className="text-muted-foreground mb-1">Next Run</div>
                  <p className="font-medium">{formatNextRun(job.next_run_at)}</p>
                </div>

                <div>
                  <div className="text-muted-foreground mb-1">Actions</div>
                  <div className="flex flex-wrap gap-1">
                    {job.actions.map((action) => (
                      <Badge key={action} variant="outline" className="text-xs">
                        {action}
                      </Badge>
                    ))}
                  </div>
                </div>

                <div>
                  <div className="text-muted-foreground mb-1">Stats</div>
                  <p className="text-xs">
                    {job.total_runs || 0} runs · {job.successful_runs || 0} success
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
