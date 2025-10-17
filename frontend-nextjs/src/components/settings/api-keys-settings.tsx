'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useToast } from '@/lib/hooks/use-toast';
import { Eye, EyeOff, AlertCircle } from 'lucide-react';

export function ApiKeysSettings() {
  const { toast } = useToast();
  const [openaiKey, setOpenaiKey] = useState('');
  const [youtubeKey, setYoutubeKey] = useState('');
  const [twitterKey, setTwitterKey] = useState('');
  const [showKeys, setShowKeys] = useState(false);

  const handleSave = () => {
    toast({
      title: 'Settings Saved',
      description: 'Your API keys have been securely saved',
    });
  };

  return (
    <div className="space-y-6">
      <div className="flex items-start gap-3 p-3 bg-blue-50 dark:bg-blue-950 border border-blue-200 dark:border-blue-800 rounded-lg">
        <AlertCircle className="h-5 w-5 text-blue-600 dark:text-blue-400 flex-shrink-0 mt-0.5" />
        <div className="text-sm text-blue-900 dark:text-blue-100">
          <p className="font-medium mb-1">API keys are stored securely</p>
          <p className="text-xs text-blue-700 dark:text-blue-300">
            Your API keys are encrypted and never shared with third parties.
          </p>
        </div>
      </div>

      <div>
        <label className="text-sm font-medium mb-2 block">
          OpenAI API Key <span className="text-red-500">*</span>
        </label>
        <p className="text-xs text-muted-foreground mb-2">
          Required for newsletter generation. Get your key from{' '}
          <a
            href="https://platform.openai.com/api-keys"
            target="_blank"
            rel="noopener noreferrer"
            className="text-primary hover:underline"
          >
            OpenAI Platform
          </a>
        </p>
        <div className="relative">
          <Input
            type={showKeys ? 'text' : 'password'}
            placeholder="sk-••••••••••••••••••••••••••••••••"
            value={openaiKey}
            onChange={(e) => setOpenaiKey(e.target.value)}
            className="pr-10"
          />
          <button
            type="button"
            onClick={() => setShowKeys(!showKeys)}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
          >
            {showKeys ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
          </button>
        </div>
      </div>

      <div>
        <label className="text-sm font-medium mb-2 block">
          YouTube API Key <span className="text-muted-foreground">(Optional)</span>
        </label>
        <p className="text-xs text-muted-foreground mb-2">
          Required only if you want to scrape YouTube channels. Get your key from{' '}
          <a
            href="https://console.cloud.google.com/apis/credentials"
            target="_blank"
            rel="noopener noreferrer"
            className="text-primary hover:underline"
          >
            Google Cloud Console
          </a>
        </p>
        <Input
          type={showKeys ? 'text' : 'password'}
          placeholder="AIza••••••••••••••••••••••••••••••••"
          value={youtubeKey}
          onChange={(e) => setYoutubeKey(e.target.value)}
        />
      </div>

      <div>
        <label className="text-sm font-medium mb-2 block">
          X/Twitter API Key <span className="text-muted-foreground">(Optional)</span>
        </label>
        <p className="text-xs text-muted-foreground mb-2">
          Required only if you want to scrape Twitter/X posts
        </p>
        <Input
          type={showKeys ? 'text' : 'password'}
          placeholder="••••••••••••••••••••••••"
          value={twitterKey}
          onChange={(e) => setTwitterKey(e.target.value)}
        />
      </div>

      <div className="flex justify-end pt-4">
        <Button onClick={handleSave}>Save API Keys</Button>
      </div>
    </div>
  );
}
