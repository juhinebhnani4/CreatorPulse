"""
Unit tests for newsletter pipeline.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from ai_newsletter.orchestrator.pipeline import NewsletterPipeline, PipelineResult
from ai_newsletter.models.content import ContentItem


class TestNewsletterPipeline:
    """Test cases for NewsletterPipeline."""
    
    def test_init_with_settings(self):
        """Test NewsletterPipeline initialization with settings."""
        settings = Mock()
        settings.reddit = Mock()
        settings.reddit.enabled = True
        settings.rss = Mock()
        settings.rss.enabled = False
        settings.blog = Mock()
        settings.blog.enabled = False
        settings.x = Mock()
        settings.x.enabled = False
        settings.youtube = Mock()
        settings.youtube.enabled = False
        settings.newsletter = Mock()
        settings.email = Mock()
        
        with patch('ai_newsletter.orchestrator.pipeline.RedditScraper') as mock_reddit:
            with patch('ai_newsletter.orchestrator.pipeline.NewsletterGenerator') as mock_generator:
                with patch('ai_newsletter.orchestrator.pipeline.EmailSender') as mock_sender:
                    pipeline = NewsletterPipeline(settings=settings)
                    
                    assert pipeline.settings == settings
                    assert 'reddit' in pipeline.scrapers
                    assert 'rss' not in pipeline.scrapers
                    assert 'blog' not in pipeline.scrapers
                    assert 'x' not in pipeline.scrapers
                    assert 'youtube' not in pipeline.scrapers
                    assert pipeline.newsletter_generator == mock_generator.return_value
                    assert pipeline.email_sender == mock_sender.return_value
    
    def test_init_without_settings(self):
        """Test NewsletterPipeline initialization without settings."""
        with patch('ai_newsletter.orchestrator.pipeline.get_settings') as mock_settings:
            mock_settings.return_value = Mock()
            mock_settings.return_value.reddit = Mock()
            mock_settings.return_value.reddit.enabled = False
            mock_settings.return_value.rss = Mock()
            mock_settings.return_value.rss.enabled = False
            mock_settings.return_value.blog = Mock()
            mock_settings.return_value.blog.enabled = False
            mock_settings.return_value.x = Mock()
            mock_settings.return_value.x.enabled = False
            mock_settings.return_value.youtube = Mock()
            mock_settings.return_value.youtube.enabled = False
            mock_settings.return_value.newsletter = Mock()
            mock_settings.return_value.email = Mock()
            
            with patch('ai_newsletter.orchestrator.pipeline.NewsletterGenerator') as mock_generator:
                with patch('ai_newsletter.orchestrator.pipeline.EmailSender') as mock_sender:
                    pipeline = NewsletterPipeline()
                    
                    assert pipeline.settings == mock_settings.return_value
                    assert len(pipeline.scrapers) == 0
                    assert pipeline.newsletter_generator == mock_generator.return_value
                    assert pipeline.email_sender == mock_sender.return_value
    
    def test_fetch_all_content(self):
        """Test fetching content from all enabled scrapers."""
        settings = Mock()
        settings.reddit = Mock()
        settings.reddit.enabled = True
        settings.reddit.subreddits = ['test_subreddit']
        settings.reddit.sort = 'hot'
        settings.rss = Mock()
        settings.rss.enabled = False
        settings.blog = Mock()
        settings.blog.enabled = False
        settings.x = Mock()
        settings.x.enabled = False
        settings.youtube = Mock()
        settings.youtube.enabled = False
        settings.newsletter = Mock()
        settings.email = Mock()
        
        with patch('ai_newsletter.orchestrator.pipeline.RedditScraper') as mock_reddit:
            mock_reddit_instance = Mock()
            mock_reddit.return_value = mock_reddit_instance
            
            # Mock content items
            mock_items = [
                ContentItem(
                    title="Test Post",
                    source="reddit",
                    source_url="https://reddit.com/test",
                    created_at=datetime.now(),
                    content="Test content",
                    summary="Test summary",
                    author="Test Author",
                    score=100
                )
            ]
            mock_reddit_instance.fetch_content.return_value = mock_items
            
            with patch('ai_newsletter.orchestrator.pipeline.NewsletterGenerator') as mock_generator:
                with patch('ai_newsletter.orchestrator.pipeline.EmailSender') as mock_sender:
                    pipeline = NewsletterPipeline(settings=settings)
                    
                    result = pipeline._fetch_all_content(max_items_per_source=10)
                    
                    assert len(result) == 1
                    assert result[0].title == "Test Post"
                    assert result[0].source == "reddit"
                    mock_reddit_instance.fetch_content.assert_called_once_with(
                        subreddit='test_subreddit',
                        limit=10,
                        sort='hot'
                    )
    
    def test_fetch_all_content_multiple_sources(self):
        """Test fetching content from multiple sources."""
        settings = Mock()
        settings.reddit = Mock()
        settings.reddit.enabled = True
        settings.reddit.subreddits = ['test_subreddit']
        settings.reddit.sort = 'hot'
        settings.rss = Mock()
        settings.rss.enabled = True
        settings.rss.feed_urls = ['https://example.com/feed.xml']
        settings.blog = Mock()
        settings.blog.enabled = False
        settings.x = Mock()
        settings.x.enabled = False
        settings.youtube = Mock()
        settings.youtube.enabled = False
        settings.newsletter = Mock()
        settings.email = Mock()
        
        with patch('ai_newsletter.orchestrator.pipeline.RedditScraper') as mock_reddit:
            with patch('ai_newsletter.orchestrator.pipeline.RSSFeedScraper') as mock_rss:
                mock_reddit_instance = Mock()
                mock_reddit.return_value = mock_reddit_instance
                mock_rss_instance = Mock()
                mock_rss.return_value = mock_rss_instance
                
                # Mock content items
                reddit_items = [
                    ContentItem(
                        title="Reddit Post",
                        source="reddit",
                        source_url="https://reddit.com/test",
                        created_at=datetime.now(),
                        content="Reddit content",
                        summary="Reddit summary",
                        author="Reddit Author",
                        score=100
                    )
                ]
                rss_items = [
                    ContentItem(
                        title="RSS Article",
                        source="rss",
                        source_url="https://example.com/article",
                        created_at=datetime.now(),
                        content="RSS content",
                        summary="RSS summary",
                        author="RSS Author",
                        score=50
                    )
                ]
                
                mock_reddit_instance.fetch_content.return_value = reddit_items
                mock_rss_instance.fetch_content.return_value = rss_items
                
                with patch('ai_newsletter.orchestrator.pipeline.NewsletterGenerator') as mock_generator:
                    with patch('ai_newsletter.orchestrator.pipeline.EmailSender') as mock_sender:
                        pipeline = NewsletterPipeline(settings=settings)
                        
                        result = pipeline._fetch_all_content(max_items_per_source=10)
                        
                        assert len(result) == 2
                        assert result[0].title == "Reddit Post"
                        assert result[1].title == "RSS Article"
                        mock_reddit_instance.fetch_content.assert_called_once()
                        mock_rss_instance.fetch_content.assert_called_once()
    
    def test_fetch_all_content_error(self):
        """Test fetching content with error in one scraper."""
        settings = Mock()
        settings.reddit = Mock()
        settings.reddit.enabled = True
        settings.reddit.subreddits = ['test_subreddit']
        settings.reddit.sort = 'hot'
        settings.rss = Mock()
        settings.rss.enabled = False
        settings.blog = Mock()
        settings.blog.enabled = False
        settings.x = Mock()
        settings.x.enabled = False
        settings.youtube = Mock()
        settings.youtube.enabled = False
        settings.newsletter = Mock()
        settings.email = Mock()
        
        with patch('ai_newsletter.orchestrator.pipeline.RedditScraper') as mock_reddit:
            mock_reddit_instance = Mock()
            mock_reddit.return_value = mock_reddit_instance
            mock_reddit_instance.fetch_content.side_effect = Exception("Scraper error")
            
            with patch('ai_newsletter.orchestrator.pipeline.NewsletterGenerator') as mock_generator:
                with patch('ai_newsletter.orchestrator.pipeline.EmailSender') as mock_sender:
                    pipeline = NewsletterPipeline(settings=settings)
                    
                    result = pipeline._fetch_all_content(max_items_per_source=10)
                    
                    assert len(result) == 0
                    mock_reddit_instance.fetch_content.assert_called_once()
    
    def test_generate_newsletter(self):
        """Test newsletter generation."""
        settings = Mock()
        settings.reddit = Mock()
        settings.reddit.enabled = False
        settings.rss = Mock()
        settings.rss.enabled = False
        settings.blog = Mock()
        settings.blog.enabled = False
        settings.x = Mock()
        settings.x.enabled = False
        settings.youtube = Mock()
        settings.youtube.enabled = False
        settings.newsletter = Mock()
        settings.email = Mock()
        
        with patch('ai_newsletter.orchestrator.pipeline.NewsletterGenerator') as mock_generator:
            mock_generator_instance = Mock()
            mock_generator.return_value = mock_generator_instance
            mock_generator_instance.generate_newsletter.return_value = "<html>Test Newsletter</html>"
            
            with patch('ai_newsletter.orchestrator.pipeline.EmailSender') as mock_sender:
                pipeline = NewsletterPipeline(settings=settings)
                
                items = [
                    ContentItem(
                        title="Test Post",
                        source="reddit",
                        source_url="https://reddit.com/test",
                        created_at=datetime.now(),
                        content="Test content",
                        summary="Test summary",
                        author="Test Author",
                        score=100
                    )
                ]
                
                result = pipeline._generate_newsletter(items, "Test Newsletter", 10)
                
                assert result == "<html>Test Newsletter</html>"
                mock_generator_instance.generate_newsletter.assert_called_once_with(
                    content_items=items,
                    title="Test Newsletter",
                    max_items=10
                )
    
    def test_generate_newsletter_error(self):
        """Test newsletter generation with error."""
        settings = Mock()
        settings.reddit = Mock()
        settings.reddit.enabled = False
        settings.rss = Mock()
        settings.rss.enabled = False
        settings.blog = Mock()
        settings.blog.enabled = False
        settings.x = Mock()
        settings.x.enabled = False
        settings.youtube = Mock()
        settings.youtube.enabled = False
        settings.newsletter = Mock()
        settings.email = Mock()
        
        with patch('ai_newsletter.orchestrator.pipeline.NewsletterGenerator') as mock_generator:
            mock_generator_instance = Mock()
            mock_generator.return_value = mock_generator_instance
            mock_generator_instance.generate_newsletter.side_effect = Exception("Generation error")
            
            with patch('ai_newsletter.orchestrator.pipeline.EmailSender') as mock_sender:
                pipeline = NewsletterPipeline(settings=settings)
                
                items = [
                    ContentItem(
                        title="Test Post",
                        source="reddit",
                        source_url="https://reddit.com/test",
                        created_at=datetime.now(),
                        content="Test content",
                        summary="Test summary",
                        author="Test Author",
                        score=100
                    )
                ]
                
                result = pipeline._generate_newsletter(items, "Test Newsletter", 10)
                
                assert result is None
                mock_generator_instance.generate_newsletter.assert_called_once()
    
    def test_send_newsletter(self):
        """Test sending newsletter."""
        settings = Mock()
        settings.reddit = Mock()
        settings.reddit.enabled = False
        settings.rss = Mock()
        settings.rss.enabled = False
        settings.blog = Mock()
        settings.blog.enabled = False
        settings.x = Mock()
        settings.x.enabled = False
        settings.youtube = Mock()
        settings.youtube.enabled = False
        settings.newsletter = Mock()
        settings.email = Mock()
        
        with patch('ai_newsletter.orchestrator.pipeline.NewsletterGenerator') as mock_generator:
            with patch('ai_newsletter.orchestrator.pipeline.EmailSender') as mock_sender:
                mock_sender_instance = Mock()
                mock_sender.return_value = mock_sender_instance
                mock_sender_instance.send_newsletter.return_value = True
                
                pipeline = NewsletterPipeline(settings=settings)
                
                recipients = ["test@example.com", "test2@example.com"]
                result = pipeline._send_newsletter(recipients, "Test Subject", "<html>Test Newsletter</html>")
                
                assert result == True
                assert mock_sender_instance.send_newsletter.call_count == 2
                mock_sender_instance.send_newsletter.assert_any_call(
                    "test@example.com",
                    "Test Subject",
                    "<html>Test Newsletter</html>"
                )
                mock_sender_instance.send_newsletter.assert_any_call(
                    "test2@example.com",
                    "Test Subject",
                    "<html>Test Newsletter</html>"
                )
    
    def test_send_newsletter_partial_failure(self):
        """Test sending newsletter with partial failure."""
        settings = Mock()
        settings.reddit = Mock()
        settings.reddit.enabled = False
        settings.rss = Mock()
        settings.rss.enabled = False
        settings.blog = Mock()
        settings.blog.enabled = False
        settings.x = Mock()
        settings.x.enabled = False
        settings.youtube = Mock()
        settings.youtube.enabled = False
        settings.newsletter = Mock()
        settings.email = Mock()
        
        with patch('ai_newsletter.orchestrator.pipeline.NewsletterGenerator') as mock_generator:
            with patch('ai_newsletter.orchestrator.pipeline.EmailSender') as mock_sender:
                mock_sender_instance = Mock()
                mock_sender.return_value = mock_sender_instance
                mock_sender_instance.send_newsletter.side_effect = [True, False]  # First succeeds, second fails
                
                pipeline = NewsletterPipeline(settings=settings)
                
                recipients = ["test@example.com", "test2@example.com"]
                result = pipeline._send_newsletter(recipients, "Test Subject", "<html>Test Newsletter</html>")
                
                assert result == False
                assert mock_sender_instance.send_newsletter.call_count == 2
    
    def test_send_newsletter_no_recipients(self):
        """Test sending newsletter with no recipients."""
        settings = Mock()
        settings.reddit = Mock()
        settings.reddit.enabled = False
        settings.rss = Mock()
        settings.rss.enabled = False
        settings.blog = Mock()
        settings.blog.enabled = False
        settings.x = Mock()
        settings.x.enabled = False
        settings.youtube = Mock()
        settings.youtube.enabled = False
        settings.newsletter = Mock()
        settings.email = Mock()
        
        with patch('ai_newsletter.orchestrator.pipeline.NewsletterGenerator') as mock_generator:
            with patch('ai_newsletter.orchestrator.pipeline.EmailSender') as mock_sender:
                pipeline = NewsletterPipeline(settings=settings)
                
                result = pipeline._send_newsletter([], "Test Subject", "<html>Test Newsletter</html>")
                
                assert result == False
    
    def test_run_newsletter_pipeline_success(self):
        """Test successful newsletter pipeline execution."""
        settings = Mock()
        settings.reddit = Mock()
        settings.reddit.enabled = True
        settings.reddit.subreddits = ['test_subreddit']
        settings.reddit.sort = 'hot'
        settings.rss = Mock()
        settings.rss.enabled = False
        settings.blog = Mock()
        settings.blog.enabled = False
        settings.x = Mock()
        settings.x.enabled = False
        settings.youtube = Mock()
        settings.youtube.enabled = False
        settings.newsletter = Mock()
        settings.email = Mock()
        
        with patch('ai_newsletter.orchestrator.pipeline.RedditScraper') as mock_reddit:
            with patch('ai_newsletter.orchestrator.pipeline.NewsletterGenerator') as mock_generator:
                with patch('ai_newsletter.orchestrator.pipeline.EmailSender') as mock_sender:
                    mock_reddit_instance = Mock()
                    mock_reddit.return_value = mock_reddit_instance
                    mock_generator_instance = Mock()
                    mock_generator.return_value = mock_generator_instance
                    mock_sender_instance = Mock()
                    mock_sender.return_value = mock_sender_instance
                    
                    # Mock content items
                    mock_items = [
                        ContentItem(
                            title="Test Post",
                            source="reddit",
                            source_url="https://reddit.com/test",
                            created_at=datetime.now(),
                            content="Test content",
                            summary="Test summary",
                            author="Test Author",
                            score=100
                        )
                    ]
                    mock_reddit_instance.fetch_content.return_value = mock_items
                    mock_generator_instance.generate_newsletter.return_value = "<html>Test Newsletter</html>"
                    mock_sender_instance.send_newsletter.return_value = True
                    
                    pipeline = NewsletterPipeline(settings=settings)
                    
                    recipients = ["test@example.com"]
                    result = pipeline.run_newsletter_pipeline(
                        recipients=recipients,
                        custom_title="Test Newsletter",
                        max_items_per_source=10,
                        max_total_items=20
                    )
                    
                    assert result.success == True
                    assert result.items_scraped == 1
                    assert result.newsletter_generated == True
                    assert result.email_sent == True
                    assert result.newsletter_html == "<html>Test Newsletter</html>"
                    assert len(result.errors) == 0
                    assert result.execution_time > 0
    
    def test_run_newsletter_pipeline_no_content(self):
        """Test newsletter pipeline execution with no content."""
        settings = Mock()
        settings.reddit = Mock()
        settings.reddit.enabled = True
        settings.reddit.subreddits = ['test_subreddit']
        settings.reddit.sort = 'hot'
        settings.rss = Mock()
        settings.rss.enabled = False
        settings.blog = Mock()
        settings.blog.enabled = False
        settings.x = Mock()
        settings.x.enabled = False
        settings.youtube = Mock()
        settings.youtube.enabled = False
        settings.newsletter = Mock()
        settings.email = Mock()
        
        with patch('ai_newsletter.orchestrator.pipeline.RedditScraper') as mock_reddit:
            with patch('ai_newsletter.orchestrator.pipeline.NewsletterGenerator') as mock_generator:
                with patch('ai_newsletter.orchestrator.pipeline.EmailSender') as mock_sender:
                    mock_reddit_instance = Mock()
                    mock_reddit.return_value = mock_reddit_instance
                    mock_reddit_instance.fetch_content.return_value = []  # No content
                    
                    pipeline = NewsletterPipeline(settings=settings)
                    
                    result = pipeline.run_newsletter_pipeline()
                    
                    assert result.success == False
                    assert result.items_scraped == 0
                    assert result.newsletter_generated == False
                    assert result.email_sent == False
                    assert "No content items were scraped" in result.errors
    
    def test_run_newsletter_pipeline_generation_error(self):
        """Test newsletter pipeline execution with generation error."""
        settings = Mock()
        settings.reddit = Mock()
        settings.reddit.enabled = True
        settings.reddit.subreddits = ['test_subreddit']
        settings.reddit.sort = 'hot'
        settings.rss = Mock()
        settings.rss.enabled = False
        settings.blog = Mock()
        settings.blog.enabled = False
        settings.x = Mock()
        settings.x.enabled = False
        settings.youtube = Mock()
        settings.youtube.enabled = False
        settings.newsletter = Mock()
        settings.email = Mock()
        
        with patch('ai_newsletter.orchestrator.pipeline.RedditScraper') as mock_reddit:
            with patch('ai_newsletter.orchestrator.pipeline.NewsletterGenerator') as mock_generator:
                with patch('ai_newsletter.orchestrator.pipeline.EmailSender') as mock_sender:
                    mock_reddit_instance = Mock()
                    mock_reddit.return_value = mock_reddit_instance
                    mock_generator_instance = Mock()
                    mock_generator.return_value = mock_generator_instance
                    
                    # Mock content items
                    mock_items = [
                        ContentItem(
                            title="Test Post",
                            source="reddit",
                            source_url="https://reddit.com/test",
                            created_at=datetime.now(),
                            content="Test content",
                            summary="Test summary",
                            author="Test Author",
                            score=100
                        )
                    ]
                    mock_reddit_instance.fetch_content.return_value = mock_items
                    mock_generator_instance.generate_newsletter.return_value = None  # Generation failed
                    
                    pipeline = NewsletterPipeline(settings=settings)
                    
                    result = pipeline.run_newsletter_pipeline()
                    
                    assert result.success == False
                    assert result.items_scraped == 1
                    assert result.newsletter_generated == False
                    assert result.email_sent == False
                    assert "Newsletter generation failed" in result.errors
    
    def test_run_newsletter_pipeline_no_recipients(self):
        """Test newsletter pipeline execution with no recipients."""
        settings = Mock()
        settings.reddit = Mock()
        settings.reddit.enabled = True
        settings.reddit.subreddits = ['test_subreddit']
        settings.reddit.sort = 'hot'
        settings.rss = Mock()
        settings.rss.enabled = False
        settings.blog = Mock()
        settings.blog.enabled = False
        settings.x = Mock()
        settings.x.enabled = False
        settings.youtube = Mock()
        settings.youtube.enabled = False
        settings.newsletter = Mock()
        settings.email = Mock()
        
        with patch('ai_newsletter.orchestrator.pipeline.RedditScraper') as mock_reddit:
            with patch('ai_newsletter.orchestrator.pipeline.NewsletterGenerator') as mock_generator:
                with patch('ai_newsletter.orchestrator.pipeline.EmailSender') as mock_sender:
                    mock_reddit_instance = Mock()
                    mock_reddit.return_value = mock_reddit_instance
                    mock_generator_instance = Mock()
                    mock_generator.return_value = mock_generator_instance
                    
                    # Mock content items
                    mock_items = [
                        ContentItem(
                            title="Test Post",
                            source="reddit",
                            source_url="https://reddit.com/test",
                            created_at=datetime.now(),
                            content="Test content",
                            summary="Test summary",
                            author="Test Author",
                            score=100
                        )
                    ]
                    mock_reddit_instance.fetch_content.return_value = mock_items
                    mock_generator_instance.generate_newsletter.return_value = "<html>Test Newsletter</html>"
                    
                    pipeline = NewsletterPipeline(settings=settings)
                    
                    result = pipeline.run_newsletter_pipeline(recipients=[])  # No recipients
                    
                    assert result.success == True  # Success even without sending
                    assert result.items_scraped == 1
                    assert result.newsletter_generated == True
                    assert result.email_sent == False  # Not sent because no recipients
                    assert result.newsletter_html == "<html>Test Newsletter</html>"
                    assert len(result.errors) == 0
    
    def test_get_pipeline_status(self):
        """Test getting pipeline status."""
        settings = Mock()
        settings.reddit = Mock()
        settings.reddit.enabled = True
        settings.rss = Mock()
        settings.rss.enabled = False
        settings.blog = Mock()
        settings.blog.enabled = False
        settings.x = Mock()
        settings.x.enabled = False
        settings.youtube = Mock()
        settings.youtube.enabled = False
        settings.newsletter = Mock()
        settings.newsletter.model = "gpt-4"
        settings.email = Mock()
        settings.scheduler = Mock()
        settings.scheduler.enabled = True
        
        with patch('ai_newsletter.orchestrator.pipeline.RedditScraper') as mock_reddit:
            with patch('ai_newsletter.orchestrator.pipeline.NewsletterGenerator') as mock_generator:
                with patch('ai_newsletter.orchestrator.pipeline.EmailSender') as mock_sender:
                    mock_sender_instance = Mock()
                    mock_sender.return_value = mock_sender_instance
                    mock_sender_instance.get_config_status.return_value = {
                        'configured': True,
                        'connection_test': True,
                        'provider': 'SMTP'
                    }
                    
                    pipeline = NewsletterPipeline(settings=settings)
                    
                    status = pipeline.get_pipeline_status()
                    
                    assert status['scrapers_configured'] == 1
                    assert 'reddit' in status['active_scrapers']
                    assert status['newsletter_generator_available'] == True
                    assert status['email_sender_available'] == True
                    assert status['settings']['reddit_enabled'] == True
                    assert status['settings']['rss_enabled'] == False
                    assert status['settings']['newsletter_model'] == "gpt-4"
                    assert status['settings']['email_provider'] == "SMTP"
                    assert status['settings']['scheduler_enabled'] == True
    
    def test_preview_newsletter(self):
        """Test newsletter preview."""
        settings = Mock()
        settings.reddit = Mock()
        settings.reddit.enabled = True
        settings.reddit.subreddits = ['test_subreddit']
        settings.reddit.sort = 'hot'
        settings.rss = Mock()
        settings.rss.enabled = False
        settings.blog = Mock()
        settings.blog.enabled = False
        settings.x = Mock()
        settings.x.enabled = False
        settings.youtube = Mock()
        settings.youtube.enabled = False
        settings.newsletter = Mock()
        settings.email = Mock()
        
        with patch('ai_newsletter.orchestrator.pipeline.RedditScraper') as mock_reddit:
            with patch('ai_newsletter.orchestrator.pipeline.NewsletterGenerator') as mock_generator:
                mock_reddit_instance = Mock()
                mock_reddit.return_value = mock_reddit_instance
                mock_generator_instance = Mock()
                mock_generator.return_value = mock_generator_instance
                
                # Mock content items
                mock_items = [
                    ContentItem(
                        title="Test Post",
                        source="reddit",
                        source_url="https://reddit.com/test",
                        created_at=datetime.now(),
                        content="Test content",
                        summary="Test summary",
                        author="Test Author",
                        score=100
                    )
                ]
                mock_reddit_instance.fetch_content.return_value = mock_items
                mock_generator_instance.generate_newsletter.return_value = "<html>Test Newsletter</html>"
                
                pipeline = NewsletterPipeline(settings=settings)
                
                result = pipeline.preview_newsletter(
                    max_items_per_source=10,
                    max_total_items=20,
                    custom_title="Test Preview"
                )
                
                assert result is not None
                assert result['title'] == "Test Preview"
                assert result['html'] == "<html>Test Newsletter</html>"
                assert result['items_count'] == 1
                assert 'reddit' in result['sources']
                assert 'generated_at' in result
    
    def test_preview_newsletter_no_content(self):
        """Test newsletter preview with no content."""
        settings = Mock()
        settings.reddit = Mock()
        settings.reddit.enabled = True
        settings.reddit.subreddits = ['test_subreddit']
        settings.reddit.sort = 'hot'
        settings.rss = Mock()
        settings.rss.enabled = False
        settings.blog = Mock()
        settings.blog.enabled = False
        settings.x = Mock()
        settings.x.enabled = False
        settings.youtube = Mock()
        settings.youtube.enabled = False
        settings.newsletter = Mock()
        settings.email = Mock()
        
        with patch('ai_newsletter.orchestrator.pipeline.RedditScraper') as mock_reddit:
            with patch('ai_newsletter.orchestrator.pipeline.NewsletterGenerator') as mock_generator:
                mock_reddit_instance = Mock()
                mock_reddit.return_value = mock_reddit_instance
                mock_reddit_instance.fetch_content.return_value = []  # No content
                
                pipeline = NewsletterPipeline(settings=settings)
                
                result = pipeline.preview_newsletter()
                
                assert result is None
    
    def test_preview_newsletter_error(self):
        """Test newsletter preview with error."""
        settings = Mock()
        settings.reddit = Mock()
        settings.reddit.enabled = True
        settings.reddit.subreddits = ['test_subreddit']
        settings.reddit.sort = 'hot'
        settings.rss = Mock()
        settings.rss.enabled = False
        settings.blog = Mock()
        settings.blog.enabled = False
        settings.x = Mock()
        settings.x.enabled = False
        settings.youtube = Mock()
        settings.youtube.enabled = False
        settings.newsletter = Mock()
        settings.email = Mock()
        
        with patch('ai_newsletter.orchestrator.pipeline.RedditScraper') as mock_reddit:
            with patch('ai_newsletter.orchestrator.pipeline.NewsletterGenerator') as mock_generator:
                mock_reddit_instance = Mock()
                mock_reddit.return_value = mock_reddit_instance
                mock_reddit_instance.fetch_content.side_effect = Exception("Preview error")
                
                pipeline = NewsletterPipeline(settings=settings)
                
                result = pipeline.preview_newsletter()
                
                assert result is None








