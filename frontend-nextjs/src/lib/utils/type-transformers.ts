/**
 * Type Transformers
 *
 * Utilities to transform between backend (snake_case) and frontend (camelCase) data structures.
 * Handles field name mapping and type conversions.
 */

import { ContentItem as BackendContentItem } from '@/types/content';

/**
 * Backend content item (as returned from API)
 */
export interface BackendContentItemRaw {
  id: string;
  workspace_id: string;
  title: string;
  source: string;
  source_type: string;
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
  created_at: string; // ISO date string
  scraped_at?: string; // ISO date string
  metadata?: Record<string, any>;
}

/**
 * Frontend content item (as used in components)
 * This is what ArticleCard and other components expect
 */
export interface FrontendContentItem {
  id: string;
  title: string;
  summary: string;
  url: string;
  source: string;
  publishedAt?: Date;
  imageUrl?: string;
}

/**
 * Transform backend content item to frontend content item
 * Maps snake_case to camelCase and converts date strings to Date objects
 */
export function transformContentItemToFrontend(item: BackendContentItemRaw): FrontendContentItem {
  return {
    id: item.id,
    title: item.title,
    summary: item.summary || '',
    url: item.source_url || item.external_url || '',
    source: item.source_type || item.source || 'Unknown',
    publishedAt: item.created_at ? new Date(item.created_at) : undefined,
    imageUrl: item.image_url,
  };
}

/**
 * Transform backend content item to the ContentItem type used in Newsletter
 * This preserves more fields for API operations
 */
export function transformContentItem(item: BackendContentItemRaw): BackendContentItem {
  return {
    id: item.id,
    workspace_id: item.workspace_id,
    title: item.title,
    source: item.source,
    source_type: item.source_type,
    source_url: item.source_url,
    content: item.content,
    summary: item.summary,
    author: item.author,
    score: item.score,
    comments_count: item.comments_count,
    tags: item.tags,
    metadata: item.metadata,
    created_at: item.created_at,
    updated_at: item.scraped_at || item.created_at,
  };
}

/**
 * Transform an array of backend content items to frontend items
 */
export function transformContentItemsToFrontend(items: BackendContentItemRaw[]): FrontendContentItem[] {
  return items.map(transformContentItemToFrontend);
}

/**
 * Newsletter item (as stored in newsletter.items)
 * Similar to ContentItem but may have additional fields
 */
export interface NewsletterItem extends BackendContentItemRaw {
  published_at?: string; // Some newsletter items might have this
}

/**
 * Transform newsletter item to frontend format
 * Handles both created_at and published_at fields
 */
export function transformNewsletterItemToFrontend(item: NewsletterItem): FrontendContentItem {
  return {
    id: item.id,
    title: item.title,
    summary: item.summary || '',
    url: item.source_url || item.external_url || '',
    source: item.source_type || item.source || 'Unknown',
    // Prefer published_at, fallback to created_at
    publishedAt: item.published_at
      ? new Date(item.published_at)
      : item.created_at
        ? new Date(item.created_at)
        : undefined,
    imageUrl: item.image_url,
  };
}

/**
 * Transform array of newsletter items to frontend format
 */
export function transformNewsletterItemsToFrontend(items: NewsletterItem[]): FrontendContentItem[] {
  return items.map(transformNewsletterItemToFrontend);
}

/**
 * Type guard to check if an object is a valid content item
 */
export function isValidContentItem(item: any): item is BackendContentItemRaw {
  return (
    typeof item === 'object' &&
    item !== null &&
    typeof item.id === 'string' &&
    typeof item.title === 'string' &&
    (typeof item.source_type === 'string' || typeof item.source === 'string')
  );
}
