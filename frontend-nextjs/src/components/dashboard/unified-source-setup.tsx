'use client';

import { useState, useMemo } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Lightbulb, Sparkles, ArrowRight } from 'lucide-react';
import { useToast } from '@/lib/hooks/use-toast';

interface ParsedSource {
  type: 'reddit' | 'rss' | 'twitter' | 'youtube' | 'blog';
  value: string;
  icon: string;
  displayName: string;
  description?: string;
  isDuplicate?: boolean;
}

interface UnifiedSourceSetupProps {
  onSourcesAdded: (sources: ParsedSource[]) => void;
  isLoading?: boolean;
  existingSources?: any[];
}

export function UnifiedSourceSetup({ onSourcesAdded, isLoading = false, existingSources = [] }: UnifiedSourceSetupProps) {
  const [input, setInput] = useState('');
  const { toast } = useToast();

  // Patterns to ignore (non-content URLs)
  const ignoredPatterns = [
    /utm_/i,           // Tracking params
    /cookie/i,         // Cookie policies
    /privacy/i,        // Privacy pages
    /terms/i,          // Terms pages
    /cdn\./i,          // CDN URLs
    /static\./i,       // Static assets
    /\.js$/i,          // JavaScript files
    /\.css$/i,         // CSS files
    /\.png$/i,         // Images
    /\.jpg$/i,         // Images
    /\.gif$/i,         // Images
  ];

  const shouldIgnoreUrl = (url: string): boolean => {
    return ignoredPatterns.some(pattern => pattern.test(url));
  };

  const cleanRssUrl = (url: string): string => {
    try {
      const urlObj = new URL(url);
      // Extract clean domain name
      let domain = urlObj.hostname.replace(/^www\./, '');

      // Get path if it indicates blog or specific feed
      const path = urlObj.pathname;
      if (path.includes('/blog')) {
        domain = `${domain}/blog`;
      } else if (path.includes('/feed')) {
        // Just use domain
      } else if (path.length > 1) {
        // Include first path segment if meaningful
        const firstPath = path.split('/')[1];
        if (firstPath && !firstPath.includes('.')) {
          domain = `${domain}/${firstPath}`;
        }
      }

      return domain;
    } catch {
      return url;
    }
  };

  const detectSourceType = (line: string): ParsedSource | null => {
    let trimmed = line.trim();
    if (!trimmed) return null;

    // Auto-normalize bare domains (e.g., "openai.com" → "https://openai.com")
    // Matches: domain.com, sub.domain.com, domain.co.uk (requires TLD)
    // Prevents XSS: No <script>, no javascript:, validates with URL constructor
    if (/^[\w.-]+\.[a-z]{2,}$/i.test(trimmed) && !trimmed.startsWith('http')) {
      trimmed = `https://${trimmed}`;
    }

    // ========================================
    // STEP 1: Reddit (r/name pattern)
    // ========================================
    if (/^r\/\w+$/i.test(trimmed) || /^\/r\/\w+$/i.test(trimmed)) {
      const subreddit = trimmed.replace(/^\//, '');
      return {
        type: 'reddit',
        value: subreddit,
        icon: '📱',
        displayName: subreddit,
        description: '10 posts per day',
      };
    }

    // ========================================
    // STEP 2: Twitter (@username, #hashtag)
    // ========================================
    if (/^@\w+$/i.test(trimmed)) {
      return {
        type: 'twitter',
        value: trimmed,
        icon: '🐦',
        displayName: trimmed,
        description: 'Latest tweets',
      };
    }

    if (/^#\w+$/i.test(trimmed)) {
      return {
        type: 'twitter',
        value: trimmed,
        icon: '🐦',
        displayName: trimmed,
        description: 'Trending hashtag',
      };
    }

    // ========================================
    // STEP 3: YouTube Channel IDs (standalone UC...)
    // ========================================
    if (/^UC[\w-]{22}$/i.test(trimmed)) {
      return {
        type: 'youtube',
        value: trimmed,
        icon: '🎥',
        displayName: `YouTube Channel`,
        description: 'Latest videos',
      };
    }

    // ========================================
    // STEP 4: YouTube URLs (DOMAIN-BASED) ⭐ FIXED
    // ========================================
    if (/^https?:\/\/(www\.)?(youtube\.com|youtu\.be)\//i.test(trimmed)) {
      try {
        const url = new URL(trimmed);

        // Match patterns:
        // - youtube.com/@username
        // - youtube.com/c/channelname
        // - youtube.com/channel/UC...
        // - youtube.com/user/username
        const pathMatch = url.pathname.match(/^\/(@[\w-]+)|(c\/[\w-]+)|(channel\/UC[\w-]{22})|(user\/[\w-]+)/i);

        if (pathMatch) {
          // Extract the identifier (remove leading slash or prefix)
          const identifier = (pathMatch[1] || pathMatch[2] || pathMatch[3] || pathMatch[4]).replace(/^\//, '');

          return {
            type: 'youtube',
            value: trimmed,  // Store full URL for backend to parse
            icon: '🎥',
            displayName: identifier,
            description: 'YouTube channel',
          };
        }
      } catch {
        // Invalid URL, ignore
      }
    }

    // ========================================
    // STEP 5: EXPLICIT RSS Feeds ⭐ MOVED UP (before blog detection)
    // ========================================
    if (/^https?:\/\/.+/i.test(trimmed)) {
      // Ignore non-content URLs
      if (shouldIgnoreUrl(trimmed)) {
        return null;
      }

      // Check for EXPLICIT RSS indicators in URL
      const hasExplicitRss = /\/(feed|rss|atom)|\.xml|\.rss/i.test(trimmed);

      if (hasExplicitRss) {
        const cleanDomain = cleanRssUrl(trimmed);
        return {
          type: 'rss',
          value: trimmed,  // Use original URL (don't modify)
          icon: '📰',
          displayName: cleanDomain,
          description: 'RSS feed',
        };
      }
    }

    // ========================================
    // STEP 6: Blog URLs (subdomain/path-based) ⭐ NEW
    // ========================================
    if (/^https?:\/\/.+/i.test(trimmed)) {
      try {
        const url = new URL(trimmed);

        // Check for blog indicators:
        // 1. Subdomain: blog.example.com, blogs.example.com
        // 2. Path: /blog/, /blog, /news/
        // 3. Domain: .blog TLD

        const isBlogSubdomain = /^blogs?\./.test(url.hostname);
        const hasBlogPath = /\/(blog|news)(\/|$)/i.test(url.pathname);
        const isBlogDomain = url.hostname.endsWith('.blog');

        if (isBlogSubdomain || hasBlogPath || isBlogDomain) {
          const cleanDomain = cleanRssUrl(trimmed);
          return {
            type: 'blog',
            value: trimmed,  // Use original URL (don't append /feed)
            icon: '📝',
            displayName: cleanDomain,
            description: 'Blog URL',
          };
        }
      } catch {
        // Invalid URL, continue
      }
    }

    // ========================================
    // STEP 7: Generic URL Fallback (CONSERVATIVE) ⭐ CHANGED
    // ========================================
    if (/^https?:\/\/.+/i.test(trimmed)) {
      try {
        const url = new URL(trimmed);

        // Only suggest RSS if URL has a meaningful path
        // (not just homepage like https://example.com/)
        const hasPath = url.pathname.length > 1 && url.pathname !== '/';

        if (hasPath) {
          const cleanDomain = cleanRssUrl(trimmed);

          // Try as RSS feed (user should verify)
          const feedUrl = trimmed.endsWith('/')
            ? `${trimmed}feed`
            : `${trimmed}/feed`;

          return {
            type: 'rss',
            value: feedUrl,
            icon: '📰',
            displayName: cleanDomain,
            description: '⚠️ Auto-detected as RSS (please verify)',
          };
        }

        // Homepage URL with no clear indicators - treat as blog
        const cleanDomain = cleanRssUrl(trimmed);
        return {
          type: 'blog',
          value: trimmed,
          icon: '📝',
          displayName: cleanDomain,
          description: '⚠️ Detected as blog (please verify)',
        };
      } catch {
        // Invalid URL
        return null;
      }
    }

    return null;
  };

  const parseInput = (): ParsedSource[] => {
    const lines = input.split('\n');
    const sourcesMap = new Map<string, ParsedSource>();

    for (const line of lines) {
      const source = detectSourceType(line);
      if (source) {
        // Create unique key for deduplication
        const key = `${source.type}-${source.displayName.toLowerCase()}`;

        // Check if duplicate of existing sources
        const isDuplicateOfExisting = existingSources.some((existing: any) => {
          const sourceType = source.type === 'twitter' ? 'x' : source.type;
          const existingType = existing.type === 'twitter' ? 'x' : existing.type;

          if (sourceType !== existingType) return false;

          // Type-specific comparison
          if (source.type === 'reddit') {
            return existing.config?.subreddits?.some((s: string) =>
              `r/${s}`.toLowerCase() === source.displayName.toLowerCase()
            );
          } else if (source.type === 'twitter') {
            return existing.config?.usernames?.some((u: string) =>
              `@${u}`.toLowerCase() === source.displayName.toLowerCase()
            );
          } else if (source.type === 'youtube') {
            return existing.config?.channels?.some((c: string) =>
              c.toLowerCase() === source.value.toLowerCase()
            );
          } else if (source.type === 'rss') {
            return existing.config?.feeds?.some((f: any) =>
              f.url === source.value
            );
          } else if (source.type === 'blog') {
            return existing.config?.urls?.some((u: string) =>
              u === source.value
            );
          }

          return false;
        });

        // Only add if not already present in textarea (deduplication)
        if (!sourcesMap.has(key)) {
          sourcesMap.set(key, { ...source, isDuplicate: isDuplicateOfExisting });
        }
      }
    }

    return Array.from(sourcesMap.values());
  };

  // Memoize parsed sources to avoid re-parsing on every render
  const parsedSources = useMemo(() => parseInput(), [input, existingSources]);

  const handleSubmit = () => {
    const sources = parsedSources;

    if (sources.length === 0) {
      toast({
        title: 'No Sources Detected',
        description: 'Please paste some valid sources (subreddits, RSS feeds, or Twitter handles)',
        variant: 'destructive',
      });
      return;
    }

    const redditCount = sources.filter(s => s.type === 'reddit').length;
    const rssCount = sources.filter(s => s.type === 'rss').length;
    const twitterCount = sources.filter(s => s.type === 'twitter').length;
    const youtubeCount = sources.filter(s => s.type === 'youtube').length;
    const blogCount = sources.filter(s => s.type === 'blog').length;

    const parts = [];
    if (redditCount > 0) parts.push(`${redditCount} Reddit`);
    if (rssCount > 0) parts.push(`${rssCount} RSS`);
    if (twitterCount > 0) parts.push(`${twitterCount} Twitter`);
    if (youtubeCount > 0) parts.push(`${youtubeCount} YouTube`);
    if (blogCount > 0) parts.push(`${blogCount} Blog`);

    toast({
      title: '✓ Sources Detected',
      description: `Found ${parts.join(', ')} source${sources.length !== 1 ? 's' : ''}`,
    });

    onSourcesAdded(sources);
  };

  const exampleText = `r/MachineLearning
r/datascience
https://blog.openai.com/feed
@ylecun
#ArtificialIntelligence`;

  const sourceCards = [
    {
      id: 'reddit',
      icon: '📱',
      name: 'Reddit',
      description: 'Subreddits & posts',
      badge: '📊 Most popular',
      example: 'r/MachineLearning',
    },
    {
      id: 'rss',
      icon: '📰',
      name: 'RSS Feed',
      description: 'Blogs & articles',
      badge: '🌟 Flexible',
      example: 'https://blog.openai.com/feed',
    },
    {
      id: 'twitter',
      icon: '🐦',
      name: 'Twitter',
      description: 'Tweets & threads',
      badge: '⚡ Real-time',
      example: '@ylecun',
    },
    {
      id: 'youtube',
      icon: '🎥',
      name: 'YouTube',
      description: 'Channels & videos',
      badge: '📹 Video content',
      example: 'UC_x5XG1OV2P6uZZ5FSM9Ttw',
    },
    {
      id: 'blog',
      icon: '✍️',
      name: 'Blog',
      description: 'Custom blogs',
      badge: '📝 Text content',
      example: 'https://example.com/blog',
    },
  ];

  const handleCardClick = (example: string) => {
    // Add example to textarea (append with newline if not empty)
    const newValue = input.trim() ? `${input}\n${example}` : example;
    setInput(newValue);
  };

  return (
    <Card className="border-2 border-dashed border-primary/30 bg-gradient-to-br from-background to-muted/30">
      <CardContent className="pt-6 pb-6">
        <div className="space-y-6">
          {/* Header */}
          <div className="text-center space-y-2">
            <h3 className="text-2xl font-bold">Content Sources</h3>
            <p className="text-muted-foreground">
              Click a source below or paste multiple sources at once
            </p>
          </div>

          {/* Source Cards Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4">
            {sourceCards.map((source, index) => (
              <button
                key={source.id}
                onClick={() => handleCardClick(source.example)}
                disabled={isLoading}
                className="border-2 border-dashed rounded-xl p-5 text-center space-y-3 hover:border-primary hover:bg-primary/5 transition-all disabled:opacity-50 disabled:cursor-not-allowed group animate-slide-up"
                style={{ animationDelay: `${index * 50}ms` }}
              >
                {/* Icon */}
                <div className="text-4xl">{source.icon}</div>

                {/* Name & Description */}
                <div>
                  <h4 className="font-semibold text-base">{source.name}</h4>
                  <p className="text-xs text-muted-foreground mt-1">
                    {source.description}
                  </p>
                </div>

                {/* Badge */}
                <div className="text-xs text-primary bg-primary/10 px-3 py-1 rounded-full inline-block">
                  {source.badge}
                </div>

                {/* Example preview */}
                <div className="text-xs font-mono text-muted-foreground bg-muted/50 px-2 py-1 rounded">
                  {source.example}
                </div>
              </button>
            ))}
          </div>

          {/* Divider */}
          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-dashed"></div>
            </div>
            <div className="relative flex justify-center text-xs uppercase">
              <span className="bg-card px-2 text-muted-foreground">Or paste multiple</span>
            </div>
          </div>

          {/* Textarea */}
          <div className="relative">
            <Textarea
              placeholder={exampleText}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              className="min-h-[200px] font-mono text-sm resize-none focus-visible:ring-2 focus-visible:ring-primary"
              disabled={isLoading}
            />
          </div>

          {/* Detection Info */}
          <div className="flex items-start gap-3 p-4 bg-primary/5 border border-primary/20 rounded-xl">
            <Lightbulb className="h-5 w-5 text-primary flex-shrink-0 mt-0.5" />
            <div className="text-sm space-y-1">
              <p className="font-medium text-foreground">💡 We automatically detect:</p>
              <ul className="text-muted-foreground space-y-0.5 ml-4">
                <li>• <span className="font-mono">r/name</span> → Reddit</li>
                <li>• <span className="font-mono">http(s)://...</span> → RSS Feed</li>
                <li>• <span className="font-mono">@username</span> or <span className="font-mono">#hashtag</span> → Twitter</li>
              </ul>
            </div>
          </div>

          {/* Submit Button */}
          <div className="flex justify-center">
            <Button
              onClick={handleSubmit}
              disabled={!input.trim() || isLoading || parsedSources.length === 0}
              className="bg-gradient-warm hover:opacity-90 h-12 px-8 text-base font-semibold shadow-lg hover:shadow-xl transition-all"
            >
              <Sparkles className="h-5 w-5 mr-2" />
              {parsedSources.length > 0
                ? `Save ${parsedSources.length} Source${parsedSources.length !== 1 ? 's' : ''} & Generate Newsletter`
                : 'Save Sources & Generate'
              }
              <ArrowRight className="h-5 w-5 ml-2" />
            </Button>
          </div>

          {/* Live Preview - Clean & User-Friendly */}
          {input.trim() && parsedSources.length > 0 && (
            <div className="pt-4 border-t">
              <div className="bg-gradient-to-br from-primary/5 to-secondary/5 border border-primary/20 rounded-xl p-5 space-y-4">
                {/* Header */}
                <div className="flex items-center gap-2">
                  <Sparkles className="h-4 w-4 text-primary" />
                  <p className="text-sm font-semibold text-foreground">
                    We detected {parsedSources.length} unique source{parsedSources.length !== 1 ? 's' : ''}:
                  </p>
                </div>

                {/* Source List */}
                <div className="space-y-3">
                  {parsedSources.map((source, idx) => (
                    <div
                      key={idx}
                      className={`flex items-start gap-3 animate-slide-up ${
                        source.isDuplicate ? 'opacity-60' : ''
                      }`}
                      style={{ animationDelay: `${idx * 50}ms` }}
                    >
                      {/* Checkmark or Warning Icon */}
                      <div className="flex items-center gap-2 flex-shrink-0">
                        {source.isDuplicate ? (
                          <span className="text-yellow-500 text-lg">⚠️</span>
                        ) : (
                          <span className="text-success text-lg">✓</span>
                        )}
                        <span className="text-xl">{source.icon}</span>
                      </div>

                      {/* Source Info */}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-baseline gap-2 flex-wrap">
                          <span className="font-semibold text-foreground">{source.displayName}</span>
                          <span className="text-xs text-muted-foreground">
                            → {source.type === 'reddit' ? 'Reddit' : source.type === 'rss' ? 'RSS Feed' : source.type === 'twitter' ? 'Twitter' : source.type === 'youtube' ? 'YouTube' : 'Blog'}
                          </span>
                          {source.isDuplicate && (
                            <span className="text-xs text-yellow-600 dark:text-yellow-400 font-medium">
                              (already added)
                            </span>
                          )}
                        </div>
                        {source.description && (
                          <div className="text-xs text-muted-foreground mt-0.5">
                            └─ {source.description}
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>

                {/* Footer Message */}
                <div className="pt-2 border-t border-primary/10">
                  <p className="text-xs text-muted-foreground flex items-center gap-1">
                    <Lightbulb className="h-3 w-3 text-primary" />
                    <span className="font-medium text-foreground">Ready to save?</span> These sources will power your daily newsletter!
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
