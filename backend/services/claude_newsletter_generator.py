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

        # Format items for prompt
        items_text = ""
        for i, item in enumerate(items, 1):
            items_text += f"""
{i}. {item.get('title', 'Untitled')}
   Source: {item.get('source', 'Unknown')}
   Author: {item.get('author', 'Unknown')}
   URL: {item.get('source_url', '#')}
   Summary: {item.get('summary') or item.get('content', 'No content')[:200]}
"""

        prompt = f"""You are an expert newsletter writer creating a high-quality AI briefing. Transform the raw content below into an insightful, narrative-driven newsletter.

CONTENT ({len(items)} items):
{items_text}

INSTRUCTIONS:

1. IDENTIFY THEMES: Analyze all items and group into 3-5 thematic sections
2. ADD CONTEXT: Explain WHY each theme matters, not just WHAT happened
3. MERGE SIMILAR TOPICS: Synthesize related stories into cohesive narratives
4. CREATE NARRATIVE FLOW: Use transitions, tell a story
5. TONE: {tone}, journalistic, insightful

Provide response as JSON:
{{
    "title": "{title or 'AI Newsletter - ' + datetime.now().strftime('%B %d, %Y')}",
    "intro": "Engaging 3-4 sentence intro that sets context and previews themes",
    "content": "HTML content with 3-5 thematic sections. Each section should have <h2> title, contextual analysis paragraphs, and inline citations with <a href> links to sources. Use <strong>, <em>, and styled callout boxes for emphasis.",
    "footer": "Brief forward-looking closing (1-2 sentences)"
}}

EXAMPLE SECTION:
```html
<h2>1. The AI Infrastructure Race Intensifies</h2>
<p>This week underscored the massive capital requirements shaping the AI landscape, with three major infrastructure announcements...</p>
<p>Key developments include <a href="URL">Company X's $37B financing deal</a> and <a href="URL">Company Y's new partnership</a>...</p>
<p><strong>What this means:</strong> Companies securing infrastructure now gain long-term competitive advantage...</p>
```

Write sophisticated but accessible content. Prioritize insight over comprehensiveness."""

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
