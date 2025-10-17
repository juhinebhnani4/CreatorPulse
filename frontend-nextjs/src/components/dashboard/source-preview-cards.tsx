'use client';

import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Plus } from 'lucide-react';

interface SourcePreview {
  id: string;
  icon: string;
  name: string;
  description: string;
}

interface SourcePreviewCardsProps {
  onAddSource: (type: string) => void;
  showPopular?: boolean;
}

export function SourcePreviewCards({ onAddSource, showPopular = true }: SourcePreviewCardsProps) {
  const sources: SourcePreview[] = [
    {
      id: 'reddit',
      icon: '📱',
      name: 'Reddit',
      description: 'Subreddits & posts',
    },
    {
      id: 'rss',
      icon: '📰',
      name: 'RSS Feed',
      description: 'Blog posts & articles',
    },
    {
      id: 'twitter',
      icon: '🐦',
      name: 'Twitter',
      description: 'Tweets & threads',
    },
  ];

  const popularSources = ['YouTube', 'Blogs', 'GitHub'];

  return (
    <Card className="border-0 shadow-lg animate-slide-up" style={{ animationDelay: '200ms' }}>
      <CardContent className="pt-6 pb-6">
        <div className="space-y-6">
          {/* Header */}
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-xl font-bold">Content Sources</h3>
              <p className="text-sm text-muted-foreground">Manage your content sources</p>
            </div>
            <Button
              size="sm"
              onClick={() => onAddSource('custom')}
              className="bg-gradient-warm hover:opacity-90"
            >
              <Plus className="h-4 w-4 mr-1" />
              Add Source
            </Button>
          </div>

          {/* Empty state message */}
          <p className="text-center text-muted-foreground">
            No sources configured yet
          </p>

          {/* Source preview grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {sources.map((source, index) => (
              <div
                key={source.id}
                className="border-2 border-dashed rounded-xl p-6 text-center space-y-3 hover:border-primary hover:bg-primary/5 transition-all cursor-pointer group animate-slide-up"
                style={{ animationDelay: `${(index + 3) * 50}ms` }}
                onClick={() => onAddSource(source.id)}
              >
                {/* Icon */}
                <div className="text-4xl">{source.icon}</div>

                {/* Name */}
                <div>
                  <h4 className="font-semibold text-base">{source.name}</h4>
                  <p className="text-xs text-muted-foreground mt-1">
                    {source.description}
                  </p>
                </div>

                {/* Add button */}
                <Button
                  size="sm"
                  variant="outline"
                  className="w-full group-hover:bg-primary group-hover:text-primary-foreground group-hover:border-primary transition-colors"
                >
                  <Plus className="h-3 w-3 mr-1" />
                  Add
                </Button>
              </div>
            ))}
          </div>

          {/* Popular sources */}
          {showPopular && (
            <div className="text-center">
              <p className="text-sm text-muted-foreground">
                <span className="font-medium">Popular:</span>{' '}
                {popularSources.map((source, index) => (
                  <span key={source}>
                    <button
                      onClick={() => onAddSource(source.toLowerCase())}
                      className="text-primary hover:underline"
                    >
                      {source}
                    </button>
                    {index < popularSources.length - 1 && ', '}
                  </span>
                ))}
              </p>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
