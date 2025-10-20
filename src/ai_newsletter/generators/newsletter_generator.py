"""
Newsletter generation engine using OpenAI.
"""

import os
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging
from pathlib import Path

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

from ..models.content import ContentItem
from ..config.settings import NewsletterConfig


class NewsletterGenerator:
    """
    Newsletter generation engine using OpenAI.
    
    Converts ContentItems into formatted newsletters using AI.
    
    Example:
        generator = NewsletterGenerator(config=newsletter_config)
        newsletter_html = generator.generate_newsletter(content_items)
    """
    
    def __init__(self, api_key: Optional[str] = None, config: Optional[NewsletterConfig] = None):
        """
        Initialize the newsletter generator.
        
        Args:
            api_key: OpenAI API key (if not provided, will use config)
            config: Newsletter configuration
        """
        # If no config provided, try to load from settings
        if config is None:
            try:
                from ..config.settings import get_settings
                settings = get_settings()
                config = settings.newsletter
            except Exception:
                config = NewsletterConfig()
        
        self.config = config

        # Only use api_key parameter if config doesn't already have one
        if not self.config.openai_api_key and api_key:
            self.config.openai_api_key = api_key

        if not OpenAI:
            raise ImportError("OpenAI package is required. Install with: pip install openai")

        # Initialize client based on provider
        if self.config.use_openrouter:
            if not self.config.openrouter_api_key:
                raise ValueError("OpenRouter API key is required when use_openrouter is True")
            self.client = OpenAI(
                api_key=self.config.openrouter_api_key,
                base_url="https://openrouter.ai/api/v1"
            )
            self.model = self.config.openrouter_model
            self.logger = self._setup_logger()
            self.logger.info(f"Initialized with OpenRouter (model: {self.model})")
        else:
            if not self.config.openai_api_key:
                raise ValueError("OpenAI API key is required")
            self.client = OpenAI(api_key=self.config.openai_api_key)
            self.model = self.config.model
            self.logger = self._setup_logger()
            self.logger.info(f"Initialized with OpenAI (model: {self.model})")
        
        # Load templates
        self.templates = self._load_templates()
    
    def _setup_logger(self) -> logging.Logger:
        """Set up logger for the generator."""
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
    
    def _load_templates(self) -> Dict[str, str]:
        """Load HTML templates."""
        templates = {}
        templates_dir = Path(__file__).parent / "templates"
        
        if templates_dir.exists():
            for template_file in templates_dir.glob("*.html"):
                try:
                    with open(template_file, 'r', encoding='utf-8') as f:
                        templates[template_file.stem] = f.read()
                except Exception as e:
                    self.logger.warning(f"Failed to load template {template_file}: {e}")
        
        # Add default template if none loaded
        if not templates:
            templates['default'] = self._get_default_template()
        
        return templates
    
    def _get_default_template(self) -> str:
        """Get default HTML template."""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{title}}</title>
    <style>
        * { box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            background: #ffffff;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px 20px;
            text-align: center;
            border-radius: 8px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .header h1 { margin: 0 0 10px 0; font-size: 28px; }
        .header p { margin: 0; opacity: 0.9; }
        .intro {
            margin-bottom: 30px;
            font-size: 16px;
            line-height: 1.8;
        }
        .content-item {
            margin-bottom: 30px;
            padding: 20px;
            border-left: 4px solid #667eea;
            background: #f8f9fa;
            border-radius: 4px;
            transition: transform 0.2s;
        }
        .content-item:hover {
            transform: translateX(4px);
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        .content-item h3 {
            margin-top: 0;
            color: #2d3748;
            font-size: 20px;
            line-height: 1.4;
        }
        .content-item h3 a {
            color: #667eea;
            text-decoration: none;
            border-bottom: 2px solid transparent;
            transition: border-color 0.2s;
        }
        .content-item h3 a:hover {
            border-bottom-color: #667eea;
        }
        .content-item .meta {
            font-size: 13px;
            color: #718096;
            margin-bottom: 12px;
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
        }
        .content-item .meta span {
            display: inline-flex;
            align-items: center;
            gap: 4px;
        }
        .content-item .summary {
            margin: 0;
            line-height: 1.6;
            color: #4a5568;
        }
        .footer {
            margin-top: 40px;
            padding-top: 20px;
            border-top: 2px solid #e2e8f0;
            text-align: center;
            color: #718096;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>{{title}}</h1>
        <p>{{date}}</p>
    </div>

    <div class="intro">
        {{intro}}
    </div>

    <div class="content">
        {{content}}
    </div>

    <div class="footer">
        <p>{{footer}}</p>
    </div>
</body>
</html>
        """

    def _score_content_item(self, item: ContentItem) -> float:
        """
        Score a content item based on multiple factors.

        Scoring factors:
        - Engagement: score, comments, views
        - Recency: newer items ranked higher
        - Content quality: has summary, has author
        - Source diversity bonus

        Args:
            item: ContentItem to score

        Returns:
            Float score (higher is better)
        """
        score = 0.0

        # Engagement score (40% weight)
        # Normalize by source type (Reddit vs YouTube have different scales)
        if item.source == 'reddit':
            score += min(item.score / 100, 10)  # Cap at 10 points
            score += min(item.comments_count / 20, 5)  # Cap at 5 points
        elif item.source == 'youtube':
            score += min(item.views_count / 10000, 10)  # Cap at 10 points
            score += min(item.comments_count / 50, 5)  # Cap at 5 points
        else:
            # Generic scoring
            score += min(item.score / 50, 10)
            score += min(item.comments_count / 10, 5)

        # Recency score (20% weight)
        # Handle both timezone-aware and timezone-naive datetimes
        now = datetime.now(item.created_at.tzinfo) if item.created_at.tzinfo else datetime.now()
        age_hours = (now - item.created_at).total_seconds() / 3600
        if age_hours < 6:
            score += 5  # Very recent
        elif age_hours < 24:
            score += 3  # Today
        elif age_hours < 48:
            score += 1  # Yesterday

        # Content quality score (20% weight)
        if item.summary and len(item.summary) > 50:
            score += 3
        if item.author and item.author != 'Unknown':
            score += 2
        if item.content and len(item.content) > 200:
            score += 2
        if item.image_url:
            score += 1
        if item.tags and len(item.tags) > 0:
            score += 2

        return score

    def _select_diverse_content(
        self,
        items: List[ContentItem],
        max_items: int = 10,
        max_per_source: int = 3
    ) -> List[ContentItem]:
        """
        Select diverse, high-quality content with intelligent ranking.

        Strategy:
        1. Score all items
        2. Sort by score
        3. Ensure source diversity (max N per source)
        4. Deduplicate by title similarity

        Args:
            items: List of all content items
            max_items: Maximum items to select
            max_per_source: Maximum items per source

        Returns:
            List of selected ContentItems, sorted by score
        """
        if not items:
            return []

        # Score all items
        scored_items = []
        for item in items:
            score = self._score_content_item(item)
            scored_items.append((score, item))

        # Sort by score (descending)
        scored_items.sort(key=lambda x: x[0], reverse=True)

        # Select with diversity constraints
        selected = []
        source_counts = {}
        seen_titles = set()

        for score, item in scored_items:
            # Check source diversity
            source = item.source
            if source_counts.get(source, 0) >= max_per_source:
                continue

            # Check title deduplication (simple approach)
            title_normalized = item.title.lower()[:50]  # First 50 chars
            if title_normalized in seen_titles:
                continue

            # Add item
            selected.append(item)
            source_counts[source] = source_counts.get(source, 0) + 1
            seen_titles.add(title_normalized)

            if len(selected) >= max_items:
                break

        self.logger.info(
            f"Selected {len(selected)} items from {len(items)} total "
            f"(diversity: {len(source_counts)} sources)"
        )

        return selected

    def generate_newsletter(
        self,
        content_items: List[ContentItem],
        title: Optional[str] = None,
        intro: Optional[str] = None,
        footer: Optional[str] = None,
        max_items: int = 10,
        trends: Optional[List[Dict[str, Any]]] = None,
        style_prompt: Optional[str] = None
    ) -> str:
        """
        Generate a newsletter from content items.

        Args:
            content_items: List of ContentItem objects
            title: Newsletter title (if not provided, will be generated)
            intro: Newsletter introduction (if not provided, will be generated)
            footer: Newsletter footer (if not provided, will be generated)
            max_items: Maximum number of items to include
            trends: Optional list of trending topics to highlight
            style_prompt: Optional writing style instructions from style profile

        Returns:
            HTML newsletter content
        """
        if not content_items:
            self.logger.warning("No content items provided")
            return self._generate_empty_newsletter()

        # Intelligently select and rank items
        items = self._select_diverse_content(
            content_items,
            max_items=max_items,
            max_per_source=min(5, max_items // 2)  # At most half from one source
        )

        if not items:
            self.logger.warning("No items selected after filtering")
            return self._generate_empty_newsletter()

        try:
            # Generate content using AI
            generated_content = self._generate_content_with_ai(items, title, intro, footer, trends, style_prompt)

            # Format as HTML
            html_content = self._format_html(generated_content, items, trends)

            self.logger.info(f"Generated newsletter with {len(items)} items")
            return html_content
            
        except Exception as e:
            self.logger.error(f"Error generating newsletter: {e}")
            return self._generate_fallback_newsletter(items)
    
    def _generate_content_with_ai(
        self,
        items: List[ContentItem],
        title: Optional[str] = None,
        intro: Optional[str] = None,
        footer: Optional[str] = None,
        trends: Optional[List[Dict[str, Any]]] = None,
        style_prompt: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Generate newsletter content using OpenAI.

        Args:
            items: List of ContentItem objects
            title: Newsletter title (if not provided, will be generated)
            intro: Newsletter introduction (if not provided, will be generated)
            footer: Newsletter footer (if not provided, will be generated)
            trends: Optional list of trending topics
            style_prompt: Optional writing style instructions

        Returns:
            Dictionary with generated content
        """
        try:
            # Build prompt
            prompt = self._build_prompt(items, title, intro, footer, trends, style_prompt)
            
            # Call API (OpenAI or OpenRouter)
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a professional newsletter writer specializing in AI and technology content."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature
            )
            
            # Parse response
            content = response.choices[0].message.content
            return self._parse_ai_response(content)
            
        except Exception as e:
            self.logger.error(f"Error generating content with AI: {e}")
            # Return fallback content
            return {
                'title': title or f"AI Newsletter - {datetime.now().strftime('%B %d, %Y')}",
                'intro': intro or "Here are the latest AI developments and insights.",
                'content': self._generate_fallback_content(items),
                'footer': footer or "Thank you for reading! Generated by CreatorPulse."
            }
    
    def _generate_fallback_content(self, items: List[ContentItem]) -> str:
        """Generate fallback content when AI generation fails."""
        content_html = ""
        for item in items:
            content_html += f"""
            <div class="content-item">
                <h3><a href="{item.source_url}" target="_blank">{item.title}</a></h3>
                <div class="meta">
                    Source: {item.source} | Author: {item.author or 'Unknown'} | Score: {item.score}
                </div>
                <div class="summary">
                    {item.summary or item.content[:200] + '...' if len(item.content) > 200 else item.content}
                </div>
            </div>
            """
        return content_html
    
    def _build_prompt(
        self,
        items: List[ContentItem],
        title: Optional[str] = None,
        intro: Optional[str] = None,
        footer: Optional[str] = None,
        trends: Optional[List[Dict[str, Any]]] = None,
        style_prompt: Optional[str] = None
    ) -> str:
        """Build the prompt for OpenAI."""

        # Calculate selection stats
        total_items = len(items)
        unique_sources = set(item.source for item in items)

        # Add style guidance if available
        style_text = ""
        if style_prompt:
            style_text = f"\n\nWRITING STYLE GUIDELINES:\n{style_prompt}\n"

        # Add trending topics context if available
        trends_text = ""
        if trends and len(trends) > 0:
            trends_text = "\n\nTRENDING TOPICS TO HIGHLIGHT:\n"
            for i, trend in enumerate(trends, 1):
                trends_text += f"{i}. {trend['topic']} (strength: {trend['strength_score']:.2f})\n"
                trends_text += f"   Keywords: {', '.join(trend['keywords'][:5])}\n"
                trends_text += f"   {trend.get('explanation', '')}\n"
            trends_text += "\nPlease emphasize content related to these trending topics in the newsletter.\n"

        # Format items for the prompt
        items_text = f"""
Content Selection:
- Total items selected: {total_items} (intelligently ranked and filtered for diversity)
- Sources: {', '.join(sorted(unique_sources))}
{style_text}{trends_text}
Top Items:
"""
        for i, item in enumerate(items, 1):
            items_text += f"""
{i}. {item.title}
   Source: {item.source}
   Author: {item.author or 'Unknown'}
   Score: {item.score}
   Comments: {item.comments_count}
   Views: {item.views_count}
   URL: {item.source_url}
   Summary: {item.summary or item.content or 'No summary available'}
   Tags: {', '.join(item.tags) if item.tags else 'None'}
"""
        
        prompt = f"""
Create a professional newsletter from the following content items:

{items_text}

Please provide the newsletter in the following JSON format:
{{
    "title": "{title or 'Your Daily Tech Digest'}",
    "intro": "A brief introduction paragraph that sets the context and highlights the most important stories",
    "content": "Formatted HTML content for each item with engaging descriptions and proper links",
    "footer": "A brief closing message"
}}

Requirements:
- Write in {self.config.language} with a {self.config.tone} tone
- Make the content engaging and informative
- Include proper HTML formatting for links and emphasis
- Keep descriptions concise but compelling
- Highlight the most important or interesting items
- Use proper HTML tags for formatting
"""
        
        return prompt
    
    def _parse_ai_response(self, content: str) -> Dict[str, str]:
        """Parse the AI response into structured content."""
        try:
            # Try to extract JSON from the response
            start_idx = content.find('{')
            end_idx = content.rfind('}') + 1
            
            if start_idx != -1 and end_idx != 0:
                json_str = content[start_idx:end_idx]
                parsed = json.loads(json_str)
                return parsed
            else:
                # Fallback: treat entire response as content
                return {
                    'title': 'Daily Newsletter',
                    'intro': 'Here are today\'s top stories:',
                    'content': content,
                    'footer': 'Thanks for reading!'
                }
                
        except json.JSONDecodeError:
            # Fallback parsing
            return {
                'title': 'Daily Newsletter',
                'intro': 'Here are today\'s top stories:',
                'content': content,
                'footer': 'Thanks for reading!'
            }
    
    def _format_html(self, generated_content: Dict[str, str], items: List[ContentItem], trends: Optional[List[Dict[str, Any]]] = None) -> str:
        """Format the generated content as HTML using templates."""

        template = self.templates.get(self.config.template, self.templates['default'])

        # Add trending section if trends are available
        trending_html = ""
        if trends and len(trends) > 0:
            trending_html = """
            <div style="background: #f0f9ff; border-left: 4px solid #3b82f6; padding: 20px; margin-bottom: 30px; border-radius: 4px;">
                <h2 style="margin-top: 0; color: #1e40af; font-size: 22px;">🔥 Trending Topics</h2>
                <div style="display: flex; flex-direction: column; gap: 12px;">
            """
            for trend in trends[:3]:  # Show top 3 trends
                trending_html += f"""
                    <div style="background: white; padding: 12px; border-radius: 4px; border: 1px solid #bfdbfe;">
                        <strong style="color: #1e40af;">{trend['topic']}</strong>
                        <span style="color: #64748b; font-size: 13px; margin-left: 8px;">(Strength: {trend['strength_score']:.0%})</span>
                        <p style="margin: 8px 0 0 0; color: #475569; font-size: 14px;">{trend.get('explanation', '')}</p>
                    </div>
                """
            trending_html += """
                </div>
            </div>
            """

        # Format content items
        content_html = ""
        for item in items:
            content_html += f"""
            <div class="content-item">
                <h3><a href="{item.source_url}" target="_blank">{item.title}</a></h3>
                <div class="meta">
                    <span>By {item.author or 'Unknown'}</span>
                    <span>{item.source}</span>
                    <span>Score: {item.score}</span>
                    <span>Comments: {item.comments_count}</span>
                    {f'<span>Views: {item.views_count}</span>' if item.views_count else ''}
                </div>
                <div class="summary">
                    {item.summary or item.content or 'No summary available'}
                </div>
            </div>
            """

        # Replace template variables
        html = template.replace('{{title}}', generated_content.get('title', 'Daily Newsletter'))
        html = html.replace('{{date}}', datetime.now().strftime('%B %d, %Y'))
        html = html.replace('{{intro}}', generated_content.get('intro', 'Here are today\'s top stories:'))
        html = html.replace('{{content}}', trending_html + content_html)
        html = html.replace('{{footer}}', generated_content.get('footer', 'Thanks for reading!'))

        return html
    
    def _generate_empty_newsletter(self) -> str:
        """Generate an empty newsletter when no content is available."""
        template = self.templates.get(self.config.template, self.templates['default'])
        
        html = template.replace('{{title}}', 'Daily Newsletter')
        html = html.replace('{{date}}', datetime.now().strftime('%B %d, %Y'))
        html = html.replace('{{intro}}', 'No new content available today.')
        html = html.replace('{{content}}', '<p>Check back tomorrow for fresh content!</p>')
        html = html.replace('{{footer}}', 'Thanks for reading!')
        
        return html
    
    def _generate_fallback_newsletter(self, items: List[ContentItem]) -> str:
        """Generate a fallback newsletter when AI generation fails."""
        template = self.templates.get(self.config.template, self.templates['default'])

        # Format content items
        content_html = ""
        for item in items:
            content_html += f"""
            <div class="content-item">
                <h3><a href="{item.source_url}" target="_blank">{item.title}</a></h3>
                <div class="meta">
                    By {item.author or 'Unknown'} • {item.source} •
                    Score: {item.score} • Comments: {item.comments_count}
                </div>
                <div class="summary">
                    {item.summary or item.content or 'No summary available'}
                </div>
            </div>
            """
        
        html = template.replace('{{title}}', 'Daily Newsletter')
        html = html.replace('{{date}}', datetime.now().strftime('%B %d, %Y'))
        html = html.replace('{{intro}}', 'Here are today\'s top stories:')
        html = html.replace('{{content}}', content_html)
        html = html.replace('{{footer}}', 'Thanks for reading!')
        
        return html
    
    def preview_newsletter(self, content_items: List[ContentItem], **kwargs) -> Dict[str, Any]:
        """
        Generate a preview of the newsletter without sending.
        
        Args:
            content_items: List of ContentItem objects
            **kwargs: Additional parameters for generate_newsletter
            
        Returns:
            Dictionary with newsletter preview data
        """
        html_content = self.generate_newsletter(content_items, **kwargs)
        
        return {
            'html': html_content,
            'item_count': len(content_items),
            'generated_at': datetime.now().isoformat(),
            'config': {
                'model': self.config.model,
                'temperature': self.config.temperature,
                'template': self.config.template
            }
        }
