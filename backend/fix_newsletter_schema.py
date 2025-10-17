"""
Fix newsletter schema - Add missing content_items_count column
"""
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ai_newsletter.database.supabase_client import SupabaseManager
import requests

def fix_schema():
    """Add missing content_items_count column to newsletters table."""
    print("Connecting to Supabase...")

    # Get Supabase credentials from environment
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_SERVICE_KEY') or os.getenv('SUPABASE_KEY')

    if not supabase_url or not supabase_key:
        print("✗ Error: SUPABASE_URL and SUPABASE_SERVICE_KEY environment variables required")
        print("\nPlease set them in your .env file:")
        print("  SUPABASE_URL=https://your-project.supabase.co")
        print("  SUPABASE_SERVICE_KEY=your-service-role-key")
        return False

    print(f"Supabase URL: {supabase_url}")

    # Read the SQL fix script
    sql_file = Path(__file__).parent / "migrations" / "fix_newsletters_schema.sql"
    with open(sql_file, 'r') as f:
        sql_content = f.read()

    print("\n" + "="*60)
    print("SQL TO APPLY:")
    print("="*60)
    print(sql_content)
    print("="*60)

    print("\nMANUAL STEPS REQUIRED:")
    print("="*60)
    print("The Supabase Python client doesn't support direct SQL execution.")
    print("Please follow these steps:\n")
    print("1. Go to: https://supabase.com/dashboard")
    print("2. Select your project")
    print("3. Click 'SQL Editor' in the left sidebar")
    print("4. Click 'New query'")
    print("5. Copy and paste the SQL shown above")
    print("6. Click 'Run' to execute\n")
    print("="*60)

    # Try to verify if the column exists using PostgREST
    print("\nChecking current table schema...")
    try:
        supabase = SupabaseManager()
        result = supabase.client.table('newsletters').select('*').limit(1).execute()

        if result.data and len(result.data) > 0:
            columns = list(result.data[0].keys())
            print(f"\nCurrent columns in newsletters table: {columns}")

            if 'content_items_count' in columns:
                print("✓ Column 'content_items_count' already exists!")
                return True
            else:
                print("✗ Column 'content_items_count' is MISSING")
                print("   Please apply the SQL migration above.")
        else:
            print("No data in newsletters table yet (table may be empty)")

    except Exception as e:
        print(f"Could not verify schema: {e}")

    return False

if __name__ == '__main__':
    success = fix_schema()
    if not success:
        print("\n" + "="*60)
        print("NEXT STEPS:")
        print("="*60)
        print("After applying the SQL in Supabase dashboard, run:")
        print("  python backend/fix_newsletter_schema.py")
        print("to verify the fix was applied successfully.")
        print("="*60)
    sys.exit(0 if success else 1)
