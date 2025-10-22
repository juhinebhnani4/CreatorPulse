"""
Clean up corrupted sources from workspace configuration.
Removes Reddit sources that contain @ symbols (Twitter usernames).
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.ai_newsletter.database.supabase_client import SupabaseManager

def fix_corrupted_sources():
    """Remove corrupted Reddit sources from all workspaces."""
    db = SupabaseManager()

    # Get all workspaces
    result = db.service_client.table('workspaces').select('*').execute()
    workspaces = result.data

    print(f"Found {len(workspaces)} workspace(s)")

    for workspace in workspaces:
        workspace_id = workspace['id']
        workspace_name = workspace['name']

        print(f"\nChecking workspace: {workspace_name} ({workspace_id})")

        # Get workspace config
        config = db.get_workspace_config(workspace_id)

        if not config or 'sources' not in config:
            print("  No sources configured")
            continue

        sources = config['sources']
        cleaned_sources = []
        removed_count = 0

        for source in sources:
            # Check Reddit sources for @ symbols
            if source.get('type') == 'reddit':
                subreddits = source.get('config', {}).get('subreddits', [])
                valid_subreddits = []

                for sub in subreddits:
                    # Remove r/ prefix if present
                    cleaned_sub = sub.replace('r/', '')

                    # Check if it's actually a Twitter username (starts with @)
                    if cleaned_sub.startswith('@'):
                        print(f"  [X] Removing corrupted Reddit source: {sub} (Twitter username)")
                        removed_count += 1
                    else:
                        valid_subreddits.append(cleaned_sub)

                # Only keep the source if it has valid subreddits
                if valid_subreddits:
                    source['config']['subreddits'] = valid_subreddits
                    cleaned_sources.append(source)
                elif not valid_subreddits and subreddits:
                    print(f"  [X] Removing entire Reddit source (all subreddits were invalid)")
                    removed_count += 1
            else:
                # Keep non-Reddit sources as-is
                cleaned_sources.append(source)

        # Update config if sources were removed
        if removed_count > 0:
            config['sources'] = cleaned_sources

            # Save updated config
            db.service_client.table('workspace_configs').update({
                'config': config
            }).eq('workspace_id', workspace_id).execute()

            print(f"  [OK] Cleaned {removed_count} corrupted source(s)")
        else:
            print("  [OK] No corrupted sources found")

if __name__ == '__main__':
    print("=" * 70)
    print("CLEANING CORRUPTED SOURCES FROM WORKSPACE CONFIGURATIONS")
    print("=" * 70)

    try:
        fix_corrupted_sources()
        print("\n" + "=" * 70)
        print("[OK] CLEANUP COMPLETE!")
        print("=" * 70)
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
