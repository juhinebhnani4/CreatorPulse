'use client';

import { useTopStories } from '@/lib/api/queries/dashboard';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { getSourceGradient, getSourceDisplayName } from '@/lib/utils/source-gradients';
import { getSourceIcon } from '@/lib/utils/source-icons';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import { useRef, useState } from 'react';

interface TopStory {
  id: string;
  title: string;
  source: string;
  source_url: string;
  image_url?: string;
  score: number;
  time_ago: string;
}

interface TopStoriesProps {
  workspaceId: string;
}

export function TopStories({ workspaceId }: TopStoriesProps) {
  const { data: stories = [], isLoading, isError } = useTopStories(workspaceId);
  const scrollContainerRef = useRef<HTMLDivElement>(null);
  const [failedImages, setFailedImages] = useState<Set<string>>(new Set());

  const scroll = (direction: 'left' | 'right') => {
    if (!scrollContainerRef.current) return;

    const scrollAmount = 300; // Scroll by ~1 card width
    const newScrollLeft =
      scrollContainerRef.current.scrollLeft +
      (direction === 'left' ? -scrollAmount : scrollAmount);

    scrollContainerRef.current.scrollTo({
      left: newScrollLeft,
      behavior: 'smooth',
    });
  };

  // Don't render if no stories
  if (!isLoading && (!stories || stories.length === 0)) {
    return null;
  }

  if (isError) {
    return null; // Silently fail - this is a non-critical feature
  }

  if (isLoading) {
    return (
      <div className="mb-6">
        <h2 className="text-lg font-semibold mb-4">Today's Top Stories</h2>
        <div className="flex gap-4 overflow-x-auto pb-2">
          {[1, 2, 3, 4, 5].map((i) => (
            <Card
              key={i}
              className="flex-shrink-0 w-[280px] h-[220px] animate-pulse bg-muted"
            />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="mb-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold">Today's Top Stories</h2>
        <div className="hidden md:flex gap-2">
          <button
            onClick={() => scroll('left')}
            className="p-2 rounded-lg hover:bg-muted transition-colors"
            aria-label="Scroll left"
          >
            <ChevronLeft className="h-5 w-5" />
          </button>
          <button
            onClick={() => scroll('right')}
            className="p-2 rounded-lg hover:bg-muted transition-colors"
            aria-label="Scroll right"
          >
            <ChevronRight className="h-5 w-5" />
          </button>
        </div>
      </div>

      <div
        ref={scrollContainerRef}
        className="flex gap-4 overflow-x-auto pb-2 scroll-smooth snap-x snap-mandatory hide-scrollbar"
        style={{
          scrollbarWidth: 'none',
          msOverflowStyle: 'none',
        }}
      >
        {stories.map((story: TopStory) => (
          <StoryCard
            key={story.id}
            story={story}
            failedImages={failedImages}
            setFailedImages={setFailedImages}
          />
        ))}
      </div>

      <style jsx>{`
        .hide-scrollbar::-webkit-scrollbar {
          display: none;
        }
      `}</style>
    </div>
  );
}

interface StoryCardProps {
  story: TopStory;
  failedImages: Set<string>;
  setFailedImages: React.Dispatch<React.SetStateAction<Set<string>>>;
}

function StoryCard({ story, failedImages, setFailedImages }: StoryCardProps) {
  const gradient = getSourceGradient(story.source);
  const icon = getSourceIcon(story.source);
  const sourceName = getSourceDisplayName(story.source);

  const handleClick = () => {
    window.open(story.source_url, '_blank', 'noopener,noreferrer');
  };

  const handleImageError = () => {
    if (story.image_url) {
      setFailedImages((prev) => new Set(prev).add(story.image_url!));
    }
  };

  const handleImageLoad = (e: React.SyntheticEvent<HTMLImageElement>) => {
    const img = e.currentTarget;
    // Reject low-quality images (< 400px width)
    if (img.naturalWidth < 400 && story.image_url) {
      setFailedImages((prev) => new Set(prev).add(story.image_url!));
    }
  };

  // Determine if we should show image or gradient
  const shouldUseGradient =
    !story.image_url || failedImages.has(story.image_url);

  return (
    <Card
      onClick={handleClick}
      className="flex-shrink-0 w-[280px] h-[220px] cursor-pointer snap-start
                 overflow-hidden relative group transition-all duration-200
                 hover:scale-[1.02] hover:shadow-lg"
    >
      {/* Background: Image or Gradient */}
      <div className="absolute inset-0">
        {shouldUseGradient ? (
          /* Gradient fallback with centered icon */
          <div
            className="w-full h-full flex items-center justify-center"
            style={{ background: gradient }}
          >
            <span className="text-6xl opacity-20">{icon}</span>
          </div>
        ) : (
          /* High-quality image with overlay */
          <>
            <img
              src={story.image_url}
              alt={story.title}
              className="w-full h-full object-cover"
              onError={handleImageError}
              onLoad={handleImageLoad}
            />
            {/* Enhanced gradient overlay for better text readability */}
            <div
              className="absolute inset-0"
              style={{
                background:
                  'linear-gradient(to bottom, rgba(0,0,0,0.4) 0%, rgba(0,0,0,0.8) 100%)',
              }}
            />
          </>
        )}
      </div>

      {/* Content */}
      <div className="relative h-full p-4 flex flex-col justify-between">
        {/* Source Badge */}
        <div className="flex items-start">
          <Badge className="bg-white/95 text-gray-900 hover:bg-white shadow-md backdrop-blur-sm">
            <span className="mr-1">{icon}</span>
            <span className="text-xs font-medium">{sourceName}</span>
          </Badge>
        </div>

        {/* Title and Time */}
        <div className="space-y-2">
          <h3
            className="text-white font-semibold text-base leading-tight line-clamp-2"
            title={story.title}
          >
            {story.title}
          </h3>
          <p className="text-white/70 text-sm">{story.time_ago}</p>
        </div>
      </div>
    </Card>
  );
}
