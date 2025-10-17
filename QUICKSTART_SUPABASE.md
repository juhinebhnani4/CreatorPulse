# Supabase Integration - Quick Start Guide

Get your CreatorPulse app connected to Supabase in 10 minutes!

## Prerequisites

- Supabase account (sign up at [supabase.com](https://supabase.com))
- Python 3.8+
- CreatorPulse repository cloned

---

## 5-Step Setup

### 1️⃣ Install Dependencies (1 min)

```bash
pip install -r requirements.txt
```

This installs Supabase client and related packages.

### 2️⃣ Create Supabase Project (2 min)

1. Go to [supabase.com/dashboard](https://supabase.com/dashboard)
2. Click **"New Project"**
3. Fill in:
   - Name: `CreatorPulse`
   - Database Password: (generate strong password)
   - Region: (closest to you)
4. Click **"Create"**
5. Wait 2-3 minutes for initialization

### 3️⃣ Get API Credentials (1 min)

1. In your project dashboard, go to **Settings** > **API**
2. Copy these values:
   ```
   Project URL: https://xxxxx.supabase.co
   anon public: eyJhbGc...
   service_role: eyJhbGc...
   ```

### 4️⃣ Update .env File (1 min)

Add to your `.env` file:

```bash
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=eyJhbGc...  # Paste anon public key
SUPABASE_SERVICE_KEY=eyJhbGc...  # Paste service_role key
```

### 5️⃣ Run Database Schema (2 min)

1. Open Supabase Dashboard > **SQL Editor**
2. Click **"New query"**
3. Copy entire contents of `scripts/supabase_schema.sql`
4. Paste into editor
5. Click **"Run"** (or Ctrl/Cmd + Enter)
6. ✅ Success message should appear

---

## Verify Setup

### Test Connection

```bash
python -c "from src.ai_newsletter.database.supabase_client import SupabaseManager; sm = SupabaseManager(); print('✅ Connected!' if sm.health_check() else '❌ Failed')"
```

Expected output: `✅ Connected!`

### Run Tests

```bash
pip install pytest
pytest tests/integration/test_supabase_integration.py -v
```

Expected: All tests pass ✅

---

## Create Your First User & Workspace

### Option A: Via Streamlit (Recommended)

```bash
streamlit run src/streamlit_app.py
```

1. Click **"Sign Up"** tab
2. Enter email + password (min 6 chars)
3. Check email for verification
4. Return and sign in
5. Create your first workspace

### Option B: Via Supabase Dashboard

1. Go to **Authentication** > **Users**
2. Click **"Add user"** > **"Create new user"**
3. Enter email + password
4. Check **"Auto Confirm User"**
5. Click **"Create"**
6. Copy the User ID (you'll need this)

---

## Migrate Existing Data (Optional)

If you have data in JSON files:

```bash
# Get your User ID from Dashboard > Authentication > Users
USER_ID="paste-user-id-here"

# Dry run first (preview)
python scripts/migrate_to_supabase.py \
    --workspace default \
    --user-id $USER_ID \
    --dry-run

# Actual migration
python scripts/migrate_to_supabase.py \
    --workspace default \
    --user-id $USER_ID
```

---

## Troubleshooting

### ❌ "Supabase credentials not configured"

**Fix:** Check `.env` file has `SUPABASE_URL` and `SUPABASE_KEY` set

### ❌ "relation 'workspaces' does not exist"

**Fix:** Run the SQL schema (Step 5 above)

### ❌ Connection timeout

**Fix:**
- Check internet connection
- Verify Supabase project is fully initialized (takes 2-3 min)
- Check project status in Supabase Dashboard

### ❌ Tests failing

**Fix:**
- Ensure schema was run successfully
- Verify credentials in `.env`
- Check Supabase Dashboard > Logs for errors

---

## What's Next?

### ✅ You now have:
- Multi-user database ready
- Authentication system configured
- Row-level security enabled
- Team collaboration support
- Scalable infrastructure

### 🚀 Start Using:

1. **Test the integration:**
   ```python
   from src.ai_newsletter.database.supabase_client import SupabaseManager

   supabase = SupabaseManager()
   workspace = supabase.create_workspace("My Newsletter", "Test workspace")
   print(f"Created: {workspace['name']}")
   ```

2. **Update scrapers** to save to Supabase instead of JSON
3. **Update Streamlit app** with authentication UI
4. **Invite team members** to collaborate

---

## Resources

- 📖 **Detailed Setup:** [SUPABASE_SETUP_GUIDE.md](SUPABASE_SETUP_GUIDE.md)
- 🏗️ **Architecture:** [SUPABASE_INTEGRATION.md](SUPABASE_INTEGRATION.md)
- 🛠️ **Scripts:** [scripts/README.md](scripts/README.md)
- ✅ **Sprint Summary:** [SPRINT_0_COMPLETE.md](SPRINT_0_COMPLETE.md)

- 🌐 **Supabase Docs:** [docs.supabase.com](https://docs.supabase.com)
- 💬 **Discord:** [supabase.com/discord](https://supabase.com/discord)

---

## Need Help?

1. Check [SUPABASE_SETUP_GUIDE.md](SUPABASE_SETUP_GUIDE.md) for detailed troubleshooting
2. Review Supabase Dashboard > Logs
3. Open an issue on GitHub

---

**🎉 You're ready to build scalable, multi-user newsletters!**

Total setup time: **~10 minutes**
