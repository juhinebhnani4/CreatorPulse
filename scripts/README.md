# CreatorPulse Scripts

This directory contains utility scripts for database management, migrations, and maintenance.

## Scripts Overview

### 1. `supabase_schema.sql`

**Purpose:** Creates the complete database schema in Supabase

**Usage:**
1. Open Supabase Dashboard > SQL Editor
2. Copy entire contents of this file
3. Paste into editor
4. Run the query

**What it creates:**
- 9 tables (workspaces, content_items, style_profiles, etc.)
- Row Level Security (RLS) policies for multi-tenant isolation
- Indexes for query optimization
- Foreign key relationships

**When to use:**
- Initial setup of new Supabase project
- Resetting database (⚠️ destroys all data)
- Creating staging/test environments

### 2. `migrate_to_supabase.py`

**Purpose:** Migrates existing data from JSON files to Supabase

**Usage:**

```bash
# Preview migration (dry run)
python scripts/migrate_to_supabase.py \
    --workspace default \
    --user-id YOUR_USER_ID \
    --dry-run

# Migrate single workspace
python scripts/migrate_to_supabase.py \
    --workspace default \
    --user-id YOUR_USER_ID

# Migrate all workspaces
python scripts/migrate_to_supabase.py \
    --all \
    --user-id YOUR_USER_ID
```

**What it migrates:**
- ✅ Workspace configuration (`config.json`)
- ✅ Style profiles (`style_profile.json`)
- ✅ Historical content (`historical_content.json`)
- ✅ Feedback data (`feedback_data.json`)
- ⚠️ Analytics events (planned - implement bulk insert)

**Options:**
- `--workspace NAME` - Migrate specific workspace
- `--user-id UUID` - Owner user ID (required)
- `--dry-run` - Preview without writing to database
- `--all` - Migrate all workspaces in `workspaces/` directory

**Requirements:**
- Supabase credentials in `.env`
- User must exist in Supabase (create via Streamlit or Dashboard)
- Source data in `workspaces/{name}/` directory

## Common Workflows

### Initial Setup

```bash
# 1. Create Supabase project and run schema
#    (in Supabase SQL Editor)

# 2. Create user via Streamlit app or Dashboard

# 3. Get user ID from Dashboard > Authentication > Users

# 4. Migrate existing data
python scripts/migrate_to_supabase.py --all --user-id <USER_ID>
```

### Adding New Environment

```bash
# 1. Create new Supabase project for staging/test

# 2. Update .env with staging credentials

# 3. Run schema
#    (in Supabase SQL Editor: supabase_schema.sql)

# 4. Migrate sample data
python scripts/migrate_to_supabase.py \
    --workspace sample \
    --user-id <USER_ID>
```

### Backup Data

```bash
# Export workspace data from Supabase
# (Use Supabase Dashboard > Database > Backups)
# Or use pg_dump:

pg_dump \
    --host=db.your-project.supabase.co \
    --port=5432 \
    --username=postgres \
    --schema=public \
    --format=custom \
    --file=backup.dump
```

## Getting User ID

### Method 1: Via Supabase Dashboard
1. Open Supabase Dashboard
2. Click **Authentication** in sidebar
3. Click **Users** tab
4. Copy the **ID** column (UUID format)

### Method 2: Via Python
```python
from src.ai_newsletter.database.supabase_client import SupabaseManager
from src.ai_newsletter.auth.auth_manager import AuthManager

supabase = SupabaseManager()
auth = AuthManager(supabase.client)

# Sign in
result = auth.sign_in("user@example.com", "password")
user_id = result['user'].id
print(f"User ID: {user_id}")
```

## Troubleshooting

### Migration fails with "workspace already exists"

The workspace name must be unique. Either:
- Delete existing workspace in Supabase Dashboard
- Rename the workspace in migration script
- Use a different `--workspace` name

### Migration fails with "RLS policy violation"

Ensure you're using the correct user ID that owns the workspace. The user must:
- Exist in `auth.users` table
- Match the `--user-id` parameter
- Have proper permissions

### "No workspaces found" error

Check that:
- `workspaces/` directory exists
- Directory contains workspace folders
- Workspace folders contain JSON files

### Schema changes not reflected

If you modify the schema:
1. Drop all tables in Supabase Dashboard
2. Re-run `supabase_schema.sql`
3. Re-migrate data

⚠️ **Warning:** This destroys all data. Backup first!

## Best Practices

### Before Migration

1. ✅ **Backup source data**
   ```bash
   cp -r workspaces/ workspaces_backup/
   ```

2. ✅ **Run dry-run first**
   ```bash
   python scripts/migrate_to_supabase.py --workspace default --user-id <ID> --dry-run
   ```

3. ✅ **Test with sample workspace** before migrating all data

### During Migration

1. ✅ **Monitor Supabase Dashboard > Logs** for errors
2. ✅ **Watch for RLS policy violations**
3. ✅ **Verify data integrity** after each workspace

### After Migration

1. ✅ **Verify data** in Supabase Dashboard > Table Editor
2. ✅ **Run integration tests**
   ```bash
   pytest tests/integration/test_supabase_integration.py -v
   ```
3. ✅ **Keep original files for 30 days** as backup
4. ✅ **Update application** to use Supabase instead of JSON

## Additional Scripts (Future)

Coming soon:
- `backup_supabase.py` - Automated backup to JSON
- `sync_workspaces.py` - Sync between JSON and Supabase
- `reset_workspace.py` - Reset workspace data
- `export_analytics.py` - Export analytics to CSV

## Support

For issues or questions:
1. Check [SUPABASE_SETUP_GUIDE.md](../SUPABASE_SETUP_GUIDE.md)
2. Review [SUPABASE_INTEGRATION.md](../SUPABASE_INTEGRATION.md)
3. Open an issue on GitHub
