/**
 * ContentItem as returned from backend API
 * All fields use snake_case to match backend response
 *
 * CRITICAL FIX #6: Use strict union types for source fields
 * This ensures TypeScript catches invalid source values at compile-time
 */
export interface ContentItem {
  id: string;
  workspace_id: string;
  title: string;
  source: 'reddit' | 'rss' | 'x' | 'youtube' | 'blog'; // Strict union, NOT string
  source_type: 'reddit' | 'rss' | 'x' | 'youtube' | 'blog'; // Same as source (for compatibility)
  source_url: string;
  content?: string;
  summary?: string;
  author?: string;
  author_url?: string;
  score?: number;
  comments_count?: number;
  shares_count?: number;
  views_count?: number;
  image_url?: string;
  video_url?: string;
  external_url?: string;
  tags?: string[];
  category?: string;
  metadata?: Record<string, any>;
  created_at: string; // ISO date string
  scraped_at?: string; // ISO date string
  updated_at?: string; // For compatibility
  published_at?: string; // Optional, used in newsletter items
}

export interface ContentStats {
  total_items: number;
  by_source: Record<string, number>;
  avg_score: number;
  date_range: {
    start: string;
    end: string;
  };
}
