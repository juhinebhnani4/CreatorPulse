'use client';

import { useState } from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent } from '@/components/ui/card';
import { useToast } from '@/lib/hooks/use-toast';
import { workspacesApi } from '@/lib/api/workspaces';
import { Trash2, Plus } from 'lucide-react';

type SourceType = 'reddit' | 'rss' | 'twitter' | 'youtube' | 'blog';

interface PendingSource {
  type: SourceType;
  config: any;
  displayName: string;
}

interface AddSourceModalProps {
  open: boolean;
  onClose: () => void;
  workspaceId: string;
  onSuccess?: () => void;
}

export function AddSourceModal({ open, onClose, workspaceId, onSuccess }: AddSourceModalProps) {
  const { toast } = useToast();
  const [sourceType, setSourceType] = useState<SourceType>('reddit');
  const [isLoading, setIsLoading] = useState(false);
  const [pendingSources, setPendingSources] = useState<PendingSource[]>([]);

  // Reddit
  const [subreddit, setSubreddit] = useState('');
  const [redditLimit, setRedditLimit] = useState('10');

  // RSS
  const [rssUrl, setRssUrl] = useState('');
  const [rssLimit, setRssLimit] = useState('10');

  // Twitter
  const [twitterHandle, setTwitterHandle] = useState('');
  const [twitterLimit, setTwitterLimit] = useState('10');

  // YouTube
  const [youtubeUrl, setYoutubeUrl] = useState('');
  const [youtubeLimit, setYoutubeLimit] = useState('25');

  // Blog
  const [blogUrl, setBlogUrl] = useState('');
  const [blogLimit, setBlogLimit] = useState('10');

  const getSourceIcon = (type: SourceType) => {
    switch (type) {
      case 'reddit': return '🔴';
      case 'rss': return '📰';
      case 'twitter': return '🐦';
      case 'youtube': return '📺';
      case 'blog': return '✍️';
    }
  };

  const handleAddToPending = () => {
    let config: any = {};
    let displayName = '';

    switch (sourceType) {
      case 'reddit':
        if (!subreddit.trim()) {
          toast({
            title: 'Error',
            description: 'Please enter a subreddit name',
            variant: 'destructive',
          });
          return;
        }
        config = {
          name: `r/${subreddit}`,
          subreddit: subreddit.trim(),
          limit: parseInt(redditLimit),
        };
        displayName = `r/${subreddit}`;
        setSubreddit('');
        setRedditLimit('10');
        break;
      case 'rss':
        if (!rssUrl.trim()) {
          toast({
            title: 'Error',
            description: 'Please enter an RSS feed URL',
            variant: 'destructive',
          });
          return;
        }
        config = {
          name: rssUrl.trim(),
          url: rssUrl.trim(),
          limit: parseInt(rssLimit),
        };
        displayName = rssUrl.trim();
        setRssUrl('');
        setRssLimit('10');
        break;
      case 'twitter':
        if (!twitterHandle.trim()) {
          toast({
            title: 'Error',
            description: 'Please enter a Twitter handle',
            variant: 'destructive',
          });
          return;
        }
        config = {
          name: `@${twitterHandle.replace('@', '')}`,
          handle: twitterHandle.replace('@', '').trim(),
          limit: parseInt(twitterLimit),
        };
        displayName = `@${twitterHandle.replace('@', '')}`;
        setTwitterHandle('');
        setTwitterLimit('10');
        break;
      case 'youtube':
        if (!youtubeUrl.trim()) {
          toast({
            title: 'Error',
            description: 'Please enter a YouTube channel URL',
            variant: 'destructive',
          });
          return;
        }
        config = {
          name: youtubeUrl.trim(),
          url: youtubeUrl.trim(),
          limit: parseInt(youtubeLimit),
        };
        displayName = youtubeUrl.trim();
        setYoutubeUrl('');
        setYoutubeLimit('25');
        break;
      case 'blog':
        if (!blogUrl.trim()) {
          toast({
            title: 'Error',
            description: 'Please enter a blog URL',
            variant: 'destructive',
          });
          return;
        }
        config = {
          name: blogUrl.trim(),
          url: blogUrl.trim(),
          limit: parseInt(blogLimit),
        };
        displayName = blogUrl.trim();
        setBlogUrl('');
        setBlogLimit('10');
        break;
    }

    setPendingSources([...pendingSources, {
      type: sourceType,
      config,
      displayName
    }]);

    toast({
      title: 'Added to list',
      description: `${displayName} will be added when you click "Add to Workspace"`,
    });
  };

  const handleRemoveFromPending = (index: number) => {
    setPendingSources(pendingSources.filter((_, i) => i !== index));
  };

  const handleSubmit = async () => {
    if (pendingSources.length === 0) {
      toast({
        title: 'No sources to add',
        description: 'Please add at least one source to the list',
        variant: 'destructive',
      });
      return;
    }

    setIsLoading(true);
    try {
      // Get current config
      let currentConfig;
      try {
        currentConfig = await workspacesApi.getConfig(workspaceId);
      } catch (error) {
        // Config doesn't exist yet, create a new one
        currentConfig = {
          workspace_id: workspaceId,
          sources: [],
          newsletter_settings: {},
          email_settings: {},
          scheduler_settings: { enabled: false },
        };
      }

      // Convert pending sources to source objects
      const newSources = pendingSources.map(ps => ({
        type: ps.type,
        enabled: true,
        config: ps.config,
      }));

      // Update config with all new sources
      await workspacesApi.updateConfig(workspaceId, {
        ...currentConfig,
        sources: [...(currentConfig.sources || []), ...newSources],
      });

      handleClose();
      toast({
        title: 'Sources Added',
        description: `Successfully added ${pendingSources.length} source${pendingSources.length > 1 ? 's' : ''}`,
      });

      if (onSuccess) {
        onSuccess();
      }
    } catch (error: any) {
      toast({
        title: 'Error',
        description: error.message || 'Failed to add sources',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleClose = () => {
    setSubreddit('');
    setRssUrl('');
    setTwitterHandle('');
    setYoutubeUrl('');
    setBlogUrl('');
    setRedditLimit('10');
    setRssLimit('10');
    setTwitterLimit('10');
    setYoutubeLimit('25');
    setBlogLimit('10');
    setPendingSources([]);
    onClose();
  };

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Add Content Sources</DialogTitle>
          <DialogDescription>
            Add multiple sources at once. They will be saved when you click "Add to Workspace".
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          {/* Tabs for different source types */}
          <Tabs value={sourceType} onValueChange={(value) => setSourceType(value as SourceType)}>
            <TabsList className="grid w-full grid-cols-5">
              <TabsTrigger value="reddit">
                <span className="text-lg mr-1">🔴</span>
                <span className="hidden sm:inline">Reddit</span>
              </TabsTrigger>
              <TabsTrigger value="rss">
                <span className="text-lg mr-1">📰</span>
                <span className="hidden sm:inline">RSS</span>
              </TabsTrigger>
              <TabsTrigger value="twitter">
                <span className="text-lg mr-1">🐦</span>
                <span className="hidden sm:inline">X</span>
              </TabsTrigger>
              <TabsTrigger value="youtube">
                <span className="text-lg mr-1">📺</span>
                <span className="hidden sm:inline">YouTube</span>
              </TabsTrigger>
              <TabsTrigger value="blog">
                <span className="text-lg mr-1">✍️</span>
                <span className="hidden sm:inline">Blog</span>
              </TabsTrigger>
            </TabsList>

            <TabsContent value="reddit" className="space-y-4 mt-4">
              <div>
                <label className="text-sm font-medium mb-2 block">
                  Subreddit Name <span className="text-red-500">*</span>
                </label>
                <p className="text-xs text-muted-foreground mb-2">
                  Enter without the "r/" prefix (e.g., "MachineLearning")
                </p>
                <Input
                  placeholder="MachineLearning"
                  value={subreddit}
                  onChange={(e) => setSubreddit(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleAddToPending()}
                />
              </div>
              <div>
                <label className="text-sm font-medium mb-2 block">Items to fetch</label>
                <Input
                  type="number"
                  placeholder="10"
                  value={redditLimit}
                  onChange={(e) => setRedditLimit(e.target.value)}
                />
              </div>
              <Button onClick={handleAddToPending} size="sm" className="w-full">
                <Plus className="h-4 w-4 mr-1" />
                Add to List
              </Button>
            </TabsContent>

            <TabsContent value="rss" className="space-y-4 mt-4">
              <div>
                <label className="text-sm font-medium mb-2 block">
                  RSS Feed URL <span className="text-red-500">*</span>
                </label>
                <p className="text-xs text-muted-foreground mb-2">
                  Full URL to the RSS/Atom feed
                </p>
                <Input
                  placeholder="https://example.com/feed.xml"
                  value={rssUrl}
                  onChange={(e) => setRssUrl(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleAddToPending()}
                />
              </div>
              <div>
                <label className="text-sm font-medium mb-2 block">Items to fetch</label>
                <Input
                  type="number"
                  placeholder="10"
                  value={rssLimit}
                  onChange={(e) => setRssLimit(e.target.value)}
                />
              </div>
              <Button onClick={handleAddToPending} size="sm" className="w-full">
                <Plus className="h-4 w-4 mr-1" />
                Add to List
              </Button>
            </TabsContent>

            <TabsContent value="twitter" className="space-y-4 mt-4">
              <div>
                <label className="text-sm font-medium mb-2 block">
                  Twitter/X Handle <span className="text-red-500">*</span>
                </label>
                <p className="text-xs text-muted-foreground mb-2">
                  Enter with or without @ (e.g., "openai" or "@openai")
                </p>
                <Input
                  placeholder="@openai"
                  value={twitterHandle}
                  onChange={(e) => setTwitterHandle(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleAddToPending()}
                />
              </div>
              <div>
                <label className="text-sm font-medium mb-2 block">Items to fetch</label>
                <Input
                  type="number"
                  placeholder="10"
                  value={twitterLimit}
                  onChange={(e) => setTwitterLimit(e.target.value)}
                />
              </div>
              <Button onClick={handleAddToPending} size="sm" className="w-full">
                <Plus className="h-4 w-4 mr-1" />
                Add to List
              </Button>
            </TabsContent>

            <TabsContent value="youtube" className="space-y-4 mt-4">
              <div>
                <label className="text-sm font-medium mb-2 block">
                  YouTube Channel URL <span className="text-red-500">*</span>
                </label>
                <p className="text-xs text-muted-foreground mb-2">
                  Full URL to the YouTube channel
                </p>
                <Input
                  placeholder="https://youtube.com/@channelname"
                  value={youtubeUrl}
                  onChange={(e) => setYoutubeUrl(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleAddToPending()}
                />
              </div>
              <div>
                <label className="text-sm font-medium mb-2 block">Items to fetch</label>
                <Input
                  type="number"
                  placeholder="25"
                  value={youtubeLimit}
                  onChange={(e) => setYoutubeLimit(e.target.value)}
                />
              </div>
              <Button onClick={handleAddToPending} size="sm" className="w-full">
                <Plus className="h-4 w-4 mr-1" />
                Add to List
              </Button>
            </TabsContent>

            <TabsContent value="blog" className="space-y-4 mt-4">
              <div>
                <label className="text-sm font-medium mb-2 block">
                  Blog URL <span className="text-red-500">*</span>
                </label>
                <p className="text-xs text-muted-foreground mb-2">
                  URL of the blog to crawl
                </p>
                <Input
                  placeholder="https://blog.example.com"
                  value={blogUrl}
                  onChange={(e) => setBlogUrl(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleAddToPending()}
                />
              </div>
              <div>
                <label className="text-sm font-medium mb-2 block">Items to fetch</label>
                <Input
                  type="number"
                  placeholder="10"
                  value={blogLimit}
                  onChange={(e) => setBlogLimit(e.target.value)}
                />
              </div>
              <Button onClick={handleAddToPending} size="sm" className="w-full">
                <Plus className="h-4 w-4 mr-1" />
                Add to List
              </Button>
            </TabsContent>
          </Tabs>

          {/* Pending Sources List */}
          {pendingSources.length > 0 && (
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-medium">Sources to Add ({pendingSources.length})</h3>
              </div>
              <Card>
                <CardContent className="p-3 space-y-2">
                  {pendingSources.map((source, index) => (
                    <div
                      key={index}
                      className="flex items-center justify-between p-2 bg-muted rounded-md"
                    >
                      <div className="flex items-center gap-2">
                        <span className="text-lg">{getSourceIcon(source.type)}</span>
                        <div>
                          <p className="text-sm font-medium">{source.displayName}</p>
                          <p className="text-xs text-muted-foreground capitalize">{source.type}</p>
                        </div>
                      </div>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleRemoveFromPending(index)}
                      >
                        <Trash2 className="h-4 w-4 text-destructive" />
                      </Button>
                    </div>
                  ))}
                </CardContent>
              </Card>
            </div>
          )}
        </div>

        <DialogFooter className="gap-2 sm:gap-0">
          <Button variant="outline" onClick={handleClose} disabled={isLoading}>
            Cancel
          </Button>
          <Button onClick={handleSubmit} disabled={isLoading || pendingSources.length === 0}>
            {isLoading ? 'Adding...' : `Add to Workspace ${pendingSources.length > 0 ? `(${pendingSources.length})` : ''}`}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
