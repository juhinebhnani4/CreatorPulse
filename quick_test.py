#!/usr/bin/env python3
"""
Quick test to verify the package structure is correct.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

print("🧪 Testing AI Newsletter Scraper Package Structure")
print("=" * 60)

# Test 1: Import base classes
print("\n1. Testing base imports...")
try:
    from ai_newsletter.models.content import ContentItem
    from ai_newsletter.scrapers.base import BaseScraper
    print("   ✅ Base classes imported successfully")
except ImportError as e:
    print(f"   ❌ Failed to import base classes: {e}")
    sys.exit(1)

# Test 2: Create a ContentItem
print("\n2. Testing ContentItem creation...")
try:
    from datetime import datetime
    item = ContentItem(
        title="Test Item",
        source="test",
        source_url="https://example.com",
        created_at=datetime.now(),
        score=100,
        tags=["ai", "ml"]
    )
    print(f"   ✅ Created: {item}")
    assert item.title == "Test Item"
    assert item.score == 100
    print("   ✅ ContentItem works correctly")
except Exception as e:
    print(f"   ❌ ContentItem test failed: {e}")
    sys.exit(1)

# Test 3: Test to_dict and from_dict
print("\n3. Testing serialization...")
try:
    data = item.to_dict()
    assert 'title' in data
    assert 'score' in data
    print("   ✅ to_dict() works")
    
    new_item = ContentItem.from_dict(data)
    assert new_item.title == item.title
    print("   ✅ from_dict() works")
except Exception as e:
    print(f"   ❌ Serialization test failed: {e}")
    sys.exit(1)

# Test 4: Test scraper registry
print("\n4. Testing scraper registry...")
try:
    from ai_newsletter.utils.scraper_registry import ScraperRegistry
    scrapers = ScraperRegistry.list_scrapers()
    print(f"   ✅ Found {len(scrapers)} registered scrapers: {', '.join(scrapers)}")
except Exception as e:
    print(f"   ❌ Registry test failed: {e}")
    sys.exit(1)

# Test 5: Test configuration
print("\n5. Testing configuration...")
try:
    from ai_newsletter.config import Settings, get_settings
    settings = Settings()
    assert settings.app_name == "AI Newsletter Scraper"
    print(f"   ✅ Settings loaded: {settings.app_name}")
except Exception as e:
    print(f"   ❌ Configuration test failed: {e}")
    sys.exit(1)

# Test 6: Test Reddit scraper instantiation
print("\n6. Testing scraper instantiation...")
try:
    from ai_newsletter.scrapers import RedditScraper
    scraper = RedditScraper()
    assert scraper.source_name == "reddit"
    assert scraper.source_type == "social"
    print(f"   ✅ RedditScraper created: {scraper}")
except Exception as e:
    print(f"   ❌ Scraper instantiation failed: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ All tests passed! Package structure is correct.")
print("=" * 60)

print("\n📝 Next steps:")
print("   1. Install all dependencies: pip install -r requirements.txt")
print("   2. Run the Streamlit app: python run.py")
print("   3. Or use examples: python examples/basic_usage.py")

