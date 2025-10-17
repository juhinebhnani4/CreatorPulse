# Sprint 2: Content Scraping - Implementation Complete

## Status: ✅ Backend Complete, Frontend Integration Pending

---

## What Was Built

### 1. Backend API (✅ Complete)

#### Content Models (`backend/models/content.py`)
- `ScrapeContentRequest` - Request schema for scraping content
- `ContentItemResponse` - Content item response schema
- `ContentListResponse` - List content items response
- `ContentStatsResponse` - Content statistics response
- `ScrapeJobResponse` - Scrape job status response

#### Content Service (`backend/services/content_service.py`)
Core business logic for content management:

**Key Methods:**
- `scrape_content()` - Scrape content from configured sources
- `list_content()` - List content items with filtering
- `get_content_stats()` - Get content statistics
- `_scrape_source()` - Source-specific scraping logic
  - Reddit scraping
  - RSS feed scraping
  - Blog scraping with smart extraction
  - X (Twitter) scraping

**Features:**
- Workspace isolation (all content scoped to workspace_id)
- Uses existing scrapers (no modifications needed!)
- Stores content in Supabase via `SupabaseManager.save_content_items()`
- Error handling per source (one source failing doesn't break others)

#### Content API Endpoints (`backend/api/v1/content.py`)

**Endpoints:**
1. `POST /api/v1/content/scrape`
   - Scrape content for a workspace
   - Returns: Scrape results with items count per source

2. `GET /api/v1/content/workspaces/{workspace_id}`
   - List content items for workspace
   - Query params: `days`, `source`, `limit`
   - Returns: List of content items

3. `GET /api/v1/content/workspaces/{workspace_id}/stats`
   - Get content statistics
   - Returns: Total items, items by source, recent activity

4. `GET /api/v1/content/workspaces/{workspace_id}/sources/{source}`
   - List content items for specific source
   - Query params: `days`, `limit`
   - Returns: Filtered content items

**All endpoints require JWT authentication** (`Authorization: Bearer <token>`)

#### Main App Integration
- Updated `backend/main.py` to include content router
- Content endpoints now available at: `http://localhost:8000/api/v1/content/*`

---

## How It Works

### Content Scraping Flow

```
1. User -> POST /api/v1/content/scrape
   {
     "workspace_id": "xxx",
     "sources": ["reddit", "rss"],  // optional
     "limit_per_source": 10          // optional
   }

2. Backend:
   - Gets workspace config from database
   - Determines which sources to scrape (all enabled or specified)
   - Calls respective scrapers (RedditScraper, RSSFeedScraper, etc.)
   - Scrapers return List[ContentItem] (no workspace_id needed!)
   - Service saves items to database with workspace_id

3. Database:
   - Items stored in content_items table
   - Automatically scoped to workspace_id
   - RLS policies ensure user only sees their workspace data

4. Response:
   {
     "workspace_id": "xxx",
     "total_items": 25,
     "items_by_source": {
       "reddit": 15,
       "rss": 10
     },
     "scraped_at": "2025-01-16T..."
   }
```

### Content Retrieval Flow

```
1. User -> GET /api/v1/content/workspaces/{id}?days=7&source=reddit

2. Backend:
   - Calls SupabaseManager.load_content_items()
   - Filters by workspace_id, days, source
   - Returns List[ContentItem]

3. Response:
   {
     "workspace_id": "xxx",
     "count": 15,
     "items": [
       {
         "id": "...",
         "title": "...",
         "source": "reddit",
         "summary": "...",
         ...
       }
     ],
     "filters": { "days": 7, "source": "reddit" }
   }
```

---

## Frontend Integration (Next Step)

### Option 1: Add New "Content Library" Tab

Create a new tab in Streamlit that shows workspace content:

**Features:**
- Display scraped content from database (not just live scraping)
- Source filters (Reddit, RSS, Blog, X)
- Date range filters
- Search functionality
- Export to CSV
- Scrape new content button

**Implementation:**
```python
# Add to streamlit_app.py tabs
from utils.content_api import (
    scrape_workspace_content,
    list_workspace_content,
    get_workspace_content_stats
)

def content_library_tab():
    st.subheader("📚 Content Library")

    workspace = get_current_workspace()
    workspace_id = workspace['id']

    # Stats
    stats = get_workspace_content_stats(workspace_id)
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Items", stats['total_items'])
    col2.metric("Last 24h", stats['items_last_24h'])
    col3.metric("Last 7d", stats['items_last_7d'])

    # Filters
    source_filter = st.selectbox("Source", ["all", "reddit", "rss", "blog", "x"])
    days_filter = st.slider("Days", 1, 30, 7)

    # List content
    content = list_workspace_content(
        workspace_id,
        days=days_filter,
        source=None if source_filter == "all" else source_filter
    )

    # Display table
    df = pd.DataFrame(content['items'])
    st.dataframe(df)

    # Scrape button
    if st.button("🔄 Scrape New Content"):
        result = scrape_workspace_content(workspace_id)
        st.success(f"Scraped {result['total_items']} items!")
```

### Option 2: Integrate with Existing Tab

Modify the existing "Content Scraper" tab to:
1. Load historical content from database first
2. Show stats on cached content
3. Allow scraping new content
4. Combine with existing live scraping features

---

## Testing

### Test Content Scraping

```bash
# Start backend
cd backend
python main.py

# Test scrape endpoint
curl -X POST http://localhost:8000/api/v1/content/scrape \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "workspace_id": "your-workspace-id",
    "sources": ["reddit", "rss"],
    "limit_per_source": 5
  }'
```

### Test Content Listing

```bash
# List all content
curl http://localhost:8000/api/v1/content/workspaces/<workspace_id>?days=7 \
  -H "Authorization: Bearer <your_token>"

# Get stats
curl http://localhost:8000/api/v1/content/workspaces/<workspace_id>/stats \
  -H "Authorization: Bearer <your_token>"

# Filter by source
curl http://localhost:8000/api/v1/content/workspaces/<workspace_id>/sources/reddit \
  -H "Authorization: Bearer <your_token>"
```

---

## Database Schema

The existing `content_items` table in Supabase handles everything:

```sql
CREATE TABLE content_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    source TEXT NOT NULL,  -- reddit, rss, blog, x, youtube
    source_url TEXT NOT NULL,
    content TEXT,
    summary TEXT,
    author TEXT,
    author_url TEXT,
    score INTEGER DEFAULT 0,
    comments_count INTEGER DEFAULT 0,
    shares_count INTEGER DEFAULT 0,
    views_count INTEGER DEFAULT 0,
    image_url TEXT,
    video_url TEXT,
    external_url TEXT,
    tags TEXT[],
    category TEXT,
    created_at TIMESTAMPTZ NOT NULL,  -- Original content creation time
    scraped_at TIMESTAMPTZ NOT NULL,  -- When we scraped it
    metadata JSONB DEFAULT '{}',
    UNIQUE(workspace_id, source_url)  -- Prevent duplicates
);

-- Indexes for performance
CREATE INDEX idx_content_workspace ON content_items(workspace_id);
CREATE INDEX idx_content_source ON content_items(workspace_id, source);
CREATE INDEX idx_content_created_at ON content_items(workspace_id, created_at DESC);
CREATE INDEX idx_content_scraped_at ON content_items(workspace_id, scraped_at DESC);

-- RLS policies already set up (Sprint 1)
```

---

## Key Design Decisions

### ✅ No Scraper Modifications Needed
- Scrapers return `List[ContentItem]` (no workspace awareness)
- Service layer adds `workspace_id` when saving to database
- Clean separation of concerns

### ✅ Workspace Isolation
- All content queries filtered by `workspace_id`
- RLS policies enforce security at database level
- Users can only see their own workspace content

### ✅ Flexible Scraping
- Scrape all enabled sources or specify subset
- Override limits per source
- Per-source error handling (resilient)

### ✅ Content Caching
- Content stored in database (not ephemeral)
- Can be queried later without re-scraping
- Supports analytics and trend detection

---

## Next Steps

1. **Frontend Integration** (20 minutes)
   - Add "Content Library" tab to Streamlit
   - Use `content_api.py` utility functions
   - Display content, filters, stats

2. **Testing** (15 minutes)
   - Test scraping from Streamlit
   - Verify content appears in database
   - Test filtering and stats

3. **Sprint 3 Planning**
   - Newsletter generation from workspace content
   - Style profiles per workspace
   - Scheduled scraping

---

## Files Created/Modified

### New Files:
- `backend/models/content.py` - Content API models
- `backend/services/content_service.py` - Content business logic
- `backend/api/v1/content.py` - Content API endpoints
- `frontend/utils/content_api.py` - Frontend API client

### Modified Files:
- `backend/main.py` - Added content router

### No Changes Needed:
- All scrapers remain unchanged ✅
- SupabaseManager already has needed methods ✅
- ContentItem model already complete ✅

---

## API Documentation

Full API docs available at: `http://localhost:8000/docs` (when backend running)

**Base URL:** `http://localhost:8000/api/v1`

**Authentication:** All endpoints require `Authorization: Bearer <jwt_token>`

**Endpoints:**
- `POST /content/scrape` - Scrape new content
- `GET /content/workspaces/{id}` - List content
- `GET /content/workspaces/{id}/stats` - Get stats
- `GET /content/workspaces/{id}/sources/{source}` - Filter by source

---

## Success Criteria

✅ Backend API endpoints functional
✅ Content scraping stores to database with workspace_id
✅ Content retrieval filters by workspace
✅ No scraper modifications needed
⏳ Frontend integration pending
⏳ End-to-end testing pending

**Sprint 2 Status: 80% Complete (Backend Done, Frontend Next)**
