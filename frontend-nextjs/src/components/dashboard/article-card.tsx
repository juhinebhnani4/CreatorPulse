'use client';

import { useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Pencil, Check, X, ExternalLink } from 'lucide-react';
import { useToast } from '@/lib/hooks/use-toast';

interface ContentItem {
  id: string;
  title: string;
  summary: string;
  url: string;
  source: string;
  publishedAt?: Date;
}

interface ArticleCardProps {
  item: ContentItem;
  editable?: boolean;
  onEdit?: (item: ContentItem) => Promise<void>;
}

export function ArticleCard({ item, editable = false, onEdit }: ArticleCardProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [editedItem, setEditedItem] = useState(item);
  const { toast } = useToast();

  const handleSave = async () => {
    if (!onEdit) return;

    setIsSaving(true);
    try {
      await onEdit(editedItem);
      setIsEditing(false);
      toast({
        title: 'Saved',
        description: 'Article updated successfully',
      });
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to save changes',
        variant: 'destructive',
      });
    } finally {
      setIsSaving(false);
    }
  };

  const handleCancel = () => {
    setEditedItem(item);
    setIsEditing(false);
  };

  if (isEditing) {
    return (
      <Card className="border-primary">
        <CardContent className="pt-6">
          <div className="space-y-3">
            <div>
              <label className="text-xs font-medium text-muted-foreground">Title</label>
              <Input
                value={editedItem.title}
                onChange={(e) => setEditedItem({ ...editedItem, title: e.target.value })}
                className="mt-1"
              />
            </div>
            <div>
              <label className="text-xs font-medium text-muted-foreground">Summary</label>
              <textarea
                value={editedItem.summary}
                onChange={(e) => setEditedItem({ ...editedItem, summary: e.target.value })}
                className="w-full min-h-[80px] px-3 py-2 text-sm border rounded-md resize-none focus:outline-none focus:ring-2 focus:ring-ring"
                rows={3}
              />
            </div>
            <div>
              <label className="text-xs font-medium text-muted-foreground">URL</label>
              <Input
                value={editedItem.url}
                onChange={(e) => setEditedItem({ ...editedItem, url: e.target.value })}
                className="mt-1"
              />
            </div>
            <div className="flex gap-2 pt-2">
              <Button
                size="sm"
                onClick={handleSave}
                disabled={isSaving}
              >
                <Check className="h-4 w-4 mr-1" />
                Save
              </Button>
              <Button
                size="sm"
                variant="outline"
                onClick={handleCancel}
                disabled={isSaving}
              >
                <X className="h-4 w-4 mr-1" />
                Cancel
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="group hover:bg-accent/50 transition-colors">
      <CardContent className="pt-6">
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1 min-w-0">
            <div className="flex items-start gap-2 mb-2">
              <h3 className="font-semibold text-base leading-tight flex-1">
                {item.title}
              </h3>
              {editable && (
                <Button
                  variant="ghost"
                  size="sm"
                  className="opacity-0 group-hover:opacity-100 transition-opacity h-8 w-8 p-0"
                  onClick={() => setIsEditing(true)}
                >
                  <Pencil className="h-4 w-4" />
                </Button>
              )}
            </div>
            <p className="text-sm text-muted-foreground leading-relaxed mb-3">
              {item.summary}
            </p>
            <div className="flex items-center gap-2 flex-wrap">
              <Badge variant="secondary" className="text-xs">
                {item.source}
              </Badge>
              {item.publishedAt && (
                <span className="text-xs text-muted-foreground">
                  {new Intl.DateTimeFormat('en-US', {
                    month: 'short',
                    day: 'numeric',
                  }).format(new Date(item.publishedAt))}
                </span>
              )}
              <a
                href={item.url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-xs text-primary hover:underline inline-flex items-center gap-1"
              >
                Read more <ExternalLink className="h-3 w-3" />
              </a>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
