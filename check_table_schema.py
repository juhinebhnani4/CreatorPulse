"""Check the users table schema to understand what's expected."""
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_KEY"))

# Try to get schema info by attempting insert with full data
print("Testing users table insert with various UUID formats...")

test_cases = [
    {
        "name": "String UUID",
        "data": {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "email": "schema-test-1@example.com",
            "username": "Schema Test 1"
        }
    },
    {
        "name": "Without created_at",
        "data": {
            "id": "550e8400-e29b-41d4-a716-446655440001",
            "email": "schema-test-2@example.com",
            "username": "Schema Test 2"
        }
    }
]

for test_case in test_cases:
    print(f"\n{test_case['name']}:")
    try:
        response = supabase.table("users").insert(test_case['data']).execute()
        if response.data:
            print(f"  [OK] Insert successful: {response.data}")
            # Clean up
            supabase.table("users").delete().eq("id", test_case['data']['id']).execute()
        else:
            print(f"  [FAIL] No data returned")
    except Exception as e:
        print(f"  [ERROR] {e}")

# Check if table has any required columns we're missing
print("\n\nAttempting to read table structure...")
try:
    response = supabase.table("users").select("*").limit(1).execute()
    if response.data and len(response.data) > 0:
        print("Sample row structure:")
        for key in response.data[0].keys():
            print(f"  - {key}")
    else:
        print("No existing rows to show structure")
except Exception as e:
    print(f"Error: {e}")
