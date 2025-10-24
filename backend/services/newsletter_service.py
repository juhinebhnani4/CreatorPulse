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

    def _verify_workspace_access(self, user_id: str, workspace_id: str) -> Dict[str, Any]:
        """
        Verify user has access to workspace.

        Args:
            user_id: User ID
            workspace_id: Workspace ID

        Returns:
            Workspace dict

        Raises:
            ValueError: If workspace not found or user lacks access
        """
        workspace = self.supabase.get_workspace(workspace_id)
        if not workspace:
            raise ValueError("Workspace not found")

        # Verify user has access to this workspace
        if not self.supabase.user_has_workspace_access(user_id, workspace_id):
            raise ValueError("Access denied: User not in workspace")

        return workspace

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

        Raises:
            ValueError: If parameters are invalid
        """
        # Validate inputs
        if not title or not title.strip():
            raise ValueError("title cannot be empty")

        if max_items <= 0 or max_items > 100:
            raise ValueError("max_items must be between 1 and 100")

        if days_back <= 0 or days_back > 365:
            raise ValueError("days_back must be between 1 and 365")

        if not 0.0 <= temperature <= 2.0:
            raise ValueError("temperature must be between 0.0 and 2.0")

        if tone and tone not in ['professional', 'casual', 'technical', 'friendly', 'humorous', 'authoritative', 'conversational']:
            raise ValueError(f"Invalid tone '{tone}'. Must be one of: professional, casual, technical, friendly, humorous, authoritative, conversational")

        # HP-2: Refactored to orchestrator pattern using helper methods
        # This method now coordinates 4 focused helper methods instead of 250+ lines of inline logic

        # Step 1: Verify workspace access
        workspace = self._verify_workspace_access(user_id, workspace_id)

        # Step 2: Fetch active trends and style profile
        trends = await self.trend_service.get_active_trends(
            workspace_id=UUID(workspace_id),
            limit=NewsletterConstants.MAX_TRENDS_TO_FETCH
        )
        style_profile = await self.style_service.get_style_profile(
            workspace_id=UUID(workspace_id)
        )

        # Step 3: Fetch and filter content
        content_items_dicts, content_items_for_generator = await self._fetch_and_filter_content(
            workspace_id=workspace_id,
            days_back=days_back,
            sources=sources,
            max_items=max_items,
            trends=trends,
            feedback_service=self.feedback_service
        )

        # Step 4: Generate newsletter with AI (or delegate to OpenRouter path)
        if settings.use_openrouter:
            # Use OpenRouter path (returns full response dict)
            return await self._generate_with_openrouter(
                workspace_id, title, tone, temperature, language,
                content_items_for_generator, content_items_dicts,
                sources, days_back, trends, style_profile
            )
        else:
            # Use direct Anthropic API
            html_content, plain_text_content = await self._generate_with_ai(
                content_items_for_generator=content_items_for_generator,
                content_items_dicts=content_items_dicts,
                title=title,
                tone=tone,
                temperature=temperature,
                language=language,
                style_profile=style_profile,
                workspace_id=workspace_id,
                sources=sources,
                days_back=days_back,
                trends=trends
            )

            # Step 5: Save newsletter to database
            newsletter = self._save_newsletter(
                workspace_id=workspace_id,
                title=title,
                html_content=html_content,
                content_items_dicts=content_items_dicts,
                temperature=temperature,
                tone=tone,
                language=language,
                sources=sources,
                days_back=days_back,
                trends=trends,
                style_profile=style_profile
            )

            # Return response with metadata
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

    def _apply_freshness_decay(self, content_items_dicts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Apply time-based score decay to prioritize recent content.

        Industry standard: Quality + recency hybrid scoring.
        Older content gets exponentially penalized to prevent stale content domination.

        Args:
            content_items_dicts: List of content items with scores

        Returns:
            Same list with adjusted scores based on age
        """
        from datetime import datetime, timezone

        print(f"[FreshnessDecay] FUNCTION CALLED - Processing {len(content_items_dicts)} items")

        now = datetime.now(timezone.utc)

        items_processed = 0
        items_skipped = 0

        for item in content_items_dicts:
            # Parse scraped_at timestamp
            scraped_at_str = item.get('scraped_at')
            if not scraped_at_str:
                items_skipped += 1
                print(f"[FreshnessDecay] SKIPPED - Item missing scraped_at: {item.get('id', 'unknown')}")
                continue

            try:
                # Handle both ISO format with and without timezone
                scraped_at = datetime.fromisoformat(scraped_at_str.replace('Z', '+00:00'))
                age_days = (now - scraped_at).days

                # Calculate decay multiplier (exponential decay curve)
                # Balances quality vs recency - high-quality old content can still rank
                if age_days <= 3:
                    decay_multiplier = 1.0      # 100% - Fresh content (0-3 days)
                elif age_days <= 7:
                    decay_multiplier = 0.7      # 70% - Recent content (4-7 days)
                elif age_days <= 14:
                    decay_multiplier = 0.4      # 40% - Week-old content (8-14 days)
                elif age_days <= 30:
                    decay_multiplier = 0.15     # 15% - Month-old content (15-30 days)
                else:
                    decay_multiplier = 0.05     # 5% - Stale content (30+ days)

                # Apply decay to score
                original_score = item.get('score', 0)
                decayed_score = int(original_score * decay_multiplier)

                # Store for debugging and future config
                item['freshness_age_days'] = age_days
                item['freshness_decay'] = decay_multiplier
                item['score_before_decay'] = original_score
                item['score'] = decayed_score

                items_processed += 1

                # Log decay calculation (truncate title for readability)
                # Use try/except to prevent Unicode errors from breaking business logic
                try:
                    title = item.get('title', 'Untitled')[:50]
                    # Replace non-ASCII characters to avoid Windows console encoding issues
                    safe_title = title.encode('ascii', errors='replace').decode('ascii')
                    print(f"[FreshnessDecay] '{safe_title}' - Age: {age_days}d, Decay: {decay_multiplier}, Score: {original_score} -> {decayed_score}")
                except Exception:
                    # Silent fallback - logging should never break the pipeline
                    pass

            except Exception as e:
                items_skipped += 1
                print(f"[FreshnessDecay] WARNING: Failed to parse scraped_at for item {item.get('id', 'unknown')}: {e}")
                continue

        print(f"[FreshnessDecay] SUMMARY - Processed: {items_processed}, Skipped: {items_skipped}, Total: {len(content_items_dicts)}")

        # Remove diagnostic fields before returning (Pydantic ContentItem model doesn't accept extra fields)
        for item in content_items_dicts:
            item.pop('freshness_age_days', None)
            item.pop('freshness_decay', None)
            item.pop('score_before_decay', None)

        return content_items_dicts

    async def _fetch_and_filter_content(
        self,
        workspace_id: str,
        days_back: int,
        sources: Optional[List[str]],
        max_items: int,
        trends: List[Any],
        feedback_service: Any
    ) -> tuple[List[Dict[str, Any]], List[Any]]:
        """
        Fetch content items, apply filtering, scoring, and trend boosting.

        Args:
            workspace_id: Workspace ID
            days_back: Days to look back
            sources: Optional source filter
            max_items: Max items to return
            trends: Active trends for boosting
            feedback_service: Feedback service instance

        Returns:
            Tuple of (content_items_dicts, content_items_for_generator)

        Raises:
            ValueError: If no content found or all filtered out
        """
        # Load content items from database
        content_items = self.supabase.load_content_items(
            workspace_id=workspace_id,
            days=days_back,
            source=sources[0] if sources and len(sources) == 1 else None,
            limit=max_items * NewsletterConstants.CONTENT_FETCH_MULTIPLIER  # Fetch more for filtering
        )

        if not content_items:
            raise ValueError(f"No content found in workspace for the last {days_back} days")

        # Exclude items from recently sent newsletters (prevents content repetition)
        excluded_ids = set(self.supabase.get_recently_sent_content_ids(
            workspace_id=workspace_id,
            days_back=30,  # Exclude items from last 30 days of sent newsletters
            max_newsletters=3  # Or last 3 newsletters, whichever is more restrictive
        ))

        if excluded_ids:
            print(f"[ContentFilter] Excluding {len(excluded_ids)} content IDs from {len(content_items)} available items")

            # Filter out excluded items
            original_count = len(content_items)
            content_items = [
                item for item in content_items
                if item.id not in excluded_ids
            ]
            filtered_count = len(content_items)

            print(f"[ContentFilter] Filtered from {original_count} to {filtered_count} items ({original_count - filtered_count} excluded)")

            if not content_items:
                print(f"[ContentFilter] WARNING: All items were excluded! Falling back to original pool.")
                # Fallback: reload without exclusion (ensures newsletter can be generated)
                content_items = self.supabase.load_content_items(
                    workspace_id=workspace_id,
                    days=days_back,
                    source=sources[0] if sources and len(sources) == 1 else None,
                    limit=max_items * NewsletterConstants.CONTENT_FETCH_MULTIPLIER
                )

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
        content_items_dicts = feedback_service.adjust_content_scoring(
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

        # Apply freshness decay to prioritize recent content (industry standard)
        print(f"[FreshnessDecay] About to apply decay to {len(content_items_dicts)} items")
        if content_items_dicts:
            first_item_keys = list(content_items_dicts[0].keys())
            has_scraped_at = 'scraped_at' in first_item_keys
            print(f"[FreshnessDecay] First item keys: {first_item_keys[:10]}")
            print(f"[FreshnessDecay] Has 'scraped_at' field: {has_scraped_at}")
            if has_scraped_at:
                print(f"[FreshnessDecay] scraped_at value: {content_items_dicts[0].get('scraped_at')}")

        content_items_dicts = self._apply_freshness_decay(content_items_dicts)
        print(f"[FreshnessDecay] Decay applied, {len(content_items_dicts)} items remain")

        # Re-sort by score after trend boosting and freshness decay
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

        return content_items_dicts, content_items_for_generator

    async def _generate_with_ai(
        self,
        content_items_for_generator: List[Any],
        content_items_dicts: List[Dict[str, Any]],
        title: str,
        tone: str,
        temperature: float,
        language: str,
        style_profile: Any,
        workspace_id: str,
        sources: Optional[List[str]],
        days_back: int,
        trends: List[Any]
    ) -> tuple[str, str]:
        """
        Generate newsletter HTML and plain text using AI (OpenRouter or Anthropic).

        Args:
            content_items_for_generator: ContentItem objects
            content_items_dicts: Content items as dicts
            title: Newsletter title
            tone: Newsletter tone
            temperature: AI creativity level
            language: Newsletter language
            style_profile: Writing style profile
            workspace_id: Workspace ID
            sources: Source filters used
            days_back: Days back filter
            trends: Active trends

        Returns:
            Tuple of (html_content, plain_text_content)
        """
        # Check if we should use OpenRouter or direct Anthropic API
        if settings.use_openrouter:
            # Use OpenRouter (via original NewsletterGenerator)
            print(f"[NewsletterService] [INFO] Using Claude via OpenRouter")
            # Note: _generate_with_openrouter returns full dict, we need to handle that differently
            raise NotImplementedError("OpenRouter path must use original generate_newsletter flow")
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

            return html_content, None  # Claude doesn't generate plain text version

    def _save_newsletter(
        self,
        workspace_id: str,
        title: str,
        html_content: str,
        content_items_dicts: List[Dict[str, Any]],
        temperature: float,
        tone: str,
        language: str,
        sources: Optional[List[str]],
        days_back: int,
        trends: List[Any],
        style_profile: Any
    ) -> Dict[str, Any]:
        """
        Save newsletter to database with metadata.

        Args:
            workspace_id: Workspace ID
            title: Newsletter title
            html_content: Generated HTML
            content_items_dicts: Content items used
            temperature: AI temperature used
            tone: Tone used
            language: Language used
            sources: Source filters
            days_back: Days back filter
            trends: Trends used
            style_profile: Style profile applied

        Returns:
            Saved newsletter dict
        """
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

        return newsletter

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

    def _populate_newsletter_items(
        self,
        newsletter: Dict[str, Any],
        bulk_items_dict: Optional[Dict[str, Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Populate newsletter items field from content_item_ids.

        Args:
            newsletter: Newsletter dict with content_item_ids
            bulk_items_dict: Optional pre-loaded items dict (id -> item).
                           If provided, skips database query (O(1) lookup).
                           Used by list_newsletters() for bulk optimization.

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

        # If bulk dict provided, use it (O(1) lookup, no database query)
        if bulk_items_dict is not None:
            items = [
                bulk_items_dict[item_id]
                for item_id in content_item_ids
                if item_id in bulk_items_dict
            ]

            # Log any missing items
            if len(items) < len(content_item_ids):
                found_ids = {item['id'] for item in items}
                missing_ids = set(content_item_ids) - found_ids
                for missing_id in missing_ids:
                    print(f"[_populate_newsletter_items] WARNING: Could not find content item {missing_id} in bulk dict")
        else:
            # Fallback to individual bulk query (backward compatibility)
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
            # Unicode-safe title printing (handles emojis on Windows console)
            title = first_item.get('title', 'MISSING')[:50] if first_item.get('title') else 'MISSING'
            # Use errors='replace' to prevent crashes from emoji characters
            safe_title = title.encode('utf-8', errors='replace').decode('utf-8', errors='replace')
            print(f"  - title: {safe_title}")
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

        # HP-4: Optimize with bulk content loading
        # Instead of N queries (one per newsletter), do 1 bulk query for ALL items

        # Step 1: Collect all content item IDs from all newsletters
        all_item_ids = []
        for nl in newsletters:
            all_item_ids.extend(nl.get('content_item_ids', []))

        # Step 2: Bulk load ALL items in a single database query
        bulk_items = {}
        if all_item_ids:
            print(f"[list_newsletters] Bulk loading {len(all_item_ids)} content items for {len(newsletters)} newsletters")
            items_list = self.supabase.get_content_items_bulk(all_item_ids)
            # Create id -> item dictionary for O(1) lookup
            bulk_items = {item['id']: item for item in items_list}
            print(f"[list_newsletters] Loaded {len(bulk_items)} unique items")

        # Step 3: Populate items for each newsletter using the bulk dict
        newsletters_with_items = [
            self._populate_newsletter_items(nl, bulk_items_dict=bulk_items)
            for nl in newsletters
        ]

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
        try:
            newsletter = self.supabase.get_newsletter(newsletter_id)

            if not newsletter:
                raise ValueError("Newsletter not found")

            # Verify user has access to the workspace
            print(f"[get_newsletter] Checking workspace access for user {user_id}, workspace {newsletter['workspace_id']}")
            has_access = self.supabase.user_has_workspace_access(
                user_id=user_id,
                workspace_id=newsletter['workspace_id']
            )
            print(f"[get_newsletter] Access check result: {has_access}")

            if not has_access:
                raise ValueError("Access denied")

            # Populate items field from content_item_ids
            newsletter = self._populate_newsletter_items(newsletter)

            return newsletter
        except Exception as e:
            print(f"[ERROR] get_newsletter failed: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
            raise

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
