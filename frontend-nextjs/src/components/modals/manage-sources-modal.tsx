'use client';

import { useState } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Switch } from '@/components/ui/switch';
import {
  Search,
  Trash2,
  Edit2,
  Check,
  X,
  Filter,
  Loader2
} from 'lucide-react';
import { useToast } from '@/lib/hooks/use-toast';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';

interface Source {
  id: string;
  type: 'reddit' | 'rss' | 'twitter' | 'youtube' | 'blog';
  identifier: string;
  enabled: boolean;
  stats?: {
    itemsCollected?: number;
    lastScraped?: string;
  };
}

interface ManageSourcesModalProps {
  open: boolean;
  onClose: () => void;
  sources: Source[];
  onUpdate: (sources: Source[]) => Promise<void>;
}

const SOURCE_ICONS = {
  reddit: '📱',
  rss: '📰',
  twitter: '🐦',
  youtube: '📺',
  blog: '📝',
};

const SOURCE_LABELS = {
  reddit: 'Reddit',
  rss: 'RSS Feed',
  twitter: 'Twitter/X',
  youtube: 'YouTube',
  blog: 'Blog',
};

export function ManageSourcesModal({ open, onClose, sources, onUpdate }: ManageSourcesModalProps) {
  const { toast } = useToast();
  const [searchQuery, setSearchQuery] = useState('');
  const [filterType, setFilterType] = useState<string>('all');
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editValue, setEditValue] = useState('');
  const [isSaving, setIsSaving] = useState(false);

  // Filter sources based on search and type filter
  const filteredSources = sources.filter(source => {
    const matchesSearch = source.identifier.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesType = filterType === 'all' || source.type === filterType;
    return matchesSearch && matchesType;
  });

  const handleToggle = async (id: string, currentlyEnabled: boolean) => {
    const updatedSources = sources.map(s =>
      s.id === id ? { ...s, enabled: !currentlyEnabled } : s
    );

    try {
      await onUpdate(updatedSources);
      toast({
        title: currentlyEnabled ? 'Source Disabled' : 'Source Enabled',
        description: `Source has been ${currentlyEnabled ? 'disabled' : 'enabled'}`,
      });
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to update source',
        variant: 'destructive',
      });
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this source?')) return;

    const updatedSources = sources.filter(s => s.id !== id);

    try {
      await onUpdate(updatedSources);
      toast({
        title: 'Source Deleted',
        description: 'Source has been removed',
      });
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to delete source',
        variant: 'destructive',
      });
    }
  };

  const startEdit = (source: Source) => {
    setEditingId(source.id);
    setEditValue(source.identifier);
  };

  const cancelEdit = () => {
    setEditingId(null);
    setEditValue('');
  };

  const saveEdit = async () => {
    if (!editingId || !editValue.trim()) return;

    const updatedSources = sources.map(s =>
      s.id === editingId ? { ...s, identifier: editValue.trim() } : s
    );

    setIsSaving(true);
    try {
      await onUpdate(updatedSources);
      toast({
        title: 'Source Updated',
        description: 'Source has been updated successfully',
      });
      setEditingId(null);
      setEditValue('');
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to update source',
        variant: 'destructive',
      });
    } finally {
      setIsSaving(false);
    }
  };

  const getStatusColor = (source: Source) => {
    if (!source.enabled) return 'text-muted-foreground';
    if (source.stats?.lastScraped) return 'text-green-500';
    return 'text-yellow-500';
  };

  const getStatusIcon = (source: Source) => {
    if (!source.enabled) return '⚪';
    if (source.stats?.lastScraped) return '🟢';
    return '🟡';
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[80vh] overflow-hidden flex flex-col">
        <DialogHeader>
          <DialogTitle className="text-2xl font-bold">Manage All Sources</DialogTitle>
          <DialogDescription>
            View, edit, enable/disable, and delete your content sources all in one place
          </DialogDescription>
        </DialogHeader>

        {/* Search and Filter Bar */}
        <div className="flex gap-3 mb-4">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search sources..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10"
            />
          </div>
          <Select value={filterType} onValueChange={setFilterType}>
            <SelectTrigger className="w-[180px]">
              <Filter className="h-4 w-4 mr-2" />
              <SelectValue placeholder="Filter by type" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Types</SelectItem>
              <SelectItem value="reddit">📱 Reddit</SelectItem>
              <SelectItem value="rss">📰 RSS</SelectItem>
              <SelectItem value="twitter">🐦 Twitter</SelectItem>
              <SelectItem value="youtube">📺 YouTube</SelectItem>
              <SelectItem value="blog">📝 Blogs</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Sources List */}
        <div className="flex-1 overflow-y-auto space-y-2 pr-2">
          {filteredSources.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-muted-foreground">
                {searchQuery || filterType !== 'all'
                  ? 'No sources match your filters'
                  : 'No sources configured yet'}
              </p>
            </div>
          ) : (
            filteredSources.map((source) => (
              <div
                key={source.id}
                className={`flex items-center gap-4 p-4 border rounded-lg transition-colors ${
                  source.enabled ? 'bg-background' : 'bg-muted/50'
                }`}
              >
                {/* Status Indicator */}
                <div className="flex items-center gap-2 min-w-[100px]">
                  <span className="text-xl" title={source.enabled ? 'Enabled' : 'Disabled'}>
                    {getStatusIcon(source)}
                  </span>
                  <span className="text-2xl">{SOURCE_ICONS[source.type]}</span>
                </div>

                {/* Source Info */}
                <div className="flex-1 min-w-0">
                  {editingId === source.id ? (
                    <div className="flex items-center gap-2">
                      <Input
                        value={editValue}
                        onChange={(e) => setEditValue(e.target.value)}
                        onKeyDown={(e) => {
                          if (e.key === 'Enter') saveEdit();
                          if (e.key === 'Escape') cancelEdit();
                        }}
                        className="h-9"
                        autoFocus
                      />
                      <Button
                        size="sm"
                        onClick={saveEdit}
                        disabled={isSaving || !editValue.trim()}
                      >
                        {isSaving ? (
                          <Loader2 className="h-4 w-4 animate-spin" />
                        ) : (
                          <Check className="h-4 w-4" />
                        )}
                      </Button>
                      <Button size="sm" variant="ghost" onClick={cancelEdit}>
                        <X className="h-4 w-4" />
                      </Button>
                    </div>
                  ) : (
                    <>
                      <div className="flex items-center gap-2 mb-1">
                        <p className={`font-medium truncate ${!source.enabled && 'text-muted-foreground'}`}>
                          {source.identifier}
                        </p>
                        <Badge variant="outline" className="text-xs">
                          {SOURCE_LABELS[source.type]}
                        </Badge>
                      </div>
                      {source.stats?.itemsCollected !== undefined && (
                        <p className="text-xs text-muted-foreground">
                          {source.stats.itemsCollected} items collected
                          {source.stats.lastScraped && ` · Last scraped ${new Date(source.stats.lastScraped).toLocaleDateString()}`}
                        </p>
                      )}
                    </>
                  )}
                </div>

                {/* Actions */}
                {editingId !== source.id && (
                  <div className="flex items-center gap-2">
                    <Switch
                      checked={source.enabled}
                      onCheckedChange={() => handleToggle(source.id, source.enabled)}
                    />
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => startEdit(source)}
                    >
                      <Edit2 className="h-4 w-4" />
                    </Button>
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => handleDelete(source.id)}
                      className="text-destructive hover:text-destructive"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                )}
              </div>
            ))
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between pt-4 border-t">
          <p className="text-sm text-muted-foreground">
            {filteredSources.length} source{filteredSources.length !== 1 ? 's' : ''} shown
            {sources.length !== filteredSources.length && ` of ${sources.length} total`}
          </p>
          <Button onClick={onClose}>Close</Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
