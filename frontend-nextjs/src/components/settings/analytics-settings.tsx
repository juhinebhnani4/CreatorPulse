'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { useToast } from '@/lib/hooks/use-toast';
import { useWorkspaceStore } from '@/lib/stores/workspace-store';
import { analyticsApi, WorkspaceAnalytics, ContentPerformance } from '@/lib/api/analytics';
import { BarChart3, Download, TrendingUp, MousePointer, Mail, ExternalLink } from 'lucide-react';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';

export function AnalyticsSettings() {
  const { toast } = useToast();
  const { currentWorkspace } = useWorkspaceStore();
  const [analytics, setAnalytics] = useState<WorkspaceAnalytics | null>(null);
  const [contentPerformance, setContentPerformance] = useState<ContentPerformance[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [period, setPeriod] = useState('30d');

  useEffect(() => {
    if (currentWorkspace?.id) {
      loadAnalytics();
    }
  }, [currentWorkspace?.id, period]);

  const loadAnalytics = async () => {
    if (!currentWorkspace?.id) return;

    try {
      setIsLoading(true);
      const data = await analyticsApi.getDashboard(currentWorkspace.id, period);
      setAnalytics(data.workspace_analytics);
      setContentPerformance(data.content_performance);
    } catch (error: any) {
      console.error('Failed to load analytics:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleExport = async (format: 'csv' | 'json') => {
    if (!currentWorkspace?.id) return;

    try {
      await analyticsApi.exportData(currentWorkspace.id, format);
      toast({
        title: 'Export Started',
        description: `Your analytics data is being downloaded as ${format.toUpperCase()}`,
      });
    } catch (error: any) {
      toast({
        title: 'Export Failed',
        description: error.message || 'Failed to export analytics data',
        variant: 'destructive',
      });
    }
  };

  return (
    <div className="space-y-6">
      {/* Info */}
      <div className="p-4 bg-blue-50 dark:bg-blue-950 border border-blue-200 dark:border-blue-800 rounded-lg">
        <div className="flex gap-3">
          <BarChart3 className="h-5 w-5 text-blue-600 dark:text-blue-400 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-sm font-medium text-blue-900 dark:text-blue-100">
              Email Analytics & Engagement Tracking
            </p>
            <p className="text-sm text-blue-700 dark:text-blue-300 mt-1">
              Track newsletter opens, clicks, bounces, and engagement. All analytics are automatically
              recorded when you send newsletters.
            </p>
          </div>
        </div>
      </div>

      {/* Period Selector & Export */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <label className="text-sm font-medium">Period:</label>
          <Select value={period} onValueChange={setPeriod}>
            <SelectTrigger className="w-[140px]">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="7d">Last 7 days</SelectItem>
              <SelectItem value="30d">Last 30 days</SelectItem>
              <SelectItem value="90d">Last 90 days</SelectItem>
              <SelectItem value="1y">Last year</SelectItem>
            </SelectContent>
          </Select>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={() => handleExport('csv')}>
            <Download className="h-4 w-4 mr-2" />
            Export CSV
          </Button>
          <Button variant="outline" size="sm" onClick={() => handleExport('json')}>
            <Download className="h-4 w-4 mr-2" />
            Export JSON
          </Button>
        </div>
      </div>

      {/* Summary Stats */}
      {analytics ? (
        <>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center gap-2 mb-2">
                  <Mail className="h-4 w-4 text-muted-foreground" />
                  <p className="text-sm text-muted-foreground">Newsletters Sent</p>
                </div>
                <p className="text-2xl font-bold">{analytics.total_newsletters}</p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center gap-2 mb-2">
                  <TrendingUp className="h-4 w-4 text-muted-foreground" />
                  <p className="text-sm text-muted-foreground">Total Sent</p>
                </div>
                <p className="text-2xl font-bold">{analytics.total_sent.toLocaleString()}</p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center gap-2 mb-2">
                  <Mail className="h-4 w-4 text-muted-foreground" />
                  <p className="text-sm text-muted-foreground">Avg. Open Rate</p>
                </div>
                <p className="text-2xl font-bold text-green-600">
                  {(analytics.avg_open_rate * 100).toFixed(1)}%
                </p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center gap-2 mb-2">
                  <MousePointer className="h-4 w-4 text-muted-foreground" />
                  <p className="text-sm text-muted-foreground">Avg. Click Rate</p>
                </div>
                <p className="text-2xl font-bold text-blue-600">
                  {(analytics.avg_click_rate * 100).toFixed(1)}%
                </p>
              </CardContent>
            </Card>
          </div>

          {/* Detailed Metrics */}
          <Card>
            <CardContent className="pt-6">
              <h3 className="font-semibold mb-4">Engagement Metrics</h3>
              <div className="grid md:grid-cols-3 gap-6">
                <div>
                  <p className="text-sm text-muted-foreground mb-2">Delivered</p>
                  <p className="text-xl font-bold">{analytics.total_delivered.toLocaleString()}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground mb-2">Opens</p>
                  <p className="text-xl font-bold">{analytics.total_opened.toLocaleString()}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground mb-2">Clicks</p>
                  <p className="text-xl font-bold">{analytics.total_clicked.toLocaleString()}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground mb-2">Click-to-Open Rate</p>
                  <p className="text-xl font-bold">{(analytics.avg_click_to_open_rate * 100).toFixed(1)}%</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </>
      ) : isLoading ? (
        <Card>
          <CardContent className="py-12 text-center text-muted-foreground">
            Loading analytics...
          </CardContent>
        </Card>
      ) : (
        <Card>
          <CardContent className="py-12 text-center">
            <BarChart3 className="h-12 w-12 mx-auto text-muted-foreground mb-2" />
            <p className="text-muted-foreground">No analytics data yet</p>
            <p className="text-sm text-muted-foreground mt-1">
              Send your first newsletter to start tracking engagement
            </p>
          </CardContent>
        </Card>
      )}

      {/* Top Content Performance */}
      {contentPerformance.length > 0 && (
        <div>
          <h3 className="text-sm font-medium mb-3">Top Performing Content</h3>
          <Card>
            <CardContent className="pt-6">
              <div className="space-y-3">
                {contentPerformance.slice(0, 5).map((item, idx) => (
                  <div key={item.content_item_id} className="flex items-start justify-between py-2 border-b last:border-0">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-sm font-medium text-muted-foreground">#{idx + 1}</span>
                        <h4 className="font-medium text-sm">{item.title}</h4>
                      </div>
                      {item.url && (
                        <a
                          href={item.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-xs text-blue-600 hover:underline flex items-center gap-1"
                        >
                          <ExternalLink className="h-3 w-3" />
                          {item.url.length > 50 ? item.url.substring(0, 50) + '...' : item.url}
                        </a>
                      )}
                    </div>
                    <div className="text-right ml-4">
                      <p className="text-sm font-bold">{item.total_clicks} clicks</p>
                      <p className="text-xs text-muted-foreground">
                        {(item.avg_click_rate * 100).toFixed(1)}% CTR
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
