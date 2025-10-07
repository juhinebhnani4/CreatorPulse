#!/usr/bin/env python3
"""
Comprehensive test suite for all features.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from ai_newsletter.scrapers import RedditScraper, RSSFeedScraper, BlogScraper
from ai_newsletter.scrapers.x_scraper import XScraper
from ai_newsletter.models.content import ContentItem
from ai_newsletter.utils.scraper_registry import ScraperRegistry
from ai_newsletter.config import Settings, get_settings
from datetime import datetime
import pandas as pd

print("=" * 70)
print("COMPREHENSIVE TEST SUITE")
print("=" * 70)

test_results = []

def test(name, func):
    """Run a test and track results."""
    try:
        print(f"\n{len(test_results) + 1}. {name}")
        func()
        print(f"   ✅ PASSED")
        test_results.append((name, True, None))
        return True
    except Exception as e:
        print(f"   ❌ FAILED: {e}")
        test_results.append((name, False, str(e)))
        return False

# ============================================================================
# TEST 1: Data Model
# ============================================================================

def test_content_item():
    """Test ContentItem creation and methods."""
    item = ContentItem(
        title="Test Title",
        source="test",
        source_url="https://example.com",
        created_at=datetime.now(),
        score=100,
        comments_count=50,
        tags=["ai", "ml"]
    )
    
    assert item.title == "Test Title"
    assert item.score == 100
    
    # Test to_dict
    data = item.to_dict()
    assert isinstance(data, dict)
    assert 'title' in data
    assert data['score'] == 100
    
    # Test from_dict
    item2 = ContentItem.from_dict(data)
    assert item2.title == item.title
    
    print(f"      Created item: {item.title}")
    print(f"      to_dict() keys: {len(data)} fields")

test("ContentItem model", test_content_item)

# ============================================================================
# TEST 2: Reddit Scraper
# ============================================================================

def test_reddit_scraper():
    """Test Reddit scraper functionality."""
    scraper = RedditScraper()
    
    assert scraper.source_name == "reddit"
    assert scraper.source_type == "social"
    
    # Fetch content
    items = scraper.fetch_content(subreddit='AI_Agents', limit=3)
    
    assert len(items) > 0, "No items fetched"
    assert all(isinstance(item, ContentItem) for item in items)
    assert all(item.source == "reddit" for item in items)
    assert all(item.title for item in items)
    
    # Test DataFrame conversion
    df = scraper.to_dataframe(items)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == len(items)
    assert 'title' in df.columns
    
    # Test filtering
    filtered = scraper.filter_items(items, min_score=0)
    assert len(filtered) <= len(items)
    
    print(f"      Fetched: {len(items)} posts")
    print(f"      DataFrame shape: {df.shape}")
    print(f"      Sample: {items[0].title[:40]}...")

test("Reddit Scraper", test_reddit_scraper)

# ============================================================================
# TEST 3: RSS Scraper
# ============================================================================

def test_rss_scraper():
    """Test RSS scraper functionality."""
    scraper = RSSFeedScraper()
    
    assert scraper.source_name == "rss"
    assert scraper.source_type == "feed"
    
    # Test with a known feed
    items = scraper.fetch_content(
        feed_urls=['https://blog.openai.com/rss/'],
        limit=3
    )
    
    # RSS feeds might be empty or slow, so we allow empty results
    if items:
        assert all(isinstance(item, ContentItem) for item in items)
        assert all(item.source == "rss" for item in items)
        print(f"      Fetched: {len(items)} articles")
        print(f"      Sample: {items[0].title[:40]}...")
    else:
        print(f"      ⚠️  No items (feed might be slow/empty)")

test("RSS Feed Scraper", test_rss_scraper)

# ============================================================================
# TEST 4: Blog Scraper
# ============================================================================

def test_blog_scraper():
    """Test Blog scraper initialization."""
    scraper = BlogScraper()
    
    assert scraper.source_name == "blog"
    assert scraper.source_type == "web"
    
    # We can't test actual scraping without a test URL
    # but we can verify the scraper exists
    print(f"      Initialized successfully")
    print(f"      Source: {scraper.source_name}")

test("Blog Scraper", test_blog_scraper)

# ============================================================================
# TEST 5: X Scraper
# ============================================================================

def test_x_scraper():
    """Test X scraper initialization."""
    scraper = XScraper()
    
    assert scraper.source_name == "x"
    assert scraper.source_type == "social"
    
    # Without API keys, client won't be initialized
    # but the scraper should still be created
    print(f"      Initialized (no API keys)")
    print(f"      Client: {scraper.client}")

test("X/Twitter Scraper", test_x_scraper)

# ============================================================================
# TEST 6: Scraper Registry
# ============================================================================

def test_registry():
    """Test scraper registry."""
    registry = ScraperRegistry()
    
    scrapers = registry.list_scrapers()
    assert len(scrapers) > 0
    assert 'reddit' in scrapers
    
    # Get a scraper
    reddit_class = registry.get_scraper('reddit')
    assert reddit_class is not None
    
    # Create instance
    scraper = reddit_class()
    assert isinstance(scraper, RedditScraper)
    
    print(f"      Registered scrapers: {', '.join(scrapers)}")
    print(f"      Total: {len(scrapers)}")

test("Scraper Registry", test_registry)

# ============================================================================
# TEST 7: Configuration
# ============================================================================

def test_configuration():
    """Test configuration system."""
    settings = Settings()
    
    assert settings.app_name == "AI Newsletter Scraper"
    assert hasattr(settings, 'reddit')
    assert hasattr(settings, 'rss')
    assert hasattr(settings, 'blog')
    assert hasattr(settings, 'x')
    
    # Test reddit config
    assert settings.reddit.enabled == True
    
    print(f"      App: {settings.app_name}")
    print(f"      Reddit enabled: {settings.reddit.enabled}")
    print(f"      Debug mode: {settings.debug}")

test("Configuration System", test_configuration)

# ============================================================================
# TEST 8: Data Pipeline
# ============================================================================

def test_data_pipeline():
    """Test complete data pipeline."""
    # Fetch from Reddit
    scraper = RedditScraper()
    items = scraper.fetch_content(subreddit='AI_Agents', limit=3)
    
    # Simulate session state
    class MockSession:
        def __init__(self):
            self.content_items = []
    
    session = MockSession()
    session.content_items = items
    
    # Get items
    retrieved_items = session.content_items
    assert isinstance(retrieved_items, list)
    assert len(retrieved_items) == len(items)
    
    # Convert to dict
    df_data = [item.to_dict() for item in retrieved_items]
    assert len(df_data) == len(items)
    
    # Create DataFrame
    df = pd.DataFrame(df_data)
    assert len(df) == len(items)
    
    # Format datetime
    if 'created_at' in df.columns:
        df['created_at'] = pd.to_datetime(df['created_at'])
        df['created_date'] = df['created_at'].dt.strftime('%Y-%m-%d %H:%M')
        assert 'created_date' in df.columns
    
    print(f"      Pipeline processed: {len(items)} items")
    print(f"      DataFrame shape: {df.shape}")
    print(f"      Columns: {len(df.columns)}")

test("Complete Data Pipeline", test_data_pipeline)

# ============================================================================
# TEST 9: Filtering and Sorting
# ============================================================================

def test_filtering_sorting():
    """Test filtering and sorting operations."""
    scraper = RedditScraper()
    items = scraper.fetch_content(subreddit='AI_Agents', limit=10)
    
    # Test filtering by score
    high_score = scraper.filter_items(items, min_score=10)
    assert len(high_score) <= len(items)
    assert all(item.score >= 10 for item in high_score)
    
    # Test filtering by comments
    active = scraper.filter_items(items, min_comments=5)
    assert all(item.comments_count >= 5 for item in active)
    
    # Test DataFrame sorting
    df = scraper.to_dataframe(items)
    df_sorted = df.sort_values('score', ascending=False)
    
    if len(df_sorted) > 1:
        assert df_sorted.iloc[0]['score'] >= df_sorted.iloc[-1]['score']
    
    print(f"      Total items: {len(items)}")
    print(f"      High score (>=10): {len(high_score)}")
    print(f"      Active (>=5 comments): {len(active)}")
    print(f"      Sorted by score ✓")

test("Filtering and Sorting", test_filtering_sorting)

# ============================================================================
# TEST 10: Multiple Sources
# ============================================================================

def test_multiple_sources():
    """Test aggregating from multiple sources."""
    all_items = []
    
    # Reddit
    reddit = RedditScraper()
    reddit_items = reddit.fetch_content(subreddit='AI_Agents', limit=3)
    all_items.extend(reddit_items)
    
    # RSS
    rss = RSSFeedScraper()
    rss_items = rss.fetch_content(
        feed_urls=['https://blog.openai.com/rss/'],
        limit=3
    )
    all_items.extend(rss_items)
    
    # Check mixed sources
    sources = set(item.source for item in all_items)
    assert 'reddit' in sources
    
    if rss_items:
        assert 'rss' in sources
    
    # Create unified DataFrame
    df_data = [item.to_dict() for item in all_items]
    df = pd.DataFrame(df_data)
    
    print(f"      Total items: {len(all_items)}")
    print(f"      Sources: {', '.join(sources)}")
    print(f"      Unified DataFrame: {df.shape}")

test("Multiple Sources Aggregation", test_multiple_sources)

# ============================================================================
# TEST 11: Export Functionality
# ============================================================================

def test_export():
    """Test CSV export."""
    scraper = RedditScraper()
    items = scraper.fetch_content(subreddit='AI_Agents', limit=3)
    df = scraper.to_dataframe(items)
    
    # Test CSV conversion
    csv_data = df.to_csv(index=False)
    assert isinstance(csv_data, str)
    assert 'title' in csv_data
    assert 'source' in csv_data
    
    lines = csv_data.split('\n')
    assert len(lines) > 1  # Header + data
    
    print(f"      CSV size: {len(csv_data)} bytes")
    print(f"      CSV lines: {len(lines)}")
    print(f"      Includes headers ✓")

test("CSV Export", test_export)

# ============================================================================
# TEST 12: Error Handling
# ============================================================================

def test_error_handling():
    """Test error handling."""
    scraper = RedditScraper()
    
    # Test with invalid subreddit (should return empty, not crash)
    items = scraper.fetch_content(subreddit='ThisSubredditDoesNotExist123456', limit=1)
    # Should handle gracefully and return empty or partial results
    assert isinstance(items, list)
    
    # Test validation
    valid_item = ContentItem(
        title="Valid",
        source="test",
        source_url="https://test.com",
        created_at=datetime.now()
    )
    assert scraper.validate_item(valid_item) == True
    
    # Invalid item (empty title)
    invalid_item = ContentItem(
        title="",
        source="test",
        source_url="https://test.com",
        created_at=datetime.now()
    )
    assert scraper.validate_item(invalid_item) == False
    
    print(f"      Invalid subreddit handled ✓")
    print(f"      Validation working ✓")

test("Error Handling", test_error_handling)

# ============================================================================
# RESULTS SUMMARY
# ============================================================================

print("\n" + "=" * 70)
print("TEST RESULTS SUMMARY")
print("=" * 70)

passed = sum(1 for _, result, _ in test_results if result)
failed = len(test_results) - passed

print(f"\nTotal Tests: {len(test_results)}")
print(f"✅ Passed: {passed}")
print(f"❌ Failed: {failed}")
print(f"Success Rate: {passed/len(test_results)*100:.1f}%")

if failed > 0:
    print("\n" + "=" * 70)
    print("FAILED TESTS:")
    print("=" * 70)
    for name, result, error in test_results:
        if not result:
            print(f"\n❌ {name}")
            print(f"   Error: {error}")

print("\n" + "=" * 70)

if failed == 0:
    print("🎉 ALL TESTS PASSED! 🎉")
    print("=" * 70)
    print("\nThe application is ready to use!")
    print("Run: ./agent/bin/streamlit run src/streamlit_app.py")
    sys.exit(0)
else:
    print("⚠️  SOME TESTS FAILED")
    print("=" * 70)
    sys.exit(1)

