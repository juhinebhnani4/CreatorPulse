# How to Apply Database Migration - Step by Step Guide

Since Supabase MCP is not available in your environment, here are your options to fix the `content_items_count` column issue:

---

## ✅ OPTION 1: Manual SQL in Supabase Dashboard (Recommended - Fastest)

This is the quickest and most reliable method:

### Steps:

1. **Open Supabase Dashboard**
   - Go to: https://supabase.com/dashboard
   - Select your project

2. **Open SQL Editor**
   - Click "SQL Editor" in the left sidebar
   - Click "New query"

3. **Copy and Paste This SQL**:
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

4. **Click "Run"**

5. **Verify Success**
   You should see: "Success. No rows returned"

6. **Test in Frontend**
   - Go back to your CreatorPulse app
   - Try clicking "Generate Draft" again
   - Should work now!

---

## ✅ OPTION 2: Using Alembic (For Future Migrations)

If you want to use the proper migration system:

### Setup (One-time):

1. **Get Your Supabase Database Password**
   - Go to Supabase Dashboard → Settings → Database
   - Under "Connection string", find your password
   - Or under "Database password", click "Reset" if needed

2. **Add to .env File** (create one if it doesn't exist):
   ```env
   # Your existing credentials
   SUPABASE_URL=https://amwyvhvgrdnncujoudrj.supabase.co
   SUPABASE_KEY=your-anon-key
   SUPABASE_SERVICE_KEY=your-service-key

   # Add this line (replace with your actual password):
   SUPABASE_DB_PASSWORD=your-database-password
   ```

3. **Run Migration**:
   ```bash
   # From project root
   cd backend
   ..\\.venv\\Scripts\\alembic.exe upgrade head
   ```

   Or use the helper script:
   ```bash
   python backend/run_migrations.py
   ```

### Troubleshooting:

If you get connection errors:
- Make sure your IP is whitelisted in Supabase (Settings → Database → Connection pooling)
- Verify the password is correct
- Check that you're using the database password, not the API key

---

## ✅ OPTION 3: Using Python Script Directly

If Alembic doesn't work, use this standalone script:

1. **Update .env with database credentials** (same as Option 2)

2. **Run**:
   ```bash
   python backend/apply_migration.py
   ```

This will:
- Connect directly to your database
- Run the SQL migration
- Refresh the schema cache

---

## 🔍 How to Verify the Fix Was Applied

After applying any of the above options:

### Method 1: Check in Supabase Dashboard
1. Go to Supabase Dashboard → Table Editor
2. Click on "newsletters" table
3. Verify you see a column named "content_items_count"

### Method 2: Test in Frontend
1. Go to your CreatorPulse app
2. Login
3. Add a content source (if you haven't already)
4. Click "Scrape Content"
5. Click "Generate Draft"
6. Should work without the 500 error!

---

## 📋 Quick Reference

**What the migration does:**
- Adds `content_items_count` column to `newsletters` table
- Sets default value to 0
- Adds comment explaining the column's purpose
- Refreshes Supabase PostgREST cache

**Why it's needed:**
- The backend code expects this column when creating newsletters
- Without it, you get: "Could not find the 'content_items_count' column"

**Files to reference:**
- SQL: `backend/migrations/fix_newsletters_schema.sql`
- Alembic migration: `backend/alembic/versions/4a408dda0acd_add_content_items_count_to_newsletters.py`
- Documentation: `backend/MIGRATIONS.md`

---

## ⚡ TL;DR - Fastest Fix

1. Go to: https://supabase.com/dashboard
2. Your project → SQL Editor → New query
3. Paste the SQL from Option 1 above
4. Click Run
5. Test in your app - should work!

---

## Need Help?

If none of these work:
1. Check if the column already exists (might have been added manually)
2. Verify your Supabase project URL is correct
3. Make sure you have database admin permissions
4. Check the browser console for any new errors after the "fix"
