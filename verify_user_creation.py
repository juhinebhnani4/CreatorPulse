"""Quick script to verify user was created in Supabase."""
import os
from dotenv import load_dotenv
from supabase import create_client

# Load environment
load_dotenv()

supabase_url = os.getenv("SUPABASE_URL")
supabase_service_key = os.getenv("SUPABASE_SERVICE_KEY")

if not supabase_url or not supabase_service_key:
    print("❌ Missing Supabase credentials")
    exit(1)

# Create service client
supabase = create_client(supabase_url, supabase_service_key)

# Check users table
print("Checking users table...")
response = supabase.table("users").select("*").eq("email", "verify@test.com").execute()

if response.data:
    print(f"[OK] User found in users table: {response.data}")
else:
    print("[FAIL] User NOT found in users table")
    print(f"Response: {response}")

# Check Supabase Auth
print("\nChecking Supabase Auth...")
auth_response = supabase.auth.admin.list_users()

matching_users = [u for u in auth_response if u.email == "verify@test.com"]
if matching_users:
    print(f"[OK] User found in Supabase Auth: {matching_users[0].email} (ID: {matching_users[0].id})")
else:
    print("[FAIL] User NOT found in Supabase Auth")
