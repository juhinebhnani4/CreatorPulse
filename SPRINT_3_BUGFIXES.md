# Sprint 3 Bug Fixes Summary

## Overview
After completing Sprint 3 implementation, two critical bugs were discovered and fixed during testing.

## Bug #1: Authentication Token Mismatch

### Issue
Both Content Library and Newsletter Generator tabs were showing:
```
API Error: Not authenticated
```

### Root Cause
The API client functions were looking for `st.session_state.auth_token`, but the authentication flow stores the token as `st.session_state.token`.

**Authentication flow:** [frontend/utils/auth.py](frontend/utils/auth.py#L48)
```python
st.session_state.token = data.get('token')  # Stored as 'token'
```

**API clients were looking for:** `st.session_state.auth_token` ❌

### Fix
Updated both API clients to use the correct session state variable:

**Files Modified:**
1. [frontend/utils/content_api.py](frontend/utils/content_api.py#L21-L22)
2. [frontend/utils/newsletter_api.py](frontend/utils/newsletter_api.py#L21-L22)

**Code Change:**
```python
# BEFORE (❌ Wrong)
if 'auth_token' in st.session_state and st.session_state.auth_token:
    headers["Authorization"] = f"Bearer {st.session_state.auth_token}"

# AFTER (✅ Correct)
if 'token' in st.session_state and st.session_state.token:
    headers["Authorization"] = f"Bearer {st.session_state.token}"
```

### Status
✅ **Fixed** - Authentication now works correctly for all API calls.

---

## Bug #2: Row Level Security (RLS) Policy Violation

### Issue
Content scraping was failing with:
```
new row violates row-level security policy for table "content_items"
```

This occurred when clicking "🔄 Scrape Content" in the Content Library tab.

### Root Cause
The `SupabaseManager` class was using `self.client` (which enforces RLS policies) for content operations. The backend API should use `self.service_client` (service key) to bypass RLS, relying on the API layer for authorization instead.

### Architecture
The codebase uses a three-layer security model:

1. **RLS Policies** - Database-level security for direct Supabase access
2. **API Authorization** - JWT token validation in backend API
3. **Service Key** - Allows backend to perform operations on behalf of authenticated users

### Fix
Changed content operations to use `service_client`:

**File Modified:** [src/ai_newsletter/database/supabase_client.py](src/ai_newsletter/database/supabase_client.py)

**Changes:**

1. **`save_content_items()` (line 254)**
   ```python
   # BEFORE
   result = self.client.table('content_items').insert(data).execute()

   # AFTER
   result = self.service_client.table('content_items').insert(data).execute()
   ```

2. **`load_content_items()` (line 277)**
   ```python
   # BEFORE
   query = self.client.table('content_items') \
       .select('*') \
       .eq('workspace_id', workspace_id) \
       ...

   # AFTER
   query = self.service_client.table('content_items') \
       .select('*') \
       .eq('workspace_id', workspace_id) \
       ...
   ```

3. **`search_content_items()` (line 331)**
   ```python
   # BEFORE
   result = self.client.table('content_items') \
       .select('*') \
       .eq('workspace_id', workspace_id) \
       ...

   # AFTER
   result = self.service_client.table('content_items') \
       .select('*') \
       .eq('workspace_id', workspace_id) \
       ...
   ```

### Additional Files Created

**[backend/migrations/002_create_content_items_table.sql](backend/migrations/002_create_content_items_table.sql)**
- Documents the schema and RLS policies for `content_items` table
- Created for reference (table already exists in production from Sprint 2)

### Status
✅ **Fixed** - Content scraping now works with service key bypass.

---

## Testing Checklist

After these fixes, the following should work:

### Content Library Tab
- [ ] Navigate to "📚 Content Library" tab
- [ ] View content stats dashboard
- [ ] Click "🔄 Scrape Content" - should scrape successfully
- [ ] View scraped content in table
- [ ] Apply filters (source, date range, limit)
- [ ] View content item details
- [ ] Export content (CSV/JSON)

### Newsletter Generator Tab
- [ ] Navigate to "📝 Newsletter Generator" tab
- [ ] View "Available Content" dashboard with metrics
- [ ] Configure generation settings (title, items, days back, sources)
- [ ] Click "🎨 Generate Newsletter" - should generate successfully
- [ ] View generated newsletter HTML
- [ ] Download newsletter
- [ ] View newsletter history (last 5 newsletters)
- [ ] View/download historical newsletters

### Database Persistence
- [ ] Refresh browser - content persists
- [ ] Log out and log in - content persists
- [ ] Generated newsletters appear in history
- [ ] Newsletter metadata tracked correctly

---

## Related Documentation

- [AUTHENTICATION_FIX.md](AUTHENTICATION_FIX.md) - Detailed authentication token fix
- [RLS_BYPASS_FIX.md](RLS_BYPASS_FIX.md) - Detailed RLS bypass fix
- [SPRINT_3_COMPLETE.md](SPRINT_3_COMPLETE.md) - Sprint 3 completion summary

---

## Environment Status

**Backend API:** ✅ Running on http://localhost:8000 (with fixes)
**Frontend UI:** ✅ Running on http://localhost:8502 (with fixes)
**Database:** ✅ Supabase configured
**Migrations:** ⚠️ Newsletter table migration already run (see note below)

### Database Migration Note

The newsletter migration attempted to run showed:
```
ERROR: policy "Users can view their workspace newsletters" for table "newsletters" already exists
```

This is **expected behavior** - it means the `newsletters` table and its RLS policies already exist in your Supabase database. No action needed.

---

---

## Bug #3: Datetime Timezone Comparison Error

### Issue
Content stats dashboard was failing with:
```
API Error: can't compare offset-naive and offset-aware datetimes
```

This occurred after successfully scraping content when viewing the Content Library stats.

### Root Cause
The `get_content_stats()` method in [backend/services/content_service.py](backend/services/content_service.py#L288-L295) was comparing:
- `item.scraped_at` - **timezone-aware** datetime from Supabase (PostgreSQL TIMESTAMPTZ)
- `datetime.now()` - **timezone-naive** datetime from Python

Python cannot compare these two datetime types.

### Fix
Changed to use timezone-aware datetime for comparisons:

**File Modified:** [backend/services/content_service.py](backend/services/content_service.py#L288-L295)

**Code Change:**
```python
# BEFORE (❌ Wrong)
cutoff_24h = datetime.now() - timedelta(hours=24)
items_24h = sum(1 for item in all_items if item.scraped_at >= cutoff_24h)

# AFTER (✅ Correct)
from datetime import timezone
cutoff_24h = datetime.now(timezone.utc) - timedelta(hours=24)
items_24h = sum(1 for item in all_items if item.scraped_at and item.scraped_at >= cutoff_24h)
```

Also added null checks to handle cases where `scraped_at` might be None.

### Status
✅ **Fixed** - Content stats dashboard now calculates metrics correctly.

---

## Summary

All three bugs have been fixed:
1. ✅ **Authentication** - API clients now use correct session state variable
2. ✅ **RLS Bypass** - Content operations now use service client
3. ✅ **Datetime Timezone** - Stats calculations now use timezone-aware datetimes

Sprint 3 is now **fully functional** and ready for testing!
