'use client';

import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { SampleDataBadge } from '@/components/ui/sample-data-badge';
import { FileText, ArrowRight, Clock, Sparkles, ExternalLink, TrendingUp } from 'lucide-react';
import Image from 'next/image';

interface EnhancedDraftCardProps {
  status: 'empty' | 'ready' | 'generating' | 'stale' | 'scheduled';
  nextRunAt?: Date;
  onConfigureSources: () => void;
  onGenerateNow?: () => void;
  onPreviewDraft?: () => void;
  onSendNow?: () => void;
  draftGeneratedAt?: Date;
  newItemsCount?: number;
}

export function EnhancedDraftCard({
  status,
  nextRunAt,
  onConfigureSources,
  onGenerateNow,
  onPreviewDraft,
  onSendNow,
  draftGeneratedAt,
  newItemsCount,
}: EnhancedDraftCardProps) {
  // Curated trending articles (rotate randomly or use first)
  const trendingArticles = [
    {
      image: 'https://images.unsplash.com/photo-1677442136019-21780ecad995?w=800&h=450&fit=crop',
      title: 'GPT-5 Rumors: What We Know So Far',
      description: 'OpenAI hints at next-gen model with breakthrough reasoning capabilities',
      summary: 'Industry insiders report that GPT-5 could launch Q2 2025 with unprecedented advances in multi-step reasoning, agentic behavior, and real-time learning. Early benchmarks suggest 10x improvement over GPT-4 in complex problem-solving tasks.',
      url: 'https://openai.com/blog',
      icon: '🤖',
    },
    {
      image: 'https://images.unsplash.com/photo-1620712943543-bcc4688e7485?w=800&h=450&fit=crop',
      title: 'New AI Coding Assistant Surpasses GitHub Copilot',
      description: 'Startup launches AI tool with 95% code completion accuracy',
      summary: 'A new entrant in the AI coding space claims to outperform GitHub Copilot with context-aware suggestions, bug detection, and automated refactoring. The tool has already attracted 50K+ developers in beta.',
      url: 'https://github.blog',
      icon: '💻',
    },
    {
      image: 'https://images.unsplash.com/photo-1635070041078-e363dbe005cb?w=800&h=450&fit=crop',
      title: 'Breakthrough in AGI Research: Self-Learning Systems',
      description: 'DeepMind announces AI that learns without human supervision',
      summary: 'Researchers at DeepMind have developed a self-learning AI system that can acquire new skills autonomously, marking a significant step toward Artificial General Intelligence. The system demonstrated human-level performance across 12 diverse tasks.',
      url: 'https://deepmind.google',
      icon: '🧠',
    },
  ];

  // Pick first article (or random)
  const trendingArticle = trendingArticles[0];

  // Empty state - no sources configured
  if (status === 'empty') {
    return (
      <Card className="border-2 border-dashed animate-slide-up" style={{ animationDelay: '100ms' }}>
        <CardContent className="pt-8 pb-8">
          <div className="space-y-6">
            {/* Header Message */}
            <div className="text-center space-y-2">
              <h3 className="text-2xl font-bold">Your first draft will appear here!</h3>
              <div className="flex items-center justify-center gap-2 text-muted-foreground">
                <TrendingUp className="h-4 w-4" />
                <p className="text-sm">Here's what's trending in AI today:</p>
              </div>
            </div>

            {/* Trending Article Preview */}
            <div className="max-w-2xl mx-auto">
              <Card className="border overflow-hidden hover:shadow-lg transition-shadow">
                {/* Featured Image */}
                <div className="relative w-full h-48 bg-muted">
                  <Image
                    src={trendingArticle.image}
                    alt={trendingArticle.title}
                    fill
                    priority
                    sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
                    className="object-cover"
                  />
                  {/* Example badge overlay */}
                  <div className="absolute top-2 right-2">
                    <SampleDataBadge
                      tooltip="This is an example article to show what your newsletter content will look like."
                      variant="secondary"
                      className="bg-white/90 backdrop-blur-sm"
                    />
                  </div>
                </div>

                <CardContent className="pt-4 pb-4">
                  <div className="space-y-3">
                    {/* Title with Icon */}
                    <div className="flex items-start gap-2">
                      <span className="text-2xl">{trendingArticle.icon}</span>
                      <h4 className="font-bold text-lg leading-tight">{trendingArticle.title}</h4>
                    </div>

                    {/* Description */}
                    <p className="text-sm font-medium text-muted-foreground">
                      {trendingArticle.description}
                    </p>

                    {/* Summary */}
                    <p className="text-sm text-muted-foreground leading-relaxed">
                      {trendingArticle.summary}
                    </p>

                    {/* Read More Link */}
                    <a
                      href={trendingArticle.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1 text-sm text-primary hover:underline"
                    >
                      Read more
                      <ExternalLink className="h-3 w-3" />
                    </a>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Bridge Text to Unified Setup */}
            <div className="text-center space-y-2">
              <div className="inline-flex items-center gap-2 text-sm text-muted-foreground bg-primary/5 border border-primary/20 px-4 py-2 rounded-lg">
                <Sparkles className="h-4 w-4 text-primary" />
                <span>
                  <span className="font-medium text-foreground">Add your sources below</span> to get personalized content like this in your daily newsletter
                </span>
              </div>
              <div className="text-2xl animate-bounce">👇</div>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  // Ready state - draft available
  if (status === 'ready') {
    return (
      <Card className="border-0 shadow-lg animate-slide-up" style={{ animationDelay: '100ms' }}>
        <CardContent className="pt-6 pb-6">
          <div className="space-y-4">
            {/* Header */}
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 rounded-xl bg-gradient-hero flex items-center justify-center">
                  <FileText className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h3 className="text-xl font-bold">Today's Newsletter Draft</h3>
                  <p className="text-sm text-muted-foreground">Ready for review</p>
                </div>
              </div>
              <Badge className="bg-success text-success-foreground">Ready</Badge>
            </div>

            {/* Actions */}
            <div className="flex gap-3 pt-2">
              <Button
                onClick={onPreviewDraft}
                className="flex-1 bg-gradient-hero hover:opacity-90"
              >
                Preview Draft
                <ArrowRight className="h-4 w-4 ml-2" />
              </Button>
              <Button
                onClick={onSendNow}
                variant="outline"
                className="hover:bg-success hover:text-success-foreground hover:border-success"
              >
                Send Now
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  // Stale state - draft is outdated
  if (status === 'stale') {
    // Helper for time ago format
    const formatTimeAgo = (date?: Date) => {
      if (!date) return 'some time ago';
      const now = new Date();
      const diffMs = now.getTime() - date.getTime();
      const diffMins = Math.floor(diffMs / 60000);
      const diffHours = Math.floor(diffMs / 3600000);
      const diffDays = Math.floor(diffMs / 86400000);

      if (diffMins < 60) return `${diffMins} min${diffMins !== 1 ? 's' : ''} ago`;
      if (diffHours < 24) return `${diffHours} hour${diffHours !== 1 ? 's' : ''} ago`;
      return `${diffDays} day${diffDays !== 1 ? 's' : ''} ago`;
    };

    return (
      <Card className="border-2 border-orange-200 shadow-lg animate-slide-up" style={{ animationDelay: '100ms' }}>
        <CardContent className="pt-6 pb-6">
          <div className="space-y-4">
            {/* Header */}
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 rounded-xl bg-orange-100 flex items-center justify-center">
                  <FileText className="w-6 h-6 text-orange-600" />
                </div>
                <div>
                  <h3 className="text-xl font-bold">Newsletter Draft (Outdated)</h3>
                  <p className="text-sm text-muted-foreground">
                    Generated {formatTimeAgo(draftGeneratedAt)}
                    {newItemsCount && newItemsCount > 0 && ` • ${newItemsCount} new items available`}
                  </p>
                </div>
              </div>
              <Badge variant="secondary" className="bg-orange-100 text-orange-700 border-orange-300">
                Outdated
              </Badge>
            </div>

            {/* Info Banner */}
            <div className="bg-orange-50 border border-orange-200 rounded-lg p-3">
              <p className="text-sm text-orange-800">
                <strong>New content is available!</strong> Regenerate your draft to include the latest items from your sources.
              </p>
            </div>

            {/* Actions */}
            <div className="flex gap-3 pt-2">
              <Button
                onClick={onGenerateNow}
                className="flex-1 bg-orange-600 hover:bg-orange-700 text-white"
              >
                <Sparkles className="h-4 w-4 mr-2" />
                Regenerate with New Content
              </Button>
              <Button
                onClick={onPreviewDraft}
                variant="outline"
                className="hover:bg-muted"
              >
                Preview Current Draft
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  // Generating state
  if (status === 'generating') {
    return (
      <Card className="border-0 shadow-lg animate-slide-up" style={{ animationDelay: '100ms' }}>
        <CardContent className="pt-8 pb-8">
          <div className="text-center space-y-4">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gradient-hero animate-pulse-soft">
              <Sparkles className="w-8 h-8 text-white" />
            </div>
            <div>
              <h3 className="text-xl font-bold mb-1">Generating your newsletter...</h3>
              <p className="text-sm text-muted-foreground">
                Our AI is curating the best content for you
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  // Scheduled state
  return (
    <Card className="border-0 shadow-lg animate-slide-up" style={{ animationDelay: '100ms' }}>
      <CardContent className="pt-6 pb-6">
        <div className="space-y-4">
          {/* Header */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-xl bg-secondary flex items-center justify-center">
                <Clock className="w-6 h-6 text-secondary-foreground" />
              </div>
              <div>
                <h3 className="text-xl font-bold">Next Newsletter</h3>
                <p className="text-sm text-muted-foreground">
                  Scheduled for {nextRunAt ? new Intl.DateTimeFormat('en-US', {
                    month: 'short',
                    day: 'numeric',
                    hour: 'numeric',
                    minute: 'numeric',
                  }).format(nextRunAt) : 'tomorrow at 8:00 AM'}
                </p>
              </div>
            </div>
            <Badge variant="secondary">Scheduled</Badge>
          </div>

          {/* Action */}
          {onGenerateNow && (
            <Button
              onClick={onGenerateNow}
              variant="outline"
              className="w-full"
            >
              Generate Draft Now
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
