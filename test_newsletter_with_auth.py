#!/usr/bin/env python3
"""
Test newsletter generation with proper authentication to reproduce the error.
"""

import sys
sys.path.insert(0, ".")

import asyncio
from backend.services.newsletter_service import newsletter_service

async def test_with_sources():
    """Test with sources parameter to trigger the filtering code."""

    print("\n" + "="*60)
    print("Testing Newsletter Generation with Sources Filter")
    print("="*60 + "\n")

    try:
        workspace_id = "a378d938-c330-4060-82a4-17579dc8bb3f"

        print(f"[1] Calling generate_newsletter with sources=['x', 'reddit']...")

        result = await newsletter_service.generate_newsletter(
            user_id="test-user-123",
            workspace_id=workspace_id,
            title="Test Newsletter - Debug Sources",
            max_items=5,
            days_back=7,
            sources=['x', 'reddit'],  # This triggers the filtering code
            tone="professional",
            language="en",
            temperature=0.7,
            use_openrouter=True
        )

        print(f"\n[SUCCESS] Newsletter generated!")
        print(f"  - ID: {result['newsletter']['id']}")
        print(f"  - Items: {result['content_items_count']}")
        print(f"  - Sources: {result['sources_used']}")

        return True

    except Exception as e:
        print(f"\n[FAILED] Error: {type(e).__name__}: {e}")
        import traceback
        print(f"\nFull traceback:")
        print(traceback.format_exc())
        return False

if __name__ == "__main__":
    success = asyncio.run(test_with_sources())
    sys.exit(0 if success else 1)
