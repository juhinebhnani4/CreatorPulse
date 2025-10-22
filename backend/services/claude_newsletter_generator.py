"""
Claude-powered newsletter generation service.
Uses Anthropic's Claude API for high-quality newsletter generation.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

try:
    from anthropic import Anthropic
except ImportError:
    Anthropic = None

from backend.settings import Settings


logger = logging.getLogger(__name__)


class ClaudeNewsletterGenerator:
    """Newsletter generator using Claude (Anthropic API)."""

    def __init__(self, settings: Settings):
        """
        Initialize Claude newsletter generator.

        Args:
            settings: Application settings with Anthropic API key
        """
        if not Anthropic:
            raise ImportError("anthropic package required. Install with: pip install anthropic")

        if not settings.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY must be set in environment variables")

        self.client = Anthropic(api_key=settings.anthropic_api_key)
        self.model = settings.anthropic_model
        self.max_tokens = settings.anthropic_max_tokens
        self.settings = settings

        logger.info(f"Initialized Claude newsletter generator (model: {self.model})")

    def generate_newsletter_content(
        self,
        items: List[Dict[str, Any]],
        title: Optional[str] = None,
        tone: str = "professional"
    ) -> Dict[str, str]:
        """
        Generate newsletter content using Claude.

        Args:
            items: List of content items (as dicts)
            title: Optional newsletter title
            tone: Writing tone (professional, casual, technical, friendly)

        Returns:
            Dict with generated content (title, intro, content, footer)
        """
        # Build prompt
        prompt = self._build_prompt(items, title, tone)

        try:
            # Call Claude API
            logger.info(f"Calling Claude API with {len(items)} items")

            message = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7
            )

            # Extract response content
            response_text = message.content[0].text

            logger.info(f"Received response from Claude ({len(response_text)} chars)")

            # Parse JSON response
            result = self._parse_response(response_text)

            logger.info("Successfully parsed Claude response")
            return result

        except Exception as e:
            logger.error(f"Error calling Claude API: {e}")
            raise

    def _build_prompt(
        self,
        items: List[Dict[str, Any]],
        title: Optional[str],
        tone: str
    ) -> str:
        """Build the prompt for Claude."""

        # Collect all available images
        hero_image = None
        images_with_context = []

        for i, item in enumerate(items, 1):
            if item.get('image_url'):
                if not hero_image:
                    hero_image = item.get('image_url')
                images_with_context.append({
                    'url': item.get('image_url'),
                    'title': item.get('title', 'Untitled'),
                    'source': item.get('source', 'Unknown'),
                    'index': i
                })

        # Build images section
        images_section = "AVAILABLE IMAGES TO USE:\n"
        if hero_image:
            images_section += f"\nHERO IMAGE (use at very top): {hero_image}\n"
        if images_with_context:
            images_section += "\nARTICLE IMAGES (use inline with relevant sections):\n"
            for img in images_with_context:
                images_section += f"  - Image {img['index']}: {img['url']}\n    (from: {img['title'][:60]}... [{img['source']}])\n"
        else:
            images_section += "No images available - create text-only newsletter\n"

        # Format items for prompt
        items_text = ""
        for i, item in enumerate(items, 1):
            has_image = "📷 HAS IMAGE" if item.get('image_url') else ""
            items_text += f"""
{i}. {item.get('title', 'Untitled')} {has_image}
   Source: {item.get('source', 'Unknown')} | Author: {item.get('author', 'Unknown')}
   URL: {item.get('source_url', '#')}
   Summary: {item.get('summary') or item.get('content', 'No content')[:200]}
"""

        newsletter_title = title or f"AI Newsletter - {datetime.now().strftime('%B %d, %Y')}"

        prompt = f"""You are an expert newsletter writer creating a high-quality AI briefing with professional visual design.

{images_section}

CONTENT TO ANALYZE ({len(items)} items):
{items_text}

YOUR TASK:
Create a complete HTML newsletter that is visually appealing and insightful. Analyze all content items, identify 3-5 major themes, and synthesize them into narrative sections.

IMPORTANT - HTML OUTPUT FORMAT:
Generate ONLY the complete HTML newsletter. No JSON, no code blocks, just pure HTML starting with the structure below.

Start your response with exactly this structure:
<div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 680px; margin: 0 auto; color: #1f2937;">

<!-- Hero Image (if available) -->
{f'<img src="{hero_image}" alt="Newsletter header" style="width: 100%; max-height: 400px; object-fit: cover; border-radius: 8px; margin-bottom: 24px;" />' if hero_image else ''}

<!-- Newsletter Title -->
<h1 style="color: #111827; font-size: 32px; font-weight: 800; margin-bottom: 8px; text-align: center;">{newsletter_title}</h1>

<!-- Date -->
<p style="text-align: center; color: #6b7280; font-size: 14px; margin-bottom: 24px;">{datetime.now().strftime('%A, %B %d, %Y')}</p>

<!-- Introduction Paragraph -->
<div style="background: #f9fafb; border-left: 4px solid #3b82f6; padding: 20px; margin-bottom: 32px; border-radius: 4px;">
<p style="color: #374151; line-height: 1.8; margin: 0; font-size: 16px;">
[Write an engaging 3-4 sentence introduction that sets context and previews the main themes you'll cover]
</p>
</div>

<!-- Section 1 -->
<h2 style="color: #1e40af; font-size: 24px; font-weight: 700; margin-top: 32px; margin-bottom: 16px; border-bottom: 2px solid #3b82f6; padding-bottom: 8px;">1. [Theme Title]</h2>

{f'<img src="[USE_RELEVANT_IMAGE_URL_HERE]" alt="Section image" style="width: 100%; max-height: 300px; object-fit: cover; border-radius: 8px; margin-bottom: 16px;" />' if images_with_context else ''}

<p style="color: #374151; line-height: 1.6; margin-bottom: 16px;">
[Your analysis paragraph explaining WHY this theme matters, synthesizing multiple sources...]
</p>

<div style="background: #eff6ff; border-left: 4px solid #3b82f6; padding: 16px; margin: 16px 0; border-radius: 4px;">
<strong style="color: #1e40af;">Key Insight:</strong> [Important takeaway or implication]
</div>

<p style="color: #374151; line-height: 1.6; margin-bottom: 16px;">
[Continue narrative, include relevant <a href="[URL]" style="color: #3b82f6; text-decoration: none;">source links</a>...]
</p>

<!-- Repeat similar structure for Sections 2-5 -->

<!-- Footer -->
<div style="margin-top: 48px; padding-top: 24px; border-top: 1px solid #e5e7eb;">
<p style="color: #6b7280; font-size: 14px; line-height: 1.6; margin: 0;">
[1-2 sentence forward-looking closing about what to watch for next]
</p>
</div>

</div>

CRITICAL INSTRUCTIONS:
1. USE ACTUAL IMAGE URLS: Replace [USE_RELEVANT_IMAGE_URL_HERE] with the actual URLs from AVAILABLE IMAGES section above
2. INCLUDE HERO IMAGE: If hero image exists, it must be in the first <img> tag right after the opening <div>
3. ARTICLE IMAGES: Place inline within relevant sections using the full URLs provided
4. NO CODE BLOCKS: Do not wrap your response in ```html```. Output pure HTML only.
5. TONE: {tone}, journalistic, insightful
6. SECTIONS: Create 3-5 thematic sections based on the content
7. LINKS: Include source links as <a> tags to original articles
8. CALLOUT BOXES: Use the blue callout box style for key insights

OUTPUT FORMAT: Start your response with <div style="font-family... and end with </div>. Nothing else."""

        return prompt

    def _parse_response(self, response_text: str) -> Dict[str, str]:
        """Parse Claude's HTML response and extract components."""
        try:
            # Claude returns pure HTML - extract it
            html_content = response_text.strip()

            # Remove any code block markers if Claude included them
            if html_content.startswith('```html'):
                html_content = html_content[7:]
            if html_content.startswith('```'):
                html_content = html_content[3:]
            if html_content.endswith('```'):
                html_content = html_content[:-3]
            html_content = html_content.strip()

            # Try to extract title from <h1> tag
            title = self._extract_title(html_content)

            # Try to extract intro from the intro box
            intro = self._extract_intro(html_content)

            # Try to extract footer
            footer = self._extract_footer(html_content)

            logger.info(f"Successfully parsed HTML response (title: {title[:50]}...)")

            return {
                'title': title,
                'intro': intro,
                'content': html_content,  # The full HTML
                'footer': footer
            }

        except Exception as e:
            logger.error(f"Error parsing HTML response: {e}")
            return self._get_fallback_response(response_text)

    def _extract_title(self, html: str) -> str:
        """Extract title from <h1> tag."""
        import re
        match = re.search(r'<h1[^>]*>(.*?)</h1>', html, re.DOTALL | re.IGNORECASE)
        if match:
            title = match.group(1).strip()
            # Remove HTML tags from title
            title = re.sub(r'<[^>]+>', '', title)
            return title
        return f"AI Newsletter - {datetime.now().strftime('%B %d, %Y')}"

    def _extract_intro(self, html: str) -> str:
        """Extract intro text from the intro box."""
        import re
        # Look for the intro box (first paragraph in the blue-bordered div)
        match = re.search(r'<div[^>]*border-left: 4px solid #3b82f6[^>]*>.*?<p[^>]*>(.*?)</p>', html, re.DOTALL | re.IGNORECASE)
        if match:
            intro = match.group(1).strip()
            # Remove HTML tags
            intro = re.sub(r'<[^>]+>', '', intro)
            return intro
        return "Here are today's top AI developments."

    def _extract_footer(self, html: str) -> str:
        """Extract footer text."""
        import re
        # Look for footer div
        match = re.search(r'<div[^>]*margin-top: 48px[^>]*>.*?<p[^>]*>(.*?)</p>', html, re.DOTALL | re.IGNORECASE)
        if match:
            footer = match.group(1).strip()
            # Remove HTML tags
            footer = re.sub(r'<[^>]+>', '', footer)
            return footer
        return "Thanks for reading!"

    def _get_default_field(self, field: str) -> str:
        """Get default value for missing field."""
        defaults = {
            'title': f"AI Newsletter - {datetime.now().strftime('%B %d, %Y')}",
            'intro': "Here are today's top AI developments.",
            'content': "<p>Newsletter content</p>",
            'footer': "Thanks for reading!"
        }
        return defaults.get(field, "")

    def _get_fallback_response(self, content: str) -> Dict[str, str]:
        """Fallback response when parsing fails."""
        return {
            'title': f"AI Newsletter - {datetime.now().strftime('%B %d, %Y')}",
            'intro': "Here are today's top stories:",
            'content': f"<div>{content}</div>",
            'footer': "Thanks for reading!"
        }
