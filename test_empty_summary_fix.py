"""
Test script to verify empty summary fixes across all scrapers.

Tests that all scrapers now generate meaningful summaries even when
content is missing or unavailable.
"""

import sys
from pathlib import Path
import os

# Force UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from ai_newsletter.scrapers.reddit_scraper import RedditScraper
from ai_newsletter.scrapers.rss_scraper import RSSFeedScraper
from ai_newsletter.scrapers.blog_scraper import BlogScraper


def test_reddit_empty_summary():
    """Test Reddit scraper generates summaries for link/image posts."""
    print("=" * 80)
    print("TEST 1: Reddit Scraper - Link/Image/Video Posts")
    print("=" * 80)

    scraper = RedditScraper()

    test_subreddits = [
        ('pics', 'Image posts'),
        ('technology', 'Link posts'),
    ]

    for subreddit, description in test_subreddits:
        print(f"\nTesting r/{subreddit} ({description})...")

        try:
            items = scraper.fetch_content(subreddit=subreddit, limit=5)

            if not items:
                print(f"  ⚠️ No items fetched from r/{subreddit}")
                continue

            empty_count = 0
            for item in items:
                if not item.summary or not item.summary.strip():
                    print(f"  ❌ Empty summary for: {item.title[:50]}")
                    empty_count += 1
                else:
                    print(f"  ✓ {item.title[:40]}: {item.summary[:60]}...")

            if empty_count == 0:
                print(f"  ✅ All {len(items)} items have summaries!")
                return True
            else:
                print(f"  ❌ {empty_count}/{len(items)} items have empty summaries")
                return False

        except Exception as e:
            print(f"  ❌ Error: {e}")
            return False

    return True


def test_rss_empty_summary():
    """Test RSS scraper generates summaries."""
    print("\n" + "=" * 80)
    print("TEST 2: RSS Scraper - Feeds with Limited Content")
    print("=" * 80)

    scraper = RSSFeedScraper()

    test_feeds = [
        "https://openai.com/news/rss.xml",
    ]

    for feed_url in test_feeds:
        print(f"\nTesting {feed_url}...")

        try:
            items = scraper.fetch_content(feed_url=feed_url, limit=5)

            if not items:
                print(f"  ⚠️ No items fetched from {feed_url}")
                continue

            empty_count = 0
            for item in items:
                if not item.summary or not item.summary.strip():
                    print(f"  ❌ Empty summary for: {item.title[:50]}")
                    empty_count += 1
                else:
                    print(f"  ✓ {item.title[:40]}: {item.summary[:60]}...")

            if empty_count == 0:
                print(f"  ✅ All {len(items)} items have summaries!")
                return True
            else:
                print(f"  ❌ {empty_count}/{len(items)} items have empty summaries")
                return False

        except Exception as e:
            print(f"  ❌ Error: {e}")
            return False

    return True


def test_blog_empty_summary():
    """Test Blog scraper generates summaries even when extraction fails."""
    print("\n" + "=" * 80)
    print("TEST 3: Blog Scraper - Pages with Limited Content")
    print("=" * 80)

    scraper = BlogScraper()

    test_url = "https://techcrunch.com/"

    print(f"\nTesting {test_url}...")

    try:
        items = scraper.fetch_content_with_crawling(
            url=test_url,
            limit=3,
            crawl_delay=0.5
        )

        if not items:
            print(f"  ⚠️ No items fetched from {test_url}")
            return True  # Not a failure

        empty_count = 0
        for item in items:
            if not item.summary or not item.summary.strip():
                print(f"  ❌ Empty summary for: {item.title[:50]}")
                empty_count += 1
            else:
                print(f"  ✓ {item.title[:40]}: {item.summary[:60]}...")

        if empty_count == 0:
            print(f"  ✅ All {len(items)} items have summaries!")
            return True
        else:
            print(f"  ❌ {empty_count}/{len(items)} items have empty summaries")
            return False

    except Exception as e:
        print(f"  ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all empty summary tests."""
    print("\n" + "=" * 80)
    print("EMPTY SUMMARY FIX - TEST SUITE")
    print("=" * 80)

    tests = [
        ("Reddit Scraper", test_reddit_empty_summary),
        ("RSS Scraper", test_rss_empty_summary),
        ("Blog Scraper", test_blog_empty_summary),
    ]

    results = {}

    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n❌ {test_name} failed with exception: {e}")
            import traceback
            traceback.print_exc()
            results[test_name] = False

    # Summary
    print("\n" + "=" * 80)
    print("TEST RESULTS SUMMARY")
    print("=" * 80)

    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")

    total = len(results)
    passed = sum(1 for v in results.values() if v)

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! No more empty summaries!")
        return 0
    else:
        print(f"\n⚠️ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    import logging

    # Set up logging
    logging.basicConfig(
        level=logging.WARNING,  # Only show warnings and errors
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    exit_code = run_all_tests()
    sys.exit(exit_code)
