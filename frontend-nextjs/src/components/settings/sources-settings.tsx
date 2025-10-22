'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useToast } from '@/lib/hooks/use-toast';
import { useWorkspace } from '@/lib/hooks/use-workspace';
import { Plus, Trash2, Lightbulb, CheckCircle2, Loader2, X, Settings } from 'lucide-react';
import { api } from '@/lib/api/client';
import { ManageSourcesModal } from '@/components/modals/manage-sources-modal';

interface UnifiedSource {
  id: string;
  type: 'reddit' | 'rss' | 'twitter' | 'youtube' | 'blog';
  identifier: string;
  enabled: boolean;
  stats?: {
    itemsCollected?: number;
    lastScraped?: string;
  };
}

export function SourcesSettings() {
  const { toast } = useToast();
  const { workspace } = useWorkspace();
  const [isLoading, setIsLoading] = useState(true);
  const [redditSubreddits, setRedditSubreddits] = useState<string[]>([]);
  const [rssFeeds, setRssFeeds] = useState<string[]>([]);
  const [twitterUsers, setTwitterUsers] = useState<string[]>([]);
  const [youtubeChannels, setYoutubeChannels] = useState<string[]>([]);
  const [blogUrls, setBlogUrls] = useState<string[]>([]);
  const [disabledSources, setDisabledSources] = useState<UnifiedSource[]>([]); // Track disabled sources
  const [newValue, setNewValue] = useState('');
  const [isSaving, setIsSaving] = useState(false);
  const [isAdding, setIsAdding] = useState(false);
  const [justAdded, setJustAdded] = useState(false);
  const [showManageModal, setShowManageModal] = useState(false);

  // Load workspace configuration on mount
  useEffect(() => {
    const loadConfig = async () => {
      if (!workspace?.id) {
        setIsLoading(false);
        return;
      }

      try {
        setIsLoading(true);

        // Load the workspace config
        const config = await api.workspaces.getConfig(workspace.id);

        // Parse sources from config
        if (config.sources) {
          // Accumulate sources instead of replacing
          const reddit: string[] = [];
          const rss: string[] = [];
          const twitter: string[] = [];
          const youtube: string[] = [];
          const blogs: string[] = [];
          const disabled: UnifiedSource[] = [];

          // Track seen sources to avoid duplicates
          const seenSources = new Set<string>();
          const getSourceKey = (type: string, identifier: string) => {
            const normalized = identifier.toLowerCase().replace(/^r\//, '').replace(/^@/, '');
            return `${type}-${normalized}`;
          };

          config.sources.forEach((source: any) => {
            // Handle disabled sources separately
            if (!source.enabled) {
              // Extract identifiers from disabled sources
              switch (source.type) {
                case 'reddit':
                  if (source.config?.subreddits) {
                    source.config.subreddits.forEach((sub: string) => {
                      const cleaned = sub.replace(/^r\//, '');
                      const key = getSourceKey('reddit', cleaned);
                      if (!seenSources.has(key)) {
                        seenSources.add(key);
                        disabled.push({
                          id: `reddit-${cleaned}`,
                          type: 'reddit',
                          identifier: `r/${cleaned}`,
                          enabled: false,
                        });
                      }
                    });
                  }
                  break;
                case 'rss':
                  if (source.config?.feeds) {
                    source.config.feeds.forEach((f: any) => {
                      const key = getSourceKey('rss', f.url);
                      if (!seenSources.has(key)) {
                        seenSources.add(key);
                        disabled.push({
                          id: `rss-${f.url}`,
                          type: 'rss',
                          identifier: f.url,
                          enabled: false,
                        });
                      }
                    });
                  }
                  break;
                case 'twitter':
                case 'x':
                  if (source.config?.usernames) {
                    source.config.usernames.forEach((user: string) => {
                      const cleaned = user.replace(/^@/, '');
                      const key = getSourceKey('twitter', cleaned);
                      if (!seenSources.has(key)) {
                        seenSources.add(key);
                        disabled.push({
                          id: `twitter-${cleaned}`,
                          type: 'twitter',
                          identifier: `@${cleaned}`,
                          enabled: false,
                        });
                      }
                    });
                  }
                  break;
                case 'youtube':
                  if (source.config?.channels) {
                    source.config.channels.forEach((channel: string) => {
                      const key = getSourceKey('youtube', channel);
                      if (!seenSources.has(key)) {
                        seenSources.add(key);
                        disabled.push({
                          id: `youtube-${channel}`,
                          type: 'youtube',
                          identifier: channel,
                          enabled: false,
                        });
                      }
                    });
                  }
                  break;
                case 'blog':
                  if (source.config?.urls) {
                    source.config.urls.forEach((url: string) => {
                      const key = getSourceKey('blog', url);
                      if (!seenSources.has(key)) {
                        seenSources.add(key);
                        disabled.push({
                          id: `blog-${url}`,
                          type: 'blog',
                          identifier: url,
                          enabled: false,
                        });
                      }
                    });
                  }
                  break;
              }
              return;
            }

            switch (source.type) {
              case 'reddit':
                if (source.config?.subreddits) {
                  // Validate: Reddit subreddits shouldn't contain @ symbols
                  source.config.subreddits.forEach((sub: string) => {
                    const cleaned = sub.replace(/^r\//, ''); // Remove r/ prefix if present
                    if (cleaned.startsWith('@')) {
                      console.warn(`Invalid Reddit subreddit detected: ${sub} (contains @, likely a Twitter username)`);
                    } else {
                      const key = getSourceKey('reddit', cleaned);
                      if (!seenSources.has(key)) {
                        seenSources.add(key);
                        reddit.push(cleaned);
                      }
                    }
                  });
                }
                break;
              case 'rss':
                if (source.config?.feeds) {
                  source.config.feeds.forEach((f: any) => {
                    const key = getSourceKey('rss', f.url);
                    if (!seenSources.has(key)) {
                      seenSources.add(key);
                      rss.push(f.url);
                    }
                  });
                }
                break;
              case 'twitter':
              case 'x':
                if (source.config?.usernames) {
                  // Validate: Twitter usernames shouldn't contain r/ prefix
                  source.config.usernames.forEach((user: string) => {
                    const cleaned = user.replace(/^@/, ''); // Remove @ prefix if present
                    if (cleaned.startsWith('r/')) {
                      console.warn(`Invalid Twitter username detected: ${user} (contains r/, likely a Reddit subreddit)`);
                    } else {
                      const key = getSourceKey('twitter', cleaned);
                      if (!seenSources.has(key)) {
                        seenSources.add(key);
                        twitter.push(cleaned);
                      }
                    }
                  });
                }
                break;
              case 'youtube':
                if (source.config?.channels) {
                  source.config.channels.forEach((channel: string) => {
                    const key = getSourceKey('youtube', channel);
                    if (!seenSources.has(key)) {
                      seenSources.add(key);
                      youtube.push(channel);
                    }
                  });
                }
                break;
              case 'blog':
                if (source.config?.urls) {
                  source.config.urls.forEach((url: string) => {
                    const key = getSourceKey('blog', url);
                    if (!seenSources.has(key)) {
                      seenSources.add(key);
                      blogs.push(url);
                    }
                  });
                }
                break;
            }
          });

          // Set state once with accumulated values
          setRedditSubreddits(reddit);
          setRssFeeds(rss);
          setTwitterUsers(twitter);
          setYoutubeChannels(youtube);
          setBlogUrls(blogs);
          setDisabledSources(disabled);
        }
      } catch (error: any) {
        console.error('Failed to load config:', error);
        console.error('Error details:', {
          message: error.message,
          status: error.status,
          code: error.code,
          name: error.name
        });

        // More specific error messaging
        let errorDescription = 'Please try refreshing the page';
        if (error.status === 401 || error.message?.includes('credentials')) {
          errorDescription = 'Authentication failed. Please log in again.';
        } else if (error.status === 404) {
          errorDescription = 'Workspace configuration not found';
        } else if (error.status === 0) {
          errorDescription = 'Unable to connect to server. Please check if the backend is running.';
        } else if (error.message) {
          errorDescription = error.message;
        }

        toast({
          title: 'Failed to Load Configuration',
          description: errorDescription,
          variant: 'destructive',
        });
      } finally {
        setIsLoading(false);
      }
    };

    loadConfig();
  }, [workspace?.id]);

  const handleSave = async (options?: {
    customDisabledSources?: UnifiedSource[];
    customReddit?: string[];
    customRss?: string[];
    customTwitter?: string[];
    customYoutube?: string[];
    customBlogs?: string[];
  }) => {
    if (!workspace?.id) {
      toast({
        title: 'Error',
        description: 'No workspace selected',
        variant: 'destructive',
      });
      return;
    }

    setIsSaving(true);

    try {
      // Use either passed sources or current state
      const sourcesToDisable = options?.customDisabledSources ?? disabledSources;
      const redditToSave = options?.customReddit ?? redditSubreddits;
      const rssToSave = options?.customRss ?? rssFeeds;
      const twitterToSave = options?.customTwitter ?? twitterUsers;
      const youtubeToSave = options?.customYoutube ?? youtubeChannels;
      const blogsToSave = options?.customBlogs ?? blogUrls;

      // Group disabled sources by type
      const disabledByType: Record<string, string[]> = {
        reddit: [],
        rss: [],
        twitter: [],
        youtube: [],
        blog: [],
      };

      sourcesToDisable.forEach((source) => {
        const identifier = source.identifier
          .replace(/^r\//, '')  // Remove r/ prefix for reddit
          .replace(/^@/, '');    // Remove @ prefix for twitter

        if (source.type === 'twitter') {
          disabledByType['twitter'].push(identifier);
        } else {
          disabledByType[source.type].push(identifier);
        }
      });

      // Build the config object matching backend schema
      const config = {
        sources: [
          // Enabled sources
          ...(redditToSave.length > 0 ? [{
            type: 'reddit',
            enabled: true,
            config: { subreddits: redditToSave }
          }] : []),
          ...(rssToSave.length > 0 ? [{
            type: 'rss',
            enabled: true,
            config: { feeds: rssToSave.map(url => ({ url, name: url })) }
          }] : []),
          ...(twitterToSave.length > 0 ? [{
            type: 'x',
            enabled: true,
            config: { usernames: twitterToSave }
          }] : []),
          ...(youtubeToSave.length > 0 ? [{
            type: 'youtube',
            enabled: true,
            config: { channels: youtubeToSave }
          }] : []),
          ...(blogsToSave.length > 0 ? [{
            type: 'blog',
            enabled: true,
            config: { urls: blogsToSave }
          }] : []),
          // Disabled sources
          ...(disabledByType.reddit.length > 0 ? [{
            type: 'reddit',
            enabled: false,
            config: { subreddits: disabledByType.reddit }
          }] : []),
          ...(disabledByType.rss.length > 0 ? [{
            type: 'rss',
            enabled: false,
            config: { feeds: disabledByType.rss.map(url => ({ url, name: url })) }
          }] : []),
          ...(disabledByType.twitter.length > 0 ? [{
            type: 'x',
            enabled: false,
            config: { usernames: disabledByType.twitter }
          }] : []),
          ...(disabledByType.youtube.length > 0 ? [{
            type: 'youtube',
            enabled: false,
            config: { channels: disabledByType.youtube }
          }] : []),
          ...(disabledByType.blog.length > 0 ? [{
            type: 'blog',
            enabled: false,
            config: { urls: disabledByType.blog }
          }] : []),
        ]
      };

      await api.workspaces.saveConfig(workspace.id, config);

      toast({
        title: '✓ Settings Saved',
        description: 'Your content sources have been updated',
        className: 'animate-celebration',
      });
    } catch (error: any) {
      console.error('Failed to save config:', error);
      toast({
        title: 'Failed to Save',
        description: error.message || 'Please try again',
        variant: 'destructive',
      });
    } finally {
      setIsSaving(false);
    }
  };

  const addRedditSubreddit = async () => {
    if (newValue.trim()) {
      setIsAdding(true);
      // Sanitize: remove r/ prefix and @ symbol
      let cleaned = newValue.trim().replace(/^r\//, '').replace(/^@/, '');

      // Validate: warn if it looks like a Twitter username
      if (newValue.trim().startsWith('@')) {
        toast({
          title: 'Invalid Subreddit',
          description: 'This looks like a Twitter username. Please add it in the Twitter tab instead.',
          variant: 'destructive',
        });
        setIsAdding(false);
        return;
      }

      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 500));
      setRedditSubreddits([...redditSubreddits, cleaned]);
      setNewValue('');
      setIsAdding(false);
      setJustAdded(true);
      setTimeout(() => setJustAdded(false), 2000);

      toast({
        title: '✓ Subreddit Added',
        description: `r/${cleaned} has been added to your sources`,
      });
    }
  };

  const removeRedditSubreddit = (index: number) => {
    setRedditSubreddits(redditSubreddits.filter((_, i) => i !== index));
    toast({
      title: 'Removed',
      description: 'Subreddit removed from sources',
    });
  };

  const addRssFeed = async () => {
    if (newValue.trim()) {
      setIsAdding(true);
      await new Promise(resolve => setTimeout(resolve, 500));
      setRssFeeds([...rssFeeds, newValue.trim()]);
      setNewValue('');
      setIsAdding(false);
      setJustAdded(true);
      setTimeout(() => setJustAdded(false), 2000);

      toast({
        title: '✓ RSS Feed Added',
        description: 'Feed has been added to your sources',
      });
    }
  };

  const removeRssFeed = (index: number) => {
    setRssFeeds(rssFeeds.filter((_, i) => i !== index));
    toast({
      title: 'Removed',
      description: 'RSS feed removed from sources',
    });
  };

  const addTwitterUser = async () => {
    if (newValue.trim()) {
      setIsAdding(true);

      // Validate: warn if it looks like a Reddit subreddit
      if (newValue.trim().startsWith('r/') || newValue.trim().startsWith('/r/')) {
        toast({
          title: 'Invalid Twitter Username',
          description: 'This looks like a Reddit subreddit. Please add it in the Reddit tab instead.',
          variant: 'destructive',
        });
        setIsAdding(false);
        return;
      }

      await new Promise(resolve => setTimeout(resolve, 500));
      const username = newValue.trim().replace(/^@/, ''); // Remove @ if user adds it
      setTwitterUsers([...twitterUsers, username]);
      setNewValue('');
      setIsAdding(false);
      setJustAdded(true);
      setTimeout(() => setJustAdded(false), 2000);

      toast({
        title: '✓ Twitter User Added',
        description: `@${username} has been added to your sources`,
      });
    }
  };

  const removeTwitterUser = (index: number) => {
    setTwitterUsers(twitterUsers.filter((_, i) => i !== index));
    toast({
      title: 'Removed',
      description: 'Twitter user removed from sources',
    });
  };

  const addYoutubeChannel = async () => {
    if (newValue.trim()) {
      setIsAdding(true);
      await new Promise(resolve => setTimeout(resolve, 500));
      setYoutubeChannels([...youtubeChannels, newValue.trim()]);
      setNewValue('');
      setIsAdding(false);
      setJustAdded(true);
      setTimeout(() => setJustAdded(false), 2000);

      toast({
        title: '✓ YouTube Channel Added',
        description: 'Channel has been added to your sources',
      });
    }
  };

  const removeYoutubeChannel = (index: number) => {
    setYoutubeChannels(youtubeChannels.filter((_, i) => i !== index));
    toast({
      title: 'Removed',
      description: 'YouTube channel removed from sources',
    });
  };

  const addBlogUrl = async () => {
    if (newValue.trim()) {
      setIsAdding(true);
      await new Promise(resolve => setTimeout(resolve, 500));
      setBlogUrls([...blogUrls, newValue.trim()]);
      setNewValue('');
      setIsAdding(false);
      setJustAdded(true);
      setTimeout(() => setJustAdded(false), 2000);

      toast({
        title: '✓ Blog Added',
        description: 'Blog URL has been added to your sources',
      });
    }
  };

  const removeBlogUrl = (index: number) => {
    setBlogUrls(blogUrls.filter((_, i) => i !== index));
    toast({
      title: 'Removed',
      description: 'Blog URL removed from sources',
    });
  };

  const popularSubreddits = ['datascience', 'technology', 'programming', 'startups'];
  const popularTwitterUsers = ['elonmusk', 'sama', 'karpathy', 'ylecun'];

  // Convert separate source arrays to unified format for ManageSourcesModal
  const convertToUnifiedSources = (): UnifiedSource[] => {
    // Use a Map to deduplicate sources by their unique key
    const sourceMap = new Map<string, UnifiedSource>();

    // Helper to create a unique key for each source
    const getSourceKey = (type: string, identifier: string): string => {
      // Normalize identifier to handle variations like r/sub vs sub, @user vs user
      const normalized = identifier
        .replace(/^r\//, '')
        .replace(/^@/, '')
        .toLowerCase();
      return `${type}-${normalized}`;
    };

    // Add enabled sources
    redditSubreddits.forEach((sub) => {
      const key = getSourceKey('reddit', sub);
      sourceMap.set(key, {
        id: `reddit-${sub}`,
        type: 'reddit',
        identifier: `r/${sub}`,
        enabled: true,
      });
    });

    rssFeeds.forEach((feed) => {
      const key = getSourceKey('rss', feed);
      sourceMap.set(key, {
        id: `rss-${feed}`,
        type: 'rss',
        identifier: feed,
        enabled: true,
      });
    });

    twitterUsers.forEach((user) => {
      const key = getSourceKey('twitter', user);
      sourceMap.set(key, {
        id: `twitter-${user}`,
        type: 'twitter',
        identifier: `@${user}`,
        enabled: true,
      });
    });

    youtubeChannels.forEach((channel) => {
      const key = getSourceKey('youtube', channel);
      sourceMap.set(key, {
        id: `youtube-${channel}`,
        type: 'youtube',
        identifier: channel,
        enabled: true,
      });
    });

    blogUrls.forEach((url) => {
      const key = getSourceKey('blog', url);
      sourceMap.set(key, {
        id: `blog-${url}`,
        type: 'blog',
        identifier: url,
        enabled: true,
      });
    });

    // Add disabled sources (will overwrite enabled if duplicate)
    disabledSources.forEach((source) => {
      const key = getSourceKey(source.type, source.identifier);
      // Only add if not already present as enabled, or overwrite with disabled
      // This gives precedence to disabled state
      sourceMap.set(key, source);
    });

    return Array.from(sourceMap.values());
  };

  // Update sources from unified format back to separate arrays
  const handleUpdateUnifiedSources = async (updatedSources: UnifiedSource[]) => {
    const newReddit: string[] = [];
    const newRss: string[] = [];
    const newTwitter: string[] = [];
    const newYoutube: string[] = [];
    const newBlogs: string[] = [];
    const newDisabled: UnifiedSource[] = [];

    updatedSources.forEach((source) => {
      if (!source.enabled) {
        // Preserve disabled sources
        newDisabled.push(source);
        return;
      }

      switch (source.type) {
        case 'reddit':
          newReddit.push(source.identifier.replace('r/', ''));
          break;
        case 'rss':
          newRss.push(source.identifier);
          break;
        case 'twitter':
          newTwitter.push(source.identifier.replace('@', ''));
          break;
        case 'youtube':
          newYoutube.push(source.identifier);
          break;
        case 'blog':
          newBlogs.push(source.identifier);
          break;
      }
    });

    // Update state
    setRedditSubreddits(newReddit);
    setRssFeeds(newRss);
    setTwitterUsers(newTwitter);
    setYoutubeChannels(newYoutube);
    setBlogUrls(newBlogs);
    setDisabledSources(newDisabled);

    // Save to backend - pass all new arrays since state hasn't updated yet
    await handleSave({
      customDisabledSources: newDisabled,
      customReddit: newReddit,
      customRss: newRss,
      customTwitter: newTwitter,
      customYoutube: newYoutube,
      customBlogs: newBlogs,
    });
  };

  // Show loading state while fetching config
  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
          <span className="ml-3 text-muted-foreground">Loading configuration...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header with count and Manage button */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-base font-semibold text-foreground">Content Sources</h3>
          <p className="text-sm text-muted-foreground">
            {redditSubreddits.length + rssFeeds.length + twitterUsers.length + youtubeChannels.length + blogUrls.length} active sources configured
          </p>
        </div>
        <Button
          onClick={() => setShowManageModal(true)}
          variant="outline"
          size="sm"
        >
          <Settings className="h-4 w-4 mr-2" />
          Manage All Sources
        </Button>
      </div>

      <Tabs defaultValue="reddit" className="w-full">
        <TabsList className="grid w-full grid-cols-5 h-11">
          <TabsTrigger value="reddit" className="font-medium">
            📱 Reddit
          </TabsTrigger>
          <TabsTrigger value="rss" className="font-medium">
            📰 RSS
          </TabsTrigger>
          <TabsTrigger value="twitter" className="font-medium">
            🐦 Twitter
          </TabsTrigger>
          <TabsTrigger value="youtube" className="font-medium">
            📺 YouTube
          </TabsTrigger>
          <TabsTrigger value="blogs" className="font-medium">
            📝 Blogs
          </TabsTrigger>
        </TabsList>

        <TabsContent value="reddit" className="space-y-5 mt-6">
          <div>
            <label className="text-sm font-semibold mb-2 block">Subreddits</label>
            <p className="text-sm text-muted-foreground mb-4">
              Add communities you want to track (without "r/" prefix)
            </p>

            {/* Enhanced input with icon */}
            <div className="flex gap-2 mb-4">
              <div className="relative flex-1">
                <Input
                  placeholder="🔍 Start typing subreddit name..."
                  value={newValue}
                  onChange={(e) => setNewValue(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && !isAdding && addRedditSubreddit()}
                  disabled={isAdding}
                  className="h-11 text-base"
                />
              </div>
              <Button
                onClick={addRedditSubreddit}
                disabled={!newValue.trim() || isAdding}
                className="bg-gradient-warm hover:opacity-90 h-11 px-6"
              >
                {isAdding ? (
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                ) : justAdded ? (
                  <CheckCircle2 className="h-4 w-4 mr-2" />
                ) : (
                  <Plus className="h-4 w-4 mr-2" />
                )}
                {isAdding ? 'Adding...' : justAdded ? 'Added!' : 'Add'}
              </Button>
            </div>

            {/* Popular suggestions */}
            {redditSubreddits.length === 0 && (
              <div className="mb-4 p-4 bg-muted/50 rounded-xl">
                <p className="text-xs font-medium text-muted-foreground mb-2">
                  POPULAR SOURCES
                </p>
                <div className="flex flex-wrap gap-2">
                  {popularSubreddits.map((sub) => (
                    <button
                      key={sub}
                      onClick={() => {
                        setNewValue(sub);
                      }}
                      className="text-xs px-3 py-1.5 bg-background border rounded-lg hover:border-primary hover:bg-primary/5 transition-colors"
                    >
                      ⭐ r/{sub}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Enhanced tags */}
            <div className="flex flex-wrap gap-2 mb-4">
              {redditSubreddits.map((sub, index) => (
                <Badge
                  key={index}
                  variant="secondary"
                  className="px-4 py-2 text-sm font-medium hover:bg-secondary/80 transition-all group animate-slide-up"
                >
                  r/{sub}
                  <button
                    onClick={() => removeRedditSubreddit(index)}
                    className="ml-2 hover:text-destructive transition-colors"
                  >
                    <X className="h-3 w-3" />
                  </button>
                </Badge>
              ))}
            </div>

            {/* Inline tip */}
            <div className="flex gap-2 p-3 bg-primary/5 border border-primary/20 rounded-xl">
              <Lightbulb className="h-4 w-4 text-primary flex-shrink-0 mt-0.5" />
              <div className="text-xs text-muted-foreground">
                <span className="font-medium text-foreground">Tip:</span> Add 3-5 subreddits for diverse content.
                Popular choices: MachineLearning, datascience, artificial
              </div>
            </div>
          </div>

          <div>
            <label className="text-sm font-semibold mb-2 block">Items per subreddit</label>
            <Input type="number" defaultValue={10} className="max-w-xs h-11" />
          </div>
        </TabsContent>

        <TabsContent value="rss" className="space-y-4 mt-4">
          <div>
            <label className="text-sm font-medium mb-2 block">RSS Feed URLs</label>
            <div className="flex gap-2 mb-3">
              <Input
                placeholder="https://example.com/feed.xml"
                value={newValue}
                onChange={(e) => setNewValue(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && addRssFeed()}
              />
              <Button onClick={addRssFeed} size="sm">
                <Plus className="h-4 w-4 mr-1" />
                Add
              </Button>
            </div>
            <div className="space-y-2">
              {rssFeeds.map((feed, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between p-2 border rounded"
                >
                  <span className="text-sm truncate flex-1">{feed}</span>
                  <Button
                    onClick={() => removeRssFeed(index)}
                    variant="ghost"
                    size="sm"
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              ))}
            </div>
          </div>
        </TabsContent>

        <TabsContent value="twitter" className="space-y-5 mt-6">
          <div>
            <label className="text-sm font-semibold mb-2 block">Twitter/X Users</label>
            <p className="text-sm text-muted-foreground mb-4">
              Add Twitter users to track (without "@" prefix)
            </p>

            {/* Enhanced input with icon */}
            <div className="flex gap-2 mb-4">
              <div className="relative flex-1">
                <Input
                  placeholder="🔍 Enter Twitter username..."
                  value={newValue}
                  onChange={(e) => setNewValue(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && !isAdding && addTwitterUser()}
                  disabled={isAdding}
                  className="h-11 text-base"
                />
              </div>
              <Button
                onClick={addTwitterUser}
                disabled={!newValue.trim() || isAdding}
                className="bg-gradient-warm hover:opacity-90 h-11 px-6"
              >
                {isAdding ? (
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                ) : justAdded ? (
                  <CheckCircle2 className="h-4 w-4 mr-2" />
                ) : (
                  <Plus className="h-4 w-4 mr-2" />
                )}
                {isAdding ? 'Adding...' : justAdded ? 'Added!' : 'Add'}
              </Button>
            </div>

            {/* Popular suggestions */}
            {twitterUsers.length === 0 && (
              <div className="mb-4 p-4 bg-muted/50 rounded-xl">
                <p className="text-xs font-medium text-muted-foreground mb-2">
                  POPULAR ACCOUNTS
                </p>
                <div className="flex flex-wrap gap-2">
                  {popularTwitterUsers.map((user) => (
                    <button
                      key={user}
                      onClick={() => {
                        setNewValue(user);
                      }}
                      className="text-xs px-3 py-1.5 bg-background border rounded-lg hover:border-primary hover:bg-primary/5 transition-colors"
                    >
                      ⭐ @{user}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Enhanced tags */}
            <div className="flex flex-wrap gap-2 mb-4">
              {twitterUsers.map((user, index) => (
                <Badge
                  key={index}
                  variant="secondary"
                  className="px-4 py-2 text-sm font-medium hover:bg-secondary/80 transition-all group animate-slide-up"
                >
                  @{user}
                  <button
                    onClick={() => removeTwitterUser(index)}
                    className="ml-2 hover:text-destructive transition-colors"
                  >
                    <X className="h-3 w-3" />
                  </button>
                </Badge>
              ))}
            </div>

            {/* Inline tip */}
            <div className="flex gap-2 p-3 bg-primary/5 border border-primary/20 rounded-xl">
              <Lightbulb className="h-4 w-4 text-primary flex-shrink-0 mt-0.5" />
              <div className="text-xs text-muted-foreground">
                <span className="font-medium text-foreground">Tip:</span> Track influential accounts in your niche.
                Their tweets will be analyzed for trending topics.
              </div>
            </div>
          </div>

          <div>
            <label className="text-sm font-semibold mb-2 block">Tweets per user</label>
            <Input type="number" defaultValue={20} className="max-w-xs h-11" />
          </div>
        </TabsContent>

        <TabsContent value="youtube" className="space-y-5 mt-6">
          <div>
            <label className="text-sm font-semibold mb-2 block">YouTube Channels</label>
            <p className="text-sm text-muted-foreground mb-4">
              Add YouTube channel URLs or handles to track
            </p>

            {/* Enhanced input with icon */}
            <div className="flex gap-2 mb-4">
              <div className="relative flex-1">
                <Input
                  placeholder="🔍 Channel URL or @handle..."
                  value={newValue}
                  onChange={(e) => setNewValue(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && !isAdding && addYoutubeChannel()}
                  disabled={isAdding}
                  className="h-11 text-base"
                />
              </div>
              <Button
                onClick={addYoutubeChannel}
                disabled={!newValue.trim() || isAdding}
                className="bg-gradient-warm hover:opacity-90 h-11 px-6"
              >
                {isAdding ? (
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                ) : justAdded ? (
                  <CheckCircle2 className="h-4 w-4 mr-2" />
                ) : (
                  <Plus className="h-4 w-4 mr-2" />
                )}
                {isAdding ? 'Adding...' : justAdded ? 'Added!' : 'Add'}
              </Button>
            </div>

            {/* Enhanced tags */}
            <div className="flex flex-wrap gap-2 mb-4">
              {youtubeChannels.map((channel, index) => (
                <Badge
                  key={index}
                  variant="secondary"
                  className="px-4 py-2 text-sm font-medium hover:bg-secondary/80 transition-all group animate-slide-up"
                >
                  {channel.includes('youtube.com') || channel.includes('@') ? (
                    <span className="truncate max-w-[200px]">{channel}</span>
                  ) : (
                    channel
                  )}
                  <button
                    onClick={() => removeYoutubeChannel(index)}
                    className="ml-2 hover:text-destructive transition-colors"
                  >
                    <X className="h-3 w-3" />
                  </button>
                </Badge>
              ))}
            </div>

            {/* Inline tip */}
            <div className="flex gap-2 p-3 bg-primary/5 border border-primary/20 rounded-xl">
              <Lightbulb className="h-4 w-4 text-primary flex-shrink-0 mt-0.5" />
              <div className="text-xs text-muted-foreground">
                <span className="font-medium text-foreground">Tip:</span> You can paste full YouTube channel URLs like
                <code className="mx-1 px-1 bg-background rounded">youtube.com/c/channelname</code>
                or use handles like <code className="px-1 bg-background rounded">@username</code>
              </div>
            </div>
          </div>

          <div>
            <label className="text-sm font-semibold mb-2 block">Videos per channel</label>
            <Input type="number" defaultValue={10} className="max-w-xs h-11" />
          </div>
        </TabsContent>

        <TabsContent value="blogs" className="space-y-5 mt-6">
          <div>
            <label className="text-sm font-semibold mb-2 block">Blog URLs</label>
            <p className="text-sm text-muted-foreground mb-4">
              Add blog or website URLs to crawl for articles
            </p>

            {/* Enhanced input with icon */}
            <div className="flex gap-2 mb-4">
              <div className="relative flex-1">
                <Input
                  placeholder="🔍 Enter blog URL (e.g., https://blog.example.com)..."
                  value={newValue}
                  onChange={(e) => setNewValue(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && !isAdding && addBlogUrl()}
                  disabled={isAdding}
                  className="h-11 text-base"
                />
              </div>
              <Button
                onClick={addBlogUrl}
                disabled={!newValue.trim() || isAdding}
                className="bg-gradient-warm hover:opacity-90 h-11 px-6"
              >
                {isAdding ? (
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                ) : justAdded ? (
                  <CheckCircle2 className="h-4 w-4 mr-2" />
                ) : (
                  <Plus className="h-4 w-4 mr-2" />
                )}
                {isAdding ? 'Adding...' : justAdded ? 'Added!' : 'Add'}
              </Button>
            </div>

            {/* Enhanced tags */}
            <div className="flex flex-wrap gap-2 mb-4">
              {blogUrls.map((url, index) => (
                <Badge
                  key={index}
                  variant="secondary"
                  className="px-4 py-2 text-sm font-medium hover:bg-secondary/80 transition-all group animate-slide-up"
                >
                  <span className="truncate max-w-[300px]">{url}</span>
                  <button
                    onClick={() => removeBlogUrl(index)}
                    className="ml-2 hover:text-destructive transition-colors"
                  >
                    <X className="h-3 w-3" />
                  </button>
                </Badge>
              ))}
            </div>

            {/* Inline tip */}
            <div className="flex gap-2 p-3 bg-primary/5 border border-primary/20 rounded-xl">
              <Lightbulb className="h-4 w-4 text-primary flex-shrink-0 mt-0.5" />
              <div className="text-xs text-muted-foreground">
                <span className="font-medium text-foreground">Tip:</span> The crawler will automatically discover
                and extract articles from the blogs you add. Works with most major blogging platforms.
              </div>
            </div>
          </div>

          <div>
            <label className="text-sm font-semibold mb-2 block">Max articles per blog</label>
            <Input type="number" defaultValue={15} className="max-w-xs h-11" />
          </div>
        </TabsContent>
      </Tabs>

      {/* Enhanced save button */}
      <div className="flex items-center justify-between pt-6 border-t">
        <p className="text-sm text-muted-foreground">
          Changes will be applied to your next newsletter generation
        </p>
        <Button
          onClick={handleSave}
          disabled={isSaving}
          size="lg"
          className="bg-gradient-hero hover:opacity-90 min-w-[140px]"
        >
          {isSaving ? (
            <>
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              Saving...
            </>
          ) : (
            <>
              <CheckCircle2 className="h-4 w-4 mr-2" />
              Save Sources
            </>
          )}
        </Button>
      </div>

      {/* Manage Sources Modal */}
      <ManageSourcesModal
        open={showManageModal}
        onClose={() => setShowManageModal(false)}
        sources={convertToUnifiedSources()}
        onUpdate={handleUpdateUnifiedSources}
      />
    </div>
  );
}
