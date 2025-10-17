# Sprint 3: Newsletter Generation from Workspace Content

## Overview

**Goal:** Generate AI-powered newsletters from workspace content (database, not live scraping)

**Duration:** ~3 hours

**Dependencies:**
- ✅ Sprint 1 Complete (Auth & Workspaces)
- ✅ Sprint 2 Complete (Content Scraping)

---

## Sprint 3 Objectives

### Core Features

1. **Newsletter Generation API**
   - Generate newsletters from workspace content
   - Use existing OpenAI/OpenRouter integration
   - Save generated newsletters to database
   - Support multiple newsletter formats

2. **Newsletter Storage**
   - Store generated newsletters in Supabase
   - Link to workspace_id
   - Track generation metadata (model, prompt, content_items used)
   - Version history

3. **Newsletter Management**
   - List newsletters per workspace
   - Get newsletter details
   - Regenerate newsletters
   - Delete newsletters

4. **Frontend Integration**
   - Newsletter Generator tab (use workspace content, not live scraping)
   - Newsletter history/library
   - Preview newsletters
   - Download newsletters

---

## Database Schema

### Table: `newsletters`

```sql
CREATE TABLE newsletters (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    html_content TEXT NOT NULL,
    plain_text_content TEXT,

    -- Generation metadata
    content_item_ids UUID[] DEFAULT '{}',  -- Array of content_item IDs used
    content_items_count INTEGER DEFAULT 0,
    model_used TEXT,                        -- gpt-4, claude-3-sonnet, etc.
    temperature REAL,
    tone TEXT,
    language TEXT,

    -- Status
    status TEXT DEFAULT 'draft',           -- draft, sent, scheduled
    generated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    sent_at TIMESTAMPTZ,

    -- Metadata
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_newsletters_workspace ON newsletters(workspace_id);
CREATE INDEX idx_newsletters_status ON newsletters(workspace_id, status);
CREATE INDEX idx_newsletters_generated_at ON newsletters(workspace_id, generated_at DESC);

-- RLS Policies
ALTER TABLE newsletters ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their workspace newsletters"
    ON newsletters FOR SELECT
    USING (
        workspace_id IN (
            SELECT workspace_id FROM user_workspaces
            WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "Users can create newsletters in their workspaces"
    ON newsletters FOR INSERT
    WITH CHECK (
        workspace_id IN (
            SELECT workspace_id FROM user_workspaces
            WHERE user_id = auth.uid()
            AND role IN ('owner', 'editor')
        )
    );

CREATE POLICY "Users can update their workspace newsletters"
    ON newsletters FOR UPDATE
    USING (
        workspace_id IN (
            SELECT workspace_id FROM user_workspaces
            WHERE user_id = auth.uid()
            AND role IN ('owner', 'editor')
        )
    );

CREATE POLICY "Users can delete their workspace newsletters"
    ON newsletters FOR DELETE
    USING (
        workspace_id IN (
            SELECT workspace_id FROM user_workspaces
            WHERE user_id = auth.uid()
            AND role = 'owner'
        )
    );
```

---

## Implementation Plan

### Phase 1: Backend API (90 minutes)

#### 1.1 Newsletter Models (15 min)
**File:** `backend/models/newsletter.py`

```python
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class GenerateNewsletterRequest(BaseModel):
    workspace_id: str
    title: str
    max_items: int = Field(default=15, ge=1, le=100)
    days_back: int = Field(default=7, ge=1, le=30)
    sources: Optional[List[str]] = None
    tone: str = Field(default="professional")
    language: str = Field(default="en")
    temperature: float = Field(default=0.7, ge=0.0, le=1.0)
    model: Optional[str] = None
    use_openrouter: bool = False

class NewsletterResponse(BaseModel):
    id: str
    workspace_id: str
    title: str
    html_content: str
    plain_text_content: Optional[str]
    content_items_count: int
    model_used: str
    status: str
    generated_at: datetime

class NewsletterListResponse(BaseModel):
    newsletters: List[NewsletterResponse]
    count: int
    workspace_id: str
```

#### 1.2 Newsletter Service (30 min)
**File:** `backend/services/newsletter_service.py`

**Key Methods:**
- `generate_newsletter()` - Generate from workspace content
- `save_newsletter()` - Save to database
- `list_newsletters()` - List workspace newsletters
- `get_newsletter()` - Get newsletter details
- `delete_newsletter()` - Delete newsletter
- `regenerate_newsletter()` - Regenerate existing newsletter

#### 1.3 Supabase Manager Updates (15 min)
**File:** `src/ai_newsletter/database/supabase_client.py`

Add methods:
- `save_newsletter()`
- `load_newsletters()`
- `get_newsletter()`
- `delete_newsletter()`

#### 1.4 Newsletter API Endpoints (30 min)
**File:** `backend/api/v1/newsletters.py`

**Endpoints:**
```
POST   /api/v1/newsletters/generate
GET    /api/v1/newsletters/workspaces/{workspace_id}
GET    /api/v1/newsletters/{newsletter_id}
DELETE /api/v1/newsletters/{newsletter_id}
POST   /api/v1/newsletters/{newsletter_id}/regenerate
```

---

### Phase 2: Frontend Integration (90 minutes)

#### 2.1 Newsletter API Client (15 min)
**File:** `frontend/utils/newsletter_api.py`

Functions:
- `generate_newsletter()`
- `list_newsletters()`
- `get_newsletter()`
- `delete_newsletter()`
- `regenerate_newsletter()`

#### 2.2 Update Newsletter Generator Tab (45 min)
**File:** Update existing `src/streamlit_app.py` newsletter_generator_tab()

**Changes:**
- Use workspace content (from database) instead of live scraping
- Show available content count before generation
- Add newsletter history section
- Preview generated newsletters
- Save to database
- Show generation metadata

#### 2.3 Newsletter Library Component (30 min)
**File:** `frontend/pages/newsletter_library.py` (new tab)

Features:
- List all workspace newsletters
- Filter by status (draft, sent, scheduled)
- Preview newsletters
- Download HTML
- Delete newsletters
- Regenerate newsletters

---

### Phase 3: Testing & Integration (30 minutes)

#### 3.1 Backend Testing
- Test newsletter generation API
- Verify database storage
- Test newsletter listing
- Test regeneration

#### 3.2 Frontend Testing
- Generate newsletter from UI
- Verify it saves to database
- Test newsletter library
- Test regeneration

#### 3.3 End-to-End Testing
- Scrape content → Generate newsletter → Save → View in library

---

## API Specification

### Generate Newsletter

```http
POST /api/v1/newsletters/generate
Authorization: Bearer <token>
Content-Type: application/json

{
  "workspace_id": "uuid",
  "title": "Weekly AI Digest",
  "max_items": 15,
  "days_back": 7,
  "sources": ["reddit", "rss"],  // optional
  "tone": "professional",
  "language": "en",
  "temperature": 0.7,
  "use_openrouter": false
}

Response: 201 Created
{
  "success": true,
  "data": {
    "id": "uuid",
    "workspace_id": "uuid",
    "title": "Weekly AI Digest",
    "html_content": "<html>...</html>",
    "content_items_count": 15,
    "model_used": "gpt-4-turbo",
    "status": "draft",
    "generated_at": "2025-01-16T..."
  }
}
```

### List Newsletters

```http
GET /api/v1/newsletters/workspaces/{workspace_id}?status=draft&limit=20
Authorization: Bearer <token>

Response: 200 OK
{
  "success": true,
  "data": {
    "newsletters": [...],
    "count": 5,
    "workspace_id": "uuid"
  }
}
```

### Get Newsletter

```http
GET /api/v1/newsletters/{newsletter_id}
Authorization: Bearer <token>

Response: 200 OK
{
  "success": true,
  "data": {
    "id": "uuid",
    "title": "...",
    "html_content": "...",
    ...
  }
}
```

### Delete Newsletter

```http
DELETE /api/v1/newsletters/{newsletter_id}
Authorization: Bearer <token>

Response: 200 OK
{
  "success": true,
  "data": {
    "message": "Newsletter deleted successfully"
  }
}
```

---

## Frontend Flow

### Newsletter Generator Tab (Updated)

```
┌─────────────────────────────────────────────────────────┐
│  📝 Newsletter Generator                                 │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  📊 Available Content                                    │
│  ┌────────────────────────────────────────────────┐    │
│  │  Reddit: 45 items                               │    │
│  │  RSS: 23 items                                  │    │
│  │  Blog: 12 items                                 │    │
│  │  Total: 80 items (last 7 days)                 │    │
│  └────────────────────────────────────────────────┘    │
│                                                          │
│  ⚙️ Newsletter Settings                                  │
│  Title: [Weekly AI Digest - Jan 16, 2025]              │
│  Max items: [15] ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━        │
│  Days back: [7] ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━         │
│  Sources: ☑ Reddit ☑ RSS ☑ Blog                        │
│  Tone: [Professional ▼]                                 │
│  Model: [GPT-4 Turbo ▼]                                 │
│                                                          │
│  [🎨 Generate Newsletter]                               │
│                                                          │
│  📄 Preview                                              │
│  [Newsletter HTML Preview Here]                         │
│                                                          │
│  💾 [Save Newsletter] 📥 [Download HTML]                │
│                                                          │
│  📚 Recent Newsletters                                   │
│  ┌────────────────────────────────────────────────┐    │
│  │ • Weekly AI Digest - Jan 16 (15 items) [View]  │    │
│  │ • Weekly AI Digest - Jan 9 (12 items) [View]   │    │
│  │ • Weekly AI Digest - Jan 2 (18 items) [View]   │    │
│  └────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

### Newsletter Library Tab (New)

```
┌─────────────────────────────────────────────────────────┐
│  📚 Newsletter Library                                   │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  📊 Statistics                                           │
│  Total: 25  |  Drafts: 15  |  Sent: 10                 │
│                                                          │
│  🔍 Filters                                              │
│  Status: [All ▼]  Date: [Last 30 days ▼]               │
│                                                          │
│  📋 Newsletters                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │ Title                  | Items | Date    | Status│   │
│  ├────────────────────────────────────────────────┤    │
│  │ Weekly AI Digest       | 15    | Jan 16  | Draft │   │
│  │ Weekly AI Digest       | 12    | Jan 9   | Sent  │   │
│  │ Monthly Summary        | 45    | Jan 1   | Draft │   │
│  └────────────────────────────────────────────────┘    │
│                                                          │
│  🔍 Newsletter Details                                   │
│  ┌────────────────────────────────────────────────┐    │
│  │ Title: Weekly AI Digest - Jan 16               │    │
│  │ Generated: 2025-01-16 10:30 AM                 │    │
│  │ Model: GPT-4 Turbo                             │    │
│  │ Items: 15 (Reddit: 8, RSS: 5, Blog: 2)        │    │
│  │ Status: Draft                                   │    │
│  │                                                 │    │
│  │ [👁️ Preview] [📥 Download] [🔄 Regenerate]     │    │
│  │ [📧 Send] [🗑️ Delete]                           │    │
│  └────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

---

## Key Design Decisions

### ✅ Use Workspace Content (Not Live Scraping)
- Newsletter Generator uses content from database
- Content Library provides the content pool
- No need to scrape every time you generate newsletter
- Faster generation

### ✅ Save Newsletters to Database
- Newsletters persist in database
- Can regenerate later with different settings
- Newsletter history for analytics
- Support for versioning

### ✅ Flexible Generation
- Select date range (1-30 days)
- Filter by sources
- Override workspace config
- Custom tone, language, model

### ✅ Newsletter Status Tracking
- Draft: Generated but not sent
- Sent: Sent via email
- Scheduled: Scheduled for future sending

---

## Testing Checklist

### Backend:
- [ ] Generate newsletter API works
- [ ] Newsletter saves to database with workspace_id
- [ ] List newsletters filtered by workspace
- [ ] Get newsletter returns full content
- [ ] Delete newsletter removes from database
- [ ] Regenerate creates new version

### Frontend:
- [ ] Newsletter Generator shows available content count
- [ ] Generate button creates newsletter
- [ ] Newsletter preview displays correctly
- [ ] Save button stores to database
- [ ] Newsletter Library lists all newsletters
- [ ] Can view, download, regenerate, delete newsletters

### Database:
- [ ] Newsletters table exists
- [ ] RLS policies enforce isolation
- [ ] content_item_ids array populated correctly
- [ ] Metadata stored properly

---

## Success Metrics

- ✅ Generate newsletter from workspace content (not live scraping)
- ✅ Save newsletter to database
- ✅ View newsletter history in library
- ✅ Regenerate newsletters with different settings
- ✅ Download newsletters as HTML
- ✅ Preview newsletters in UI

---

## Sprint 3 Deliverables

### Backend:
1. `backend/models/newsletter.py` - API models
2. `backend/services/newsletter_service.py` - Business logic
3. `backend/api/v1/newsletters.py` - REST endpoints
4. Update `src/ai_newsletter/database/supabase_client.py` - DB methods

### Frontend:
1. `frontend/utils/newsletter_api.py` - API client
2. Update `src/streamlit_app.py` - Newsletter Generator tab
3. `frontend/pages/newsletter_library.py` - Newsletter Library tab (new)

### Database:
1. SQL migration script for `newsletters` table
2. RLS policies setup

### Documentation:
1. `SPRINT_3_NEWSLETTER_GENERATION.md` - This file
2. `SPRINT_3_COMPLETE.md` - Completion summary (after sprint)

---

## Dependencies

### Python Packages (Already Installed):
- ✅ openai
- ✅ supabase
- ✅ pydantic
- ✅ fastapi

### Existing Components:
- ✅ NewsletterGenerator class (src/ai_newsletter/generators/)
- ✅ SupabaseManager (src/ai_newsletter/database/)
- ✅ ContentItem model
- ✅ OpenAI/OpenRouter integration

---

## Sprint 3 Timeline

**Total Duration: ~3 hours**

| Phase | Task | Duration | Status |
|-------|------|----------|--------|
| 1.1 | Newsletter Models | 15 min | ⏳ Pending |
| 1.2 | Newsletter Service | 30 min | ⏳ Pending |
| 1.3 | Supabase Updates | 15 min | ⏳ Pending |
| 1.4 | Newsletter API Endpoints | 30 min | ⏳ Pending |
| 2.1 | Newsletter API Client | 15 min | ⏳ Pending |
| 2.2 | Update Generator Tab | 45 min | ⏳ Pending |
| 2.3 | Newsletter Library Tab | 30 min | ⏳ Pending |
| 3.1 | Backend Testing | 10 min | ⏳ Pending |
| 3.2 | Frontend Testing | 10 min | ⏳ Pending |
| 3.3 | End-to-End Testing | 10 min | ⏳ Pending |

---

## Ready to Start!

Sprint 3 is fully planned and ready to execute. Let's build newsletter generation! 🚀
