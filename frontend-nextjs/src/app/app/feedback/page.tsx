'use client';

import { useState, useEffect } from 'react';
import { useWorkspace } from '@/lib/hooks/use-workspace';
import { feedbackApi, FeedbackAnalytics, SourceQualityScore, ContentPreferences } from '@/lib/api/feedback';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { useToast } from '@/lib/hooks/use-toast';
import {
  TrendingUp,
  TrendingDown,
  Star,
  ThumbsUp,
  ThumbsDown,
  Target,
  Zap,
  BarChart3,
  RefreshCw,
  Loader2,
  CheckCircle2,
  XCircle,
  MinusCircle,
  Lightbulb,
} from 'lucide-react';

export default function FeedbackPage() {
  const { workspace } = useWorkspace();
  const { toast } = useToast();

  const [loading, setLoading] = useState(false);
  const [analytics, setAnalytics] = useState<FeedbackAnalytics | null>(null);
  const [sourceQuality, setSourceQuality] = useState<SourceQualityScore[]>([]);
  const [preferences, setPreferences] = useState<ContentPreferences | null>(null);
  const [applyingLearning, setApplyingLearning] = useState(false);

  useEffect(() => {
    if (workspace?.id) {
      loadFeedbackData();
    }
  }, [workspace?.id]);

  const loadFeedbackData = async () => {
    if (!workspace?.id) return;

    try {
      setLoading(true);

      const [analyticsData, sourceData, prefsData] = await Promise.all([
        feedbackApi.getAnalytics(workspace.id),
        feedbackApi.getSourceQuality(workspace.id),
        feedbackApi.getPreferences(workspace.id).catch(() => null),
      ]);

      setAnalytics(analyticsData);
      setSourceQuality(sourceData.sources);
      setPreferences(prefsData);
    } catch (error: any) {
      toast({
        title: 'Failed to load feedback data',
        description: error.message,
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleApplyLearning = async () => {
    if (!workspace?.id) return;

    try {
      setApplyingLearning(true);

      const result = await feedbackApi.applyLearning(workspace.id);

      toast({
        title: '✨ Learning applied!',
        description: `${result.preferences_applied} content preferences have been applied to future content selection.`,
      });

      await loadFeedbackData();
    } catch (error: any) {
      toast({
        title: 'Failed to apply learning',
        description: error.message,
        variant: 'destructive',
      });
    } finally {
      setApplyingLearning(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <Loader2 className="w-8 h-8 animate-spin text-orange-600" />
      </div>
    );
  }

  if (!analytics) {
    return (
      <div className="container mx-auto p-6">
        <Card className="p-12 text-center">
          <Lightbulb className="w-16 h-16 text-muted-foreground mx-auto mb-4" />
          <h2 className="text-2xl font-semibold mb-2">No Feedback Data Yet</h2>
          <p className="text-muted-foreground mb-6">
            Start rating content items and newsletters to help the AI learn your preferences.
          </p>
          <Button onClick={loadFeedbackData}>
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh
          </Button>
        </Card>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-orange-600 to-amber-600 bg-clip-text text-transparent">
            Feedback & Learning
          </h1>
          <p className="text-muted-foreground mt-2">
            Track feedback and help AI learn your content preferences
          </p>
        </div>

        <div className="flex gap-2">
          <Button variant="outline" onClick={loadFeedbackData} disabled={loading}>
            <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
          <Button
            onClick={handleApplyLearning}
            disabled={applyingLearning || analytics.total_item_feedback < 10}
            className="bg-gradient-to-r from-orange-600 to-amber-600"
          >
            {applyingLearning ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Applying...
              </>
            ) : (
              <>
                <Zap className="w-4 h-4 mr-2" />
                Apply Learning
              </>
            )}
          </Button>
        </div>
      </div>

      {/* Overview Stats */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="Total Feedback"
          value={analytics.total_item_feedback + analytics.total_newsletter_feedback}
          icon={<BarChart3 className="w-5 h-5 text-orange-600" />}
          trend="+12%"
          trendUp={true}
        />
        <StatCard
          title="Item Feedback"
          value={analytics.total_item_feedback}
          icon={<ThumbsUp className="w-5 h-5 text-green-600" />}
          subtitle={`${analytics.avg_newsletter_rating.toFixed(1)} avg rating`}
        />
        <StatCard
          title="Newsletter Rating"
          value={`${analytics.avg_newsletter_rating.toFixed(1)}/5`}
          icon={<Star className="w-5 h-5 text-yellow-600" />}
          subtitle={`${analytics.total_newsletter_feedback} rated`}
        />
        <StatCard
          title="Learning Applied"
          value={analytics.learning_applied_count}
          icon={<Zap className="w-5 h-5 text-purple-600" />}
          subtitle={
            analytics.last_learning_applied_at
              ? `Last: ${new Date(analytics.last_learning_applied_at).toLocaleDateString()}`
              : 'Never applied'
          }
        />
      </div>

      {/* Source Quality Scores */}
      <Card className="p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold flex items-center gap-2">
            <Target className="w-5 h-5 text-orange-600" />
            Source Quality Scores
          </h2>
          <Badge variant="secondary">
            {sourceQuality.length} sources analyzed
          </Badge>
        </div>

        <div className="space-y-4">
          {sourceQuality.length === 0 ? (
            <p className="text-sm text-muted-foreground text-center py-8">
              No source quality data yet. Start rating content to build quality scores.
            </p>
          ) : (
            sourceQuality.map((source) => (
              <SourceQualityRow key={source.source_type} source={source} />
            ))
          )}
        </div>
      </Card>

      {/* Content Preferences */}
      {preferences && (
        <div className="grid gap-6 md:grid-cols-2">
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <ThumbsUp className="w-5 h-5 text-green-600" />
              Preferred Topics
            </h3>
            <div className="space-y-2">
              {preferences.preferred_topics.length > 0 ? (
                preferences.preferred_topics.slice(0, 5).map((topic, idx) => (
                  <div key={idx} className="flex items-center justify-between">
                    <span className="text-sm">{topic.topic}</span>
                    <Badge variant="secondary">{(topic.score * 100).toFixed(0)}%</Badge>
                  </div>
                ))
              ) : (
                <p className="text-sm text-muted-foreground">Not enough data yet</p>
              )}
            </div>
          </Card>

          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <ThumbsDown className="w-5 h-5 text-red-600" />
              Avoided Topics
            </h3>
            <div className="space-y-2">
              {preferences.avoided_topics.length > 0 ? (
                preferences.avoided_topics.slice(0, 5).map((topic, idx) => (
                  <div key={idx} className="flex items-center justify-between">
                    <span className="text-sm">{topic.topic}</span>
                    <Badge variant="outline" className="border-red-200 text-red-700">
                      Avoid
                    </Badge>
                  </div>
                ))
              ) : (
                <p className="text-sm text-muted-foreground">Not enough data yet</p>
              )}
            </div>
          </Card>
        </div>
      )}

      {/* Learning Status */}
      {analytics.total_item_feedback < 10 && (
        <Card className="p-6 bg-amber-50 dark:bg-amber-950/20 border-amber-200">
          <div className="flex items-start gap-3">
            <Lightbulb className="w-5 h-5 text-amber-600 mt-0.5" />
            <div className="flex-1">
              <h3 className="font-semibold text-amber-900 dark:text-amber-100 mb-1">
                Keep rating content to improve learning
              </h3>
              <p className="text-sm text-amber-700 dark:text-amber-300 mb-3">
                You need at least 10 feedback items to apply learning. Current: {analytics.total_item_feedback}/10
              </p>
              <Progress
                value={(analytics.total_item_feedback / 10) * 100}
                className="h-2"
              />
            </div>
          </div>
        </Card>
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
  trendUp,
}: {
  title: string;
  value: string | number;
  icon: React.ReactNode;
  subtitle?: string;
  trend?: string;
  trendUp?: boolean;
}) {
  return (
    <Card className="p-6">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-sm text-muted-foreground mb-1">{title}</p>
          <p className="text-2xl font-bold">{value}</p>
          {subtitle && (
            <p className="text-xs text-muted-foreground mt-1">{subtitle}</p>
          )}
        </div>
        <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-orange-50 to-amber-50 dark:from-orange-950/30 dark:to-amber-950/30 flex items-center justify-center">
          {icon}
        </div>
      </div>
      {trend && (
        <div className={`flex items-center gap-1 mt-2 text-sm ${trendUp ? 'text-green-600' : 'text-red-600'}`}>
          {trendUp ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
          <span>{trend}</span>
        </div>
      )}
    </Card>
  );
}

// Source Quality Row Component
function SourceQualityRow({ source }: { source: SourceQualityScore }) {
  const getQualityColor = (score: number) => {
    if (score >= 0.8) return 'text-green-600 bg-green-50 border-green-200';
    if (score >= 0.6) return 'text-blue-600 bg-blue-50 border-blue-200';
    if (score >= 0.4) return 'text-yellow-600 bg-yellow-50 border-yellow-200';
    return 'text-red-600 bg-red-50 border-red-200';
  };

  const getQualityIcon = (score: number) => {
    if (score >= 0.6) return <CheckCircle2 className="w-4 h-4" />;
    if (score >= 0.4) return <MinusCircle className="w-4 h-4" />;
    return <XCircle className="w-4 h-4" />;
  };

  return (
    <div className="flex items-center justify-between p-4 rounded-lg border bg-card">
      <div className="flex items-center gap-3 flex-1">
        <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${getQualityColor(source.quality_score)}`}>
          {getQualityIcon(source.quality_score)}
        </div>
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            <span className="font-medium capitalize">{source.source_type}</span>
            <Badge variant="outline" className="text-xs">
              {(source.quality_score * 100).toFixed(0)}% quality
            </Badge>
          </div>
          <div className="flex gap-4 text-xs text-muted-foreground">
            <span>{source.total_feedback_count} ratings</span>
            <span>{source.positive_count} positive</span>
            <span>{source.inclusion_rate.toFixed(0)}% included</span>
          </div>
        </div>
      </div>

      <div className="w-32">
        <Progress value={source.quality_score * 100} className="h-2" />
      </div>
    </div>
  );
}
