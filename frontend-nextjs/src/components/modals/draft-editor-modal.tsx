'use client';

import { useState, useEffect } from 'react';
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ArticleCard } from '@/components/dashboard/article-card';
import { useToast } from '@/lib/hooks/use-toast';
import { Monitor, Smartphone, Save, Send, Clock } from 'lucide-react';

interface ContentItem {
  id: string;
  title: string;
  summary: string;
  url: string;
  source: string;
  publishedAt?: Date;
}

interface DraftEditorModalProps {
  open: boolean;
  onClose: () => void;
  draftId?: string;
  subject: string;
  items: ContentItem[];
  onSave?: (data: { subject: string; items: ContentItem[] }) => Promise<void>;
  onSendNow?: () => void;
  onSendLater?: () => void;
  onSendTest?: () => void;
}

export function DraftEditorModal({
  open,
  onClose,
  draftId,
  subject: initialSubject,
  items: initialItems,
  onSave,
  onSendNow,
  onSendLater,
  onSendTest,
}: DraftEditorModalProps) {
  const { toast } = useToast();
  const [subject, setSubject] = useState(initialSubject || '');
  const [items, setItems] = useState(initialItems || []);
  const [previewMode, setPreviewMode] = useState<'desktop' | 'mobile'>('desktop');
  const [isSaving, setIsSaving] = useState(false);
  const [lastSaved, setLastSaved] = useState<Date | null>(null);

  useEffect(() => {
    setSubject(initialSubject || '');
    setItems(initialItems || []);
  }, [initialSubject, initialItems]);

  // Auto-save functionality
  useEffect(() => {
    if (!open) return;

    const timer = setTimeout(async () => {
      if (onSave) {
        setIsSaving(true);
        try {
          await onSave({ subject, items });
          setLastSaved(new Date());
        } catch (error) {
          console.error('Auto-save failed:', error);
        } finally {
          setIsSaving(false);
        }
      }
    }, 2000); // Auto-save after 2 seconds of inactivity

    return () => clearTimeout(timer);
  }, [subject, items, open, onSave]);

  const handleEditItem = async (updatedItem: ContentItem) => {
    setItems((prev) =>
      prev.map((item) => (item.id === updatedItem.id ? updatedItem : item))
    );
  };

  const handleManualSave = async () => {
    if (!onSave) return;
    setIsSaving(true);
    try {
      await onSave({ subject, items });
      setLastSaved(new Date());
      toast({
        title: 'Saved',
        description: 'Your draft has been saved',
      });
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to save draft',
        variant: 'destructive',
      });
    } finally {
      setIsSaving(false);
    }
  };

  const subjectLength = subject.length;
  const subjectColor =
    subjectLength < 40
      ? 'text-red-600'
      : subjectLength <= 60
      ? 'text-green-600'
      : 'text-yellow-600';

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-hidden flex flex-col">
        <DialogHeader className="border-b pb-4">
          <div className="flex items-center justify-between">
            <DialogTitle>Edit Newsletter Draft</DialogTitle>
            <div className="flex items-center gap-2">
              <Tabs value={previewMode} onValueChange={(value) => setPreviewMode(value as any)}>
                <TabsList className="grid w-[200px] grid-cols-2">
                  <TabsTrigger value="desktop" className="text-xs">
                    <Monitor className="h-3 w-3 mr-1" />
                    Desktop
                  </TabsTrigger>
                  <TabsTrigger value="mobile" className="text-xs">
                    <Smartphone className="h-3 w-3 mr-1" />
                    Mobile
                  </TabsTrigger>
                </TabsList>
              </Tabs>
            </div>
          </div>
        </DialogHeader>

        <div className="flex-1 overflow-y-auto space-y-6 py-4">
          {/* Subject Line Editor */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="text-sm font-medium">Subject Line</label>
              <span className={`text-xs font-medium ${subjectColor}`}>
                {subjectLength} characters
                {subjectLength >= 40 && subjectLength <= 60 && ' ✓'}
              </span>
            </div>
            <Input
              value={subject}
              onChange={(e) => setSubject(e.target.value)}
              placeholder="Enter your newsletter subject..."
              className="text-lg font-semibold"
            />
            <p className="text-xs text-muted-foreground mt-1">
              Optimal: 40-60 characters for best open rates
            </p>
          </div>

          {/* Preview Container */}
          <div
            className={`border rounded-lg p-6 bg-background ${
              previewMode === 'mobile' ? 'max-w-sm mx-auto' : ''
            }`}
          >
            {/* Newsletter Header */}
            <div className="mb-6 pb-4 border-b">
              <h1 className="text-2xl font-bold mb-1">{subject || 'Your Newsletter'}</h1>
              <p className="text-sm text-muted-foreground">
                {new Intl.DateTimeFormat('en-US', {
                  weekday: 'long',
                  month: 'long',
                  day: 'numeric',
                  year: 'numeric',
                }).format(new Date())}
              </p>
            </div>

            {/* Articles */}
            <div className="space-y-4">
              <h2 className="text-lg font-semibold mb-3">Today's Top Stories</h2>
              {items.map((item) => (
                <ArticleCard
                  key={item.id}
                  item={item}
                  editable={true}
                  onEdit={handleEditItem}
                />
              ))}
            </div>

            {/* Footer */}
            <div className="mt-8 pt-4 border-t text-center text-xs text-muted-foreground">
              <p>You're receiving this because you subscribed to our newsletter</p>
              <p className="mt-1">
                <a href="#" className="hover:underline">
                  Unsubscribe
                </a>
                {' • '}
                <a href="#" className="hover:underline">
                  Manage Preferences
                </a>
              </p>
            </div>
          </div>
        </div>

        <DialogFooter className="border-t pt-4 flex-col sm:flex-row gap-2">
          {/* Auto-save status */}
          <div className="flex-1 flex items-center gap-2 text-xs text-muted-foreground">
            {isSaving ? (
              <>
                <Save className="h-3 w-3 animate-pulse" />
                Saving...
              </>
            ) : lastSaved ? (
              <>
                <Save className="h-3 w-3" />
                Saved {new Intl.DateTimeFormat('en-US', { timeStyle: 'short' }).format(lastSaved)}
              </>
            ) : null}
          </div>

          {/* Actions */}
          <div className="flex gap-2">
            <Button variant="outline" size="sm" onClick={handleManualSave} disabled={isSaving}>
              <Save className="h-4 w-4 mr-1" />
              Save
            </Button>
            <Button variant="outline" size="sm" onClick={onSendTest}>
              <Send className="h-4 w-4 mr-1" />
              Send Test
            </Button>
            <Button variant="outline" size="sm" onClick={onSendLater}>
              <Clock className="h-4 w-4 mr-1" />
              Schedule
            </Button>
            <Button size="sm" onClick={onSendNow}>
              <Send className="h-4 w-4 mr-1" />
              Send Now
            </Button>
          </div>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
