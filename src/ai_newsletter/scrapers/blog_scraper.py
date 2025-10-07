"""
Blog/Website scraper implementation using web scraping.
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin, urlparse

from .base import BaseScraper
from ..models.content import ContentItem


class BlogScraper(BaseScraper):
    """
    Scraper for blog posts and articles using web scraping.
    
    This scraper extracts content from blog pages using BeautifulSoup.
    It can be configured with CSS selectors for different blog platforms.
    
    Example:
        scraper = BlogScraper()
        items = scraper.fetch_content(
            url='https://blog.example.com',
            article_selector='.post',
            limit=10
        )
        df = scraper.to_dataframe(items)
    """
    
    def __init__(self, user_agent: str = "AINewsletterScraper/1.0", **kwargs):
        """
        Initialize the blog scraper.
        
        Args:
            user_agent: User agent string for requests
            **kwargs: Additional configuration options
        """
        super().__init__(source_name="blog", source_type="web", **kwargs)
        
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': user_agent})
    
    def fetch_content(
        self,
        limit: int = 10,
        url: Optional[str] = None,
        urls: Optional[List[str]] = None,
        article_selector: str = 'article',
        title_selector: str = 'h1, h2, .title',
        content_selector: str = '.content, .post-content, article',
        date_selector: str = 'time, .date, .published',
        author_selector: str = '.author, .by-line',
        **kwargs
    ) -> List[ContentItem]:
        """
        Fetch blog posts from web pages.
        
        Args:
            limit: Maximum number of articles to fetch
            url: Single URL to scrape
            urls: List of URLs to scrape
            article_selector: CSS selector for article containers
            title_selector: CSS selector for titles
            content_selector: CSS selector for content
            date_selector: CSS selector for dates
            author_selector: CSS selector for authors
            **kwargs: Additional parameters
            
        Returns:
            List of ContentItem objects
        """
        page_urls = []
        if url:
            page_urls.append(url)
        if urls:
            page_urls.extend(urls)
        
        if not page_urls:
            self.logger.warning("No URLs provided")
            return []
        
        all_items = []
        
        for page_url in page_urls:
            try:
                self.logger.info(f"Scraping {page_url}")
                response = self.session.get(page_url, timeout=10)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find all articles
                articles = soup.select(article_selector)[:limit]
                
                for article in articles:
                    try:
                        item = self._parse_item(
                            article,
                            base_url=page_url,
                            title_selector=title_selector,
                            content_selector=content_selector,
                            date_selector=date_selector,
                            author_selector=author_selector
                        )
                        
                        if self.validate_item(item):
                            all_items.append(item)
                    except Exception as e:
                        self.logger.warning(f"Failed to parse article: {e}")
                        continue
                
                self.logger.info(f"Successfully scraped {len(articles)} articles from {page_url}")
                
            except requests.exceptions.RequestException as e:
                self.logger.error(f"Error fetching {page_url}: {e}")
                continue
            except Exception as e:
                self.logger.error(f"Error parsing {page_url}: {e}")
                continue
        
        return all_items[:limit]
    
    def _parse_item(
        self,
        raw_item: Any,
        base_url: str,
        title_selector: str,
        content_selector: str,
        date_selector: str,
        author_selector: str
    ) -> ContentItem:
        """
        Parse a blog article into a ContentItem.
        
        Args:
            raw_item: BeautifulSoup element containing the article
            base_url: Base URL for resolving relative links
            title_selector: CSS selector for title
            content_selector: CSS selector for content
            date_selector: CSS selector for date
            author_selector: CSS selector for author
            
        Returns:
            ContentItem object
        """
        # Extract title
        title_elem = raw_item.select_one(title_selector)
        title = title_elem.get_text(strip=True) if title_elem else 'Untitled'
        
        # Extract link
        link_elem = raw_item.find('a', href=True)
        if link_elem:
            link = urljoin(base_url, link_elem['href'])
        else:
            link = base_url
        
        # Extract content
        content_elem = raw_item.select_one(content_selector)
        content = content_elem.get_text(strip=True) if content_elem else ''
        summary = content[:200] + '...' if len(content) > 200 else content
        
        # Extract date
        date_elem = raw_item.select_one(date_selector)
        created_at = datetime.now()
        if date_elem:
            date_str = date_elem.get('datetime') or date_elem.get_text(strip=True)
            try:
                # Try to parse common date formats
                from dateutil import parser
                created_at = parser.parse(date_str, fuzzy=True)
            except:
                pass
        
        # Extract author
        author = None
        author_elem = raw_item.select_one(author_selector)
        if author_elem:
            author = author_elem.get_text(strip=True)
        
        # Extract image
        image_url = None
        img_elem = raw_item.find('img', src=True)
        if img_elem:
            image_url = urljoin(base_url, img_elem['src'])
        
        # Extract tags/categories
        tags = []
        tag_elems = raw_item.select('.tag, .category, .label')
        for tag_elem in tag_elems:
            tag = tag_elem.get_text(strip=True)
            if tag:
                tags.append(tag)
        
        # Domain as category
        domain = urlparse(base_url).netloc
        
        # Create ContentItem
        item = ContentItem(
            title=title,
            source=self.source_name,
            source_url=link,
            created_at=created_at,
            content=content,
            summary=summary,
            author=author,
            image_url=image_url,
            external_url=link,
            tags=tags,
            category=tags[0] if tags else domain,
            metadata={
                'domain': domain,
                'base_url': base_url,
            }
        )
        
        return item
    
    def fetch_with_template(
        self,
        url: str,
        template_name: str,
        limit: int = 10
    ) -> List[ContentItem]:
        """
        Fetch content using a predefined template for popular platforms.
        
        Args:
            url: URL to scrape
            template_name: Name of the template ('medium', 'wordpress', 'ghost', etc.)
            limit: Maximum number of articles
            
        Returns:
            List of ContentItem objects
        """
        templates = {
            'medium': {
                'article_selector': 'article',
                'title_selector': 'h1, h2',
                'content_selector': 'article section',
                'date_selector': 'time',
                'author_selector': 'a[rel="author"]',
            },
            'wordpress': {
                'article_selector': 'article, .post',
                'title_selector': '.entry-title, h1, h2',
                'content_selector': '.entry-content, .post-content',
                'date_selector': '.published, time',
                'author_selector': '.author, .by-line',
            },
            'ghost': {
                'article_selector': 'article, .post-card',
                'title_selector': '.post-card-title, h1',
                'content_selector': '.post-content, .post-card-excerpt',
                'date_selector': 'time',
                'author_selector': '.author-name',
            },
            'substack': {
                'article_selector': '.post, article',
                'title_selector': 'h1',
                'content_selector': '.body, .available-content',
                'date_selector': 'time',
                'author_selector': '.author',
            },
        }
        
        template = templates.get(template_name.lower())
        if not template:
            self.logger.warning(f"Unknown template: {template_name}")
            template = templates['wordpress']  # Default fallback
        
        return self.fetch_content(url=url, limit=limit, **template)

