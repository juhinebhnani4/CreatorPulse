'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/lib/stores/auth-store';
import { useWorkspaceStore } from '@/lib/stores/workspace-store';
import { authApi } from '@/lib/api/auth';
import { workspacesApi } from '@/lib/api/workspaces';
import { newslettersApi } from '@/lib/api/newsletters';
import { contentApi, ContentStats } from '@/lib/api/content';
import { deliveryApi } from '@/lib/api/delivery';
import { schedulerApi } from '@/lib/api/scheduler';
import { subscribersApi } from '@/lib/api/subscribers';
import { analyticsApi } from '@/lib/api/analytics';
import { transformNewsletterItemToFrontend } from '@/lib/utils/type-transformers';
import { Button } from '@/components/ui/button';
import { DraftStatusCard } from '@/components/dashboard/draft-status-card';
import { ArticleCard } from '@/components/dashboard/article-card';
import { QuickSourceManager } from '@/components/dashboard/quick-source-manager';
import { StatsOverview } from '@/components/dashboard/stats-overview';
import { EmptyState } from '@/components/dashboard/empty-state';
import { RecentActivity } from '@/components/dashboard/recent-activity';
import { WelcomeSection } from '@/components/dashboard/welcome-section';
import { EnhancedDraftCard } from '@/components/dashboard/enhanced-draft-card';
import { UnifiedSourceSetup } from '@/components/dashboard/unified-source-setup';
import { MotivationalTip } from '@/components/dashboard/motivational-tip';
import { DraftEditorModal } from '@/components/modals/draft-editor-modal';
import { SendConfirmationModal } from '@/components/modals/send-confirmation-modal';
import { AddSourceModal } from '@/components/modals/add-source-modal';
import { SendTestModal } from '@/components/modals/send-test-modal';
import { ScheduleSendModal } from '@/components/modals/schedule-send-modal';
import { GenerationSettingsModal, GenerationSettings } from '@/components/modals/generation-settings-modal';
import { AppHeader } from '@/components/layout/app-header';
import { useToast } from '@/lib/hooks/use-toast';
import { Newsletter } from '@/types/newsletter';
import { Workspace, WorkspaceConfig } from '@/types/workspace';

export default function DashboardPage() {
  const router = useRouter();
  const { user, isAuthenticated, clearAuth, _hasHydrated } = useAuthStore();
  const { currentWorkspace, setCurrentWorkspace } = useWorkspaceStore();
  const { toast } = useToast();
  const [isLoading, setIsLoading] = useState(true);
  const [isMounted, setIsMounted] = useState(false);

  // Real API data
  const [workspace, setWorkspaceData] = useState<Workspace | null>(null);
  const [config, setConfig] = useState<WorkspaceConfig | null>(null);
  const [latestNewsletter, setLatestNewsletter] = useState<Newsletter | null>(null);
  const [contentStats, setContentStats] = useState<ContentStats | null>(null);
  const [subscriberCount, setSubscriberCount] = useState<number>(0);
  const [analyticsData, setAnalyticsData] = useState<any | null>(null);
  const [hasSources, setHasSources] = useState(false);
  const [draftStatus, setDraftStatus] = useState<'ready' | 'generating' | 'scheduled' | 'stale' | 'empty'>('empty');

  // Modal states
  const [showDraftEditor, setShowDraftEditor] = useState(false);
  const [showSendConfirmation, setShowSendConfirmation] = useState(false);
  const [showAddSource, setShowAddSource] = useState(false);
  const [showSendTest, setShowSendTest] = useState(false);
  const [showScheduleSend, setShowScheduleSend] = useState(false);
  const [showGenerationSettings, setShowGenerationSettings] = useState(false);

  useEffect(() => {
    setIsMounted(true);
  }, []);

  // Fetch workspace and newsletter data
  useEffect(() => {
    if (!isMounted || !_hasHydrated) return;

    if (!isAuthenticated) {
      router.push('/login');
      return;
    }

    async function fetchData() {
      try {
        setIsLoading(true);

        // Get user's workspaces
        const workspaces = await workspacesApi.list();
        console.log('[Dashboard] Fetched workspaces:', workspaces);

        if (!workspaces || workspaces.length === 0) {
          // Create a default workspace
          try {
            const newWorkspace = await workspacesApi.create({
              name: `${user?.username || 'My'} Workspace`,
              description: 'Default workspace',
            });
            setWorkspaceData(newWorkspace);
            setCurrentWorkspace(newWorkspace);

            toast({
              title: '✓ Workspace Created',
              description: 'Your workspace is ready to use',
            });
          } catch (error: any) {
            console.error('Workspace creation error:', error);

            // If workspace already exists or creation failed, try fetching again
            if (error.message?.includes('already exists') || error.message?.includes('duplicate')) {
              console.log('[Dashboard] Workspace might already exist, retrying fetch...');
              try {
                const retryWorkspaces = await workspacesApi.list();
                if (retryWorkspaces && retryWorkspaces.length > 0) {
                  console.log('[Dashboard] Found existing workspace:', retryWorkspaces[0]);
                  setWorkspaceData(retryWorkspaces[0]);
                  setCurrentWorkspace(retryWorkspaces[0]);

                  toast({
                    title: 'Workspace Loaded',
                    description: 'Using your existing workspace',
                  });
                } else {
                  throw new Error('No workspace found after retry');
                }
              } catch (retryError) {
                console.error('Retry fetch failed:', retryError);
                throw error; // Re-throw original error
              }
            } else {
              // Different error - show to user
              toast({
                title: 'Workspace Creation Failed',
                description: error.message || 'Failed to create workspace',
                variant: 'destructive',
              });
              throw error;
            }
          }
        } else {
          // Use first workspace or current workspace from store
          const ws = currentWorkspace
            ? workspaces.find(w => w.id === currentWorkspace.id) || workspaces[0]
            : workspaces[0];

          if (!ws) {
            throw new Error('No workspace found');
          }

          setWorkspaceData(ws);
          setCurrentWorkspace(ws);

          // Fetch workspace config
          let wsConfig = null;
          try {
            wsConfig = await workspacesApi.getConfig(ws.id);

            // Clean and validate sources
            if (wsConfig.sources) {
              const originalCount = wsConfig.sources.length;
              const cleanedSources = wsConfig.sources.filter((source: any) => {
                // FIX 4: Remove sources with empty configs (no actual sources configured)
                const hasContent =
                  (source.config?.subreddits && source.config.subreddits.length > 0) ||
                  (source.config?.feeds && source.config.feeds.length > 0) ||
                  (source.config?.usernames && source.config.usernames.length > 0) ||
                  (source.config?.channels && source.config.channels.length > 0) ||
                  (source.config?.urls && source.config.urls.length > 0);

                if (!hasContent) {
                  console.warn(`[Dashboard Cleanup] Removing empty ${source.type} source config with no actual sources`);
                  return false;
                }

                // Validate Reddit sources don't contain @ symbols
                if (source.type === 'reddit' && source.config?.subreddits) {
                  const hasInvalidSub = source.config.subreddits.some((sub: string) => {
                    const cleaned = sub.replace(/^r\//, '');
                    return cleaned.startsWith('@');
                  });
                  if (hasInvalidSub) {
                    console.warn(`Removing invalid Reddit source with @ symbol:`, source);
                    return false;
                  }
                }

                // Validate Twitter sources don't contain r/ prefix
                if ((source.type === 'x' || source.type === 'twitter') && source.config?.usernames) {
                  const hasInvalidUser = source.config.usernames.some((user: string) => {
                    const cleaned = user.replace(/^@/, '');
                    return cleaned.startsWith('r/');
                  });
                  if (hasInvalidUser) {
                    console.warn(`Removing invalid Twitter source with r/ prefix:`, source);
                    return false;
                  }
                }

                return true;
              });

              // FIX 4: If we cleaned anything, save the cleaned config back to database
              if (cleanedSources.length < originalCount) {
                const removedCount = originalCount - cleanedSources.length;
                console.log(`[Dashboard Cleanup] Cleaned ${removedCount} invalid source(s) from config. Saving cleaned config...`);

                wsConfig.sources = cleanedSources;

                // Save the cleaned config back to the database
                try {
                  await workspacesApi.updateConfig(ws.id, { sources: cleanedSources });
                  console.log('[Dashboard Cleanup] Successfully saved cleaned config to database');
                } catch (saveError) {
                  console.error('[Dashboard Cleanup] Failed to save cleaned config:', saveError);
                }
              } else {
                wsConfig.sources = cleanedSources;
              }
            }

            setConfig(wsConfig);
            setHasSources(wsConfig.sources?.some(s => s.enabled) || false);
          } catch (error) {
            console.error('Failed to fetch config:', error);
            setHasSources(false);
          }

          // Fetch content stats
          let stats = null;
          try {
            stats = await contentApi.getStats(ws.id);
            setContentStats(stats);
          } catch (error) {
            console.error('Failed to fetch content stats:', error);
          }

          // Fetch subscriber count
          try {
            const subscriberStats = await subscribersApi.getStats(ws.id);
            setSubscriberCount(subscriberStats.active_subscribers || 0);
          } catch (error) {
            console.error('Failed to fetch subscriber stats:', error);
            setSubscriberCount(0); // Graceful fallback to 0
          }

          // Fetch analytics data
          try {
            const analytics = await analyticsApi.getWorkspaceSummary(ws.id);
            setAnalyticsData(analytics);
          } catch (error) {
            console.error('Failed to fetch analytics:', error);
            setAnalyticsData(null); // Graceful fallback
          }

          // Fetch latest newsletter
          try {
            const newsletters = await newslettersApi.list(ws.id);
            if (newsletters.length > 0) {
              const latest = newsletters[0]; // Assuming sorted by date
              setLatestNewsletter(latest);

              // Determine draft status with freshness detection
              if (latest.status === 'draft') {
                // Check if draft is stale (new content exists after draft creation)

                // ✅ COMPREHENSIVE DEBUG LOGGING (SAFE VERSION)
                console.log('[Dashboard Freshness Debug] Starting freshness check:', {
                  hasStats: !!stats,
                  statsLatestScrape: stats?.latest_scrape,
                  statsLatestScrapeType: typeof stats?.latest_scrape,
                  statsItemsLast24h: stats?.items_last_24h,
                  statsTotalItems: stats?.total_items,
                  draftId: latest.id,
                  draftStatus: latest.status,
                  draftCreatedAt: latest.created_at,
                  draftCreatedAtType: typeof latest.created_at,
                  draftGeneratedAt: (latest as any).generated_at, // Check if this field exists
                  draftGeneratedAtType: typeof (latest as any).generated_at,
                });

                if (stats && stats.latest_scrape) {
                  // ✅ SAFE DATE PARSING with validation
                  const draftCreatedRaw = latest.generated_at || latest.created_at;
                  const latestScrapeRaw = stats.latest_scrape;

                  if (!draftCreatedRaw) {
                    console.warn('[Dashboard] ⚠️ Draft has no generated_at timestamp - cannot check freshness');
                    setDraftStatus('ready');
                  } else {
                    const draftCreated = new Date(draftCreatedRaw);
                    const latestContentScraped = new Date(latestScrapeRaw);

                    // ✅ VALIDATE DATES before calling .toISOString()
                    const draftCreatedValid = !isNaN(draftCreated.getTime());
                    const latestScrapeValid = !isNaN(latestContentScraped.getTime());

                    console.log('[Dashboard Freshness Debug] Timestamp comparison:', {
                      draftCreatedAt: draftCreatedRaw,
                      draftCreatedParsed: draftCreatedValid ? draftCreated.toISOString() : 'INVALID DATE',
                      draftCreatedTimestamp: draftCreatedValid ? draftCreated.getTime() : 'INVALID',
                      latestScrapeRaw: latestScrapeRaw,
                      latestScrapeParsed: latestScrapeValid ? latestContentScraped.toISOString() : 'INVALID DATE',
                      latestScrapeTimestamp: latestScrapeValid ? latestContentScraped.getTime() : 'INVALID',
                      isLatestScrapeNewer: (draftCreatedValid && latestScrapeValid) ? latestContentScraped > draftCreated : 'CANNOT COMPARE',
                      timeDifferenceMs: (draftCreatedValid && latestScrapeValid) ? latestContentScraped.getTime() - draftCreated.getTime() : 'CANNOT CALCULATE',
                      timeDifferenceHours: (draftCreatedValid && latestScrapeValid) ? (latestContentScraped.getTime() - draftCreated.getTime()) / (1000 * 60 * 60) : 'CANNOT CALCULATE',
                    });

                    if (!draftCreatedValid) {
                      console.error('[Dashboard] ❌ Invalid draft created_at date:', draftCreatedRaw);
                      setDraftStatus('ready'); // Fallback to ready if date is invalid
                    } else if (!latestScrapeValid) {
                      console.error('[Dashboard] ❌ Invalid latest_scrape date:', latestScrapeRaw);
                      setDraftStatus('ready'); // Fallback to ready if date is invalid
                    } else if (latestContentScraped > draftCreated) {
                      console.log('[Dashboard] ✅ Draft is STALE - marking as outdated');
                      setDraftStatus('stale');
                    } else {
                      console.log('[Dashboard] ℹ️ Draft is FRESH - marking as ready');
                      setDraftStatus('ready');
                    }
                  }
                } else {
                  console.log('[Dashboard] ⚠️ No stats or latest_scrape - defaulting to ready');
                  setDraftStatus('ready');
                }
              } else if (latest.status === 'scheduled') {
                setDraftStatus('scheduled');
              } else {
                setDraftStatus(wsConfig?.sources?.some(s => s.enabled) ? 'scheduled' : 'empty');
              }
            } else {
              setDraftStatus(wsConfig?.sources?.some(s => s.enabled) ? 'scheduled' : 'empty');
            }
          } catch (error) {
            console.error('Failed to fetch newsletters:', error);
            setDraftStatus('empty');
          }
        }
      } catch (error: any) {
        console.error('Failed to fetch data:', error);
        toast({
          title: 'Error',
          description: error.message || 'Failed to load dashboard data',
          variant: 'destructive',
        });
      } finally {
        setIsLoading(false);
      }
    }

    fetchData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isAuthenticated, isMounted, _hasHydrated]);

  if (!isMounted || !_hasHydrated || !isAuthenticated) {
    return null;
  }

  const handleLogout = () => {
    authApi.logout();
    clearAuth();
    router.push('/login');
  };

  const handleAddSource = () => {
    setShowAddSource(true);
  };

  const handlePauseSource = async (sourceId: string) => {
    if (!workspace) return;

    try {
      // Parse sourceId to get the index (format: "type-index")
      const sourceIndex = parseInt(sourceId.split('-').pop() || '0');

      if (config && config.sources[sourceIndex]) {
        const updatedSources = [...config.sources];
        updatedSources[sourceIndex] = { ...updatedSources[sourceIndex], enabled: false };

        const updatedConfig = {
          ...config,
          sources: updatedSources,
        };

        await workspacesApi.updateConfig(workspace.id, updatedConfig);

        // Update local state instead of reloading
        setConfig(updatedConfig);

        toast({
          title: 'Source Paused',
          description: 'Source has been paused',
        });
      }
    } catch (error: any) {
      toast({
        title: 'Error',
        description: error.message || 'Failed to pause source',
        variant: 'destructive',
      });
    }
  };

  const handleResumeSource = async (sourceId: string) => {
    if (!workspace) return;

    try {
      // Parse sourceId to get the index (format: "type-index")
      const sourceIndex = parseInt(sourceId.split('-').pop() || '0');

      if (config && config.sources[sourceIndex]) {
        const updatedSources = [...config.sources];
        updatedSources[sourceIndex] = { ...updatedSources[sourceIndex], enabled: true };

        const updatedConfig = {
          ...config,
          sources: updatedSources,
        };

        await workspacesApi.updateConfig(workspace.id, updatedConfig);

        // Update local state instead of reloading
        setConfig(updatedConfig);

        toast({
          title: 'Source Resumed',
          description: 'Source has been resumed',
        });
      }
    } catch (error: any) {
      toast({
        title: 'Error',
        description: error.message || 'Failed to resume source',
        variant: 'destructive',
      });
    }
  };

  const handlePreviewDraft = () => {
    if (latestNewsletter && latestNewsletter.status === 'draft') {
      setShowDraftEditor(true);
    } else {
      toast({
        title: 'No Draft Available',
        description: 'Please generate a newsletter first',
      });
    }
  };

  const handleSendNow = () => {
    if (latestNewsletter && latestNewsletter.status === 'draft') {
      setShowSendConfirmation(true);
    } else {
      toast({
        title: 'No Draft Available',
        description: 'Please generate a newsletter first',
      });
    }
  };

  const handleScrapeContent = async () => {
    if (!workspace) return;

    try {
      setIsLoading(true);
      toast({
        title: 'Scraping Content',
        description: 'Fetching content from your sources...',
      });

      // Call scrape API using apiClient (handles auth automatically)
      const response = await fetch(`http://localhost:8000/api/v1/content/scrape`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
        body: JSON.stringify({
          workspace_id: workspace.id,
        }),
      });

      const result = await response.json();

      if (result.success) {
        toast({
          title: 'Content Scraped',
          description: `Successfully fetched ${result.data.total_items} items from ${Object.keys(result.data.items_by_source).length} sources`,
        });

        // Refresh content stats to update item counts
        if (workspace) {
          try {
            const stats = await contentApi.getStats(workspace.id);
            setContentStats(stats);

            // Mark existing draft as stale if new content was scraped
            if (latestNewsletter && latestNewsletter.status === 'draft' && result.data.total_items > 0) {
              setDraftStatus('stale');

              // Show actionable toast with regenerate button
              toast({
                title: '✓ New Content Available',
                description: `Scraped ${result.data.total_items} new items. Regenerate your draft to include them.`,
                action: (
                  <Button
                    size="sm"
                    onClick={() => {
                      setShowGenerationSettings(true);
                    }}
                    className="bg-white text-primary hover:bg-white/90"
                  >
                    Regenerate Now
                  </Button>
                ),
                duration: 10000, // 10 seconds so user can click
              });
            }
          } catch (error) {
            console.error('Failed to refresh content stats:', error);
          }
        }
      } else {
        throw new Error(result.error || 'Failed to scrape content');
      }
    } catch (error: any) {
      console.error('Failed to scrape content:', error);
      toast({
        title: 'Scraping Failed',
        description: error.message || 'Failed to scrape content',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleGenerateNow = () => {
    setShowGenerationSettings(true);
  };

  const handleGenerateWithSettings = async (settings: GenerationSettings) => {
    if (!workspace) return;

    try {
      setDraftStatus('generating');

      // Show progress with steps
      const steps = [
        'Analyzing content...',
        'Detecting trends...',
        'Crafting newsletter...',
        'Finalizing...'
      ];

      let currentStep = 0;
      const stepInterval = setInterval(() => {
        if (currentStep < steps.length) {
          toast({
            title: steps[currentStep],
            description: `Step ${currentStep + 1} of ${steps.length}`,
          });
          currentStep++;
        }
      }, 1500);

      const newsletter = await newslettersApi.generate({
        workspace_id: workspace.id,
        title: `Newsletter - ${new Date().toLocaleDateString()}`,
        ...settings,
      });

      clearInterval(stepInterval);
      setLatestNewsletter(newsletter);
      setDraftStatus('ready');

      toast({
        title: '✓ Newsletter Generated',
        description: 'Your newsletter is ready to review',
        className: 'animate-celebration',
      });
    } catch (error: any) {
      console.error('Failed to generate newsletter:', error);
      setDraftStatus('empty');

      // Check if error is about no content
      const errorMsg = error.message || 'Failed to generate newsletter';
      if (errorMsg.includes('No content found')) {
        toast({
          title: 'No Content Available',
          description: 'Please scrape content first before generating a newsletter',
          variant: 'destructive',
          action: {
            label: 'Scrape Content',
            onClick: handleScrapeContent,
          },
        });
      } else {
        toast({
          title: 'Generation Failed',
          description: errorMsg,
          variant: 'destructive',
        });
      }
    }
  };

  const handleEditArticle = async (item: any) => {
    if (!latestNewsletter || !latestNewsletter.items) return;

    try {
      // Update the actual content item in database
      await contentApi.updateItem(item.id, {
        title: item.title,
        summary: item.summary,
        url: item.url,
      });

      // Update local state to reflect changes immediately
      const updatedItems = latestNewsletter.items.map(i =>
        i.id === item.id ? item : i
      );

      setLatestNewsletter({
        ...latestNewsletter,
        items: updatedItems,
      });
    } catch (error: any) {
      toast({
        title: 'Error',
        description: error.message || 'Failed to update article',
        variant: 'destructive',
      });
    }
  };

  const handleSaveDraft = async (data: { subject: string; items: any[] }) => {
    if (!latestNewsletter) return;

    try {
      // Only update subject line if it has changed (items are updated via handleEditArticle)
      if (data.subject !== latestNewsletter.subject_line) {
        await newslettersApi.update(latestNewsletter.id, {
          subject_line: data.subject,
        });

        setLatestNewsletter({
          ...latestNewsletter,
          subject_line: data.subject,
        });
      }
      // If subject hasn't changed, this is a no-op (silent success)
    } catch (error: any) {
      throw new Error(error.message || 'Failed to save draft');
    }
  };

  const handleUnifiedSourcesAdded = async (sources: Array<{ type: string; value: string }>) => {
    if (!workspace) return;

    try {
      setIsLoading(true);

      // Get current config
      const currentConfig = config || {
        sources: [],
        newsletter_settings: {
          max_items: 15,
          tone: 'professional',
          language: 'en',
        },
      };

      // Convert parsed sources to config format (matching Settings page structure)
      const newSources = sources.map((source) => {
        if (source.type === 'reddit') {
          return {
            type: 'reddit',
            enabled: true,
            config: {
              subreddits: [source.value.replace(/^r\//, '')],
              limit: 10, // Items per subreddit
            },
          };
        } else if (source.type === 'rss') {
          return {
            type: 'rss',
            enabled: true,
            config: {
              feeds: [{ url: source.value, name: new URL(source.value).hostname }],
              limit: 10, // Items per RSS feed
            },
          };
        } else if (source.type === 'twitter') {
          // Use 'x' type to match Settings page
          return {
            type: 'x',
            enabled: true,
            config: {
              usernames: [source.value.replace(/^@/, '')],
              limit: 20, // Tweets per user (X/Twitter gets higher limit)
            },
          };
        } else if (source.type === 'youtube') {
          return {
            type: 'youtube',
            enabled: true,
            config: {
              channels: [source.value],
              limit: 10, // Videos per channel
            },
          };
        } else if (source.type === 'blog') {
          return {
            type: 'blog',
            enabled: true,
            config: {
              urls: [source.value],
              limit: 15, // Articles per blog
            },
          };
        }
        return null;
      }).filter(Boolean);

      // Merge with existing sources (actually avoid duplicates this time!)
      const existingSources = currentConfig.sources || [];

      // Check for duplicates before adding
      const duplicates: string[] = [];
      const actuallyNewSources: any[] = [];

      for (const newSource of newSources) {
        const isDuplicate = existingSources.some((existing: any) => {
          // Same type check (handle x/twitter equivalence)
          const newType = newSource.type === 'twitter' ? 'x' : newSource.type;
          const existingType = existing.type === 'twitter' ? 'x' : existing.type;

          if (newType !== existingType) return false;

          // Type-specific duplicate detection
          if (newSource.type === 'reddit') {
            const newSub = newSource.config.subreddits[0]?.toLowerCase();
            return existing.config.subreddits?.some((s: string) =>
              s.toLowerCase() === newSub
            );
          } else if (newSource.type === 'x' || newSource.type === 'twitter') {
            const newUser = newSource.config.usernames[0]?.toLowerCase();
            return existing.config.usernames?.some((u: string) =>
              u.toLowerCase() === newUser
            );
          } else if (newSource.type === 'youtube') {
            const newCh = newSource.config.channels[0]?.toLowerCase();
            return existing.config.channels?.some((c: string) =>
              c.toLowerCase() === newCh
            );
          } else if (newSource.type === 'rss') {
            const newFeed = newSource.config.feeds[0]?.url;
            return existing.config.feeds?.some((f: any) => f.url === newFeed);
          } else if (newSource.type === 'blog') {
            const newUrl = newSource.config.urls[0];
            return existing.config.urls?.some((u: string) => u === newUrl);
          }

          return false;
        });

        if (isDuplicate) {
          // Get source name for toast
          let sourceName = '';
          if (newSource.type === 'reddit') sourceName = `r/${newSource.config.subreddits[0]}`;
          else if (newSource.type === 'x' || newSource.type === 'twitter') sourceName = `@${newSource.config.usernames[0]}`;
          else if (newSource.type === 'youtube') sourceName = newSource.config.channels[0];
          else if (newSource.type === 'rss') sourceName = newSource.config.feeds[0].url;
          else if (newSource.type === 'blog') sourceName = newSource.config.urls[0];

          duplicates.push(sourceName);
        } else {
          actuallyNewSources.push(newSource);
        }
      }

      // Show warning if duplicates found
      if (duplicates.length > 0) {
        toast({
          title: 'Duplicate Sources Skipped',
          description: `${duplicates.length} source(s) already exist: ${duplicates.slice(0, 3).join(', ')}${duplicates.length > 3 ? '...' : ''}`,
          variant: 'destructive',
        });
      }

      // If no new sources to add, just return
      if (actuallyNewSources.length === 0) {
        setIsLoading(false);
        return;
      }

      // Merge only non-duplicate sources
      const mergedSources = [...existingSources, ...actuallyNewSources];

      // Update workspace config
      const updatedConfig = {
        ...currentConfig,
        sources: mergedSources,
      };

      await workspacesApi.updateConfig(workspace.id, updatedConfig);
      setConfig(updatedConfig);
      setHasSources(true);

      toast({
        title: '✓ Sources Added',
        description: `Successfully added ${actuallyNewSources.length} source(s)${duplicates.length > 0 ? ` (${duplicates.length} duplicates skipped)` : ''}. Generating your first newsletter...`,
      });

      // Automatically trigger scraping and generation
      setTimeout(() => {
        handleScrapeContent();
      }, 1000);

      // Auto-generate with default settings after scraping completes
      setTimeout(async () => {
        await handleGenerateWithSettings({
          tone: 'professional',
          maxItems: 15,
          includeTrends: true,
          language: 'en',
        });
      }, 5000);

    } catch (error: any) {
      console.error('Failed to add sources:', error);
      toast({
        title: 'Error',
        description: error.message || 'Failed to add sources',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  // Calculate setup progress based on real data
  const setupSteps = 3; // sources, email, subscribers
  const hasEmailConfig = config?.delivery?.method ? true : false;
  const hasSubscribers = subscriberCount > 0;
  const completedSteps = (hasSources ? 1 : 0) + (hasEmailConfig ? 1 : 0) + (hasSubscribers ? 1 : 0);

  return (
    <div className="min-h-screen bg-muted/20">
      <AppHeader />

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8 max-w-7xl">
        {/* Enhanced Welcome Section with Progress */}
        <div className="mb-8">
          <WelcomeSection
            username={user?.username || 'there'}
            stepsCompleted={completedSteps}
            totalSteps={setupSteps}
            showProgress={!hasSources || completedSteps < setupSteps}
          />
        </div>

        <div className="space-y-6">
          {/* Motivational Tip */}
          {!hasSources && (
            <MotivationalTip
              stepsCompleted={completedSteps}
              totalSteps={setupSteps}
            />
          )}

          {/* Enhanced Draft Card */}
          <EnhancedDraftCard
            status={hasSources ? draftStatus : 'empty'}
            nextRunAt={new Date(Date.now() + 24 * 60 * 60 * 1000)}
            onConfigureSources={() => router.push('/app/settings')}
            onGenerateNow={handleGenerateNow}
            onPreviewDraft={handlePreviewDraft}
            onSendNow={handleSendNow}
            draftGeneratedAt={latestNewsletter?.generated_at ? new Date(latestNewsletter.generated_at) : undefined}
            newItemsCount={
              contentStats && latestNewsletter && contentStats.latest_scrape
                ? contentStats.items_last_24h // Approximate new items count
                : undefined
            }
          />

          {hasSources && draftStatus === 'ready' && latestNewsletter && (
            <>
              {/* Subject Line Preview */}
              <div className="bg-background border rounded-lg p-4">
                <p className="text-sm text-muted-foreground mb-1">Subject Line</p>
                <h2 className="text-xl font-semibold">{latestNewsletter.subject_line}</h2>
              </div>

              {/* Article Preview Cards */}
              <div>
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-lg font-semibold">Today's Top Stories ({Math.min(3, latestNewsletter.items?.length || 0)})</h2>
                  <Button variant="outline" size="sm" onClick={handlePreviewDraft}>
                    View All
                  </Button>
                </div>
                <div className="space-y-3">
                  {(latestNewsletter.items || []).slice(0, 3).map((item) => (
                    <ArticleCard
                      key={item.id}
                      item={transformNewsletterItemToFrontend(item)}
                      editable={true}
                      onEdit={handleEditArticle}
                    />
                  ))}
                </div>
              </div>
            </>
          )}

          {/* Unified Source Setup - Always available, collapsible when sources exist */}
          {!isLoading && (
            <div className="space-y-4">
              {hasSources ? (
                <details className="group">
                  <summary className="cursor-pointer list-none">
                    <div className="flex items-center justify-between p-4 border-2 border-dashed border-primary/30 rounded-lg hover:bg-primary/5 transition-colors">
                      <div className="flex items-center gap-3">
                        <span className="text-2xl">📋</span>
                        <div>
                          <h3 className="font-semibold text-lg">Bulk Add Sources</h3>
                          <p className="text-sm text-muted-foreground">
                            Paste multiple sources at once (Reddit, RSS, Twitter, YouTube, Blogs)
                          </p>
                        </div>
                      </div>
                      <span className="text-muted-foreground group-open:rotate-180 transition-transform">
                        ▼
                      </span>
                    </div>
                  </summary>
                  <div className="mt-4">
                    <UnifiedSourceSetup
                      onSourcesAdded={handleUnifiedSourcesAdded}
                      isLoading={isLoading}
                      existingSources={config?.sources || []}
                    />
                  </div>
                </details>
              ) : (
                <UnifiedSourceSetup
                  onSourcesAdded={handleUnifiedSourcesAdded}
                  isLoading={isLoading}
                  existingSources={config?.sources || []}
                />
              )}
            </div>
          )}

          {/* Quick Source Manager - Show when sources exist */}
          {hasSources && (
            <QuickSourceManager
              sources={config?.sources ? config.sources
                // FIX 3: Filter out empty source configs before displaying
                .filter((s) => {
                  const hasContent =
                    (s.config?.subreddits && s.config.subreddits.length > 0) ||
                    (s.config?.feeds && s.config.feeds.length > 0) ||
                    (s.config?.usernames && s.config.usernames.length > 0) ||
                    (s.config?.channels && s.config.channels.length > 0) ||
                    (s.config?.urls && s.config.urls.length > 0);

                  if (!hasContent) {
                    console.warn(`[Dashboard] Filtering empty ${s.type} source from display`);
                  }
                  return hasContent;
                })
                .map((s, idx) => {
                  // Get source name based on type
                  let name = s.type.toUpperCase();
                  if (s.type === 'reddit' && s.config.subreddits?.length) {
                    name = `r/${s.config.subreddits[0]}`;
                  } else if (s.type === 'rss' && s.config.feeds?.length) {
                    name = s.config.feeds[0].name || s.config.feeds[0].url;
                  } else if ((s.type === 'x' || s.type === 'twitter') && s.config.usernames?.length) {
                    name = `@${s.config.usernames[0]}`;
                  } else if (s.type === 'youtube' && s.config.channels?.length) {
                    name = s.config.channels[0];
                  } else if (s.type === 'blog' && s.config.urls?.length) {
                    name = s.config.urls[0];
                  }

                  return {
                    id: `${s.type}-${idx}`,
                    type: s.type === 'x' ? 'twitter' : s.type, // Map 'x' back to 'twitter' for display
                    name,
                    itemCount: contentStats?.items_by_source?.[s.type] || 0,
                    isPaused: !s.enabled,
                  };
                }) : []}
              onPause={handlePauseSource}
              onResume={handleResumeSource}
              onAdd={handleAddSource}
              isLoading={isLoading}
            />
          )}

          {/* Two Column Layout for Stats and Activity */}
          {hasSources && (
            <div className="grid lg:grid-cols-3 gap-8">
              {/* Left: Stats Overview (takes 2 columns) */}
              <div className="lg:col-span-2">
                <h2 className="text-2xl font-bold mb-6">Performance Overview</h2>
                <StatsOverview
                  subscriberCount={subscriberCount}
                  lastSentAt={analyticsData?.period_end ? new Date(analyticsData.period_end) : undefined}
                  openRate={analyticsData?.avg_open_rate ? Math.round(analyticsData.avg_open_rate * 100) : undefined}
                  openRateTrend={undefined} // TODO: Calculate trend from historical data
                  isLoading={isLoading}
                  isUsingMockData={subscriberCount === 0 && !analyticsData}
                />
              </div>

              {/* Right: Recent Activity (takes 1 column) */}
              <div className="lg:col-span-1">
                <RecentActivity />
              </div>
            </div>
          )}
        </div>
      </main>

      {/* Modals */}
      {latestNewsletter && (
        <>
          <DraftEditorModal
            open={showDraftEditor}
            onClose={() => setShowDraftEditor(false)}
            draftId={latestNewsletter.id}
            subject={latestNewsletter.subject_line}
            items={(latestNewsletter.items || []).map(transformNewsletterItemToFrontend)}
            onSave={handleSaveDraft}
            onEditArticle={handleEditArticle}
            onSendNow={() => {
              setShowDraftEditor(false);
              setShowSendConfirmation(true);
            }}
            onSendLater={() => {
              setShowDraftEditor(false);
              setShowScheduleSend(true);
            }}
            onSendTest={() => {
              setShowDraftEditor(false);
              setShowSendTest(true);
            }}
          />

          <SendConfirmationModal
            open={showSendConfirmation}
            onClose={() => setShowSendConfirmation(false)}
            newsletterId={latestNewsletter.id}
            subscriberCount={subscriberCount}
            subject={latestNewsletter.subject_line}
            onConfirm={async () => {
              if (!workspace) return;

              try {
                // Send newsletter using delivery API
                await deliveryApi.send({
                  newsletter_id: latestNewsletter.id,
                  workspace_id: workspace.id,
                });

                toast({
                  title: 'Newsletter Sent',
                  description: 'Your newsletter is being sent to all subscribers',
                });

                setShowSendConfirmation(false);

                // Update newsletter status
                setLatestNewsletter({
                  ...latestNewsletter,
                  status: 'sent',
                });

                setDraftStatus('scheduled'); // Reset to scheduled for next draft
              } catch (error: any) {
                toast({
                  title: 'Send Failed',
                  description: error.message || 'Failed to send newsletter',
                  variant: 'destructive',
                });
              }
            }}
          />
        </>
      )}

      {workspace?.id && (
        <AddSourceModal
          open={showAddSource}
          onClose={() => setShowAddSource(false)}
          workspaceId={workspace.id}
          onSuccess={() => {
            setShowAddSource(false);
            toast({
              title: 'Source Added',
              description: 'Your source has been added successfully',
            });
            // Refresh data
            window.location.reload();
          }}
        />
      )}

      {latestNewsletter && workspace && (
        <>
          <SendTestModal
            open={showSendTest}
            onClose={() => setShowSendTest(false)}
            onSend={async (email) => {
              try {
                await deliveryApi.sendTest(
                  latestNewsletter.id,
                  workspace.id,
                  email
                );

                toast({
                  title: 'Test Email Sent',
                  description: `A test email has been sent to ${email}`,
                });

                setShowSendTest(false);
              } catch (error: any) {
                toast({
                  title: 'Send Failed',
                  description: error.message || 'Failed to send test email',
                  variant: 'destructive',
                });
                throw error; // Re-throw to keep modal open
              }
            }}
          />

          <ScheduleSendModal
            open={showScheduleSend}
            onClose={() => setShowScheduleSend(false)}
            onSchedule={async (scheduledAt) => {
              try {
                // Create a scheduled job for this newsletter
                await schedulerApi.scheduleOnce(
                  workspace.id,
                  latestNewsletter.id,
                  scheduledAt
                );

                toast({
                  title: 'Newsletter Scheduled',
                  description: `Your newsletter will be sent on ${scheduledAt.toLocaleString()}`,
                });

                setShowScheduleSend(false);

                // Update newsletter status
                setLatestNewsletter({
                  ...latestNewsletter,
                  status: 'scheduled',
                });

                setDraftStatus('scheduled');
              } catch (error: any) {
                toast({
                  title: 'Scheduling Failed',
                  description: error.message || 'Failed to schedule newsletter',
                  variant: 'destructive',
                });
                throw error; // Re-throw to keep modal open
              }
            }}
          />
        </>
      )}

      {/* Generation Settings Modal */}
      <GenerationSettingsModal
        open={showGenerationSettings}
        onClose={() => setShowGenerationSettings(false)}
        onGenerate={handleGenerateWithSettings}
      />
    </div>
  );
}
