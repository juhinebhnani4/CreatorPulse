"""
Script to run the create_users_table.sql migration.
This creates the public.users table in Supabase.
"""

import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

from supabase import create_client

def run_migration():
    """Run the users table migration."""

    # Get Supabase credentials
    url = os.getenv("SUPABASE_URL")
    service_key = os.getenv("SUPABASE_SERVICE_KEY")

    if not url or not service_key:
        print("❌ Error: SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in .env")
        return False

    print(f"🔗 Connecting to Supabase: {url}")

    try:
        # Create service client (needs service key for admin operations)
        supabase = create_client(url, service_key)

        # Read migration file
        migration_file = Path(__file__).parent / "migrations" / "create_users_table.sql"

        if not migration_file.exists():
            print(f"❌ Error: Migration file not found: {migration_file}")
            return False

        print(f"📄 Reading migration: {migration_file}")
        sql = migration_file.read_text()

        # Execute SQL
        print("🚀 Executing migration...")

        # Split SQL into individual statements and execute
        statements = [s.strip() for s in sql.split(';') if s.strip() and not s.strip().startswith('--')]

        for i, statement in enumerate(statements, 1):
            if not statement:
                continue

            print(f"  [{i}/{len(statements)}] Executing statement...")

            try:
                # Execute via RPC or direct SQL
                result = supabase.rpc('exec_sql', {'sql': statement}).execute()
                print(f"  ✅ Statement {i} executed")
            except Exception as e:
                # If RPC doesn't exist, try using PostgREST
                error_msg = str(e).lower()
                if 'function' in error_msg and 'does not exist' in error_msg:
                    print("  ⚠️  Note: exec_sql RPC not available, migration must be run manually in Supabase SQL editor")
                    print("\n" + "="*80)
                    print("MANUAL MIGRATION REQUIRED")
                    print("="*80)
                    print("\n1. Go to your Supabase project dashboard")
                    print("2. Navigate to SQL Editor")
                    print("3. Copy and paste the contents of:")
                    print(f"   {migration_file}")
                    print("4. Click 'Run' to execute the SQL")
                    print("\nMigration SQL:")
                    print("-" * 80)
                    print(sql)
                    print("-" * 80)
                    return False
                else:
                    raise

        print("\n✅ Migration completed successfully!")
        print("\nThe public.users table has been created with:")
        print("  - UUID primary key referencing auth.users")
        print("  - email and username columns")
        print("  - Row Level Security (RLS) enabled")
        print("  - Policies for user access and service role")

        return True

    except Exception as e:
        print(f"\n❌ Migration failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("="*80)
    print("CREATE PUBLIC.USERS TABLE MIGRATION")
    print("="*80)
    print()

    success = run_migration()

    if not success:
        sys.exit(1)

    print("\n" + "="*80)
    print("NEXT STEPS")
    print("="*80)
    print("\n1. Re-run the backend tests:")
    print("   cd backend")
    print("   python -m pytest tests/ -v")
    print("\n2. All tests should now pass!")
