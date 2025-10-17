'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Clock, CheckCircle2, Calendar, Zap } from 'lucide-react';

interface Activity {
  id: string;
  type: 'scrape' | 'generate' | 'send' | 'schedule';
  title: string;
  description: string;
  timestamp: Date;
  status: 'success' | 'pending' | 'scheduled';
}

interface RecentActivityProps {
  activities?: Activity[];
}

const mockActivities: Activity[] = [
  {
    id: '1',
    type: 'schedule',
    title: 'Next Newsletter Scheduled',
    description: 'Tomorrow at 8:00 AM',
    timestamp: new Date(Date.now() + 24 * 60 * 60 * 1000),
    status: 'scheduled',
  },
  {
    id: '2',
    type: 'scrape',
    title: 'Content Scraped',
    description: '25 new items from 5 sources',
    timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000),
    status: 'success',
  },
  {
    id: '3',
    type: 'generate',
    title: 'Newsletter Generated',
    description: 'Draft ready for review',
    timestamp: new Date(Date.now() - 24 * 60 * 60 * 1000),
    status: 'success',
  },
];

export function RecentActivity({ activities = mockActivities }: RecentActivityProps) {
  const getIcon = (type: Activity['type']) => {
    switch (type) {
      case 'scrape':
        return Zap;
      case 'generate':
        return CheckCircle2;
      case 'send':
        return CheckCircle2;
      case 'schedule':
        return Calendar;
      default:
        return Clock;
    }
  };

  const getIconColor = (type: Activity['type']) => {
    switch (type) {
      case 'scrape':
        return 'bg-gradient-warm';
      case 'generate':
        return 'bg-gradient-hero';
      case 'send':
        return 'bg-gradient-cool';
      case 'schedule':
        return 'bg-secondary';
      default:
        return 'bg-muted';
    }
  };

  const getStatusBadge = (status: Activity['status']) => {
    switch (status) {
      case 'success':
        return <Badge className="bg-success text-success-foreground">Success</Badge>;
      case 'pending':
        return <Badge className="bg-warning text-warning-foreground">Pending</Badge>;
      case 'scheduled':
        return <Badge className="bg-secondary text-secondary-foreground">Scheduled</Badge>;
      default:
        return null;
    }
  };

  const formatTimestamp = (date: Date) => {
    const now = new Date();
    const diffMs = date.getTime() - now.getTime();
    const diffHours = Math.floor(Math.abs(diffMs) / (1000 * 60 * 60));
    const diffDays = Math.floor(diffHours / 24);

    if (diffMs > 0) {
      // Future date
      if (diffHours < 24) return `in ${diffHours}h`;
      return `in ${diffDays}d`;
    } else {
      // Past date
      if (diffHours < 1) return 'just now';
      if (diffHours < 24) return `${diffHours}h ago`;
      if (diffDays === 1) return 'yesterday';
      return `${diffDays}d ago`;
    }
  };

  return (
    <Card className="border-0 shadow-lg">
      <CardHeader className="pb-3">
        <CardTitle className="text-xl font-bold flex items-center gap-2">
          <Clock className="h-5 w-5 text-primary" />
          Recent Activity
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {activities.map((activity, index) => {
            const Icon = getIcon(activity.type);
            const iconColorClass = getIconColor(activity.type);

            return (
              <div
                key={activity.id}
                className="flex items-start gap-4 pb-4 last:pb-0 last:border-0 border-b border-border/50 animate-slide-up"
                style={{ animationDelay: `${index * 50}ms` }}
              >
                {/* Icon */}
                <div className={`p-2 rounded-lg ${iconColorClass} flex-shrink-0`}>
                  <Icon className="h-4 w-4 text-white" />
                </div>

                {/* Content */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex-1">
                      <p className="font-semibold text-sm leading-tight">{activity.title}</p>
                      <p className="text-xs text-muted-foreground mt-1">{activity.description}</p>
                    </div>
                    {getStatusBadge(activity.status)}
                  </div>
                  <p className="text-xs text-muted-foreground mt-2">
                    {formatTimestamp(activity.timestamp)}
                  </p>
                </div>
              </div>
            );
          })}
        </div>

        {activities.length === 0 && (
          <div className="text-center py-8">
            <Clock className="h-12 w-12 text-muted-foreground mx-auto mb-3 opacity-50" />
            <p className="text-sm text-muted-foreground">No recent activity</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
