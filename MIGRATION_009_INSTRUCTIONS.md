# How to Run Migration 009: Analytics Tables

**Migration File:** `backend/migrations/009_create_analytics_tables.sql`

---

## ✅ EASIEST METHOD: Supabase Dashboard (Recommended)

This is the simplest way to run the migration:

### Steps:

1. **Open Supabase Dashboard**
   - Go to: https://supabase.com/dashboard
   - Login and select your project

2. **Open SQL Editor**
   - Click **"SQL Editor"** in the left sidebar
   - Click **"+ New Query"** button

3. **Copy Migration SQL**
   - Open the file: `backend/migrations/009_create_analytics_tables.sql`
   - Copy ALL the content (650 lines)

4. **Paste and Run**
   - Paste into the SQL Editor
   - Click **"Run"** button at the bottom
   - Wait for completion (should take 2-5 seconds)

5. **Verify Success**
   You should see messages like:
   ```
   NOTICE: Email analytics events table created successfully (empty)
   NOTICE: Newsletter analytics summary table created successfully (empty)
   NOTICE: Content performance table created successfully (empty)

   status: "Migration 009 completed: analytics and email tracking tables created"
   ```

6. **Check Tables Were Created**
   - Go to **"Table Editor"** in the left sidebar
   - You should see 3 new tables:
     - `email_analytics_events`
     - `newsletter_analytics_summary`
     - `content_performance`

---

## Alternative Method 1: psql Command Line

If you have `psql` installed:

### Your Connection Details:

```bash
Host: db.amwyvhvgrdnncujoudrj.supabase.co
Port: 5432
Database: postgres
User: postgres
Password: [Get from Supabase Dashboard > Settings > Database]
```

### Command:

```bash
psql -h db.amwyvhvgrdnncujoudrj.supabase.co \
     -p 5432 \
     -U postgres \
     -d postgres \
     -f backend/migrations/009_create_analytics_tables.sql
```

When prompted, enter your database password.

### Get Your Database Password:

1. Go to Supabase Dashboard
2. Click **Settings** > **Database**
3. Under **"Connection string"**, click **"Reset database password"** if you don't have it
4. Copy the password

---

## Alternative Method 2: Connection String Format

```bash
psql "postgresql://postgres:YOUR_PASSWORD@db.amwyvhvgrdnncujoudrj.supabase.co:5432/postgres" \
     -f backend/migrations/009_create_analytics_tables.sql
```

Replace `YOUR_PASSWORD` with your database password.

---

## Alternative Method 3: Install psql (if not installed)

### Windows:
1. Download PostgreSQL from: https://www.postgresql.org/download/windows/
2. Install (you only need the command-line tools)
3. Add to PATH: `C:\Program Files\PostgreSQL\16\bin`

### Mac:
```bash
brew install postgresql
```

### Linux:
```bash
sudo apt install postgresql-client
```

---

## After Running the Migration

### Verify It Worked:

Run this SQL query in Supabase SQL Editor:

```sql
-- Check if tables exist
SELECT table_name
FROM information_schema.tables
WHERE table_name IN (
    'email_analytics_events',
    'newsletter_analytics_summary',
    'content_performance'
);
```

You should see 3 rows returned.

### Test Table Structure:

```sql
-- Check email_analytics_events table
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'email_analytics_events'
ORDER BY ordinal_position;
```

---

## Troubleshooting

### Error: "relation already exists"

This means the tables are already created. You're good to go!

### Error: "permission denied"

Make sure you're using the `postgres` user or a user with CREATE TABLE permissions.

### Error: "syntax error"

Make sure you copied the ENTIRE SQL file. It's 650 lines and includes multiple statements.

### Connection timeout

Check your internet connection and Supabase project status.

---

## What the Migration Creates

### Tables:

1. **email_analytics_events** (17 columns)
   - Stores every tracking event (sent, opened, clicked, bounced, etc.)
   - Includes user agent, IP, device type, location
   - Privacy-compliant (IP anonymization)

2. **newsletter_analytics_summary** (22 columns)
   - Pre-calculated metrics per newsletter
   - Open rates, click rates, engagement scores
   - Automatically updated by triggers

3. **content_performance** (12 columns)
   - Tracks performance of individual content items
   - Times included, clicked, engagement score
   - Used for content recommendations

### Also Creates:

- **21 Indexes** for fast queries
- **12 RLS Policies** for security
- **4 Triggers** for automatic updates
- **4 Utility Functions** for maintenance

---

## Next Steps After Migration

Once the migration is complete:

1. **Start the backend server:**
   ```bash
   cd backend
   python -m uvicorn backend.main:app --reload --port 8000
   ```

2. **Verify API is working:**
   ```bash
   curl http://localhost:8000/health
   ```

3. **Check analytics endpoints are available:**
   ```bash
   curl http://localhost:8000/docs
   ```
   Look for the "Analytics" and "Tracking" sections

4. **Run the structure test:**
   ```bash
   python test_sprint8_structure.py
   ```

5. **Review the complete documentation:**
   - [SPRINT_8_COMPLETE.md](SPRINT_8_COMPLETE.md) - Implementation details
   - [SPRINT_8_TEST_RESULTS.md](SPRINT_8_TEST_RESULTS.md) - Test results

---

## Need Help?

If you encounter any issues:

1. Check the Supabase logs: Dashboard > Logs
2. Verify your connection details are correct
3. Make sure you have the database password
4. Try the Supabase Dashboard method (easiest)

---

**Recommended:** Use the **Supabase Dashboard** method. It's the easiest and most reliable way to run migrations.
