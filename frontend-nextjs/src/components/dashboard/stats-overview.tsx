'use client';

import { Card, CardContent } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { Users, Send, TrendingUp, TrendingDown } from 'lucide-react';

interface StatsOverviewProps {
  subscriberCount: number;
  lastSentAt?: Date;
  openRate?: number;
  openRateTrend?: number; // Percentage change from previous
  isLoading?: boolean;
}

export function StatsOverview({
  subscriberCount,
  lastSentAt,
  openRate,
  openRateTrend,
  isLoading = false,
}: StatsOverviewProps) {
  if (isLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {[1, 2, 3].map((i) => (
          <Card key={i}>
            <CardContent className="pt-6">
              <Skeleton className="h-20 w-full" />
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  const formatNumber = (num: number) => {
    if (num >= 1000000) {
      return `${(num / 1000000).toFixed(1)}M`;
    }
    if (num >= 1000) {
      return `${(num / 1000).toFixed(1)}K`;
    }
    return num.toString();
  };

  const formatDate = (date?: Date) => {
    if (!date) return 'Never';
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffDays = Math.floor(diffHours / 24);

    if (diffHours < 1) return 'Just now';
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays === 1) return 'Yesterday';
    if (diffDays < 7) return `${diffDays}d ago`;

    return new Intl.DateTimeFormat('en-US', {
      month: 'short',
      day: 'numeric',
    }).format(date);
  };

  const stats = [
    {
      label: 'Subscribers',
      value: formatNumber(subscriberCount),
      icon: Users,
      description: 'Total subscribers',
    },
    {
      label: 'Last Sent',
      value: formatDate(lastSentAt),
      icon: Send,
      description: lastSentAt
        ? new Intl.DateTimeFormat('en-US', {
            month: 'short',
            day: 'numeric',
            hour: 'numeric',
            minute: 'numeric',
          }).format(lastSentAt)
        : 'No newsletters sent yet',
    },
    {
      label: 'Open Rate',
      value: openRate !== undefined ? `${openRate}%` : 'N/A',
      icon: openRateTrend !== undefined && openRateTrend >= 0 ? TrendingUp : TrendingDown,
      description:
        openRateTrend !== undefined
          ? `${openRateTrend >= 0 ? '+' : ''}${openRateTrend}% from last week`
          : 'No data yet',
      trend: openRateTrend,
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      {stats.map((stat, index) => {
        const Icon = stat.icon;
        const isPositiveTrend = stat.trend !== undefined && stat.trend >= 0;
        const isNegativeTrend = stat.trend !== undefined && stat.trend < 0;

        // Determine gradient background based on index
        const gradientClass = index === 0
          ? 'bg-gradient-warm'
          : index === 1
          ? 'bg-gradient-hero'
          : 'bg-gradient-cool';

        return (
          <Card
            key={stat.label}
            className="border-0 shadow-lg hover:shadow-xl transition-all duration-300 hover:-translate-y-1 animate-slide-up"
            style={{ animationDelay: `${index * 100}ms` }}
          >
            <CardContent className="pt-6 pb-6">
              <div className="space-y-3">
                {/* Icon with gradient background */}
                <div className="flex items-center justify-between">
                  <div className={`p-3 rounded-xl ${gradientClass} shadow-md`}>
                    <Icon className="h-6 w-6 text-white" />
                  </div>
                  {stat.trend !== undefined && (
                    <div className="flex items-center gap-1">
                      {isPositiveTrend ? (
                        <TrendingUp className="h-4 w-4 text-success" />
                      ) : (
                        <TrendingDown className="h-4 w-4 text-destructive" />
                      )}
                      <span
                        className={`text-sm font-bold ${
                          isPositiveTrend ? 'text-success' : 'text-destructive'
                        }`}
                      >
                        {isPositiveTrend ? '+' : ''}
                        {stat.trend}%
                      </span>
                    </div>
                  )}
                </div>

                {/* Label */}
                <div>
                  <p className="text-sm font-medium text-muted-foreground uppercase tracking-wide">
                    {stat.label}
                  </p>
                </div>

                {/* Value */}
                <div>
                  <p className="text-4xl font-bold tracking-tight">{stat.value}</p>
                </div>

                {/* Description with better visual */}
                <div className="pt-2 border-t border-border/50">
                  <p className="text-xs text-muted-foreground leading-relaxed">
                    {stat.description}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        );
      })}
    </div>
  );
}
