'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/lib/stores/auth-store';
import { useWorkspaceStore } from '@/lib/stores/workspace-store';
import { contentApi, ContentItem, ContentStats } from '@/lib/api/content';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { useToast } from '@/lib/hooks/use-toast';
import { Loader2, Search, RefreshCw, ThumbsUp, ThumbsDown, ExternalLink, Calendar, User } from 'lucide-react';
import { AppHeader } from '@/components/layout/app-header';
import { Thumbnail } from '@/components/ui/thumbnail';
import { feedbackApi } from '@/lib/api/feedback';

export default function ContentPage() {
  const router = useRouter();
  const { isAuthenticated, _hasHydrated } = useAuthStore();
  const { currentWorkspace } = useWorkspaceStore();
  const { toast } = useToast();

  const [isMounted, setIsMounted] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [isScraping, setIsScraping] = useState(false);
  const [stats, setStats] = useState<ContentStats | null>(null);
  const [items, setItems] = useState<ContentItem[]>([]);
  const [total, setTotal] = useState(0);

  // Filters
  const [searchQuery, setSearchQuery] = useState('');
  const [sourceFilter, setSourceFilter] = useState<string>('all');
  const [daysFilter, setDaysFilter] = useState<number>(7);

  useEffect(() => {
    setIsMounted(true);
  }, []);

  useEffect(() => {
    if (!isMounted || !_hasHydrated) return;

    if (!isAuthenticated) {
      router.push('/login');
      return;
    }

    fetchData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isAuthenticated, isMounted, _hasHydrated, currentWorkspace, sourceFilter, daysFilter]);

  const fetchData = async () => {
    if (!currentWorkspace) {
      console.warn('[Content] No workspace selected');
      setIsLoading(false);
      setItems([]);
      setTotal(0);
      setStats(null);
      return;
    }

    try {
      setIsLoading(true);

      // Fetch stats
      const statsData = await contentApi.getStats(currentWorkspace.id);
      setStats(statsData);

      // Fetch items
      const contentData = sourceFilter === 'all'
        ? await contentApi.list(currentWorkspace.id, {
            days: daysFilter,
            limit: 100,
          })
        : await contentApi.getBySource(currentWorkspace.id, sourceFilter, {
            days: daysFilter,
            limit: 100,
          });

      setItems(contentData.items);
      setTotal(contentData.total);

      // DEBUG: Log first item to verify structure
      if (contentData.items.length > 0) {
        console.log('[Content] Sample item structure:', {
          id: contentData.items[0].id,
          hasId: !!contentData.items[0].id,
          idType: typeof contentData.items[0].id,
          keys: Object.keys(contentData.items[0])
        });
      }
    } catch (error: any) {
      console.error('Failed to fetch content:', error);
      toast({
        title: 'Error',
        description: error.message || 'Failed to load content',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleScrape = async () => {
    if (!currentWorkspace) return;

    try {
      setIsScraping(true);
      toast({
        title: 'Scraping Content',
        description: 'Fetching content from your sources...',
      });

      const result = await contentApi.scrape({
        workspace_id: currentWorkspace.id,
      });

      toast({
        title: '✓ Content Scraped',
        description: `Successfully fetched ${result.total_items} items from ${Object.keys(result.items_by_source).length} sources`,
        className: 'animate-celebration',
      });

      // Refresh data
      await fetchData();
    } catch (error: any) {
      console.error('Failed to scrape:', error);
      toast({
        title: 'Scraping Failed',
        description: error.message || 'Failed to scrape content',
        variant: 'destructive',
      });
    } finally {
      setIsScraping(false);
    }
  };

  const filteredItems = items.filter(item =>
    searchQuery === '' ||
    item.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    item.content.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // Source icon and color helpers
  const getSourceIcon = (source: string) => {
    const icons: Record<string, string> = {
      'reddit': '🔴',
      'rss': '🟠',
      'twitter': '🔵',
      'x': '🔵',
      'youtube': '🟢',
      'blog': '🟣'
    };
    return icons[source.toLowerCase()] || '📄';
  };

  const getSourceColor = (source: string) => {
    const colors: Record<string, 'destructive' | 'default' | 'secondary' | 'outline'> = {
      'reddit': 'destructive',
      'rss': 'secondary',
      'twitter': 'default',
      'x': 'default',
      'youtube': 'outline',
      'blog': 'secondary'
    };
    return colors[source.toLowerCase()] || 'default';
  };

  // Feedback handler
  const handleFeedback = async (itemId: string, rating: 'positive' | 'negative') => {
    if (!currentWorkspace) return;

    // CRITICAL: Validate itemId exists and is not empty
    if (!itemId || itemId === 'undefined' || itemId === 'null') {
      console.error('[Feedback] Invalid itemId:', itemId);
      toast({
        title: 'Invalid Item',
        description: 'Cannot submit feedback for invalid content item',
        variant: 'destructive',
      });
      return;
    }

    console.log('[Feedback] Submitting feedback:', {
      itemId,
      rating,
      itemIdType: typeof itemId,
      itemIdLength: itemId.length
    });

    try {
      const payload = {
        content_item_id: itemId,
        rating: rating,
        included_in_final: false,
        feedback_notes: 'Quick feedback from content library'
      };

      console.log('[Feedback] Payload before API call:', JSON.stringify(payload, null, 2));

      await feedbackApi.createItemFeedback(payload);

      toast({
        title: '✓ Feedback Recorded',
        description: 'We\'ll use this to improve future curation',
        duration: 2000
      });
    } catch (error: any) {
      console.error('[Feedback] Error details:', error);
      toast({
        title: 'Feedback Failed',
        description: error.message || 'Failed to record feedback',
        variant: 'destructive',
      });
    }
  };

  if (!isMounted || !_hasHydrated) {
    return null;
  }

  // Show workspace error if no workspace selected
  if (!currentWorkspace) {
    return (
      <div className="min-h-screen bg-muted/20">
        <AppHeader />
        <main className="container mx-auto px-4 py-8 max-w-7xl">
          <Card className="p-12 text-center">
            <h2 className="text-2xl font-semibold mb-2">No Workspace Selected</h2>
            <p className="text-muted-foreground mb-6">
              Please refresh the page or select a workspace to view content
            </p>
            <Button onClick={() => router.push('/app')} className="bg-gradient-warm hover:opacity-90">
              Go to Dashboard
            </Button>
          </Card>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-muted/20">
      <AppHeader />

      <main className="container mx-auto px-4 py-8 max-w-7xl">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-2 bg-gradient-to-r from-primary to-primary/60 bg-clip-text text-transparent">
            Content Library
          </h1>
          <p className="text-muted-foreground">
            View and manage all scraped content from your sources
          </p>
        </div>

        {/* Stats Row */}
        {stats && (
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4 mb-6">
            <Card className="p-4 bg-gradient-warm/10 border-none shadow-md hover:-translate-y-1 transition-transform">
              <p className="text-xs uppercase tracking-wide text-muted-foreground mb-1">Total Items</p>
              <p className="text-3xl font-bold">{stats.total_items}</p>
            </Card>

            {Object.entries(stats.items_by_source).map(([source, count]) => (
              <Card
                key={source}
                className="p-4 bg-background border shadow-md hover:-translate-y-1 transition-transform cursor-pointer"
                onClick={() => setSourceFilter(source)}
              >
                <p className="text-xs uppercase tracking-wide text-muted-foreground mb-1">{source}</p>
                <p className="text-3xl font-bold">{count}</p>
              </Card>
            ))}
          </div>
        )}

        {/* Filter Bar */}
        <Card className="p-4 mb-6 shadow-md">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search content..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10 h-11"
              />
            </div>

            <Select value={sourceFilter} onValueChange={setSourceFilter}>
              <SelectTrigger className="w-full md:w-[180px] h-11">
                <SelectValue placeholder="All Sources" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Sources</SelectItem>
                <SelectItem value="reddit">Reddit</SelectItem>
                <SelectItem value="rss">RSS</SelectItem>
                <SelectItem value="x">Twitter/X</SelectItem>
                <SelectItem value="youtube">YouTube</SelectItem>
                <SelectItem value="blog">Blogs</SelectItem>
              </SelectContent>
            </Select>

            <Select value={daysFilter.toString()} onValueChange={(val) => setDaysFilter(parseInt(val))}>
              <SelectTrigger className="w-full md:w-[180px] h-11">
                <SelectValue placeholder="Time Range" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="3">Last 3 days</SelectItem>
                <SelectItem value="7">Last 7 days</SelectItem>
                <SelectItem value="14">Last 14 days</SelectItem>
                <SelectItem value="30">Last 30 days</SelectItem>
              </SelectContent>
            </Select>

            <Button
              onClick={handleScrape}
              disabled={isScraping}
              className="bg-gradient-warm hover:opacity-90 h-11"
            >
              {isScraping ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Scraping...
                </>
              ) : (
                <>
                  <RefreshCw className="h-4 w-4 mr-2" />
                  Scrape Now
                </>
              )}
            </Button>
          </div>
        </Card>

        {/* Content Grid */}
        {isLoading ? (
          <div className="flex items-center justify-center py-20">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
            <span className="ml-3 text-muted-foreground">Loading content...</span>
          </div>
        ) : filteredItems.length === 0 ? (
          <Card className="p-12 text-center shadow-md">
            <p className="text-xl font-semibold mb-2">No Content Found</p>
            <p className="text-muted-foreground mb-6">
              {searchQuery
                ? 'Try adjusting your search or filters'
                : 'Scrape content from your sources to get started'}
            </p>
            {!searchQuery && (
              <Button onClick={handleScrape} className="bg-gradient-warm hover:opacity-90">
                <RefreshCw className="h-4 w-4 mr-2" />
                Scrape Now
              </Button>
            )}
          </Card>
        ) : (
          <>
            <div className="mb-4 flex items-center justify-between">
              <p className="text-sm text-muted-foreground">
                Showing {filteredItems.length} of {total} items
              </p>
            </div>

            <div className="grid gap-4">
              {filteredItems.map((item, index) => (
                <Card
                  key={item.id}
                  data-testid="content-card"
                  data-item-id={item.id}
                  data-source={item.source_type}
                  className="overflow-hidden shadow-md hover:shadow-lg transition-shadow animate-slide-up"
                  style={{ animationDelay: `${index * 50}ms` }}
                >
                  <div className="flex gap-4">
                    {/* Thumbnail */}
                    {item.image_url && (
                      <Thumbnail
                        src={item.image_url}
                        alt={item.title}
                        source={item.source_type}
                        className="w-48 h-32 object-cover flex-shrink-0"
                      />
                    )}

                    {/* Content */}
                    <div className="flex-1 p-6 min-w-0">
                      <div className="flex items-center gap-2 mb-2">
                        <Badge variant={getSourceColor(item.source_type)} className="text-xs" data-testid="source-badge">
                          {getSourceIcon(item.source_type)} {item.source_type}
                        </Badge>
                        {item.score && item.score > 0 && (
                          <Badge variant="outline" className="text-xs">
                            ⬆ {item.score}
                          </Badge>
                        )}
                      </div>

                      <h3 className="text-lg font-semibold mb-2 flex items-center gap-2">
                        <a
                          href={item.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="hover:text-primary transition-colors hover:underline flex-1 truncate"
                        >
                          {item.title}
                        </a>
                        <a
                          href={item.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-muted-foreground hover:text-primary transition-colors flex-shrink-0"
                          aria-label="Open in new tab"
                        >
                          <ExternalLink className="h-4 w-4" />
                        </a>
                      </h3>

                      <p className="text-sm text-muted-foreground mb-4 line-clamp-2">
                        {item.summary || item.content}
                      </p>

                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-4 text-xs text-muted-foreground">
                          {item.author && (
                            <div className="flex items-center gap-1">
                              <User className="h-3 w-3" />
                              <span className="truncate max-w-[150px]">{item.author}</span>
                            </div>
                          )}
                          <div className="flex items-center gap-1">
                            <Calendar className="h-3 w-3" />
                            {new Date(item.published_at).toLocaleDateString()}
                          </div>
                        </div>

                        <div className="flex gap-2">
                          <Button
                            size="sm"
                            variant="ghost"
                            className="text-muted-foreground hover:text-success gap-1"
                            onClick={() => handleFeedback(item.id, 'positive')}
                            data-testid="feedback-keep-button"
                          >
                            <ThumbsUp className="h-4 w-4" />
                            Keep
                          </Button>
                          <Button
                            size="sm"
                            variant="ghost"
                            className="text-muted-foreground hover:text-destructive gap-1"
                            onClick={() => handleFeedback(item.id, 'negative')}
                            data-testid="feedback-skip-button"
                          >
                            <ThumbsDown className="h-4 w-4" />
                            Skip
                          </Button>
                        </div>
                      </div>
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          </>
        )}
      </main>
    </div>
  );
}
