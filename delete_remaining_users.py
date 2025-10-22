"""
Script to delete remaining Supabase Auth users with foreign key constraints
We'll use admin endpoint which should handle cascading deletes
"""
import requests
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

# Remaining user IDs that failed
user_ids = [
    "b01ca18a-05bc-407b-a230-f0a2dc9df274",  # amit.d789@gmail.com
    "e64a9795-5397-4984-80c8-ea9016edef0f",  # nebhnanijuhi@gmail.com
    "967f58b9-c136-427b-97f7-211abf34e2d5",  # user-1760649952-4482@example.com
    "b164cd12-4f09-4af2-a52d-efc2ce772230",  # ssbrightaccessories@gmail.com
    "b8b30a2e-5fff-4553-8e38-fc7c1cb974f7",  # juhinebhnani4@gmail.com
]

def delete_user_with_cascade(user_id):
    """Delete a user using admin endpoint with should_soft_delete=false"""
    url = f"{SUPABASE_URL}/auth/v1/admin/users/{user_id}"
    headers = {
        "apikey": SUPABASE_SERVICE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
        "Content-Type": "application/json"
    }

    # Try with should_soft_delete parameter
    params = {"should_soft_delete": "false"}
    response = requests.delete(url, headers=headers, params=params)
    return response.status_code, response.text

def main():
    print(f"Attempting to delete {len(user_ids)} remaining users with cascade...")

    deleted = 0
    failed = 0
    failed_users = []

    for user_id in user_ids:
        status_code, response_text = delete_user_with_cascade(user_id)

        if status_code in [200, 204]:
            deleted += 1
            print(f"[OK] Deleted user: {user_id}")
        else:
            failed += 1
            failed_users.append((user_id, status_code, response_text))
            print(f"[FAIL] Failed to delete user {user_id}: {status_code}")

    print(f"\n--- Summary ---")
    print(f"Successfully deleted: {deleted}")
    print(f"Failed: {failed}")

    if failed_users:
        print("\nFailed users details:")
        for user_id, status_code, response_text in failed_users:
            print(f"  User: {user_id}")
            print(f"  Status: {status_code}")
            print(f"  Error: {response_text[:200]}")
            print()

if __name__ == "__main__":
    main()
