'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { useToast } from '@/lib/hooks/use-toast';
import { useWorkspaceStore } from '@/lib/stores/workspace-store';
import { styleApi, StyleProfile, StyleProfileSummary } from '@/lib/api/style';
import { Sparkles, Trash2, FileText, Plus, X, AlertCircle } from 'lucide-react';

export function StyleSettings() {
  const { toast } = useToast();
  const { currentWorkspace } = useWorkspaceStore();
  const [summary, setSummary] = useState<StyleProfileSummary | null>(null);
  const [profile, setProfile] = useState<StyleProfile | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isTraining, setIsTraining] = useState(false);

  // Training form
  const [samples, setSamples] = useState<string[]>(['']);
  const [showTraining, setShowTraining] = useState(false);

  useEffect(() => {
    if (currentWorkspace?.id) {
      loadSummary();
    }
  }, [currentWorkspace?.id]);

  const loadSummary = async () => {
    if (!currentWorkspace?.id) return;

    try {
      const data = await styleApi.getSummary(currentWorkspace.id);
      setSummary(data);

      if (data.has_profile) {
        // Load full profile if it exists
        const fullProfile = await styleApi.getProfile(currentWorkspace.id);
        setProfile(fullProfile);
      }
    } catch (error: any) {
      console.error('Failed to load style summary:', error);
    }
  };

  const handleAddSample = () => {
    setSamples([...samples, '']);
  };

  const handleRemoveSample = (index: number) => {
    setSamples(samples.filter((_, i) => i !== index));
  };

  const handleSampleChange = (index: number, value: string) => {
    const newSamples = [...samples];
    newSamples[index] = value;
    setSamples(newSamples);
  };

  const handleTrain = async () => {
    if (!currentWorkspace?.id) return;

    // Filter out empty samples
    const validSamples = samples.filter((s) => s.trim().length >= 50);

    if (validSamples.length < 5) {
      toast({
        title: 'Not Enough Samples',
        description: 'Please provide at least 5 newsletter samples (minimum 50 words each)',
        variant: 'destructive',
      });
      return;
    }

    try {
      setIsTraining(true);
      const result = await styleApi.train({
        workspace_id: currentWorkspace.id,
        samples: validSamples,
        retrain: summary?.has_profile || false,
      });

      toast({
        title: 'Style Profile Trained',
        description: `Successfully trained on ${validSamples.length} samples`,
      });

      setProfile(result.profile);
      setSummary({
        has_profile: true,
        sample_count: validSamples.length,
        tone: result.profile.tone,
        formality: result.profile.formality,
        last_updated: result.profile.updated_at,
      });

      setShowTraining(false);
      setSamples(['']);
    } catch (error: any) {
      toast({
        title: 'Training Failed',
        description: error.message || 'Failed to train style profile',
        variant: 'destructive',
      });
    } finally {
      setIsTraining(false);
    }
  };

  const handleDelete = async () => {
    if (!currentWorkspace?.id || !profile) return;

    if (!confirm('Delete your style profile? Your newsletters will use the default writing style.')) {
      return;
    }

    try {
      setIsLoading(true);
      await styleApi.delete(currentWorkspace.id);

      toast({
        title: 'Style Profile Deleted',
        description: 'Your newsletters will now use the default writing style',
      });

      setProfile(null);
      setSummary({ has_profile: false, sample_count: 0 });
    } catch (error: any) {
      toast({
        title: 'Error',
        description: error.message || 'Failed to delete style profile',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Info */}
      <div className="p-4 bg-blue-50 dark:bg-blue-950 border border-blue-200 dark:border-blue-800 rounded-lg">
        <div className="flex gap-3">
          <Sparkles className="h-5 w-5 text-blue-600 dark:text-blue-400 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-sm font-medium text-blue-900 dark:text-blue-100">
              AI Writing Style Training
            </p>
            <p className="text-sm text-blue-700 dark:text-blue-300 mt-1">
              Train the AI to write newsletters in your unique voice. Provide 5+ past newsletter samples,
              and the AI will learn your tone, vocabulary, and writing patterns.
            </p>
          </div>
        </div>
      </div>

      {/* Current Profile Status */}
      {summary?.has_profile && profile ? (
        <Card>
          <CardContent className="pt-6">
            <div className="space-y-4">
              <div className="flex items-start justify-between">
                <div className="flex items-start gap-3">
                  <div className="p-2 bg-primary/10 rounded-lg">
                    <Sparkles className="h-5 w-5 text-primary" />
                  </div>
                  <div>
                    <h3 className="font-semibold mb-1">Style Profile Active</h3>
                    <p className="text-sm text-muted-foreground">
                      Trained on {summary.sample_count} newsletter samples
                    </p>
                  </div>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleDelete}
                  disabled={isLoading}
                >
                  <Trash2 className="h-4 w-4 text-red-600" />
                </Button>
              </div>

              {/* Profile Details */}
              <div className="grid grid-cols-2 gap-4 pt-4 border-t">
                <div>
                  <p className="text-sm text-muted-foreground">Tone</p>
                  <Badge variant="secondary" className="mt-1">{profile.tone}</Badge>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Formality</p>
                  <Badge variant="secondary" className="mt-1">{profile.formality}</Badge>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Avg. Sentence Length</p>
                  <p className="font-medium mt-1">{profile.avg_sentence_length} words</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Vocabulary Level</p>
                  <Badge variant="secondary" className="mt-1">{profile.vocabulary_level}</Badge>
                </div>
                {profile.emoji_usage && (
                  <div>
                    <p className="text-sm text-muted-foreground">Emoji Usage</p>
                    <Badge variant="secondary" className="mt-1">{profile.emoji_usage}</Badge>
                  </div>
                )}
              </div>

              {/* Favorite Phrases */}
              {profile.favorite_phrases && profile.favorite_phrases.length > 0 && (
                <div className="pt-4 border-t">
                  <p className="text-sm text-muted-foreground mb-2">Favorite Phrases</p>
                  <div className="flex flex-wrap gap-2">
                    {profile.favorite_phrases.slice(0, 5).map((phrase, idx) => (
                      <Badge key={idx} variant="outline">{phrase}</Badge>
                    ))}
                  </div>
                </div>
              )}

              {/* Action */}
              <div className="pt-4 border-t">
                <Button onClick={() => setShowTraining(true)} variant="outline">
                  <Sparkles className="h-4 w-4 mr-2" />
                  Retrain with New Samples
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      ) : (
        /* No Profile - Training CTA */
        <Card>
          <CardContent className="py-12 text-center">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-primary/10 mb-4">
              <Sparkles className="h-8 w-8 text-primary" />
            </div>
            <h3 className="text-lg font-semibold mb-2">No Style Profile Yet</h3>
            <p className="text-sm text-muted-foreground mb-4 max-w-md mx-auto">
              Train the AI to write in your unique voice by providing past newsletter examples
            </p>
            <Button onClick={() => setShowTraining(true)}>
              <Plus className="h-4 w-4 mr-2" />
              Train Style Profile
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Training Form */}
      {showTraining && (
        <Card>
          <CardContent className="pt-6 space-y-4">
            <div className="flex items-start justify-between">
              <div>
                <h3 className="font-semibold mb-1">
                  {summary?.has_profile ? 'Retrain Style Profile' : 'Train Style Profile'}
                </h3>
                <p className="text-sm text-muted-foreground">
                  Paste 5-20 past newsletter samples (minimum 50 words each)
                </p>
              </div>
              <Button variant="ghost" size="sm" onClick={() => setShowTraining(false)}>
                <X className="h-4 w-4" />
              </Button>
            </div>

            {/* Samples */}
            <div className="space-y-3">
              {samples.map((sample, index) => (
                <div key={index} className="relative">
                  <div className="flex items-start gap-2">
                    <div className="flex-1">
                      <label className="text-xs font-medium mb-1 block">
                        Sample {index + 1} {sample.trim().length > 0 && `(${sample.trim().split(/\s+/).length} words)`}
                      </label>
                      <textarea
                        value={sample}
                        onChange={(e) => handleSampleChange(index, e.target.value)}
                        placeholder="Paste a past newsletter here (minimum 50 words)..."
                        className="w-full min-h-[120px] p-3 border rounded-md text-sm font-mono resize-y"
                        disabled={isTraining}
                      />
                    </div>
                    {samples.length > 1 && (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleRemoveSample(index)}
                        disabled={isTraining}
                      >
                        <X className="h-4 w-4" />
                      </Button>
                    )}
                  </div>
                </div>
              ))}
            </div>

            {/* Add Sample Button */}
            <Button
              onClick={handleAddSample}
              variant="outline"
              size="sm"
              disabled={isTraining}
            >
              <Plus className="h-4 w-4 mr-2" />
              Add Another Sample
            </Button>

            {/* Warning */}
            {samples.filter(s => s.trim().length >= 50).length < 5 && (
              <div className="p-3 bg-orange-50 dark:bg-orange-950 border border-orange-200 dark:border-orange-800 rounded-lg">
                <div className="flex gap-2">
                  <AlertCircle className="h-4 w-4 text-orange-600 dark:text-orange-400 flex-shrink-0 mt-0.5" />
                  <p className="text-sm text-orange-800 dark:text-orange-200">
                    You need at least 5 samples of 50+ words each. Currently have {samples.filter(s => s.trim().length >= 50).length}.
                  </p>
                </div>
              </div>
            )}

            {/* Actions */}
            <div className="flex gap-2 pt-4 border-t">
              <Button
                onClick={handleTrain}
                disabled={isTraining || samples.filter(s => s.trim().length >= 50).length < 5}
              >
                <Sparkles className="h-4 w-4 mr-2" />
                {isTraining ? 'Training...' : summary?.has_profile ? 'Retrain Profile' : 'Train Profile'}
              </Button>
              <Button
                onClick={() => setShowTraining(false)}
                variant="outline"
                disabled={isTraining}
              >
                Cancel
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
