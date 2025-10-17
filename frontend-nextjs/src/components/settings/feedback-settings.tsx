'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { useToast } from '@/lib/hooks/use-toast';
import { useWorkspaceStore } from '@/lib/stores/workspace-store';
import { feedbackApi, FeedbackAnalytics, SourceQualityScore, ContentPreferences } from '@/lib/api/feedback';
import { Heart, ThumbsUp, ThumbsDown, RefreshCw, Brain, Star } from 'lucide-react';

export function FeedbackSettings() {
  const { toast } = useToast();
  const { currentWorkspace } = useWorkspaceStore();
  const [analytics, setAnalytics] = useState<FeedbackAnalytics | null>(null);
  const [sourceQuality, setSourceQuality] = useState<SourceQualityScore[]>([]);
  const [preferences, setPreferences] = useState<ContentPreferences | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isApplying, setIsApplying] = useState(false);

  useEffect(() => {
    if (currentWorkspace?.id) {
      loadData();
    }
  }, [currentWorkspace?.id]);

  const loadData = async () => {
    if (!currentWorkspace?.id) return;

    try {
      setIsLoading(true);
      const [analyticsData, sourceData, prefData] = await Promise.all([
        feedbackApi.getAnalytics(currentWorkspace.id).catch(() => null),
        feedbackApi.getSourceQuality(currentWorkspace.id).catch(() => ({ sources: [] })),
        feedbackApi.getPreferences(currentWorkspace.id).catch(() => null),
      ]);

      setAnalytics(analyticsData);
      setSourceQuality(sourceData?.sources || []);
      setPreferences(prefData);
    } catch (error: any) {
      console.error('Failed to load feedback data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleApplyLearning = async () => {
    if (!currentWorkspace?.id) return;

    try {
      setIsApplying(true);
      const result = await feedbackApi.applyLearning(currentWorkspace.id);

      toast({
        title: 'Learning Applied',
        description: result.message,
      });

      loadData();
    } catch (error: any) {
      toast({
        title: 'Failed to Apply Learning',
        description: error.message || 'Failed to apply learned preferences',
        variant: 'destructive',
      });
    } finally {
      setIsApplying(false);
    }
  };

  const getQualityColor = (score: number) => {
    if (score >= 0.7) return 'text-green-600';
    if (score >= 0.4) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <div className="space-y-6">
      {/* Info */}
      <div className="p-4 bg-purple-50 dark:bg-purple-950 border border-purple-200 dark:border-purple-800 rounded-lg">
        <div className="flex gap-3">
          <Brain className="h-5 w-5 text-purple-600 dark:text-purple-400 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-sm font-medium text-purple-900 dark:text-purple-100">
              AI Feedback Loop & Learning
            </p>
            <p className="text-sm text-purple-700 dark:text-purple-300 mt-1">
              The AI learns from your edits and preferences to improve future newsletter generation.
              Rate content, and the system will automatically prioritize what you like.
            </p>
          </div>
        </div>
      </div>

      {/* Summary Stats */}
      {analytics && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center gap-2 mb-2">
                <ThumbsUp className="h-4 w-4 text-muted-foreground" />
                <p className="text-sm text-muted-foreground">Item Feedback</p>
              </div>
              <p className="text-2xl font-bold">{analytics.total_item_feedback}</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center gap-2 mb-2">
                <Star className="h-4 w-4 text-muted-foreground" />
                <p className="text-sm text-muted-foreground">Newsletter Ratings</p>
              </div>
              <p className="text-2xl font-bold">{analytics.total_newsletter_feedback}</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center gap-2 mb-2">
                <Star className="h-4 w-4 text-yellow-500" />
                <p className="text-sm text-muted-foreground">Avg. Rating</p>
              </div>
              <p className="text-2xl font-bold">{analytics.avg_newsletter_rating.toFixed(1)}/5</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center gap-2 mb-2">
                <Brain className="h-4 w-4 text-muted-foreground" />
                <p className="text-sm text-muted-foreground">Learning Applied</p>
              </div>
              <p className="text-2xl font-bold">{analytics.learning_applied_count}x</p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Apply Learning */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <h3 className="font-semibold mb-2">Apply Learned Preferences</h3>
              <p className="text-sm text-muted-foreground mb-4">
                Update content filtering and ranking based on your feedback history.
                This will prioritize sources and topics you've liked in the past.
              </p>
            </div>
          </div>
          <Button onClick={handleApplyLearning} disabled={isApplying}>
            <RefreshCw className={`h-4 w-4 mr-2 ${isApplying ? 'animate-spin' : ''}`} />
            {isApplying ? 'Applying...' : 'Apply Learning Now'}
          </Button>
          {analytics?.last_learning_applied_at && (
            <p className="text-xs text-muted-foreground mt-2">
              Last applied: {new Date(analytics.last_learning_applied_at).toLocaleString()}
            </p>
          )}
        </CardContent>
      </Card>

      {/* Source Quality */}
      {sourceQuality.length > 0 && (
        <div>
          <h3 className="text-sm font-medium mb-3">Source Quality Scores</h3>
          <Card>
            <CardContent className="pt-6">
              <div className="space-y-4">
                {sourceQuality.map((source) => (
                  <div key={source.source_type} className="flex items-center justify-between pb-3 border-b last:border-0">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <p className="font-medium">{source.source_type.toUpperCase()}</p>
                        <Badge variant="outline">
                          {source.total_feedback_count} feedback
                        </Badge>
                      </div>
                      <div className="flex items-center gap-4 text-xs text-muted-foreground">
                        <span className="flex items-center gap-1">
                          <ThumbsUp className="h-3 w-3 text-green-600" />
                          {source.positive_count}
                        </span>
                        <span className="flex items-center gap-1">
                          <ThumbsDown className="h-3 w-3 text-red-600" />
                          {source.negative_count}
                        </span>
                        <span>{(source.inclusion_rate * 100).toFixed(0)}% inclusion</span>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className={`text-2xl font-bold ${getQualityColor(source.quality_score)}`}>
                        {(source.quality_score * 100).toFixed(0)}%
                      </p>
                      <p className="text-xs text-muted-foreground">Quality</p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Preferences */}
      {preferences && (
        <div className="grid md:grid-cols-2 gap-4">
          {/* Preferred Topics */}
          {preferences.preferred_topics.length > 0 && (
            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center gap-2 mb-3">
                  <Heart className="h-4 w-4 text-green-600" />
                  <h3 className="font-semibold">Preferred Topics</h3>
                </div>
                <div className="flex flex-wrap gap-2">
                  {preferences.preferred_topics.slice(0, 10).map((topic, idx) => (
                    <Badge key={idx} variant="secondary">
                      {topic.topic} ({(topic.score * 100).toFixed(0)}%)
                    </Badge>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Avoided Topics */}
          {preferences.avoided_topics.length > 0 && (
            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center gap-2 mb-3">
                  <ThumbsDown className="h-4 w-4 text-red-600" />
                  <h3 className="font-semibold">Avoided Topics</h3>
                </div>
                <div className="flex flex-wrap gap-2">
                  {preferences.avoided_topics.slice(0, 10).map((topic, idx) => (
                    <Badge key={idx} variant="outline">
                      {topic.topic}
                    </Badge>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      )}

      {/* Empty State */}
      {!isLoading && !analytics && (
        <Card>
          <CardContent className="py-12 text-center">
            <Brain className="h-12 w-12 mx-auto text-muted-foreground mb-2" />
            <p className="text-muted-foreground mb-2">No feedback data yet</p>
            <p className="text-sm text-muted-foreground">
              Start rating content items and newsletters to train the AI
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
