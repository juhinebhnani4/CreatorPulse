"""
Newsletter service - Business logic for newsletter generation and management.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.ai_newsletter.database.supabase_client import SupabaseManager
from src.ai_newsletter.generators import NewsletterGenerator
from src.ai_newsletter.config.settings import get_settings


class NewsletterService:
    """Service for newsletter generation and management."""

    def __init__(self):
        """Initialize newsletter service."""
        self.supabase = SupabaseManager()
        self.settings = get_settings()

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

        # Load content items from database
        content_items = self.supabase.load_content_items(
            workspace_id=workspace_id,
            days=days_back,
            source=sources[0] if sources and len(sources) == 1 else None,
            limit=max_items * 2  # Fetch more for filtering
        )

        if not content_items:
            raise ValueError(f"No content found in workspace for the last {days_back} days")

        # Filter by sources if specified
        if sources:
            content_items = [item for item in content_items if item.source in sources]

        # Limit to max_items
        content_items = content_items[:max_items]

        if not content_items:
            raise ValueError("No content items match the specified filters")

        # Initialize newsletter generator
        generator = NewsletterGenerator(config=self.settings.newsletter)

        # Override settings
        generator.config.tone = tone
        generator.config.language = language
        generator.config.temperature = temperature

        # Handle model selection
        if use_openrouter:
            generator.config.use_openrouter = True
            if model:
                generator.config.openrouter_model = model
                generator.model = model
            else:
                generator.model = generator.config.openrouter_model

            # Reinitialize client with OpenRouter
            from openai import OpenAI
            generator.client = OpenAI(
                api_key=self.settings.newsletter.openrouter_api_key,
                base_url="https://openrouter.ai/api/v1"
            )
        else:
            generator.config.use_openrouter = False
            if model:
                generator.config.model = model
                generator.model = model
            else:
                generator.model = self.settings.newsletter.model

            # Reinitialize client with OpenAI
            from openai import OpenAI
            generator.client = OpenAI(api_key=self.settings.newsletter.openai_api_key)

        # Generate newsletter
        html_content = generator.generate_newsletter(
            content_items,
            title=title,
            max_items=max_items
        )

        # Extract content item IDs
        content_item_ids = [item.metadata.get('id') for item in content_items if item.metadata.get('id')]

        # Save to database
        newsletter = self.supabase.save_newsletter(
            workspace_id=workspace_id,
            title=title,
            html_content=html_content,
            plain_text_content=None,  # TODO: Generate plain text version
            content_item_ids=content_item_ids,
            model_used=generator.model,
            temperature=temperature,
            tone=tone,
            language=language,
            metadata={
                'sources': sources or [],
                'days_back': days_back,
                'use_openrouter': use_openrouter
            }
        )

        return {
            'newsletter': newsletter,
            'content_items_count': len(content_items),
            'sources_used': list(set(item.source for item in content_items))
        }

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

        return {
            'workspace_id': workspace_id,
            'newsletters': newsletters,
            'count': len(newsletters),
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
        updates = {}
        if status:
            updates['status'] = status
        if sent_at:
            updates['sent_at'] = sent_at.isoformat()
        if title:
            updates['title'] = title

        if not updates:
            raise ValueError("No fields to update")

        return self.supabase.update_newsletter(newsletter_id, updates)


# Global service instance
newsletter_service = NewsletterService()
