"""
List all workspaces in Supabase
"""
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from backend.database import get_supabase_service_client

def list_workspaces():
    service_client = get_supabase_service_client()

    print("=" * 60)
    print("WORKSPACES IN DATABASE")
    print("=" * 60)

    try:
        result = service_client.table('workspaces').select('*').execute()

        if not result.data:
            print("\nNo workspaces found in database!")
            print("\nYou need to create a workspace first.")
            print("The frontend should create one automatically when you sign in.")
            return

        print(f"\nFound {len(result.data)} workspace(s):\n")

        for ws in result.data:
            print(f"ID: {ws.get('id')}")
            print(f"Name: {ws.get('name')}")
            print(f"Owner: {ws.get('owner_id')}")
            print(f"Created: {ws.get('created_at')}")
            print("-" * 60)

        # Check user_workspaces
        print("\nUSER_WORKSPACES MEMBERSHIPS:")
        print("=" * 60)

        memberships = service_client.table('user_workspaces').select('*').execute()

        if not memberships.data:
            print("\nNo memberships found!")
            print("This is a problem - users need workspace memberships.")
        else:
            for m in memberships.data:
                print(f"User: {m.get('user_id')} | Workspace: {m.get('workspace_id')} | Role: {m.get('role')}")

    except Exception as e:
        print(f"\nERROR: {e}")

if __name__ == "__main__":
    list_workspaces()
