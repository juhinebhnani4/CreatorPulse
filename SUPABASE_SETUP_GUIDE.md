# Supabase Setup Guide for CreatorPulse

This guide walks you through setting up Supabase for CreatorPulse step-by-step.

## Prerequisites

- A Supabase account (free tier is sufficient)
- Python 3.8+ installed
- Git repository cloned

## Step 1: Create Supabase Project

1. Go to [supabase.com](https://supabase.com) and sign up/login
2. Click **"New Project"**
3. Fill in project details:
   - **Name:** CreatorPulse (or your preferred name)
   - **Database Password:** Generate a strong password (save this!)
   - **Region:** Choose closest to you
   - **Pricing Plan:** Free (sufficient for testing)
4. Click **"Create new project"**
5. Wait 2-3 minutes for project to initialize

## Step 2: Get API Credentials

1. In your Supabase project dashboard, click **Settings** (gear icon) in sidebar
2. Click **API** in the settings menu
3. Copy these values:
   - **Project URL** (e.g., `https://xxxxx.supabase.co`)
   - **anon public key** (starts with `eyJhbGc...`)
   - **service_role key** (starts with `eyJhbGc...`) - Keep this secret!

## Step 3: Update .env File

Open your `.env` file and add/update these lines:

```bash
# Supabase Configuration
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=eyJhbGc...  # anon key from step 2
SUPABASE_SERVICE_KEY=eyJhbGc...  # service_role key from step 2
```

## Step 4: Run Database Migration

1. In Supabase Dashboard, click **SQL Editor** in sidebar
2. Click **"New query"**
3. Open `scripts/supabase_schema.sql` in a text editor
4. Copy the entire contents
5. Paste into the SQL Editor
6. Click **"Run"** (or press Ctrl/Cmd + Enter)
7. Wait for success message: `"CreatorPulse database schema created successfully!"`

**Verify tables created:**
1. Click **Table Editor** in sidebar
2. You should see these tables:
   - workspaces
   - user_workspaces
   - workspace_configs
   - content_items
   - style_profiles
   - trends
   - feedback_items
   - newsletters
   - analytics_events

## Step 5: Install Dependencies

Install the new Supabase dependencies:

```bash
pip install -r requirements.txt
```

This will install:
- `supabase` - Supabase Python client
- `postgrest-py` - PostgreSQL REST API
- `realtime-py` - Real-time subscriptions
- `storage3` - File storage
- `psycopg2-binary` - PostgreSQL adapter
- `python-jose` - JWT handling
- `passlib` - Password hashing

## Step 6: Test Connection

Run the test script to verify everything is working:

```bash
python -c "from src.ai_newsletter.database.supabase_client import SupabaseManager; sm = SupabaseManager(); print('✅ Connected!' if sm.health_check() else '❌ Failed')"
```

You should see: `✅ Connected!`

## Step 7: Create Your First User

There are two ways to create users:

### Option A: Through Streamlit App (Recommended)

1. Run the app: `streamlit run src/streamlit_app.py`
2. You'll see a login page
3. Click the **"Sign Up"** tab
4. Enter email and password (min 6 characters)
5. Check your email for verification link (check spam folder!)
6. Click verification link
7. Return to app and sign in

### Option B: Through Supabase Dashboard

1. In Supabase Dashboard, click **Authentication** in sidebar
2. Click **"Add user"**
3. Select **"Create new user"**
4. Enter email and password
5. Check **"Auto Confirm User"** (for testing)
6. Click **"Create user"**
7. Copy the User ID (UUID)

## Step 8: Create Your First Workspace

After logging in to the Streamlit app:

1. The app will prompt you to create a workspace
2. Enter a name (e.g., "My Newsletter")
3. Optionally add a description
4. Click **"Create Workspace"**

The workspace will be created with default configuration.

## Step 9: Migrate Existing Data (Optional)

If you have existing data in JSON files, migrate it:

```bash
# Dry run first (preview without writing)
python scripts/migrate_to_supabase.py --workspace default --user-id YOUR_USER_ID --dry-run

# Actual migration
python scripts/migrate_to_supabase.py --workspace default --user-id YOUR_USER_ID

# Migrate all workspaces
python scripts/migrate_to_supabase.py --all --user-id YOUR_USER_ID
```

To get your User ID:
1. Go to Supabase Dashboard > Authentication > Users
2. Copy the ID column for your user

## Step 10: Run Integration Tests

Verify everything is working:

```bash
# Make sure pytest is installed
pip install pytest

# Run tests
pytest tests/integration/test_supabase_integration.py -v
```

All tests should pass ✅

## Troubleshooting

### Error: "Supabase credentials not configured"

- Check that `.env` file exists in project root
- Verify `SUPABASE_URL` and `SUPABASE_KEY` are set
- Make sure there are no extra spaces or quotes

### Error: "relation 'workspaces' does not exist"

- You need to run the SQL schema migration (Step 4)
- Go to Supabase Dashboard > SQL Editor
- Run `scripts/supabase_schema.sql`

### Error: "Invalid API key"

- Verify you copied the correct anon key (not service_role key)
- Check for copy/paste errors
- Regenerate keys in Supabase Dashboard > Settings > API

### Tests failing

- Make sure Supabase project is fully initialized (takes 2-3 minutes)
- Verify credentials in `.env`
- Check your internet connection
- Look at Supabase Dashboard > Logs for errors

### Email verification not working

- Check spam/junk folder
- In Supabase Dashboard > Authentication > Settings
- Verify email templates are enabled
- For testing, you can disable email confirmation:
  - Go to Authentication > Policies
  - Temporarily disable email confirmation requirement

## Next Steps

Once setup is complete:

1. ✅ **Start using the app** - `streamlit run src/streamlit_app.py`
2. ✅ **Configure sources** - Add Reddit, RSS, YouTube sources
3. ✅ **Scrape content** - Test content scraping
4. ✅ **Generate newsletter** - Create your first newsletter
5. ✅ **Invite team members** - Add collaborators to workspace (Pro feature)

## Security Best Practices

- ❌ Never commit `.env` to git
- ❌ Never share your `service_role` key
- ✅ Use environment variables for credentials
- ✅ Enable Row Level Security (RLS) - already configured
- ✅ Use `anon` key for client-side operations
- ✅ Use `service_role` key only for server-side admin tasks

## Support

- **Documentation:** [docs.supabase.com](https://docs.supabase.com)
- **Community:** [supabase.com/discord](https://supabase.com/discord)
- **CreatorPulse Issues:** [github.com/your-repo/issues](https://github.com)

---

**✨ Setup Complete! You're ready to build multi-user newsletters with Supabase.**
