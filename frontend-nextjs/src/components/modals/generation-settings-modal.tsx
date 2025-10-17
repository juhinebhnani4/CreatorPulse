'use client';

import { useState } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Slider } from '@/components/ui/slider';
import { Loader2, Sparkles, TrendingUp } from 'lucide-react';

interface GenerationSettingsModalProps {
  open: boolean;
  onClose: () => void;
  onGenerate: (settings: GenerationSettings) => Promise<void>;
}

export interface GenerationSettings {
  max_items: number;
  days_back: number;
  tone: 'professional' | 'casual' | 'enthusiastic' | 'technical';
  language: string;
  use_trends?: boolean;
}

export function GenerationSettingsModal({ open, onClose, onGenerate }: GenerationSettingsModalProps) {
  const [isGenerating, setIsGenerating] = useState(false);
  const [maxItems, setMaxItems] = useState(15);
  const [daysBack, setDaysBack] = useState(7);
  const [tone, setTone] = useState<GenerationSettings['tone']>('professional');
  const [language, setLanguage] = useState('en');
  const [useTrends, setUseTrends] = useState(true);

  const handleGenerate = async () => {
    try {
      setIsGenerating(true);
      await onGenerate({
        max_items: maxItems,
        days_back: daysBack,
        tone,
        language,
        use_trends: useTrends,
      });
      onClose();
    } catch (error) {
      console.error('Generation failed:', error);
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2 text-2xl">
            <Sparkles className="h-6 w-6 text-primary" />
            Newsletter Generation Settings
          </DialogTitle>
          <DialogDescription>
            Customize how your newsletter will be generated
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6 py-4">
          {/* Max Items Slider */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <Label htmlFor="max-items" className="text-sm font-semibold">
                Max Items
              </Label>
              <span className="text-sm font-bold text-primary">{maxItems} items</span>
            </div>
            <Slider
              id="max-items"
              min={5}
              max={30}
              step={1}
              value={[maxItems]}
              onValueChange={(value) => setMaxItems(value[0])}
              className="w-full"
            />
            <p className="text-xs text-muted-foreground">
              Number of articles to include in the newsletter
            </p>
          </div>

          {/* Days Back Slider */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <Label htmlFor="days-back" className="text-sm font-semibold">
                Days Back
              </Label>
              <span className="text-sm font-bold text-primary">{daysBack} days</span>
            </div>
            <Slider
              id="days-back"
              min={3}
              max={14}
              step={1}
              value={[daysBack]}
              onValueChange={(value) => setDaysBack(value[0])}
              className="w-full"
            />
            <p className="text-xs text-muted-foreground">
              How far back to look for content
            </p>
          </div>

          {/* Tone Selector */}
          <div className="space-y-3">
            <Label htmlFor="tone" className="text-sm font-semibold">
              Tone
            </Label>
            <Select value={tone} onValueChange={(val) => setTone(val as GenerationSettings['tone'])}>
              <SelectTrigger id="tone" className="h-11">
                <SelectValue placeholder="Select tone" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="professional">
                  <div className="flex flex-col">
                    <span className="font-medium">Professional</span>
                    <span className="text-xs text-muted-foreground">Formal and business-focused</span>
                  </div>
                </SelectItem>
                <SelectItem value="casual">
                  <div className="flex flex-col">
                    <span className="font-medium">Casual</span>
                    <span className="text-xs text-muted-foreground">Friendly and conversational</span>
                  </div>
                </SelectItem>
                <SelectItem value="enthusiastic">
                  <div className="flex flex-col">
                    <span className="font-medium">Enthusiastic</span>
                    <span className="text-xs text-muted-foreground">Energetic and exciting</span>
                  </div>
                </SelectItem>
                <SelectItem value="technical">
                  <div className="flex flex-col">
                    <span className="font-medium">Technical</span>
                    <span className="text-xs text-muted-foreground">Detailed and in-depth</span>
                  </div>
                </SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Language Selector */}
          <div className="space-y-3">
            <Label htmlFor="language" className="text-sm font-semibold">
              Language
            </Label>
            <Select value={language} onValueChange={setLanguage}>
              <SelectTrigger id="language" className="h-11">
                <SelectValue placeholder="Select language" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="en">English</SelectItem>
                <SelectItem value="es">Spanish</SelectItem>
                <SelectItem value="fr">French</SelectItem>
                <SelectItem value="de">German</SelectItem>
                <SelectItem value="pt">Portuguese</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Use Trends Toggle */}
          <div className="flex items-center justify-between p-4 bg-primary/5 border border-primary/20 rounded-xl">
            <div className="flex items-center gap-3">
              <TrendingUp className="h-5 w-5 text-primary" />
              <div>
                <p className="text-sm font-semibold">AI Trend Detection</p>
                <p className="text-xs text-muted-foreground">Prioritize trending topics</p>
              </div>
            </div>
            <Button
              variant={useTrends ? "default" : "outline"}
              size="sm"
              onClick={() => setUseTrends(!useTrends)}
              className={useTrends ? "bg-gradient-warm hover:opacity-90" : ""}
            >
              {useTrends ? 'On' : 'Off'}
            </Button>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex gap-3 pt-4 border-t">
          <Button
            variant="outline"
            onClick={onClose}
            disabled={isGenerating}
            className="flex-1 h-11"
          >
            Cancel
          </Button>
          <Button
            onClick={handleGenerate}
            disabled={isGenerating}
            className="flex-1 bg-gradient-warm hover:opacity-90 h-11"
          >
            {isGenerating ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Generating...
              </>
            ) : (
              <>
                <Sparkles className="h-4 w-4 mr-2" />
                Generate Newsletter
              </>
            )}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
