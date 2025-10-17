# Frontend-Backend Endpoint Mapping

**Last Updated:** 2025-10-17
**Purpose:** Complete mapping of frontend architecture to backend API endpoints

---

## Table of Contents
1. [Frontend Architecture Overview](#frontend-architecture-overview)
2. [Frontend → Backend Mapping](#frontend--backend-mapping)
3. [Unmapped Backend Endpoints](#unmapped-backend-endpoints)
4. [Missing Frontend Pages](#missing-frontend-pages)
5. [Schema Mismatches](#schema-mismatches)

---

## Frontend Architecture Overview

### Routes Structure

```
/ (Landing Page)
├── /login
├── /register
└── /app (Protected Routes)
    ├── /app (Dashboard)
    ├── /app/settings
    └── /app/history
```

### Frontend API Clients

All API clients located in `frontend-nextjs/src/lib/api/`:

- ✅ `auth.ts` - Authentication (login, register, logout)
- ✅ `workspaces.ts` - Workspace management
- ✅ `newsletters.ts` - Newsletter generation and management
- ✅ `content.ts` - Content statistics
- ✅ `delivery.ts` - Email delivery
- ✅ `scheduler.ts` - Scheduling
- ✅ `subscribers.ts` - Subscriber management
- ✅ `style.ts` - Writing style
- ✅ `trends.ts` - Trends detection
- ✅ `analytics.ts` - Analytics tracking
- ✅ `feedback.ts` - Feedback loop

---

## Frontend → Backend Mapping

### 1. **Authentication** (`/login`, `/register`)

| Frontend Page | API Client | Backend Endpoint | Status |
|--------------|------------|------------------|--------|
| `/register` | `authApi.register()` | `POST /api/v1/auth/signup` | ✅ Working |
| `/login` | `authApi.login()` | `POST /api/v1/auth/login` | ✅ Working |
| N/A | `authApi.logout()` | `POST /api/v1/auth/logout` | ✅ Working |
| N/A | `authApi.getCurrentUser()` | `GET /api/v1/auth/me` | ✅ Working |

**Frontend Implementation:**
- [frontend-nextjs/src/app/register/page.tsx](frontend-nextjs/src/app/register/page.tsx:29) - Calls `authApi.register()`
- [frontend-nextjs/src/app/login/page.tsx](frontend-nextjs/src/app/login/page.tsx:28) - Calls `authApi.login()`

**Backend Implementation:**
- [backend/api/v1/auth.py](backend/api/v1/auth.py:66-99) - Signup endpoint
- [backend/api/v1/auth.py](backend/api/v1/auth.py:102-128) - Login endpoint
- [backend/api/v1/auth.py](backend/api/v1/auth.py:158-175) - Logout endpoint
- [backend/api/v1/auth.py](backend/api/v1/auth.py:131-155) - Get current user endpoint

**Schema:**
```typescript
// Request
{
  email: string,
  password: string,
  username: string (signup only)
}

// Response
{
  success: true,
  data: {
    user_id: string,
    email: string,
    username: string,
    token: string,  // JWT token
    expires_at: string
  }
}
```

---

### 2. **Dashboard** (`/app`)

| Feature | API Client | Backend Endpoint | Status |
|---------|------------|------------------|--------|
| **Workspace Management** |
| List workspaces | `workspacesApi.list()` | `GET /api/v1/workspaces` | ✅ Working |
| Create workspace | `workspacesApi.create()` | `POST /api/v1/workspaces` | ✅ Working |
| Get workspace | `workspacesApi.get(id)` | `GET /api/v1/workspaces/{id}` | ✅ Working |
| Update workspace | `workspacesApi.update()` | `PUT /api/v1/workspaces/{id}` | ✅ Working |
| Delete workspace | `workspacesApi.delete()` | `DELETE /api/v1/workspaces/{id}` | ✅ Working |
| Get config | `workspacesApi.getConfig()` | `GET /api/v1/workspaces/{id}/config` | ✅ Working |
| Update config | `workspacesApi.updateConfig()` | `PUT /api/v1/workspaces/{id}/config` | ✅ Working |
| **Content Management** |
| Get stats | `contentApi.getStats()` | `GET /api/v1/content/workspaces/{id}/stats` | ✅ Working |
| Scrape content | Direct fetch | `POST /api/v1/content/scrape` | ✅ Working |
| **Newsletter Management** |
| List newsletters | `newslettersApi.list()` | `GET /api/v1/newsletters/workspaces/{id}` | ✅ Working |
| Generate newsletter | `newslettersApi.generate()` | `POST /api/v1/newsletters/generate` | ✅ Working |
| Update newsletter | `newslettersApi.update()` | `PUT /api/v1/newsletters/{id}` | ✅ Working |
| **Delivery** |
| Send newsletter | `deliveryApi.send()` | `POST /api/v1/delivery/send` | ✅ Working |
| Send test email | `deliveryApi.sendTest()` | `POST /api/v1/delivery/send-sync` | ✅ Working |
| **Scheduling** |
| Schedule once | `schedulerApi.scheduleOnce()` | `POST /api/v1/scheduler/{id}/run-now` | ✅ Working |

**Frontend Implementation:**
- [frontend-nextjs/src/app/app/page.tsx](frontend-nextjs/src/app/app/page.tsx:108) - Fetches workspaces
- [frontend-nextjs/src/app/app/page.tsx](frontend-nextjs/src/app/app/page.tsx:135) - Fetches config
- [frontend-nextjs/src/app/app/page.tsx](frontend-nextjs/src/app/app/page.tsx:145) - Fetches content stats
- [frontend-nextjs/src/app/app/page.tsx](frontend-nextjs/src/app/app/page.tsx:153) - Fetches newsletters
- [frontend-nextjs/src/app/app/page.tsx](frontend-nextjs/src/app/app/page.tsx:307) - Scrapes content
- [frontend-nextjs/src/app/app/page.tsx](frontend-nextjs/src/app/app/page.tsx:360) - Generates newsletter
- [frontend-nextjs/src/app/app/page.tsx](frontend-nextjs/src/app/app/page.tsx:705-732) - Sends newsletter via deliveryApi.send()
- [frontend-nextjs/src/app/app/page.tsx](frontend-nextjs/src/app/app/page.tsx:760-780) - Sends test email via deliveryApi.sendTest()
- [frontend-nextjs/src/app/app/page.tsx](frontend-nextjs/src/app/app/page.tsx:789-818) - Schedules newsletter via schedulerApi.scheduleOnce()

---

### 3. **Settings** (`/app/settings`)

| Setting Component | API Client | Backend Endpoint | Status |
|-------------------|------------|------------------|--------|
| Sources Settings | `workspacesApi.getConfig()` | `GET /api/v1/workspaces/{id}/config` | ✅ Working |
| | `workspacesApi.updateConfig()` | `PUT /api/v1/workspaces/{id}/config` | ✅ Working |
| Schedule Settings | ❓ Not implemented | ❓ Scheduler API | ⚠️ Incomplete |
| Email Settings | ❓ Not implemented | ❓ No backend | ❌ Missing |
| API Keys Settings | ❓ Not implemented | ❓ No backend | ❌ Missing |
| Subscribers | ❓ Not implemented | Backend exists | ⚠️ Incomplete |
| Workspace Settings | `workspacesApi.update()` | `PUT /api/v1/workspaces/{id}` | ✅ Working |
| Style Settings | ❓ Not implemented | Backend exists | ⚠️ Incomplete |
| Trends Settings | ❓ Not implemented | Backend exists | ⚠️ Incomplete |
| Analytics Settings | ❓ Not implemented | Backend exists | ⚠️ Incomplete |
| Feedback Settings | ❓ Not implemented | Backend exists | ⚠️ Incomplete |

**Frontend Implementation:**
- [frontend-nextjs/src/app/app/settings/page.tsx](frontend-nextjs/src/app/app/settings/page.tsx:5-14) - Imports settings components
- Settings components are defined but many are placeholder implementations

**Issue:** Most settings components exist but don't actually call backend APIs yet.

---

### 4. **History** (`/app/history`)

| Feature | API Client | Backend Endpoint | Status |
|---------|------------|------------------|--------|
| List past newsletters | `newslettersApi.list()` | `GET /api/v1/newsletters/workspaces/{id}` | ✅ Working |
| View newsletter | `newslettersApi.get()` | `GET /api/v1/newsletters/{id}` | ✅ Working |
| Duplicate newsletter | `newslettersApi.generate()` | `POST /api/v1/newsletters/generate` | ✅ Working |
| Resend newsletter | `deliveryApi.send()` | `POST /api/v1/delivery/send` | ✅ Working |

**Frontend Implementation:**
- [frontend-nextjs/src/app/app/history/page.tsx](frontend-nextjs/src/app/app/history/page.tsx) - Uses real API calls via newslettersApi.list()
- Filters newsletters by status='sent' to show only sent newsletters
- Handles loading states and empty states properly
- Gracefully handles newsletters without analytics data

**Status:** ✅ Fully connected to backend with real data

---

## Unmapped Backend Endpoints

These backend endpoints exist but have NO frontend implementation:

### **Delivery API** (`backend/api/v1/delivery.py`)

```python
# Backend endpoints that exist:
POST /api/v1/delivery/send          # Send newsletter to all subscribers
POST /api/v1/delivery/send-sync     # Send test email (synchronous)
GET  /api/v1/delivery/{id}/status   # Get delivery job status
GET  /api/v1/delivery/workspaces/{workspace_id}  # Delivery history
```

**Status:** ✅ Frontend has fully implemented `deliveryApi` client
**Frontend Implementation:**
- [frontend-nextjs/src/lib/api/delivery.ts](frontend-nextjs/src/lib/api/delivery.ts) - All methods implemented
- [frontend-nextjs/src/app/app/page.tsx](frontend-nextjs/src/app/app/page.tsx:705-732) - Send confirmation modal
- [frontend-nextjs/src/app/app/page.tsx](frontend-nextjs/src/app/app/page.tsx:760-780) - Send test modal
- E2E Tests: [frontend-nextjs/e2e/journey-5-delivery.spec.ts](frontend-nextjs/e2e/journey-5-delivery.spec.ts)

---

### **Scheduler API** (`backend/api/v1/scheduler.py`)

```python
# Backend endpoints that exist:
POST   /api/v1/scheduler                # Create scheduled job
POST   /api/v1/scheduler/{id}/run-now   # Trigger immediate execution
GET    /api/v1/scheduler/workspaces/{id}   # List schedules
GET    /api/v1/scheduler/{id}           # Get schedule details
DELETE /api/v1/scheduler/{id}           # Delete schedule
PUT    /api/v1/scheduler/{id}           # Update schedule
POST   /api/v1/scheduler/{id}/pause     # Pause schedule
POST   /api/v1/scheduler/{id}/resume    # Resume schedule
```

**Status:** ⚠️ Frontend has `schedulerApi` client - scheduleOnce() implemented, rest partially implemented
**Frontend Implementation:**
- [frontend-nextjs/src/lib/api/scheduler.ts](frontend-nextjs/src/lib/api/scheduler.ts) - All methods implemented
- [frontend-nextjs/src/app/app/page.tsx](frontend-nextjs/src/app/app/page.tsx:789-818) - Schedule send modal uses scheduleOnce()
- Settings page has ScheduleSettings component but not fully connected

---

### **Subscribers API** (`backend/api/v1/subscribers.py`)

```python
# Backend endpoints that exist:
POST   /api/v1/subscribers                        # Add subscriber
POST   /api/v1/subscribers/bulk                   # Bulk import
GET    /api/v1/subscribers/workspaces/{id}        # List subscribers
GET    /api/v1/subscribers/{id}                   # Get subscriber
PUT    /api/v1/subscribers/{id}                   # Update subscriber
DELETE /api/v1/subscribers/{id}                   # Delete subscriber
POST   /api/v1/subscribers/{id}/unsubscribe       # Unsubscribe
GET    /api/v1/subscribers/workspaces/{id}/stats  # Subscriber stats
```

**Status:** ⚠️ Frontend has `subscribersApi` client but NOT used anywhere
**Location:** Settings page has SubscribersSettings component but not connected

---

### **Style API** (`backend/api/v1/style.py`)

```python
# Backend endpoints that exist:
POST /api/v1/style/train                  # Train writing style
GET  /api/v1/style/workspaces/{id}        # Get style profile
PUT  /api/v1/style/workspaces/{id}        # Update style profile
POST /api/v1/style/workspaces/{id}/analyze  # Analyze text samples
```

**Status:** ⚠️ Frontend has `styleApi` client but NOT connected
**Location:** Settings page has StyleSettings component

---

### **Trends API** (`backend/api/v1/trends.py`)

```python
# Backend endpoints that exist:
POST /api/v1/trends/detect                # Detect trends
GET  /api/v1/trends/workspaces/{id}       # List detected trends
GET  /api/v1/trends/workspaces/{id}/config  # Get trend detection config
PUT  /api/v1/trends/workspaces/{id}/config  # Update config
```

**Status:** ⚠️ Frontend has `trendsApi` client but NOT connected
**Location:** Settings page has TrendsSettings component

---

### **Analytics API** (`backend/api/v1/analytics.py`)

```python
# Backend endpoints that exist:
POST /api/v1/analytics/track              # Track event
GET  /api/v1/analytics/workspaces/{id}    # Get workspace analytics
GET  /api/v1/analytics/newsletters/{id}   # Get newsletter analytics
GET  /api/v1/analytics/workspaces/{id}/export  # Export analytics
```

**Status:** ⚠️ Frontend has `analyticsApi` client but NOT connected
**Location:** Settings page has AnalyticsSettings component, History page shows mock data

---

### **Feedback API** (`backend/api/v1/feedback.py`)

```python
# Backend endpoints that exist:
POST /api/v1/feedback                     # Submit feedback
GET  /api/v1/feedback/workspaces/{id}     # List feedback
GET  /api/v1/feedback/content/{id}        # Get content feedback
GET  /api/v1/feedback/workspaces/{id}/stats  # Feedback stats
```

**Status:** ⚠️ Frontend has `feedbackApi` client but NOT connected
**Location:** Settings page has FeedbackSettings component

---

### **Content API - Additional Endpoints**

```python
# These content endpoints exist but are NOT used:
GET /api/v1/content/workspaces/{id}                    # List content items
GET /api/v1/content/workspaces/{id}/sources/{source}   # List by source
```

**Status:** ⚠️ Content listing not implemented in frontend
**Note:** Dashboard only shows stats, not actual content items

---

### **Newsletter API - Additional Endpoints**

```python
# These newsletter endpoints exist but are NOT used:
GET    /api/v1/newsletters/workspaces/{id}/stats  # Newsletter stats
DELETE /api/v1/newsletters/{id}                   # Delete newsletter
POST   /api/v1/newsletters/{id}/regenerate        # Regenerate newsletter
```

**Status:** ⚠️ Newsletter stats, deletion, and regeneration not implemented

---

## Missing Frontend Pages

These features are in user stories but have NO frontend pages:

1. **Content Browser** - Browse and select content items
   - Backend: ✅ `GET /api/v1/content/workspaces/{id}`
   - Frontend: ❌ No page exists
   - User Story: 4.2, 4.3

2. **Newsletter Editor** - Full newsletter editor
   - Backend: ✅ `PUT /api/v1/newsletters/{id}`
   - Frontend: ⚠️ Modal exists but limited
   - User Story: 5.2

3. **Newsletter Analytics** - Detailed analytics view
   - Backend: ✅ `GET /api/v1/analytics/newsletters/{id}`
   - Frontend: ❌ No page, only mock data in history
   - User Story: 9.1, 9.2, 9.3

4. **Subscriber Management Page**
   - Backend: ✅ Full subscriber API
   - Frontend: ❌ No dedicated page
   - User Story: 8.1, 8.2

5. **Schedule Management Page**
   - Backend: ✅ Full scheduler API
   - Frontend: ❌ Settings component only
   - User Story: 7.1, 7.2

6. **Style Training Page**
   - Backend: ✅ Full style API
   - Frontend: ❌ Settings component only
   - User Story: 10.1, 10.2

7. **Trends Dashboard**
   - Backend: ✅ Full trends API
   - Frontend: ❌ Settings component only
   - User Story: 11.1, 11.2

---

## Schema Mismatches

### 1. Workspace Config Schema

**Frontend expects:**
```typescript
{
  sources: Array<{
    type: 'reddit' | 'rss' | 'twitter' | 'youtube',
    enabled: boolean,
    config: {
      // Reddit
      subreddits?: string[],
      time_filter?: string,
      post_limit?: number,

      // RSS
      feeds?: Array<{url: string, name: string}>,

      // Twitter
      accounts?: string[],
      hashtags?: string[],
      tweet_limit?: number
    }
  }>,
  newsletter_settings: {
    max_items: number,
    tone: string,
    language: string
  }
}
```

**Backend provides:**
```python
# Same structure, but may include additional fields
{
  "sources": [...],
  "newsletter_settings": {...},
  "email_settings": {...},      # Additional
  "schedule_settings": {...}     # Additional
}
```

**Status:** ✅ Compatible, frontend ignores extra fields

---

### 2. Newsletter Items Schema

**Frontend expects:**
```typescript
{
  id: string,
  title: string,
  summary: string,
  url: string,
  source: string,  // Display name
  publishedAt?: Date
}
```

**Backend provides:**
```python
{
  "id": "uuid",
  "title": "string",
  "summary": "string",
  "url": "string",
  "source_type": "reddit|rss|blog|x|youtube",  # ← Different field name
  "published_at": "ISO datetime"               # ← Different field name
}
```

**Issue:** ⚠️ Frontend maps `source_type` → `source` and `published_at` → `publishedAt`
**Location:** [frontend-nextjs/src/app/app/page.tsx](frontend-nextjs/src/app/app/page.tsx:602)

---

### 3. Auth Token Field Name

**Frontend expects:** `token`
**Backend returns:** `token`

**Status:** ✅ Compatible

---

### 4. Newsletter Status Values

**Frontend uses:**
- `'draft'`
- `'sent'`
- `'scheduled'`

**Backend uses:**
- `'draft'`
- `'sent'`
- `'scheduled'`
- `'failed'` (additional)

**Status:** ✅ Compatible

---

## Summary Statistics

### Frontend Pages
- ✅ **4 pages implemented**
  - Landing (`/`)
  - Login (`/login`)
  - Register (`/register`)
  - Dashboard (`/app`)
  - Settings (`/app/settings`)
  - History (`/app/history`)

### API Integration Status
- ✅ **Fully Integrated (Working):** 7
  - Authentication
  - Workspaces
  - Content Stats
  - Newsletter Generation
  - Newsletter History
  - Delivery (Send Now, Send Test)
  - Scheduler (Schedule Once)

- ⚠️ **Partially Integrated:** 5
  - Settings (components exist, not all connected)
  - Scheduler (scheduleOnce works, recurring schedules not connected)
  - Subscribers (client exists, not used)
  - Style (client exists, not connected)
  - Trends (client exists, not connected)
  - Analytics (client exists, not connected)
  - Feedback (client exists, not connected)

- ❌ **Not Integrated:** 0
  - All backend APIs have at least stub frontend clients

### Backend Endpoints
- **Total Endpoints:** ~40+
- **Fully Mapped to Frontend:** ~20 (50%)
- **Partially Mapped:** ~8 (20%)
- **Unmapped (No frontend):** ~12 (30%)

---

## Recommendations

### Priority 1 (Critical for MVP)
1. ✅ ~~Connect History Page to backend~~ **COMPLETE**
   - ✅ Replaced mock data with `newslettersApi.list()`
   - ✅ Implemented newsletter view with `newslettersApi.get()`

2. ✅ ~~Implement Delivery API in frontend~~ **COMPLETE (Verified)**
   - ✅ Methods already fully implemented in [frontend-nextjs/src/lib/api/delivery.ts](frontend-nextjs/src/lib/api/delivery.ts)
   - ✅ Send and SendTest modals already connected

3. ✅ ~~Fix Schema Field Mapping~~ **COMPLETE**
   - ✅ Created type transformer utility in [frontend-nextjs/src/lib/utils/type-transformers.ts](frontend-nextjs/src/lib/utils/type-transformers.ts)
   - ✅ Updated ContentItem type to match backend schema
   - ✅ Transformers handle source_type → source, created_at/published_at → publishedAt (Date)
   - ✅ Removed manual field mapping from dashboard and modals

### Priority 2 (Important Features)
4. **Implement Subscriber Management**
   - Create dedicated `/app/subscribers` page
   - Connect to backend subscribers API
   - Add bulk import functionality

5. **Connect Scheduler Settings**
   - Implement schedule creation in settings
   - Connect to `POST /api/v1/scheduler/daily`
   - Show active schedules

6. **Implement Content Browser**
   - Create `/app/content` page
   - Show all scraped content items
   - Allow filtering and selection

### Priority 3 (Advanced Features)
7. **Connect Analytics**
   - Replace mock analytics in history
   - Show real open/click rates
   - Add analytics dashboard

8. **Implement Style Training**
   - Connect style settings to backend
   - Add sample upload functionality
   - Show style profile

9. **Connect Trends Detection**
   - Show detected trends on dashboard
   - Connect trends settings to backend
   - Add trend visualization

10. **Implement Feedback Loop**
    - Add thumbs up/down on content items
    - Connect to feedback API
    - Show learning stats

---

## Files That Need Updates

### High Priority
1. ✅ ~~`frontend-nextjs/src/lib/api/delivery.ts`~~ - Already complete
2. ✅ ~~`frontend-nextjs/src/lib/api/scheduler.ts`~~ - Already complete (scheduleOnce works)
3. ✅ ~~`frontend-nextjs/src/app/app/history/page.tsx`~~ - Already connected to real API
4. ✅ ~~`frontend-nextjs/src/lib/utils/type-transformers.ts`~~ - Type transformers created
5. `frontend-nextjs/src/components/settings/subscribers-settings.tsx` - Connect to backend

### Medium Priority
6. `frontend-nextjs/src/lib/api/analytics.ts` - Implement analytics methods
7. `frontend-nextjs/src/lib/api/subscribers.ts` - Complete subscriber methods
8. `frontend-nextjs/src/components/settings/schedule-settings.tsx` - Connect to backend
9. Create `frontend-nextjs/src/app/app/content/page.tsx` - New content browser page
10. Create `frontend-nextjs/src/app/app/subscribers/page.tsx` - New subscriber management page

### Low Priority
11. `frontend-nextjs/src/lib/api/style.ts` - Implement style methods
12. `frontend-nextjs/src/lib/api/trends.ts` - Implement trends methods
13. `frontend-nextjs/src/lib/api/feedback.ts` - Implement feedback methods
14. `frontend-nextjs/src/components/settings/style-settings.tsx` - Connect to backend
15. `frontend-nextjs/src/components/settings/trends-settings.tsx` - Connect to backend
16. `frontend-nextjs/src/components/settings/feedback-settings.tsx` - Connect to backend

---

**End of Mapping Document**
