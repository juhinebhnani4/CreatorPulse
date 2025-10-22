# Frontend-Backend Field Mapping

**Purpose**: Definitive reference for field name mappings between frontend TypeScript interfaces and backend database/API fields.

**When to use**: When you encounter type errors, API response issues, or need to ensure consistent field naming.

---

## Critical Mismatches (High Priority Fixes)

### ⚠️ Newsletter Fields
| Frontend (OLD - DEPRECATED) | Frontend (NEW - CORRECT) | Backend Field | Status |
|------------------------------|--------------------------|---------------|--------|
| `htmlContent` | `content_html` | `content_html` | ✅ Fixed in latest |
| `textContent` | `content_text` | `content_text` | ✅ Fixed in latest |

**Fix**: Always use snake_case field names to match backend.

### ⚠️ Content Item Fields
| Frontend (INCONSISTENT) | Backend Field | Correct Usage |
|-------------------------|---------------|---------------|
| `sourceType` | `source` | Use `source` |
| `commentsCount` | `comments_count` | Use `comments_count` |
| `sharesCount` | `shares_count` | Use `shares_count` |
| `viewsCount` | `views_count` | Use `views_count` |
| `imageUrl` | `image_url` | Use `image_url` |
| `videoUrl` | `video_url` | Use `video_url` |

**Fix**: Use snake_case to match backend directly, or create transformer functions.

---

## Complete Field Mappings by Domain

### 1. Authentication & Users

#### User Profile
```typescript
// Frontend: User interface
interface User {
  id: string                    // backend: id (UUID)
  email: string                 // backend: email
  username: string              // backend: username
  createdAt: string             // backend: created_at (ISO 8601)
  updatedAt: string             // backend: updated_at
}
```

**API Endpoints**:
- `POST /api/v1/auth/signup` → Returns: `{ success: true, data: { user: User, token: string } }`
- `POST /api/v1/auth/login` → Returns: `{ success: true, data: { user: User, token: string } }`
- `GET /api/v1/auth/me` → Returns: `{ success: true, data: { user: User } }`

#### Auth Tokens
```typescript
// Frontend: Auth state
interface AuthState {
  user: User | null
  token: string | null          // JWT token from backend
  isAuthenticated: boolean
}

// Backend: JWT payload
{
  "sub": "user-uuid",           // Subject (user ID)
  "exp": 1234567890,            // Expiry timestamp (30 minutes)
  "iat": 1234567860             // Issued at timestamp
}
```

---

### 2. Workspaces

#### Workspace Model
```typescript
// Frontend: Workspace interface
interface Workspace {
  id: string                    // backend: id (UUID)
  name: string                  // backend: name
  description: string | null    // backend: description
  ownerId: string               // backend: owner_id
  createdAt: string             // backend: created_at
  updatedAt: string             // backend: updated_at
}
```

#### Workspace Membership
```typescript
// Frontend: WorkspaceMember interface
interface WorkspaceMember {
  id: string                    // backend: id (UUID)
  workspaceId: string           // backend: workspace_id
  userId: string                // backend: user_id
  role: 'owner' | 'editor' | 'viewer'  // backend: role
  joinedAt: string              // backend: joined_at
}
```

#### Workspace Configuration (JSONB)
```typescript
// Frontend: WorkspaceConfig interface
interface WorkspaceConfig {
  sources: SourceConfig[]
  generation: GenerationConfig
  delivery: DeliveryConfig
}

// Backend: workspace_configs.config (JSONB)
{
  "sources": [...],
  "generation": {...},
  "delivery": {...}
}
```

**API Endpoints**:
- `GET /api/v1/workspaces/{id}/config` → Returns: `{ success: true, data: { config: WorkspaceConfig } }`
- `POST /api/v1/workspaces/{id}/config` → Request: `{ config: WorkspaceConfig }`

---

### 3. Content Items

#### Content Item Model
```typescript
// Frontend: ContentItem interface (CORRECT)
interface ContentItem {
  id: string                    // backend: id (UUID)
  workspace_id: string          // backend: workspace_id ⚠️ snake_case
  title: string                 // backend: title
  source: 'reddit' | 'rss' | 'youtube' | 'x' | 'blog'  // backend: source ⚠️ NOT sourceType
  source_url: string            // backend: source_url ⚠️ snake_case
  content: string               // backend: content (full text)
  summary: string | null        // backend: summary (AI-generated)
  author: string | null         // backend: author
  author_url: string | null     // backend: author_url
  score: number | null          // backend: score (Reddit/X engagement)
  comments_count: number | null // backend: comments_count ⚠️ snake_case
  shares_count: number | null   // backend: shares_count ⚠️ snake_case
  views_count: number | null    // backend: views_count ⚠️ snake_case
  image_url: string | null      // backend: image_url ⚠️ snake_case
  video_url: string | null      // backend: video_url ⚠️ snake_case
  external_url: string | null   // backend: external_url
  tags: string[]                // backend: tags (PostgreSQL TEXT[] type)
  category: string | null       // backend: category
  created_at: string            // backend: created_at (ISO 8601) ⚠️ snake_case
  scraped_at: string            // backend: scraped_at ⚠️ snake_case
  metadata: Record<string, any> // backend: metadata (JSONB)
}
```

#### Legacy Field Names (DEPRECATED - DO NOT USE)
```typescript
// ❌ OLD (incorrect)
interface ContentItemOld {
  sourceType: string            // Should be: source
  sourceUrl: string             // Should be: source_url
  commentsCount: number         // Should be: comments_count
  sharesCount: number           // Should be: shares_count
  viewsCount: number            // Should be: views_count
  imageUrl: string              // Should be: image_url
  videoUrl: string              // Should be: video_url
  createdAt: string             // Should be: created_at
  scrapedAt: string             // Should be: scraped_at
}
```

**API Endpoints**:
- `GET /api/v1/content/workspaces/{id}` → Returns: `{ success: true, data: ContentItem[] }`
- `GET /api/v1/content/{id}` → Returns: `{ success: true, data: ContentItem }`
- `POST /api/v1/content/scrape` → Returns: `{ success: true, data: { scraped_count: number, items: ContentItem[] } }`

---

### 4. Newsletters

#### Newsletter Model
```typescript
// Frontend: Newsletter interface (CORRECT)
interface Newsletter {
  id: string                    // backend: id (UUID)
  workspace_id: string          // backend: workspace_id ⚠️ snake_case
  title: string                 // backend: title
  content_html: string          // backend: content_html ⚠️ NOT htmlContent
  content_text: string          // backend: content_text ⚠️ NOT textContent
  model_used: string            // backend: model_used (e.g., "gpt-4-turbo-preview")
  temperature: number           // backend: temperature (0.0-1.0)
  tone: string                  // backend: tone ("professional" | "casual" | "technical" | "friendly")
  language: string              // backend: language ("en", "es", etc.)
  status: 'draft' | 'sent' | 'scheduled'  // backend: status
  generated_at: string          // backend: generated_at (ISO 8601) ⚠️ snake_case
  sent_at: string | null        // backend: sent_at ⚠️ snake_case
  content_items_count: number   // backend: content_items_count ⚠️ snake_case
  metadata: Record<string, any> // backend: metadata (JSONB)
  created_at: string            // backend: created_at ⚠️ snake_case
  updated_at: string            // backend: updated_at ⚠️ snake_case
}
```

#### Legacy Field Names (DEPRECATED - DO NOT USE)
```typescript
// ❌ OLD (incorrect)
interface NewsletterOld {
  htmlContent: string           // Should be: content_html
  textContent: string           // Should be: content_text
  modelUsed: string             // Should be: model_used
  generatedAt: string           // Should be: generated_at
  sentAt: string                // Should be: sent_at
  contentItemsCount: number     // Should be: content_items_count
  createdAt: string             // Should be: created_at
  updatedAt: string             // Should be: updated_at
}
```

**API Endpoints**:
- `POST /api/v1/newsletters` → Request: `{ workspace_id, tone, language, max_items }` → Returns: `{ success: true, data: Newsletter }`
- `GET /api/v1/newsletters/{id}` → Returns: `{ success: true, data: Newsletter }`
- `GET /api/v1/newsletters/{id}/html` → Returns: `{ success: true, data: { html: string } }`
- `PUT /api/v1/newsletters/{id}` → Request: `{ title?, status? }` → Returns: `{ success: true, data: Newsletter }`

---

### 5. Subscribers

#### Subscriber Model
```typescript
// Frontend: Subscriber interface
interface Subscriber {
  id: string                    // backend: id (UUID)
  workspace_id: string          // backend: workspace_id ⚠️ snake_case
  email: string                 // backend: email
  status: 'subscribed' | 'unsubscribed' | 'bounced'  // backend: status
  subscribed_at: string         // backend: subscribed_at ⚠️ snake_case
  unsubscribed_at: string | null  // backend: unsubscribed_at ⚠️ snake_case
}
```

**API Endpoints**:
- `GET /api/v1/delivery/workspaces/{id}/subscribers` → Returns: `{ success: true, data: Subscriber[] }`
- `POST /api/v1/delivery/workspaces/{id}/subscribers` → Request: `{ email }` → Returns: `{ success: true, data: Subscriber }`
- `DELETE /api/v1/delivery/workspaces/{id}/subscribers/{email}` → Returns: `{ success: true }`

---

### 6. Scheduler

#### Scheduler Job Model
```typescript
// Frontend: SchedulerJob interface
interface SchedulerJob {
  id: string                    // backend: id (UUID)
  workspace_id: string          // backend: workspace_id ⚠️ snake_case
  schedule: string              // backend: schedule (cron expression, e.g., "0 9 * * *")
  is_enabled: boolean           // backend: is_enabled ⚠️ snake_case
  status: 'active' | 'paused' | 'completed'  // backend: status
  last_run_at: string | null    // backend: last_run_at ⚠️ snake_case
  next_run_at: string | null    // backend: next_run_at ⚠️ snake_case
  created_at: string            // backend: created_at ⚠️ snake_case
}
```

#### Scheduler Execution Log
```typescript
// Frontend: SchedulerExecutionLog interface
interface SchedulerExecutionLog {
  id: string                    // backend: id (UUID)
  job_id: string                // backend: job_id ⚠️ snake_case
  status: 'success' | 'failed'  // backend: status
  result: Record<string, any>   // backend: result (JSONB)
  error_message: string | null  // backend: error_message ⚠️ snake_case
  started_at: string            // backend: started_at ⚠️ snake_case
  completed_at: string          // backend: completed_at ⚠️ snake_case
}
```

**API Endpoints**:
- `POST /api/v1/scheduler/jobs` → Request: `{ workspace_id, schedule, is_enabled }` → Returns: `{ success: true, data: SchedulerJob }`
- `GET /api/v1/scheduler/jobs/{id}` → Returns: `{ success: true, data: SchedulerJob }`
- `GET /api/v1/scheduler/jobs/{id}/history` → Returns: `{ success: true, data: SchedulerExecutionLog[] }`

---

### 7. Style Profiles

#### Style Profile Model
```typescript
// Frontend: StyleProfile interface
interface StyleProfile {
  id: string                    // backend: id (UUID)
  workspace_id: string          // backend: workspace_id ⚠️ snake_case
  tone: string                  // backend: tone ("professional" | "casual" | "technical" | "friendly")
  sentence_length_avg: number   // backend: sentence_length_avg ⚠️ snake_case
  readability_score: number     // backend: readability_score (Flesch-Kincaid) ⚠️ snake_case
  vocabulary_complexity: number // backend: vocabulary_complexity ⚠️ snake_case
  metadata: Record<string, any> // backend: metadata (JSONB, common phrases, patterns)
  trained_at: string            // backend: trained_at ⚠️ snake_case
}
```

**API Endpoints**:
- `POST /api/v1/style/train` → Request: `{ workspace_id, sample_text }` → Returns: `{ success: true, data: StyleProfile }`
- `GET /api/v1/style/workspaces/{id}` → Returns: `{ success: true, data: StyleProfile }`

---

### 8. Trends

#### Trend Model
```typescript
// Frontend: Trend interface
interface Trend {
  id: string                    // backend: id (UUID)
  workspace_id: string          // backend: workspace_id ⚠️ snake_case
  topic: string                 // backend: topic (e.g., "GPT-4 Release")
  confidence: number            // backend: confidence (0.0-1.0)
  content_count: number         // backend: content_count ⚠️ snake_case
  velocity: number              // backend: velocity (trend growth rate)
  detected_at: string           // backend: detected_at ⚠️ snake_case
}
```

**API Endpoints**:
- `POST /api/v1/trends/detect` → Request: `{ workspace_id }` → Returns: `{ success: true, data: Trend[] }`
- `GET /api/v1/trends/{id}` → Returns: `{ success: true, data: Trend }`
- `GET /api/v1/trends/{id}/content` → Returns: `{ success: true, data: ContentItem[] }`

---

### 9. Feedback

#### Feedback Model
```typescript
// Frontend: Feedback interface
interface Feedback {
  id: string                    // backend: id (UUID)
  workspace_id: string          // backend: workspace_id ⚠️ snake_case
  content_item_id: string | null  // backend: content_item_id ⚠️ snake_case
  newsletter_id: string | null  // backend: newsletter_id ⚠️ snake_case
  rating: number                // backend: rating (1-5)
  feedback_type: 'like' | 'dislike' | 'relevant' | 'irrelevant'  // backend: feedback_type ⚠️ snake_case
  created_at: string            // backend: created_at ⚠️ snake_case
}
```

**API Endpoints**:
- `POST /api/v1/feedback/items` → Request: `{ content_item_id, rating, feedback_type }` → Returns: `{ success: true, data: Feedback }`
- `GET /api/v1/feedback/workspaces/{id}` → Returns: `{ success: true, data: { positive: number, negative: number } }`

---

### 10. Analytics

#### Analytics Event Model
```typescript
// Frontend: AnalyticsEvent interface
interface AnalyticsEvent {
  id: string                    // backend: id (UUID)
  newsletter_id: string         // backend: newsletter_id ⚠️ snake_case
  content_item_id: string | null  // backend: content_item_id (for click events) ⚠️ snake_case
  subscriber_email: string      // backend: subscriber_email ⚠️ snake_case
  event_type: 'sent' | 'delivered' | 'opened' | 'clicked' | 'bounced' | 'spam_reported'  // backend: event_type ⚠️ snake_case
  user_agent: string | null     // backend: user_agent ⚠️ snake_case
  ip_address: string | null     // backend: ip_address (anonymized) ⚠️ snake_case
  device_type: string | null    // backend: device_type ⚠️ snake_case
  email_client: string | null   // backend: email_client ⚠️ snake_case
  timestamp: string             // backend: timestamp (ISO 8601)
}
```

#### Newsletter Analytics Summary
```typescript
// Frontend: NewsletterAnalytics interface
interface NewsletterAnalytics {
  id: string                    // backend: id (UUID)
  newsletter_id: string         // backend: newsletter_id ⚠️ snake_case
  sent_count: number            // backend: sent_count ⚠️ snake_case
  delivered_count: number       // backend: delivered_count ⚠️ snake_case
  open_count: number            // backend: open_count ⚠️ snake_case
  unique_opens: number          // backend: unique_opens ⚠️ snake_case
  click_count: number           // backend: click_count ⚠️ snake_case
  unique_clicks: number         // backend: unique_clicks ⚠️ snake_case
  bounce_count: number          // backend: bounce_count ⚠️ snake_case
  unsubscribe_count: number     // backend: unsubscribe_count ⚠️ snake_case
  open_rate: number             // backend: open_rate (0.0-1.0) ⚠️ snake_case
  click_rate: number            // backend: click_rate (0.0-1.0) ⚠️ snake_case
  last_updated_at: string       // backend: last_updated_at ⚠️ snake_case
}
```

**API Endpoints**:
- `GET /api/v1/analytics/newsletters/{id}` → Returns: `{ success: true, data: NewsletterAnalytics }`
- `GET /api/v1/analytics/workspaces/{id}/summary` → Returns: `{ success: true, data: { total_sent, avg_open_rate, avg_click_rate } }`

---

## Type Transformation Utilities

### Recommended Approach: Use Backend Field Names Directly

Instead of transforming, use backend field names in frontend:

```typescript
// ✅ RECOMMENDED: Match backend exactly
interface ContentItem {
  id: string
  workspace_id: string          // snake_case
  source: string                // Not sourceType
  source_url: string            // snake_case
  comments_count: number        // snake_case
  // ... etc
}
```

### Alternative: Transformation Functions (if needed)

If you must use camelCase in frontend:

```typescript
// lib/utils/type-transformers.ts

export function transformContentItem(backend: any): ContentItemFrontend {
  return {
    id: backend.id,
    workspaceId: backend.workspace_id,
    source: backend.source,  // ⚠️ Use 'source', not 'sourceType'
    sourceUrl: backend.source_url,
    commentsCount: backend.comments_count,
    sharesCount: backend.shares_count,
    viewsCount: backend.views_count,
    imageUrl: backend.image_url,
    videoUrl: backend.video_url,
    createdAt: backend.created_at,
    scrapedAt: backend.scraped_at,
    // ... etc
  }
}

export function transformNewsletter(backend: any): NewsletterFrontend {
  return {
    id: backend.id,
    workspaceId: backend.workspace_id,
    contentHtml: backend.content_html,  // ⚠️ Transform here
    contentText: backend.content_text,
    modelUsed: backend.model_used,
    generatedAt: backend.generated_at,
    sentAt: backend.sent_at,
    contentItemsCount: backend.content_items_count,
    // ... etc
  }
}
```

**Usage**:
```typescript
// In API client
const response = await axios.get('/api/v1/content/workspaces/123')
const items = response.data.data.map(transformContentItem)
```

---

## Common Pitfalls

### 1. Using `sourceType` instead of `source`
```typescript
// ❌ WRONG
const contentItem = {
  sourceType: 'reddit'  // Backend doesn't have this field!
}

// ✅ CORRECT
const contentItem = {
  source: 'reddit'
}
```

### 2. Using camelCase for nested fields
```typescript
// ❌ WRONG
const newsletter = {
  htmlContent: '...',        // Backend uses content_html
  contentItemsCount: 5       // Backend uses content_items_count
}

// ✅ CORRECT
const newsletter = {
  content_html: '...',
  content_items_count: 5
}
```

### 3. Forgetting to handle null values
```typescript
// ❌ WRONG - Will crash if author is null
const authorName = contentItem.author.toUpperCase()

// ✅ CORRECT
const authorName = contentItem.author?.toUpperCase() ?? 'Unknown'
```

### 4. Mixing old and new field names
```typescript
// ❌ WRONG - Inconsistent
interface Newsletter {
  htmlContent: string          // Old naming
  content_text: string         // New naming (mixed!)
}

// ✅ CORRECT - Consistent
interface Newsletter {
  content_html: string         // All snake_case
  content_text: string
}
```

---

## Validation

### Backend Validation (Pydantic)
```python
# backend/models/content.py
from pydantic import BaseModel, Field

class ContentItem(BaseModel):
    id: str
    workspace_id: str
    title: str
    source: Literal["reddit", "rss", "youtube", "x", "blog"]  # ⚠️ Enum validation
    source_url: str = Field(..., min_length=1)
    comments_count: Optional[int] = Field(None, ge=0)  # Must be non-negative
    tags: List[str] = Field(default_factory=list)
    # ... etc
```

### Frontend Validation (Zod)
```typescript
// frontend-nextjs/src/types/validation.ts
import { z } from 'zod'

export const ContentItemSchema = z.object({
  id: z.string().uuid(),
  workspace_id: z.string().uuid(),
  source: z.enum(['reddit', 'rss', 'youtube', 'x', 'blog']),  // ⚠️ Match backend enum
  source_url: z.string().url(),
  comments_count: z.number().int().nonnegative().nullable(),
  tags: z.array(z.string()).default([]),
  // ... etc
})

export type ContentItem = z.infer<typeof ContentItemSchema>
```

---

## Summary

**Key Rules**:
1. ✅ **Use snake_case** for all field names to match backend
2. ✅ **Use `source`** (not `sourceType`) for content items
3. ✅ **Use `content_html`** and `content_text`** (not `htmlContent`, `textContent`) for newsletters
4. ✅ **Handle null values** explicitly in TypeScript
5. ✅ **Validate enums** match exactly between frontend and backend
6. ✅ **Check this file** before writing API client code

**When in doubt**: Check the backend Pydantic models in `backend/models/*.py` for the source of truth.

---

**END OF FRONTEND_BACKEND_MAPPING.md**