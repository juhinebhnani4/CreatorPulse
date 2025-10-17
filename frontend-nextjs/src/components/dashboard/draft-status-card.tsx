'use client';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { Clock, CheckCircle2, Loader2, AlertCircle } from 'lucide-react';

export type DraftStatus = 'ready' | 'generating' | 'scheduled' | 'empty';

interface DraftStatusCardProps {
  status: DraftStatus;
  nextRunAt?: Date;
  progress?: number; // 0-100 for generating state
  onGenerateNow?: () => void;
  onScrapeContent?: () => void;
  onPreviewDraft?: () => void;
  onSendNow?: () => void;
  isLoading?: boolean;
}

export function DraftStatusCard({
  status,
  nextRunAt,
  progress = 0,
  onGenerateNow,
  onScrapeContent,
  onPreviewDraft,
  onSendNow,
  isLoading = false,
}: DraftStatusCardProps) {
  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <Skeleton className="h-6 w-48" />
          <Skeleton className="h-4 w-64" />
        </CardHeader>
        <CardContent>
          <Skeleton className="h-20 w-full" />
        </CardContent>
      </Card>
    );
  }

  const getStatusContent = () => {
    switch (status) {
      case 'ready':
        return {
          icon: <CheckCircle2 className="h-12 w-12 text-green-500" />,
          title: 'Your newsletter is ready to send!',
          description: 'Review your draft and send it to your subscribers',
          badge: <Badge variant="default" className="bg-green-500">Ready</Badge>,
          actions: (
            <div className="flex gap-3">
              <Button variant="outline" onClick={onPreviewDraft}>
                Preview Full Draft
              </Button>
              <Button onClick={onSendNow}>
                Send Now
              </Button>
            </div>
          ),
        };

      case 'generating':
        return {
          icon: <Loader2 className="h-12 w-12 text-blue-500 animate-spin" />,
          title: 'Generating your draft...',
          description: `${Math.round(progress)}% complete - This usually takes about 45 seconds`,
          badge: <Badge variant="secondary">Generating</Badge>,
          actions: (
            <div className="w-full">
              <div className="w-full bg-secondary rounded-full h-2 mb-2">
                <div
                  className="bg-primary h-2 rounded-full transition-all duration-300"
                  style={{ width: `${progress}%` }}
                />
              </div>
            </div>
          ),
        };

      case 'scheduled':
        const formattedDate = nextRunAt
          ? new Intl.DateTimeFormat('en-US', {
              weekday: 'long',
              hour: 'numeric',
              minute: 'numeric',
              hour12: true,
            }).format(nextRunAt)
          : 'tomorrow at 8:00 AM';

        return {
          icon: <Clock className="h-12 w-12 text-orange-500" />,
          title: `Next draft arrives ${formattedDate}`,
          description: 'First, scrape content from your sources, then generate your newsletter',
          badge: <Badge variant="secondary">Scheduled</Badge>,
          actions: (
            <div className="flex gap-3">
              <Button variant="outline" onClick={onScrapeContent}>
                Scrape Content
              </Button>
              <Button onClick={onGenerateNow}>
                Generate Draft
              </Button>
            </div>
          ),
        };

      case 'empty':
        return {
          icon: <AlertCircle className="h-12 w-12 text-muted-foreground" />,
          title: 'No draft yet',
          description: 'Add content sources to get started with your first newsletter',
          badge: <Badge variant="outline">Empty</Badge>,
          actions: (
            <Button onClick={onGenerateNow}>
              Configure Sources & Generate
            </Button>
          ),
        };
    }
  };

  const content = getStatusContent();

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>Today's Newsletter Draft</CardTitle>
            <CardDescription>Your AI-powered newsletter</CardDescription>
          </div>
          {content.badge}
        </div>
      </CardHeader>
      <CardContent>
        <div className="flex items-start gap-4">
          <div className="flex-shrink-0">
            {content.icon}
          </div>
          <div className="flex-1">
            <h3 className="text-lg font-semibold mb-1">{content.title}</h3>
            <p className="text-sm text-muted-foreground mb-4">{content.description}</p>
            {content.actions}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
