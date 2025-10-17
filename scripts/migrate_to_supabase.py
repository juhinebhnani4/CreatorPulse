"""
Migration script to transfer data from JSON files to Supabase.

Usage:
    python scripts/migrate_to_supabase.py --workspace default --user-id <user_id>
    python scripts/migrate_to_supabase.py --all --user-id <user_id> --dry-run
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ai_newsletter.database.supabase_client import SupabaseManager
from src.ai_newsletter.models.content import ContentItem
from src.ai_newsletter.models.style_profile import StyleProfile
from src.ai_newsletter.models.feedback import FeedbackItem


def migrate_workspace(workspace_name: str, user_id: str, dry_run: bool = False):
    """
    Migrate a workspace from file-based storage to Supabase.

    Args:
        workspace_name: Name of workspace directory
        user_id: Owner user ID in Supabase
        dry_run: If True, don't actually write to database
    """
    workspace_path = Path('workspaces') / workspace_name

    if not workspace_path.exists():
        print(f"❌ Workspace directory not found: {workspace_path}")
        return False

    print(f"🔄 Migrating workspace: {workspace_name}")
    print(f"   Path: {workspace_path}")
    print(f"   Owner: {user_id}")
    print(f"   Dry run: {dry_run}")
    print()

    # Initialize Supabase
    try:
        supabase = SupabaseManager()
        print("✅ Connected to Supabase")
    except Exception as e:
        print(f"❌ Failed to connect to Supabase: {e}")
        return False

    # Step 1: Create workspace in Supabase
    print("1️⃣  Creating workspace...")

    if not dry_run:
        try:
            workspace = supabase.create_workspace(
                name=workspace_name,
                description=f"Migrated from {workspace_path}",
                user_id=user_id
            )
            workspace_id = workspace['id']
            print(f"   ✅ Created workspace: {workspace_id}")
        except Exception as e:
            print(f"   ❌ Failed to create workspace: {e}")
            return False
    else:
        workspace_id = "DRY_RUN_ID"
        print(f"   🔍 Would create workspace")

    # Step 2: Migrate config.json
    print("2️⃣  Migrating configuration...")

    config_file = workspace_path / 'config.json'
    if config_file.exists():
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)

            if not dry_run:
                supabase.save_workspace_config(workspace_id, config, user_id)
                print(f"   ✅ Migrated config.json")
            else:
                print(f"   🔍 Would migrate config.json ({len(config)} keys)")
        except Exception as e:
            print(f"   ⚠️  Error migrating config: {e}")
    else:
        print(f"   ℹ️  No config.json found")

    # Step 3: Migrate style_profile.json
    print("3️⃣  Migrating style profile...")

    style_file = workspace_path / 'style_profile.json'
    if style_file.exists():
        try:
            with open(style_file, 'r') as f:
                style_data = json.load(f)

            profile = StyleProfile.from_dict(style_data)

            if not dry_run:
                supabase.save_style_profile(workspace_id, profile, user_id)
                print(f"   ✅ Migrated style profile")
            else:
                print(f"   🔍 Would migrate style profile")
        except Exception as e:
            print(f"   ⚠️  Error migrating style profile: {e}")
    else:
        print(f"   ℹ️  No style profile found (optional)")

    # Step 4: Migrate historical_content.json
    print("4️⃣  Migrating historical content...")

    historical_file = workspace_path / 'historical_content.json'
    if historical_file.exists():
        try:
            with open(historical_file, 'r') as f:
                historical_data = json.load(f)

            # Flatten the date-based structure
            all_items = []
            for date, items in historical_data.items():
                all_items.extend(items)

            # Convert to ContentItem objects
            content_items = []
            for item in all_items:
                try:
                    content_items.append(ContentItem.from_dict(item))
                except Exception as e:
                    print(f"   ⚠️  Skipping invalid item: {e}")

            if content_items:
                if not dry_run:
                    # Batch insert in chunks of 100
                    chunk_size = 100
                    for i in range(0, len(content_items), chunk_size):
                        chunk = content_items[i:i + chunk_size]
                        supabase.save_content_items(workspace_id, chunk)
                    print(f"   ✅ Migrated {len(content_items)} content items")
                else:
                    print(f"   🔍 Would migrate {len(content_items)} content items")
            else:
                print(f"   ℹ️  No valid content items found")
        except Exception as e:
            print(f"   ⚠️  Error migrating content: {e}")
    else:
        print(f"   ℹ️  No historical content found (optional)")

    # Step 5: Migrate feedback_data.json
    print("5️⃣  Migrating feedback data...")

    feedback_file = workspace_path / 'feedback_data.json'
    if feedback_file.exists():
        try:
            with open(feedback_file, 'r') as f:
                feedback_data = json.load(f)

            if feedback_data:
                if not dry_run:
                    for feedback_item_data in feedback_data:
                        try:
                            feedback_item = FeedbackItem.from_dict(feedback_item_data)
                            supabase.save_feedback(workspace_id, feedback_item, user_id)
                        except Exception as e:
                            print(f"   ⚠️  Skipping invalid feedback item: {e}")
                    print(f"   ✅ Migrated {len(feedback_data)} feedback items")
                else:
                    print(f"   🔍 Would migrate {len(feedback_data)} feedback items")
            else:
                print(f"   ℹ️  No feedback items found")
        except Exception as e:
            print(f"   ⚠️  Error migrating feedback: {e}")
    else:
        print(f"   ℹ️  No feedback data found (optional)")

    print()
    print("✅ Migration complete!" if not dry_run else "🔍 Dry run complete!")
    print()

    return True


def main():
    """Main migration entry point."""
    parser = argparse.ArgumentParser(description='Migrate workspace data to Supabase')
    parser.add_argument('--workspace', help='Workspace name to migrate')
    parser.add_argument('--user-id', required=True, help='Owner user ID in Supabase')
    parser.add_argument('--dry-run', action='store_true', help='Preview migration without writing')
    parser.add_argument('--all', action='store_true', help='Migrate all workspaces')

    args = parser.parse_args()

    if not args.workspace and not args.all:
        print("❌ Error: Must specify either --workspace or --all")
        parser.print_help()
        return

    print("=" * 60)
    print("  CreatorPulse - Supabase Migration Tool")
    print("=" * 60)
    print()

    if args.all:
        # Migrate all workspaces
        workspaces_dir = Path('workspaces')
        if not workspaces_dir.exists():
            print("❌ No workspaces directory found")
            return

        workspaces = [d.name for d in workspaces_dir.iterdir() if d.is_dir()]
        if not workspaces:
            print("❌ No workspaces found in workspaces/ directory")
            return

        print(f"Found {len(workspaces)} workspaces to migrate:")
        for ws in workspaces:
            print(f"  - {ws}")
        print()

        for workspace_name in workspaces:
            migrate_workspace(workspace_name, args.user_id, args.dry_run)
            print()
    else:
        # Migrate single workspace
        migrate_workspace(args.workspace, args.user_id, args.dry_run)

    print("=" * 60)
    print("Migration complete!")
    print()
    print("Next steps:")
    print("1. Verify data in Supabase dashboard (https://supabase.com/dashboard)")
    print("2. Test application with Supabase backend")
    print("3. Backup original files (keep for 30 days)")
    print("4. Update .env to use Supabase")
    print("=" * 60)


if __name__ == '__main__':
    main()
