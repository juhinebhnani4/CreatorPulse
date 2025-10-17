"""
Run scheduler migration (005_create_scheduler_tables.sql) programmatically.
"""

import os
from pathlib import Path
from supabase import create_client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def run_migration():
    """Run the scheduler migration."""
    # Get Supabase credentials
    url = os.getenv("SUPABASE_URL")
    service_key = os.getenv("SUPABASE_SERVICE_KEY")

    if not url or not service_key:
        print("❌ Error: SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in .env")
        return False

    # Create client with service key (admin access)
    client = create_client(url, service_key)

    # Read migration file
    migration_file = Path(__file__).parent.parent / "backend" / "migrations" / "005_create_scheduler_tables.sql"

    if not migration_file.exists():
        print(f"❌ Error: Migration file not found: {migration_file}")
        return False

    print(f"📖 Reading migration: {migration_file}")
    migration_sql = migration_file.read_text()

    # Execute migration
    print("🚀 Executing migration...")
    try:
        # Split on semicolons and execute each statement
        statements = [s.strip() for s in migration_sql.split(';') if s.strip()]

        for i, statement in enumerate(statements, 1):
            if statement:
                print(f"  Executing statement {i}/{len(statements)}...")
                # Use rpc to execute raw SQL
                result = client.rpc('exec_sql', {'sql': statement}).execute()

    except Exception as e:
        print(f"❌ Error executing migration: {e}")
        print("\n⚠️  Manual migration required:")
        print("1. Open Supabase SQL Editor: https://supabase.com/dashboard/project/YOUR_PROJECT/sql")
        print(f"2. Copy contents of: {migration_file}")
        print("3. Paste and execute in SQL Editor")
        return False

    print("✅ Migration completed successfully!")

    # Verify tables were created
    print("\n🔍 Verifying tables...")
    try:
        result = client.table('scheduler_jobs').select('id').limit(1).execute()
        print("  ✅ scheduler_jobs table exists")

        result = client.table('scheduler_executions').select('id').limit(1).execute()
        print("  ✅ scheduler_executions table exists")

    except Exception as e:
        print(f"  ⚠️  Verification warning: {e}")
        print("  Tables may not exist. Please run migration manually in Supabase SQL Editor.")
        return False

    return True

if __name__ == "__main__":
    print("=" * 60)
    print("Scheduler Migration Script")
    print("=" * 60)
    print()

    success = run_migration()

    if not success:
        print("\n" + "=" * 60)
        print("❌ Migration failed - manual intervention required")
        print("=" * 60)
        exit(1)
    else:
        print("\n" + "=" * 60)
        print("✅ All done! Scheduler tables are ready.")
        print("=" * 60)
        exit(0)
