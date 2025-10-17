"""
Newsletter pipeline orchestrator.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass

from ..models.content import ContentItem
from ..scrapers.base import BaseScraper
from ..scrapers.reddit_scraper import RedditScraper
from ..scrapers.rss_scraper import RSSFeedScraper
from ..scrapers.youtube_scraper import YouTubeScraper
from ..generators.newsletter_generator import NewsletterGenerator
from ..delivery.email_sender import EmailSender
from ..config.settings import Settings, NewsletterConfig, EmailConfig


@dataclass
class PipelineResult:
    """Result of a pipeline run."""
    success: bool
    items_scraped: int
    newsletter_generated: bool
    email_sent: bool
    errors: List[str]
    execution_time: float
    generated_at: datetime


class NewsletterPipeline:
    """
    Main pipeline orchestrator for CreatorPulse.
    
    Coordinates the entire flow: Scrape → Filter → Generate → Send
    
    Example:
        pipeline = NewsletterPipeline(settings)
        result = pipeline.run_newsletter_pipeline()
    """
    
    def __init__(self, settings: Optional[Settings] = None):
        """
        Initialize the newsletter pipeline.
        
        Args:
            settings: Application settings
        """
        self.settings = settings or get_settings()
        self.logger = self._setup_logger()
        
        # Initialize components
        self.scrapers: List[BaseScraper] = []
        self.newsletter_generator: Optional[NewsletterGenerator] = None
        self.email_sender: Optional[EmailSender] = None
        
        self._initialize_components()
    
    def _setup_logger(self) -> logging.Logger:
        """Set up logger for the pipeline."""
        logger = logging.getLogger(f"{self.__class__.__name__}")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def _initialize_components(self):
        """Initialize all pipeline components."""
        # Initialize scrapers
        self._initialize_scrapers()
        
        # Initialize newsletter generator
        self._initialize_newsletter_generator()
        
        # Initialize email sender
        self._initialize_email_sender()
    
    def _initialize_scrapers(self):
        """Initialize configured scrapers."""
        # Reddit scraper
        if self.settings.reddit.enabled and self.settings.reddit.subreddits:
            try:
                reddit_scraper = RedditScraper()
                self.scrapers.append(reddit_scraper)
                self.logger.info("Reddit scraper initialized")
            except Exception as e:
                self.logger.error(f"Failed to initialize Reddit scraper: {e}")
        
        # RSS scraper
        if self.settings.rss.enabled and self.settings.rss.feed_urls:
            try:
                rss_scraper = RSSFeedScraper()
                self.scrapers.append(rss_scraper)
                self.logger.info("RSS scraper initialized")
            except Exception as e:
                self.logger.error(f"Failed to initialize RSS scraper: {e}")
        
        # YouTube scraper
        if (self.settings.youtube.enabled and 
            self.settings.youtube.api_key and 
            (self.settings.youtube.channel_ids or 
             self.settings.youtube.channel_usernames or 
             self.settings.youtube.search_queries)):
            try:
                youtube_scraper = YouTubeScraper(api_key=self.settings.youtube.api_key)
                self.scrapers.append(youtube_scraper)
                self.logger.info("YouTube scraper initialized")
            except Exception as e:
                self.logger.error(f"Failed to initialize YouTube scraper: {e}")
    
    def _initialize_newsletter_generator(self):
        """Initialize newsletter generator."""
        if self.settings.newsletter.openai_api_key:
            try:
                self.newsletter_generator = NewsletterGenerator(
                    config=self.settings.newsletter
                )
                self.logger.info("Newsletter generator initialized")
            except Exception as e:
                self.logger.error(f"Failed to initialize newsletter generator: {e}")
        else:
            self.logger.warning("OpenAI API key not configured, newsletter generation disabled")
    
    def _initialize_email_sender(self):
        """Initialize email sender."""
        try:
            self.email_sender = EmailSender(config=self.settings.email)
            self.logger.info("Email sender initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize email sender: {e}")
    
    def run_newsletter_pipeline(
        self,
        recipients: Optional[List[str]] = None,
        custom_title: Optional[str] = None,
        max_items_per_source: int = 10,
        max_total_items: int = 30
    ) -> PipelineResult:
        """
        Run the complete newsletter pipeline.
        
        Args:
            recipients: List of email recipients (if not provided, uses config)
            custom_title: Custom newsletter title
            max_items_per_source: Maximum items per scraper
            max_total_items: Maximum total items
            
        Returns:
            PipelineResult with execution details
        """
        start_time = datetime.now()
        errors = []
        
        try:
            self.logger.info("Starting newsletter pipeline")
            
            # Step 1: Scrape content
            all_items = self._scrape_content(max_items_per_source)
            self.logger.info(f"Scraped {len(all_items)} items from {len(self.scrapers)} sources")
            
            if not all_items:
                errors.append("No content items scraped")
                return PipelineResult(
                    success=False,
                    items_scraped=0,
                    newsletter_generated=False,
                    email_sent=False,
                    errors=errors,
                    execution_time=(datetime.now() - start_time).total_seconds(),
                    generated_at=start_time
                )
            
            # Step 2: Filter and sort content
            filtered_items = self._filter_and_sort_content(all_items, max_total_items)
            self.logger.info(f"Filtered to {len(filtered_items)} items")
            
            # Step 3: Generate newsletter
            newsletter_html = None
            if self.newsletter_generator:
                try:
                    newsletter_html = self.newsletter_generator.generate_newsletter(
                        filtered_items,
                        title=custom_title
                    )
                    self.logger.info("Newsletter generated successfully")
                except Exception as e:
                    error_msg = f"Newsletter generation failed: {e}"
                    self.logger.error(error_msg)
                    errors.append(error_msg)
            else:
                errors.append("Newsletter generator not available")
            
            # Step 4: Send email
            email_sent = False
            if newsletter_html and self.email_sender:
                try:
                    recipients = recipients or [self.settings.email.from_email]
                    if recipients:
                        subject = custom_title or f"Daily Newsletter - {datetime.now().strftime('%B %d, %Y')}"
                        
                        for recipient in recipients:
                            success = self.email_sender.send_newsletter(
                                recipient, subject, newsletter_html
                            )
                            if success:
                                email_sent = True
                                self.logger.info(f"Newsletter sent to {recipient}")
                            else:
                                errors.append(f"Failed to send to {recipient}")
                    else:
                        errors.append("No recipients configured")
                except Exception as e:
                    error_msg = f"Email sending failed: {e}"
                    self.logger.error(error_msg)
                    errors.append(error_msg)
            else:
                if not newsletter_html:
                    errors.append("No newsletter content to send")
                if not self.email_sender:
                    errors.append("Email sender not available")
            
            # Determine overall success
            success = len(errors) == 0 and email_sent
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            result = PipelineResult(
                success=success,
                items_scraped=len(all_items),
                newsletter_generated=newsletter_html is not None,
                email_sent=email_sent,
                errors=errors,
                execution_time=execution_time,
                generated_at=start_time
            )
            
            self.logger.info(f"Pipeline completed in {execution_time:.2f} seconds")
            return result
            
        except Exception as e:
            error_msg = f"Pipeline execution failed: {e}"
            self.logger.error(error_msg)
            errors.append(error_msg)
            
            return PipelineResult(
                success=False,
                items_scraped=0,
                newsletter_generated=False,
                email_sent=False,
                errors=errors,
                execution_time=(datetime.now() - start_time).total_seconds(),
                generated_at=start_time
            )
    
    def _scrape_content(self, max_items_per_source: int) -> List[ContentItem]:
        """Scrape content from all configured sources."""
        all_items = []
        
        for scraper in self.scrapers:
            try:
                if isinstance(scraper, RedditScraper):
                    items = scraper.fetch_multiple_subreddits(
                        self.settings.reddit.subreddits,
                        max_items_per_source
                    )
                elif isinstance(scraper, RSSFeedScraper):
                    items = scraper.fetch_multiple_feeds(
                        self.settings.rss.feed_urls,
                        max_items_per_source
                    )
                elif isinstance(scraper, YouTubeScraper):
                    items = []
                    # Fetch from channels
                    for channel_id in self.settings.youtube.channel_ids:
                        channel_items = scraper.fetch_channel(channel_id, max_items_per_source)
                        items.extend(channel_items)
                    # Fetch from usernames
                    for username in self.settings.youtube.channel_usernames:
                        username_items = scraper.fetch_content(
                            channel_username=username, 
                            limit=max_items_per_source
                        )
                        items.extend(username_items)
                    # Search queries
                    for query in self.settings.youtube.search_queries:
                        search_items = scraper.search_videos(query, max_items_per_source)
                        items.extend(search_items)
                else:
                    # Generic scraper
                    items = scraper.fetch_content(limit=max_items_per_source)
                
                all_items.extend(items)
                self.logger.info(f"Scraped {len(items)} items from {scraper.source_name}")
                
            except Exception as e:
                self.logger.error(f"Failed to scrape from {scraper.source_name}: {e}")
                continue
        
        return all_items
    
    def _filter_and_sort_content(
        self, 
        items: List[ContentItem], 
        max_items: int
    ) -> List[ContentItem]:
        """Filter and sort content items."""
        if not items:
            return []
        
        # Filter by date (last 7 days)
        cutoff_date = datetime.now() - timedelta(days=7)
        recent_items = [
            item for item in items 
            if item.created_at >= cutoff_date
        ]
        
        # Sort by score (engagement)
        sorted_items = sorted(
            recent_items,
            key=lambda x: (x.score + x.comments_count + x.views_count),
            reverse=True
        )
        
        # Remove duplicates based on title similarity
        unique_items = []
        seen_titles = set()
        
        for item in sorted_items:
            title_lower = item.title.lower()
            if title_lower not in seen_titles:
                unique_items.append(item)
                seen_titles.add(title_lower)
        
        return unique_items[:max_items]
    
    def preview_newsletter(
        self,
        max_items_per_source: int = 10,
        max_total_items: int = 30
    ) -> Optional[Dict[str, Any]]:
        """
        Generate a preview of the newsletter without sending.
        
        Args:
            max_items_per_source: Maximum items per scraper
            max_total_items: Maximum total items
            
        Returns:
            Newsletter preview data or None if failed
        """
        try:
            # Scrape and filter content
            all_items = self._scrape_content(max_items_per_source)
            filtered_items = self._filter_and_sort_content(all_items, max_total_items)
            
            if not filtered_items:
                return None
            
            # Generate preview
            if self.newsletter_generator:
                preview = self.newsletter_generator.preview_newsletter(filtered_items)
                preview['items_count'] = len(filtered_items)
                preview['sources'] = list(set(item.source for item in filtered_items))
                return preview
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to generate preview: {e}")
            return None
    
    def get_pipeline_status(self) -> Dict[str, Any]:
        """
        Get the current status of the pipeline.
        
        Returns:
            Dictionary with pipeline status information
        """
        status = {
            'scrapers_configured': len(self.scrapers),
            'newsletter_generator_available': self.newsletter_generator is not None,
            'email_sender_available': self.email_sender is not None,
            'settings': {
                'reddit_enabled': self.settings.reddit.enabled,
                'rss_enabled': self.settings.rss.enabled,
                'youtube_enabled': self.settings.youtube.enabled,
                'newsletter_enabled': True,  # Always enabled if generator is available
                'email_enabled': self.email_sender is not None
            },
            'errors': [],
            'warnings': []
        }
        
        # Check for configuration issues
        if not self.scrapers:
            status['warnings'].append("No scrapers configured")
        
        if not self.newsletter_generator:
            status['errors'].append("Newsletter generator not available")
        
        if not self.email_sender:
            status['warnings'].append("Email sender not configured")
        
        # Check API keys
        if not self.settings.newsletter.openai_api_key:
            status['errors'].append("OpenAI API key not configured")
        
        if self.settings.youtube.enabled and not self.settings.youtube.api_key:
            status['warnings'].append("YouTube API key not configured")
        
        return status
