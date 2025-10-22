"""
Clear X/Twitter content from database to test enhanced scraper.
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.ai_newsletter.database.supabase_client import SupabaseManager
from backend.settings import settings

def clear_x_content():
    """Delete all X/Twitter content items."""
    client = SupabaseManager()

    # First, get the actual workspace ID
    workspaces = client.service_client.table('workspaces').select('id, name').execute()

    if not workspaces.data:
        print("❌ No workspaces found!")
        return

    # Use the first workspace
    workspace = workspaces.data[0]
    workspace_id = workspace['id']
    workspace_name = workspace.get('name', 'Unknown')

    print(f"Found workspace: {workspace_name} ({workspace_id})")
    print(f"Deleting X/Twitter content from this workspace...")

    # Delete X content
    result = client.service_client.table('content_items') \
        .delete() \
        .eq('workspace_id', workspace_id) \
        .eq('source', 'x') \
        .execute()

    deleted_count = len(result.data) if result.data else 0
    print(f"[OK] Deleted {deleted_count} X/Twitter content items")
    print(f"\nNow:")
    print(f"  1. Restart your backend (if not using --reload)")
    print(f"  2. Click 'Scrape Now' to test the enhanced scraper!")
    print(f"  3. Look for improved titles (no URLs) and rich summaries!")

if __name__ == "__main__":
    clear_x_content()
