"""
Debug RLS issue with newsletters table
"""
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from backend.database import get_supabase_client, get_supabase_service_client

def debug_rls():
    print("=" * 60)
    print("DEBUG: Newsletter RLS Issue")
    print("=" * 60)

    # Get both clients
    client = get_supabase_client()
    service_client = get_supabase_service_client()

    print("\n1. Testing regular client vs service client:")
    print(f"   Regular client uses key: {client.supabase_key[:20]}...")
    print(f"   Service client uses key: {service_client.supabase_key[:20]}...")
    print(f"   Are they different? {client.supabase_key != service_client.supabase_key}")

    # Try to insert with both
    test_workspace_id = "3353d8f1-4bec-465c-9518-91ccc35d2898"  # From your screenshot

    print(f"\n2. Testing workspace: {test_workspace_id}")

    # Check if workspace exists
    try:
        ws = service_client.table('workspaces').select('*').eq('id', test_workspace_id).execute()
        if ws.data:
            print(f"   Workspace found: {ws.data[0].get('name')}")
        else:
            print("   WARNING: Workspace not found!")
    except Exception as e:
        print(f"   ERROR checking workspace: {e}")

    # Check user_workspaces
    print("\n3. Checking user_workspaces membership:")
    try:
        memberships = service_client.table('user_workspaces').select('*').eq('workspace_id', test_workspace_id).execute()
        if memberships.data:
            for m in memberships.data:
                print(f"   User: {m.get('user_id')} | Role: {m.get('role')}")
        else:
            print("   WARNING: No user_workspaces entries found for this workspace!")
            print("   This might be the issue - RLS policies check user_workspaces")
    except Exception as e:
        print(f"   ERROR checking memberships: {e}")

    # Test insert with service client
    print("\n4. Testing newsletter insert with SERVICE client:")
    test_data = {
        'workspace_id': test_workspace_id,
        'title': 'RLS Test Newsletter',
        'content_html': '<h1>Test</h1>',
        'content_text': 'Test',
        'status': 'draft',
        'generated_at': '2025-01-16T00:00:00Z'
    }

    try:
        result = service_client.table('newsletters').insert(test_data).execute()
        print("   SUCCESS! Newsletter inserted:")
        print(f"   ID: {result.data[0].get('id')}")
        print("\n   Cleaning up test newsletter...")
        service_client.table('newsletters').delete().eq('id', result.data[0].get('id')).execute()
        print("   Test newsletter deleted")
    except Exception as e:
        print(f"   ERROR: {e}")
        print("\n   This is the problem! Even service_client can't insert.")

    print("\n" + "=" * 60)
    print("ANALYSIS:")
    print("=" * 60)
    print("If the insert failed even with service_client, the issue is likely:")
    print("1. Service key might not actually bypass RLS (check Supabase dashboard)")
    print("2. There might be a missing user_workspaces entry")
    print("3. The RLS policy might be checking auth.uid() which doesn't work with service key")
    print("=" * 60)

if __name__ == "__main__":
    debug_rls()
