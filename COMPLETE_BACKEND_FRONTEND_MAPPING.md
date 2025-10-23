# 🗺️ Complete Backend-Frontend Mapping Guide

**For Complete Beginners - Every Feature Mapped**

This document shows you EXACTLY how every backend feature connects to the frontend, what files are involved, and how data flows through the system.

---

## 📋 Table of Contents

1. [How to Read This Document](#how-to-read-this-document)
2. [System Overview](#system-overview)
3. [Feature Mapping (12 Modules)](#feature-mapping)
   - [1. Authentication](#1-authentication)
   - [2. Workspaces](#2-workspaces)
   - [3. Content Scraping](#3-content-scraping)
   - [4. Newsletters](#4-newsletters)
   - [5. Subscribers](#5-subscribers)
   - [6. Delivery (Email Sending)](#6-delivery-email-sending)
   - [7. Scheduler (Automation)](#7-scheduler-automation)
   - [8. Analytics](#8-analytics)
   - [9. Style Training](#9-style-training)
   - [10. Trends Detection](#10-trends-detection)
   - [11. Feedback & Learning](#11-feedback--learning)
   - [12. Tracking (Pixel/Click)](#12-tracking-pixelclick)
4. [Unused/Missing Files](#unused-files)
5. [File Status Report](#file-status-report)

---

## 🎓 How to Read This Document

**Structure for Each Feature:**

```
Feature Name
├── What It Does (Plain English)
├── Backend Files
│   ├── API Endpoint File
│   ├── Service File (Business Logic)
│   └── Database Table(s)
├── Frontend Files
│   ├── Page(s) That Use It
│   ├── API Integration File
│   └── Components That Display Data
└── Data Flow Diagram
```

**Color Legend:**
- ✅ **Working** - File exists and is functional
- ⚠️ **Partial** - File exists but has issues or is incomplete
- ❌ **Broken** - File missing or has critical errors
- 🔵 **Not Used** - File exists but not imported/used anywhere

---

## 🏗️ System Overview

### Architecture Pattern

```
User clicks button
     ↓
Frontend Page (src/app/**/page.tsx)
     ↓
Calls API Function (src/lib/api/*.ts)
     ↓
HTTP Request to Backend (POST /api/v1/...)
     ↓
Backend API Endpoint (backend/api/v1/*.py)
     ↓
Calls Service Layer (backend/services/*_service.py)
     ↓
Queries Database (Supabase PostgreSQL)
     ↓
Returns Data (JSON response)
     ↓
Frontend Updates UI (React components)
```

### File Structure Overview

**Backend:**
```
backend/
├── main.py                    # Main FastAPI app (routes registration)
├── settings.py               # Environment variables configuration
├── database.py               # Supabase connection manager
├── api/
│   └── v1/                   # API endpoints (12 files)
│       ├── auth.py           # Login, signup, logout
│       ├── workspaces.py     # Workspace CRUD
│       ├── content.py        # Scraping, content list
│       ├── newsletters.py    # Generate, edit, delete
│       ├── subscribers.py    # Subscriber management
│       ├── delivery.py       # Email sending
│       ├── scheduler.py      # Scheduled jobs
│       ├── analytics.py      # Email tracking stats
│       ├── style.py          # Writing style training
│       ├── trends.py         # Trend detection
│       └── feedback.py       # User feedback collection
├── services/                 # Business logic (12 files)
│   ├── auth_service.py
│   ├── workspace_service.py
│   ├── content_service.py
│   ├── newsletter_service.py
│   ├── delivery_service.py
│   ├── scheduler_service.py
│   ├── analytics_service.py
│   └── ... (6 more)
└── models/                   # Request/response schemas
    └── ... (12 files)
```

**Frontend:**
```
frontend-nextjs/src/
├── app/                      # Pages (Next.js App Router)
│   ├── page.tsx             # Landing page (public)
│   ├── login/page.tsx       # Login page
│   ├── register/page.tsx    # Registration page
│   └── app/                 # Protected pages (requires login)
│       ├── page.tsx         # Dashboard (main hub)
│       ├── content/page.tsx # Content browser
│       ├── history/page.tsx # Newsletter history
│       ├── settings/page.tsx # Settings hub
│       ├── subscribers/page.tsx
│       ├── schedule/page.tsx
│       ├── analytics/page.tsx
│       ├── trends/page.tsx
│       ├── feedback/page.tsx
│       └── style/page.tsx
├── lib/
│   ├── api/                 # API integration (12 files)
│   │   ├── auth.ts
│   │   ├── workspaces.ts
│   │   ├── content.ts
│   │   ├── newsletters.ts
│   │   ├── subscribers.ts
│   │   ├── delivery.ts
│   │   ├── scheduler.ts
│   │   ├── analytics.ts
│   │   └── ... (4 more)
│   └── stores/              # State management (Zustand)
│       ├── auth-store.ts    # User authentication state
│       └── workspace-store.ts # Current workspace state
└── components/              # UI components (50+ files)
    ├── dashboard/           # Dashboard-specific
    ├── settings/            # Settings sections
    ├── modals/              # Popup dialogs
    └── ui/                  # Reusable UI primitives
```

---

## 🔍 Feature Mapping

---

## 1. Authentication

### What It Does
Handles user login, registration, and logout. Stores a JWT token in browser localStorage to keep you logged in.

### Backend Files

**API Endpoint:** `backend/api/v1/auth.py` ✅
- `POST /api/v1/auth/signup` - Create new account
- `POST /api/v1/auth/login` - Log in with email/password
- `POST /api/v1/auth/logout` - Log out
- `GET /api/v1/auth/me` - Get current user info
- `POST /api/v1/auth/refresh` - Refresh expired token

**Service:** `backend/services/auth_service.py` ✅
- `signup(email, password, username)` - Creates user in database
- `login(email, password)` - Verifies credentials, generates JWT token
- `create_access_token()` - Creates JWT with 30-minute expiry

**Database Tables:**
- `auth.users` (Supabase managed) - User credentials
- `public.users` (Custom) - User profile (username, email)

### Frontend Files

**Pages:**
- `src/app/login/page.tsx` ✅ - Login form
- `src/app/register/page.tsx` ✅ - Registration form
- `src/app/forgot-password/page.tsx` ✅ - Password reset

**API Integration:** `src/lib/api/auth.ts` ✅
```typescript
authApi.login(email, password)      // Calls POST /api/v1/auth/login
authApi.register(email, password)   // Calls POST /api/v1/auth/signup
authApi.logout()                    // Calls POST /api/v1/auth/logout
authApi.getCurrentUser()            // Calls GET /api/v1/auth/me
authApi.isAuthenticated()           // Checks if token exists in localStorage
```

**State Management:** `src/lib/stores/auth-store.ts` ✅
- Stores: `user`, `token`, `isAuthenticated`
- Functions: `setAuth()`, `clearAuth()`
- Persists to localStorage automatically

**Components Used:**
- `src/components/ui/input.tsx` - Email/password fields
- `src/components/ui/button.tsx` - Submit buttons
- `src/components/ui/card.tsx` - Form container

### Data Flow

```
User enters email/password on login page
     ↓
authApi.login(email, password) called
     ↓
POST request to http://localhost:8000/api/v1/auth/login
     ↓
Backend: auth.py endpoint receives request
     ↓
Calls auth_service.login(email, password)
     ↓
Queries database: SELECT * FROM auth.users WHERE email = ?
     ↓
Verifies password with bcrypt
     ↓
Generates JWT token (expires in 30 minutes)
     ↓
Returns: {success: true, data: {token: "eyJhbG...", user: {...}}}
     ↓
Frontend: auth-store.setAuth(token, user)
     ↓
Token saved to localStorage
     ↓
User redirected to /app (dashboard)
```

**Request Example:**
```json
POST /api/v1/auth/login
{
  "email": "user@example.com",
  "password": "mypassword123"
}
```

**Response Example:**
```json
{
  "success": true,
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "email": "user@example.com",
      "username": "john_doe"
    }
  }
}
```

---

## 2. Workspaces

### What It Does
Manages workspaces (like folders for organizing newsletters). Each workspace has its own content sources, subscribers, and settings.

### Backend Files

**API Endpoint:** `backend/api/v1/workspaces.py` ✅
- `GET /api/v1/workspaces` - List all workspaces user can access
- `POST /api/v1/workspaces` - Create new workspace
- `GET /api/v1/workspaces/{id}` - Get workspace details
- `PUT /api/v1/workspaces/{id}` - Update workspace name/description
- `DELETE /api/v1/workspaces/{id}` - Delete workspace
- `GET /api/v1/workspaces/{id}/config` - Get workspace configuration (sources, settings)
- `PUT /api/v1/workspaces/{id}/config` - Update workspace configuration

**Service:** `backend/services/workspace_service.py` ✅
- `list_workspaces(user_id)` - Get all workspaces for user
- `create_workspace(user_id, name, description)` - Create new workspace
- `get_workspace_config(workspace_id)` - Load configuration JSON
- `update_workspace_config(workspace_id, config)` - Save configuration

**Database Tables:**
- `workspaces` - Workspace metadata (name, description, owner)
- `user_workspaces` - Team membership (who can access which workspace)
- `workspace_configs` - Configuration JSON (sources, generation settings, delivery settings)

### Frontend Files

**Pages:**
- `src/app/app/page.tsx` ✅ - Dashboard (loads workspaces on startup)
- `src/app/app/settings/page.tsx` ✅ - Workspace settings section

**API Integration:** `src/lib/api/workspaces.ts` ✅
```typescript
workspacesApi.list()                        // GET /api/v1/workspaces
workspacesApi.create({name, description})   // POST /api/v1/workspaces
workspacesApi.get(id)                       // GET /api/v1/workspaces/{id}
workspacesApi.update(id, {name})            // PUT /api/v1/workspaces/{id}
workspacesApi.delete(id)                    // DELETE /api/v1/workspaces/{id}
workspacesApi.getConfig(id)                 // GET /api/v1/workspaces/{id}/config
workspacesApi.updateConfig(id, config)      // PUT /api/v1/workspaces/{id}/config
```

**State Management:** `src/lib/stores/workspace-store.ts` ✅
- Stores: `currentWorkspace`, `workspaces`
- Functions: `setCurrentWorkspace()`, `clearWorkspace()`

**Components Used:**
- `src/components/dashboard/workspace-management.tsx` ⚠️ - Workspace switcher
- `src/components/settings/workspace-settings.tsx` ✅ - Workspace settings editor
- `src/components/settings/sources-settings.tsx` ✅ - Configure content sources

### Data Flow

```
Dashboard loads → workspacesApi.list()
     ↓
GET /api/v1/workspaces
     ↓
Backend: workspace_service.list_workspaces(user_id)
     ↓
Queries: SELECT * FROM workspaces
         JOIN user_workspaces ON workspace_id
         WHERE user_id = ?
     ↓
Returns: [{id, name, description, owner_id, created_at}, ...]
     ↓
Frontend: Sets first workspace as currentWorkspace
     ↓
All other API calls use currentWorkspace.id
```

**Workspace Config Structure:**
```json
{
  "sources": [
    {
      "type": "reddit",
      "enabled": true,
      "config": {
        "subreddits": ["MachineLearning", "OpenAI"],
        "sort": "hot",
        "limit": 25
      }
    },
    {
      "type": "rss",
      "enabled": true,
      "config": {
        "feed_urls": ["https://openai.com/news/rss.xml"]
      }
    }
  ],
  "generation": {
    "model": "openai",
    "openai_model": "gpt-4-turbo-preview",
    "temperature": 0.7,
    "tone": "professional",
    "max_items": 10
  },
  "delivery": {
    "method": "smtp",
    "from_name": "My Newsletter",
    "reply_to": "reply@example.com"
  }
}
```

---

## 3. Content Scraping

### What It Does
Fetches articles from Reddit, RSS feeds, YouTube, X/Twitter, and blogs. Stores them in the database for later use in newsletters.

### Backend Files

**API Endpoint:** `backend/api/v1/content.py` ✅
- `POST /api/v1/content/scrape` - Trigger scraping job
- `GET /api/v1/content/workspaces/{workspace_id}` - List scraped content
- `GET /api/v1/content/workspaces/{workspace_id}/stats` - Get content statistics
- `GET /api/v1/content/workspaces/{workspace_id}/sources/{source}` - Get content by source
- `PUT /api/v1/content/{id}` - Update content item
- `DELETE /api/v1/content/{id}` - Delete content item

**Service:** `backend/services/content_service.py` ✅
- `scrape_content(workspace_id, sources)` - Orchestrates scraping
- `list_content(workspace_id, days, limit)` - Get content items
- `get_content_stats(workspace_id)` - Calculate statistics

**Scrapers:** (Called by content_service)
- `backend/scrapers/reddit_scraper.py` ✅
- `backend/scrapers/rss_scraper.py` ✅
- `backend/scrapers/youtube_scraper.py` ⚠️ (Requires API key)
- `backend/scrapers/x_scraper.py` ⚠️ (Requires API key)
- `backend/scrapers/blog_scraper.py` ✅

**Database Tables:**
- `content_items` - Scraped articles (title, content, source, url, author, score, image_url, scraped_at)

### Frontend Files

**Pages:**
- `src/app/app/page.tsx` ✅ - Dashboard (shows content stats, triggers scraping)
- `src/app/app/content/page.tsx` ✅ - Content browser (full list with filters)

**API Integration:** `src/lib/api/content.ts` ✅
```typescript
contentApi.scrape({workspace_id, sources})      // POST /api/v1/content/scrape
contentApi.list(workspace_id, {days, limit})    // GET /api/v1/content/workspaces/{id}
contentApi.getStats(workspace_id)               // GET /api/v1/content/workspaces/{id}/stats
contentApi.getBySource(workspace_id, source)    // GET /api/v1/content/workspaces/{id}/sources/{source}
contentApi.updateItem(id, {title, summary})     // PUT /api/v1/content/{id}
```

**Components Used:**
- `src/components/dashboard/quick-source-manager.tsx` ✅ - Scrape button on dashboard
- `src/components/dashboard/article-card.tsx` ✅ - Display individual content item
- `src/components/dashboard/unified-source-setup.tsx` ✅ - Configure sources
- `src/components/modals/add-source-modal.tsx` ✅ - Add new content source

### Data Flow

```
User clicks "Scrape Content" button
     ↓
contentApi.scrape({workspace_id, sources: ["reddit", "rss"]})
     ↓
POST /api/v1/content/scrape
     ↓
Backend: content_service.scrape_content(workspace_id)
     ↓
Loads workspace config from workspace_configs table
     ↓
For each enabled source:
  ├─ RedditScraper.scrape(subreddits=["OpenAI"])
  │    ↓ Fetches from reddit.com/r/OpenAI.json
  │    ↓ Returns [{title, url, content, score, author}, ...]
  │
  ├─ RSSFeedScraper.scrape(feed_urls=["..."])
  │    ↓ Uses feedparser library
  │    ↓ Returns [{title, url, content, published_at}, ...]
  │
  └─ BlogScraper.scrape(url="...")
       ↓ Uses BeautifulSoup to extract article text
       ↓ Returns [{title, url, content, author}, ...]
     ↓
Saves to database: INSERT INTO content_items (workspace_id, source, title, ...)
     ↓
Returns: {total_items: 25, items_by_source: {reddit: 15, rss: 10}}
     ↓
Frontend: Shows toast "✓ Scraped 25 new items"
     ↓
Refreshes content list
```

**Request Example:**
```json
POST /api/v1/content/scrape
{
  "workspace_id": "aec6120d-42ec-438b-b0ae-c8149ae6ca9b",
  "sources": ["reddit", "rss"],
  "limit_per_source": 25
}
```

**Response Example:**
```json
{
  "success": true,
  "data": {
    "total_items": 35,
    "items_by_source": {
      "reddit": 20,
      "rss": 15
    },
    "status": "completed"
  }
}
```

---

## 4. Newsletters

### What It Does
Generates newsletters using AI (GPT-4 or Claude) from scraped content. You can edit, preview, and manage drafts before sending.

### Backend Files

**API Endpoint:** `backend/api/v1/newsletters.py` ✅
- `POST /api/v1/newsletters/generate` - Generate new newsletter with AI
- `GET /api/v1/newsletters/workspaces/{workspace_id}` - List all newsletters
- `GET /api/v1/newsletters/{id}` - Get single newsletter
- `PUT /api/v1/newsletters/{id}` - Update newsletter (title, content, status)
- `DELETE /api/v1/newsletters/{id}` - Delete newsletter
- `GET /api/v1/newsletters/{id}/html` - Export as HTML
- `GET /api/v1/newsletters/{id}/text` - Export as plain text

**Service:** `backend/services/newsletter_service.py` ✅
- `generate_newsletter(workspace_id, tone, temperature)` - Creates newsletter
- `update_newsletter_status(newsletter_id, status, title)` - Update draft
- `get_newsletter(newsletter_id)` - Fetch with content items

**AI Generators:**
- `backend/services/openai_newsletter_generator.py` ✅ - Uses OpenAI GPT-4
- `backend/services/claude_newsletter_generator.py` ⚠️ - Uses Anthropic Claude (needs `pip install anthropic`)

**Database Tables:**
- `newsletters` - Newsletter drafts (title, content_html, content_text, model_used, tone, status, generated_at, sent_at)
- `newsletter_content_items` - M:M relationship (which content items are in which newsletter)

### Frontend Files

**Pages:**
- `src/app/app/page.tsx` ✅ - Dashboard (generate button, latest draft preview)
- `src/app/app/history/page.tsx` ✅ - Newsletter history (list of all past newsletters)

**API Integration:** `src/lib/api/newsletters.ts` ✅
```typescript
newslettersApi.generate({workspace_id, tone, temperature})  // POST /api/v1/newsletters/generate
newslettersApi.list(workspace_id)                           // GET /api/v1/newsletters/workspaces/{id}
newslettersApi.get(id)                                      // GET /api/v1/newsletters/{id}
newslettersApi.update(id, {subject_line, status})           // PUT /api/v1/newsletters/{id}
newslettersApi.delete(id)                                   // DELETE /api/v1/newsletters/{id}
```

**Components Used:**
- `src/components/dashboard/enhanced-draft-card.tsx` ✅ - Preview latest newsletter on dashboard
- `src/components/modals/draft-editor-modal.tsx` ✅ - Edit newsletter before sending
- `src/components/modals/generation-settings-modal.tsx` ✅ - Configure AI settings (tone, temperature)

### Data Flow

```
User clicks "Generate Newsletter" button
     ↓
Opens GenerationSettingsModal (choose tone, temperature, max items)
     ↓
User clicks "Generate" → newslettersApi.generate({workspace_id, tone: "professional", temperature: 0.7})
     ↓
POST /api/v1/newsletters/generate
     ↓
Backend: newsletter_service.generate_newsletter(workspace_id)
     ↓
Step 1: Fetch recent content from database
  SELECT * FROM content_items
  WHERE workspace_id = ? AND scraped_at > NOW() - INTERVAL '7 days'
  ORDER BY score DESC LIMIT 10
     ↓
Step 2: Apply feedback ranking (boost preferred sources +20%, penalize disliked -30%)
     ↓
Step 3: Load style profile (if trained) from style_profiles table
     ↓
Step 4: Build AI prompt
  System: "You are a newsletter writer with professional tone..."
  User: "Create newsletter from these 10 items: [summaries]"
     ↓
Step 5: Call OpenAI API
  openai.ChatCompletion.create(
    model="gpt-4-turbo-preview",
    temperature=0.7,
    messages=[system, user]
  )
     ↓
Step 6: Parse AI response (extracts HTML content)
     ↓
Step 7: Save to database
  INSERT INTO newsletters (workspace_id, title, content_html, content_text, status='draft')
  INSERT INTO newsletter_content_items (newsletter_id, content_item_id) -- for each item used
     ↓
Returns: {newsletter: {...}, content_items_count: 10, sources_used: ["reddit", "rss"]}
     ↓
Frontend: Shows success toast, opens DraftEditorModal with preview
     ↓
User can edit title/content before sending
```

**Request Example:**
```json
POST /api/v1/newsletters/generate
{
  "workspace_id": "aec6120d-42ec-438b-b0ae-c8149ae6ca9b",
  "tone": "professional",
  "temperature": 0.7,
  "max_items": 10,
  "custom_instructions": "Focus on AI safety topics"
}
```

**Response Example:**
```json
{
  "success": true,
  "data": {
    "message": "Newsletter generated successfully",
    "newsletter": {
      "id": "3df53dc8-f0cc-42af-8d34-5492acc853cc",
      "workspace_id": "aec6120d-42ec-438b-b0ae-c8149ae6ca9b",
      "title": "This Week in AI: Major Breakthroughs",
      "content_html": "<html>...</html>",
      "content_text": "Plain text version...",
      "model_used": "gpt-4-turbo-preview",
      "temperature": 0.7,
      "tone": "professional",
      "status": "draft",
      "generated_at": "2025-10-23T13:22:27Z",
      "content_items_count": 10
    },
    "content_items_count": 10,
    "sources_used": ["reddit", "rss", "blog"]
  }
}
```

---

## 5. Subscribers

### What It Does
Manages email addresses of people who will receive newsletters. Supports adding single emails, bulk imports (CSV), and tracking subscription status.

### Backend Files

**API Endpoint:** `backend/api/v1/subscribers.py` ✅
- `POST /api/v1/subscribers` - Add single subscriber
- `POST /api/v1/subscribers/bulk` - Import multiple subscribers (CSV upload)
- `GET /api/v1/subscribers/workspaces/{workspace_id}` - List all subscribers
- `GET /api/v1/subscribers/workspaces/{workspace_id}/stats` - Get subscriber statistics
- `GET /api/v1/subscribers/{id}` - Get single subscriber
- `PUT /api/v1/subscribers/{id}` - Update subscriber (email, status)
- `DELETE /api/v1/subscribers/{id}` - Delete subscriber
- `POST /api/v1/subscribers/{id}/unsubscribe` - Mark as unsubscribed

**Service:** `backend/services/subscriber_service.py` ⚠️ (Uses database directly, no service file yet)

**Database Tables:**
- `subscribers` - Email list (email, workspace_id, status='subscribed'|'unsubscribed'|'bounced', subscribed_at, unsubscribed_at)

### Frontend Files

**Pages:**
- `src/app/app/subscribers/page.tsx` ✅ - Full subscriber management page
- `src/app/app/settings/page.tsx` ✅ - Subscribers section in settings

**API Integration:** `src/lib/api/subscribers.ts` ✅
```typescript
subscribersApi.create({workspace_id, email, first_name, last_name})  // POST /api/v1/subscribers
subscribersApi.bulkCreate({workspace_id, subscribers: [...]})        // POST /api/v1/subscribers/bulk
subscribersApi.list(workspace_id, status, limit)                     // GET /api/v1/subscribers/workspaces/{id}
subscribersApi.getStats(workspace_id)                                // GET /api/v1/subscribers/workspaces/{id}/stats
subscribersApi.update(id, {email, status})                           // PUT /api/v1/subscribers/{id}
subscribersApi.delete(id)                                            // DELETE /api/v1/subscribers/{id}
subscribersApi.unsubscribe(id)                                       // POST /api/v1/subscribers/{id}/unsubscribe
```

**Components Used:**
- `src/components/settings/subscribers-settings.tsx` ✅ - Subscriber list with add/edit/delete
- `src/components/modals/add-subscriber-modal.tsx` ✅ - Add single subscriber form
- `src/components/modals/import-subscribers-modal.tsx` ✅ - CSV upload interface
- `src/components/modals/import-csv-modal.tsx` ✅ - CSV parsing and preview

### Data Flow

```
User clicks "Add Subscriber" → Opens AddSubscriberModal
     ↓
User enters email: "user@example.com"
     ↓
subscribersApi.create({workspace_id, email, first_name, last_name})
     ↓
POST /api/v1/subscribers
{
  "workspace_id": "aec6120d-...",
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe"
}
     ↓
Backend: Validates email format
     ↓
Checks for duplicates: SELECT * FROM subscribers WHERE email = ? AND workspace_id = ?
     ↓
If duplicate: Returns 400 error "Email already exists"
     ↓
If unique: INSERT INTO subscribers (workspace_id, email, first_name, last_name, status='subscribed', subscribed_at=NOW())
     ↓
Returns: {id: "...", email: "user@example.com", status: "subscribed", subscribed_at: "2025-10-23T..."}
     ↓
Frontend: Shows toast "✓ Subscriber added", refreshes list
```

**CSV Import Flow:**
```
User uploads subscribers.csv:
  email,first_name,last_name
  john@example.com,John,Doe
  jane@example.com,Jane,Smith
     ↓
Frontend: Parses CSV using Papa Parse library
     ↓
Validates each row (checks email format, required fields)
     ↓
subscribersApi.bulkCreate({workspace_id, subscribers: [{email, first_name, last_name}, ...]})
     ↓
POST /api/v1/subscribers/bulk
     ↓
Backend: Processes each subscriber
  - Skips duplicates
  - Validates email format
  - Inserts valid ones
     ↓
Returns: {created: 50, skipped: 5, errors: 2, details: [...]}
     ↓
Frontend: Shows summary "✓ Imported 50 subscribers, 5 duplicates skipped"
```

---

## 6. Delivery (Email Sending)

### What It Does
Sends newsletters to subscribers via email. Supports SMTP (Gmail, Outlook) and SendGrid. Includes test email feature and tracking pixel injection.

### Backend Files

**API Endpoint:** `backend/api/v1/delivery.py` ✅
- `POST /api/v1/delivery/send` - Send newsletter (background, returns immediately)
- `POST /api/v1/delivery/send-sync` - Send newsletter (waits for completion)
- `GET /api/v1/delivery/{id}/status` - Check delivery status
- `GET /api/v1/delivery/workspaces/{workspace_id}` - List delivery history

**Service:** `backend/services/delivery_service.py` ✅
- `send_newsletter(newsletter_id, workspace_id, test_email)` - Sends emails
- `inject_tracking_pixel(html, newsletter_id, email)` - Adds 1x1 transparent image
- `inject_tracking_links(html, newsletter_id, email)` - Wraps links with tracking redirect

**Database Tables:**
- `delivery_logs` - Send records (newsletter_id, subscriber_email, status='sent'|'failed', sent_at, error_message)

### Frontend Files

**Pages:**
- `src/app/app/page.tsx` ✅ - Dashboard (send button)

**API Integration:** `src/lib/api/delivery.ts` ✅
```typescript
deliveryApi.sendNewsletter({newsletter_id, workspace_id}, sync=false)      // POST /api/v1/delivery/send
deliveryApi.send({newsletter_id, workspace_id})                            // Alias for above
deliveryApi.sendTest(newsletter_id, workspace_id, test_email)              // POST /api/v1/delivery/send-sync (with test_email)
deliveryApi.getDeliveryStatus(delivery_id)                                 // GET /api/v1/delivery/{id}/status
deliveryApi.listDeliveries(workspace_id, limit)                            // GET /api/v1/delivery/workspaces/{id}
```

**Components Used:**
- `src/components/modals/send-confirmation-modal.tsx` ✅ - Confirm before sending to all
- `src/components/modals/send-test-modal.tsx` ✅ - Send test email to your address
- `src/components/modals/schedule-send-modal.tsx` ✅ - Schedule send for later (uses scheduler API)

### Data Flow

```
User clicks "Send Newsletter" → Opens SendConfirmationModal
     ↓
Shows: "Send to 1,234 subscribers?"
     ↓
User confirms → deliveryApi.send({newsletter_id, workspace_id})
     ↓
POST /api/v1/delivery/send (background task)
     ↓
Returns immediately: {status: "sending", message: "Newsletter delivery started"}
     ↓
Backend (in background):
  Step 1: Fetch newsletter HTML from newsletters table
  Step 2: Fetch all subscribers WHERE workspace_id = ? AND status = 'subscribed'
  Step 3: For each subscriber:
    ├─ Inject tracking pixel:
    │   <img src="http://localhost:8000/track/pixel/{HMAC_TOKEN}.png" width="1" height="1">
    │   Token contains: newsletter_id, subscriber_email (HMAC signed for security)
    │
    ├─ Replace all <a href> links with tracking redirects:
    │   <a href="http://localhost:8000/track/click/{HMAC_TOKEN}">
    │   Token contains: newsletter_id, subscriber_email, target_url, content_item_id
    │
    ├─ Send email via SMTP or SendGrid:
    │   If SMTP: Uses Python smtplib
    │   If SendGrid: Uses SendGrid API
    │
    └─ Record result:
        INSERT INTO delivery_logs (newsletter_id, subscriber_email, status='sent'|'failed', sent_at, error_message)
        INSERT INTO email_analytics_events (newsletter_id, recipient_email, event_type='sent', timestamp)
     ↓
Step 4: Update newsletter status
  UPDATE newsletters SET status='sent', sent_at=NOW() WHERE id = ?
     ↓
Frontend: Shows toast "✓ Sending newsletter to 1,234 subscribers"
     ↓
User can check progress in delivery history
```

**Test Email Flow:**
```
User clicks "Send Test" → Opens SendTestModal
     ↓
User enters: "myemail@example.com"
     ↓
deliveryApi.sendTest(newsletter_id, workspace_id, "myemail@example.com")
     ↓
POST /api/v1/delivery/send-sync (sync=true, waits for result)
{
  "newsletter_id": "...",
  "workspace_id": "...",
  "test_email": "myemail@example.com"
}
     ↓
Backend: Sends to ONLY that email address (ignores subscribers table)
     ↓
Waits for SMTP/SendGrid response
     ↓
Returns: {status: "sent", recipient: "myemail@example.com", sent_at: "..."}
     ↓
Frontend: Shows toast "✓ Test email sent to myemail@example.com"
```

---

## 7. Scheduler (Automation)

### What It Does
Automates the entire pipeline: scrape content → generate newsletter → send to subscribers. Runs on a schedule (e.g., daily at 8 AM).

### Backend Files

**API Endpoint:** `backend/api/v1/scheduler.py` ✅
- `POST /api/v1/scheduler` - Create scheduled job
- `GET /api/v1/scheduler/workspaces/{workspace_id}` - List all jobs
- `GET /api/v1/scheduler/{job_id}` - Get job details
- `PUT /api/v1/scheduler/{job_id}` - Update job (schedule, enabled)
- `DELETE /api/v1/scheduler/{job_id}` - Delete job
- `POST /api/v1/scheduler/{job_id}/pause` - Pause job
- `POST /api/v1/scheduler/{job_id}/resume` - Resume job
- `POST /api/v1/scheduler/{job_id}/run-now` - Trigger immediate execution
- `GET /api/v1/scheduler/{job_id}/history` - Get execution logs
- `GET /api/v1/scheduler/{job_id}/stats` - Get success/failure stats

**Service:** `backend/services/scheduler_service.py` ✅
- `create_job(workspace_id, schedule, actions)` - Creates cron job
- `execute_job(job_id)` - Runs the pipeline

**Worker:** `backend/worker.py` ✅
- Background process that runs scheduled jobs
- Uses APScheduler library
- Checks every 5 minutes for jobs due to run

**Database Tables:**
- `scheduler_jobs` - Job definitions (workspace_id, schedule='0 9 * * *', is_enabled=true, actions=['scrape','generate','send'], last_run_at, next_run_at)
- `scheduler_execution_logs` - Execution history (job_id, status='success'|'failed', started_at, completed_at, result, error_message)

### Frontend Files

**Pages:**
- `src/app/app/schedule/page.tsx` ✅ - Full scheduler management page
- `src/app/app/settings/page.tsx` ✅ - Schedule section in settings

**API Integration:** `src/lib/api/scheduler.ts` ✅
```typescript
schedulerApi.createJob({workspace_id, schedule, actions})   // POST /api/v1/scheduler
schedulerApi.listJobs(workspace_id)                         // GET /api/v1/scheduler/workspaces/{id}
schedulerApi.getJob(job_id)                                 // GET /api/v1/scheduler/{job_id}
schedulerApi.updateJob(job_id, {schedule, is_enabled})      // PUT /api/v1/scheduler/{job_id}
schedulerApi.deleteJob(job_id)                              // DELETE /api/v1/scheduler/{job_id}
schedulerApi.pauseJob(job_id)                               // POST /api/v1/scheduler/{job_id}/pause
schedulerApi.resumeJob(job_id)                              // POST /api/v1/scheduler/{job_id}/resume
schedulerApi.runJobNow(job_id, {actions})                   // POST /api/v1/scheduler/{job_id}/run-now
schedulerApi.getExecutionHistory(job_id, limit)             // GET /api/v1/scheduler/{job_id}/history
schedulerApi.getExecutionStats(job_id)                      // GET /api/v1/scheduler/{job_id}/stats
```

**Components Used:**
- `src/components/settings/schedule-settings.tsx` ✅ - Create/edit scheduled jobs
- `src/components/modals/schedule-send-modal.tsx` ✅ - Schedule one-time send

### Data Flow

```
User creates schedule: "Every day at 8:00 AM"
     ↓
schedulerApi.createJob({
  workspace_id: "...",
  schedule: "0 8 * * *",  // Cron expression: minute hour day month weekday
  actions: ["scrape", "generate", "send"],
  is_enabled: true
})
     ↓
POST /api/v1/scheduler
     ↓
Backend: scheduler_service.create_job()
     ↓
Calculates next_run_at from cron expression (2025-10-24 08:00:00)
     ↓
INSERT INTO scheduler_jobs (workspace_id, schedule, actions, is_enabled, next_run_at)
     ↓
Returns: {id: "...", schedule: "0 8 * * *", next_run_at: "2025-10-24T08:00:00Z", is_enabled: true}
     ↓
Frontend: Shows "✓ Job scheduled for tomorrow at 8:00 AM"

--- NEXT DAY AT 8:00 AM ---

Background worker (backend/worker.py) checks for jobs:
     ↓
SELECT * FROM scheduler_jobs WHERE next_run_at <= NOW() AND is_enabled = true
     ↓
Found job → scheduler_service.execute_job(job_id)
     ↓
Logs start: INSERT INTO scheduler_execution_logs (job_id, status='running', started_at=NOW())
     ↓
Step 1: Execute "scrape" action
  ├─ Calls content_service.scrape_content(workspace_id)
  └─ Result: {total_items: 25}
     ↓
Step 2: Execute "generate" action
  ├─ Calls newsletter_service.generate_newsletter(workspace_id)
  └─ Result: {newsletter_id: "..."}
     ↓
Step 3: Execute "send" action
  ├─ Calls delivery_service.send_newsletter(newsletter_id, workspace_id)
  └─ Result: {sent_count: 1234}
     ↓
Logs completion: UPDATE scheduler_execution_logs SET status='success', completed_at=NOW(), result={...}
     ↓
Update job: UPDATE scheduler_jobs SET last_run_at=NOW(), next_run_at='2025-10-25 08:00:00'
     ↓
Job scheduled again for tomorrow at 8:00 AM
```

**Cron Expression Examples:**
```
"0 8 * * *"    → Every day at 8:00 AM
"0 9 * * 1"    → Every Monday at 9:00 AM
"0 12 1 * *"   → 1st of every month at 12:00 PM
"*/30 * * * *" → Every 30 minutes
"0 0 * * 0"    → Every Sunday at midnight
```

---

## 8. Analytics

### What It Does
Tracks email opens, clicks, and engagement. Uses tracking pixels (invisible 1x1 images) and click redirects to measure how subscribers interact with newsletters.

### Backend Files

**API Endpoint:** `backend/api/v1/analytics.py` ✅
- `POST /api/v1/analytics/events` - Record analytics event (internal use)
- `GET /api/v1/analytics/newsletters/{newsletter_id}` - Get newsletter stats
- `GET /api/v1/analytics/workspaces/{workspace_id}/summary` - Get workspace summary (**Recently optimized - was 6-7s, now <500ms**)
- `GET /api/v1/analytics/workspaces/{workspace_id}/content-performance` - Get top-performing content
- `GET /api/v1/analytics/workspaces/{workspace_id}/export` - Export CSV/JSON
- `POST /api/v1/analytics/newsletters/{newsletter_id}/recalculate` - Recalculate stats

**Tracking Endpoints:** `backend/api/tracking.py` ✅
- `GET /track/pixel/{hmac_token}.png` - Tracking pixel (records email open)
- `GET /track/click/{hmac_token}` - Click tracking redirect
- `GET /track/unsubscribe/{hmac_token}` - Unsubscribe link

**Service:** `backend/services/analytics_service.py` ✅
- `record_event(event_type, newsletter_id, recipient_email)` - Logs event
- `get_newsletter_analytics(newsletter_id)` - Calculate open/click rates
- `get_workspace_analytics(workspace_id)` - Aggregate statistics

**Database Tables:**
- `email_analytics_events` - Raw events (event_type='sent'|'opened'|'clicked'|'bounced'|'unsubscribed', newsletter_id, recipient_email, timestamp, user_agent, ip_address)
- `newsletter_analytics_summary` - Aggregated stats (newsletter_id, total_sent, unique_opens, unique_clicks, open_rate, click_rate, engagement_score)
- `content_performance` - Content engagement (content_item_id, times_included, total_clicks, engagement_score)

**Database RPC Function:**
- `get_workspace_analytics_summary(workspace_uuid, start_date, end_date)` ✅ - Optimized SQL function (migration 011)

### Frontend Files

**Pages:**
- `src/app/app/page.tsx` ✅ - Dashboard (displays workspace analytics summary)
- `src/app/app/analytics/page.tsx` ✅ - Full analytics page
- `src/app/app/history/page.tsx` ✅ - Newsletter history (shows open/click rates per newsletter)

**API Integration:** `src/lib/api/analytics.ts` ✅
```typescript
analyticsApi.recordEvent({event_type, newsletter_id, recipient_email})         // POST /api/v1/analytics/events
analyticsApi.getNewsletterAnalytics(newsletter_id)                             // GET /api/v1/analytics/newsletters/{id}
analyticsApi.recalculateNewsletterAnalytics(newsletter_id)                     // POST /api/v1/analytics/newsletters/{id}/recalculate
analyticsApi.getWorkspaceSummary(workspace_id, start_date, end_date)           // GET /api/v1/analytics/workspaces/{id}/summary
analyticsApi.getContentPerformance(workspace_id, limit)                        // GET /api/v1/analytics/workspaces/{id}/content-performance
analyticsApi.getDashboard(workspace_id, period)                                // GET /api/v1/analytics/workspaces/{id}/dashboard
analyticsApi.exportData(workspace_id, format, start_date, end_date)            // GET /api/v1/analytics/workspaces/{id}/export
```

**Components Used:**
- `src/components/dashboard/stats-overview.tsx` ✅ - Displays key metrics on dashboard
- `src/components/dashboard/recent-activity.tsx` ✅ - Shows recent events
- `src/components/settings/analytics-settings.tsx` ✅ - Analytics preferences

### Data Flow

**Tracking Pixel (Email Open):**
```
Email sent with HTML:
  <img src="http://localhost:8000/track/pixel/a1b2c3d4e5f6.png" width="1" height="1">
     ↓
Subscriber opens email in Gmail/Outlook
     ↓
Email client loads image → GET /track/pixel/a1b2c3d4e5f6.png
     ↓
Backend: tracking.py endpoint receives request
     ↓
Verifies HMAC token (ensures it's not tampered)
     ↓
Extracts: newsletter_id, recipient_email from token
     ↓
Records event:
  INSERT INTO email_analytics_events (
    newsletter_id,
    recipient_email,
    event_type='opened',
    timestamp=NOW(),
    user_agent='Mozilla/5.0...',
    ip_address='192.168.1.1'
  )
     ↓
Returns: 1x1 transparent PNG image (1 byte)
     ↓
Email client displays invisible pixel (user doesn't see anything)
     ↓
Background job recalculates stats:
  UPDATE newsletter_analytics_summary
  SET unique_opens = (SELECT COUNT(DISTINCT recipient_email) FROM events WHERE event_type='opened'),
      open_rate = unique_opens / total_sent * 100
  WHERE newsletter_id = ?
```

**Click Tracking:**
```
Email contains link:
  <a href="http://localhost:8000/track/click/x9y8z7w6v5u4">Read Article</a>
     ↓
Subscriber clicks link
     ↓
Browser requests: GET /track/click/x9y8z7w6v5u4
     ↓
Backend: tracking.py endpoint
     ↓
Verifies HMAC token → Extracts: newsletter_id, recipient_email, target_url, content_item_id
     ↓
Records event:
  INSERT INTO email_analytics_events (event_type='clicked', content_item_id=?, ...)
  UPDATE content_performance SET total_clicks = total_clicks + 1 WHERE content_item_id = ?
     ↓
Responds with 302 redirect to target_url (e.g., https://openai.com/blog/...)
     ↓
Browser follows redirect → User sees the article
```

**Analytics Summary (Dashboard Load):**
```
Dashboard loads → analyticsApi.getWorkspaceSummary(workspace_id)
     ↓
GET /api/v1/analytics/workspaces/{id}/summary?start_date=2025-09-23&end_date=2025-10-23
     ↓
Backend: analytics_service.get_workspace_analytics(workspace_id, start_date, end_date)
     ↓
Calls database RPC function:
  SELECT * FROM get_workspace_analytics_summary(
    workspace_uuid := 'aec6120d-...',
    start_date := '2025-09-23',
    end_date := '2025-10-23'
  )
     ↓
RPC function (optimized with migration 011):
  - Uses single CTE-based query (not 7 separate queries)
  - Leverages 5 performance indexes
  - Completes in <500ms (was 6-7 seconds before)
     ↓
Returns:
{
  "workspace_id": "aec6120d-...",
  "date_range": {"start": "2025-09-23", "end": "2025-10-23"},
  "total_newsletters": 15,
  "total_sent": 18510,       // 15 newsletters × 1234 subscribers
  "total_delivered": 18450,
  "total_opened": 9225,       // 50% open rate
  "total_clicked": 3690,      // 20% click rate
  "avg_open_rate": 50.0,
  "avg_click_rate": 20.0,
  "avg_engagement_score": 75.5,
  "top_performing_content": [
    {
      "content_item_id": "...",
      "clicks": 450,
      "engagement_score": 92.5
    },
    ...
  ]
}
     ↓
Frontend: Displays in StatsOverview component
  - "50% Open Rate" badge
  - "20% Click Rate" badge
  - Chart showing trend over time
```

---

## 9. Style Training

### What It Does
Learns your writing style from sample text you provide. AI then mimics your tone, vocabulary, and sentence structure when generating newsletters.

### Backend Files

**API Endpoint:** `backend/api/v1/style.py` ✅
- `POST /api/v1/style/train` - Train style profile from sample text
- `GET /api/v1/style/workspaces/{workspace_id}` - Get trained style profile
- `PUT /api/v1/style/workspaces/{workspace_id}` - Update style profile
- `DELETE /api/v1/style/workspaces/{workspace_id}` - Delete style profile
- `POST /api/v1/style/test` - Test style with sample generation

**Service:** `backend/services/style_service.py` ✅
- `train_style_profile(workspace_id, sample_text)` - Analyzes writing style
- `get_style_profile(workspace_id)` - Retrieves stored profile
- `apply_style_to_prompt(prompt, style_profile)` - Injects style into AI prompt

**Database Tables:**
- `style_profiles` - Style data (workspace_id, tone, vocabulary_sample, sentence_structure, trained_at, sample_count)

### Frontend Files

**Pages:**
- `src/app/app/style/page.tsx` ✅ - Full style training page
- `src/app/app/settings/page.tsx` ✅ - Style section in settings

**API Integration:** `src/lib/api/style.ts` ✅
```typescript
styleApi.train({workspace_id, sample_text})          // POST /api/v1/style/train
styleApi.getProfile(workspace_id)                    // GET /api/v1/style/workspaces/{id}
styleApi.updateProfile(workspace_id, {tone, ...})    // PUT /api/v1/style/workspaces/{id}
styleApi.deleteProfile(workspace_id)                 // DELETE /api/v1/style/workspaces/{id}
styleApi.testStyle({workspace_id, test_content})     // POST /api/v1/style/test
```

**Components Used:**
- `src/components/settings/style-settings.tsx` ✅ - Style training interface
- Textarea for pasting sample text
- Preview button to test style

### Data Flow

```
User pastes sample text (e.g., previous newsletters they wrote)
     ↓
styleApi.train({workspace_id, sample_text: "..."})
     ↓
POST /api/v1/style/train
{
  "workspace_id": "...",
  "sample_text": "Welcome to this week's newsletter! I'm excited to share..."
}
     ↓
Backend: style_service.train_style_profile(workspace_id, sample_text)
     ↓
Step 1: Analyze tone using NLP (nltk library)
  - Detects: formal vs. casual, enthusiastic vs. neutral
  - Result: "friendly, enthusiastic"
     ↓
Step 2: Extract vocabulary patterns
  - Common words/phrases: "excited", "share", "discover"
  - Sentence starters: "Welcome to", "I'm excited to"
     ↓
Step 3: Analyze sentence structure
  - Average sentence length: 15 words
  - Complexity: medium (mix of simple and compound sentences)
     ↓
Step 4: Save to database
  INSERT INTO style_profiles (
    workspace_id,
    tone='friendly, enthusiastic',
    vocabulary_sample=['excited', 'share', 'discover', ...],
    sentence_structure={'avg_length': 15, 'complexity': 'medium'},
    sample_count=1,
    trained_at=NOW()
  )
     ↓
Returns: {tone: "friendly, enthusiastic", vocabulary_sample: [...], ...}
     ↓
Frontend: Shows "✓ Style profile trained" with preview

--- WHEN GENERATING NEWSLETTER ---

newsletter_service.generate_newsletter(workspace_id) called
     ↓
Loads style profile: SELECT * FROM style_profiles WHERE workspace_id = ?
     ↓
Modifies AI prompt:
  System: "You are a newsletter writer. Write in a friendly, enthusiastic tone.
           Use words like 'excited', 'share', 'discover'.
           Keep sentences around 15 words on average.
           Start with phrases like 'Welcome to' or 'I'm excited to'."
     ↓
AI generates newsletter matching your style
```

---

## 10. Trends Detection

### What It Does
Identifies trending topics from your scraped content using machine learning (TF-IDF + K-means clustering). Helps you see what's popular.

### Backend Files

**API Endpoint:** `backend/api/v1/trends.py` ✅
- `POST /api/v1/trends/detect` - Detect trends from content
- `GET /api/v1/trends/workspaces/{workspace_id}` - List detected trends
- `GET /api/v1/trends/{trend_id}` - Get trend details
- `DELETE /api/v1/trends/{trend_id}` - Delete trend

**Service:** `backend/services/trend_service.py` ✅
- `detect_trends(workspace_id, days)` - Runs ML algorithm
- `get_trends(workspace_id)` - Retrieves stored trends
- Uses scikit-learn: TfidfVectorizer + KMeans clustering

**Database Tables:**
- `trends` - Detected trends (workspace_id, topic_name, keywords, article_count, confidence_score, detected_at)

### Frontend Files

**Pages:**
- `src/app/app/trends/page.tsx` ✅ - Full trends page
- `src/app/app/settings/page.tsx` ✅ - Trends section in settings

**API Integration:** `src/lib/api/trends.ts` ✅
```typescript
trendsApi.detect({workspace_id, days, min_articles})   // POST /api/v1/trends/detect
trendsApi.list(workspace_id)                           // GET /api/v1/trends/workspaces/{id}
trendsApi.get(trend_id)                                // GET /api/v1/trends/{trend_id}
trendsApi.delete(trend_id)                             // DELETE /api/v1/trends/{trend_id}
```

**Components Used:**
- `src/components/settings/trends-settings.tsx` ✅ - Trends configuration and display

### Data Flow

```
User clicks "Detect Trends"
     ↓
trendsApi.detect({workspace_id, days: 7, min_articles: 5})
     ↓
POST /api/v1/trends/detect
     ↓
Backend: trend_service.detect_trends(workspace_id, days=7)
     ↓
Step 1: Fetch recent content
  SELECT title, content FROM content_items
  WHERE workspace_id = ? AND scraped_at > NOW() - INTERVAL '7 days'
     ↓
Step 2: Preprocess text
  - Remove stopwords ("the", "a", "is")
  - Tokenize (split into words)
  - Result: ["ai", "model", "training", "gpt4", "openai", ...]
     ↓
Step 3: TF-IDF vectorization (scikit-learn)
  - Converts text to numerical vectors
  - Identifies important words (high frequency in one article, rare across all articles)
     ↓
Step 4: K-means clustering
  - Groups similar articles into clusters
  - Each cluster = one trend
  - Example: Cluster 1 = AI safety articles, Cluster 2 = GPT-4 articles
     ↓
Step 5: Extract keywords for each cluster
  - Top 5 words with highest TF-IDF score
  - Example: ["ai", "safety", "alignment", "risk", "ethics"]
     ↓
Step 6: Save to database
  INSERT INTO trends (
    workspace_id,
    topic_name='AI Safety',
    keywords=['ai', 'safety', 'alignment', 'risk', 'ethics'],
    article_count=15,
    confidence_score=0.85,
    detected_at=NOW()
  )
     ↓
Returns: [{topic_name: "AI Safety", keywords: [...], article_count: 15}, ...]
     ↓
Frontend: Displays trend cards with keywords and article count
```

---

## 11. Feedback & Learning

### What It Does
Lets you rate content items (thumbs up/down) and entire newsletters. System learns your preferences and ranks content accordingly in future newsletters.

### Backend Files

**API Endpoint:** `backend/api/v1/feedback.py` ✅
- `POST /api/v1/feedback/items/{item_id}/rate` - Rate content item (like/dislike)
- `POST /api/v1/feedback/newsletters/{newsletter_id}/rate` - Rate newsletter
- `GET /api/v1/feedback/workspaces/{workspace_id}` - Get feedback history
- `POST /api/v1/feedback/preferences` - Set content preferences

**Service:** `backend/services/feedback_service.py` ✅
- `rate_content_item(item_id, rating)` - Stores rating
- `apply_feedback_ranking(workspace_id, content_items)` - Adjusts content scores
- Logic: Boost preferred sources +20%, penalize disliked -30%

**Database Tables:**
- `content_feedback` - Item ratings (content_item_id, user_id, rating='like'|'dislike', feedback_text, created_at)
- `newsletter_feedback` - Newsletter ratings (newsletter_id, user_id, rating, feedback_text)
- `content_preferences` - User preferences (user_id, workspace_id, preferred_sources, preferred_topics)

### Frontend Files

**Pages:**
- `src/app/app/content/page.tsx` ✅ - Content browser (thumbs up/down buttons on each item)
- `src/app/app/feedback/page.tsx` ✅ - Full feedback page
- `src/app/app/settings/page.tsx` ✅ - Feedback section in settings

**API Integration:** `src/lib/api/feedback.ts` ✅
```typescript
feedbackApi.rateContentItem(item_id, {rating, feedback_text})         // POST /api/v1/feedback/items/{id}/rate
feedbackApi.rateNewsletter(newsletter_id, {rating, feedback_text})    // POST /api/v1/feedback/newsletters/{id}/rate
feedbackApi.getFeedbackHistory(workspace_id)                          // GET /api/v1/feedback/workspaces/{id}
feedbackApi.setPreferences({workspace_id, preferred_sources, ...})    // POST /api/v1/feedback/preferences
```

**Components Used:**
- `src/components/settings/feedback-settings.tsx` ✅ - Feedback preferences
- Thumbs up/down buttons in content cards

### Data Flow

```
User clicks thumbs up on a Reddit post
     ↓
feedbackApi.rateContentItem(item_id, {rating: "like"})
     ↓
POST /api/v1/feedback/items/{item_id}/rate
{
  "rating": "like",
  "feedback_text": "Great article!"
}
     ↓
Backend: feedback_service.rate_content_item(item_id, rating)
     ↓
INSERT INTO content_feedback (content_item_id, user_id, rating='like', created_at=NOW())
     ↓
Returns: {status: "recorded", item_id: "...", rating: "like"}
     ↓
Frontend: Shows checkmark on thumbs up button

--- WHEN GENERATING NEXT NEWSLETTER ---

newsletter_service.generate_newsletter(workspace_id)
     ↓
Step 1: Fetch recent content (as usual)
     ↓
Step 2: Apply feedback ranking → feedback_service.apply_feedback_ranking(workspace_id, content_items)
     ↓
Queries feedback:
  SELECT content_item_id, rating FROM content_feedback WHERE user_id = ?
     ↓
Adjusts scores:
  For each item:
    - If item has "like" rating: score *= 1.2 (boost by 20%)
    - If item has "dislike" rating: score *= 0.7 (penalize by 30%)
    - If item's source matches preferred sources: score *= 1.2
     ↓
Sorts by adjusted score (highest first)
     ↓
Selects top N items for newsletter
     ↓
Result: Newsletter prioritizes content you liked and avoids content you disliked
```

---

## 12. Tracking (Pixel/Click)

### What It Does
Backend-only endpoints for tracking email opens and clicks. Used by email clients when loading pixels or following links.

### Backend Files

**API Endpoint:** `backend/api/tracking.py` ✅
- `GET /track/pixel/{hmac_token}.png` - Tracking pixel (1x1 transparent PNG)
- `GET /track/click/{hmac_token}` - Click tracking redirect
- `GET /track/unsubscribe/{hmac_token}` - Unsubscribe link

**Service:** `backend/services/tracking_service.py` ✅
- `record_open(newsletter_id, recipient_email)` - Logs email open
- `record_click(newsletter_id, recipient_email, content_item_id, target_url)` - Logs click

**HMAC Token Generation:** `backend/utils/hmac_auth.py` ✅
- Creates secure tokens that can't be tampered with
- Token format: HMAC-SHA256({newsletter_id, recipient_email, ...}, secret_key)

**Database Tables:**
- `email_analytics_events` - All tracking events

### Frontend Files

**None** - These are backend-only endpoints called by email clients, not the frontend.

### Data Flow

See [Analytics section](#8-analytics) for full tracking flow.

---

## 📂 Unused/Missing Files

### ⚠️ Backend Files with Issues

1. **`backend/services/claude_newsletter_generator.py`** ⚠️
   - **Issue**: Requires `pip install anthropic` (not installed)
   - **Error**: `ImportError: anthropic package required`
   - **Impact**: Can't use Claude AI for generation (OpenAI works fine)
   - **Fix**: Run `pip install anthropic`

2. **`backend/api/v1/style.py`, `backend/api/v1/trends.py`, `backend/api/v1/feedback.py`** ⚠️
   - **Status**: Endpoints exist but minimal usage
   - **Impact**: Advanced features, not essential for core functionality
   - **Frontend**: Pages exist but may not be fully integrated

3. **`backend/scrapers/youtube_scraper.py`, `backend/scrapers/x_scraper.py`** ⚠️
   - **Issue**: Require API keys (YOUTUBE_API_KEY, X_API_KEY) not set
   - **Impact**: Can't scrape YouTube/X content
   - **Fix**: Set API keys in `.env` file

### 🔵 Frontend Files Not Used

**None found** - All page files and API integration files are properly connected.

### ✅ Fully Functional Modules

1. **Authentication** ✅ - Login, signup, logout working
2. **Workspaces** ✅ - CRUD, config management working
3. **Content Scraping** ✅ - Reddit, RSS, Blog scrapers working (YouTube/X need keys)
4. **Newsletters** ✅ - Generation with OpenAI working
5. **Subscribers** ✅ - CRUD, bulk import working
6. **Delivery** ✅ - SMTP/SendGrid sending working
7. **Scheduler** ✅ - Cron jobs, automation working
8. **Analytics** ✅ - Tracking, stats working (recently optimized)

### ⚠️ Partially Implemented Modules

9. **Style Training** ⚠️ - Backend exists, frontend page exists, integration unclear
10. **Trends Detection** ⚠️ - Backend exists, frontend page exists, integration unclear
11. **Feedback & Learning** ⚠️ - Backend exists, frontend page exists, thumbs up/down in content page

---

## 📊 File Status Report

### Backend API Endpoints (12 files)

| File | Status | Issues | Frontend Usage |
|------|--------|--------|----------------|
| `auth.py` | ✅ Working | None | Login, Register pages |
| `workspaces.py` | ✅ Working | None | Dashboard, Settings |
| `content.py` | ✅ Working | None | Dashboard, Content page |
| `newsletters.py` | ✅ Working | None | Dashboard, History page |
| `subscribers.py` | ✅ Working | None | Subscribers page, Settings |
| `delivery.py` | ✅ Working | None | Dashboard (send modals) |
| `scheduler.py` | ✅ Working | None | Schedule page, Settings |
| `analytics.py` | ✅ Working | Recently optimized (6-7s → <500ms) | Dashboard, Analytics page |
| `style.py` | ⚠️ Partial | Low usage | Style page, Settings |
| `trends.py` | ⚠️ Partial | Low usage | Trends page, Settings |
| `feedback.py` | ⚠️ Partial | Low usage | Content page (thumbs), Feedback page |
| `tracking.py` | ✅ Working | None | Email clients only (not frontend) |

### Backend Services (12 files)

| File | Status | Issues |
|------|--------|--------|
| `auth_service.py` | ✅ Working | None |
| `workspace_service.py` | ✅ Working | None |
| `content_service.py` | ✅ Working | None |
| `newsletter_service.py` | ✅ Working | Recently fixed (newsletter update bug) |
| `delivery_service.py` | ✅ Working | None |
| `scheduler_service.py` | ✅ Working | None |
| `analytics_service.py` | ✅ Working | Recently optimized (uses new RPC function) |
| `tracking_service.py` | ✅ Working | None |
| `style_service.py` | ⚠️ Partial | Low usage |
| `trend_service.py` | ⚠️ Partial | Low usage |
| `feedback_service.py` | ⚠️ Partial | Low usage |
| `openai_newsletter_generator.py` | ✅ Working | None |
| `claude_newsletter_generator.py` | ❌ Broken | Missing `anthropic` package |

### Backend Scrapers (5 files)

| File | Status | Issues |
|------|--------|--------|
| `reddit_scraper.py` | ✅ Working | None (uses public API) |
| `rss_scraper.py` | ✅ Working | None |
| `blog_scraper.py` | ✅ Working | None (BeautifulSoup) |
| `youtube_scraper.py` | ⚠️ Needs Key | Requires YOUTUBE_API_KEY in .env |
| `x_scraper.py` | ⚠️ Needs Key | Requires X_API_KEY, X_API_SECRET in .env |

### Frontend Pages (14 files)

| File | Status | Issues | Backend API Used |
|------|--------|--------|-----------------|
| `page.tsx` (landing) | ✅ Working | None | None (public) |
| `login/page.tsx` | ✅ Working | None | `auth.py` |
| `register/page.tsx` | ✅ Working | None | `auth.py` |
| `forgot-password/page.tsx` | ✅ Working | None | `auth.py` |
| `app/page.tsx` (dashboard) | ✅ Working | None | All APIs (hub) |
| `app/content/page.tsx` | ✅ Working | None | `content.py`, `feedback.py` |
| `app/history/page.tsx` | ✅ Working | None | `newsletters.py`, `analytics.py` |
| `app/settings/page.tsx` | ✅ Working | None | All APIs (unified hub) |
| `app/subscribers/page.tsx` | ✅ Working | None | `subscribers.py` |
| `app/schedule/page.tsx` | ✅ Working | None | `scheduler.py` |
| `app/analytics/page.tsx` | ✅ Working | None | `analytics.py` |
| `app/style/page.tsx` | ⚠️ Partial | Low integration | `style.py` |
| `app/trends/page.tsx` | ⚠️ Partial | Low integration | `trends.py` |
| `app/feedback/page.tsx` | ⚠️ Partial | Low integration | `feedback.py` |

### Frontend API Integration (12 files)

| File | Status | Issues | Endpoints Called |
|------|--------|--------|-----------------|
| `auth.ts` | ✅ Working | None | `/api/v1/auth/*` |
| `workspaces.ts` | ✅ Working | None | `/api/v1/workspaces/*` |
| `content.ts` | ✅ Working | None | `/api/v1/content/*` |
| `newsletters.ts` | ✅ Working | None | `/api/v1/newsletters/*` |
| `subscribers.ts` | ✅ Working | None | `/api/v1/subscribers/*` |
| `delivery.ts` | ✅ Working | None | `/api/v1/delivery/*` |
| `scheduler.ts` | ✅ Working | None | `/api/v1/scheduler/*` |
| `analytics.ts` | ✅ Working | None | `/api/v1/analytics/*` |
| `style.ts` | ⚠️ Partial | Low usage | `/api/v1/style/*` |
| `trends.ts` | ⚠️ Partial | Low usage | `/api/v1/trends/*` |
| `feedback.ts` | ⚠️ Partial | Low usage | `/api/v1/feedback/*` |
| `client.ts` | ✅ Working | None | Base API client (Axios wrapper) |

### Frontend Components (50+ files)

**Dashboard Components** (All ✅ Working):
- `enhanced-draft-card.tsx`
- `article-card.tsx`
- `stats-overview.tsx`
- `recent-activity.tsx`
- `welcome-section.tsx`
- `motivational-tip.tsx`
- `quick-source-manager.tsx`
- `unified-source-setup.tsx`
- `workspace-management.tsx`
- `draft-status-card.tsx`
- `source-preview-cards.tsx`
- `empty-state.tsx`

**Settings Components** (All ✅ Working):
- `settings-sidebar.tsx`
- `setup-progress.tsx`
- `sources-settings.tsx`
- `schedule-settings.tsx`
- `subscribers-settings.tsx`
- `email-settings.tsx`
- `workspace-settings.tsx`
- `api-keys-settings.tsx`
- `style-settings.tsx` ⚠️
- `trends-settings.tsx` ⚠️
- `analytics-settings.tsx`
- `feedback-settings.tsx` ⚠️
- `source-card.tsx`
- `empty-state-coming-soon.tsx`

**Modal Components** (All ✅ Working):
- `draft-editor-modal.tsx`
- `send-confirmation-modal.tsx`
- `send-test-modal.tsx`
- `schedule-send-modal.tsx`
- `generation-settings-modal.tsx`
- `add-source-modal.tsx`
- `manage-sources-modal.tsx`
- `add-subscriber-modal.tsx`
- `import-subscribers-modal.tsx`
- `import-csv-modal.tsx`

**UI Primitives** (All ✅ Working):
- `button.tsx`, `input.tsx`, `card.tsx`, `dialog.tsx`, `badge.tsx`
- `select.tsx`, `toast.tsx`, `skeleton.tsx`, `tabs.tsx`, `table.tsx`
- `switch.tsx`, `slider.tsx`, `checkbox.tsx`, `label.tsx`, `textarea.tsx`
- `dropdown-menu.tsx`, `accordion.tsx`, `thumbnail.tsx`, `tooltip.tsx`
- `toaster.tsx`, `sample-data-badge.tsx`

**Layout Components** (All ✅ Working):
- `app-header.tsx`

**Common Components** (All ✅ Working):
- `client-only.tsx`

---

## 🔧 Quick Fixes Needed

### High Priority

1. **Install Anthropic Package** (for Claude AI support)
   ```bash
   pip install anthropic
   ```

### Medium Priority

2. **Add YouTube API Key** (for YouTube scraping)
   - Get key from: https://console.cloud.google.com/
   - Add to `.env`: `YOUTUBE_API_KEY=AIzaSy...`

3. **Add X/Twitter API Keys** (for X scraping)
   - Get keys from: https://developer.twitter.com/
   - Add to `.env`:
     ```
     X_API_KEY=abcd1234...
     X_API_SECRET=secret123...
     X_BEARER_TOKEN=Bearer ...
     ```

### Low Priority

4. **Integrate Style/Trends/Feedback Pages More Deeply**
   - Backend works, frontend pages exist
   - Need better UX flow for users to discover these features
   - Consider adding prominent CTAs on dashboard

---

## 📖 How to Use This Document

**Finding a Feature:**
1. Use Ctrl+F to search for page name (e.g., "dashboard", "login")
2. Scroll to the relevant module section
3. Follow the data flow diagram to understand how it works

**Debugging:**
1. Find the feature in this document
2. Check the "Data Flow" section to see where the issue might be
3. Look at "Request Example" and "Response Example" to verify payloads
4. Check "File Status Report" for known issues

**Adding a New Feature:**
1. Pick an existing module as a template
2. Follow the same structure: API endpoint → Service → Database
3. Create frontend page → API integration → Components
4. Update this document with your new feature!

---

**Last Updated:** 2025-10-23
**Document Version:** 1.0
**Total Backend Endpoints:** 80+
**Total Frontend Pages:** 14
**Total Components:** 50+
**Status:** 85% Complete (Core features working, advanced features partial)
