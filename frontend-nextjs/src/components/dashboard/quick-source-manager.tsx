'use client';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { Plus, Pause, Play } from 'lucide-react';

interface Source {
  id: string;
  type: 'reddit' | 'rss' | 'twitter' | 'youtube' | 'blog';
  name: string;
  itemCount: number;
  isPaused: boolean;
}

interface QuickSourceManagerProps {
  sources: Source[];
  onPause: (sourceId: string) => Promise<void>;
  onResume: (sourceId: string) => Promise<void>;
  onAdd: () => void;
  isLoading?: boolean;
}

const sourceIcons: Record<Source['type'], string> = {
  reddit: '🔴',
  rss: '📰',
  twitter: '🐦',
  youtube: '📺',
  blog: '✍️',
};

export function QuickSourceManager({
  sources,
  onPause,
  onResume,
  onAdd,
  isLoading = false,
}: QuickSourceManagerProps) {
  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <Skeleton className="h-6 w-32" />
          <Skeleton className="h-4 w-48" />
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {[1, 2, 3].map((i) => (
              <Skeleton key={i} className="h-12 w-full" />
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>Content Sources</CardTitle>
            <CardDescription>Manage your content sources</CardDescription>
          </div>
          <Button onClick={onAdd} size="sm">
            <Plus className="h-4 w-4 mr-1" />
            Add Source
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        {sources.length === 0 ? (
          <div className="text-center py-8">
            <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-muted mb-3">
              <Plus className="h-6 w-6 text-muted-foreground" />
            </div>
            <p className="text-sm text-muted-foreground mb-3">
              No sources configured yet
            </p>
            <Button onClick={onAdd} variant="outline" size="sm">
              Add Your First Source
            </Button>
          </div>
        ) : (
          <div className="space-y-2">
            {sources.map((source) => (
              <div
                key={source.id}
                className={`flex items-center justify-between p-3 rounded-lg border ${
                  source.isPaused ? 'bg-muted/50 opacity-60' : 'bg-background'
                }`}
              >
                <div className="flex items-center gap-3 flex-1 min-w-0">
                  <span className="text-2xl flex-shrink-0">
                    {sourceIcons[source.type]}
                  </span>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <p className="font-medium text-sm truncate">{source.name}</p>
                      {source.isPaused && (
                        <Badge variant="outline" className="text-xs">
                          Paused
                        </Badge>
                      )}
                    </div>
                    <p className="text-xs text-muted-foreground">
                      {source.itemCount} {source.itemCount === 1 ? 'item' : 'items'}
                    </p>
                  </div>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() =>
                    source.isPaused ? onResume(source.id) : onPause(source.id)
                  }
                  className="flex-shrink-0"
                >
                  {source.isPaused ? (
                    <>
                      <Play className="h-4 w-4 mr-1" />
                      Resume
                    </>
                  ) : (
                    <>
                      <Pause className="h-4 w-4 mr-1" />
                      Pause
                    </>
                  )}
                </Button>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
