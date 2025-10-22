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
import { WorkspaceManagement } from '@/components/dashboard/workspace-management';
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
  const [hasSources, setHasSources] = useState(false);
  const [draftStatus, setDraftStatus] = useState<'ready' | 'generating' | 'scheduled' | 'empty'>('empty');

  // Modal states
  const [showDraftEditor, setShowDraftEditor] = useState(false);
  const [showSendConfirmation, setShowSendConfirmation] = useState(false);
  const [showAddSource, setShowAddSource] = useState(false);
  const [showSendTest, setShowSendTest] = useState(false);
  const [showScheduleSend, setShowScheduleSend] = useState(false);
  const [showGenerationSettings, setShowGenerationSettings] = useState(false);

  const mockSources = [
    { id: '1', type: 'reddit' as const, name: 'r/MachineLearning', itemCount: 5, isPaused: false },
    { id: '2', type: 'rss' as const, name: 'Hacker News', itemCount: 4, isPaused: false },
    { id: '3', type: 'twitter' as const, name: '@OpenAI', itemCount: 3, isPaused: true },
  ];

  const mockArticles = [
    {
      id: '1',
      title: 'GPT-4 Turbo Hits New Reasoning Milestone',
      summary: 'OpenAI announces breakthrough in reasoning capabilities with new GPT-4 Turbo update, showing significant improvements in complex problem-solving tasks.',
      url: 'https://example.com/article1',
      source: 'Reddit',
      publishedAt: new Date('2025-10-15'),
    },
    {
      id: '2',
      title: 'Why AI Agents Will Replace 40% of Jobs',
      summary: 'New study reveals shocking timeline for automation. Industry experts weigh in on the future of work and how to prepare for the AI revolution.',
      url: 'https://example.com/article2',
      source: 'Hacker News',
      publishedAt: new Date('2025-10-15'),
    },
    {
      id: '3',
      title: 'The Surprising Truth About LLM Context Windows',
      summary: 'Research shows bigger isn\'t always better. Optimal context window sizes for different tasks and how to maximize LLM performance.',
      url: 'https://example.com/article3',
      source: 'Twitter',
      publishedAt: new Date('2025-10-14'),
    },
  ];

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
              const cleanedSources = wsConfig.sources.filter((source: any) => {
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

              wsConfig.sources = cleanedSources;
            }

            setConfig(wsConfig);
            setHasSources(wsConfig.sources?.some(s => s.enabled) || false);
          } catch (error) {
            console.error('Failed to fetch config:', error);
            setHasSources(false);
          }

          // Fetch content stats
          try {
            const stats = await contentApi.getStats(ws.id);
            setContentStats(stats);
          } catch (error) {
            console.error('Failed to fetch content stats:', error);
          }

          // Fetch latest newsletter
          try {
            const newsletters = await newslettersApi.list(ws.id);
            if (newsletters.length > 0) {
              const latest = newsletters[0]; // Assuming sorted by date
              setLatestNewsletter(latest);

              // Determine draft status
              if (latest.status === 'draft') {
                setDraftStatus('ready');
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
            },
          };
        } else if (source.type === 'rss') {
          return {
            type: 'rss',
            enabled: true,
            config: {
              feeds: [{ url: source.value, name: new URL(source.value).hostname }],
            },
          };
        } else if (source.type === 'twitter') {
          // Use 'x' type to match Settings page
          return {
            type: 'x',
            enabled: true,
            config: {
              usernames: [source.value.replace(/^@/, '')],
            },
          };
        } else if (source.type === 'youtube') {
          return {
            type: 'youtube',
            enabled: true,
            config: {
              channels: [source.value],
            },
          };
        } else if (source.type === 'blog') {
          return {
            type: 'blog',
            enabled: true,
            config: {
              urls: [source.value],
            },
          };
        }
        return null;
      }).filter(Boolean);

      // Merge with existing sources (avoid duplicates)
      const mergedSources = [...(currentConfig.sources || []), ...newSources as any[]];

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
        description: `Successfully added ${sources.length} source(s). Generating your first newsletter...`,
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

  // Calculate setup progress
  const setupSteps = 3; // sources, email, schedule
  const completedSteps = (hasSources ? 1 : 0) + 2; // Mock: assume email and schedule are done

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

          {/* Unified Source Setup - Show when no sources configured */}
          {!hasSources && !isLoading && (
            <UnifiedSourceSetup
              onSourcesAdded={handleUnifiedSourcesAdded}
              isLoading={isLoading}
            />
          )}

          {/* Workspace Management - Available for both individual and agency users */}
          {!isLoading && (
            <WorkspaceManagement
              onWorkspaceCreated={async () => {
                // Refresh workspace list
                const workspaces = await workspacesApi.list();
                if (workspaces && workspaces.length > 0) {
                  setWorkspaceData(workspaces[workspaces.length - 1]);
                  setCurrentWorkspace(workspaces[workspaces.length - 1]);
                }
              }}
            />
          )}

          {/* Quick Source Manager - Show when sources exist */}
          {hasSources && (
            <QuickSourceManager
              sources={config?.sources ? config.sources.map((s, idx) => {
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
                  subscriberCount={1234}
                  lastSentAt={new Date('2025-10-15T08:00:00')}
                  openRate={34}
                  openRateTrend={3}
                  isLoading={isLoading}
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
            subscriberCount={1234}
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
