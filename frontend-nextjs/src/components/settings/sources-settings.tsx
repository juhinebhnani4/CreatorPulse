'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useToast } from '@/lib/hooks/use-toast';
import { Plus, Trash2, Lightbulb, CheckCircle2, Loader2, X } from 'lucide-react';
import { api } from '@/lib/api/client';

export function SourcesSettings() {
  const { toast } = useToast();
  const [workspaceId, setWorkspaceId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [redditSubreddits, setRedditSubreddits] = useState<string[]>([]);
  const [rssFeeds, setRssFeeds] = useState<string[]>([]);
  const [twitterUsers, setTwitterUsers] = useState<string[]>([]);
  const [youtubeChannels, setYoutubeChannels] = useState<string[]>([]);
  const [blogUrls, setBlogUrls] = useState<string[]>([]);
  const [newValue, setNewValue] = useState('');
  const [isSaving, setIsSaving] = useState(false);
  const [isAdding, setIsAdding] = useState(false);
  const [justAdded, setJustAdded] = useState(false);

  // Load workspace configuration on mount
  useEffect(() => {
    const loadConfig = async () => {
      try {
        setIsLoading(true);

        // Get the first workspace (or the current one from context/route params)
        const workspaces = await api.workspaces.list();
        if (workspaces.length === 0) {
          toast({
            title: 'No Workspace Found',
            description: 'Please create a workspace first',
            variant: 'destructive',
          });
          setIsLoading(false);
          return;
        }

        const workspace = workspaces[0];
        setWorkspaceId(workspace.id);

        // Load the workspace config
        const config = await api.workspaces.getConfig(workspace.id);

        // Parse sources from config
        if (config.sources) {
          config.sources.forEach((source: any) => {
            if (!source.enabled) return;

            switch (source.type) {
              case 'reddit':
                if (source.config?.subreddits) {
                  setRedditSubreddits(source.config.subreddits);
                }
                break;
              case 'rss':
                if (source.config?.feeds) {
                  setRssFeeds(source.config.feeds.map((f: any) => f.url));
                }
                break;
              case 'twitter':
              case 'x':
                if (source.config?.usernames) {
                  setTwitterUsers(source.config.usernames);
                }
                break;
              case 'youtube':
                if (source.config?.channels) {
                  setYoutubeChannels(source.config.channels);
                }
                break;
              case 'blog':
                if (source.config?.urls) {
                  setBlogUrls(source.config.urls);
                }
                break;
            }
          });
        }
      } catch (error: any) {
        console.error('Failed to load config:', error);
        toast({
          title: 'Failed to Load Configuration',
          description: error.message || 'Please try refreshing the page',
          variant: 'destructive',
        });
      } finally {
        setIsLoading(false);
      }
    };

    loadConfig();
  }, [toast]);

  const handleSave = async () => {
    if (!workspaceId) {
      toast({
        title: 'Error',
        description: 'No workspace selected',
        variant: 'destructive',
      });
      return;
    }

    setIsSaving(true);

    try {
      // Build the config object matching backend schema
      const config = {
        sources: [
          ...(redditSubreddits.length > 0 ? [{
            type: 'reddit',
            enabled: true,
            config: { subreddits: redditSubreddits }
          }] : []),
          ...(rssFeeds.length > 0 ? [{
            type: 'rss',
            enabled: true,
            config: { feeds: rssFeeds.map(url => ({ url, name: url })) }
          }] : []),
          ...(twitterUsers.length > 0 ? [{
            type: 'x',
            enabled: true,
            config: { usernames: twitterUsers }
          }] : []),
          ...(youtubeChannels.length > 0 ? [{
            type: 'youtube',
            enabled: true,
            config: { channels: youtubeChannels }
          }] : []),
          ...(blogUrls.length > 0 ? [{
            type: 'blog',
            enabled: true,
            config: { urls: blogUrls }
          }] : []),
        ]
      };

      await api.workspaces.saveConfig(workspaceId, config);

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
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 500));
      setRedditSubreddits([...redditSubreddits, newValue.trim()]);
      setNewValue('');
      setIsAdding(false);
      setJustAdded(true);
      setTimeout(() => setJustAdded(false), 2000);

      toast({
        title: '✓ Subreddit Added',
        description: `r/${newValue.trim()} has been added to your sources`,
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
      await new Promise(resolve => setTimeout(resolve, 500));
      const username = newValue.trim().replace('@', ''); // Remove @ if user adds it
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
      {/* Header with count */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-base font-semibold text-foreground">Content Sources</h3>
          <p className="text-sm text-muted-foreground">
            {redditSubreddits.length + rssFeeds.length + twitterUsers.length + youtubeChannels.length + blogUrls.length} active sources configured
          </p>
        </div>
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
    </div>
  );
}
