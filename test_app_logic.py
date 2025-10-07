#!/usr/bin/env python3
"""
Test the core app logic without Streamlit.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from ai_newsletter.scrapers import RedditScraper
from ai_newsletter.models.content import ContentItem
import pandas as pd

print("=" * 60)
print("Testing App Logic")
print("=" * 60)

# Test 1: Fetch from Reddit
print("\n1. Testing Reddit fetch...")
try:
    reddit_scraper = RedditScraper()
    fetched_items = reddit_scraper.fetch_content(
        subreddit='AI_Agents',
        limit=3,
        sort='hot'
    )
    print(f"   ✅ Fetched {len(fetched_items)} items")
    assert len(fetched_items) > 0, "No items fetched"
    assert all(isinstance(item, ContentItem) for item in fetched_items)
    print(f"   ✅ All items are ContentItem instances")
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

# Test 2: Simulate session state
print("\n2. Testing session state simulation...")
class FakeSessionState:
    def __init__(self):
        self.items = []

session_state = FakeSessionState()
all_items = []
all_items.extend(fetched_items)
session_state.items = all_items[:100]

items = session_state.items
print(f"   Items type: {type(items)}")
print(f"   Items length: {len(items)}")
assert isinstance(items, list)
print(f"   ✅ Items is a list")

# Test 3: Convert to dict
print("\n3. Testing conversion to dict...")
try:
    df_data = [item.to_dict() for item in items]
    print(f"   ✅ Converted {len(df_data)} items to dict")
    assert len(df_data) == len(items)
except TypeError as e:
    print(f"   ❌ TypeError: {e}")
    print(f"   Items type: {type(items)}")
    if items:
        print(f"   First item type: {type(items[0])}")
        print(f"   First item has to_dict: {hasattr(items[0], 'to_dict')}")
    sys.exit(1)

# Test 4: Create DataFrame
print("\n4. Testing DataFrame creation...")
try:
    df = pd.DataFrame(df_data)
    print(f"   ✅ Created DataFrame with shape {df.shape}")
    print(f"   Columns: {list(df.columns)[:5]}...")
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

# Test 5: Format datetime
print("\n5. Testing datetime formatting...")
try:
    if 'created_at' in df.columns:
        df['created_at'] = pd.to_datetime(df['created_at'])
        df['created_date'] = df['created_at'].dt.strftime('%Y-%m-%d %H:%M')
        print(f"   ✅ Formatted datetime columns")
    else:
        print(f"   ⚠️  No created_at column")
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

# Test 6: Display sample
print("\n6. Sample data:")
print(df[['title', 'source', 'score', 'comments_count']].head(3))

print("\n" + "=" * 60)
print("✅ All tests passed!")
print("=" * 60)
print("\nThe core logic works correctly.")
print("If Streamlit app still has issues, it's a Streamlit-specific problem.")

