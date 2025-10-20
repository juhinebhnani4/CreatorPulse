'use client';

import { useState } from 'react';
import { ImageIcon } from 'lucide-react';

interface ThumbnailProps {
  src?: string | null;
  alt: string;
  source: string;
  className?: string;
  onClick?: () => void;
}

export function Thumbnail({ src, alt, source, className = '', onClick }: ThumbnailProps) {
  const [error, setError] = useState(false);

  // Source-specific fallback colors
  const fallbackColors: Record<string, string> = {
    'reddit': 'bg-red-100 dark:bg-red-950',
    'rss': 'bg-orange-100 dark:bg-orange-950',
    'twitter': 'bg-blue-100 dark:bg-blue-950',
    'x': 'bg-blue-100 dark:bg-blue-950',
    'youtube': 'bg-green-100 dark:bg-green-950',
    'blog': 'bg-purple-100 dark:bg-purple-950'
  };

  const fallbackColor = fallbackColors[source.toLowerCase()] || 'bg-gray-100 dark:bg-gray-800';

  if (!src || error) {
    return (
      <div
        className={`${className} ${fallbackColor} flex items-center justify-center`}
        onClick={onClick}
        data-testid="thumbnail-fallback"
      >
        <ImageIcon className="h-8 w-8 text-muted-foreground" />
      </div>
    );
  }

  return (
    <img
      src={src}
      alt={alt}
      className={className}
      onError={() => setError(true)}
      loading="lazy"
      onClick={onClick}
      data-testid="content-thumbnail"
    />
  );
}
