"""
Integration tests for Reddit scraper.
"""

import pytest
from src.ai_newsletter.scrapers.reddit_scraper import RedditScraper
from src.ai_newsletter.models.content import ContentItem


@pytest.mark.integration
class TestRedditScraperIntegration:
    """Integration tests for RedditScraper."""
    
    def test_fetch_from_subreddit(self):
        """Test fetching posts from a real subreddit."""
        scraper = RedditScraper()
        items = scraper.fetch_content(subreddit="AI_Agents", limit=5)
        
        # Should fetch some items
        assert len(items) > 0
        assert len(items) <= 5
        
        # All items should be ContentItems
        assert all(isinstance(item, ContentItem) for item in items)
        
        # All items should have required fields
        for item in items:
            assert item.title
            assert item.source == "reddit"
            assert item.source_url
            assert item.created_at
    
    def test_fetch_multiple_subreddits(self):
        """Test fetching from multiple subreddits."""
        scraper = RedditScraper()
        items = scraper.fetch_multiple_subreddits(
            subreddits=["AI_Agents", "MachineLearning"],
            limit_per_subreddit=3
        )
        
        assert len(items) > 0
        # Should have items from both subreddits
        subreddits = {item.metadata.get('subreddit') for item in items}
        assert len(subreddits) >= 1
    
    def test_to_dataframe(self):
        """Test converting Reddit items to DataFrame."""
        scraper = RedditScraper()
        items = scraper.fetch_content(subreddit="AI_Agents", limit=3)
        df = scraper.to_dataframe(items)
        
        assert len(df) > 0
        assert 'title' in df.columns
        assert 'author' in df.columns
        assert 'score' in df.columns
        assert 'comments_count' in df.columns

