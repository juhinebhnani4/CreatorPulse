'use client';

import { useState, useEffect } from 'react';
import { useWorkspace } from '@/lib/hooks/use-workspace';
import {
  analyticsApi,
  WorkspaceAnalytics,
  ContentPerformance,
  NewsletterAnalytics,
} from '@/lib/api/analytics';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { useToast } from '@/lib/hooks/use-toast';
import {
  BarChart3,
  TrendingUp,
  Mail,
  MousePointerClick,
  Eye,
  Download,
  RefreshCw,
  Loader2,
  Calendar,
  Users,
  Target,
  ExternalLink,
  ArrowUpRight,
  ArrowDownRight,
  Minus,
} from 'lucide-react';

type TimePeriod = '7d' | '30d' | '90d' | '1y';

export default function AnalyticsPage() {
  const { workspace } = useWorkspace();
  const { toast } = useToast();

  const [loading, setLoading] = useState(false);
  const [period, setPeriod] = useState<TimePeriod>('30d');
  const [workspaceAnalytics, setWorkspaceAnalytics] = useState<WorkspaceAnalytics | null>(null);
  const [contentPerformance, setContentPerformance] = useState<ContentPerformance[]>([]);
  const [exporting, setExporting] = useState(false);

  useEffect(() => {
    if (workspace?.id) {
      loadAnalytics();
    }
  }, [workspace?.id, period]);

  const loadAnalytics = async () => {
    if (!workspace?.id) return;

    try {
      setLoading(true);

      const data = await analyticsApi.getDashboard(workspace.id, period);

      setWorkspaceAnalytics(data.workspace_analytics);
      setContentPerformance(data.content_performance || []);
    } catch (error: any) {
      console.error('Analytics loading error:', error);
      // Don't show error toast for empty data
      if (!error.message.includes('not found')) {
        toast({
          title: 'Failed to load analytics',
          description: error.message,
          variant: 'destructive',
        });
      }
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async (format: 'csv' | 'json') => {
    if (!workspace?.id) return;

    try {
      setExporting(true);

      // Calculate date range based on period
      const endDate = new Date();
      const startDate = new Date();
      const days = period === '7d' ? 7 : period === '30d' ? 30 : period === '90d' ? 90 : 365;
      startDate.setDate(startDate.getDate() - days);

      await analyticsApi.exportData(workspace.id, format, startDate, endDate);

      toast({
        title: `Analytics exported`,
        description: `Downloaded as ${format.toUpperCase()} file`,
      });
    } catch (error: any) {
      toast({
        title: 'Export failed',
        description: error.message,
        variant: 'destructive',
      });
    } finally {
      setExporting(false);
    }
  };

  const getPeriodLabel = (p: TimePeriod) => {
    switch (p) {
      case '7d':
        return 'Last 7 Days';
      case '30d':
        return 'Last 30 Days';
      case '90d':
        return 'Last 90 Days';
      case '1y':
        return 'Last Year';
    }
  };

  if (loading && !workspaceAnalytics) {
    return (
      <div className="flex items-center justify-center h-96">
        <Loader2 className="w-8 h-8 animate-spin text-orange-600" />
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-orange-600 to-amber-600 bg-clip-text text-transparent">
            Analytics & Insights
          </h1>
          <p className="text-muted-foreground mt-2">
            Track newsletter performance and engagement metrics
          </p>
        </div>

        <div className="flex gap-2">
          <Button variant="outline" onClick={loadAnalytics} disabled={loading}>
            <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
          <Button
            variant="outline"
            onClick={() => handleExport('csv')}
            disabled={exporting || !workspaceAnalytics}
          >
            <Download className="w-4 h-4 mr-2" />
            Export CSV
          </Button>
          <Button
            variant="outline"
            onClick={() => handleExport('json')}
            disabled={exporting || !workspaceAnalytics}
          >
            <Download className="w-4 h-4 mr-2" />
            Export JSON
          </Button>
        </div>
      </div>

      {/* Time Period Selector */}
      <div className="flex items-center gap-2">
        <Calendar className="w-5 h-5 text-muted-foreground" />
        <span className="text-sm text-muted-foreground">Period:</span>
        <div className="flex gap-2">
          {(['7d', '30d', '90d', '1y'] as TimePeriod[]).map((p) => (
            <Button
              key={p}
              variant={period === p ? 'default' : 'outline'}
              size="sm"
              onClick={() => setPeriod(p)}
              className={period === p ? 'bg-gradient-to-r from-orange-600 to-amber-600' : ''}
            >
              {getPeriodLabel(p)}
            </Button>
          ))}
        </div>
      </div>

      {!workspaceAnalytics ? (
        <Card className="p-12 text-center">
          <BarChart3 className="w-16 h-16 text-muted-foreground mx-auto mb-4" />
          <h2 className="text-2xl font-semibold mb-2">No Analytics Data Yet</h2>
          <p className="text-muted-foreground mb-6">
            Send some newsletters to start tracking engagement metrics and performance.
          </p>
          <Button onClick={loadAnalytics}>
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh
          </Button>
        </Card>
      ) : (
        <>
          {/* Overview Stats */}
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <StatCard
              title="Newsletters Sent"
              value={workspaceAnalytics.total_newsletters}
              icon={<Mail className="w-5 h-5 text-blue-600" />}
              subtitle={`${workspaceAnalytics.total_sent} emails delivered`}
            />
            <StatCard
              title="Open Rate"
              value={`${(workspaceAnalytics.avg_open_rate * 100).toFixed(1)}%`}
              icon={<Eye className="w-5 h-5 text-green-600" />}
              subtitle={`${workspaceAnalytics.total_opened} opens`}
              trend={workspaceAnalytics.avg_open_rate > 0.2 ? 'up' : workspaceAnalytics.avg_open_rate > 0.15 ? 'neutral' : 'down'}
            />
            <StatCard
              title="Click Rate"
              value={`${(workspaceAnalytics.avg_click_rate * 100).toFixed(1)}%`}
              icon={<MousePointerClick className="w-5 h-5 text-orange-600" />}
              subtitle={`${workspaceAnalytics.total_clicked} clicks`}
              trend={workspaceAnalytics.avg_click_rate > 0.05 ? 'up' : workspaceAnalytics.avg_click_rate > 0.02 ? 'neutral' : 'down'}
            />
            <StatCard
              title="Click-to-Open"
              value={`${(workspaceAnalytics.avg_click_to_open_rate * 100).toFixed(1)}%`}
              icon={<Target className="w-5 h-5 text-purple-600" />}
              subtitle="CTOR"
              trend={workspaceAnalytics.avg_click_to_open_rate > 0.15 ? 'up' : workspaceAnalytics.avg_click_to_open_rate > 0.1 ? 'neutral' : 'down'}
            />
          </div>

          {/* Engagement Breakdown */}
          <Card className="p-6">
            <h2 className="text-xl font-semibold mb-6 flex items-center gap-2">
              <BarChart3 className="w-5 h-5 text-orange-600" />
              Engagement Funnel
            </h2>

            <div className="space-y-6">
              <FunnelStep
                label="Delivered"
                count={workspaceAnalytics.total_delivered}
                total={workspaceAnalytics.total_sent}
                color="blue"
              />
              <FunnelStep
                label="Opened"
                count={workspaceAnalytics.total_opened}
                total={workspaceAnalytics.total_sent}
                color="green"
              />
              <FunnelStep
                label="Clicked"
                count={workspaceAnalytics.total_clicked}
                total={workspaceAnalytics.total_sent}
                color="orange"
              />
            </div>

            <div className="mt-6 pt-6 border-t border-border">
              <div className="grid grid-cols-3 gap-4 text-center">
                <div>
                  <p className="text-2xl font-bold text-green-600">
                    {((workspaceAnalytics.total_delivered / workspaceAnalytics.total_sent) * 100).toFixed(1)}%
                  </p>
                  <p className="text-xs text-muted-foreground">Delivery Rate</p>
                </div>
                <div>
                  <p className="text-2xl font-bold text-blue-600">
                    {(workspaceAnalytics.avg_open_rate * 100).toFixed(1)}%
                  </p>
                  <p className="text-xs text-muted-foreground">Avg Open Rate</p>
                </div>
                <div>
                  <p className="text-2xl font-bold text-orange-600">
                    {(workspaceAnalytics.avg_click_rate * 100).toFixed(1)}%
                  </p>
                  <p className="text-xs text-muted-foreground">Avg Click Rate</p>
                </div>
              </div>
            </div>
          </Card>

          {/* Top Performing Content */}
          <Card className="p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-orange-600" />
                Top Performing Content
              </h2>
              <Badge variant="secondary">{contentPerformance.length} items</Badge>
            </div>

            <div className="space-y-3">
              {contentPerformance.length === 0 ? (
                <p className="text-sm text-muted-foreground text-center py-8">
                  No content performance data yet. Include content items in newsletters and track clicks.
                </p>
              ) : (
                contentPerformance.slice(0, 10).map((item, idx) => (
                  <ContentPerformanceRow key={item.content_item_id} item={item} rank={idx + 1} />
                ))
              )}
            </div>
          </Card>

          {/* Performance Benchmarks */}
          <Card className="p-6 bg-gradient-to-r from-orange-50 to-amber-50 dark:from-orange-950/20 dark:to-amber-950/20 border-orange-200">
            <h3 className="font-semibold text-orange-900 dark:text-orange-100 mb-4">
              Industry Benchmarks
            </h3>
            <div className="grid md:grid-cols-3 gap-4 text-sm">
              <BenchmarkItem
                metric="Open Rate"
                yourValue={workspaceAnalytics.avg_open_rate * 100}
                benchmark={20}
                unit="%"
              />
              <BenchmarkItem
                metric="Click Rate"
                yourValue={workspaceAnalytics.avg_click_rate * 100}
                benchmark={2.5}
                unit="%"
              />
              <BenchmarkItem
                metric="CTOR"
                yourValue={workspaceAnalytics.avg_click_to_open_rate * 100}
                benchmark={12}
                unit="%"
              />
            </div>
          </Card>
        </>
      )}
    </div>
  );
}

// Stat Card Component
function StatCard({
  title,
  value,
  icon,
  subtitle,
  trend,
}: {
  title: string;
  value: string | number;
  icon: React.ReactNode;
  subtitle?: string;
  trend?: 'up' | 'down' | 'neutral';
}) {
  const getTrendIcon = () => {
    if (trend === 'up') return <ArrowUpRight className="w-4 h-4 text-green-600" />;
    if (trend === 'down') return <ArrowDownRight className="w-4 h-4 text-red-600" />;
    return <Minus className="w-4 h-4 text-gray-600" />;
  };

  const getTrendColor = () => {
    if (trend === 'up') return 'text-green-600';
    if (trend === 'down') return 'text-red-600';
    return 'text-gray-600';
  };

  return (
    <Card className="p-6">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-sm text-muted-foreground mb-1">{title}</p>
          <p className="text-2xl font-bold">{value}</p>
          {subtitle && <p className="text-xs text-muted-foreground mt-1">{subtitle}</p>}
        </div>
        <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-orange-50 to-amber-50 dark:from-orange-950/30 dark:to-amber-950/30 flex items-center justify-center">
          {icon}
        </div>
      </div>
      {trend && (
        <div className={`flex items-center gap-1 mt-2 text-sm ${getTrendColor()}`}>
          {getTrendIcon()}
          <span className="text-xs">vs. industry avg</span>
        </div>
      )}
    </Card>
  );
}

// Funnel Step Component
function FunnelStep({
  label,
  count,
  total,
  color,
}: {
  label: string;
  count: number;
  total: number;
  color: 'blue' | 'green' | 'orange';
}) {
  const percentage = total > 0 ? (count / total) * 100 : 0;

  const colorClasses = {
    blue: 'bg-blue-500',
    green: 'bg-green-500',
    orange: 'bg-orange-500',
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm font-medium">{label}</span>
        <div className="flex items-center gap-2">
          <span className="text-sm text-muted-foreground">
            {count.toLocaleString()} ({percentage.toFixed(1)}%)
          </span>
        </div>
      </div>
      <div className="relative w-full h-8 bg-muted rounded-lg overflow-hidden">
        <div
          className={`absolute left-0 top-0 h-full ${colorClasses[color]} transition-all duration-500`}
          style={{ width: `${Math.min(percentage, 100)}%` }}
        />
      </div>
    </div>
  );
}

// Content Performance Row Component
function ContentPerformanceRow({ item, rank }: { item: ContentPerformance; rank: number }) {
  const getRankColor = (r: number) => {
    if (r === 1) return 'bg-yellow-500 text-white';
    if (r === 2) return 'bg-gray-400 text-white';
    if (r === 3) return 'bg-orange-600 text-white';
    return 'bg-muted text-muted-foreground';
  };

  return (
    <div className="flex items-center gap-3 p-3 rounded-lg border bg-card hover:shadow-md transition-shadow">
      <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${getRankColor(rank)}`}>
        {rank}
      </div>
      <div className="flex-1 min-w-0">
        <h4 className="font-medium truncate">{item.title}</h4>
        <a
          href={item.url}
          target="_blank"
          rel="noopener noreferrer"
          className="text-xs text-muted-foreground hover:text-orange-600 flex items-center gap-1 truncate"
        >
          {item.url}
          <ExternalLink className="w-3 h-3" />
        </a>
      </div>
      <div className="text-right">
        <p className="text-sm font-semibold">{item.total_clicks} clicks</p>
        <p className="text-xs text-muted-foreground">
          {(item.avg_click_rate * 100).toFixed(1)}% CTR
        </p>
      </div>
      <div className="text-right">
        <Badge variant="secondary">{item.times_included}x included</Badge>
      </div>
    </div>
  );
}

// Benchmark Item Component
function BenchmarkItem({
  metric,
  yourValue,
  benchmark,
  unit,
}: {
  metric: string;
  yourValue: number;
  benchmark: number;
  unit: string;
}) {
  const performance = yourValue >= benchmark ? 'above' : 'below';
  const diff = Math.abs(yourValue - benchmark);

  return (
    <div className="p-3 bg-white dark:bg-orange-900/20 rounded-lg">
      <p className="text-xs text-orange-700 dark:text-orange-300 mb-1">{metric}</p>
      <div className="flex items-baseline gap-2">
        <span className="text-lg font-bold text-orange-900 dark:text-orange-100">
          {yourValue.toFixed(1)}{unit}
        </span>
        <span className="text-xs text-muted-foreground">vs {benchmark}{unit}</span>
      </div>
      <p className={`text-xs mt-1 ${performance === 'above' ? 'text-green-600' : 'text-red-600'}`}>
        {diff.toFixed(1)}{unit} {performance} avg
      </p>
    </div>
  );
}
