'use client';

import { Card, CardContent } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';

/**
 * DashboardSkeleton - Loading skeleton for the dashboard page
 * Matches the actual dashboard layout to prevent layout shift
 */
export function DashboardSkeleton() {
  return (
    <div className="min-h-screen bg-muted/20">
      {/* Header Skeleton */}
      <div className="border-b bg-background">
        <div className="container mx-auto px-4 py-4 max-w-7xl">
          <div className="flex items-center justify-between">
            <Skeleton className="h-8 w-40" />
            <div className="flex items-center gap-4">
              <Skeleton className="h-10 w-32" />
              <Skeleton className="h-10 w-10 rounded-full" />
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8 max-w-7xl">
        {/* Welcome Section Skeleton */}
        <div className="mb-8">
          <Card className="border-0 bg-gradient-hero shadow-lg overflow-hidden">
            <CardContent className="pt-8 pb-8">
              <div className="space-y-4">
                {/* Greeting */}
                <Skeleton className="h-9 w-64 bg-white/20" />

                {/* Motivational message */}
                <Skeleton className="h-6 w-96 bg-white/20" />

                {/* Progress bar */}
                <div className="space-y-2 pt-2">
                  <div className="flex items-center justify-between">
                    <Skeleton className="h-4 w-32 bg-white/20" />
                    <Skeleton className="h-4 w-12 bg-white/20" />
                  </div>
                  <Skeleton className="h-3 w-full bg-white/20 rounded-full" />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="space-y-6">
          {/* Draft Card Skeleton */}
          <Card>
            <CardContent className="pt-6">
              <div className="space-y-4">
                <div className="flex items-start justify-between">
                  <div className="space-y-2 flex-1">
                    <Skeleton className="h-6 w-48" />
                    <Skeleton className="h-4 w-64" />
                  </div>
                  <Skeleton className="h-10 w-32" />
                </div>
                <div className="flex gap-2">
                  <Skeleton className="h-9 w-28" />
                  <Skeleton className="h-9 w-28" />
                  <Skeleton className="h-9 w-28" />
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Article Cards Skeleton */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <Skeleton className="h-6 w-48" />
              <Skeleton className="h-9 w-24" />
            </div>

            {/* 3 Article Cards */}
            {[1, 2, 3].map((i) => (
              <Card key={i}>
                <CardContent className="pt-6">
                  <div className="flex gap-4">
                    {/* Image placeholder */}
                    <Skeleton className="h-24 w-24 rounded-lg flex-shrink-0" />

                    {/* Content */}
                    <div className="flex-1 space-y-2">
                      <Skeleton className="h-5 w-3/4" />
                      <Skeleton className="h-4 w-full" />
                      <Skeleton className="h-4 w-5/6" />
                      <div className="flex gap-4 pt-2">
                        <Skeleton className="h-3 w-20" />
                        <Skeleton className="h-3 w-20" />
                        <Skeleton className="h-3 w-20" />
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Stats Overview Skeleton */}
          <Card>
            <CardContent className="pt-6">
              <div className="space-y-4">
                <Skeleton className="h-6 w-32" />
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {[1, 2, 3].map((i) => (
                    <div key={i} className="space-y-2">
                      <Skeleton className="h-4 w-24" />
                      <Skeleton className="h-8 w-16" />
                    </div>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
}
