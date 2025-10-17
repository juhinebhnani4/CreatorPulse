"""
Integration tests for Supabase database operations.

Run with: pytest tests/integration/test_supabase_integration.py -v
"""

import pytest
from datetime import datetime
import os
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.ai_newsletter.database.supabase_client import SupabaseManager
from src.ai_newsletter.auth.auth_manager import AuthManager
from src.ai_newsletter.models.content import ContentItem
from src.ai_newsletter.models.style_profile import StyleProfile


@pytest.fixture(scope="module")
def supabase():
    """Initialize Supabase client for testing."""
    # Check if Supabase credentials are configured
    if not os.getenv("SUPABASE_URL") or not os.getenv("SUPABASE_KEY"):
        pytest.skip("Supabase credentials not configured")

    return SupabaseManager()


@pytest.fixture
def test_workspace(supabase):
    """Create a test workspace."""
    # Create unique workspace name with timestamp
    workspace_name = f"test_workspace_{int(datetime.now().timestamp())}"

    try:
        workspace = supabase.create_workspace(
            name=workspace_name,
            description="Test workspace for integration tests"
        )
        yield workspace
    finally:
        # Cleanup
        try:
            supabase.delete_workspace(workspace['id'])
        except Exception as e:
            print(f"Warning: Failed to cleanup test workspace: {e}")


def test_supabase_connection(supabase):
    """Test basic Supabase connection."""
    assert supabase.health_check() is True, "Supabase health check failed"


def test_create_workspace(supabase, test_workspace):
    """Test workspace creation."""
    assert test_workspace['name'].startswith('test_workspace'), "Workspace name incorrect"
    assert test_workspace['id'] is not None, "Workspace ID not generated"
    assert 'owner_id' in test_workspace, "Owner ID not set"


def test_list_workspaces(supabase, test_workspace):
    """Test listing workspaces."""
    workspaces = supabase.list_workspaces()
    assert len(workspaces) > 0, "No workspaces found"

    # Check if our test workspace is in the list
    workspace_ids = [w['id'] for w in workspaces]
    assert test_workspace['id'] in workspace_ids, "Test workspace not in list"


def test_get_workspace(supabase, test_workspace):
    """Test getting a specific workspace."""
    workspace = supabase.get_workspace(test_workspace['id'])
    assert workspace is not None, "Workspace not found"
    assert workspace['id'] == test_workspace['id'], "Wrong workspace returned"


def test_update_workspace(supabase, test_workspace):
    """Test updating workspace details."""
    new_description = "Updated test description"
    updated = supabase.update_workspace(
        test_workspace['id'],
        {'description': new_description}
    )
    assert updated['description'] == new_description, "Description not updated"


def test_workspace_config(supabase, test_workspace):
    """Test workspace configuration operations."""
    workspace_id = test_workspace['id']

    # Get default config
    config = supabase.get_workspace_config(workspace_id)
    assert config is not None, "Config not found"
    assert 'reddit' in config, "Default Reddit config missing"

    # Update config
    new_config = config.copy()
    new_config['reddit']['limit'] = 50

    saved_config = supabase.save_workspace_config(workspace_id, new_config)
    assert saved_config is not None, "Config not saved"

    # Verify update
    loaded_config = supabase.get_workspace_config(workspace_id)
    assert loaded_config['reddit']['limit'] == 50, "Config not updated"


def test_save_and_load_content(supabase, test_workspace):
    """Test saving and loading content items."""
    workspace_id = test_workspace['id']

    # Create test content items
    items = [
        ContentItem(
            title=f"Test Item {i}",
            source="reddit",
            source_url=f"https://reddit.com/test{i}",
            created_at=datetime.now(),
            content=f"Test content {i}",
            summary=f"Test summary {i}",
            score=100 * i,
            comments_count=10 * i
        )
        for i in range(5)
    ]

    # Save items
    saved = supabase.save_content_items(workspace_id, items)
    assert len(saved) == 5, "Not all items saved"

    # Load items
    loaded = supabase.load_content_items(workspace_id, days=1)
    assert len(loaded) == 5, "Not all items loaded"
    assert loaded[0].title.startswith("Test Item"), "Item data incorrect"


def test_content_filtering(supabase, test_workspace):
    """Test content filtering by source."""
    workspace_id = test_workspace['id']

    # Create items from different sources
    items = [
        ContentItem(
            title="Reddit Item",
            source="reddit",
            source_url="https://reddit.com/test",
            created_at=datetime.now()
        ),
        ContentItem(
            title="RSS Item",
            source="rss",
            source_url="https://example.com/rss",
            created_at=datetime.now()
        )
    ]

    supabase.save_content_items(workspace_id, items)

    # Load only Reddit items
    reddit_items = supabase.load_content_items(workspace_id, days=1, source="reddit")
    assert len(reddit_items) == 1, "Wrong number of Reddit items"
    assert reddit_items[0].source == "reddit", "Wrong source"


def test_style_profile(supabase, test_workspace):
    """Test style profile operations."""
    workspace_id = test_workspace['id']

    # Create style profile
    profile = StyleProfile(
        tone="professional",
        formality_level=0.8,
        avg_sentence_length=20.0,
        vocabulary_level="advanced",
        favorite_phrases=["in conclusion", "furthermore"],
        uses_emojis=False
    )

    # Save profile
    saved = supabase.save_style_profile(workspace_id, profile)
    assert saved is not None, "Profile not saved"

    # Load profile
    loaded = supabase.load_style_profile(workspace_id)
    assert loaded is not None, "Profile not loaded"
    assert loaded.tone == "professional", "Tone incorrect"
    assert loaded.formality_level == 0.8, "Formality level incorrect"
    assert len(loaded.favorite_phrases) == 2, "Favorite phrases incorrect"


def test_workspace_isolation(supabase):
    """Test that workspaces are properly isolated."""
    # Create two workspaces
    workspace1_name = f"test_ws1_{int(datetime.now().timestamp())}"
    workspace2_name = f"test_ws2_{int(datetime.now().timestamp())}"

    workspace1 = supabase.create_workspace(workspace1_name, "Workspace 1")
    workspace2 = supabase.create_workspace(workspace2_name, "Workspace 2")

    try:
        # Add content to workspace 1
        items1 = [ContentItem(
            title="Item in WS1",
            source="reddit",
            source_url="https://reddit.com/test",
            created_at=datetime.now()
        )]
        supabase.save_content_items(workspace1['id'], items1)

        # Load content from workspace 2 (should be empty)
        items2 = supabase.load_content_items(workspace2['id'], days=1)
        assert len(items2) == 0, "Workspace isolation broken - found items from other workspace"

        # Load content from workspace 1 (should have 1 item)
        items1_loaded = supabase.load_content_items(workspace1['id'], days=1)
        assert len(items1_loaded) == 1, "Items not properly saved to workspace 1"

    finally:
        # Cleanup
        supabase.delete_workspace(workspace1['id'])
        supabase.delete_workspace(workspace2['id'])


def test_default_config_structure(supabase, test_workspace):
    """Test that default config has all required fields."""
    config = supabase.get_workspace_config(test_workspace['id'])

    # Check required top-level keys
    required_keys = ['reddit', 'rss', 'youtube', 'blog', 'x', 'newsletter']
    for key in required_keys:
        assert key in config, f"Missing required config key: {key}"

    # Check Reddit config structure
    assert 'enabled' in config['reddit'], "Reddit config missing 'enabled'"
    assert 'limit' in config['reddit'], "Reddit config missing 'limit'"
    assert 'subreddits' in config['reddit'], "Reddit config missing 'subreddits'"


# Run tests
if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
