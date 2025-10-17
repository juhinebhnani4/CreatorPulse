'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Checkbox } from '@/components/ui/checkbox';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { TrendingUp, TrendingDown, Eye, Copy, Send, Loader2, Trash2, RefreshCw, Edit } from 'lucide-react';
import { useToast } from '@/lib/hooks/use-toast';
import { AppHeader } from '@/components/layout/app-header';
import { useAuthStore } from '@/lib/stores/auth-store';
import { useWorkspaceStore } from '@/lib/stores/workspace-store';
import { newslettersApi } from '@/lib/api/newsletters';
import { analyticsApi } from '@/lib/api/analytics';
import { Newsletter } from '@/types/newsletter';

interface NewsletterWithAnalytics extends Newsletter {
  subscriberCount?: number;
  openRate?: number;
  openRateTrend?: number;
  clicks?: number;
  clicksTrend?: number;
  unsubscribes?: number;
}

export default function HistoryPage() {
  const router = useRouter();
  const { toast } = useToast();
  const { isAuthenticated, _hasHydrated } = useAuthStore();
  const { currentWorkspace } = useWorkspaceStore();
  const [isMounted, setIsMounted] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [newsletters, setNewsletters] = useState<NewsletterWithAnalytics[]>([]);
  const [dateFilter, setDateFilter] = useState('30');
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [isDeleting, setIsDeleting] = useState(false);

  useEffect(() => {
    setIsMounted(true);
  }, []);

  useEffect(() => {
    if (!isMounted || !_hasHydrated) return;

    if (!isAuthenticated) {
      router.push('/login');
      return;
    }

    if (!currentWorkspace) {
      return;
    }

    async function fetchNewsletters() {
      try {
        setIsLoading(true);

        // Fetch newsletters for the workspace
        const newsletterList = await newslettersApi.list(currentWorkspace!.id);

        // Filter by date range
        const now = new Date();
        const daysBack = parseInt(dateFilter);
        const filteredNewsletters = daysBack === 0
          ? newsletterList
          : newsletterList.filter(n => {
              const createdDate = new Date(n.created_at);
              const diffTime = Math.abs(now.getTime() - createdDate.getTime());
              const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
              return diffDays <= daysBack;
            });

        // TODO: Fetch analytics for each newsletter
        // For now, we'll use the newsletters as-is without analytics
        // Once analytics API is connected, uncomment below:
        /*
        const newslettersWithAnalytics = await Promise.all(
          sentNewsletters.map(async (newsletter) => {
            try {
              const analytics = await analyticsApi.getNewsletterAnalytics(newsletter.id);
              return {
                ...newsletter,
                subscriberCount: analytics.total_recipients,
                openRate: analytics.open_rate,
                clicks: analytics.click_count,
                unsubscribes: analytics.unsubscribe_count,
              };
            } catch {
              return newsletter;
            }
          })
        );
        setNewsletters(newslettersWithAnalytics);
        */

        setNewsletters(filteredNewsletters);
      } catch (error: any) {
        console.error('Failed to fetch newsletters:', error);
        toast({
          title: 'Error',
          description: error.message || 'Failed to load newsletter history',
          variant: 'destructive',
        });
      } finally {
        setIsLoading(false);
      }
    }

    fetchNewsletters();
  }, [isAuthenticated, isMounted, _hasHydrated, currentWorkspace, dateFilter, router, toast]);

  if (!isMounted || !_hasHydrated || !isAuthenticated) {
    return null;
  }

  const handleView = (id: string) => {
    router.push(`/app/newsletters/${id}`);
  };

  const handleDuplicate = async (id: string) => {
    try {
      const newsletter = await newslettersApi.get(id);

      // Create a new draft based on this newsletter
      if (currentWorkspace) {
        const duplicated = await newslettersApi.generate({
          workspace_id: currentWorkspace.id,
          title: `${newsletter.title} (Copy)`,
          max_items: 15,
          days_back: 7,
        });

        toast({
          title: 'Newsletter Duplicated',
          description: 'A copy has been created in drafts',
        });

        router.push('/app');
      }
    } catch (error: any) {
      toast({
        title: 'Failed to Duplicate',
        description: error.message || 'Could not duplicate newsletter',
        variant: 'destructive',
      });
    }
  };

  const handleResend = (id: string) => {
    toast({
      title: 'Resend Newsletter',
      description: 'This feature will be available soon',
    });
  };

  const handleEdit = (id: string) => {
    router.push(`/app/newsletters/${id}/edit`);
  };

  const handleRegenerate = async (id: string) => {
    try {
      const newsletter = await newslettersApi.get(id);

      if (currentWorkspace) {
        toast({
          title: 'Regenerating Newsletter',
          description: 'Creating a fresh version based on latest content...',
        });

        const regenerated = await newslettersApi.generate({
          workspace_id: currentWorkspace.id,
          title: newsletter.title,
          max_items: 15,
          days_back: 7,
        });

        toast({
          title: '✓ Newsletter Regenerated',
          description: 'A new version has been created',
          className: 'animate-celebration',
        });

        // Refresh the list
        router.refresh();
      }
    } catch (error: any) {
      toast({
        title: 'Failed to Regenerate',
        description: error.message || 'Could not regenerate newsletter',
        variant: 'destructive',
      });
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this newsletter? This action cannot be undone.')) {
      return;
    }

    try {
      await newslettersApi.delete(id);

      toast({
        title: '✓ Newsletter Deleted',
        description: 'The newsletter has been removed',
      });

      // Remove from local state
      setNewsletters(newsletters.filter(n => n.id !== id));
    } catch (error: any) {
      toast({
        title: 'Failed to Delete',
        description: error.message || 'Could not delete newsletter',
        variant: 'destructive',
      });
    }
  };

  const toggleSelection = (id: string) => {
    setSelectedIds(prev =>
      prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]
    );
  };

  const toggleSelectAll = () => {
    if (selectedIds.length === newsletters.length) {
      setSelectedIds([]);
    } else {
      setSelectedIds(newsletters.map(n => n.id));
    }
  };

  const handleBulkDelete = async () => {
    if (selectedIds.length === 0) return;

    if (!confirm(`Are you sure you want to delete ${selectedIds.length} newsletter${selectedIds.length > 1 ? 's' : ''}? This action cannot be undone.`)) {
      return;
    }

    try {
      setIsDeleting(true);

      // Delete all selected newsletters
      await Promise.all(selectedIds.map(id => newslettersApi.delete(id)));

      toast({
        title: '✓ Newsletters Deleted',
        description: `${selectedIds.length} newsletter${selectedIds.length > 1 ? 's' : ''} removed successfully`,
      });

      // Remove from local state
      setNewsletters(newsletters.filter(n => !selectedIds.includes(n.id)));
      setSelectedIds([]);
    } catch (error: any) {
      toast({
        title: 'Bulk Delete Failed',
        description: error.message || 'Could not delete all newsletters',
        variant: 'destructive',
      });
    } finally {
      setIsDeleting(false);
    }
  };

  return (
    <div className="min-h-screen bg-muted/20">
      <AppHeader />

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8 max-w-6xl">
        {/* Header with gradient */}
        <div className="mb-10 animate-slide-up">
          <h1 className="text-4xl font-bold mb-3 text-gradient">Newsletter History</h1>
          <p className="text-lg text-muted-foreground">View past newsletters and performance metrics</p>
        </div>

        {/* Filters Bar */}
        <div className="mb-8 flex flex-wrap gap-3 items-center animate-slide-up" style={{ animationDelay: '100ms' }}>
          {/* Bulk Actions */}
          {newsletters.length > 0 && (
            <div className="flex items-center gap-3">
              <Checkbox
                checked={selectedIds.length === newsletters.length && newsletters.length > 0}
                onCheckedChange={toggleSelectAll}
                aria-label="Select all newsletters"
              />
              <span className="text-sm text-muted-foreground">
                {selectedIds.length > 0 ? `${selectedIds.length} selected` : 'Select all'}
              </span>
              {selectedIds.length > 0 && (
                <Button
                  variant="destructive"
                  size="sm"
                  onClick={handleBulkDelete}
                  disabled={isDeleting}
                  className="rounded-xl"
                >
                  {isDeleting ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      Deleting...
                    </>
                  ) : (
                    <>
                      <Trash2 className="h-4 w-4 mr-2" />
                      Delete Selected
                    </>
                  )}
                </Button>
              )}
            </div>
          )}

          <Select value={dateFilter} onValueChange={setDateFilter}>
            <SelectTrigger className="w-[200px] h-11 rounded-xl border-2">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="7">Last 7 days</SelectItem>
              <SelectItem value="30">Last 30 days</SelectItem>
              <SelectItem value="90">Last 90 days</SelectItem>
              <SelectItem value="0">All time</SelectItem>
            </SelectContent>
          </Select>

          {/* Summary Stats */}
          <div className="flex-1" />
          <div className="flex items-center gap-6 text-sm">
            <div className="text-center">
              <p className="font-bold text-2xl">{newsletters.length}</p>
              <p className="text-muted-foreground">Sent</p>
            </div>
            <div className="text-center">
              <p className="font-bold text-2xl text-success">
                {newsletters.length > 0
                  ? Math.round(newsletters.reduce((acc, n) => acc + (n.openRate || 0), 0) / newsletters.length)
                  : 0}%
              </p>
              <p className="text-muted-foreground">Avg Open</p>
            </div>
          </div>
        </div>

        {/* Loading State */}
        {isLoading && (
          <div className="flex items-center justify-center py-20">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
          </div>
        )}

        {/* Newsletter List */}
        {!isLoading && newsletters.length > 0 && (
          <div className="space-y-5">
          {newsletters.map((newsletter, index) => {
            // Determine performance level (if analytics available)
            const hasAnalytics = newsletter.openRate !== undefined;
            const performanceLevel = hasAnalytics
              ? (newsletter.openRate! >= 35 ? 'excellent' : newsletter.openRate! >= 25 ? 'good' : 'needs-improvement')
              : 'unknown';
            const performanceColor = performanceLevel === 'excellent' ? 'text-success' : performanceLevel === 'good' ? 'text-warning' : 'text-muted-foreground';
            const performanceBg = performanceLevel === 'excellent' ? 'bg-success/10' : performanceLevel === 'good' ? 'bg-warning/10' : 'bg-muted';

            const sentAt = newsletter.sent_at ? new Date(newsletter.sent_at) : new Date();

            return (
              <Card
                key={newsletter.id}
                className="border-0 shadow-lg hover:shadow-xl transition-all duration-300 animate-slide-up"
                style={{ animationDelay: `${(index + 2) * 100}ms` }}
              >
                <CardContent className="pt-6 pb-6">
                  <div className="space-y-5">
                    {/* Header with performance indicator */}
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex items-start gap-3 flex-1">
                        <Checkbox
                          checked={selectedIds.includes(newsletter.id)}
                          onCheckedChange={() => toggleSelection(newsletter.id)}
                          className="mt-1"
                          aria-label={`Select ${newsletter.title}`}
                        />
                        <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <h3 className="text-xl font-bold">
                            {newsletter.subject_line || newsletter.title}
                          </h3>
                          {/* Status Badge */}
                          <Badge
                            className={`border-0 ${
                              newsletter.status === 'sent'
                                ? 'bg-success/10 text-success'
                                : newsletter.status === 'draft'
                                ? 'bg-warning/10 text-warning'
                                : newsletter.status === 'scheduled'
                                ? 'bg-blue-500/10 text-blue-600'
                                : 'bg-destructive/10 text-destructive'
                            }`}
                          >
                            {newsletter.status === 'sent' ? '✓ Sent' : newsletter.status === 'draft' ? '📝 Draft' : newsletter.status === 'scheduled' ? '⏰ Scheduled' : '✗ Failed'}
                          </Badge>
                          {hasAnalytics && (
                            <Badge className={`${performanceBg} ${performanceColor} border-0`}>
                              {performanceLevel === 'excellent' ? '🔥 Excellent' : performanceLevel === 'good' ? '👍 Good' : '📈 Can Improve'}
                            </Badge>
                          )}
                        </div>
                        <p className="text-sm text-muted-foreground flex items-center gap-2">
                          {newsletter.subscriberCount && (
                            <>
                              <span className="font-medium">{newsletter.subscriberCount.toLocaleString()} subscribers</span>
                              <span>•</span>
                            </>
                          )}
                          <span>{new Intl.DateTimeFormat('en-US', {
                            month: 'short',
                            day: 'numeric',
                            hour: 'numeric',
                            minute: 'numeric',
                          }).format(sentAt)}</span>
                        </p>
                        </div>
                      </div>
                    </div>

                    {/* Metrics with visual improvements */}
                    {hasAnalytics ? (
                      <div className="grid grid-cols-3 gap-6 py-5 bg-muted/30 rounded-xl px-6">
                        <div>
                          <div className="flex items-baseline gap-2 mb-1">
                            <span className="text-3xl font-bold">{newsletter.openRate}%</span>
                            {newsletter.openRateTrend !== undefined && newsletter.openRateTrend !== 0 && (
                              <span
                                className={`text-sm font-bold inline-flex items-center gap-1 ${
                                  newsletter.openRateTrend >= 0
                                    ? 'text-success'
                                    : 'text-destructive'
                                }`}
                              >
                                {newsletter.openRateTrend >= 0 ? (
                                  <TrendingUp className="h-4 w-4" />
                                ) : (
                                  <TrendingDown className="h-4 w-4" />
                                )}
                                {Math.abs(newsletter.openRateTrend)}%
                              </span>
                            )}
                          </div>
                          <p className="text-xs text-muted-foreground font-medium uppercase tracking-wide">Open Rate</p>
                        </div>

                        <div>
                          <div className="flex items-baseline gap-2 mb-1">
                            <span className="text-3xl font-bold">{newsletter.clicks || 0}</span>
                            {newsletter.clicksTrend !== undefined && newsletter.clicksTrend !== 0 && (
                              <span
                                className={`text-sm font-bold inline-flex items-center gap-1 ${
                                  newsletter.clicksTrend >= 0
                                    ? 'text-success'
                                    : 'text-destructive'
                                }`}
                              >
                                {newsletter.clicksTrend >= 0 ? (
                                  <TrendingUp className="h-4 w-4" />
                                ) : (
                                  <TrendingDown className="h-4 w-4" />
                                )}
                                {Math.abs(newsletter.clicksTrend)}
                              </span>
                            )}
                          </div>
                          <p className="text-xs text-muted-foreground font-medium uppercase tracking-wide">Total Clicks</p>
                        </div>

                        <div>
                          <div className="flex items-baseline gap-2 mb-1">
                            <span className="text-3xl font-bold">{newsletter.unsubscribes || 0}</span>
                          </div>
                          <p className="text-xs text-muted-foreground font-medium uppercase tracking-wide">Unsubscribes</p>
                        </div>
                      </div>
                    ) : (
                      <div className="py-4 text-center text-sm text-muted-foreground">
                        Analytics will be available once tracking is enabled
                      </div>
                    )}

                    {/* Actions with better styling */}
                    <div className="flex gap-3 flex-wrap">
                      <Button
                        variant="outline"
                        size="default"
                        onClick={() => handleView(newsletter.id)}
                        className="rounded-xl hover:bg-primary hover:text-primary-foreground transition-colors"
                      >
                        <Eye className="h-4 w-4 mr-2" />
                        View
                      </Button>
                      {newsletter.status === 'draft' && (
                        <Button
                          variant="outline"
                          size="default"
                          onClick={() => handleEdit(newsletter.id)}
                          className="rounded-xl hover:bg-blue-500 hover:text-white transition-colors"
                        >
                          <Edit className="h-4 w-4 mr-2" />
                          Edit
                        </Button>
                      )}
                      <Button
                        variant="outline"
                        size="default"
                        onClick={() => handleRegenerate(newsletter.id)}
                        className="rounded-xl hover:bg-purple-500 hover:text-white transition-colors"
                      >
                        <RefreshCw className="h-4 w-4 mr-2" />
                        Regenerate
                      </Button>
                      <Button
                        variant="outline"
                        size="default"
                        onClick={() => handleDuplicate(newsletter.id)}
                        className="rounded-xl hover:bg-secondary hover:text-secondary-foreground transition-colors"
                      >
                        <Copy className="h-4 w-4 mr-2" />
                        Duplicate
                      </Button>
                      {newsletter.status === 'sent' && (
                        <Button
                          variant="outline"
                          size="default"
                          onClick={() => handleResend(newsletter.id)}
                          className="rounded-xl hover:bg-accent hover:text-accent-foreground transition-colors"
                        >
                          <Send className="h-4 w-4 mr-2" />
                          Resend
                        </Button>
                      )}
                      <Button
                        variant="outline"
                        size="default"
                        onClick={() => handleDelete(newsletter.id)}
                        className="rounded-xl hover:bg-destructive hover:text-destructive-foreground transition-colors"
                      >
                        <Trash2 className="h-4 w-4 mr-2" />
                        Delete
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            );
          })}
          </div>
        )}

        {/* Empty State */}
        {!isLoading && newsletters.length === 0 && (
          <Card>
            <CardContent className="py-12 text-center">
              <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-muted mb-4">
                <Send className="h-8 w-8 text-muted-foreground" />
              </div>
              <h3 className="text-lg font-semibold mb-2">No newsletters sent yet</h3>
              <p className="text-sm text-muted-foreground mb-4">
                Your sent newsletters will appear here once you send your first one
              </p>
              <Button onClick={() => router.push('/app')}>
                Go to Dashboard
              </Button>
            </CardContent>
          </Card>
        )}
      </main>
    </div>
  );
}
