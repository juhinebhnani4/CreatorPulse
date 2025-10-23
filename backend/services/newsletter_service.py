"""
Newsletter service - Business logic for newsletter generation and management.
Updated: 2025-01-20 - Fixed type handling for source filtering
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from uuid import UUID
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.ai_newsletter.database.supabase_client import SupabaseManager
from src.ai_newsletter.generators import NewsletterGenerator
from src.ai_newsletter.config.settings import get_settings
from backend.services.trend_service import TrendDetectionService
from backend.services.style_service import StyleAnalysisService
from backend.services.feedback_service import FeedbackService
from backend.services.claude_newsletter_generator import ClaudeNewsletterGenerator
from backend.config.constants import NewsletterConstants
from backend.settings import settings


class NewsletterService:
    """Service for newsletter generation and management."""

    def __init__(self):
        """Initialize newsletter service."""
        self.supabase = SupabaseManager()
        self.settings = get_settings()

        # Validate API keys at initialization
        self._validate_api_keys()

        self.trend_service = TrendDetectionService()
        self.style_service = StyleAnalysisService()
        self.feedback_service = FeedbackService(self.supabase)

    def _validate_api_keys(self):
        """
        Validate that required API keys are configured.

        Raises:
            ValueError: If no valid API key is found
        """
        has_anthropic = bool(settings.anthropic_api_key)
        has_openai = bool(self.settings.newsletter.openai_api_key)
        has_openrouter = bool(self.settings.newsletter.openrouter_api_key)

        if not has_anthropic and not has_openai and not has_openrouter:
            raise ValueError(
                "No AI API key configured. Set ANTHROPIC_API_KEY in your .env file"
            )

        # Log which API is available (without exposing keys)
        # SECURITY: Never log API keys or credentials, even partially
        if has_anthropic:
            print("[NewsletterService] [OK] Anthropic Claude API configured")
        if has_openai:
            print("[NewsletterService] [WARNING] OpenAI API configured (deprecated, using Claude)")
        if has_openrouter:
            print("[NewsletterService] [INFO] OpenRouter API configured (backup only)")

        # Use Claude by default
        if not has_anthropic:
            print("[NewsletterService] [WARNING] ANTHROPIC_API_KEY not set. Please add it to .env file")

    async def generate_newsletter(
        self,
        user_id: str,
        workspace_id: str,
        title: str,
        max_items: int = 15,
        days_back: int = 7,
        sources: Optional[List[str]] = None,
        tone: str = "professional",
        language: str = "en",
        temperature: float = 0.7,
        model: Optional[str] = None,
        use_openrouter: bool = False
    ) -> Dict[str, Any]:
        """
        Generate newsletter from workspace content.

        Args:
            user_id: User ID (for auth check)
            workspace_id: Workspace ID
            title: Newsletter title
            max_items: Maximum content items to include
            days_back: Number of days to look back for content
            sources: Optional source filter
            tone: Newsletter tone
            language: Newsletter language
            temperature: AI creativity level
            model: AI model to use (overrides config)
            use_openrouter: Use OpenRouter instead of OpenAI

        Returns:
            Dict with generated newsletter data
        """
        # Verify user has access to workspace
        workspace = self.supabase.get_workspace(workspace_id)
        if not workspace:
            raise ValueError("Workspace not found")

        # Fetch active trends for this workspace
        trends = await self.trend_service.get_active_trends(
            workspace_id=UUID(workspace_id),
            limit=NewsletterConstants.MAX_TRENDS_TO_FETCH
        )

        # Fetch style profile for this workspace
        style_profile = await self.style_service.get_style_profile(
            workspace_id=UUID(workspace_id)
        )

        # Load content items from database
        content_items = self.supabase.load_content_items(
            workspace_id=workspace_id,
            days=days_back,
            source=sources[0] if sources and len(sources) == 1 else None,
            limit=max_items * NewsletterConstants.CONTENT_FETCH_MULTIPLIER  # Fetch more for filtering
        )

        if not content_items:
            raise ValueError(f"No content found in workspace for the last {days_back} days")

        # Filter by sources if specified
        if sources:
            print(f"[DEBUG] Filtering by sources: {sources}")
            print(f"[DEBUG] First item type before filter: {type(content_items[0]) if content_items else 'empty'}")
            print(f"[DEBUG] First item value: {content_items[0] if content_items else 'empty'}")

            filtered_items = []
            for item in content_items:
                # Check if it's a ContentItem object or dict
                if hasattr(item, 'source'):
                    # It's a ContentItem object
                    if item.source in sources:
                        filtered_items.append(item)
                elif isinstance(item, dict):
                    # It's a dict
                    print(f"[WARNING] Found dict instead of ContentItem: {item.get('source')}")
                    if item.get('source') in sources:
                        filtered_items.append(item)
                else:
                    print(f"[ERROR] Unknown item type: {type(item)}")

            content_items = filtered_items
            print(f"[DEBUG] Filtered to {len(content_items)} items")

        # Apply feedback-based content scoring adjustments
        # NOTE: This converts ContentItem objects to dicts
        content_items_dicts = self.feedback_service.adjust_content_scoring(
            workspace_id=workspace_id,
            content_items=content_items,
            apply_source_quality=True,
            apply_preferences=True
        )

        # Boost content related to active trends
        if trends:
            trend_keywords = set()
            for trend in trends:
                trend_keywords.update([kw.lower() for kw in trend.keywords])

            for item in content_items_dicts:
                # Check if item is related to any trend
                item_text = (item.get('title', '') + ' ' + item.get('summary', '')).lower()
                if any(keyword in item_text for keyword in trend_keywords):
                    # Boost score using configured multiplier
                    item['trend_boosted'] = True
                    item['original_score'] = item.get('score', 0)
                    item['score'] = int(item.get('score', 0) * NewsletterConstants.TREND_SCORE_BOOST_MULTIPLIER)

        # Re-sort by score after trend boosting
        content_items_dicts.sort(key=lambda x: x.get('score', 0), reverse=True)

        # Limit to max_items
        content_items_dicts = content_items_dicts[:max_items]

        if not content_items_dicts:
            raise ValueError("No content items match the specified filters")

        # Convert back to ContentItem objects for generator
        from src.ai_newsletter.models.content import ContentItem
        content_items_for_generator = []
        for item_dict in content_items_dicts:
            try:
                # ContentItem.from_dict() handles datetime parsing
                content_items_for_generator.append(ContentItem.from_dict(item_dict))
            except Exception as e:
                # If conversion fails, skip this item with a warning
                print(f"Warning: Failed to convert item to ContentItem: {e}")
                continue

        if not content_items_for_generator:
            raise ValueError("No valid content items after conversion")

        # Check if we should use OpenRouter or direct Anthropic API
        if settings.use_openrouter:
            # Use OpenRouter (via original NewsletterGenerator)
            print(f"[NewsletterService] [INFO] Using Claude via OpenRouter")
            return await self._generate_with_openrouter(
                workspace_id, title, tone, temperature, language,
                content_items_for_generator, content_items_dicts,
                sources, days_back, trends, style_profile
            )
        else:
            # Use direct Anthropic API (Claude)
            print(f"[NewsletterService] [INFO] Using Claude direct API")
            # Initialize Claude newsletter generator
            claude_generator = ClaudeNewsletterGenerator(settings)

        # Convert ContentItem objects to dicts for Claude generator
        items_for_claude = []
        for item in content_items_for_generator:
            items_for_claude.append({
                'title': item.title,
                'source': item.source,
                'author': item.author or 'Unknown',
                'source_url': item.source_url,
                'summary': item.summary or item.content[:200] if item.content else 'No content',
                'content': item.content
            })

        # Pass image URLs to Claude generator
        # Extract image URLs from content items
        for idx, item in enumerate(items_for_claude):
            # Match with original content_items_dicts to get image_url
            if idx < len(content_items_dicts):
                item['image_url'] = content_items_dicts[idx].get('image_url')

        # Generate newsletter content using Claude
        print(f"[NewsletterService] [INFO] Calling Claude API with {len(items_for_claude)} items")
        claude_result = claude_generator.generate_newsletter_content(
            items=items_for_claude,
            title=title,
            tone=tone,
            style_profile=style_profile  # Pass the fetched style profile
        )

        # Claude now returns COMPLETE HTML with images and styling
        # Use it directly without wrapping in another template
        html_content = claude_result.get('content', '')

        # Debug: Check HTML content
        print(f"[DEBUG] Newsletter generation completed")
        print(f"[DEBUG] HTML content length: {len(html_content) if html_content else 0}")
        print(f"[DEBUG] HTML content type: {type(html_content)}")
        print(f"[DEBUG] HTML preview (first 200 chars): {html_content[:200] if html_content else 'None'}")

        # Extract content item IDs from dict items (before conversion)
        content_item_ids = []
        print(f"[DEBUG] Extracting content item IDs from {len(content_items_dicts)} items")
        for idx, item_dict in enumerate(content_items_dicts):
            # Try to get ID from metadata or top level
            item_id = item_dict.get('id') or item_dict.get('metadata', {}).get('id')
            if idx == 0:
                print(f"[DEBUG] First item keys: {list(item_dict.keys())}")
                print(f"[DEBUG] First item ID: {item_id}")
            if item_id:
                content_item_ids.append(item_id)

        print(f"[DEBUG] Extracted {len(content_item_ids)} content item IDs: {content_item_ids[:3] if content_item_ids else 'NONE'}")

        # Extract subject line from h1 tag in HTML (for email subject)
        import re
        subject_line_match = re.search(r'<h1[^>]*>(.*?)</h1>', html_content, re.DOTALL | re.IGNORECASE)
        if subject_line_match:
            subject_line = subject_line_match.group(1).strip()
            # Remove any HTML tags within the h1
            subject_line = re.sub(r'<[^>]+>', '', subject_line)
        else:
            subject_line = title  # Fallback to title if no h1 found

        # Save to database
        newsletter = self.supabase.save_newsletter(
            workspace_id=workspace_id,
            title=title,
            subject_line=subject_line,  # Add subject line for email
            html_content=html_content,
            plain_text_content=None,  # TODO: Generate plain text version
            content_item_ids=content_item_ids,
            model_used=settings.anthropic_model,  # Use Claude model
            temperature=temperature,
            tone=tone,
            language=language,
            metadata={
                'sources': sources or [],
                'days_back': days_back,
                'use_claude': True,  # Track that Claude was used
                'trends_used': [trend.topic for trend in trends] if trends else [],
                'trend_boosted_items': len([item for item in content_items_dicts if item.get('trend_boosted', False)]),
                'style_profile_applied': style_profile is not None,
                'style_tone': style_profile.tone if style_profile else None,
                'style_formality': style_profile.formality_level if style_profile else None,
                'style_trained_samples': style_profile.trained_on_count if style_profile else 0,
                'style_vocabulary_level': style_profile.vocabulary_level if style_profile else None,
                'feedback_adjusted_items': len([item for item in content_items_dicts if item.get('adjustments', [])])
            }
        )

        return {
            'newsletter': newsletter,
            'items': content_items_dicts,  # Include items array for frontend Edit mode and feedback buttons
            'content_items_count': len(content_items_dicts),
            'sources_used': list(set(item.get('source', 'unknown') for item in content_items_dicts)),
            'trends_applied': len(trends) if trends else 0,
            'trend_boosted_items': len([item for item in content_items_dicts if item.get('trend_boosted', False)]),
            'style_profile_applied': style_profile is not None,
            'feedback_adjusted_items': len([item for item in content_items_dicts if item.get('adjustments', [])])
        }

    async def _generate_with_openrouter(
        self,
        workspace_id: str,
        title: str,
        tone: str,
        temperature: float,
        language: str,
        content_items_for_generator: List[Any],
        content_items_dicts: List[Dict],
        sources: List[str],
        days_back: int,
        trends: List[Any],
        style_profile: Any
    ) -> Dict[str, Any]:
        """
        Generate newsletter using OpenRouter (Claude via OpenRouter API).

        This method uses the original NewsletterGenerator which supports OpenRouter.
        """
        print(f"[NewsletterService] [INFO] Initializing NewsletterGenerator with OpenRouter")

        # Use the original generator which has OpenRouter support
        generator = NewsletterGenerator(self.settings)

        # Generate newsletter using OpenRouter
        result = generator.generate_newsletter(
            title=title,
            content_items=content_items_for_generator,
            tone=tone,
            temperature=temperature,
            language=language,
            max_tokens=self.settings.newsletter.max_tokens
        )

        html_content = result['html']
        plain_text_content = result.get('text', '')

        # Extract content item IDs
        content_item_ids = []
        for item_dict in content_items_dicts:
            item_id = item_dict.get('id') or item_dict.get('metadata', {}).get('id')
            if item_id:
                content_item_ids.append(item_id)

        # Extract subject line from h1 tag in HTML (for email subject)
        import re
        subject_line_match = re.search(r'<h1[^>]*>(.*?)</h1>', html_content, re.DOTALL | re.IGNORECASE)
        if subject_line_match:
            subject_line = subject_line_match.group(1).strip()
            # Remove any HTML tags within the h1
            subject_line = re.sub(r'<[^>]+>', '', subject_line)
        else:
            subject_line = title  # Fallback to title if no h1 found

        # Save to database
        newsletter = self.supabase.save_newsletter(
            workspace_id=workspace_id,
            title=title,
            subject_line=subject_line,  # Add subject line for email
            html_content=html_content,
            plain_text_content=plain_text_content,
            content_item_ids=content_item_ids,
            model_used=self.settings.newsletter.openrouter_model or "anthropic/claude-3.5-sonnet",
            temperature=temperature,
            tone=tone,
            language=language,
            metadata={
                'sources': sources or [],
                'days_back': days_back,
                'use_openrouter': True,
                'trends_used': [trend.topic for trend in trends] if trends else [],
                'trend_boosted_items': len([item for item in content_items_dicts if item.get('trend_boosted', False)]),
                'style_profile_applied': style_profile is not None,
                'style_tone': style_profile.tone if style_profile else None,
                'style_formality': style_profile.formality_level if style_profile else None,
                'style_trained_samples': style_profile.trained_on_count if style_profile else 0,
                'style_vocabulary_level': style_profile.vocabulary_level if style_profile else None,
                'feedback_adjusted_items': len([item for item in content_items_dicts if item.get('adjustments', [])])
            }
        )

        return {
            'newsletter': newsletter,
            'items': content_items_dicts,  # Include items array for frontend Edit mode and feedback buttons
            'content_items_count': len(content_items_dicts),
            'sources_used': list(set(item.get('source', 'unknown') for item in content_items_dicts)),
            'trends_applied': len(trends) if trends else 0,
            'trend_boosted_items': len([item for item in content_items_dicts if item.get('trend_boosted', False)]),
            'style_profile_applied': style_profile is not None,
            'feedback_adjusted_items': len([item for item in content_items_dicts if item.get('adjustments', [])])
        }

    async def update_newsletter_html(
        self,
        newsletter_id: str,
        updated_html: str,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Update newsletter HTML content after user inline edits.

        Args:
            newsletter_id: Newsletter ID
            updated_html: Updated HTML content
            user_id: User ID (for authorization)

        Returns:
            Updated newsletter object
        """
        from datetime import datetime

        # Verify user has access to this newsletter's workspace
        newsletter = self.supabase.get_newsletter(newsletter_id)
        if not newsletter:
            raise ValueError("Newsletter not found")

        # Update HTML content
        updated_newsletter = self.supabase.update_newsletter(
            newsletter_id=newsletter_id,
            updates={
                'content_html': updated_html,
                'metadata': {
                    **newsletter.get('metadata', {}),
                    'html_edited_at': datetime.now().isoformat(),
                    'edited_by': user_id
                }
            }
        )

        return updated_newsletter

    def _populate_newsletter_items(self, newsletter: Dict[str, Any]) -> Dict[str, Any]:
        """
        Populate newsletter items field from content_item_ids.

        Args:
            newsletter: Newsletter dict with content_item_ids

        Returns:
            Newsletter dict with items field populated
        """
        # Get content item IDs
        content_item_ids = newsletter.get('content_item_ids', [])

        print(f"[_populate_newsletter_items] Newsletter ID: {newsletter.get('id')}")
        print(f"[_populate_newsletter_items] Content item IDs count: {len(content_item_ids)}")

        if not content_item_ids:
            newsletter['items'] = []
            print(f"[_populate_newsletter_items] No content items found, returning empty items")
            return newsletter

        # Fetch content items from database in bulk (single query instead of N queries)
        items = self.supabase.get_content_items_bulk(content_item_ids)

        # Log any missing items (items not found in database)
        if len(items) < len(content_item_ids):
            found_ids = {item['id'] for item in items}
            missing_ids = set(content_item_ids) - found_ids
            for missing_id in missing_ids:
                print(f"[_populate_newsletter_items] WARNING: Could not find content item {missing_id}")

        # Add items field to newsletter
        newsletter['items'] = items
        print(f"[_populate_newsletter_items] Populated {len(items)} items for newsletter")

        # Debug: Show first item structure if available
        if items:
            first_item = items[0]
            print(f"[_populate_newsletter_items] First item sample:")
            print(f"  - id: {first_item.get('id', 'MISSING')}")
            print(f"  - title: {first_item.get('title', 'MISSING')[:50] if first_item.get('title') else 'MISSING'}")
            print(f"  - source: {first_item.get('source', 'MISSING')}")
            print(f"  - Keys: {list(first_item.keys())[:10]}")

        return newsletter

    async def list_newsletters(
        self,
        user_id: str,
        workspace_id: str,
        status: Optional[str] = None,
        limit: int = 50
    ) -> Dict[str, Any]:
        """
        List newsletters for a workspace.

        Args:
            user_id: User ID (for auth check)
            workspace_id: Workspace ID
            status: Optional status filter
            limit: Maximum newsletters to return

        Returns:
            Dict with newsletters list
        """
        # Verify user has access
        workspace = self.supabase.get_workspace(workspace_id)
        if not workspace:
            raise ValueError("Workspace not found")

        # Load newsletters
        newsletters = self.supabase.load_newsletters(
            workspace_id=workspace_id,
            status=status,
            limit=limit
        )

        # Populate items field for each newsletter
        newsletters_with_items = [self._populate_newsletter_items(nl) for nl in newsletters]

        return {
            'workspace_id': workspace_id,
            'newsletters': newsletters_with_items,
            'count': len(newsletters_with_items),
            'filters': {
                'status': status,
                'limit': limit
            }
        }

    async def get_newsletter(
        self,
        user_id: str,
        newsletter_id: str
    ) -> Dict[str, Any]:
        """
        Get newsletter details.

        Args:
            user_id: User ID (for auth check)
            newsletter_id: Newsletter ID

        Returns:
            Newsletter data
        """
        newsletter = self.supabase.get_newsletter(newsletter_id)

        if not newsletter:
            raise ValueError("Newsletter not found")

        # Verify user has access to workspace
        workspace = self.supabase.get_workspace(newsletter['workspace_id'])
        if not workspace:
            raise ValueError("Access denied")

        # Populate items field from content_item_ids
        newsletter = self._populate_newsletter_items(newsletter)

        return newsletter

    async def delete_newsletter(
        self,
        user_id: str,
        newsletter_id: str
    ) -> bool:
        """
        Delete newsletter.

        Args:
            user_id: User ID (for auth check)
            newsletter_id: Newsletter ID

        Returns:
            True if deleted
        """
        # Get newsletter to check access
        newsletter = await self.get_newsletter(user_id, newsletter_id)

        # Delete
        return self.supabase.delete_newsletter(newsletter_id)

    async def regenerate_newsletter(
        self,
        user_id: str,
        newsletter_id: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Regenerate newsletter with new settings.

        Args:
            user_id: User ID
            newsletter_id: Original newsletter ID
            **kwargs: Generation parameters to override

        Returns:
            New newsletter data
        """
        # Get original newsletter
        original = await self.get_newsletter(user_id, newsletter_id)

        # Extract original settings
        workspace_id = original['workspace_id']
        title = kwargs.get('title', original['title'])
        tone = kwargs.get('tone', original.get('tone', 'professional'))
        language = kwargs.get('language', original.get('language', 'en'))
        temperature = kwargs.get('temperature', original.get('temperature', 0.7))
        model = kwargs.get('model', original.get('model_used'))

        # Get metadata for sources and days_back
        metadata = original.get('metadata', {})
        max_items = kwargs.get('max_items', original.get('content_items_count', 15))
        days_back = kwargs.get('days_back', metadata.get('days_back', 7))
        sources = kwargs.get('sources', metadata.get('sources'))
        use_openrouter = kwargs.get('use_openrouter', metadata.get('use_openrouter', False))

        # Generate new newsletter
        result = await self.generate_newsletter(
            user_id=user_id,
            workspace_id=workspace_id,
            title=f"{title} (Regenerated)",
            max_items=max_items,
            days_back=days_back,
            sources=sources,
            tone=tone,
            language=language,
            temperature=temperature,
            model=model,
            use_openrouter=use_openrouter
        )

        return result

    async def get_newsletter_stats(
        self,
        user_id: str,
        workspace_id: str
    ) -> Dict[str, Any]:
        """
        Get newsletter statistics for workspace.

        Args:
            user_id: User ID (for auth check)
            workspace_id: Workspace ID

        Returns:
            Dict with statistics
        """
        # Verify user has access
        workspace = self.supabase.get_workspace(workspace_id)
        if not workspace:
            raise ValueError("Workspace not found")

        return self.supabase.get_newsletter_stats(workspace_id)

    async def update_newsletter_status(
        self,
        user_id: str,
        newsletter_id: str,
        status: Optional[str] = None,
        sent_at: Optional[datetime] = None,
        title: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update newsletter details.

        Args:
            user_id: User ID
            newsletter_id: Newsletter ID
            status: New status (draft, sent, scheduled)
            sent_at: Optional sent timestamp
            title: Optional newsletter title

        Returns:
            Updated newsletter
        """
        # Verify access
        newsletter = await self.get_newsletter(user_id, newsletter_id)

        # Update
        # Use 'is not None' to allow empty strings and distinguish None from empty
        updates = {}
        if status is not None:
            updates['status'] = status
        if sent_at is not None:
            updates['sent_at'] = sent_at.isoformat()
        if title is not None:
            updates['title'] = title

        if not updates:
            raise ValueError("No fields to update")

        return self.supabase.update_newsletter(newsletter_id, updates)


# Global service instance
newsletter_service = NewsletterService()
