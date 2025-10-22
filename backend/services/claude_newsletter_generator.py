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

        # Find hero image (highest scoring item with image)
        hero_image = None
        for item in items:
            if item.get('image_url'):
                hero_image = item.get('image_url')
                break

        # Format items for prompt
        items_text = ""
        for i, item in enumerate(items, 1):
            image_info = f"\n   Image: {item.get('image_url')}" if item.get('image_url') else ""
            items_text += f"""
{i}. {item.get('title', 'Untitled')}
   Source: {item.get('source', 'Unknown')}
   Author: {item.get('author', 'Unknown')}
   URL: {item.get('source_url', '#')}{image_info}
   Summary: {item.get('summary') or item.get('content', 'No content')[:200]}
"""

        prompt = f"""You are an expert newsletter writer creating a high-quality AI briefing. Transform the raw content below into an insightful, narrative-driven newsletter with professional visual design.

CONTENT ({len(items)} items):
{items_text}

HERO IMAGE (use at top of newsletter): {hero_image or 'No hero image available'}

INSTRUCTIONS:

1. VISUAL DESIGN:
   - Start with hero image at top (if available)
   - Include article thumbnails inline where images are provided
   - Use professional color scheme (blues, oranges for accents)
   - Add visual separators between sections

2. IDENTIFY THEMES: Analyze all items and group into 3-5 thematic sections

3. ADD CONTEXT: Explain WHY each theme matters, not just WHAT happened

4. MERGE SIMILAR TOPICS: Synthesize related stories into cohesive narratives

5. CREATE NARRATIVE FLOW: Use transitions, tell a story

6. TONE: {tone}, journalistic, insightful

Provide response as JSON:
{{
    "title": "{title or 'AI Newsletter - ' + datetime.now().strftime('%B %d, %Y')}",
    "intro": "Engaging 3-4 sentence intro that sets context and previews themes",
    "content": "HTML content with professional design. Include hero image at top, thematic sections with <h2> titles, inline article images, contextual analysis paragraphs, and <a href> links. Use modern styling with colors, spacing, and visual hierarchy.",
    "footer": "Brief forward-looking closing (1-2 sentences)"
}}

STYLING GUIDELINES:
- Hero image: <img src="URL" style="width: 100%; max-height: 400px; object-fit: cover; border-radius: 8px; margin-bottom: 24px;" />
- Section headers: <h2 style="color: #1e40af; font-size: 24px; font-weight: 700; margin-top: 32px; margin-bottom: 16px; border-bottom: 2px solid #3b82f6; padding-bottom: 8px;">Title</h2>
- Article thumbnails: <img src="URL" style="width: 120px; height: 80px; object-fit: cover; border-radius: 4px; float: left; margin-right: 16px;" />
- Callout boxes: <div style="background: #eff6ff; border-left: 4px solid #3b82f6; padding: 16px; margin: 16px 0; border-radius: 4px;"><strong>Key Insight:</strong> Text here</div>
- Body text: <p style="color: #374151; line-height: 1.6; margin-bottom: 16px;">Content</p>

EXAMPLE SECTION WITH IMAGE:
```html
<h2 style="color: #1e40af; font-size: 24px; font-weight: 700; margin-top: 32px; margin-bottom: 16px; border-bottom: 2px solid #3b82f6; padding-bottom: 8px;">1. The AI Infrastructure Race Intensifies</h2>
<img src="IMAGE_URL" style="width: 100%; max-height: 300px; object-fit: cover; border-radius: 8px; margin-bottom: 16px;" />
<p style="color: #374151; line-height: 1.6; margin-bottom: 16px;">This week underscored the massive capital requirements shaping the AI landscape, with three major infrastructure announcements...</p>
<div style="background: #eff6ff; border-left: 4px solid #3b82f6; padding: 16px; margin: 16px 0; border-radius: 4px;">
<strong style="color: #1e40af;">What this means:</strong> Companies securing infrastructure now gain long-term competitive advantage...
</div>
```

Write sophisticated but accessible content with modern visual design. Prioritize insight and visual appeal."""

        return prompt

    def _parse_response(self, response_text: str) -> Dict[str, str]:
        """Parse Claude's JSON response."""
        try:
            # Try to extract JSON
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1

            if start_idx != -1 and end_idx != 0:
                json_str = response_text[start_idx:end_idx]
                parsed = json.loads(json_str)

                # Validate required fields
                required_fields = ['title', 'intro', 'content', 'footer']
                for field in required_fields:
                    if field not in parsed:
                        parsed[field] = self._get_default_field(field)

                return parsed
            else:
                # Fallback
                logger.warning("No JSON found in Claude response, using fallback")
                return self._get_fallback_response(response_text)

        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {e}")
            return self._get_fallback_response(response_text)

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
        """Fallback response when JSON parsing fails."""
        return {
            'title': f"AI Newsletter - {datetime.now().strftime('%B %d, %Y')}",
            'intro': "Here are today's top stories:",
            'content': f"<div>{content}</div>",
            'footer': "Thanks for reading!"
        }
