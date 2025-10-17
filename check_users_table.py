"""Check if users table exists in Supabase."""
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_KEY"))

# Try to select from users table
try:
    response = supabase.table("users").select("*").limit(1).execute()
    print(f"[OK] Users table exists. Sample: {response.data if response.data else 'No data'}")
except Exception as e:
    print(f"[FAIL] Users table error: {e}")

# Try to insert a test record
try:
    test_user = {
        "id": "test-user-id-12345",
        "email": "tabletest@example.com",
        "username": "Table Test"
    }
    response = supabase.table("users").insert(test_user).execute()
    print(f"[OK] Insert successful: {response.data}")

    # Clean up
    supabase.table("users").delete().eq("id", "test-user-id-12345").execute()
    print("[OK] Test record cleaned up")
except Exception as e:
    print(f"[FAIL] Insert failed: {e}")
