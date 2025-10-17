# Database Migrations with Alembic

This project uses [Alembic](https://alembic.sqlalchemy.org/) for database schema migrations.

## Setup

1. **Install dependencies** (already done if you ran `pip install -r requirements.txt`):
   ```bash
   pip install alembic psycopg2-binary
   ```

2. **Configure database connection**:

   Add to your `.env` file (choose one method):

   **Method 1: Direct DATABASE_URL**
   ```env
   DATABASE_URL=postgresql://postgres:your-password@db.xxx.supabase.co:5432/postgres
   ```

   **Method 2: Supabase credentials (auto-constructs URL)**
   ```env
   SUPABASE_URL=https://xxx.supabase.co
   SUPABASE_DB_PASSWORD=your-database-password
   ```

   To get your Supabase database password:
   - Go to https://supabase.com/dashboard
   - Select your project
   - Settings → Database → Connection string
   - Copy the password from the connection string

## Common Migration Commands

### Run pending migrations
```bash
cd backend
alembic upgrade head
```

### Create a new migration
```bash
cd backend
alembic revision -m "description_of_change"
```

### Downgrade to previous version
```bash
cd backend
alembic downgrade -1
```

### Show current migration version
```bash
cd backend
alembic current
```

### Show migration history
```bash
cd backend
alembic history
```

## Quick Fix for Current Issue

To fix the missing `content_items_count` column:

```bash
cd backend
alembic upgrade head
```

This will apply the migration `4a408dda0acd_add_content_items_count_to_newsletters.py`

## Creating New Migrations

1. **Create migration file**:
   ```bash
   alembic revision -m "your_migration_description"
   ```

2. **Edit the generated file** in `backend/alembic/versions/`:
   ```python
   def upgrade() -> None:
       """Add your schema changes here."""
       op.add_column('table_name',
           sa.Column('column_name', sa.String(255), nullable=True)
       )

   def downgrade() -> None:
       """Revert your schema changes here."""
       op.drop_column('table_name', 'column_name')
   ```

3. **Apply the migration**:
   ```bash
   alembic upgrade head
   ```

## Migration Best Practices

1. **Always test migrations** in development first
2. **Make migrations reversible** (implement both `upgrade()` and `downgrade()`)
3. **Keep migrations small** - one logical change per migration
4. **Never edit applied migrations** - create a new migration instead
5. **Add schema cache refresh** for Supabase:
   ```python
   op.execute("NOTIFY pgrst, 'reload schema'")
   ```

## Troubleshooting

### "Column already exists" error
The migration is idempotent - it checks if the column exists before adding it. However, if you get this error, you can:

1. **Mark migration as applied without running it**:
   ```bash
   alembic stamp head
   ```

2. **Or apply the SQL manually** in Supabase dashboard and then stamp:
   ```bash
   alembic stamp head
   ```

### Connection errors
- Verify your DATABASE_URL or SUPABASE credentials in `.env`
- Check your IP is whitelisted in Supabase (Settings → Database → Connection pooling)
- Ensure you're using the correct database password

### Schema cache not refreshing in Supabase
If changes don't appear immediately in PostgREST API:
1. Wait a few seconds
2. Manually reload: Settings → API → Reload schema cache
3. Or execute: `NOTIFY pgrst, 'reload schema'` in SQL Editor

## Files

- `alembic.ini` - Alembic configuration
- `alembic/env.py` - Environment setup (loads .env variables)
- `alembic/versions/` - Migration files
- `MIGRATIONS.md` - This file
