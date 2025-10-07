"""
Basic usage examples for AI Newsletter Scraper.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ai_newsletter.scrapers import RedditScraper, RSSFeedScraper


def example_reddit():
    """Example: Fetch posts from Reddit."""
    print("=" * 50)
    print("Reddit Scraper Example")
    print("=" * 50)
    
    scraper = RedditScraper()
    
    # Fetch from single subreddit
    items = scraper.fetch_content(
        subreddit="AI_Agents",
        limit=5,
        sort="hot"
    )
    
    print(f"\nFetched {len(items)} posts from r/AI_Agents")
    
    for i, item in enumerate(items, 1):
        print(f"\n{i}. {item.title}")
        print(f"   Score: {item.score} | Comments: {item.comments_count}")
        print(f"   Author: {item.author}")
        print(f"   URL: {item.source_url}")
    
    # Convert to DataFrame
    df = scraper.to_dataframe(items)
    print(f"\nDataFrame shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")


def example_rss():
    """Example: Fetch posts from RSS feeds."""
    print("\n" + "=" * 50)
    print("RSS Scraper Example")
    print("=" * 50)
    
    scraper = RSSFeedScraper()
    
    # Fetch from multiple feeds
    feeds = [
        "https://blog.openai.com/rss/",
        "https://ai.googleblog.com/feeds/posts/default"
    ]
    
    items = scraper.fetch_content(
        feed_urls=feeds,
        limit=3
    )
    
    print(f"\nFetched {len(items)} articles from RSS feeds")
    
    for i, item in enumerate(items, 1):
        print(f"\n{i}. {item.title}")
        print(f"   Author: {item.author or 'Unknown'}")
        print(f"   Date: {item.created_at.strftime('%Y-%m-%d')}")
        print(f"   URL: {item.source_url}")
        if item.summary:
            print(f"   Summary: {item.summary[:100]}...")


def example_filtering():
    """Example: Filter and sort content."""
    print("\n" + "=" * 50)
    print("Filtering Example")
    print("=" * 50)
    
    scraper = RedditScraper()
    items = scraper.fetch_content(subreddit="MachineLearning", limit=20)
    
    print(f"\nTotal items: {len(items)}")
    
    # Filter by score
    high_score = scraper.filter_items(items, min_score=50)
    print(f"Items with score >= 50: {len(high_score)}")
    
    # Filter by comments
    active = scraper.filter_items(items, min_comments=10)
    print(f"Items with >= 10 comments: {len(active)}")
    
    # Combined filters
    popular = scraper.filter_items(items, min_score=30, min_comments=5)
    print(f"Popular items (score>=30, comments>=5): {len(popular)}")
    
    # Convert to DataFrame and sort
    df = scraper.to_dataframe(popular)
    df_sorted = df.sort_values('score', ascending=False)
    
    print("\nTop 3 by score:")
    for idx, row in df_sorted.head(3).iterrows():
        print(f"  - {row['title'][:60]}... (Score: {row['score']})")


def example_multiple_sources():
    """Example: Aggregate from multiple sources."""
    print("\n" + "=" * 50)
    print("Multiple Sources Example")
    print("=" * 50)
    
    all_items = []
    
    # Reddit
    reddit = RedditScraper()
    reddit_items = reddit.fetch_content(subreddit="AI_Agents", limit=5)
    all_items.extend(reddit_items)
    print(f"Reddit: {len(reddit_items)} items")
    
    # RSS
    rss = RSSFeedScraper()
    rss_items = rss.fetch_content(
        feed_urls=["https://blog.openai.com/rss/"],
        limit=5
    )
    all_items.extend(rss_items)
    print(f"RSS: {len(rss_items)} items")
    
    print(f"\nTotal aggregated items: {len(all_items)}")
    
    # Group by source
    from collections import Counter
    sources = Counter(item.source for item in all_items)
    print("\nItems by source:")
    for source, count in sources.items():
        print(f"  {source}: {count}")


if __name__ == "__main__":
    # Run examples
    example_reddit()
    example_rss()
    example_filtering()
    example_multiple_sources()
    
    print("\n" + "=" * 50)
    print("Examples completed!")
    print("=" * 50)

