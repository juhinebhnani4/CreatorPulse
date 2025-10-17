"""
Verify Supabase database connection and schema status.
"""

import os
import sys
from dotenv import load_dotenv
from supabase import create_client, Client

# Fix encoding for Windows console
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

# Load environment variables
load_dotenv()

def verify_supabase_connection():
    """Test Supabase connection and check schema."""

    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")

    if not supabase_url or not supabase_key:
        print("[ERROR] Supabase credentials not found in .env")
        return False

    print(f"[INFO] Connecting to Supabase: {supabase_url}")

    try:
        # Create Supabase client
        supabase: Client = create_client(supabase_url, supabase_key)

        print("[SUCCESS] Successfully connected to Supabase!")

        # Check if tables exist by trying to query them
        tables_to_check = [
            'workspaces',
            'user_workspaces',
            'workspace_configs',
            'content_items',
            'style_profiles',
            'trends',
            'feedback_items',
            'newsletters',
            'analytics_events'
        ]

        existing_tables = []
        missing_tables = []

        print("\n[INFO] Checking database tables...")
        for table in tables_to_check:
            try:
                # Try to query the table
                response = supabase.table(table).select("*").limit(0).execute()
                existing_tables.append(table)
                print(f"  [OK] {table}")
            except Exception as e:
                missing_tables.append(table)
                error_msg = str(e)
                if "does not exist" in error_msg or "relation" in error_msg:
                    print(f"  [MISSING] {table} (not found)")
                else:
                    print(f"  [WARN] {table} (error: {error_msg[:50]}...)")

        print(f"\n[SUMMARY]")
        print(f"  Existing tables: {len(existing_tables)}/9")
        print(f"  Missing tables: {len(missing_tables)}/9")

        if len(existing_tables) == 9:
            print("\n[SUCCESS] Database schema is fully deployed!")
            return True
        elif len(existing_tables) > 0:
            print(f"\n[WARN] Partial schema deployment detected")
            print(f"   Missing: {', '.join(missing_tables)}")
            return False
        else:
            print("\n[ERROR] Database schema not deployed")
            print("   Need to run: scripts/supabase_schema.sql")
            return False

    except Exception as e:
        print(f"[ERROR] Error connecting to Supabase: {e}")
        return False

if __name__ == "__main__":
    verify_supabase_connection()
