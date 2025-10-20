'use client';

import { useState, useEffect } from 'react';
import { useWorkspace } from '@/lib/hooks/use-workspace';
import { styleApi, StyleProfile, StyleProfileSummary } from '@/lib/api/style';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { useToast } from '@/lib/hooks/use-toast';
import {
  Upload,
  Sparkles,
  Trash2,
  Eye,
  Edit,
  Loader2,
  BookOpen,
  Zap,
  TrendingUp,
  MessageSquare,
  CheckCircle2,
  AlertCircle,
} from 'lucide-react';

export default function StyleProfilePage() {
  const { workspace } = useWorkspace();
  const { toast } = useToast();

  const [loading, setLoading] = useState(false);
  const [profile, setProfile] = useState<StyleProfile | null>(null);
  const [summary, setSummary] = useState<StyleProfileSummary | null>(null);
  const [samples, setSamples] = useState('');
  const [trainingStage, setTrainingStage] = useState<string>('');
  const [viewMode, setViewMode] = useState<'upload' | 'view'>('upload');

  useEffect(() => {
    if (workspace?.id) {
      loadProfileSummary();
    }
  }, [workspace?.id]);

  const loadProfileSummary = async () => {
    if (!workspace?.id) return;

    try {
      const data = await styleApi.getSummary(workspace.id);
      setSummary(data);

      if (data.has_profile) {
        setViewMode('view');
        await loadFullProfile();
      }
    } catch (error) {
      // No profile exists yet - that's okay
      console.log('No style profile yet');
    }
  };

  const loadFullProfile = async () => {
    if (!workspace?.id) return;

    try {
      setLoading(true);
      const data = await styleApi.getProfile(workspace.id);
      setProfile(data);
    } catch (error: any) {
      toast({
        title: 'Error',
        description: error.message,
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleTrain = async () => {
    if (!workspace?.id) return;
    if (!samples.trim()) {
      toast({
        title: 'No samples provided',
        description: 'Please paste at least 10 newsletter samples separated by "---"',
        variant: 'destructive',
      });
      return;
    }

    // Split samples by separator
    const sampleArray = samples
      .split('---')
      .map((s) => s.trim())
      .filter((s) => s.length > 50); // At least 50 chars per sample

    if (sampleArray.length < 10) {
      toast({
        title: 'Not enough samples',
        description: `You provided ${sampleArray.length} samples. Please provide at least 10 for accurate training.`,
        variant: 'destructive',
      });
      return;
    }

    try {
      setLoading(true);
      setTrainingStage('Uploading samples...');

      const response = await styleApi.train({
        workspace_id: workspace.id,
        samples: sampleArray,
        retrain: summary?.has_profile || false,
      });

      setTrainingStage('Analyzing writing patterns...');
      await new Promise((resolve) => setTimeout(resolve, 1000));

      setTrainingStage('Extracting style characteristics...');
      await new Promise((resolve) => setTimeout(resolve, 1000));

      setProfile(response.profile);
      setSummary({
        has_profile: true,
        sample_count: response.profile.sample_count,
        tone: response.profile.tone,
        formality: response.profile.formality,
        last_updated: response.profile.updated_at,
      });

      toast({
        title: '✨ Style profile trained!',
        description: `Analyzed ${sampleArray.length} samples. Your unique writing style has been captured.`,
      });

      setViewMode('view');
      setSamples('');
      setTrainingStage('');
    } catch (error: any) {
      toast({
        title: 'Training failed',
        description: error.message,
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
      setTrainingStage('');
    }
  };

  const handleDelete = async () => {
    if (!workspace?.id) return;
    if (!confirm('Are you sure you want to delete your style profile? This cannot be undone.')) {
      return;
    }

    try {
      setLoading(true);
      await styleApi.delete(workspace.id);

      setProfile(null);
      setSummary(null);
      setViewMode('upload');

      toast({
        title: 'Style profile deleted',
        description: 'You can train a new profile anytime',
      });
    } catch (error: any) {
      toast({
        title: 'Deletion failed',
        description: error.message,
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-orange-600 to-amber-600 bg-clip-text text-transparent">
            Writing Style Trainer
          </h1>
          <p className="text-muted-foreground mt-2">
            Train AI to match your unique voice and writing patterns
          </p>
        </div>

        {summary?.has_profile && (
          <div className="flex gap-2">
            <Button
              variant="outline"
              onClick={() => setViewMode(viewMode === 'view' ? 'upload' : 'view')}
            >
              {viewMode === 'view' ? <Upload className="w-4 h-4 mr-2" /> : <Eye className="w-4 h-4 mr-2" />}
              {viewMode === 'view' ? 'Retrain' : 'View Profile'}
            </Button>
          </div>
        )}
      </div>

      {/* Status Card */}
      {summary?.has_profile && (
        <Card className="p-4 bg-gradient-to-r from-orange-50 to-amber-50 dark:from-orange-950/20 dark:to-amber-950/20 border-orange-200">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-orange-500 to-amber-600 rounded-lg flex items-center justify-center">
                <CheckCircle2 className="w-6 h-6 text-white" />
              </div>
              <div>
                <p className="font-semibold text-orange-900 dark:text-orange-100">
                  Style Profile Active
                </p>
                <p className="text-sm text-orange-700 dark:text-orange-300">
                  Trained on {summary.sample_count} samples • {summary.tone} • {summary.formality}
                </p>
              </div>
            </div>
            <Button variant="ghost" size="sm" onClick={handleDelete} className="text-red-600 hover:text-red-700">
              <Trash2 className="w-4 h-4" />
            </Button>
          </div>
        </Card>
      )}

      {/* Main Content */}
      {viewMode === 'upload' ? (
        <UploadSection
          samples={samples}
          setSamples={setSamples}
          loading={loading}
          trainingStage={trainingStage}
          onTrain={handleTrain}
          hasExisting={summary?.has_profile || false}
        />
      ) : (
        <ProfileViewSection profile={profile} loading={loading} />
      )}
    </div>
  );
}

// Upload Section Component
function UploadSection({
  samples,
  setSamples,
  loading,
  trainingStage,
  onTrain,
  hasExisting,
}: {
  samples: string;
  setSamples: (value: string) => void;
  loading: boolean;
  trainingStage: string;
  onTrain: () => void;
  hasExisting: boolean;
}) {
  return (
    <Card className="p-6">
      <div className="space-y-6">
        <div>
          <h2 className="text-xl font-semibold mb-2 flex items-center gap-2">
            <BookOpen className="w-5 h-5 text-orange-600" />
            {hasExisting ? 'Retrain Style Profile' : 'Train Your Writing Style'}
          </h2>
          <p className="text-sm text-muted-foreground">
            Paste 10-50 of your past newsletters below. Separate each with "---". The more samples you provide, the better
            the AI will match your voice.
          </p>
        </div>

        <div className="space-y-2">
          <Textarea
            placeholder={`Example:

Hey everyone! Here's what's trending this week in AI...

--- (Separator)

Welcome back to another edition! Today we're diving into...

--- (Separator)

(Add 10+ samples separated by ---)
`}
            value={samples}
            onChange={(e) => setSamples(e.target.value)}
            rows={15}
            className="font-mono text-sm"
            disabled={loading}
          />

          <div className="flex items-center justify-between text-sm text-muted-foreground">
            <span>
              {samples.split('---').filter((s) => s.trim().length > 50).length} samples ready
            </span>
            <span>Minimum: 10 samples recommended</span>
          </div>
        </div>

        {loading && trainingStage && (
          <Card className="p-4 bg-orange-50 dark:bg-orange-950/20 border-orange-200">
            <div className="flex items-center gap-3">
              <Loader2 className="w-5 h-5 animate-spin text-orange-600" />
              <div>
                <p className="font-medium text-orange-900 dark:text-orange-100">{trainingStage}</p>
                <p className="text-sm text-orange-700 dark:text-orange-300">This may take a minute...</p>
              </div>
            </div>
          </Card>
        )}

        <div className="flex gap-3">
          <Button onClick={onTrain} disabled={loading} className="bg-gradient-to-r from-orange-600 to-amber-600">
            {loading ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Training...
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4 mr-2" />
                {hasExisting ? 'Retrain Profile' : 'Train Style Profile'}
              </>
            )}
          </Button>

          <Button variant="outline" onClick={() => setSamples('')} disabled={loading}>
            Clear
          </Button>
        </div>
      </div>
    </Card>
  );
}

// Profile View Section Component
function ProfileViewSection({ profile, loading }: { profile: StyleProfile | null; loading: boolean }) {
  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="w-8 h-8 animate-spin text-orange-600" />
      </div>
    );
  }

  if (!profile) {
    return (
      <Card className="p-12 text-center">
        <AlertCircle className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
        <p className="text-muted-foreground">No profile data available</p>
      </Card>
    );
  }

  return (
    <div className="grid gap-6 md:grid-cols-2">
      {/* Voice Characteristics */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <MessageSquare className="w-5 h-5 text-orange-600" />
          Voice Characteristics
        </h3>

        <div className="space-y-4">
          <CharacteristicRow label="Tone" value={profile.tone} icon={<Sparkles className="w-4 h-4" />} />
          <CharacteristicRow label="Formality" value={profile.formality} icon={<TrendingUp className="w-4 h-4" />} />
          <CharacteristicRow
            label="Vocabulary"
            value={profile.vocabulary_level}
            icon={<BookOpen className="w-4 h-4" />}
          />
          <CharacteristicRow label="Emoji Usage" value={profile.emoji_usage} icon={<Zap className="w-4 h-4" />} />
        </div>
      </Card>

      {/* Sentence Patterns */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Edit className="w-5 h-5 text-orange-600" />
          Sentence Patterns
        </h3>

        <div className="space-y-4">
          <CharacteristicRow
            label="Avg Sentence Length"
            value={`${profile.avg_sentence_length} words`}
            icon={<TrendingUp className="w-4 h-4" />}
          />
          <CharacteristicRow
            label="Section Count"
            value={profile.section_count_preference || 'Adaptive'}
            icon={<BookOpen className="w-4 h-4" />}
          />
          <CharacteristicRow
            label="Greeting Style"
            value={profile.greeting_style || 'Not specified'}
            icon={<MessageSquare className="w-4 h-4" />}
          />
          <CharacteristicRow
            label="Closing Style"
            value={profile.closing_style || 'Not specified'}
            icon={<MessageSquare className="w-4 h-4" />}
          />
        </div>
      </Card>

      {/* Favorite Phrases */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4">Favorite Phrases</h3>
        <div className="flex flex-wrap gap-2">
          {profile.favorite_phrases.length > 0 ? (
            profile.favorite_phrases.map((phrase, idx) => (
              <Badge key={idx} variant="secondary">
                {phrase}
              </Badge>
            ))
          ) : (
            <p className="text-sm text-muted-foreground">None identified yet</p>
          )}
        </div>
      </Card>

      {/* Avoided Words */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4">Avoided Words</h3>
        <div className="flex flex-wrap gap-2">
          {profile.avoided_words.length > 0 ? (
            profile.avoided_words.map((word, idx) => (
              <Badge key={idx} variant="outline" className="border-red-200 text-red-700">
                {word}
              </Badge>
            ))
          ) : (
            <p className="text-sm text-muted-foreground">None identified yet</p>
          )}
        </div>
      </Card>

      {/* Training Info */}
      <Card className="p-6 md:col-span-2 bg-gradient-to-r from-orange-50 to-amber-50 dark:from-orange-950/20 dark:to-amber-950/20 border-orange-200">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 bg-gradient-to-br from-orange-500 to-amber-600 rounded-lg flex items-center justify-center">
            <Sparkles className="w-6 h-6 text-white" />
          </div>
          <div className="flex-1">
            <h3 className="font-semibold text-orange-900 dark:text-orange-100">Training Complete</h3>
            <p className="text-sm text-orange-700 dark:text-orange-300">
              Profile trained on {profile.sample_count} newsletters • Last updated{' '}
              {new Date(profile.updated_at).toLocaleDateString()}
            </p>
          </div>
        </div>
      </Card>
    </div>
  );
}

// Helper Component
function CharacteristicRow({ label, value, icon }: { label: string; value: string | number; icon: React.ReactNode }) {
  return (
    <div className="flex items-center justify-between py-2 border-b border-border/50 last:border-0">
      <div className="flex items-center gap-2 text-sm text-muted-foreground">
        {icon}
        <span>{label}</span>
      </div>
      <span className="font-medium capitalize">{value}</span>
    </div>
  );
}
