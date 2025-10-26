'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { useToast } from '@/lib/hooks/use-toast';
import { useWorkspaceStore } from '@/lib/stores/workspace-store';
import { trendsApi, Trend, TrendSummary } from '@/lib/api/trends';
import { TrendingUp, RefreshCw, Trash2, BarChart3, Calendar } from 'lucide-react';

export function TrendsSettings() {
  const { toast } = useToast();
  const { currentWorkspace } = useWorkspaceStore();
  const [trends, setTrends] = useState<Trend[]>([]);
  const [summary, setSummary] = useState<TrendSummary | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isDetecting, setIsDetecting] = useState(false);

  // Detection settings
  const [daysBack, setDaysBack] = useState(7);
  const [maxTrends, setMaxTrends] = useState(5);
  const [minConfidence, setMinConfidence] = useState(0.6);

  useEffect(() => {
    if (currentWorkspace?.id) {
      loadTrends();
      loadSummary();
    }
  }, [currentWorkspace?.id]);

  const loadTrends = async () => {
    if (!currentWorkspace?.id) return;

    try {
      setIsLoading(true);
      const data = await trendsApi.getActive(currentWorkspace.id, 10);
      setTrends(data.trends);
    } catch (error: any) {
      console.error('Failed to load trends:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const loadSummary = async () => {
    if (!currentWorkspace?.id) return;

    try {
      const data = await trendsApi.getSummary(currentWorkspace.id);
      setSummary(data);
    } catch (error: any) {
      console.error('Failed to load summary:', error);
    }
  };

  const handleDetectTrends = async () => {
    if (!currentWorkspace?.id) return;

    try {
      setIsDetecting(true);
      const result = await trendsApi.detect({
        workspace_id: currentWorkspace.id,
        days_back: daysBack,
        max_trends: maxTrends,
        min_confidence: minConfidence,
      });

      toast({
        title: 'Trends Detected',
        description: result.message,
      });

      setTrends(result.trends);
      loadSummary();
    } catch (error: any) {
      toast({
        title: 'Detection Failed',
        description: error.message || 'Failed to detect trends',
        variant: 'destructive',
      });
    } finally {
      setIsDetecting(false);
    }
  };

  const handleDeleteTrend = async (trendId: string, topic: string) => {
    if (!confirm(`Delete trend "${topic}"?`)) return;

    try {
      await trendsApi.delete(trendId);

      toast({
        title: 'Trend Deleted',
        description: `"${topic}" has been removed`,
      });

      loadTrends();
      loadSummary();
    } catch (error: any) {
      toast({
        title: 'Error',
        description: error.message || 'Failed to delete trend',
        variant: 'destructive',
      });
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'rising':
        return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200';
      case 'peak':
        return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200';
      case 'declining':
        return 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200';
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200';
    }
  };

  return (
    <div className="space-y-6">
      {/* Info */}
      <div className="p-4 bg-purple-50 dark:bg-purple-950 border border-purple-200 dark:border-purple-800 rounded-lg">
        <div className="flex gap-3">
          <TrendingUp className="h-5 w-5 text-purple-600 dark:text-purple-400 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-sm font-medium text-purple-900 dark:text-purple-100">
              AI Trend Detection
            </p>
            <p className="text-sm text-purple-700 dark:text-purple-300 mt-1">
              Automatically detect trending topics across your content sources using machine learning.
              Trends are identified based on frequency, velocity, and cross-source validation.
            </p>
          </div>
        </div>
      </div>

      {/* Summary Stats */}
      {summary && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <Card>
            <CardContent className="pt-6">
              <p className="text-sm text-muted-foreground">Total Trends</p>
              <p className="text-2xl font-bold mt-1">{summary.total_trends}</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <p className="text-sm text-muted-foreground">Active</p>
              <p className="text-2xl font-bold text-green-600 mt-1">{summary.active_trends}</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <p className="text-sm text-muted-foreground">Avg. Strength</p>
              <p className="text-2xl font-bold mt-1">{(summary.avg_strength_score * 100).toFixed(0)}%</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <p className="text-sm text-muted-foreground">Content Analyzed</p>
              <p className="text-2xl font-bold mt-1">{summary.total_content_analyzed}</p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Detection Settings */}
      <Card>
        <CardContent className="pt-6 space-y-4">
          <h3 className="font-semibold mb-3">Detection Settings</h3>
          <div className="grid md:grid-cols-3 gap-4">
            <div>
              <label className="text-sm font-medium mb-1 block">Days Back</label>
              <Input
                type="number"
                min="1"
                max="30"
                value={daysBack}
                onChange={(e) => setDaysBack(parseInt(e.target.value))}
              />
              <p className="text-xs text-muted-foreground mt-1">Analyze content from last N days</p>
            </div>
            <div>
              <label className="text-sm font-medium mb-1 block">Max Trends</label>
              <Input
                type="number"
                min="1"
                max="20"
                value={maxTrends}
                onChange={(e) => setMaxTrends(parseInt(e.target.value))}
              />
              <p className="text-xs text-muted-foreground mt-1">Maximum trends to detect</p>
            </div>
            <div>
              <label className="text-sm font-medium mb-1 block">Min. Confidence</label>
              <Input
                type="number"
                min="0"
                max="1"
                step="0.1"
                value={minConfidence}
                onChange={(e) => setMinConfidence(parseFloat(e.target.value))}
              />
              <p className="text-xs text-muted-foreground mt-1">Minimum confidence (0.0-1.0)</p>
            </div>
          </div>
          <Button onClick={handleDetectTrends} disabled={isDetecting}>
            <RefreshCw className={`h-4 w-4 mr-2 ${isDetecting ? 'animate-spin' : ''}`} />
            {isDetecting ? 'Detecting...' : 'Detect Trends Now'}
          </Button>
        </CardContent>
      </Card>

      {/* Trends List */}
      <div>
        <h3 className="text-sm font-medium mb-3">Active Trends ({trends.length})</h3>
        {isLoading && trends.length === 0 ? (
          <Card>
            <CardContent className="py-12 text-center text-muted-foreground">
              Loading trends...
            </CardContent>
          </Card>
        ) : trends.length === 0 ? (
          <Card>
            <CardContent className="py-12 text-center">
              <TrendingUp className="h-12 w-12 mx-auto text-muted-foreground mb-2" />
              <p className="text-muted-foreground mb-4">No trends detected yet</p>
              <Button onClick={handleDetectTrends} disabled={isDetecting}>
                <RefreshCw className="h-4 w-4 mr-2" />
                Detect Trends
              </Button>
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-3">
            {trends.map((trend) => (
              <Card key={trend.id}>
                <CardContent className="pt-6">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <h4 className="font-semibold">{trend.topic}</h4>
                        <Badge className={getStatusColor(trend.status)}>
                          {trend.status}
                        </Badge>
                        <Badge variant="outline">
                          {(trend.strength_score * 100).toFixed(0)}% strength
                        </Badge>
                      </div>

                      {trend.explanation && (
                        <p className="text-sm text-muted-foreground mb-3">{trend.explanation}</p>
                      )}

                      <div className="flex flex-wrap gap-2 mb-3">
                        {trend.keywords.slice(0, 5).map((keyword, idx) => (
                          <Badge key={idx} variant="secondary">
                            {keyword}
                          </Badge>
                        ))}
                      </div>

                      <div className="flex items-center gap-4 text-xs text-muted-foreground">
                        <span className="flex items-center gap-1">
                          <BarChart3 className="h-3 w-3" />
                          {trend.mention_count} items
                        </span>
                        <span className="flex items-center gap-1">
                          <Calendar className="h-3 w-3" />
                          First seen {trend.first_seen ? new Date(trend.first_seen).toLocaleDateString() : 'Unknown'}
                        </span>
                        <span>{trend.sources.join(', ')}</span>
                      </div>
                    </div>

                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleDeleteTrend(trend.id, trend.topic)}
                    >
                      <Trash2 className="h-4 w-4 text-red-600" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
