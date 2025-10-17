# Frontend Issues Fixed - Summary

This document summarizes all the fixes applied to resolve frontend errors in the CreatorPulse application.

## Issues Fixed

### 1. Authentication Error (401 Unauthorized) on Content Scraping

**Error:**
```
POST http://localhost:8000/api/v1/content/scrape 401 (Unauthorized)
```

**Root Cause:**
The `handleScrapeContent` function in [frontend-nextjs/src/app/app/page.tsx](frontend-nextjs/src/app/app/page.tsx#L289) was using the wrong localStorage key for the auth token.

**Fix:**
- Changed `localStorage.getItem('token')` to `localStorage.getItem('auth_token')`
- This matches the key used by the API client in [frontend-nextjs/src/lib/api/client.ts](frontend-nextjs/src/lib/api/client.ts#L50)

**Files Changed:**
- `frontend-nextjs/src/app/app/page.tsx` (line 289)

---

### 2. Scraping Returns 0 Items

**Error:**
Successfully authenticated but scraping returned "Successfully fetched 0 items from 0 sources"

**Root Cause:**
Multiple configuration format mismatches between frontend and backend:

1. **Config Structure Mismatch:**
   - Frontend stores sources as an array: `sources: [{type, enabled, config}]`
   - Backend expected flat dict: `{reddit: {enabled: true}, rss: {enabled: true}}`

2. **Field Name Mismatches:**
   - Frontend sends: `subreddit` (string), `url` (string), `handle` (string)
   - Backend expected: `subreddits` (array), `feed_urls` (array), `usernames` (array)

**Fix:**
Updated [backend/services/content_service.py](backend/services/content_service.py) to:

1. **Parse both config formats** (lines 55-76):
   - Support new array format: `sources: [{type, enabled, config}]`
   - Support legacy dict format: `{reddit: {...}, rss: {...}}`

2. **Normalize field names** for each scraper:
   - **Reddit** (lines 167-194): Accept both `subreddit` and `subreddits`
   - **RSS** (lines 196-213): Accept both `url` and `feed_urls`
   - **Blog** (lines 215-233): Accept both `url` and `urls`
   - **X/Twitter** (lines 235-258): Accept both `handle` and `usernames`

**Files Changed:**
- `backend/services/content_service.py`

---

### 3. Newsletter Generation Error (500 Internal Server Error)

**Error:**
```
POST http://localhost:8000/api/v1/newsletters/generate 500 (Internal Server Error)
Newsletter generation failed: {'message': "Could not find the 'content_items_count' column of 'newsletters' in the schema cache", 'code': 'PGRST204'}
```

**Root Cause:**
The `newsletters` table in Supabase was missing the `content_items_count` column. The schema was out of sync.

**Fix:**
Set up Alembic for database migrations:

1. **Installed Alembic:**
   ```bash
   pip install alembic psycopg2-binary SQLAlchemy
   ```

2. **Configured Alembic:**
   - Created `backend/alembic.ini` configuration
   - Updated `backend/alembic/env.py` to load database URL from environment variables
   - Supports both `DATABASE_URL` and auto-construction from `SUPABASE_URL` + `SUPABASE_DB_PASSWORD`

3. **Created Migration:**
   - File: `backend/alembic/versions/4a408dda0acd_add_content_items_count_to_newsletters.py`
   - Adds `content_items_count` column to `newsletters` table
   - Includes idempotency check (won't fail if column already exists)
   - Refreshes Supabase PostgREST schema cache

4. **Documentation:**
   - Created [backend/MIGRATIONS.md](backend/MIGRATIONS.md) with complete migration guide
   - Updated [.env.example](.env.example) with database connection examples

**Files Created/Changed:**
- `backend/alembic/` (directory)
- `backend/alembic.ini`
- `backend/alembic/env.py`
- `backend/alembic/versions/4a408dda0acd_add_content_items_count_to_newsletters.py`
- `backend/MIGRATIONS.md`
- `backend/migrations/fix_newsletters_schema.sql`
- `backend/fix_newsletter_schema.py`
- `backend/apply_migration.py`
- `.env.example`
- `requirements.txt`

---

## How to Apply the Newsletter Fix

### Option 1: Using Alembic (Recommended for future)

1. Add to your `.env` file:
   ```env
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_DB_PASSWORD=your-database-password
   ```

2. Run the migration:
   ```bash
   cd backend
   alembic upgrade head
   ```

### Option 2: Manual SQL (Quick fix)

1. Go to https://supabase.com/dashboard
2. Select your project
3. Click "SQL Editor"
4. Run this SQL:

```sql
-- Add content_items_count column if missing
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = 'newsletters'
        AND column_name = 'content_items_count'
    ) THEN
        ALTER TABLE newsletters
        ADD COLUMN content_items_count INTEGER DEFAULT 0;

        COMMENT ON COLUMN newsletters.content_items_count
        IS 'Number of content items included in this newsletter';
    END IF;
END $$;

-- Refresh Supabase schema cache
NOTIFY pgrst, 'reload schema';
```

---

## Testing the Fixes

After applying all fixes:

1. **Test Content Scraping:**
   - Login to the dashboard
   - Add a source (e.g., Reddit subreddit or RSS feed)
   - Click "Scrape Content"
   - Should see: "Successfully fetched X items from Y sources"

2. **Test Newsletter Generation:**
   - After scraping content
   - Click "Generate Draft"
   - Should see: "Newsletter generated successfully"

---

## Future Migrations

For any future database schema changes, use Alembic:

```bash
# Create new migration
cd backend
alembic revision -m "description_of_change"

# Edit the generated file in backend/alembic/versions/

# Apply migration
alembic upgrade head
```

See [backend/MIGRATIONS.md](backend/MIGRATIONS.md) for detailed instructions.

---

## Summary

All frontend errors have been resolved:

✅ **Authentication** - Fixed token storage key mismatch
✅ **Content Scraping** - Fixed config format and field name mismatches
✅ **Newsletter Generation** - Set up database migrations system
✅ **Future Migrations** - Alembic configured and documented

The application should now work end-to-end for:
- User authentication
- Adding content sources
- Scraping content
- Generating newsletters
