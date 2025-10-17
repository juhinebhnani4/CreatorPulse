"""Verify the fix worked - check both tables."""
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_KEY"))

email = "configfix@test.com"

# Check public.users table
print(f"Checking public.users table for {email}...")
response = supabase.table("users").select("*").eq("email", email).execute()

if response.data:
    user = response.data[0]
    print(f"[OK] User found in public.users!")
    print(f"  - ID: {user['id']}")
    print(f"  - Email: {user['email']}")
    print(f"  - Username: {user['username']}")
else:
    print("[FAIL] User NOT in public.users")

# Check Supabase Auth
print(f"\nChecking Supabase Auth for {email}...")
auth_response = supabase.auth.admin.list_users()
matching_users = [u for u in auth_response if u.email == email]

if matching_users:
    print(f"[OK] User found in Supabase Auth!")
    print(f"  - ID: {matching_users[0].id}")
    print(f"  - Email: {matching_users[0].email}")
else:
    print("[FAIL] User NOT in Supabase Auth")

# Summary
print("\n" + "="*50)
if response.data and matching_users:
    print("[SUCCESS] User exists in BOTH tables - Fix works!")
else:
    print("[FAIL] User missing from one or both tables")
