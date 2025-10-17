'use client';

import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { X, Pause, Play, RefreshCw } from 'lucide-react';

interface SourceCardProps {
  icon: string;
  name: string;
  type: string;
  itemCount: number;
  lastSynced?: Date;
  isPaused?: boolean;
  onRemove?: () => void;
  onTogglePause?: () => void;
  onRefresh?: () => void;
}

export function SourceCard({
  icon,
  name,
  type,
  itemCount,
  lastSynced,
  isPaused = false,
  onRemove,
  onTogglePause,
  onRefresh,
}: SourceCardProps) {
  const formatLastSynced = (date?: Date) => {
    if (!date) return 'Never synced';

    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / (1000 * 60));
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays === 1) return 'Yesterday';
    return `${diffDays}d ago`;
  };

  return (
    <Card className={`border-2 transition-all duration-300 hover:shadow-lg animate-slide-up ${
      isPaused ? 'border-muted bg-muted/20 opacity-75' : 'border-border hover:border-primary'
    }`}>
      <CardContent className="pt-4 pb-4">
        <div className="space-y-3">
          {/* Header */}
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-3 flex-1">
              <div className="text-2xl">{icon}</div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <h4 className="font-semibold text-base truncate">{name}</h4>
                  {isPaused && (
                    <Badge variant="secondary" className="bg-warning/20 text-warning text-xs">
                      Paused
                    </Badge>
                  )}
                </div>
                <p className="text-xs text-muted-foreground">
                  {type.charAt(0).toUpperCase() + type.slice(1)} • {itemCount} items
                </p>
              </div>
            </div>

            <Button
              variant="ghost"
              size="sm"
              onClick={onRemove}
              className="h-8 w-8 p-0 hover:bg-destructive/10 hover:text-destructive"
            >
              <X className="h-4 w-4" />
            </Button>
          </div>

          {/* Footer with actions */}
          <div className="flex items-center justify-between pt-2 border-t border-border/50">
            <div className="flex items-center gap-2 text-xs text-muted-foreground">
              <RefreshCw className="h-3 w-3" />
              <span>Last synced: {formatLastSynced(lastSynced)}</span>
            </div>

            <div className="flex items-center gap-1">
              {onRefresh && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={onRefresh}
                  className="h-7 px-2 text-xs hover:bg-primary/10 hover:text-primary"
                >
                  <RefreshCw className="h-3 w-3 mr-1" />
                  Sync
                </Button>
              )}
              {onTogglePause && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={onTogglePause}
                  className="h-7 px-2 text-xs hover:bg-secondary/10 hover:text-secondary"
                >
                  {isPaused ? (
                    <>
                      <Play className="h-3 w-3 mr-1" />
                      Resume
                    </>
                  ) : (
                    <>
                      <Pause className="h-3 w-3 mr-1" />
                      Pause
                    </>
                  )}
                </Button>
              )}
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
