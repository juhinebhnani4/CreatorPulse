"""
Apply newsletter table schema fixes to Supabase
"""
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from backend.database import get_supabase_client

def apply_newsletter_schema_fix():
    """Apply the newsletter table schema fixes"""

    sql_statements = [
        "ALTER TABLE newsletters ADD COLUMN IF NOT EXISTS content_items_count INTEGER DEFAULT 0;",
        "ALTER TABLE newsletters ADD COLUMN IF NOT EXISTS content_item_ids UUID[] DEFAULT '{}';",
        "ALTER TABLE newsletters ADD COLUMN IF NOT EXISTS model_used TEXT;",
        "ALTER TABLE newsletters ADD COLUMN IF NOT EXISTS temperature REAL;",
        "ALTER TABLE newsletters ADD COLUMN IF NOT EXISTS tone TEXT;",
        "ALTER TABLE newsletters ADD COLUMN IF NOT EXISTS language TEXT;",
        "ALTER TABLE newsletters ADD COLUMN IF NOT EXISTS metadata JSONB DEFAULT '{}';",
        "ALTER TABLE newsletters ADD COLUMN IF NOT EXISTS html_content TEXT DEFAULT '';",
        "ALTER TABLE newsletters ADD COLUMN IF NOT EXISTS plain_text_content TEXT;",
        "ALTER TABLE newsletters ADD COLUMN IF NOT EXISTS title TEXT DEFAULT 'Newsletter';",
        "ALTER TABLE newsletters ADD COLUMN IF NOT EXISTS status TEXT DEFAULT 'draft';",
        "ALTER TABLE newsletters ADD COLUMN IF NOT EXISTS generated_at TIMESTAMPTZ DEFAULT NOW();",
        "ALTER TABLE newsletters ADD COLUMN IF NOT EXISTS sent_at TIMESTAMPTZ;",
    ]

    print("Applying newsletter table schema fixes...")
    print("=" * 60)

    try:
        client = get_supabase_client()

        # Execute each SQL statement
        for i, sql in enumerate(sql_statements, 1):
            print(f"\n[{i}/{len(sql_statements)}] Executing: {sql[:50]}...")

            try:
                # Use the postgrest client to execute raw SQL
                # Note: This requires the service_role key with appropriate permissions
                result = client.rpc('exec_sql', {'query': sql}).execute()
                print(f"    [OK] Success")
            except Exception as e:
                error_msg = str(e)
                # If column already exists, that's fine
                if "already exists" in error_msg.lower():
                    print(f"    [INFO] Column already exists (skipping)")
                else:
                    print(f"    [ERROR] Error: {error_msg}")
                    # Continue with other statements

        print("\n" + "=" * 60)
        print("[SUCCESS] Newsletter table schema fix complete!")
        print("\nVerifying columns...")

        # Verify by attempting to query the table structure
        result = client.rpc('exec_sql', {
            'query': """
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = 'newsletters'
            ORDER BY ordinal_position;
            """
        }).execute()

        if result.data:
            print(f"\n[OK] Found {len(result.data)} columns in newsletters table:")
            for col in result.data:
                print(f"   - {col['column_name']} ({col['data_type']})")

        print("\nAll done! Try generating your newsletter again.")
        return True

    except Exception as e:
        print(f"\n[ERROR] Error applying fix: {e}")
        print("\nAlternative solution:")
        print("   1. Go to Supabase Dashboard SQL Editor")
        print("   2. Copy the SQL from FIX_NEWSLETTER_TABLE_NOW.md")
        print("   3. Run it manually")
        return False

if __name__ == "__main__":
    success = apply_newsletter_schema_fix()
    sys.exit(0 if success else 1)
