# TypeScript Type Definitions

**Purpose**: Copy-paste ready TypeScript interfaces that exactly match backend database/API schemas.

**When to use**: When writing API clients, creating new components, or fixing type errors.

---

## Usage Instructions

1. **Copy entire interfaces** from this file into your TypeScript code
2. **Do NOT modify field names** - they match backend exactly
3. **Use snake_case** for all fields (matches PostgreSQL columns)
4. **Import from central location**: Create `src/types/index.ts` and import from there

---

## Core Type Utilities

### API Response Wrapper (All Endpoints)

```typescript
/**
 * Standard API response wrapper
 * All backend endpoints return this structure
 */
export interface APIResponse<T = any> {
  success: boolean
  data?: T
  error?: string
  message?: string
}

/**
 * Usage example:
 * const response: APIResponse<Newsletter> = await axios.post('/api/v1/newsletters', {...})
 * if (response.success) {
 *   console.log(response.data.title)
 * } else {
 *   console.error(response.error)
 * }
 */
```

### Pagination Wrapper

```typescript
export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  has_more: boolean
}

/**
 * Usage:
 * const response: APIResponse<PaginatedResponse<ContentItem>> = await axios.get('/api/v1/content/...')
 */
```

---

## Authentication & Users

### User

```typescript
/**
 * User profile
 * Table: public.users
 * Related: auth.users (Supabase managed)
 */
export interface User {
  id: string                    // UUID, primary key
  email: string                 // Unique, required
  username: string              // Display name, required
  created_at: string            // ISO 8601 timestamp
  updated_at: string            // ISO 8601 timestamp
}
```

### Auth State (Frontend only)

```typescript
/**
 * Frontend auth state (Zustand store)
 * Not from backend, but included for completeness
 */
export interface AuthState {
  user: User | null
  token: string | null          // JWT token
  isAuthenticated: boolean
  login: (email: string, password: string) => Promise<void>
  logout: () => void
  refreshToken: () => Promise<void>
}
```

### Auth Requests/Responses

```typescript
export interface SignupRequest {
  email: string
  password: string
  username: string
}

export interface LoginRequest {
  email: string
  password: string
}

export interface AuthResponse {
  user: User
  token: string                 // JWT token (30min expiry)
}
```

---

## Workspaces

### Workspace

```typescript
/**
 * Workspace (multi-tenant container)
 * Table: workspaces
 */
export interface Workspace {
  id: string                    // UUID, primary key
  name: string                  // Unique, required
  description: string | null
  owner_id: string              // UUID, foreign key → users.id
  created_at: string            // ISO 8601 timestamp
  updated_at: string            // ISO 8601 timestamp
}
```

### Workspace Member

```typescript
/**
 * Workspace team membership
 * Table: user_workspaces
 */
export interface WorkspaceMember {
  id: string                    // UUID, primary key
  workspace_id: string          // UUID, foreign key → workspaces.id
  user_id: string               // UUID, foreign key → users.id
  role: 'owner' | 'editor' | 'viewer'  // Role-based permissions
  joined_at: string             // ISO 8601 timestamp
}

/**
 * Role permissions:
 * - owner: Full access (read, write, delete, manage team)
 * - editor: Read and write (create/edit content and newsletters)
 * - viewer: Read-only access
 */
```

### Workspace Configuration

```typescript
/**
 * Workspace configuration (JSONB field)
 * Table: workspace_configs.config
 */
export interface WorkspaceConfig {
  sources: SourceConfig[]
  generation: GenerationConfig
  delivery: DeliveryConfig
}

export interface SourceConfig {
  type: 'reddit' | 'rss' | 'youtube' | 'x' | 'blog'
  enabled: boolean
  config: RedditConfig | RSSConfig | YouTubeConfig | XConfig | BlogConfig
}

/**
 * Reddit source configuration
 */
export interface RedditConfig {
  subreddits: string[]          // e.g., ["MachineLearning", "artificial"]
  sort?: 'hot' | 'new' | 'top'  // Default: 'hot'
  limit?: number                // Default: 25, max: 100
}

/**
 * RSS feed source configuration
 */
export interface RSSConfig {
  feed_urls: string[]           // e.g., ["https://example.com/feed.xml"]
  limit?: number                // Default: 10
}

/**
 * YouTube source configuration
 */
export interface YouTubeConfig {
  channel_ids?: string[]        // e.g., ["UCBJycsmduvYEL83R_U4JriQ"]
  query?: string                // Search query (e.g., "AI news")
  limit?: number                // Default: 10
}

/**
 * X/Twitter source configuration
 */
export interface XConfig {
  usernames?: string[]          // e.g., ["OpenAI", "AndrewYNg"]
  search_query?: string         // Search query (e.g., "#AI")
  limit?: number                // Default: 10
}

/**
 * Blog source configuration
 */
export interface BlogConfig {
  url: string                   // Blog homepage URL
  selectors: {
    article: string             // CSS selector for article container
    title: string               // CSS selector for title
    content: string             // CSS selector for content
    author?: string             // CSS selector for author (optional)
    date?: string               // CSS selector for date (optional)
  }
}

/**
 * Newsletter generation configuration
 */
export interface GenerationConfig {
  model: 'openai' | 'openrouter'
  openai_model?: string         // e.g., "gpt-4-turbo-preview"
  openrouter_model?: string     // e.g., "anthropic/claude-3.5-sonnet"
  temperature: number           // 0.0-1.0, default: 0.7 (higher = more creative)
  tone: 'professional' | 'casual' | 'technical' | 'friendly'
  language: string              // ISO 639-1 code (e.g., "en", "es")
  max_items: number             // Max content items per newsletter, default: 10
}

/**
 * Email delivery configuration
 */
export interface DeliveryConfig {
  method: 'smtp' | 'sendgrid'
  from_name: string             // Display name in "From" field
  reply_to?: string             // Reply-to email address (optional)
}
```

---

## Content Items

### Content Item

```typescript
/**
 * Scraped content item
 * Table: content_items
 */
export interface ContentItem {
  id: string                    // UUID, primary key
  workspace_id: string          // UUID, foreign key → workspaces.id
  title: string                 // Required
  source: 'reddit' | 'rss' | 'youtube' | 'x' | 'blog'  // Source type
  source_url: string            // Original URL (unique per workspace)
  content: string               // Full text content
  summary: string | null        // AI-generated summary (optional)
  author: string | null
  author_url: string | null
  score: number | null          // Engagement score (Reddit upvotes, X likes, etc.)
  comments_count: number | null
  shares_count: number | null
  views_count: number | null
  image_url: string | null      // Thumbnail/featured image
  video_url: string | null      // Video embed URL
  external_url: string | null   // Additional related URL
  tags: string[]                // PostgreSQL TEXT[] array
  category: string | null
  created_at: string            // ISO 8601 timestamp (original publish date)
  scraped_at: string            // ISO 8601 timestamp (when scraped)
  metadata: Record<string, any> // JSONB field for source-specific data
}

/**
 * Unique constraint: (workspace_id, source_url)
 * Migration: 010_add_content_unique_constraint.sql
 */
```

### Content Metadata Examples

```typescript
/**
 * Reddit-specific metadata
 */
interface RedditMetadata {
  permalink: string             // Reddit post permalink
  subreddit: string             // Subreddit name
  num_comments: number
  upvote_ratio: number          // 0.0-1.0
  gilded: number                // Awards count
}

/**
 * YouTube-specific metadata
 */
interface YouTubeMetadata {
  video_id: string
  channel_title: string
  duration: string              // ISO 8601 duration (e.g., "PT15M33S")
  view_count: number
  like_count: number
  comment_count: number
}

/**
 * X/Twitter-specific metadata
 */
interface XMetadata {
  tweet_id: string
  user_handle: string
  retweet_count: number
  favorite_count: number
  replied_to?: string           // Tweet ID if reply
}
```

---

## Newsletters

### Newsletter

```typescript
/**
 * Generated newsletter
 * Table: newsletters
 */
export interface Newsletter {
  id: string                    // UUID, primary key
  workspace_id: string          // UUID, foreign key → workspaces.id
  title: string                 // Required
  content_html: string          // HTML version (with CSS)
  content_text: string          // Plain text version
  model_used: string            // AI model name (e.g., "gpt-4-turbo-preview")
  temperature: number           // 0.0-1.0
  tone: string                  // "professional" | "casual" | "technical" | "friendly"
  language: string              // ISO 639-1 code
  status: 'draft' | 'sent' | 'scheduled'
  generated_at: string          // ISO 8601 timestamp
  sent_at: string | null        // ISO 8601 timestamp (null if not sent)
  content_items_count: number   // Number of items included
  metadata: Record<string, any> // JSONB field (generation params, etc.)
  created_at: string            // ISO 8601 timestamp
  updated_at: string            // ISO 8601 timestamp
}
```

### Newsletter Generation Request

```typescript
export interface GenerateNewsletterRequest {
  workspace_id: string
  tone?: string                 // Default: from workspace config
  language?: string             // Default: from workspace config
  max_items?: number            // Default: from workspace config
  custom_prompt?: string        // Optional custom instructions
}

export interface GenerateNewsletterResponse {
  newsletter: Newsletter
  content_items: ContentItem[]  // Items included in newsletter
}
```

---

## Subscribers

### Subscriber

```typescript
/**
 * Email subscriber
 * Table: subscribers
 */
export interface Subscriber {
  id: string                    // UUID, primary key
  workspace_id: string          // UUID, foreign key → workspaces.id
  email: string                 // Email address (unique per workspace)
  status: 'subscribed' | 'unsubscribed' | 'bounced'
  subscribed_at: string         // ISO 8601 timestamp
  unsubscribed_at: string | null  // ISO 8601 timestamp (null if still subscribed)
}
```

---

## Email Delivery

### Delivery Log

```typescript
/**
 * Email delivery log entry
 * Table: delivery_logs (implied, not in migration files but used in service)
 */
export interface DeliveryLog {
  id: string                    // UUID, primary key
  newsletter_id: string         // UUID, foreign key → newsletters.id
  subscriber_email: string
  status: 'sent' | 'failed' | 'bounced'
  error_message: string | null
  sent_at: string               // ISO 8601 timestamp
}
```

### Delivery Request/Response

```typescript
export interface SendNewsletterRequest {
  newsletter_id: string
  subscriber_ids?: string[]     // If omitted, sends to all subscribed
  test_mode?: boolean           // If true, sends only to sender
}

export interface SendNewsletterResponse {
  sent_count: number
  failed_count: number
  failed_emails: string[]       // List of emails that failed
}
```

---

## Scheduler

### Scheduler Job

```typescript
/**
 * Scheduled job (automated newsletter generation + send)
 * Table: scheduler_jobs
 */
export interface SchedulerJob {
  id: string                    // UUID, primary key
  workspace_id: string          // UUID, foreign key → workspaces.id
  schedule: string              // Cron expression (e.g., "0 9 * * *" = daily at 9am)
  is_enabled: boolean           // Can be paused without deleting
  status: 'active' | 'paused' | 'completed'
  last_run_at: string | null    // ISO 8601 timestamp (null if never run)
  next_run_at: string | null    // ISO 8601 timestamp (calculated from cron)
  created_at: string            // ISO 8601 timestamp
}

/**
 * Cron expression examples:
 * - "0 9 * * *"    = Every day at 9:00 AM
 * - "0 9 * * 1"    = Every Monday at 9:00 AM
 * - "0 9 * * 1-5"  = Every weekday at 9:00 AM
 * - "0 */6 * * *"  = Every 6 hours
 * - "0 0 1 * *"    = First day of every month at midnight
 */
```

### Scheduler Execution Log

```typescript
/**
 * Job execution history
 * Table: scheduler_execution_logs
 */
export interface SchedulerExecutionLog {
  id: string                    // UUID, primary key
  job_id: string                // UUID, foreign key → scheduler_jobs.id
  status: 'success' | 'failed'
  result: ExecutionResult       // JSONB field with execution details
  error_message: string | null
  started_at: string            // ISO 8601 timestamp
  completed_at: string          // ISO 8601 timestamp
}

export interface ExecutionResult {
  scraped_items: number
  newsletter_id?: string        // UUID if newsletter generated
  sent_count?: number
  failed_count?: number
  errors?: string[]
}
```

---

## Style Profiles

### Style Profile

```typescript
/**
 * Learned writing style
 * Table: style_profiles
 */
export interface StyleProfile {
  id: string                    // UUID, primary key
  workspace_id: string          // UUID, foreign key → workspaces.id
  tone: string                  // Detected tone
  sentence_length_avg: number   // Average words per sentence
  readability_score: number     // Flesch-Kincaid grade level
  vocabulary_complexity: number // 0.0-1.0 (simple to complex)
  metadata: StyleMetadata       // JSONB field
  trained_at: string            // ISO 8601 timestamp
}

export interface StyleMetadata {
  common_phrases: string[]      // Frequently used phrases
  vocabulary_preferences: Record<string, number>  // Word frequency
  sentence_patterns: string[]   // Common sentence structures
  punctuation_style: Record<string, number>  // Punctuation usage
}
```

---

## Trends

### Trend

```typescript
/**
 * Detected content trend
 * Table: trends
 */
export interface Trend {
  id: string                    // UUID, primary key
  workspace_id: string          // UUID, foreign key → workspaces.id
  topic: string                 // Trend topic/name (e.g., "GPT-4 Release")
  confidence: number            // 0.0-1.0 (detection confidence)
  content_count: number         // Number of content items mentioning topic
  velocity: number              // Trend growth rate (higher = rising faster)
  detected_at: string           // ISO 8601 timestamp
}

/**
 * Trend scoring algorithm (TrendService):
 * - Mention frequency: 30% weight
 * - Velocity (rising trend): 40% weight
 * - Source diversity: 30% weight
 */
```

---

## Feedback

### Feedback

```typescript
/**
 * User feedback on content/newsletters
 * Table: feedback
 */
export interface Feedback {
  id: string                    // UUID, primary key
  workspace_id: string          // UUID, foreign key → workspaces.id
  content_item_id: string | null  // UUID, foreign key → content_items.id (null for newsletter feedback)
  newsletter_id: string | null  // UUID, foreign key → newsletters.id (null for content feedback)
  rating: number                // 1-5 stars
  feedback_type: 'like' | 'dislike' | 'relevant' | 'irrelevant'
  created_at: string            // ISO 8601 timestamp
}

/**
 * Feedback impact on future generation:
 * - Preferred sources: +20% score boost
 * - Disliked sources: -30% score penalty
 * Applied in NewsletterService.generate_newsletter()
 */
```

### Feedback Summary

```typescript
export interface FeedbackSummary {
  positive_count: number        // like + relevant
  negative_count: number        // dislike + irrelevant
  avg_rating: number            // Average star rating
  source_preferences: Record<string, number>  // Source → preference score
}
```

---

## Analytics

### Analytics Event

```typescript
/**
 * Individual tracking event
 * Table: email_analytics_events
 */
export interface AnalyticsEvent {
  id: string                    // UUID, primary key
  newsletter_id: string         // UUID, foreign key → newsletters.id
  content_item_id: string | null  // UUID (for click events on specific content)
  subscriber_email: string
  event_type: 'sent' | 'delivered' | 'opened' | 'clicked' | 'bounced' | 'spam_reported'
  user_agent: string | null     // Browser/email client user agent
  ip_address: string | null     // Anonymized IP address
  device_type: string | null    // 'desktop' | 'mobile' | 'tablet'
  email_client: string | null   // 'gmail' | 'outlook' | 'apple_mail' | etc.
  timestamp: string             // ISO 8601 timestamp
}
```

### Newsletter Analytics Summary

```typescript
/**
 * Aggregated newsletter metrics
 * Table: newsletter_analytics_summary
 */
export interface NewsletterAnalytics {
  id: string                    // UUID, primary key
  newsletter_id: string         // UUID, foreign key → newsletters.id
  sent_count: number
  delivered_count: number       // sent - bounced
  open_count: number            // Total opens (includes re-opens)
  unique_opens: number          // Unique subscribers who opened
  click_count: number           // Total clicks (includes multiple clicks)
  unique_clicks: number         // Unique subscribers who clicked
  bounce_count: number
  unsubscribe_count: number
  open_rate: number             // unique_opens / delivered_count
  click_rate: number            // unique_clicks / delivered_count
  last_updated_at: string       // ISO 8601 timestamp
}
```

### Content Performance

```typescript
/**
 * Per-content-item engagement metrics
 * Table: content_performance
 */
export interface ContentPerformance {
  id: string                    // UUID, primary key
  content_item_id: string       // UUID, foreign key → content_items.id
  newsletter_id: string         // UUID, foreign key → newsletters.id
  click_count: number           // Total clicks on this content
  unique_clicks: number         // Unique subscribers who clicked
  click_rate: number            // unique_clicks / newsletter.delivered_count
  last_updated_at: string       // ISO 8601 timestamp
}
```

### Workspace Analytics Summary

```typescript
export interface WorkspaceAnalyticsSummary {
  total_sent: number            // Total newsletters sent
  total_delivered: number
  avg_open_rate: number         // Average across all newsletters
  avg_click_rate: number
  total_subscribers: number
  active_subscribers: number    // status = 'subscribed'
  top_performing_content: ContentPerformance[]
  recent_newsletters: NewsletterAnalytics[]
}
```

---

## Tracking (HMAC Tokens)

### Tracking Token Payload

```typescript
/**
 * HMAC tracking token payload (used in URLs)
 * Not stored in database, encoded in tracking URLs
 */
export interface TrackingTokenPayload {
  newsletter_id: string
  subscriber_email: string
  content_item_id?: string      // For click tracking
  target_url?: string           // For click redirect
  timestamp: number             // Unix timestamp
}

/**
 * Tracking URL examples:
 * - Open: /track/pixel/{hmac_token}.png
 * - Click: /track/click/{hmac_token}
 * - Unsubscribe: /unsubscribe/{hmac_token}
 */
```

---

## Zod Validation Schemas

### Example: Content Item Validation

```typescript
import { z } from 'zod'

export const ContentItemSchema = z.object({
  id: z.string().uuid(),
  workspace_id: z.string().uuid(),
  title: z.string().min(1).max(500),
  source: z.enum(['reddit', 'rss', 'youtube', 'x', 'blog']),
  source_url: z.string().url(),
  content: z.string().min(1),
  summary: z.string().nullable(),
  author: z.string().nullable(),
  author_url: z.string().url().nullable(),
  score: z.number().int().nonnegative().nullable(),
  comments_count: z.number().int().nonnegative().nullable(),
  shares_count: z.number().int().nonnegative().nullable(),
  views_count: z.number().int().nonnegative().nullable(),
  image_url: z.string().url().nullable(),
  video_url: z.string().url().nullable(),
  external_url: z.string().url().nullable(),
  tags: z.array(z.string()).default([]),
  category: z.string().nullable(),
  created_at: z.string().datetime(),
  scraped_at: z.string().datetime(),
  metadata: z.record(z.any()).default({}),
})

export type ContentItem = z.infer<typeof ContentItemSchema>
```

---

## Type Guards

```typescript
/**
 * Type guard to check if response is successful
 */
export function isSuccessResponse<T>(
  response: APIResponse<T>
): response is APIResponse<T> & { success: true; data: T } {
  return response.success === true && response.data !== undefined
}

/**
 * Usage:
 * const response = await fetchNewsletter(id)
 * if (isSuccessResponse(response)) {
 *   console.log(response.data.title)  // ✅ TypeScript knows data exists
 * } else {
 *   console.error(response.error)
 * }
 */

/**
 * Type guard to check if value is ContentItem
 */
export function isContentItem(value: any): value is ContentItem {
  return (
    typeof value === 'object' &&
    value !== null &&
    typeof value.id === 'string' &&
    typeof value.source === 'string' &&
    ['reddit', 'rss', 'youtube', 'x', 'blog'].includes(value.source)
  )
}
```

---

## Recommended File Structure

```typescript
// src/types/index.ts
export * from './api'
export * from './auth'
export * from './workspace'
export * from './content'
export * from './newsletter'
export * from './subscriber'
export * from './scheduler'
export * from './style'
export * from './trend'
export * from './feedback'
export * from './analytics'

// Usage in components:
import { ContentItem, Newsletter, APIResponse } from '@/types'
```

---

## Important Notes

1. **Always use snake_case** for field names (matches PostgreSQL columns)
2. **UUID fields** are strings, not a custom UUID type
3. **Timestamps** are ISO 8601 strings (e.g., "2025-01-20T12:34:56.789Z")
4. **Nullable fields** use `| null`, never `undefined`
5. **Arrays** default to empty array `[]` if not provided
6. **JSONB fields** use `Record<string, any>` type
7. **Enums** use TypeScript literal types (e.g., `'draft' | 'sent' | 'scheduled'`)

---

**END OF TYPE_DEFINITIONS.md**