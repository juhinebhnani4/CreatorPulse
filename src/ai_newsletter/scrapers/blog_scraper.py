"""
Blog/Website scraper implementation using web scraping.
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin, urlparse
import json
import re
import time

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
        
        # Extract content with better text handling
        content_elem = raw_item.select_one(content_selector)
        if content_elem:
            # Try to get just paragraphs first (main content)
            paragraphs = content_elem.find_all('p', recursive=True)
            if paragraphs:
                # Get text from paragraphs only, filtering short ones (navigation/boilerplate)
                para_texts = [p.get_text(separator=' ', strip=True) for p in paragraphs]
                para_texts = [p for p in para_texts if len(p) > 50]  # Filter short noise
                content = ' '.join(para_texts)
            else:
                # Fallback: get all text with proper spacing
                content = content_elem.get_text(separator=' ', strip=True)

            # Clean up extra whitespace
            import re
            content = re.sub(r'\s+', ' ', content).strip()
        else:
            content = ''

        # Generate intelligent summary
        summary = self._extract_summary(content, 200, title=title)
        
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

    def _extract_summary(self, content: str, max_length: int = 200, title: str = '') -> str:
        """
        Extract intelligent summary from content.

        Tries to:
        1. Extract first complete sentences up to max_length
        2. Fall back to first paragraph
        3. Fall back to title
        4. Last resort: "No content available"

        Args:
            content: Full content text
            max_length: Maximum summary length
            title: Fallback title if content is empty

        Returns:
            Extracted summary (never empty)
        """
        # Handle empty content upfront
        if not content or not content.strip():
            if title:
                return title[:max_length] + '...' if len(title) > max_length else title
            return "No content available"

        if len(content) <= max_length:
            return content

        import re

        # Try complete sentences
        sentences = re.split(r'(?<=[.!?])\s+', content)
        summary = ''
        for sentence in sentences:
            if len(summary) + len(sentence) + 1 <= max_length:
                summary += sentence + ' '
            else:
                break

        if summary.strip():
            return summary.strip()

        # Try first paragraph
        first_para = content.split('\n\n')[0] if '\n\n' in content else content
        if len(first_para) <= max_length:
            return first_para

        # Last resort: truncate at word boundary
        truncated = content[:max_length]
        last_space = truncated.rfind(' ')
        if last_space > max_length * 0.8:  # If we can save most of it
            truncated = truncated[:last_space]
        return truncated + '...'

    def _extract_opengraph(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """
        Extract Open Graph metadata from HTML.

        Args:
            soup: BeautifulSoup object

        Returns:
            Dictionary of Open Graph metadata
        """
        og_data = {}
        og_tags = soup.find_all('meta', property=re.compile(r'^og:'))

        for tag in og_tags:
            property_name = tag.get('property', '').replace('og:', '')
            content = tag.get('content', '')
            if property_name and content:
                og_data[property_name] = content

        return og_data

    def _extract_twitter_cards(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """
        Extract Twitter Card metadata from HTML.

        Args:
            soup: BeautifulSoup object

        Returns:
            Dictionary of Twitter Card metadata
        """
        twitter_data = {}
        twitter_tags = soup.find_all('meta', attrs={'name': re.compile(r'^twitter:')})

        for tag in twitter_tags:
            name = tag.get('name', '').replace('twitter:', '')
            content = tag.get('content', '')
            if name and content:
                twitter_data[name] = content

        return twitter_data

    def _extract_jsonld(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """
        Extract JSON-LD structured data from HTML.

        Args:
            soup: BeautifulSoup object

        Returns:
            List of JSON-LD objects
        """
        jsonld_data = []
        scripts = soup.find_all('script', type='application/ld+json')

        for script in scripts:
            try:
                data = json.loads(script.string)
                # Handle both single objects and arrays
                if isinstance(data, list):
                    jsonld_data.extend(data)
                else:
                    jsonld_data.append(data)
            except (json.JSONDecodeError, AttributeError):
                continue

        return jsonld_data

    def _extract_meta_tags(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """
        Extract standard HTML meta tags.

        Args:
            soup: BeautifulSoup object

        Returns:
            Dictionary of meta tag data
        """
        meta_data = {}

        # Description
        description_tag = soup.find('meta', attrs={'name': 'description'})
        if description_tag:
            meta_data['description'] = description_tag.get('content', '')

        # Author
        author_tag = soup.find('meta', attrs={'name': 'author'})
        if author_tag:
            meta_data['author'] = author_tag.get('content', '')

        # Keywords
        keywords_tag = soup.find('meta', attrs={'name': 'keywords'})
        if keywords_tag:
            keywords_str = keywords_tag.get('content', '')
            meta_data['keywords'] = [k.strip() for k in keywords_str.split(',')]

        # Date
        date_tag = soup.find('meta', attrs={'name': re.compile(r'date|published', re.I)})
        if date_tag:
            meta_data['date'] = date_tag.get('content', '')

        return meta_data

    def _detect_platform(self, url: str, soup: BeautifulSoup) -> str:
        """
        Auto-detect blog platform from URL and HTML.

        Args:
            url: Page URL
            soup: BeautifulSoup object

        Returns:
            Platform name ('wordpress', 'medium', 'ghost', 'substack', or 'generic')
        """
        # Check URL patterns first (fastest)
        domain = urlparse(url).netloc.lower()

        if 'medium.com' in domain or 'towardsdatascience.com' in domain:
            return 'medium'
        if 'substack.com' in domain:
            return 'substack'
        if 'ghost.io' in domain or 'ghost.org' in domain:
            return 'ghost'

        # Check generator meta tag
        generator_tag = soup.find('meta', attrs={'name': 'generator'})
        if generator_tag:
            generator = generator_tag.get('content', '').lower()
            if 'wordpress' in generator:
                return 'wordpress'
            if 'ghost' in generator:
                return 'ghost'
            if 'jekyll' in generator or 'hugo' in generator:
                return 'generic'  # Static site generators

        # Check for WordPress-specific patterns
        if (soup.find(class_=re.compile(r'wp-')) or
            soup.find('link', href=re.compile(r'wp-content|wp-includes'))):
            return 'wordpress'

        # Check for Ghost-specific patterns
        if soup.find(class_=re.compile(r'post-card|ghost')):
            return 'ghost'

        # Check for Medium-specific patterns
        if soup.find('meta', property='al:android:app_name', content='Medium'):
            return 'medium'

        # Default to generic
        self.logger.info(f"Could not detect platform for {url}, using generic extraction")
        return 'generic'

    def _extract_with_trafilatura(self, html_content: str, url: str) -> Dict[str, Any]:
        """
        Extract article content using trafilatura.

        Args:
            html_content: Raw HTML content
            url: Page URL

        Returns:
            Dictionary with extracted content
        """
        try:
            import trafilatura

            # Extract main content
            extracted = trafilatura.extract(
                html_content,
                include_comments=False,
                include_tables=False,
                no_fallback=False,  # Use fallback methods
                favor_precision=False,  # Favor recall over precision
                url=url
            )

            # Extract metadata
            metadata = trafilatura.extract_metadata(html_content)

            result = {}
            if extracted:
                result['content'] = extracted
                # Generate summary from extracted content (no title available here)
                result['summary'] = self._extract_summary(extracted, 200, title='')

            if metadata:
                if metadata.title:
                    result['title'] = metadata.title
                if metadata.author:
                    result['author'] = metadata.author
                if metadata.date:
                    result['date'] = metadata.date
                if metadata.description:
                    result['description'] = metadata.description
                if metadata.categories:
                    result['tags'] = metadata.categories
                if metadata.image:
                    result['image_url'] = metadata.image

            return result

        except ImportError:
            self.logger.warning("trafilatura not installed, falling back to template extraction")
            return {}
        except Exception as e:
            self.logger.warning(f"trafilatura extraction failed: {e}")
            return {}

    def fetch_content_smart(
        self,
        url: str,
        limit: int = 10,
        force_template: Optional[str] = None
    ) -> List[ContentItem]:
        """
        Intelligently fetch blog content using multiple extraction methods with fallback chain.

        This method:
        1. Auto-detects blog platform (unless force_template specified)
        2. Tries trafilatura extraction (most reliable)
        3. Extracts metadata from Open Graph, JSON-LD, Twitter Cards
        4. Falls back to template-based extraction
        5. Merges all sources to maximize data completeness

        Args:
            url: Blog URL to scrape
            limit: Maximum number of articles to fetch
            force_template: Optional platform template to use instead of auto-detection

        Returns:
            List of ContentItem objects with maximum data completeness
        """
        try:
            self.logger.info(f"Smart scraping: {url}")
            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            html_content = response.content
            soup = BeautifulSoup(html_content, 'html.parser')

            # Auto-detect platform or use forced template
            if force_template and force_template != 'auto':
                platform = force_template
                self.logger.info(f"Using forced template: {platform}")
            else:
                platform = self._detect_platform(url, soup)
                self.logger.info(f"Detected platform: {platform}")

            # Extract using trafilatura (primary method)
            trafilatura_data = self._extract_with_trafilatura(html_content.decode('utf-8', errors='ignore'), url)

            # Extract metadata from various sources
            og_data = self._extract_opengraph(soup)
            twitter_data = self._extract_twitter_cards(soup)
            jsonld_data = self._extract_jsonld(soup)
            meta_data = self._extract_meta_tags(soup)

            # Try to find articles in JSON-LD
            articles_from_jsonld = []
            for item in jsonld_data:
                if item.get('@type') in ['Article', 'BlogPosting', 'NewsArticle']:
                    articles_from_jsonld.append(item)

            items = []

            # If this is a single article page (most common case)
            if trafilatura_data or og_data or articles_from_jsonld:
                item = self._create_item_from_multiple_sources(
                    url=url,
                    trafilatura_data=trafilatura_data,
                    og_data=og_data,
                    twitter_data=twitter_data,
                    jsonld_data=articles_from_jsonld[0] if articles_from_jsonld else {},
                    meta_data=meta_data,
                    soup=soup
                )

                if self.validate_item(item):
                    items.append(item)

            # If no items yet or if this looks like a list page, try template-based extraction
            if not items or limit > 1:
                template_items = self.fetch_with_template(url, platform, limit)
                items.extend(template_items)

            # Remove duplicates based on URL
            seen_urls = set()
            unique_items = []
            for item in items:
                if item.source_url not in seen_urls:
                    seen_urls.add(item.source_url)
                    unique_items.append(item)

            self.logger.info(f"Smart scraping extracted {len(unique_items)} unique items from {url}")
            return unique_items[:limit]

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error fetching {url}: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Error in smart scraping {url}: {e}")
            return []

    def _create_item_from_multiple_sources(
        self,
        url: str,
        trafilatura_data: Dict[str, Any],
        og_data: Dict[str, Any],
        twitter_data: Dict[str, Any],
        jsonld_data: Dict[str, Any],
        meta_data: Dict[str, Any],
        soup: BeautifulSoup
    ) -> ContentItem:
        """
        Create ContentItem by merging data from multiple extraction sources.

        Uses priority system: trafilatura > JSON-LD > Open Graph > Twitter Cards > meta tags > fallback

        Args:
            url: Page URL
            trafilatura_data: Data from trafilatura extraction
            og_data: Open Graph metadata
            twitter_data: Twitter Card metadata
            jsonld_data: JSON-LD structured data
            meta_data: Standard meta tags
            soup: BeautifulSoup object for fallback extraction

        Returns:
            ContentItem with maximum data completeness
        """
        from dateutil import parser as date_parser

        # Title (priority: trafilatura > JSON-LD > OG > title tag)
        title = (
            trafilatura_data.get('title') or
            jsonld_data.get('headline') or
            jsonld_data.get('name') or
            og_data.get('title') or
            twitter_data.get('title') or
            (soup.find('title').get_text(strip=True) if soup.find('title') else None) or
            'Untitled'
        )

        # Content (priority: trafilatura > JSON-LD > OG description)
        content = (
            trafilatura_data.get('content') or
            jsonld_data.get('articleBody') or
            ''
        )

        # Summary (priority: trafilatura > OG > Twitter > meta description > content > title)
        summary = (
            trafilatura_data.get('summary') or
            og_data.get('description') or
            twitter_data.get('description') or
            meta_data.get('description') or
            jsonld_data.get('description') or
            self._extract_summary(content, 200, title=title)
        )

        # Author (priority: trafilatura > JSON-LD > OG > meta)
        author = None
        if trafilatura_data.get('author'):
            author = trafilatura_data['author']
        elif jsonld_data.get('author'):
            author_data = jsonld_data['author']
            if isinstance(author_data, dict):
                author = author_data.get('name')
            elif isinstance(author_data, str):
                author = author_data
        elif og_data.get('article:author'):
            author = og_data['article:author']
        elif meta_data.get('author'):
            author = meta_data['author']

        # Date (priority: trafilatura > JSON-LD > OG > meta)
        created_at = datetime.now()
        date_str = (
            trafilatura_data.get('date') or
            jsonld_data.get('datePublished') or
            og_data.get('article:published_time') or
            og_data.get('published_time') or
            meta_data.get('date')
        )

        if date_str:
            try:
                created_at = date_parser.parse(date_str, fuzzy=True)
            except:
                pass

        # Image (priority: OG > Twitter > JSON-LD > trafilatura)
        image_url = (
            og_data.get('image') or
            twitter_data.get('image') or
            (jsonld_data.get('image', {}).get('url') if isinstance(jsonld_data.get('image'), dict) else jsonld_data.get('image')) or
            trafilatura_data.get('image_url')
        )

        # Make image URL absolute
        if image_url and not image_url.startswith('http'):
            image_url = urljoin(url, image_url)

        # Tags (priority: JSON-LD > meta keywords > trafilatura)
        tags = []
        if jsonld_data.get('keywords'):
            keywords = jsonld_data['keywords']
            if isinstance(keywords, list):
                tags = keywords
            elif isinstance(keywords, str):
                tags = [k.strip() for k in keywords.split(',')]
        elif meta_data.get('keywords'):
            tags = meta_data['keywords']
        elif trafilatura_data.get('tags'):
            tags = trafilatura_data['tags']

        # Category
        category = None
        if jsonld_data.get('articleSection'):
            category = jsonld_data['articleSection']
        elif tags:
            category = tags[0]
        else:
            category = urlparse(url).netloc

        # Create ContentItem
        item = ContentItem(
            title=title,
            source=self.source_name,
            source_url=url,
            created_at=created_at,
            content=content,
            summary=summary,
            author=author,
            image_url=image_url,
            external_url=url,
            tags=tags[:5] if tags else [],  # Limit to 5 tags
            category=category,
            metadata={
                'domain': urlparse(url).netloc,
                'extraction_method': 'smart_multi_source',
                'has_trafilatura': bool(trafilatura_data),
                'has_jsonld': bool(jsonld_data),
                'has_opengraph': bool(og_data),
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

    # =========================================================================
    # Link Crawling Support
    # =========================================================================

    def supports_link_crawling(self) -> bool:
        """Enable deep link crawling for BlogScraper."""
        return True

    def _extract_article_links(
        self,
        soup: BeautifulSoup,
        base_url: str,
        limit: int = 10
    ) -> List[str]:
        """
        Extract article links from a blog list/index page.

        Filters out common non-article pages like:
        - About, Contact, Privacy pages
        - Tag/Category archive pages
        - Author pages
        - Navigation links

        Args:
            soup: BeautifulSoup object of the list page
            base_url: Base URL for resolving relative links
            limit: Maximum number of links to extract

        Returns:
            List of deduplicated article URLs
        """
        article_links = []
        seen_urls = set()

        # URL patterns to exclude (navigation, metadata pages)
        exclude_patterns = [
            r'/about',
            r'/contact',
            r'/privacy',
            r'/terms',
            r'/tag/',
            r'/tags/',
            r'/category/',
            r'/categories/',
            r'/author/',
            r'/page/',
            r'/search',
            r'/archive',
            r'#',  # Anchor links
        ]

        # Try multiple strategies to find article links

        # Strategy 1: Look for article elements with links
        articles = soup.find_all('article')
        for article in articles:
            link = article.find('a', href=True)
            if link:
                full_url = urljoin(base_url, link['href'])
                article_links.append(full_url)

        # Strategy 2: Look for common article link patterns
        if len(article_links) < limit:
            # h1, h2, h3 headings often contain article links
            headings = soup.find_all(['h1', 'h2', 'h3'])
            for heading in headings:
                link = heading.find('a', href=True)
                if link:
                    full_url = urljoin(base_url, link['href'])
                    article_links.append(full_url)

        # Strategy 3: Look for links with common article CSS classes
        if len(article_links) < limit:
            article_selectors = [
                '.post-title a',
                '.entry-title a',
                '.article-title a',
                '.post-link',
                '.entry-link',
                'a[rel="bookmark"]'
            ]
            for selector in article_selectors:
                links = soup.select(selector)
                for link in links:
                    if link.has_attr('href'):
                        full_url = urljoin(base_url, link['href'])
                        article_links.append(full_url)

        # Filter and deduplicate
        filtered_links = []
        base_domain = urlparse(base_url).netloc

        for url in article_links:
            # Skip if already seen
            normalized_url = self._normalize_url(url)
            if normalized_url in seen_urls:
                continue

            # Skip external links (keep same domain only)
            if urlparse(url).netloc != base_domain:
                continue

            # Skip excluded patterns
            if any(re.search(pattern, url, re.IGNORECASE) for pattern in exclude_patterns):
                continue

            # Skip if URL is too short (likely homepage or index)
            if len(urlparse(url).path) < 2:
                continue

            filtered_links.append(url)
            seen_urls.add(normalized_url)

            if len(filtered_links) >= limit:
                break

        self.logger.info(f"Extracted {len(filtered_links)} article links from {base_url}")
        return filtered_links

    def _normalize_url(self, url: str) -> str:
        """
        Normalize URL for deduplication.

        Removes:
        - Trailing slashes
        - URL fragments (#anchors)
        - Common tracking parameters
        - www prefix

        Args:
            url: URL to normalize

        Returns:
            Normalized URL string
        """
        from urllib.parse import urlparse, urlunparse, parse_qs, urlencode

        parsed = urlparse(url)

        # Remove www prefix
        netloc = parsed.netloc.lower()
        if netloc.startswith('www.'):
            netloc = netloc[4:]

        # Remove tracking parameters
        tracking_params = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term', 'ref', 'source']
        query_params = parse_qs(parsed.query)
        cleaned_params = {k: v for k, v in query_params.items() if k not in tracking_params}
        query = urlencode(cleaned_params, doseq=True)

        # Remove fragment
        fragment = ''

        # Remove trailing slash from path
        path = parsed.path.rstrip('/')

        normalized = urlunparse((
            parsed.scheme,
            netloc,
            path,
            parsed.params,
            query,
            fragment
        ))

        return normalized

    def _fetch_full_item(
        self,
        article_url: str,
        delay: float = 1.0,
        timeout: int = 30
    ) -> Optional[ContentItem]:
        """
        Fetch full content from an individual article page.

        Uses fetch_content_smart with all extraction methods:
        - Trafilatura (primary)
        - JSON-LD structured data
        - Open Graph metadata
        - Twitter Cards
        - Fallback to template extraction

        Safeguards:
        - Configurable delay between requests
        - Timeout protection
        - Error isolation (returns None on failure)

        Args:
            article_url: URL of the article to fetch
            delay: Delay in seconds before fetching (rate limiting)
            timeout: Request timeout in seconds

        Returns:
            ContentItem with full article data, or None if fetch failed
        """
        # Rate limiting
        if delay > 0:
            time.sleep(delay)

        try:
            self.logger.info(f"Fetching full article: {article_url}")

            # Use existing smart extraction with timeout
            old_timeout = self.session.timeout if hasattr(self.session, 'timeout') else None

            response = self.session.get(article_url, timeout=timeout)
            response.raise_for_status()

            html_content = response.content
            soup = BeautifulSoup(html_content, 'html.parser')

            # Extract using trafilatura (primary method)
            trafilatura_data = self._extract_with_trafilatura(
                html_content.decode('utf-8', errors='ignore'),
                article_url
            )

            # Extract metadata from various sources
            og_data = self._extract_opengraph(soup)
            twitter_data = self._extract_twitter_cards(soup)
            jsonld_data = self._extract_jsonld(soup)
            meta_data = self._extract_meta_tags(soup)

            # Find article in JSON-LD
            article_jsonld = {}
            for item in jsonld_data:
                if item.get('@type') in ['Article', 'BlogPosting', 'NewsArticle']:
                    article_jsonld = item
                    break

            # Create item from multiple sources
            item = self._create_item_from_multiple_sources(
                url=article_url,
                trafilatura_data=trafilatura_data,
                og_data=og_data,
                twitter_data=twitter_data,
                jsonld_data=article_jsonld,
                meta_data=meta_data,
                soup=soup
            )

            if self.validate_item(item):
                self.logger.info(f"Successfully fetched article: {item.title}")
                return item
            else:
                self.logger.warning(f"Invalid item extracted from {article_url}")
                return None

        except requests.exceptions.Timeout:
            self.logger.warning(f"Timeout fetching {article_url} (>{timeout}s)")
            return None
        except requests.exceptions.RequestException as e:
            self.logger.warning(f"Request error fetching {article_url}: {e}")
            return None
        except Exception as e:
            self.logger.warning(f"Error fetching full article {article_url}: {e}")
            return None

    def fetch_content_with_crawling(
        self,
        url: str,
        limit: int = 10,
        crawl_delay: float = 1.0,
        crawl_timeout: int = 30,
        force_template: Optional[str] = None,
        progress_callback: Optional[callable] = None
    ) -> List[ContentItem]:
        """
        Fetch blog content with deep link crawling.

        This method:
        1. Fetches the list/index page
        2. Extracts article links
        3. Crawls each article page for full content
        4. Falls back to preview extraction if crawling fails

        Args:
            url: Blog URL to scrape
            limit: Maximum number of articles to fetch
            crawl_delay: Delay between requests (seconds, for rate limiting)
            crawl_timeout: Timeout for each article fetch (seconds)
            force_template: Optional platform template override
            progress_callback: Optional callback(current, total, article_url) for progress updates

        Returns:
            List of ContentItem objects with maximum data completeness
        """
        try:
            self.logger.info(f"Starting crawling scrape of {url}")

            # Step 1: Fetch list page
            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            html_content = response.content
            soup = BeautifulSoup(html_content, 'html.parser')

            # Step 2: Extract article links
            article_links = self._extract_article_links(soup, url, limit)

            if not article_links:
                self.logger.warning(f"No article links found on {url}, falling back to preview extraction")
                return self.fetch_content_smart(url, limit, force_template)

            # Step 3: Crawl each article
            items = []
            failed_count = 0

            for idx, article_url in enumerate(article_links, 1):
                # Progress callback
                if progress_callback:
                    progress_callback(idx, len(article_links), article_url)

                # Fetch full article
                item = self._fetch_full_item(
                    article_url,
                    delay=crawl_delay,
                    timeout=crawl_timeout
                )

                if item:
                    items.append(item)
                else:
                    failed_count += 1
                    self.logger.warning(f"Failed to fetch {article_url}, continuing...")

            # Log success rate
            success_rate = (len(items) / len(article_links) * 100) if article_links else 0
            self.logger.info(
                f"Crawling complete: {len(items)}/{len(article_links)} articles "
                f"({success_rate:.1f}% success rate)"
            )

            # If crawling mostly failed, fall back to preview extraction
            if len(items) == 0:
                self.logger.warning("All crawling attempts failed, falling back to preview extraction")
                return self.fetch_content_smart(url, limit, force_template)

            return items

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error fetching list page {url}: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Error in crawling scrape {url}: {e}")
            return []

