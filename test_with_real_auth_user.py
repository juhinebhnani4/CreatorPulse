"""Test inserting with a real auth user ID."""
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_KEY"))

# Get a real auth user we created earlier
email = "finaltest99@example.com"

print(f"Finding auth user: {email}")
auth_response = supabase.auth.admin.list_users()
matching_users = [u for u in auth_response if u.email == email]

if not matching_users:
    print("[FAIL] Auth user not found")
    exit(1)

auth_user = matching_users[0]
print(f"[OK] Found auth user:")
print(f"  - ID: {auth_user.id}")
print(f"  - Type: {type(auth_user.id)}")
print(f"  - Email: {auth_user.email}")

# Now try to insert into public.users with this real ID
print(f"\nAttempting to insert into public.users with auth user ID...")

try:
    user_data = {
        "id": str(auth_user.id),
        "email": str(auth_user.email),
        "username": "Final Test"
    }

    print(f"Data to insert: {user_data}")

    response = supabase.table("users").insert(user_data).execute()

    if response.data:
        print(f"[SUCCESS] User inserted into public.users!")
        print(f"  Data: {response.data}")
    else:
        print(f"[FAIL] No data returned")
        print(f"  Response: {response}")

except Exception as e:
    print(f"[ERROR] Insert failed: {e}")

# Verify
print("\nVerifying in public.users...")
check = supabase.table("users").select("*").eq("email", email).execute()
if check.data:
    print(f"[OK] User now exists in public.users: {check.data}")
else:
    print(f"[FAIL] User still not in public.users")
