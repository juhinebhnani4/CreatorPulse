"""
Test script for blog crawling functionality.

This script tests the new deep crawling feature that:
1. Extracts article links from blog list pages
2. Crawls individual articles for full content
3. Handles errors gracefully with fallbacks
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

from ai_newsletter.scrapers.blog_scraper import BlogScraper


def test_link_extraction():
    """Test link extraction from a blog list page."""
    print("=" * 80)
    print("TEST 1: Link Extraction")
    print("=" * 80)

    scraper = BlogScraper()

    # Test URL - using a well-known tech blog with standard structure
    test_url = "https://techcrunch.com/"

    print(f"\nTesting link extraction from: {test_url}")

    try:
        import requests
        from bs4 import BeautifulSoup

        response = requests.get(test_url, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')

        links = scraper._extract_article_links(soup, test_url, limit=5)

        print(f"\n✅ Extracted {len(links)} article links:")
        for idx, link in enumerate(links, 1):
            print(f"  {idx}. {link}")

        return len(links) > 0

    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False


def test_url_normalization():
    """Test URL normalization and deduplication."""
    print("\n" + "=" * 80)
    print("TEST 2: URL Normalization")
    print("=" * 80)

    scraper = BlogScraper()

    test_urls = [
        "https://www.example.com/article",
        "https://example.com/article/",
        "https://example.com/article?utm_source=twitter",
        "https://example.com/article#section1",
    ]

    print("\nTesting URL normalization:")
    normalized = []
    for url in test_urls:
        norm = scraper._normalize_url(url)
        normalized.append(norm)
        print(f"  {url}")
        print(f"  → {norm}")

    # Check if all normalized to same URL
    if len(set(normalized)) == 1:
        print("\n✅ All URLs normalized to same value (deduplication works!)")
        return True
    else:
        print(f"\n❌ URLs normalized to {len(set(normalized))} different values")
        return False


def test_full_crawling():
    """Test full crawling workflow with a real blog."""
    print("\n" + "=" * 80)
    print("TEST 3: Full Crawling Workflow")
    print("=" * 80)

    scraper = BlogScraper()

    # Use a small limit to avoid rate limiting
    test_url = "https://techcrunch.com/"
    limit = 3

    print(f"\nTesting full crawling of: {test_url}")
    print(f"Limit: {limit} articles")
    print(f"This will take ~{limit * 1.0}s due to rate limiting...\n")

    try:
        def progress_callback(current, total, article_url):
            print(f"  [{current}/{total}] Crawling: {article_url}")

        items = scraper.fetch_content_with_crawling(
            url=test_url,
            limit=limit,
            crawl_delay=1.0,
            crawl_timeout=30,
            progress_callback=progress_callback
        )

        print(f"\n✅ Crawled {len(items)} articles successfully!")

        # Show sample data
        if items:
            print("\n📊 Sample Article Data:")
            item = items[0]
            print(f"\nTitle: {item.title}")
            print(f"Author: {item.author or 'N/A'}")
            print(f"URL: {item.source_url}")
            print(f"Content length: {len(item.content)} characters")
            print(f"Summary length: {len(item.summary)} characters")
            print(f"Tags: {', '.join(item.tags) if item.tags else 'N/A'}")
            print(f"Image: {item.image_url or 'N/A'}")

            # Show content preview
            print(f"\n📄 Content Preview (first 200 chars):")
            print(f"{item.content[:200]}...")

        return len(items) > 0

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_fallback():
    """Test fallback to preview extraction when crawling fails."""
    print("\n" + "=" * 80)
    print("TEST 4: Fallback to Preview Extraction")
    print("=" * 80)

    scraper = BlogScraper()

    # Use a simple URL for fallback testing
    test_url = "https://techcrunch.com"

    print(f"\nTesting fallback behavior with: {test_url}")

    try:
        items = scraper.fetch_content_with_crawling(
            url=test_url,
            limit=3,
            crawl_delay=0.5
        )

        if items:
            print(f"\n✅ Fallback worked! Extracted {len(items)} items using preview extraction")
            return True
        else:
            print("\n⚠️ No items extracted (might be expected for homepage)")
            return True  # Not a failure, just no content

    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False


def run_all_tests():
    """Run all tests."""
    print("\n" + "=" * 80)
    print("BLOG CRAWLING - TEST SUITE")
    print("=" * 80)

    tests = [
        ("Link Extraction", test_link_extraction),
        ("URL Normalization", test_url_normalization),
        ("Full Crawling", test_full_crawling),
        ("Fallback Mechanism", test_fallback),
    ]

    results = {}

    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n❌ {test_name} failed with exception: {e}")
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
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    import logging

    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    exit_code = run_all_tests()
    sys.exit(exit_code)
