# Datetime Timezone Comparison Fix

## Issue
Content stats endpoint was failing with error:
```
Error loading stats: API Error: can't compare offset-naive and offset-aware datetimes
```

This occurred when viewing the Content Library tab after successfully scraping content.

## Root Cause
In [backend/services/content_service.py](backend/services/content_service.py), the `get_content_stats()` method was comparing:
- `item.scraped_at` - **timezone-aware** datetime from Supabase (PostgreSQL TIMESTAMPTZ)
- `datetime.now()` - **timezone-naive** datetime from Python

Python cannot compare these two types of datetime objects, resulting in a TypeError.

## Technical Details

**PostgreSQL Storage:**
- `content_items.scraped_at` column is `TIMESTAMPTZ` (timestamp with timezone)
- Supabase returns timezone-aware datetime objects

**Python datetime.now():**
- Returns timezone-naive datetime by default
- Must use `datetime.now(timezone.utc)` for timezone-aware datetime

## Fix

**File Modified:** [backend/services/content_service.py](backend/services/content_service.py#L288-L295)

### Before (❌ Broken)
```python
# Items in last 24h
cutoff_24h = datetime.now() - timedelta(hours=24)
items_24h = sum(1 for item in all_items if item.scraped_at >= cutoff_24h)

# Items in last 7d
cutoff_7d = datetime.now() - timedelta(days=7)
items_7d = sum(1 for item in all_items if item.scraped_at >= cutoff_7d)
```

### After (✅ Fixed)
```python
# Items in last 24h (use timezone-aware datetime)
from datetime import timezone
cutoff_24h = datetime.now(timezone.utc) - timedelta(hours=24)
items_24h = sum(1 for item in all_items if item.scraped_at and item.scraped_at >= cutoff_24h)

# Items in last 7d
cutoff_7d = datetime.now(timezone.utc) - timedelta(days=7)
items_7d = sum(1 for item in all_items if item.scraped_at and item.scraped_at >= cutoff_7d)
```

### Changes Made:
1. ✅ Changed `datetime.now()` to `datetime.now(timezone.utc)` for timezone-aware comparison
2. ✅ Added null check (`item.scraped_at and ...`) to handle cases where `scraped_at` might be None
3. ✅ Imported `timezone` from `datetime` module

## Impact

**Content Stats Dashboard now correctly calculates:**
- Total items in workspace
- Items by source (reddit, rss, blog, x, youtube)
- Items scraped in last 24 hours
- Items scraped in last 7 days
- Latest scrape timestamp

## Testing

To verify the fix:
1. Navigate to "📚 Content Library" tab
2. Click "🔄 Scrape Content" to fetch new content
3. Verify stats dashboard shows correct metrics:
   - ✅ Total Items count
   - ✅ Last 24h count
   - ✅ Last 7d count
   - ✅ Source breakdown
4. No error message should appear

## Related Issues

This is the **third bug** discovered during Sprint 3 testing:

1. ✅ **Bug #1:** Authentication token mismatch ([AUTHENTICATION_FIX.md](AUTHENTICATION_FIX.md))
2. ✅ **Bug #2:** RLS policy violation ([RLS_BYPASS_FIX.md](RLS_BYPASS_FIX.md))
3. ✅ **Bug #3:** Datetime timezone comparison (this fix)

## Best Practice

**Always use timezone-aware datetimes when working with database timestamps:**

```python
# ❌ Bad - timezone-naive
now = datetime.now()

# ✅ Good - timezone-aware
now = datetime.now(timezone.utc)
```

This ensures consistent behavior across:
- Database storage (PostgreSQL TIMESTAMPTZ)
- API responses (ISO 8601 with timezone)
- Python datetime comparisons

## Status
✅ **Fixed** - Content stats dashboard now works correctly with timezone-aware datetime comparisons.

## Related Files
- [backend/services/content_service.py](backend/services/content_service.py#L156-L210) - Content stats calculation
- [src/ai_newsletter/database/supabase_client.py](src/ai_newsletter/database/supabase_client.py) - Supabase client
- [frontend/pages/content_library.py](frontend/pages/content_library.py) - Content Library UI
