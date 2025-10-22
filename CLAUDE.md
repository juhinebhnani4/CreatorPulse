<!--
FILE: CLAUDE.md
PRIORITY: 1 - CRITICAL - READ THIS FIRST EVERY CHAT
LAST_UPDATED: 2025-01-20
AUTO_UPDATE: Yes (via .git/hooks/post-commit)
TOKEN_BUDGET: ~20k tokens (10% of 200k budget)
-->

# CreatorPulse - AI Newsletter Generation Platform

## 🚨 START HERE - Navigation Guide

**You are Claude, starting a new chat session. Read this file first, then navigate based on the task.**

### Quick Task-Based Navigation

| **Task** | **Read These Files (in order)** |
|----------|--------------------------------|
| **Fixing frontend error** | 1. [Common Errors](#common-errors-quick-reference) (below) <br> 2. `docs/_PRIORITY_1_CONTEXT/FRONTEND_BACKEND_MAPPING.md` <br> 3. `docs/_PRIORITY_1_CONTEXT/TYPE_DEFINITIONS.md` |
| **Backend 500 error** | 1. [Common Errors](#common-errors-quick-reference) (below) <br> 2. `docs/_PRIORITY_1_CONTEXT/COMMON_ERRORS.md` <br> 3. Relevant service file |
| **API integration issue** | 1. [Frontend-Backend Mappings](#frontend-backend-field-mappings-quick-reference) (below) <br> 2. `docs/_PRIORITY_2_REFERENCE/API_REFERENCE.md` |
| **Type mismatch** | 1. [Type Definitions](#critical-type-definitions-quick-reference) (below) <br> 2. `docs/_PRIORITY_1_CONTEXT/TYPE_DEFINITIONS.md` |
| **Adding new feature** | 1. [Architecture Overview](#architecture-overview) (below) <br> 2. [Data Flow](#data-flow) (below) <br> 3. Relevant service files |
| **Database query issue** | 1. [Database Schema](#database-schema-quick-reference) (below) <br> 2. `docs/_PRIORITY_2_REFERENCE/DATABASE_SCHEMA.md` |
| **Understanding codebase** | Read this entire file, then explore as needed |

---

## Project Overview

**CreatorPulse** is a production-ready, full-stack AI newsletter generation platform that automates content aggregation from multiple sources (Reddit, RSS, YouTube, X/Twitter, Blogs), generates AI-powered newsletters with customized styling, and delivers them to subscribers with comprehensive analytics.

### Key Facts
- **Status**: Production-ready, 8 sprints completed, deployed on Railway
- **Architecture**: FastAPI backend + Next.js 14 frontend + Supabase PostgreSQL
- **Team Model**: Multi-tenant workspaces with role-based access
- **AI Providers**: OpenAI (GPT-4) and OpenRouter (Claude, alternatives)
- **Email Delivery**: SMTP (Gmail/Outlook) and SendGrid
- **Background Jobs**: APScheduler with async task execution

### Tech Stack Summary
| Layer | Technology |
|-------|-----------|
| **Backend** | Python 3.11, FastAPI 0.95+, Uvicorn ASGI |
| **Frontend** | Next.js 14.2, React 18, TypeScript 5 |
| **Database** | Supabase (PostgreSQL) with Row-Level Security |
| **Auth** | Supabase Auth (JWT), python-jose |
| **State** | Zustand 5 with localStorage persistence |
| **Data Fetching** | TanStack React Query 5, Axios |
| **UI** | Radix UI, Tailwind CSS 3.4 |
| **Scrapers** | BeautifulSoup4, feedparser, trafilatura |
| **AI/NLP** | OpenAI API, nltk, scikit-learn, textstat |
| **Scheduling** | APScheduler (asyncio, cron triggers) |
| **Testing** | pytest (backend), Playwright (frontend E2E) |

---

## Architecture Overview

### System Architecture Diagram
```
┌─────────────────────────────────────────────────────────────────┐
│                    Frontend Layer (Next.js 14)                   │
│                                                                   │
│  Dashboard | Content Browser | Newsletters | Settings | Analytics│
│  Delivery | Scheduler | Trends | Feedback | Style Training      │
│                                                                   │
│  State: Zustand + React Query                                    │
└─────────────────────────────────────────────────────────────────┘
                              ↓
                    HTTP/REST (Axios + JWT Auth)
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    FastAPI Backend (12 Routers)                  │
│                                                                   │
│  Auth | Workspaces | Content | Newsletters | Subscribers         │
│  Delivery | Scheduler | Style | Trends | Feedback | Analytics   │
│  Tracking | Workspace Config                                     │
│                                                                   │
│  Middleware: CORS, Auth (JWT verify), Rate Limiting              │
└─────────────────────────────────────────────────────────────────┘
                              ↓
                    Service Layer (Business Logic)
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    Data & Integration Layer                      │
│                                                                   │
│  [Supabase PostgreSQL]  [Scrapers]      [AI APIs]    [Email]    │
│  - 17 tables            - Reddit        - OpenAI     - SMTP      │
│  - RLS policies         - RSS           - OpenRouter - SendGrid  │
│  - Migrations           - YouTube                                │
│                         - X/Twitter                              │
│                         - Blogs                                  │
│                                                                   │
│  [Background Worker]                                             │
│  - APScheduler (asyncio)                                         │
│  - Cron-based job execution                                      │
│  - Content scrape → Generate → Send pipeline                     │
└─────────────────────────────────────────────────────────────────┘
```

### Architectural Patterns
1. **Service Layer Pattern** - Business logic isolated in `backend/services/`
2. **Base Service Pattern** - All services extend `BaseService` for consistency
3. **Template Method Pattern** - Base scraper class with uniform interface
4. **Dependency Injection** - Services accept DB connections for testing
5. **Multi-Tenancy** - Workspace-based isolation with RLS policies
6. **Repository Pattern** - Supabase manager abstracts data access

---

## Critical File Locations

### Frontend Pages (Quick Reference)

**Public Routes**:
- `/` - Landing page (marketing)
- `/login` - Authentication
- `/register` - Sign up

**Protected Routes** (requires login):
- `/app` - Dashboard (main hub)
- `/app/content` - Content Library (browse/filter scraped content)
- `/app/history` - Newsletter history (view past newsletters)
- `/app/settings` - ⭐ **Unified Settings Hub** (sidebar with 10 sections)
  - Essential: Sources, Schedule, Subscribers, Email, Workspace
  - Advanced: API Keys, Style, Trends, Analytics, Feedback

**Dedicated Pages** (future full-screen views, also available in Settings):
- `/app/subscribers`, `/app/schedule`, `/app/style`, `/app/trends`, `/app/feedback`, `/app/analytics`

**Note**: Settings page provides quick access via sidebar. Dedicated pages are reserved for future power-user interfaces.

---

### Backend (Python)
```
backend/
├── main.py                          # FastAPI app entry, CORS, routes
├── settings.py                      # Pydantic settings (env vars)
├── database.py                      # SupabaseManager singleton
├── worker.py                        # APScheduler background jobs
│
├── api/
│   ├── v1/                          # API routes (12 routers)
│   │   ├── auth.py                  # POST /signup, /login, /refresh
│   │   ├── workspaces.py            # CRUD workspaces, config, members
│   │   ├── content.py               # Scraping, listing, stats
│   │   ├── newsletters.py           # Generate, CRUD, HTML/text export
│   │   ├── delivery.py              # Send, test, history, subscribers
│   │   ├── scheduler.py             # CRUD jobs, pause/resume, history
│   │   ├── style.py                 # Train, get profile, test
│   │   ├── trends.py                # Detect, list, details
│   │   ├── feedback.py              # Rate items/newsletters, preferences
│   │   ├── analytics.py             # Events, metrics, export, dashboard
│   │   ├── subscribers.py           # CRUD subscriber list
│   │   └── workspaces.py            # Workspace config management
│   └── tracking.py                  # Pixel tracking, click tracking, unsubscribe
│
├── services/                        # Business logic layer
│   ├── base_service.py              # BaseService (DB, logger)
│   ├── auth_service.py              # Signup, login, token generation
│   ├── workspace_service.py         # Workspace CRUD, team management
│   ├── content_service.py           # Scraping orchestration
│   ├── newsletter_service.py        # AI generation (OpenAI/OpenRouter)
│   ├── delivery_service.py          # Email sending (SMTP/SendGrid)
│   ├── scheduler_service.py         # Job scheduling, execution logs
│   ├── style_service.py             # Style analysis and training
│   ├── trend_service.py             # Trend detection (TF-IDF, K-means)
│   ├── feedback_service.py          # Feedback collection and application
│   ├── analytics_service.py         # Analytics calculation
│   └── tracking_service.py          # Tracking event recording
│
├── models/                          # Pydantic schemas (request/response)
│   ├── auth.py, workspace.py, content.py, newsletter.py
│   ├── subscriber.py, scheduler.py, style_profile.py, trend.py
│   ├── feedback.py, analytics_models.py, responses.py
│   └── newsletter_responses.py      # Standardized API responses
│
├── middleware/
│   ├── auth.py                      # get_current_user JWT dependency
│   ├── cors.py                      # CORS configuration
│   └── rate_limiter.py              # Slowapi rate limiting
│
├── utils/
│   ├── error_handling.py            # @handle_service_errors decorator
│   └── hmac_auth.py                 # HMAC token generation for tracking
│
├── config/
│   ├── constants.py                 # Magic numbers, defaults
│   └── __init__.py
│
├── migrations/                      # SQL migrations (10 files)
│   ├── 001_create_users_table.sql
│   ├── 002_create_content_items_table.sql
│   ├── 003_create_newsletters_table.sql
│   ├── ... (through 010)
│   └── 010_add_content_unique_constraint.sql
│
└── tests/
    ├── conftest.py                  # Pytest fixtures
    ├── factories.py                 # Test data factories
    ├── unit/
    └── integration/                 # API endpoint tests
```

### Frontend (Next.js/TypeScript)
```
frontend-nextjs/
├── src/
│   ├── app/                         # Next.js App Router
│   │   ├── page.tsx                 # Landing page (public)
│   │   ├── login/page.tsx           # Login
│   │   ├── register/page.tsx        # Registration
│   │   └── app/                     # Protected routes (dashboard)
│   │       ├── page.tsx             # Dashboard (main hub)
│   │       ├── content/page.tsx     # Content browser (dedicated page)
│   │       ├── history/page.tsx     # Newsletter history (dedicated page)
│   │       ├── newsletters/         # Newsletter management (implied)
│   │       │
│   │       ├── settings/page.tsx    # ⭐ UNIFIED SETTINGS HUB (sidebar with 10 sections)
│   │       │                        #    Sections: Sources, Schedule, Subscribers, Email, Workspace,
│   │       │                        #             API Keys, Style, Trends, Analytics, Feedback
│   │       │
│   │       ├── subscribers/page.tsx # Subscribers (dedicated page, also in Settings)
│   │       ├── schedule/page.tsx    # Scheduler (dedicated page, also in Settings)
│   │       ├── style/page.tsx       # Style training (dedicated page, also in Settings)
│   │       ├── trends/page.tsx      # Trends (dedicated page, also in Settings)
│   │       ├── feedback/page.tsx    # Feedback (dedicated page, also in Settings)
│   │       └── analytics/page.tsx   # Analytics (dedicated page, also in Settings)
│   │
│   │   # NOTE: Some features exist in BOTH Settings (sidebar section) AND dedicated pages.
│   │   # - Settings provides unified quick access via sidebar navigation
│   │   # - Dedicated pages are reserved for future full-screen power-user interfaces
│   │   # - This architecture allows flexibility: enhance dedicated pages without cluttering Settings
│   │
│   ├── components/
│   │   ├── dashboard/               # Dashboard-specific components
│   │   │   ├── enhanced-draft-card.tsx
│   │   │   ├── article-card.tsx
│   │   │   ├── stats-overview.tsx
│   │   │   └── recent-activity.tsx
│   │   ├── modals/                  # Modal dialogs
│   │   │   ├── draft-editor-modal.tsx
│   │   │   ├── send-confirmation-modal.tsx
│   │   │   ├── add-source-modal.tsx
│   │   │   └── manage-sources-modal.tsx
│   │   ├── settings/                # Settings page components (10 section components)
│   │   │   ├── settings-sidebar.tsx # Sidebar navigation
│   │   │   ├── setup-progress.tsx   # Progress tracker
│   │   │   ├── sources-settings.tsx # Content sources configuration
│   │   │   ├── schedule-settings.tsx # Schedule configuration
│   │   │   ├── subscribers-settings.tsx # Subscriber management
│   │   │   ├── email-settings.tsx   # Email provider setup
│   │   │   ├── workspace-settings.tsx # Workspace configuration
│   │   │   ├── api-keys-settings.tsx # API keys management
│   │   │   ├── style-settings.tsx   # Writing style training
│   │   │   ├── trends-settings.tsx  # Trends detection config
│   │   │   ├── analytics-settings.tsx # Analytics preferences
│   │   │   └── feedback-settings.tsx # Feedback collection config
│   │   └── ui/                      # Radix UI components
│   │       ├── button.tsx, input.tsx, card.tsx, dialog.tsx
│   │       └── ... (20+ UI primitives)
│   │
│   ├── lib/
│   │   ├── store/                   # Zustand state management
│   │   │   ├── auth-store.ts        # Auth state (user, token)
│   │   │   └── workspace-store.ts   # Current workspace
│   │   ├── api/                     # API client functions
│   │   │   ├── auth.ts, workspaces.ts, content.ts
│   │   │   ├── newsletters.ts, delivery.ts, scheduler.ts
│   │   │   └── analytics.ts, feedback.ts, trends.ts
│   │   └── utils/
│   │       ├── axios-instance.ts    # Axios with auth interceptor
│   │       └── type-transformers.ts # Frontend/backend type mapping
│   │
│   └── types/                       # TypeScript definitions
│       ├── api.ts                   # APIResponse<T> wrapper
│       ├── content.ts               # ContentItem interface
│       ├── newsletter.ts            # Newsletter interface
│       ├── workspace.ts             # Workspace, WorkspaceConfig
│       └── ... (all domain types)
│
├── public/                          # Static assets
├── tailwind.config.js               # Tailwind customization
├── next.config.js                   # Next.js config
└── tsconfig.json                    # TypeScript config
```

### Configuration Files
```
Root Directory:
├── .env                             # Backend environment (DO NOT COMMIT)
├── .env.example                     # Backend env template
├── frontend-nextjs/.env.local       # Frontend environment (DO NOT COMMIT)
├── requirements.txt                 # Python dependencies
├── package.json (frontend)          # Node dependencies
├── config.example.json              # Scraper config template
└── CLAUDE.md (THIS FILE)            # Primary context for Claude
```

---

## Data Flow

### 1. Content Scraping Flow
```
User triggers scrape (POST /api/v1/content/scrape)
  ↓
ContentService.scrape_content(workspace_id)
  ↓
Load workspace config → sources array
  ↓
For each enabled source:
  ├─ Reddit: RedditScraper.scrape() → fetch JSON from reddit.com/r/{sub}.json
  ├─ RSS: RSSFeedScraper.scrape() → feedparser.parse(feed_url)
  ├─ YouTube: YouTubeScraper.scrape() → Google API v3 search
  ├─ X: XScraper.scrape() → X API v2 tweets/search
  └─ Blog: BlogScraper.scrape() → BeautifulSoup CSS selectors
  ↓
Extract: title, content, author, URL, engagement metrics
  ↓
Insert into content_items table (workspace_id, source, source_url, ...)
  ↓
Return: ContentItem[] with scraped data
```

### 2. Newsletter Generation Flow
```
User clicks "Generate Newsletter" (POST /api/v1/newsletters)
  ↓
NewsletterService.generate_newsletter(workspace_id, params)
  ↓
Fetch recent content items (last 7 days, filtered by workspace_id)
  ↓
Apply feedback-based ranking (boost preferred sources +20%, penalize disliked -30%)
  ↓
Select top N items (default: 10, configurable in workspace config)
  ↓
Load style profile (if trained) → tone, vocabulary, sentence structure
  ↓
Build AI prompt:
  ├─ System: "You are a newsletter writer with [tone] style"
  ├─ User: "Create newsletter from these items: [content summaries]"
  └─ Parameters: temperature, max_tokens, model (gpt-4-turbo / claude-3.5-sonnet)
  ↓
Call AI API (OpenAI or OpenRouter based on config)
  ↓
Parse response → HTML content + plain text version
  ↓
Insert into newsletters table (workspace_id, content_html, status='draft', ...)
  ↓
Link content items → newsletter_content_items M:M table
  ↓
Return: Newsletter object with generated content
```

### 3. Email Delivery Flow
```
User clicks "Send Newsletter" (POST /api/v1/delivery/send)
  ↓
DeliveryService.send_newsletter(newsletter_id, subscriber_ids)
  ↓
Fetch newsletter HTML from newsletters table
  ↓
Inject tracking pixel: <img src="/track/pixel/{hmac_token}.png" />
  ↓
Replace all links with tracking redirects: /track/click/{hmac_token}
  ↓
Fetch subscribers list (status='subscribed')
  ↓
For each subscriber:
  ├─ If method='smtp': smtplib.sendmail()
  └─ If method='sendgrid': SendGrid API send()
  ↓
Record in delivery_logs (newsletter_id, subscriber_email, status='sent')
  ↓
Record analytics event (event_type='sent') → email_analytics_events
  ↓
Update newsletter status → 'sent', sent_at = NOW()
  ↓
Return: Delivery summary (sent_count, failed_count)
```

### 4. Scheduled Job Flow
```
User creates job (POST /api/v1/scheduler/jobs) with cron schedule
  ↓
Insert into scheduler_jobs (workspace_id, schedule='0 9 * * *', is_enabled=true)
  ↓
Background worker (backend/worker.py) polls every 5 minutes
  ↓
Load all enabled jobs from scheduler_jobs table
  ↓
For each job with next_run_at <= NOW():
  ├─ Execute job function:
  │   ├─ Step 1: ContentService.scrape_content(workspace_id)
  │   ├─ Step 2: NewsletterService.generate_newsletter(workspace_id)
  │   └─ Step 3: DeliveryService.send_newsletter(newsletter_id)
  ├─ Record in scheduler_execution_logs (status='success'/'failed', result, error_message)
  ├─ Update last_run_at = NOW()
  └─ Calculate next_run_at from cron expression
  ↓
APScheduler reschedules job for next_run_at
```

### 5. Analytics Tracking Flow
```
Subscriber opens email
  ↓
Email client loads tracking pixel: GET /track/pixel/{hmac_token}.png
  ↓
Backend verifies HMAC token → extract newsletter_id, subscriber_email
  ↓
Record event: INSERT INTO email_analytics_events (event_type='opened', ...)
  ↓
Return 1x1 transparent PNG
  ↓
Subscriber clicks link
  ↓
Browser requests: GET /track/click/{hmac_token}
  ↓
Backend verifies HMAC → extract newsletter_id, subscriber_email, content_item_id, target_url
  ↓
Record event: INSERT INTO email_analytics_events (event_type='clicked', ...)
  ↓
Redirect to target_url (302 redirect)
  ↓
Background aggregation (every hour):
  ├─ Calculate metrics: open_rate, click_rate, unique_opens, unique_clicks
  └─ Update newsletter_analytics_summary table
```

---

## Frontend-Backend Field Mappings (Quick Reference)

### ⚠️ CRITICAL: Known Mismatches

| Domain | Frontend Property | Backend Field | Notes |
|--------|------------------|---------------|-------|
| **Content** | `sourceType` | `source` | ⚠️ Frontend should use `source` |
| **Newsletter** | `htmlContent` | `content_html` | ⚠️ Fixed in latest frontend |
| **Newsletter** | `textContent` | `content_text` | ⚠️ Fixed in latest frontend |
| **Content** | `commentsCount` | `comments_count` | Snake case in DB |
| **Content** | `sharesCount` | `shares_count` | Snake case in DB |
| **Content** | `viewsCount` | `views_count` | Snake case in DB |
| **Content** | `imageUrl` | `image_url` | Snake case in DB |
| **Content** | `videoUrl` | `video_url` | Snake case in DB |

### Content Item Mapping
```typescript
// Frontend: ContentItem interface
interface ContentItem {
  id: string                    // backend: id (UUID)
  workspaceId: string           // backend: workspace_id
  title: string                 // backend: title
  source: 'reddit' | 'rss' | 'youtube' | 'x' | 'blog'  // backend: source (enum)
  sourceUrl: string             // backend: source_url
  content: string               // backend: content
  summary: string | null        // backend: summary
  author: string | null         // backend: author
  score: number | null          // backend: score
  commentsCount: number | null  // backend: comments_count ⚠️
  imageUrl: string | null       // backend: image_url ⚠️
  tags: string[]                // backend: tags (PostgreSQL array)
  createdAt: string             // backend: created_at (ISO 8601)
  scrapedAt: string             // backend: scraped_at
}
```

### Newsletter Mapping
```typescript
// Frontend: Newsletter interface
interface Newsletter {
  id: string                    // backend: id
  workspaceId: string           // backend: workspace_id
  title: string                 // backend: title
  contentHtml: string           // backend: content_html ⚠️
  contentText: string           // backend: content_text ⚠️
  modelUsed: string             // backend: model_used
  temperature: number           // backend: temperature
  tone: string                  // backend: tone
  status: 'draft' | 'sent' | 'scheduled'  // backend: status
  generatedAt: string           // backend: generated_at
  sentAt: string | null         // backend: sent_at
  contentItemsCount: number     // backend: content_items_count
}
```

**For complete mappings, see:** `docs/_PRIORITY_1_CONTEXT/FRONTEND_BACKEND_MAPPING.md`

---

## Common Errors (Quick Reference)

### Backend Errors

#### 1. 500 - Newsletter Generation Failed
**Symptoms**: `POST /api/v1/newsletters` returns 500, generic error message

**Causes**:
1. No content items available (empty content_items for workspace)
2. Missing AI API keys (`OPENAI_API_KEY` or `OPENROUTER_API_KEY` not set)
3. Malformed workspace config (invalid JSON in workspace_configs.config)
4. AI API rate limit exceeded

**Debug**:
```bash
# Check content exists
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/v1/content/workspaces/{id}?limit=1"

# Check workspace config
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/v1/workspaces/{id}/config"

# Check backend logs
tail -f backend/logs/app.log
```

**Fix**:
- Scrape content first: `POST /api/v1/content/scrape`
- Verify `.env` has `OPENAI_API_KEY` or `OPENROUTER_API_KEY`
- Validate workspace config JSON structure

#### 2. 401 - Unauthorized
**Symptoms**: All API calls return `{"detail": "Not authenticated"}`

**Causes**:
1. Token expired (30-minute lifetime)
2. Missing `Authorization: Bearer {token}` header
3. Invalid token format (corrupted in localStorage)
4. Token signed with wrong `SECRET_KEY`

**Fix**:
```typescript
// Frontend: Check token in localStorage
const token = localStorage.getItem('auth-token')
console.log('Token:', token?.substring(0, 20) + '...')

// Refresh token
const response = await axios.post('/api/v1/auth/refresh', { token })

// Or re-login
await axios.post('/api/v1/auth/login', { email, password })
```

#### 3. 403 - Workspace Access Denied
**Symptoms**: Can't access workspace data despite valid token

**Cause**: User not in `user_workspaces` table for the requested workspace

**Debug**:
```sql
-- Check workspace membership
SELECT * FROM user_workspaces
WHERE user_id = '{user_id}' AND workspace_id = '{workspace_id}';
```

**Fix**:
- Add user to workspace: `POST /api/v1/workspaces/{id}/members`
- Use workspace where user is member

#### 4. RLS Policy Blocking Query
**Symptoms**: Query returns empty despite data existing in database

**Cause**: Row-Level Security policy blocking access (using wrong Supabase client)

**Fix**:
```python
# In services: Use service client for initial access verification
service_db = SupabaseManager(use_service_role=True)
workspace = service_db.client.table('workspaces').select('*').eq('id', workspace_id).single().execute()

# Then use user client for data access (RLS enforced)
user_db = SupabaseManager(use_service_role=False, user_token=user_jwt)
content = user_db.client.table('content_items').select('*').eq('workspace_id', workspace_id).execute()
```

### Frontend Errors

#### 5. TypeError: Cannot read property 'content_html' of undefined
**Symptoms**: Frontend crashes when displaying newsletter

**Cause**: Newsletter object structure mismatch (expecting old field names)

**Fix**:
```typescript
// OLD (incorrect)
const html = newsletter.html_content

// NEW (correct)
const html = newsletter.content_html
```

#### 6. Hydration Error (Next.js)
**Symptoms**: "Text content does not match server-rendered HTML"

**Cause**: Client-side code rendering differently than server

**Fix**:
```typescript
// Use client-only rendering for dynamic content
'use client'
import { useEffect, useState } from 'react'

const [mounted, setMounted] = useState(false)
useEffect(() => setMounted(true), [])

if (!mounted) return null
return <div>{dynamicContent}</div>
```

#### 7. CORS Error
**Symptoms**: "Blocked by CORS policy" in browser console

**Cause**: Backend CORS middleware not allowing frontend origin

**Fix**: Check `backend/middleware/cors.py`:
```python
origins = [
    "http://localhost:3000",  # Local dev
    "http://localhost:8000",  # Backend serving frontend
    os.getenv("FRONTEND_URL", ""),  # Production
]
```

**For complete error reference, see:** `docs/_PRIORITY_1_CONTEXT/COMMON_ERRORS.md`

---

## Critical Type Definitions (Quick Reference)

### API Response Wrapper (All Endpoints)
```typescript
interface APIResponse<T = any> {
  success: boolean
  data?: T
  error?: string
  message?: string
}

// Usage
const response: APIResponse<Newsletter> = await createNewsletter(...)
if (response.success) {
  console.log(response.data.title)
} else {
  console.error(response.error)
}
```

### ContentItem (Exact Backend Match)
```typescript
interface ContentItem {
  id: string
  workspace_id: string
  title: string
  source: 'reddit' | 'rss' | 'youtube' | 'x' | 'blog'  // ⚠️ Not sourceType
  source_url: string
  content: string
  summary: string | null
  author: string | null
  author_url: string | null
  score: number | null
  comments_count: number | null  // ⚠️ Snake case
  shares_count: number | null
  views_count: number | null
  image_url: string | null       // ⚠️ Snake case
  video_url: string | null
  external_url: string | null
  tags: string[]                 // PostgreSQL array type
  category: string | null
  created_at: string             // ISO 8601 timestamp
  scraped_at: string
  metadata: Record<string, any>  // JSONB field
}
```

### Newsletter (Exact Backend Match)
```typescript
interface Newsletter {
  id: string
  workspace_id: string
  title: string
  content_html: string           // ⚠️ Not htmlContent
  content_text: string           // ⚠️ Not textContent
  model_used: string             // "gpt-4-turbo-preview" or "anthropic/claude-3.5-sonnet"
  temperature: number            // 0.0-1.0
  tone: string                   // "professional" | "casual" | "technical" | "friendly"
  language: string               // "en", "es", etc.
  status: 'draft' | 'sent' | 'scheduled'
  generated_at: string
  sent_at: string | null
  content_items_count: number
  metadata: Record<string, any>
  created_at: string
  updated_at: string
}
```

### WorkspaceConfig (JSONB Structure)
```typescript
interface WorkspaceConfig {
  sources: SourceConfig[]
  generation: GenerationConfig
  delivery: DeliveryConfig
}

interface SourceConfig {
  type: 'reddit' | 'rss' | 'youtube' | 'x' | 'blog'
  enabled: boolean
  config: {
    // Reddit-specific
    subreddits?: string[]          // e.g., ["MachineLearning", "artificial"]
    sort?: 'hot' | 'new' | 'top'
    limit?: number                 // default: 25

    // RSS-specific
    feed_urls?: string[]           // e.g., ["https://example.com/feed"]

    // YouTube-specific
    channel_ids?: string[]
    query?: string

    // X/Twitter-specific
    usernames?: string[]
    search_query?: string

    // Blog-specific
    url?: string
    selectors?: {
      article: string              // CSS selector for article container
      title: string
      content: string
      author?: string
      date?: string
    }
  }
}

interface GenerationConfig {
  model: 'openai' | 'openrouter'
  openai_model?: string            // e.g., "gpt-4-turbo-preview"
  openrouter_model?: string        // e.g., "anthropic/claude-3.5-sonnet"
  temperature: number              // 0.0-1.0, default: 0.7
  tone: string                     // "professional" | "casual" | "technical" | "friendly"
  language: string                 // "en", default
  max_items: number                // default: 10
}

interface DeliveryConfig {
  method: 'smtp' | 'sendgrid'
  from_name: string
  reply_to?: string
}
```

**For complete type definitions, see:** `docs/_PRIORITY_1_CONTEXT/TYPE_DEFINITIONS.md`

---

## Database Schema (Quick Reference)

### Core Tables (17 total)

#### 1. auth.users (Supabase managed)
```sql
id UUID PRIMARY KEY
email TEXT UNIQUE
-- password_hash managed by Supabase Auth
created_at TIMESTAMPTZ
updated_at TIMESTAMPTZ
```

#### 2. public.users (Custom profile)
```sql
id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE
email TEXT UNIQUE
username TEXT NOT NULL
created_at TIMESTAMPTZ
updated_at TIMESTAMPTZ
```

#### 3. workspaces
```sql
id UUID PRIMARY KEY
name TEXT NOT NULL UNIQUE
description TEXT
owner_id UUID REFERENCES public.users(id)
created_at TIMESTAMPTZ
updated_at TIMESTAMPTZ
```

#### 4. user_workspaces (Team membership)
```sql
id UUID PRIMARY KEY
workspace_id UUID REFERENCES workspaces(id)
user_id UUID REFERENCES public.users(id)
role TEXT  -- 'owner' | 'editor' | 'viewer'
joined_at TIMESTAMPTZ
```

#### 5. workspace_configs
```sql
id UUID PRIMARY KEY
workspace_id UUID REFERENCES workspaces(id)
config JSONB  -- WorkspaceConfig structure (see above)
version INTEGER
created_at TIMESTAMPTZ
updated_at TIMESTAMPTZ
```

#### 6. content_items
```sql
id UUID PRIMARY KEY
workspace_id UUID REFERENCES workspaces(id)
title TEXT NOT NULL
source TEXT  -- 'reddit' | 'rss' | 'youtube' | 'x' | 'blog'
source_url TEXT NOT NULL
content TEXT
summary TEXT
author TEXT
author_url TEXT
score INTEGER
comments_count INTEGER
shares_count INTEGER
views_count INTEGER
image_url TEXT
video_url TEXT
external_url TEXT
tags TEXT[]  -- PostgreSQL array type
category TEXT
created_at TIMESTAMPTZ
scraped_at TIMESTAMPTZ
metadata JSONB

-- Unique constraint (migration 010)
UNIQUE(workspace_id, source_url)
```

#### 7. newsletters
```sql
id UUID PRIMARY KEY
workspace_id UUID REFERENCES workspaces(id)
title TEXT NOT NULL
content_html TEXT
content_text TEXT
model_used TEXT
temperature FLOAT
tone TEXT
language TEXT
status TEXT  -- 'draft' | 'sent' | 'scheduled'
generated_at TIMESTAMPTZ
sent_at TIMESTAMPTZ
content_items_count INTEGER
metadata JSONB
created_at TIMESTAMPTZ
updated_at TIMESTAMPTZ
```

#### 8. newsletter_content_items (M:M relationship)
```sql
id UUID PRIMARY KEY
newsletter_id UUID REFERENCES newsletters(id)
content_item_id UUID REFERENCES content_items(id)
```

#### 9. subscribers
```sql
id UUID PRIMARY KEY
workspace_id UUID REFERENCES workspaces(id)
email TEXT NOT NULL
status TEXT  -- 'subscribed' | 'unsubscribed' | 'bounced'
subscribed_at TIMESTAMPTZ
unsubscribed_at TIMESTAMPTZ
```

#### 10. scheduler_jobs
```sql
id UUID PRIMARY KEY
workspace_id UUID REFERENCES workspaces(id)
schedule TEXT  -- Cron expression (e.g., "0 9 * * *")
is_enabled BOOLEAN
status TEXT  -- 'active' | 'paused' | 'completed'
last_run_at TIMESTAMPTZ
next_run_at TIMESTAMPTZ
created_at TIMESTAMPTZ
```

#### 11. scheduler_execution_logs
```sql
id UUID PRIMARY KEY
job_id UUID REFERENCES scheduler_jobs(id)
status TEXT  -- 'success' | 'failed'
result JSONB
error_message TEXT
started_at TIMESTAMPTZ
completed_at TIMESTAMPTZ
```

#### 12. email_analytics_events (Tracking)
```sql
id UUID PRIMARY KEY
newsletter_id UUID REFERENCES newsletters(id)
content_item_id UUID REFERENCES content_items(id)  -- For click tracking
subscriber_email TEXT
event_type TEXT  -- 'sent' | 'delivered' | 'opened' | 'clicked' | 'bounced' | 'spam_reported'
user_agent TEXT
ip_address TEXT  -- Anonymized
device_type TEXT
email_client TEXT
timestamp TIMESTAMPTZ
```

**For complete schema with all 17 tables, see:** `docs/_PRIORITY_2_REFERENCE/DATABASE_SCHEMA.md`

---

## Authentication & Security

### Authentication Flow
```
1. User Registration (POST /api/v1/auth/signup)
   └─ Supabase Auth creates auth.users entry
   └─ Backend creates public.users profile
   └─ Backend generates JWT token (30min expiry)
   └─ Frontend stores token in localStorage

2. User Login (POST /api/v1/auth/login)
   └─ Authenticate with Supabase Auth
   └─ Generate JWT token
   └─ Frontend stores token in localStorage

3. Authenticated Request
   └─ Frontend adds "Authorization: Bearer {token}" header
   └─ Backend middleware verifies token (get_current_user)
   └─ Returns user_id for authorization checks
```

### JWT Token Structure
```python
# Token generation (backend/services/auth_service.py)
from jose import jwt
from datetime import datetime, timedelta

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=30)  # 30min expiry
    to_encode.update({"exp": expire, "sub": user_id})
    return jwt.encode(to_encode, settings.secret_key, algorithm="HS256")

# Token verification (backend/middleware/auth.py)
async def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
    user_id = payload.get("sub")
    return user_id
```

### Multi-Tenant Authorization
```python
# Check workspace access (in services)
def verify_workspace_access(user_id: str, workspace_id: str) -> bool:
    # Use service client to bypass RLS for access check
    service_db = SupabaseManager(use_service_role=True)

    result = service_db.client.table('user_workspaces') \
        .select('role') \
        .eq('user_id', user_id) \
        .eq('workspace_id', workspace_id) \
        .execute()

    return len(result.data) > 0

# Role-based permissions
roles = {
    'owner': ['read', 'write', 'delete', 'manage_team'],
    'editor': ['read', 'write'],
    'viewer': ['read']
}
```

### Security Best Practices
1. **Password Hashing**: Bcrypt via passlib (handled by Supabase Auth)
2. **Token Expiry**: 30 minutes (configurable in `backend/settings.py`)
3. **HTTPS Only**: In production (enforced by Railway)
4. **CORS**: Whitelist specific origins (see `backend/middleware/cors.py`)
5. **Rate Limiting**: 60 requests/minute per IP (configurable per endpoint)
6. **HMAC Tracking**: Tracking URLs use HMAC tokens to prevent tampering
7. **Row-Level Security**: Database policies enforce workspace isolation

---

## Environment Variables

### Backend (.env)
```bash
# Required - Database
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...  # Anon key
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...  # Service role key

# Required - Authentication
SECRET_KEY=your-secret-key-here-change-in-production  # For JWT signing

# Required - AI (at least one)
OPENAI_API_KEY=sk-proj-...
# OR
OPENROUTER_API_KEY=sk-or-v1-...

# Required - Email (choose one)
# Option 1: SMTP
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password  # NOT your Google password!
FROM_EMAIL=your-email@gmail.com

# Option 2: SendGrid
SENDGRID_API_KEY=SG.abcd1234...

# Optional - Content Sources
YOUTUBE_API_KEY=AIzaSy...  # For YouTube scraper
X_API_KEY=abcd1234...  # For X/Twitter scraper
X_API_SECRET=secret123...
X_BEARER_TOKEN=Bearer ...

# Optional - Deployment
ENVIRONMENT=production  # development | production
DEBUG=false  # true | false
RAILWAY_PUBLIC_DOMAIN=your-app.railway.app  # Auto-detected on Railway
```

### Frontend (.env.local)
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000  # Backend URL
# In production: https://your-backend.railway.app
```

---

## Known Issues & Technical Debt

### High Priority

1. **Synchronous Scraping** (Performance bottleneck)
   - **Issue**: Content scraping is synchronous, blocks API response
   - **Impact**: Large scraping jobs (100+ items) timeout
   - **Current Workaround**: Limit items per source in config
   - **TODO**: Implement async task queue (Celery + Redis)
   - **Files**: `backend/services/content_service.py:45-120`

2. **No Caching Layer** (Performance)
   - **Issue**: No Redis/Memcached for frequently accessed data
   - **Impact**: Repeated DB queries for same workspace configs, content
   - **TODO**: Add Redis caching for workspace configs, popular content
   - **Files**: All services

3. **Type Mismatch Cleanup** (Frontend/Backend consistency)
   - **Issue**: Some legacy code still uses old field names (`html_content` vs `content_html`)
   - **Impact**: Intermittent TypeScript errors, runtime crashes
   - **TODO**: Global find-replace and type validation
   - **Files**: `frontend-nextjs/src/types/*.ts`, various components

### Medium Priority

4. **Rate Limiting Configuration** (Security)
   - **Issue**: Default 60 req/min may be too restrictive for some endpoints, too lenient for others
   - **TODO**: Fine-tune per endpoint (e.g., auth: 5/min, content read: 100/min)
   - **Files**: `backend/api/v1/*.py` (add `@limiter.limit()` decorators)

5. **Database Indexing** (Performance)
   - **Issue**: Missing indexes on frequently queried foreign keys
   - **TODO**: Add indexes on `workspace_id`, `newsletter_id`, `content_item_id`
   - **Files**: New migration file `backend/migrations/011_add_performance_indexes.sql`

6. **Error Message Specificity** (Developer Experience)
   - **Issue**: Many errors return generic 500 with "Internal Server Error"
   - **TODO**: Custom exception classes with specific HTTP status codes
   - **Files**: `backend/utils/error_handling.py`, all services

### Low Priority

7. **Test Coverage** (Quality Assurance)
   - **Issue**: Limited unit tests, mainly integration tests
   - **Current**: ~40% coverage
   - **TODO**: Increase to 80%+ with unit tests for services
   - **Files**: `backend/tests/unit/` (expand)

8. **API Documentation** (Developer Experience)
   - **Issue**: Swagger docs exist but not always up-to-date
   - **TODO**: Automate OpenAPI spec generation from Pydantic models
   - **Files**: `backend/main.py` (FastAPI auto-docs)

9. **Configuration Consolidation** (Maintainability)
   - **Issue**: Settings split between `backend/settings.py`, `backend/config/constants.py`, `.env`
   - **TODO**: Consolidate into single Pydantic settings class
   - **Files**: Create `backend/config/settings.py`, deprecate `constants.py`

### Recently Fixed

✅ **Empty Content Newsletter Error** (Fixed 2025-01-20)
- **Was**: 500 error when generating newsletter with no content
- **Now**: Returns 400 with clear message "No content items available"
- **File**: `backend/services/newsletter_service.py:78`

✅ **BaseService Pattern** (Fixed 2025-01-20)
- **Was**: Inconsistent service initialization, duplicated DB connection logic
- **Now**: All services extend `BaseService`, lazy-load DB, standardized logging
- **File**: `backend/services/base_service.py`

✅ **Rate Limiting** (Added 2025-01-19)
- **Was**: No rate limiting on resource-intensive endpoints
- **Now**: 60 req/min default, configurable per endpoint
- **File**: `backend/middleware/rate_limiter.py`

---

## Recent Changes (Auto-Updated by Git Hook)

<!-- Keep last 10 significant changes -->
- 2025-01-22: Completed persistent context system with Priority 2 reference docs (FRONTEND_ARCHITECTURE.md, SETTINGS_COMPONENTS.md)
- 2025-01-20: Updated documentation to accurately reflect Settings page architecture (unified hub with sidebar, 10 sections)
- 2025-01-20: Created comprehensive CLAUDE.md context file with priority system and .claude/instructions.md
- 2025-01-20: Created docs/_PRIORITY_1_CONTEXT/ structure (FRONTEND_BACKEND_MAPPING, COMMON_ERRORS, TYPE_DEFINITIONS)
- 2025-01-20: Added error handling decorators to services (@handle_service_errors)
- 2025-01-20: Standardized BaseService pattern across all services
- 2025-01-20: Fixed newsletter 500 error (empty content handling)
- 2025-01-20: Added .claudeignore and git hooks for documentation maintenance
- 2025-01-19: Added rate limiting to resource-intensive endpoints
- 2025-01-19: Added type validation to service responses

---

## Architecture Decisions

### Why Supabase?
- **Multi-tenancy**: Row-Level Security (RLS) policies enforce workspace isolation
- **Built-in Auth**: Reduces custom auth implementation
- **REST API**: PostgREST provides instant REST API for all tables
- **Realtime**: WebSocket support for future real-time features
- **Hosted**: Managed PostgreSQL with backups and scaling

### Why Service Layer Pattern?
- **Testability**: Services can be unit tested independently
- **Reusability**: Business logic reused across API endpoints and background jobs
- **Separation of Concerns**: API routes handle HTTP, services handle business logic
- **Maintainability**: Changes to business logic don't require API route changes

### Why FastAPI over Flask/Django?
- **Async Support**: Native asyncio for concurrent operations (scraping, API calls)
- **Type Safety**: Pydantic models enforce request/response contracts
- **Auto Documentation**: OpenAPI/Swagger docs generated automatically
- **Performance**: Faster than Flask/Django for I/O-bound operations
- **Modern**: Built on ASGI (Starlette) with modern Python features

### Why Next.js 14 (App Router)?
- **Server Components**: Reduce client-side JavaScript bundle
- **File-based Routing**: Intuitive page structure
- **Built-in Optimization**: Image optimization, font optimization, code splitting
- **SEO**: Server-side rendering for better SEO
- **TypeScript**: First-class TypeScript support

### Why Zustand over Redux?
- **Simplicity**: Less boilerplate than Redux
- **TypeScript**: Better TypeScript inference
- **Performance**: Selective re-rendering without Context API overhead
- **Persistence**: Easy localStorage persistence with middleware
- **Size**: Smaller bundle size (1KB vs 10KB for Redux)

### Why APScheduler?
- **Python-Native**: No external dependencies (Redis, RabbitMQ)
- **Async Support**: Works with asyncio for concurrent job execution
- **Cron Expressions**: Familiar cron syntax for scheduling
- **Persistence**: Jobs stored in database, survive restarts
- **Simple**: Easy to integrate, no separate worker process needed (though we use one)

### Why Monorepo?
- **Shared Types**: Frontend can reference backend types (future)
- **Atomic Changes**: API changes and frontend updates in same commit
- **Simplified Deployment**: Single repository to deploy
- **Developer Experience**: One clone, one setup

---

## Testing Commands

### Backend
```bash
# All tests
pytest

# Unit tests only
pytest backend/tests/unit/

# Integration tests only
pytest backend/tests/integration/

# Specific test file
pytest backend/tests/integration/test_newsletters_api.py

# With coverage
pytest --cov=backend --cov-report=html

# Verbose output
pytest -v

# Stop on first failure
pytest -x

# Run tests matching pattern
pytest -k "newsletter"
```

### Frontend
```bash
# E2E tests (Playwright)
npm run test:e2e

# Interactive UI mode
npm run test:e2e:ui

# Headed mode (browser visible)
npm run test:e2e:headed

# Debug mode
npm run test:e2e:debug

# Generate report
npm run test:e2e:report

# TypeScript type checking
npx tsc --noEmit
```

---

## Deployment

### Current Platform: Railway

**Backend**:
- Auto-deployed from `main` branch
- Environment variables set in Railway dashboard
- URL: `https://{railway-domain}/`
- Health check: `GET /health`

**Frontend**:
- Static build served by backend (Next.js export)
- Build command: `npm run build`
- Start command: `.venv/Scripts/python.exe -m uvicorn backend.main:app --host 0.0.0.0 --port ${PORT}`

**Database**:
- Supabase hosted PostgreSQL
- Migrations applied manually via Supabase dashboard SQL editor

### Deployment Checklist
1. ✅ Set all required environment variables in Railway
2. ✅ Apply database migrations (manually via Supabase)
3. ✅ Test `/health` endpoint
4. ✅ Test login flow
5. ✅ Test newsletter generation with real API keys
6. ✅ Test email delivery with real SMTP/SendGrid credentials
7. ✅ Verify background worker is running (check scheduler logs)
8. ✅ Set up monitoring (Railway logs, Supabase logs)

---

## When to Read Companion Documentation

This file (CLAUDE.md) contains **quick reference** information. For deep dives:

| **Need** | **Read** |
|----------|----------|
| Complete field mappings for all models | `docs/_PRIORITY_1_CONTEXT/FRONTEND_BACKEND_MAPPING.md` |
| Full error catalog with debug steps | `docs/_PRIORITY_1_CONTEXT/COMMON_ERRORS.md` |
| All TypeScript interfaces (copy-paste ready) | `docs/_PRIORITY_1_CONTEXT/TYPE_DEFINITIONS.md` |
| Complete API endpoint reference | `docs/_PRIORITY_2_REFERENCE/API_REFERENCE.md` |
| Full database schema with all 17 tables | `docs/_PRIORITY_2_REFERENCE/DATABASE_SCHEMA.md` |
| Historical sprint documentation | `docs/_PRIORITY_3_HISTORICAL/SPRINT_*.md` |

---

## Token Budget Management

**Target**: Use max 20k tokens (10% of 200k budget) for context loading

**Priority Allocation**:
1. **This file (CLAUDE.md)**: ~15k tokens (primary context)
2. **Task-specific context files**: ~5k tokens (only when needed)
3. **Code files**: ~50k tokens (selective reading based on task)
4. **Reserve**: ~125k tokens (responses, tool outputs, exploration)

**Reading Strategy**:
1. ✅ Always read CLAUDE.md first (you're here!)
2. ✅ Check [Navigation Guide](#-start-here---navigation-guide) for task-specific files
3. ✅ Use Grep/Glob to locate specific code before reading full files
4. ✅ Read only relevant services/components, not entire codebase
5. ❌ Don't read test files unless debugging tests
6. ❌ Don't read historical docs unless explicitly asked
7. ❌ Don't read config files unless debugging configuration

---

## Anti-Patterns (DON'T DO THIS)

❌ **Reading all test files to understand code**
→ ✅ Read service/component files directly, tests are supplementary

❌ **Reading all documentation files at once**
→ ✅ Use this file as index, read specific docs only when needed

❌ **Searching entire codebase without checking context files first**
→ ✅ Check CLAUDE.md, use Grep with specific file patterns

❌ **Re-reading code files every chat session**
→ ✅ Trust information in this file, read code only for verification/updates

❌ **Using generic error messages**
→ ✅ Reference [Common Errors](#common-errors-quick-reference) for specific solutions

❌ **Guessing field names**
→ ✅ Check [Frontend-Backend Mappings](#frontend-backend-field-mappings-quick-reference)

---

## Contributing to This File

### Auto-Update (Git Hook)
This file is automatically updated via `.git/hooks/post-commit`:
- New commits are added to [Recent Changes](#recent-changes-auto-updated-by-git-hook)
- Last 10 entries are kept

### Manual Updates
When making significant changes:

1. **Architecture changes** → Update [Architecture Overview](#architecture-overview)
2. **New API endpoints** → Update [Critical File Locations](#critical-file-locations)
3. **Database schema changes** → Update [Database Schema](#database-schema-quick-reference)
4. **Fixed bugs** → Add to [Recently Fixed](#recently-fixed), remove from [Known Issues](#known-issues--technical-debt)
5. **New errors discovered** → Add to [Common Errors](#common-errors-quick-reference)
6. **Type changes** → Update [Critical Type Definitions](#critical-type-definitions-quick-reference)

### Keep It Current
- ⏱️ Review quarterly (or after major changes)
- 🎯 Keep quick reference sections under 50 lines each
- 📝 Move detailed info to `docs/_PRIORITY_*` files
- 🔄 Update "Last Updated" date at top

---

## Summary: What You (Claude) Should Know

After reading this file, you should be able to:

✅ **Navigate the codebase** - Know where to find services, API routes, components
✅ **Debug common errors** - Recognize symptoms and apply fixes
✅ **Understand data flow** - Trace requests from frontend → backend → database
✅ **Work with types** - Use correct field names and structures
✅ **Make architecture decisions** - Understand why current patterns were chosen
✅ **Add new features** - Know which services/files to modify
✅ **Fix integration issues** - Resolve frontend-backend mismatches
✅ **Deploy changes** - Understand deployment process and checklist

**Questions?** Ask the user for clarification. Prefer using information in this file over re-reading code.

---

**END OF CLAUDE.md**