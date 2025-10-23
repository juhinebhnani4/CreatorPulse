"""
Apply SQL migration to fix get_style_profile_summary function
"""
import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

# Read migration SQL
with open("backend/migrations/006_fix_style_profile_summary_null.sql", "r") as f:
    sql = f.read()

# Create Supabase client with service role key
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

# Execute migration
print("Applying migration to fix get_style_profile_summary function...")
print("-" * 60)

try:
    # Execute the SQL
    result = supabase.rpc('exec', {'sql': sql}).execute()
    print("✅ Migration applied successfully!")
    print(f"Result: {result.data}")
except Exception as e:
    # Try using postgrest query if rpc fails
    try:
        # Split SQL into statements
        statements = [s.strip() for s in sql.split(';') if s.strip() and not s.strip().startswith('--')]

        for statement in statements:
            if statement:
                print(f"\nExecuting: {statement[:100]}...")
                # Use the postgREST API directly
                response = supabase.postgrest.rpc('query', {'sql': statement}).execute()
                print(f"✅ Statement executed")

        print("\n✅ Migration applied successfully!")
    except Exception as e2:
        print(f"❌ Error applying migration: {e2}")
        print("\nPlease apply the migration manually via Supabase SQL Editor:")
        print("-" * 60)
        print(sql)
        print("-" * 60)
