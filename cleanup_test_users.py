"""
Cleanup Script - Delete All Test Users and Associated Data
This script will:
1. Delete all test users (test_*, test_phase1_*, etc.)
2. Cascade delete all associated data (workspaces, newsletters, content, etc.)
3. Keep only real user accounts
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

# Initialize Supabase client with service role (bypasses RLS)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

# Real users to keep (not test accounts)
KEEP_USERS = [
    "juhinebhnani4@gmail.com",
    "ssbrightaccessories@gmail.com",
    "jyoti_nebhnani@yahoo.co.in",
]

def get_all_users():
    """Fetch all users from Supabase Auth"""
    try:
        # Using REST API to get users
        response = supabase.auth.admin.list_users()
        return response
    except Exception as e:
        print(f"Error fetching users: {e}")
        return []

def delete_user_data(user_id: str, email: str):
    """Delete all data associated with a user"""
    print(f"\n  Deleting data for user: {email} ({user_id})")

    try:
        # 1. Get user's workspaces first
        workspaces_query = supabase.table('workspaces').select('id').eq('owner_id', user_id).execute()
        workspace_ids = [ws['id'] for ws in workspaces_query.data] if workspaces_query.data else []

        if workspace_ids:
            print(f"    [INFO] Found {len(workspace_ids)} workspaces")

            # Delete newsletters for each workspace (will cascade to analytics, feedback)
            total_newsletters = 0
            for ws_id in workspace_ids:
                newsletters_result = supabase.table('newsletters').delete().eq('workspace_id', ws_id).execute()
                count = len(newsletters_result.data) if newsletters_result.data else 0
                total_newsletters += count
            print(f"    [OK] Deleted {total_newsletters} newsletters")

            # Delete content items for each workspace
            total_content = 0
            for ws_id in workspace_ids:
                content_result = supabase.table('content_items').delete().eq('workspace_id', ws_id).execute()
                count = len(content_result.data) if content_result.data else 0
                total_content += count
            print(f"    [OK] Deleted {total_content} content items")

        # 2. Delete workspaces (will cascade to workspace_config)
        workspaces_result = supabase.table('workspaces').delete().eq('owner_id', user_id).execute()
        print(f"    [OK] Deleted {len(workspaces_result.data) if workspaces_result.data else 0} workspaces")

        # 3. Delete style profiles
        try:
            style_result = supabase.table('style_profiles').delete().eq('user_id', user_id).execute()
            print(f"    [OK] Deleted {len(style_result.data) if style_result.data else 0} style profiles")
        except:
            pass  # Table might not exist yet

        # 4. Delete scheduled jobs
        try:
            jobs_result = supabase.table('scheduled_jobs').delete().eq('user_id', user_id).execute()
            print(f"    [OK] Deleted {len(jobs_result.data) if jobs_result.data else 0} scheduled jobs")
        except:
            pass  # Table might not exist yet

        # 5. Delete the user from auth
        supabase.auth.admin.delete_user(user_id)
        print(f"    [OK] Deleted user from auth")

        return True

    except Exception as e:
        print(f"    [ERROR] Error deleting user data: {e}")
        return False

def main():
    print("=" * 60)
    print("CLEANUP: Deleting Test Users")
    print("=" * 60)

    # Get all users
    users_response = get_all_users()

    if not users_response:
        print("No users found or error fetching users")
        return

    all_users = users_response

    print(f"\nTotal users in database: {len(all_users)}")
    print(f"Users to keep: {', '.join(KEEP_USERS)}")

    # Identify test users to delete
    test_users = []
    keep_user_count = 0

    for user in all_users:
        email = user.email
        user_id = user.id

        if email in KEEP_USERS:
            keep_user_count += 1
            print(f"\n[KEEP] Keeping user: {email}")
        else:
            test_users.append((user_id, email))

    print(f"\n{'=' * 60}")
    print(f"Users to delete: {len(test_users)}")
    print(f"Users to keep: {keep_user_count}")
    print(f"{'=' * 60}")

    if not test_users:
        print("\nNo test users to delete!")
        return

    # Confirm deletion
    print("\nTest users to be deleted:")
    for user_id, email in test_users:
        print(f"  - {email}")

    confirm = input(f"\nAre you sure you want to delete {len(test_users)} test users? (yes/no): ")

    if confirm.lower() != 'yes':
        print("\nCancelled by user")
        return

    # Delete test users
    print(f"\n{'=' * 60}")
    print("Starting deletion...")
    print(f"{'=' * 60}")

    success_count = 0
    error_count = 0

    for user_id, email in test_users:
        if delete_user_data(user_id, email):
            success_count += 1
        else:
            error_count += 1

    # Final summary
    print(f"\n{'=' * 60}")
    print("CLEANUP COMPLETE")
    print(f"{'=' * 60}")
    print(f"[SUCCESS] Successfully deleted: {success_count} users")
    if error_count > 0:
        print(f"[ERROR] Errors: {error_count} users")
    print(f"[INFO] Remaining users: {keep_user_count}")
    print(f"{'=' * 60}")

if __name__ == "__main__":
    main()
