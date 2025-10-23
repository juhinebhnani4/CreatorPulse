'use client';

import { useState, useEffect, useRef } from 'react';
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
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Textarea } from '@/components/ui/textarea';
import { ArticleCard } from '@/components/dashboard/article-card';
import { useToast } from '@/lib/hooks/use-toast';
import { Monitor, Smartphone, Save, Send, Clock, Eye, Edit3 } from 'lucide-react';
import { newslettersApi } from '@/lib/api/newsletters';
import { feedbackApi } from '@/lib/api/feedback';

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
  onEditArticle?: (item: ContentItem) => Promise<void>;
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
  onEditArticle,
  onSendNow,
  onSendLater,
  onSendTest,
}: DraftEditorModalProps) {
  const { toast } = useToast();
  const [subject, setSubject] = useState(initialSubject || '');
  const [items, setItems] = useState(initialItems || []);
  const [viewMode, setViewMode] = useState<'edit' | 'preview'>('edit');
  const [previewMode, setPreviewMode] = useState<'desktop' | 'mobile'>('desktop');
  const [isSaving, setIsSaving] = useState(false);
  const [lastSaved, setLastSaved] = useState<Date | null>(null);
  const [newsletterHtml, setNewsletterHtml] = useState<string | null>(null);
  const [isLoadingHtml, setIsLoadingHtml] = useState(false);

  // State for inline HTML editing
  const [editingSection, setEditingSection] = useState<{
    tagName: string;
    index: number;
    originalText: string;
    itemId: string | null;
    type: 'title' | 'content';
  } | null>(null);

  const previewRef = useRef<HTMLDivElement>(null);

  // State for tracking title presence and clean HTML (without dynamic UI elements)
  const [hasTitle, setHasTitle] = useState(false);
  const [cleanHtml, setCleanHtml] = useState<string>('');

  useEffect(() => {
    setSubject(initialSubject || '');
    setItems(initialItems || []);
  }, [initialSubject, initialItems]);

  // Fetch newsletter HTML when modal opens
  useEffect(() => {
    async function fetchNewsletterHtml() {
      if (!open || !draftId) return;

      setIsLoadingHtml(true);
      try {
        const newsletter = await newslettersApi.get(draftId);
        console.log('[DraftEditorModal] Fetched newsletter:', {
          id: newsletter.id,
          hasContentHtml: !!newsletter.content_html,
          contentHtmlLength: newsletter.content_html?.length,
          hasHtmlContent: !!(newsletter as any).html_content,
          htmlContentLength: (newsletter as any).html_content?.length,
        });

        // Use content_html field (correct field name)
        const html = newsletter.content_html || '';
        setNewsletterHtml(html);

        // Check if h1 exists
        const hasH1 = /<h1[^>]*>/.test(html);
        setHasTitle(hasH1);

        // If no h1, we'll add it in rendering
        if (!hasH1) {
          console.warn('[DraftEditorModal] No h1 tag found in HTML, will prepend title');
        }
      } catch (error) {
        console.error('[DraftEditorModal] Failed to fetch newsletter HTML:', error);
        toast({
          title: 'Error Loading Newsletter',
          description: 'Could not load newsletter HTML preview',
          variant: 'destructive',
        });
      } finally {
        setIsLoadingHtml(false);
      }
    }

    fetchNewsletterHtml();
  }, [open, draftId]);

  // Initialize clean HTML state when newsletter HTML loads
  // IMPORTANT: cleanHtml must match what's actually displayed (including prepended h1)
  useEffect(() => {
    if (newsletterHtml) {
      const htmlToStore = hasTitle
        ? newsletterHtml
        : `<h1 style="color: #111827; font-size: 32px; font-weight: 800; margin-bottom: 8px; text-align: center;">${subject || 'Newsletter'}</h1>${newsletterHtml}`;
      setCleanHtml(htmlToStore);
    }
  }, [newsletterHtml, hasTitle, subject]);

  // Auto-save functionality (only for subject line changes)
  // Note: Article edits are already auto-saved via onEditArticle
  useEffect(() => {
    if (!open) return;

    const timer = setTimeout(async () => {
      if (onSave && subject !== initialSubject) {
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
  }, [subject, open, onSave]); // Only trigger on subject changes, not items

  const handleEditItem = async (updatedItem: ContentItem) => {
    // Update local state for immediate UI feedback
    setItems((prev) =>
      prev.map((item) => (item.id === updatedItem.id ? updatedItem : item))
    );

    // Persist to database if handler provided
    if (onEditArticle) {
      await onEditArticle(updatedItem);
    }
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

  // Helper functions for inline HTML editing
  const getElementSelector = (element: HTMLElement): { tagName: string; index: number; text: string } => {
    if (!previewRef.current) return { tagName: '', index: 0, text: '' };

    const tagName = element.tagName.toLowerCase();
    const allOfType = Array.from(previewRef.current.querySelectorAll(tagName));
    const index = allOfType.indexOf(element);
    const text = element.textContent || '';

    return { tagName, index, text };
  };

  const createFeedbackButton = (
    emoji: string,
    action: 'like' | 'dislike' | 'remove',
    itemId: string
  ): HTMLButtonElement => {
    const btn = document.createElement('button');
    btn.textContent = emoji;
    btn.dataset.action = action;
    btn.dataset.itemId = itemId;
    btn.style.cssText = `
      background: none;
      border: 1px solid #e5e7eb;
      border-radius: 4px;
      padding: 4px 8px;
      margin: 0 4px;
      cursor: pointer;
      font-size: 14px;
      transition: all 0.2s;
    `;
    return btn;
  };

  // Handler for inline edit save
  const handleSaveInlineEdit = async (newText: string) => {
    if (!editingSection || !draftId) return;

    try {
      const originalText = editingSection.originalText;
      const { tagName, index } = editingSection;

      // Parse cleanHtml (NOT live DOM) to avoid capturing dynamic UI
      const parser = new DOMParser();
      const doc = parser.parseFromString(cleanHtml, 'text/html');

      // Find all elements of this tag type
      const elements = doc.body.querySelectorAll(tagName);

      if (!elements[index]) {
        throw new Error(`Element not found: ${tagName}[${index}]`);
      }

      // Update text in parsed document
      elements[index].textContent = newText;

      // Serialize back to clean HTML string
      const updatedCleanHtml = doc.body.innerHTML;

      // Save to backend
      await newslettersApi.updateHtml(draftId, updatedCleanHtml);

      // Record feedback (Stage 2: included_in_final=true)
      if (editingSection.itemId) {
        await feedbackApi.createItemFeedback({
          content_item_id: editingSection.itemId,
          rating: 'neutral',
          included_in_final: true,
          newsletter_id: draftId,
          original_summary: originalText,
          edited_summary: newText,
          feedback_notes: `Inline ${editingSection.type} edit`,
        });
      }

      // Update ONLY cleanHtml (don't update newsletterHtml to avoid duplication)
      // The rendering now uses cleanHtml directly, so this is the single source of truth
      setCleanHtml(updatedCleanHtml);
      setEditingSection(null);

      toast({
        title: 'Edit Saved',
        description: 'Changes will appear in sent email',
        duration: 3000,
      });
    } catch (error: any) {
      console.error('[handleSaveInlineEdit] Error:', error);
      toast({
        title: 'Save Failed',
        description: error.message,
        variant: 'destructive',
      });
    }
  };

  // Handler for article feedback buttons
  const handleArticleFeedback = async (
    action: 'like' | 'dislike' | 'remove',
    itemId: string
  ) => {
    if (!draftId) return;

    try {
      if (action === 'like' || action === 'dislike') {
        // Submit Stage 2 feedback (newsletter-level)
        await feedbackApi.createItemFeedback({
          content_item_id: itemId,
          rating: action === 'like' ? 'positive' : 'negative',
          included_in_final: true,
          newsletter_id: draftId,
          feedback_notes: `Article ${action}d in newsletter preview`,
        });

        toast({
          title: action === 'like' ? '✓ Marked Helpful' : '✓ Marked Unhelpful',
          description: 'Future newsletters will reflect this preference',
          duration: 2000,
        });
      } else if (action === 'remove') {
        // Record negative feedback
        await feedbackApi.createItemFeedback({
          content_item_id: itemId,
          rating: 'negative',
          included_in_final: false,
          newsletter_id: draftId,
          feedback_notes: 'Article removed from newsletter',
        });

        toast({
          title: 'Feedback Recorded',
          description: 'Article marked for removal preference',
          duration: 2000,
        });
      }
    } catch (error: any) {
      toast({
        title: 'Feedback Failed',
        description: error.message,
        variant: 'destructive',
      });
    }
  };

  // Make HTML sections editable on preview render
  useEffect(() => {
    if (!previewRef.current || !newsletterHtml || !items || viewMode !== 'preview') return;

    // Find all editable elements (h2 for titles, p for paragraphs)
    const editableSelectors = 'h2, p';
    const elements = previewRef.current.querySelectorAll(editableSelectors);

    elements.forEach((el: Element, index) => {
      const htmlEl = el as HTMLElement;
      // Skip if already has edit handler
      if (htmlEl.dataset.editable) return;

      htmlEl.dataset.editable = 'true';
      htmlEl.style.cursor = 'pointer';
      htmlEl.title = 'Click to edit';
      htmlEl.style.transition = 'background-color 0.2s';

      const handleMouseEnter = () => {
        htmlEl.style.backgroundColor = 'rgba(59, 130, 246, 0.1)';
      };

      const handleMouseLeave = () => {
        htmlEl.style.backgroundColor = 'transparent';
      };

      const handleClick = (e: Event) => {
        e.stopPropagation();

        // Try to map to content item (by index)
        const sectionIndex = Math.floor(index / 2); // Approximate mapping
        const itemId = items[sectionIndex]?.id || null;

        // Get element selector
        const selector = getElementSelector(htmlEl);

        setEditingSection({
          tagName: selector.tagName,
          index: selector.index,
          originalText: htmlEl.textContent || '',
          itemId: itemId,
          type: htmlEl.tagName === 'H2' ? 'title' : 'content',
        });
      };

      htmlEl.addEventListener('mouseenter', handleMouseEnter);
      htmlEl.addEventListener('mouseleave', handleMouseLeave);
      htmlEl.addEventListener('click', handleClick);
    });

    // Cleanup
    return () => {
      if (previewRef.current) {
        const elements = previewRef.current.querySelectorAll('[data-editable]');
        elements.forEach((el) => {
          const htmlEl = el as HTMLElement;
          htmlEl.removeEventListener('mouseenter', () => {});
          htmlEl.removeEventListener('mouseleave', () => {});
          htmlEl.removeEventListener('click', () => {});
        });
      }
    };
  }, [cleanHtml, items, viewMode]);

  // Add feedback buttons to articles
  useEffect(() => {
    if (!previewRef.current || !items || !cleanHtml || viewMode !== 'preview') return;

    // Find all h2 elements (article titles)
    const articleTitles = previewRef.current.querySelectorAll('h2');

    articleTitles.forEach((title, index) => {
      // Map themes to items using modulo (wrap around if more themes than items)
      const item = items[index % items.length];
      if (!item) return; // Safety check

      // Skip if already has feedback buttons
      if (title.querySelector('.feedback-buttons')) return;

      // Create feedback button container
      const feedbackContainer = document.createElement('div');
      feedbackContainer.className = 'feedback-buttons';
      feedbackContainer.style.cssText = `
        display: inline-block;
        margin-left: 12px;
        vertical-align: middle;
      `;

      // Create buttons
      const likeBtn = createFeedbackButton('👍', 'like', item.id);
      const dislikeBtn = createFeedbackButton('👎', 'dislike', item.id);
      const removeBtn = createFeedbackButton('🗑️', 'remove', item.id);

      // Add click handlers
      likeBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        handleArticleFeedback('like', item.id);
      });

      dislikeBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        handleArticleFeedback('dislike', item.id);
      });

      removeBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        handleArticleFeedback('remove', item.id);
      });

      // Add hover effects
      [likeBtn, dislikeBtn, removeBtn].forEach((btn) => {
        btn.addEventListener('mouseenter', () => {
          btn.style.backgroundColor = '#f3f4f6';
          btn.style.transform = 'scale(1.1)';
        });

        btn.addEventListener('mouseleave', () => {
          btn.style.backgroundColor = 'transparent';
          btn.style.transform = 'scale(1)';
        });
      });

      feedbackContainer.appendChild(likeBtn);
      feedbackContainer.appendChild(dislikeBtn);
      feedbackContainer.appendChild(removeBtn);

      title.appendChild(feedbackContainer);
    });
  }, [cleanHtml, items, viewMode]);

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-hidden flex flex-col">
        <DialogHeader className="border-b pb-4">
          <div className="flex items-center justify-between">
            <DialogTitle>Newsletter Draft</DialogTitle>
            <DialogDescription className="sr-only">
              View and edit your newsletter with live preview
            </DialogDescription>
            <div className="flex items-center gap-2">
              {/* View Mode Toggle */}
              <Tabs value={viewMode} onValueChange={(value) => setViewMode(value as 'edit' | 'preview')}>
                <TabsList className="grid w-[200px] grid-cols-2">
                  <TabsTrigger value="edit" className="text-xs">
                    <Edit3 className="h-3 w-3 mr-1" />
                    Edit
                  </TabsTrigger>
                  <TabsTrigger value="preview" className="text-xs">
                    <Eye className="h-3 w-3 mr-1" />
                    HTML Preview
                  </TabsTrigger>
                </TabsList>
              </Tabs>

              {/* Device Preview (only show in preview mode) */}
              {viewMode === 'preview' && (
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
              )}
            </div>
          </div>
        </DialogHeader>

        <div className="flex-1 overflow-y-auto space-y-6 py-4">
          {viewMode === 'edit' ? (
            <>
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
              <div className="border rounded-lg p-6 bg-background">
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

                  {/* Show helpful message if no items (thematic newsletter) */}
                  {items.length === 0 ? (
                    <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 text-center">
                      <div className="text-blue-600 mb-2">
                        <Eye className="h-8 w-8 mx-auto mb-2" />
                        <p className="font-semibold">This is a thematic newsletter</p>
                      </div>
                      <p className="text-sm text-blue-700 mb-4">
                        This newsletter uses AI to synthesize content into narrative sections.
                        Individual article editing is not available.
                      </p>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setViewMode('preview')}
                        className="border-blue-300 text-blue-700 hover:bg-blue-100"
                      >
                        <Eye className="h-4 w-4 mr-2" />
                        Switch to HTML Preview
                      </Button>
                    </div>
                  ) : (
                    items.map((item) => (
                      <ArticleCard
                        key={item.id}
                        item={item}
                        editable={true}
                        onEdit={handleEditItem}
                      />
                    ))
                  )}
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
            </>
          ) : (
            <>
              {/* HTML Preview Mode */}
              {isLoadingHtml ? (
                <div className="flex items-center justify-center h-64">
                  <div className="text-center">
                    <div className="animate-spin h-8 w-8 border-4 border-primary border-t-transparent rounded-full mx-auto mb-4"></div>
                    <p className="text-muted-foreground">Loading newsletter preview...</p>
                  </div>
                </div>
              ) : newsletterHtml ? (
                <div
                  className={`border rounded-lg bg-white shadow-sm ${
                    previewMode === 'mobile' ? 'max-w-sm mx-auto' : ''
                  }`}
                  style={{ minHeight: '400px' }}
                >
                  <div
                    ref={previewRef}
                    dangerouslySetInnerHTML={{
                      __html: cleanHtml || newsletterHtml
                    }}
                  />
                </div>
              ) : (
                <div className="flex items-center justify-center h-64 border rounded-lg">
                  <div className="text-center">
                    <p className="text-muted-foreground">No HTML content available</p>
                    <p className="text-sm text-muted-foreground mt-2">Try regenerating the newsletter</p>
                  </div>
                </div>
              )}
            </>
          )}
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

      {/* Edit Dialog for inline editing */}
      {editingSection && (
        <Dialog open={true} onOpenChange={() => setEditingSection(null)}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>
                Edit {editingSection.type === 'title' ? 'Title' : 'Content'}
              </DialogTitle>
              <DialogDescription>
                Make inline changes to the newsletter content
              </DialogDescription>
            </DialogHeader>

            <div className="space-y-4">
              <Textarea
                id="edit-text"
                defaultValue={editingSection.originalText}
                rows={editingSection.type === 'title' ? 2 : 6}
                className="w-full"
                autoFocus
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && e.ctrlKey) {
                    handleSaveInlineEdit(e.currentTarget.value);
                  } else if (e.key === 'Escape') {
                    setEditingSection(null);
                  }
                }}
              />

              <div className="text-sm text-muted-foreground">
                💡 Press <kbd className="px-2 py-1 bg-gray-100 rounded">Ctrl+Enter</kbd> to save, <kbd className="px-2 py-1 bg-gray-100 rounded">Esc</kbd> to cancel
              </div>
            </div>

            <DialogFooter>
              <Button variant="outline" onClick={() => setEditingSection(null)}>
                Cancel
              </Button>
              <Button
                onClick={() => {
                  const textarea = document.getElementById('edit-text') as HTMLTextAreaElement;
                  if (textarea) handleSaveInlineEdit(textarea.value);
                }}
              >
                Save Changes
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      )}
    </Dialog>
  );
}
