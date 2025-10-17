"""
Integration tests for CreatorPulse pipeline.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

from ai_newsletter.orchestrator import NewsletterPipeline, PipelineResult
from ai_newsletter.scrapers.youtube_scraper import YouTubeScraper
from ai_newsletter.scrapers.reddit_scraper import RedditScraper
from ai_newsletter.generators import NewsletterGenerator
from ai_newsletter.delivery import EmailSender
from ai_newsletter.scheduler import DailyScheduler
from ai_newsletter.models.content import ContentItem
from ai_newsletter.config.settings import Settings, NewsletterConfig, EmailConfig, SchedulerConfig


class TestNewsletterPipelineIntegration:
    """Integration tests for the complete newsletter pipeline."""
    
    @pytest.fixture
    def mock_settings(self):
        """Create mock settings for testing."""
        settings = get_settings()
        
        # Configure Reddit
        settings.reddit.enabled = True
        settings.reddit.subreddits = ["AI_Agents", "MachineLearning"]
        
        # Configure YouTube
        settings.youtube.enabled = True
        settings.youtube.api_key = "test_youtube_key"
        settings.youtube.channel_ids = ["test_channel_1", "test_channel_2"]
        
        # Configure Newsletter
        settings.newsletter.openai_api_key = "test_openai_key"
        settings.newsletter.model = "gpt-3.5-turbo"
        
        # Configure Email
        settings.email.smtp_server = "smtp.gmail.com"
        settings.email.smtp_port = 587
        settings.email.from_email = "test@example.com"
        settings.email.smtp_username = "test@example.com"
        settings.email.smtp_password = "test_password"
        
        return settings
    
    @pytest.fixture
    def sample_content_items(self):
        """Create sample content items for testing."""
        return [
            ContentItem(
                title="AI Breakthrough: New Model Achieves Human Performance",
                source="reddit",
                source_url="https://reddit.com/r/AI_Agents/comments/test1",
                created_at=datetime.now() - timedelta(hours=2),
                content="Researchers have developed a new AI model...",
                summary="Revolutionary AI model shows unprecedented capabilities.",
                author="AI_Researcher",
                score=1250,
                comments_count=89,
                views_count=15420,
                tags=["AI", "Machine Learning", "Breakthrough"]
            ),
            ContentItem(
                title="Building AI Agents: Complete Tutorial",
                source="youtube",
                source_url="https://youtube.com/watch?v=test2",
                created_at=datetime.now() - timedelta(hours=5),
                content="In this comprehensive tutorial...",
                summary="Step-by-step guide to creating AI agents.",
                author="TechTutorials",
                score=890,
                comments_count=45,
                views_count=12500,
                tags=["Tutorial", "AI Agents", "Programming"]
            ),
            ContentItem(
                title="The Future of Work: AI Transformation",
                source="rss",
                source_url="https://example.com/blog/future-work",
                created_at=datetime.now() - timedelta(hours=8),
                content="Artificial Intelligence is revolutionizing work...",
                summary="Analysis of AI's impact on employment and productivity.",
                author="FutureInsights",
                score=650,
                comments_count=23,
                views_count=8900,
                tags=["Future of Work", "AI Impact", "Business"]
            )
        ]
    
    def test_pipeline_initialization(self, mock_settings):
        """Test pipeline initialization with mock settings."""
        with patch('ai_newsletter.orchestrator.RedditScraper') as mock_reddit, \
             patch('ai_newsletter.orchestrator.YouTubeScraper') as mock_youtube, \
             patch('ai_newsletter.orchestrator.NewsletterGenerator') as mock_generator, \
             patch('ai_newsletter.orchestrator.EmailSender') as mock_email:
            
            # Mock scraper instances
            mock_reddit_instance = Mock()
            mock_reddit.return_value = mock_reddit_instance
            
            mock_youtube_instance = Mock()
            mock_youtube.return_value = mock_youtube_instance
            
            # Mock generator and email sender
            mock_generator_instance = Mock()
            mock_generator.return_value = mock_generator_instance
            
            mock_email_instance = Mock()
            mock_email.return_value = mock_email_instance
            
            pipeline = NewsletterPipeline(mock_settings)
            
            assert len(pipeline.scrapers) == 2  # Reddit and YouTube
            assert pipeline.newsletter_generator == mock_generator_instance
            assert pipeline.email_sender == mock_email_instance
    
    def test_pipeline_run_success(self, mock_settings, sample_content_items):
        """Test successful pipeline run."""
        with patch('ai_newsletter.orchestrator.RedditScraper') as mock_reddit, \
             patch('ai_newsletter.orchestrator.YouTubeScraper') as mock_youtube, \
             patch('ai_newsletter.orchestrator.NewsletterGenerator') as mock_generator, \
             patch('ai_newsletter.orchestrator.EmailSender') as mock_email:
            
            # Mock scrapers
            mock_reddit_instance = Mock()
            mock_reddit_instance.fetch_multiple_subreddits.return_value = sample_content_items[:1]
            mock_reddit.return_value = mock_reddit_instance
            
            mock_youtube_instance = Mock()
            mock_youtube_instance.fetch_channel.return_value = sample_content_items[1:2]
            mock_youtube.return_value = mock_youtube_instance
            
            # Mock newsletter generator
            mock_generator_instance = Mock()
            mock_generator_instance.generate_newsletter.return_value = "<html>Test Newsletter</html>"
            mock_generator.return_value = mock_generator_instance
            
            # Mock email sender
            mock_email_instance = Mock()
            mock_email_instance.send_newsletter.return_value = True
            mock_email.return_value = mock_email_instance
            
            pipeline = NewsletterPipeline(mock_settings)
            
            result = pipeline.run_newsletter_pipeline(
                recipients=["test@example.com"],
                max_items_per_source=5,
                max_total_items=10
            )
            
            assert isinstance(result, PipelineResult)
            assert result.success is True
            assert result.items_scraped > 0
            assert result.newsletter_generated is True
            assert result.email_sent is True
            assert len(result.errors) == 0
    
    def test_pipeline_run_no_content(self, mock_settings):
        """Test pipeline run with no content scraped."""
        with patch('ai_newsletter.orchestrator.RedditScraper') as mock_reddit, \
             patch('ai_newsletter.orchestrator.YouTubeScraper') as mock_youtube, \
             patch('ai_newsletter.orchestrator.NewsletterGenerator') as mock_generator, \
             patch('ai_newsletter.orchestrator.EmailSender') as mock_email:
            
            # Mock scrapers returning empty results
            mock_reddit_instance = Mock()
            mock_reddit_instance.fetch_multiple_subreddits.return_value = []
            mock_reddit.return_value = mock_reddit_instance
            
            mock_youtube_instance = Mock()
            mock_youtube_instance.fetch_channel.return_value = []
            mock_youtube.return_value = mock_youtube_instance
            
            # Mock other components
            mock_generator_instance = Mock()
            mock_generator.return_value = mock_generator_instance
            
            mock_email_instance = Mock()
            mock_email.return_value = mock_email_instance
            
            pipeline = NewsletterPipeline(mock_settings)
            
            result = pipeline.run_newsletter_pipeline()
            
            assert isinstance(result, PipelineResult)
            assert result.success is False
            assert result.items_scraped == 0
            assert result.newsletter_generated is False
            assert result.email_sent is False
            assert "No content items scraped" in result.errors
    
    def test_pipeline_run_generation_failure(self, mock_settings, sample_content_items):
        """Test pipeline run with newsletter generation failure."""
        with patch('ai_newsletter.orchestrator.RedditScraper') as mock_reddit, \
             patch('ai_newsletter.orchestrator.YouTubeScraper') as mock_youtube, \
             patch('ai_newsletter.orchestrator.NewsletterGenerator') as mock_generator, \
             patch('ai_newsletter.orchestrator.EmailSender') as mock_email:
            
            # Mock scrapers
            mock_reddit_instance = Mock()
            mock_reddit_instance.fetch_multiple_subreddits.return_value = sample_content_items[:1]
            mock_reddit.return_value = mock_reddit_instance
            
            mock_youtube_instance = Mock()
            mock_youtube_instance.fetch_channel.return_value = sample_content_items[1:2]
            mock_youtube.return_value = mock_youtube_instance
            
            # Mock newsletter generator failure
            mock_generator_instance = Mock()
            mock_generator_instance.generate_newsletter.side_effect = Exception("OpenAI API error")
            mock_generator.return_value = mock_generator_instance
            
            # Mock email sender
            mock_email_instance = Mock()
            mock_email.return_value = mock_email_instance
            
            pipeline = NewsletterPipeline(mock_settings)
            
            result = pipeline.run_newsletter_pipeline()
            
            assert isinstance(result, PipelineResult)
            assert result.success is False
            assert result.items_scraped > 0
            assert result.newsletter_generated is False
            assert result.email_sent is False
            assert any("Newsletter generation failed" in error for error in result.errors)
    
    def test_pipeline_run_email_failure(self, mock_settings, sample_content_items):
        """Test pipeline run with email sending failure."""
        with patch('ai_newsletter.orchestrator.RedditScraper') as mock_reddit, \
             patch('ai_newsletter.orchestrator.YouTubeScraper') as mock_youtube, \
             patch('ai_newsletter.orchestrator.NewsletterGenerator') as mock_generator, \
             patch('ai_newsletter.orchestrator.EmailSender') as mock_email:
            
            # Mock scrapers
            mock_reddit_instance = Mock()
            mock_reddit_instance.fetch_multiple_subreddits.return_value = sample_content_items[:1]
            mock_reddit.return_value = mock_reddit_instance
            
            mock_youtube_instance = Mock()
            mock_youtube_instance.fetch_channel.return_value = sample_content_items[1:2]
            mock_youtube.return_value = mock_youtube_instance
            
            # Mock newsletter generator
            mock_generator_instance = Mock()
            mock_generator_instance.generate_newsletter.return_value = "<html>Test Newsletter</html>"
            mock_generator.return_value = mock_generator_instance
            
            # Mock email sender failure
            mock_email_instance = Mock()
            mock_email_instance.send_newsletter.return_value = False
            mock_email.return_value = mock_email_instance
            
            pipeline = NewsletterPipeline(mock_settings)
            
            result = pipeline.run_newsletter_pipeline()
            
            assert isinstance(result, PipelineResult)
            assert result.success is False
            assert result.items_scraped > 0
            assert result.newsletter_generated is True
            assert result.email_sent is False
            assert any("Failed to send to" in error for error in result.errors)
    
    def test_pipeline_preview(self, mock_settings, sample_content_items):
        """Test pipeline preview functionality."""
        with patch('ai_newsletter.orchestrator.RedditScraper') as mock_reddit, \
             patch('ai_newsletter.orchestrator.YouTubeScraper') as mock_youtube, \
             patch('ai_newsletter.orchestrator.NewsletterGenerator') as mock_generator, \
             patch('ai_newsletter.orchestrator.EmailSender') as mock_email:
            
            # Mock scrapers
            mock_reddit_instance = Mock()
            mock_reddit_instance.fetch_multiple_subreddits.return_value = sample_content_items[:1]
            mock_reddit.return_value = mock_reddit_instance
            
            mock_youtube_instance = Mock()
            mock_youtube_instance.fetch_channel.return_value = sample_content_items[1:2]
            mock_youtube.return_value = mock_youtube_instance
            
            # Mock newsletter generator
            mock_generator_instance = Mock()
            mock_preview = {
                'html': '<html>Test Preview</html>',
                'item_count': 2,
                'generated_at': datetime.now().isoformat(),
                'config': {'model': 'gpt-3.5-turbo', 'temperature': 0.7}
            }
            mock_generator_instance.preview_newsletter.return_value = mock_preview
            mock_generator.return_value = mock_generator_instance
            
            # Mock email sender
            mock_email_instance = Mock()
            mock_email.return_value = mock_email_instance
            
            pipeline = NewsletterPipeline(mock_settings)
            
            preview = pipeline.preview_newsletter()
            
            assert preview is not None
            assert preview['items_count'] > 0
            assert 'reddit' in preview['sources']
            assert 'youtube' in preview['sources']
            assert 'html' in preview
    
    def test_pipeline_status(self, mock_settings):
        """Test pipeline status reporting."""
        with patch('ai_newsletter.orchestrator.RedditScraper') as mock_reddit, \
             patch('ai_newsletter.orchestrator.YouTubeScraper') as mock_youtube, \
             patch('ai_newsletter.orchestrator.NewsletterGenerator') as mock_generator, \
             patch('ai_newsletter.orchestrator.EmailSender') as mock_email:
            
            # Mock components
            mock_reddit_instance = Mock()
            mock_reddit_instance.source_name = "reddit"
            mock_reddit.return_value = mock_reddit_instance
            
            mock_youtube_instance = Mock()
            mock_youtube_instance.source_name = "youtube"
            mock_youtube.return_value = mock_youtube_instance
            
            mock_generator_instance = Mock()
            mock_generator.return_value = mock_generator_instance
            
            mock_email_instance = Mock()
            mock_email_instance.get_config_status.return_value = {
                'provider': 'SMTP',
                'configured': True,
                'connection_test': True
            }
            mock_email.return_value = mock_email_instance
            
            pipeline = NewsletterPipeline(mock_settings)
            
            status = pipeline.get_pipeline_status()
            
            assert status['scrapers_configured'] == 2
            assert 'reddit' in status['scraper_types']
            assert 'youtube' in status['scraper_types']
            assert status['newsletter_generator_available'] is True
            assert status['email_sender_available'] is True
            assert status['email_config_status']['provider'] == 'SMTP'


class TestSchedulerIntegration:
    """Integration tests for the scheduler system."""
    
    def test_scheduler_with_pipeline(self):
        """Test scheduler integration with pipeline."""
        with patch('ai_newsletter.scheduler.daily_scheduler.BackgroundScheduler') as mock_scheduler_class, \
             patch('ai_newsletter.orchestrator.NewsletterPipeline') as mock_pipeline_class:
            
            # Mock scheduler
            mock_scheduler = Mock()
            mock_scheduler.running = False
            mock_scheduler_class.return_value = mock_scheduler
            
            # Mock pipeline
            mock_pipeline = Mock()
            mock_pipeline.run_newsletter_pipeline.return_value = Mock(
                success=True,
                items_scraped=10,
                newsletter_generated=True,
                email_sent=True,
                errors=[],
                execution_time=5.0,
                generated_at=datetime.now()
            )
            mock_pipeline_class.return_value = mock_pipeline
            
            # Create scheduler
            config = SchedulerConfig(enabled=True, time="08:00", timezone="UTC")
            scheduler = DailyScheduler(config=config)
            
            # Create callback that uses pipeline
            def newsletter_callback():
                pipeline = NewsletterPipeline()
                result = pipeline.run_newsletter_pipeline()
                return result.success
            
            # Schedule job
            success = scheduler.schedule_newsletter_job(
                newsletter_callback,
                job_id="test_job",
                schedule_time="08:00",
                timezone="UTC"
            )
            
            assert success is True
            assert "test_job" in scheduler.jobs
            assert "test_job" in scheduler.job_callbacks
    
    def test_scheduler_job_execution(self):
        """Test scheduler job execution with retry logic."""
        with patch('ai_newsletter.scheduler.daily_scheduler.BackgroundScheduler') as mock_scheduler_class:
            
            # Mock scheduler
            mock_scheduler = Mock()
            mock_scheduler.running = False
            mock_scheduler_class.return_value = mock_scheduler
            
            # Create scheduler with retry config
            config = SchedulerConfig(
                enabled=True,
                time="08:00",
                timezone="UTC",
                max_retries=2,
                retry_delay=1
            )
            scheduler = DailyScheduler(config=config)
            
            # Track callback calls
            call_count = 0
            
            def test_callback():
                nonlocal call_count
                call_count += 1
                if call_count < 3:
                    raise Exception("Test error")
                return True
            
            scheduler.job_callbacks["test_job"] = test_callback
            
            # Run job with retries
            with patch('ai_newsletter.scheduler.daily_scheduler.time_module.sleep') as mock_sleep:
                scheduler._run_newsletter_job("test_job")
                
                assert call_count == 3  # Should succeed on third try
                assert mock_sleep.call_count == 2  # Two retries


class TestEmailIntegration:
    """Integration tests for email delivery."""
    
    def test_email_with_newsletter_content(self):
        """Test email sending with newsletter content."""
        with patch('ai_newsletter.delivery.email_sender.smtplib.SMTP') as mock_smtp:
            
            # Mock SMTP server
            mock_server = Mock()
            mock_smtp.return_value.__enter__.return_value = mock_server
            
            # Create email sender
            config = EmailConfig(
                smtp_server="smtp.gmail.com",
                smtp_port=587,
                smtp_username="test@example.com",
                smtp_password="test_password",
                from_email="test@example.com",
                from_name="CreatorPulse",
                use_tls=True
            )
            
            email_sender = EmailSender(config=config)
            
            # Newsletter content
            newsletter_html = """
            <html>
            <body>
                <h1>Daily AI Newsletter</h1>
                <p>Here are today's top AI stories:</p>
                <ul>
                    <li><a href="https://example.com/story1">AI Breakthrough Story</a></li>
                    <li><a href="https://example.com/story2">Machine Learning Tutorial</a></li>
                </ul>
            </body>
            </html>
            """
            
            # Send newsletter
            success = email_sender.send_newsletter(
                to_email="recipient@example.com",
                subject="Daily AI Newsletter - Test",
                html_content=newsletter_html,
                text_content="Daily AI Newsletter - Here are today's top stories..."
            )
            
            assert success is True
            mock_server.starttls.assert_called_once()
            mock_server.login.assert_called_once_with("test@example.com", "test_password")
            mock_server.send_message.assert_called_once()
    
    def test_bulk_email_sending(self):
        """Test bulk email sending functionality."""
        with patch('ai_newsletter.delivery.email_sender.smtplib.SMTP') as mock_smtp:
            
            # Mock SMTP server
            mock_server = Mock()
            mock_smtp.return_value.__enter__.return_value = mock_server
            
            # Create email sender
            config = EmailConfig(
                smtp_server="smtp.gmail.com",
                smtp_port=587,
                smtp_username="test@example.com",
                smtp_password="test_password",
                from_email="test@example.com",
                from_name="CreatorPulse",
                use_tls=True
            )
            
            email_sender = EmailSender(config=config)
            
            # Newsletter content
            newsletter_html = "<html><body><h1>Test Newsletter</h1></body></html>"
            
            # Recipients
            recipients = [
                "user1@example.com",
                "user2@example.com",
                "user3@example.com"
            ]
            
            # Send bulk newsletter
            result = email_sender.send_bulk_newsletter(
                recipients=recipients,
                subject="Test Newsletter",
                html_content=newsletter_html
            )
            
            assert result['sent'] == 3
            assert result['failed'] == 0
            assert len(result['errors']) == 0
            assert mock_server.send_message.call_count == 3


if __name__ == "__main__":
    pytest.main([__file__])



