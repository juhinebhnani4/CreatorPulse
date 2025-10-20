'use client';

import { useState, useEffect } from 'react';
import { useWorkspace } from '@/lib/hooks/use-workspace';
import { trendsApi, Trend, TrendSummary, DetectTrendsRequest } from '@/lib/api/trends';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { useToast } from '@/lib/hooks/use-toast';
import {
  TrendingUp,
  Flame,
  Sparkles,
  Target,
  RefreshCw,
  Loader2,
  BarChart3,
  Clock,
  Layers,
  Search,
  ChevronRight,
  AlertCircle,
} from 'lucide-react';

export default function TrendsPage() {
  const { workspace } = useWorkspace();
  const { toast } = useToast();

  const [loading, setLoading] = useState(false);
  const [detecting, setDetecting] = useState(false);
  const [trends, setTrends] = useState<Trend[]>([]);
  const [summary, setSummary] = useState<TrendSummary | null>(null);

  // Detection parameters
  const [daysBack, setDaysBack] = useState(7);
  const [maxTrends, setMaxTrends] = useState(5);
  const [minConfidence, setMinConfidence] = useState(0.6);

  useEffect(() => {
    if (workspace?.id) {
      loadTrends();
      loadSummary();
    }
  }, [workspace?.id]);

  const loadTrends = async () => {
    if (!workspace?.id) return;

    try {
      setLoading(true);
      const data = await trendsApi.getActive(workspace.id, 10);
      setTrends(data.trends);
    } catch (error: any) {
      console.log('No active trends yet');
      setTrends([]);
    } finally {
      setLoading(false);
    }
  };

  const loadSummary = async () => {
    if (!workspace?.id) return;

    try {
      const data = await trendsApi.getSummary(workspace.id, daysBack);
      setSummary(data);
    } catch (error: any) {
      console.log('No trend summary yet');
    }
  };

  const handleDetectTrends = async () => {
    if (!workspace?.id) return;

    try {
      setDetecting(true);

      const request: DetectTrendsRequest = {
        workspace_id: workspace.id,
        days_back: daysBack,
        max_trends: maxTrends,
        min_confidence: minConfidence,
      };

      const result = await trendsApi.detect(request);

      toast({
        title: '🔥 Trends detected!',
        description: `Found ${result.trends.length} trends from ${result.analysis_summary.content_items_analyzed} content items.`,
      });

      setTrends(result.trends);
      await loadSummary();
    } catch (error: any) {
      toast({
        title: 'Detection failed',
        description: error.message,
        variant: 'destructive',
      });
    } finally {
      setDetecting(false);
    }
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-orange-600 to-amber-600 bg-clip-text text-transparent">
            Trend Detection
          </h1>
          <p className="text-muted-foreground mt-2">
            Discover emerging topics and patterns in your content
          </p>
        </div>

        <div className="flex gap-2">
          <Button variant="outline" onClick={loadTrends} disabled={loading}>
            <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>
      </div>

      {/* Detection Controls */}
      <Card className="p-6">
        <div className="flex items-start justify-between mb-6">
          <div>
            <h2 className="text-xl font-semibold flex items-center gap-2 mb-2">
              <Search className="w-5 h-5 text-orange-600" />
              Detect New Trends
            </h2>
            <p className="text-sm text-muted-foreground">
              Analyze recent content using AI-powered trend detection
            </p>
          </div>
        </div>

        <div className="grid gap-4 md:grid-cols-3 mb-4">
          <div>
            <Label htmlFor="daysBack">Days Back</Label>
            <Input
              id="daysBack"
              type="number"
              min={1}
              max={30}
              value={daysBack}
              onChange={(e) => setDaysBack(parseInt(e.target.value) || 7)}
            />
            <p className="text-xs text-muted-foreground mt-1">1-30 days</p>
          </div>

          <div>
            <Label htmlFor="maxTrends">Max Trends</Label>
            <Input
              id="maxTrends"
              type="number"
              min={1}
              max={20}
              value={maxTrends}
              onChange={(e) => setMaxTrends(parseInt(e.target.value) || 5)}
            />
            <p className="text-xs text-muted-foreground mt-1">1-20 trends</p>
          </div>

          <div>
            <Label htmlFor="minConfidence">Min Confidence</Label>
            <Input
              id="minConfidence"
              type="number"
              min={0}
              max={1}
              step={0.1}
              value={minConfidence}
              onChange={(e) => setMinConfidence(parseFloat(e.target.value) || 0.6)}
            />
            <p className="text-xs text-muted-foreground mt-1">0.0-1.0</p>
          </div>
        </div>

        <Button
          onClick={handleDetectTrends}
          disabled={detecting}
          className="bg-gradient-to-r from-orange-600 to-amber-600"
        >
          {detecting ? (
            <>
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              Analyzing...
            </>
          ) : (
            <>
              <Sparkles className="w-4 h-4 mr-2" />
              Detect Trends
            </>
          )}
        </Button>
      </Card>

      {/* Summary Stats */}
      {summary && (
        <div className="grid gap-4 md:grid-cols-4">
          <StatCard
            title="Total Trends"
            value={summary.total_trends}
            icon={<BarChart3 className="w-5 h-5 text-orange-600" />}
          />
          <StatCard
            title="Active Trends"
            value={summary.active_trends}
            icon={<Flame className="w-5 h-5 text-red-600" />}
          />
          <StatCard
            title="Avg Strength"
            value={`${(summary.avg_strength_score * 100).toFixed(0)}%`}
            icon={<Target className="w-5 h-5 text-green-600" />}
          />
          <StatCard
            title="Content Analyzed"
            value={summary.total_content_analyzed}
            icon={<Layers className="w-5 h-5 text-blue-600" />}
          />
        </div>
      )}

      {/* Trends List */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-semibold">
            {trends.length > 0 ? `${trends.length} Active Trends` : 'No Active Trends'}
          </h2>
          {trends.length > 0 && (
            <Badge variant="secondary">{trends.filter((t) => t.status === 'rising').length} rising</Badge>
          )}
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="w-8 h-8 animate-spin text-orange-600" />
          </div>
        ) : trends.length === 0 ? (
          <Card className="p-12 text-center">
            <AlertCircle className="w-16 h-16 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-xl font-semibold mb-2">No Trends Detected Yet</h3>
            <p className="text-muted-foreground mb-6">
              Click &quot;Detect Trends&quot; above to analyze your recent content and discover emerging topics.
            </p>
          </Card>
        ) : (
          trends.map((trend) => <TrendCard key={trend.id} trend={trend} />)
        )}
      </div>
    </div>
  );
}

// Stat Card Component
function StatCard({
  title,
  value,
  icon,
}: {
  title: string;
  value: string | number;
  icon: React.ReactNode;
}) {
  return (
    <Card className="p-6">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm text-muted-foreground mb-1">{title}</p>
          <p className="text-2xl font-bold">{value}</p>
        </div>
        <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-orange-50 to-amber-50 dark:from-orange-950/30 dark:to-amber-950/30 flex items-center justify-center">
          {icon}
        </div>
      </div>
    </Card>
  );
}

// Trend Card Component
function TrendCard({ trend }: { trend: Trend }) {
  const getStrengthColor = (score: number) => {
    if (score >= 0.8) return 'text-red-600 bg-red-50 border-red-200';
    if (score >= 0.6) return 'text-orange-600 bg-orange-50 border-orange-200';
    return 'text-yellow-600 bg-yellow-50 border-yellow-200';
  };

  const getStrengthIcon = (score: number) => {
    if (score >= 0.8) return <Flame className="w-5 h-5" />;
    if (score >= 0.6) return <TrendingUp className="w-5 h-5" />;
    return <Sparkles className="w-5 h-5" />;
  };

  const getStrengthLabel = (score: number) => {
    if (score >= 0.8) return 'Hot';
    if (score >= 0.6) return 'Growing';
    return 'Emerging';
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'rising':
        return 'bg-green-500';
      case 'peak':
        return 'bg-red-500';
      case 'declining':
        return 'bg-yellow-500';
      default:
        return 'bg-gray-500';
    }
  };

  return (
    <Card className="p-6 hover:shadow-lg transition-shadow">
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-2">
            <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${getStrengthColor(trend.strength_score)}`}>
              {getStrengthIcon(trend.strength_score)}
            </div>
            <div className="flex-1">
              <h3 className="text-xl font-semibold">{trend.topic}</h3>
              <div className="flex items-center gap-2 mt-1">
                <Badge variant="secondary">{getStrengthLabel(trend.strength_score)}</Badge>
                <Badge variant="outline" className="capitalize">
                  {trend.status}
                </Badge>
                <span className={`w-2 h-2 rounded-full ${getStatusColor(trend.status)}`} />
              </div>
            </div>
          </div>
        </div>

        <div className="text-right">
          <div className="text-2xl font-bold text-orange-600">
            {(trend.strength_score * 100).toFixed(0)}%
          </div>
          <p className="text-xs text-muted-foreground">Strength</p>
        </div>
      </div>

      {/* Explanation */}
      {trend.explanation && (
        <p className="text-sm text-muted-foreground mb-4 p-3 bg-muted rounded-lg">
          {trend.explanation}
        </p>
      )}

      {/* Keywords */}
      <div className="mb-4">
        <p className="text-xs font-medium text-muted-foreground mb-2">Keywords</p>
        <div className="flex flex-wrap gap-2">
          {trend.keywords.slice(0, 10).map((keyword, idx) => (
            <Badge key={idx} variant="outline" className="text-xs">
              {keyword}
            </Badge>
          ))}
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-4 gap-4 pt-4 border-t border-border">
        <div>
          <p className="text-xs text-muted-foreground mb-1">Mentions</p>
          <p className="text-sm font-semibold">{trend.content_count}</p>
        </div>
        <div>
          <p className="text-xs text-muted-foreground mb-1">Sources</p>
          <p className="text-sm font-semibold">{trend.sources.length}</p>
        </div>
        <div>
          <p className="text-xs text-muted-foreground mb-1">Velocity</p>
          <p className="text-sm font-semibold">{trend.velocity > 0 ? '+' : ''}{(trend.velocity * 100).toFixed(0)}%</p>
        </div>
        <div>
          <p className="text-xs text-muted-foreground mb-1">First Seen</p>
          <p className="text-sm font-semibold flex items-center gap-1">
            <Clock className="w-3 h-3" />
            {new Date(trend.first_seen).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })}
          </p>
        </div>
      </div>

      {/* Sources */}
      <div className="mt-4 pt-4 border-t border-border">
        <p className="text-xs font-medium text-muted-foreground mb-2">From Sources</p>
        <div className="flex flex-wrap gap-2">
          {trend.sources.map((source, idx) => (
            <Badge key={idx} variant="secondary" className="text-xs capitalize">
              {source}
            </Badge>
          ))}
        </div>
      </div>

      {/* View Details */}
      <Button variant="ghost" size="sm" className="w-full mt-4">
        View {trend.key_content_ids.length} Related Items
        <ChevronRight className="w-4 h-4 ml-2" />
      </Button>
    </Card>
  );
}
