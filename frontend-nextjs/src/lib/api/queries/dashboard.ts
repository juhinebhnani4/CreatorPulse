import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { workspacesApi } from '@/lib/api/workspaces';
import { newslettersApi } from '@/lib/api/newsletters';
import { contentApi } from '@/lib/api/content';
import { subscribersApi } from '@/lib/api/subscribers';
import { analyticsApi } from '@/lib/api/analytics';
import { Workspace, WorkspaceConfig } from '@/types/workspace';
import { Newsletter } from '@/types/newsletter';

/**
 * Dashboard Query Hooks
 *
 * These hooks use React Query to:
 * - Cache API responses for instant navigation
 * - Automatically refetch stale data
 * - Handle loading and error states
 * - Deduplicate simultaneous requests
 */

// ============================================================================
// Query Keys (used for cache management and invalidation)
// ============================================================================

export const dashboardKeys = {
  all: ['dashboard'] as const,
  workspaces: () => [...dashboardKeys.all, 'workspaces'] as const,
  workspace: (id: string) => [...dashboardKeys.all, 'workspace', id] as const,
  config: (workspaceId: string) => [...dashboardKeys.all, 'config', workspaceId] as const,
  newsletters: (workspaceId: string) => [...dashboardKeys.all, 'newsletters', workspaceId] as const,
  contentStats: (workspaceId: string) => [...dashboardKeys.all, 'content-stats', workspaceId] as const,
  subscriberStats: (workspaceId: string) => [...dashboardKeys.all, 'subscriber-stats', workspaceId] as const,
  analytics: (workspaceId: string) => [...dashboardKeys.all, 'analytics', workspaceId] as const,
  topStories: (workspaceId: string) => [...dashboardKeys.all, 'top-stories', workspaceId] as const,
};

// ============================================================================
// Individual Query Hooks
// ============================================================================

/**
 * Fetch user's workspaces
 */
export function useWorkspaces() {
  return useQuery({
    queryKey: dashboardKeys.workspaces(),
    queryFn: async () => {
      const workspaces = await workspacesApi.list();
      return workspaces || [];
    },
    staleTime: 10 * 60 * 1000, // 10 minutes (workspaces rarely change)
  });
}

/**
 * Fetch workspace config with source validation
 */
export function useWorkspaceConfig(workspaceId: string | undefined) {
  return useQuery({
    queryKey: dashboardKeys.config(workspaceId || ''),
    queryFn: async () => {
      if (!workspaceId) return null;

      const wsConfig = await workspacesApi.getConfig(workspaceId);

      // Clean and validate sources (same logic as original dashboard)
      if (wsConfig.sources) {
        const cleanedSources = wsConfig.sources.filter((source: any) => {
          // Remove sources with empty configs
          const hasContent =
            (source.config?.subreddits && source.config.subreddits.length > 0) ||
            (source.config?.feeds && source.config.feeds.length > 0) ||
            (source.config?.usernames && source.config.usernames.length > 0) ||
            (source.config?.channels && source.config.channels.length > 0) ||
            (source.config?.urls && source.config.urls.length > 0);

          if (!hasContent) {
            console.warn(`[useWorkspaceConfig] Removing empty ${source.type} source config`);
            return false;
          }

          // Validate Reddit sources don't contain @ symbols
          if (source.type === 'reddit' && source.config?.subreddits) {
            const hasInvalidSub = source.config.subreddits.some((sub: string) => {
              const cleaned = sub.replace(/^r\//, '');
              return cleaned.startsWith('@');
            });
            if (hasInvalidSub) {
              console.warn(`[useWorkspaceConfig] Removing invalid Reddit source with @ symbol`);
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
              console.warn(`[useWorkspaceConfig] Removing invalid Twitter source with r/ prefix`);
              return false;
            }
          }

          return true;
        });

        wsConfig.sources = cleanedSources;

        // If we cleaned sources, save back to database
        if (cleanedSources.length < wsConfig.sources.length) {
          try {
            await workspacesApi.updateConfig(workspaceId, { sources: cleanedSources });
            console.log('[useWorkspaceConfig] Saved cleaned config to database');
          } catch (error) {
            console.error('[useWorkspaceConfig] Failed to save cleaned config:', error);
          }
        }
      }

      return wsConfig;
    },
    enabled: !!workspaceId, // Only run if workspaceId exists
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

/**
 * Fetch content statistics for workspace
 */
export function useContentStats(workspaceId: string | undefined) {
  return useQuery({
    queryKey: dashboardKeys.contentStats(workspaceId || ''),
    queryFn: async () => {
      if (!workspaceId) return null;
      return await contentApi.getStats(workspaceId);
    },
    enabled: !!workspaceId,
    staleTime: 2 * 60 * 1000, // 2 minutes (content changes frequently)
  });
}

/**
 * Fetch newsletters for workspace
 */
export function useNewsletters(workspaceId: string | undefined) {
  return useQuery({
    queryKey: dashboardKeys.newsletters(workspaceId || ''),
    queryFn: async () => {
      if (!workspaceId) return [];
      return await newslettersApi.list(workspaceId);
    },
    enabled: !!workspaceId,
    staleTime: 30 * 1000, // 30 seconds (reduced from 3 minutes to prevent stale data)
  });
}

/**
 * Fetch subscriber statistics
 */
export function useSubscriberStats(workspaceId: string | undefined) {
  return useQuery({
    queryKey: dashboardKeys.subscriberStats(workspaceId || ''),
    queryFn: async () => {
      if (!workspaceId) return { active_subscribers: 0 };
      return await subscribersApi.getStats(workspaceId);
    },
    enabled: !!workspaceId,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

/**
 * Fetch analytics summary
 */
export function useAnalyticsSummary(workspaceId: string | undefined) {
  return useQuery({
    queryKey: dashboardKeys.analytics(workspaceId || ''),
    queryFn: async () => {
      if (!workspaceId) return null;
      return await analyticsApi.getWorkspaceSummary(workspaceId);
    },
    enabled: !!workspaceId,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

// ============================================================================
// Master Dashboard Hook (combines all data)
// ============================================================================

/**
 * useDashboardData - Master hook that fetches all dashboard data
 *
 * This hook:
 * - Fetches workspaces first, then dependent data
 * - Returns combined loading state
 * - Provides all data needed for dashboard render
 * - Handles errors gracefully
 *
 * @param currentWorkspaceId - Optional workspace ID from store
 */
export function useDashboardData(currentWorkspaceId?: string) {
  // Fetch workspaces first
  const {
    data: workspaces = [],
    isLoading: isLoadingWorkspaces,
    error: workspacesError,
  } = useWorkspaces();

  // Determine which workspace to use (validate cached ID exists in user's workspaces)
  const validWorkspaceId = currentWorkspaceId && workspaces.some(w => w.id === currentWorkspaceId)
    ? currentWorkspaceId
    : workspaces[0]?.id;
  const workspaceId = validWorkspaceId;
  const workspace = workspaces.find(w => w.id === workspaceId) || workspaces[0];

  // Fetch dependent data (only runs if workspace exists)
  const {
    data: config,
    isLoading: isLoadingConfig,
    error: configError,
  } = useWorkspaceConfig(workspaceId);

  const {
    data: contentStats,
    isLoading: isLoadingContent,
    error: contentError,
  } = useContentStats(workspaceId);

  const {
    data: newsletters = [],
    isLoading: isLoadingNewsletters,
    error: newslettersError,
  } = useNewsletters(workspaceId);

  const {
    data: subscriberStats,
    isLoading: isLoadingSubscribers,
    error: subscribersError,
  } = useSubscriberStats(workspaceId);

  const {
    data: analyticsData,
    isLoading: isLoadingAnalytics,
    error: analyticsError,
  } = useAnalyticsSummary(workspaceId);

  // Calculate derived states
  const hasSources = config?.sources?.some(s => s.enabled) || false;
  const subscriberCount = subscriberStats?.active_subscribers || 0;
  const latestNewsletter = newsletters[0] || null;

  // Combine loading states
  const isLoading =
    isLoadingWorkspaces ||
    isLoadingConfig ||
    isLoadingContent ||
    isLoadingNewsletters ||
    isLoadingSubscribers ||
    isLoadingAnalytics;

  // Combine errors
  const error =
    workspacesError ||
    configError ||
    contentError ||
    newslettersError ||
    subscribersError ||
    analyticsError;

  return {
    // Data
    workspaces,
    workspace,
    config,
    contentStats,
    newsletters,
    latestNewsletter,
    subscriberCount,
    analyticsData,
    hasSources,

    // States
    isLoading,
    error,

    // Workspace info
    workspaceId,
  };
}

// ============================================================================
// Mutation Hooks (for cache invalidation)
// ============================================================================

/**
 * Hook to invalidate workspace config cache
 * Use after updating sources, email settings, etc.
 */
export function useInvalidateConfig() {
  const queryClient = useQueryClient();

  return (workspaceId: string) => {
    queryClient.invalidateQueries({
      queryKey: dashboardKeys.config(workspaceId),
    });
  };
}

/**
 * Hook to invalidate newsletter cache
 * Use after creating/updating newsletters
 */
export function useInvalidateNewsletters() {
  const queryClient = useQueryClient();

  return async (workspaceId: string) => {
    await queryClient.invalidateQueries({
      queryKey: dashboardKeys.newsletters(workspaceId),
      refetchType: 'active',  // Force active queries to refetch immediately
    });
  };
}

/**
 * Hook to invalidate content stats cache
 * Use after scraping new content
 */
export function useInvalidateContentStats() {
  const queryClient = useQueryClient();

  return (workspaceId: string) => {
    queryClient.invalidateQueries({
      queryKey: dashboardKeys.contentStats(workspaceId),
    });
  };
}

/**
 * Fetch top stories for carousel display
 */
export function useTopStories(workspaceId: string | undefined) {
  return useQuery({
    queryKey: dashboardKeys.topStories(workspaceId || ''),
    queryFn: async () => {
      if (!workspaceId) return [];

      const baseURL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const token = localStorage.getItem('auth_token');

      const response = await fetch(
        `${baseURL}/api/v1/content/workspaces/${workspaceId}/top?limit=5&hours=24`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        }
      );

      if (!response.ok) {
        throw new Error('Failed to fetch top stories');
      }

      const data = await response.json();
      return data.data?.stories || [];
    },
    enabled: !!workspaceId,
    staleTime: 2 * 60 * 1000, // 2 minutes (fresh trending content)
    gcTime: 10 * 60 * 1000,   // 10 minutes cache
  });
}

/**
 * Hook to invalidate top stories cache
 * Use after scraping new content
 */
export function useInvalidateTopStories() {
  const queryClient = useQueryClient();

  return (workspaceId: string) => {
    queryClient.invalidateQueries({
      queryKey: dashboardKeys.topStories(workspaceId),
    });
  };
}
