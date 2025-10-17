"""
Helper script to run migration 009 on Supabase.
This script reads the SQL file and executes it using the Supabase client.
"""

import os
import sys
from pathlib import Path

# Try to import required packages
try:
    from supabase import create_client, Client
except ImportError:
    print("ERROR: supabase package not installed")
    print("Install it with: pip install supabase")
    sys.exit(1)

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("WARNING: python-dotenv not installed, using environment variables")
    pass

def get_db_connection_string():
    """Extract PostgreSQL connection string from Supabase URL."""
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_SERVICE_KEY') or os.getenv('SUPABASE_KEY')

    if not supabase_url or not supabase_key:
        print("ERROR: SUPABASE_URL and SUPABASE_KEY must be set in .env")
        return None, None

    # Extract project reference from URL
    # Format: https://PROJECT_REF.supabase.co
    project_ref = supabase_url.split('//')[1].split('.')[0]

    # Construct database connection details
    # Note: You'll need the database password from Supabase dashboard
    db_host = f"db.{project_ref}.supabase.co"
    db_port = "5432"
    db_name = "postgres"
    db_user = "postgres"

    return {
        'host': db_host,
        'port': db_port,
        'database': db_name,
        'user': db_user,
        'project_ref': project_ref
    }, supabase_key

def run_migration_with_psql(db_info):
    """Run migration using psql command."""
    migration_file = "backend/migrations/009_create_analytics_tables.sql"

    if not Path(migration_file).exists():
        print(f"ERROR: Migration file not found: {migration_file}")
        return False

    print("="*70)
    print("MIGRATION 009: Analytics Tables")
    print("="*70)
    print()
    print("To run this migration, you need your Supabase database password.")
    print("Find it in: Supabase Dashboard > Settings > Database > Connection String")
    print()
    print("Then run this command:")
    print()
    print(f"psql -h {db_info['host']} \\")
    print(f"     -p {db_info['port']} \\")
    print(f"     -U {db_info['user']} \\")
    print(f"     -d {db_info['database']} \\")
    print(f"     -f {migration_file}")
    print()
    print("Or use this connection string format:")
    print(f"psql 'postgresql://{db_info['user']}:YOUR_PASSWORD@{db_info['host']}:{db_info['port']}/{db_info['database']}' -f {migration_file}")
    print()
    return True

def run_migration_with_supabase_client():
    """Attempt to run migration using Supabase client (may have limitations)."""
    migration_file = Path("backend/migrations/009_create_analytics_tables.sql")

    if not migration_file.exists():
        print(f"ERROR: Migration file not found: {migration_file}")
        return False

    print("="*70)
    print("Running Migration 009 via Supabase Client")
    print("="*70)
    print()

    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_SERVICE_KEY') or os.getenv('SUPABASE_KEY')

    if not supabase_url or not supabase_key:
        print("ERROR: SUPABASE_URL and SUPABASE_KEY must be set in .env")
        return False

    try:
        # Create Supabase client
        supabase: Client = create_client(supabase_url, supabase_key)
        print(f"✓ Connected to Supabase: {supabase_url}")

        # Read migration file
        with open(migration_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()

        print(f"✓ Loaded migration file ({len(sql_content)} characters)")
        print()
        print("Note: The Supabase Python client doesn't support running raw SQL.")
        print("You need to either:")
        print("1. Use the Supabase SQL Editor (Dashboard > SQL Editor)")
        print("2. Use psql command line tool")
        print("3. Use the Supabase API with service role key")
        print()

        # Try to check if tables already exist
        print("Checking if analytics tables already exist...")
        try:
            result = supabase.table("email_analytics_events").select("id").limit(1).execute()
            print("✓ Table 'email_analytics_events' already exists!")

            result = supabase.table("newsletter_analytics_summary").select("id").limit(1).execute()
            print("✓ Table 'newsletter_analytics_summary' already exists!")

            result = supabase.table("content_performance").select("id").limit(1).execute()
            print("✓ Table 'content_performance' already exists!")

            print()
            print("✓ All analytics tables exist! Migration may have already been run.")
            return True

        except Exception as e:
            print(f"✗ Tables don't exist yet: {str(e)}")
            print()
            return False

    except Exception as e:
        print(f"ERROR: {str(e)}")
        return False

def print_migration_options():
    """Print all available options for running the migration."""
    print("="*70)
    print("MIGRATION 009: How to Run")
    print("="*70)
    print()
    print("Choose one of these methods:")
    print()
    print("METHOD 1: Supabase Dashboard (Easiest)")
    print("-" * 70)
    print("1. Go to https://supabase.com/dashboard")
    print("2. Select your project")
    print("3. Click 'SQL Editor' in the left sidebar")
    print("4. Click 'New Query'")
    print("5. Copy and paste the entire content of:")
    print("   backend/migrations/009_create_analytics_tables.sql")
    print("6. Click 'Run' at the bottom")
    print()

    print("METHOD 2: psql Command Line")
    print("-" * 70)
    db_info, _ = get_db_connection_string()
    if db_info:
        print("Install psql if you don't have it:")
        print("  - Windows: https://www.postgresql.org/download/windows/")
        print("  - Mac: brew install postgresql")
        print("  - Linux: sudo apt install postgresql-client")
        print()
        print("Then run:")
        print(f"psql -h {db_info['host']} -U {db_info['user']} -d {db_info['database']} \\")
        print(f"     -f backend/migrations/009_create_analytics_tables.sql")
        print()
        print("When prompted, enter your database password from:")
        print("Supabase Dashboard > Settings > Database > Database Password")
    print()

    print("METHOD 3: Python Script with Direct SQL Execution")
    print("-" * 70)
    print("If you have the supabase-py library with RPC support:")
    print("python run_migration_directly.py")
    print()

    print("="*70)

def main():
    """Main entry point."""
    print()
    print("="*70)
    print("SPRINT 8: Analytics Tables Migration Helper")
    print("="*70)
    print()

    # Check if migration file exists
    migration_file = Path("backend/migrations/009_create_analytics_tables.sql")
    if not migration_file.exists():
        print(f"ERROR: Migration file not found: {migration_file}")
        print("Make sure you're running this from the project root directory.")
        sys.exit(1)

    print(f"✓ Migration file found: {migration_file}")
    print(f"  Size: {migration_file.stat().st_size:,} bytes")
    print()

    # Try to check if tables already exist
    print("Checking if migration has already been run...")
    print()

    if run_migration_with_supabase_client():
        print()
        print("="*70)
        print("✓ SUCCESS: Analytics tables are already set up!")
        print("="*70)
        print()
        print("You can now:")
        print("1. Start the backend server: python -m uvicorn backend.main:app --reload")
        print("2. Test the analytics endpoints")
        print("3. Check the test results in SPRINT_8_TEST_RESULTS.md")
        return

    # If tables don't exist, show migration options
    print_migration_options()

    print("RECOMMENDED: Use Method 1 (Supabase Dashboard) for easiest setup.")
    print()

if __name__ == "__main__":
    main()
