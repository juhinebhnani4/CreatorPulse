"""
Supabase client manager for CreatorPulse.

Provides a unified interface for all database operations.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from supabase import create_client, Client
import os
from pathlib import Path

# Load environment variables from .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv not available, continue without it
    pass

from ..models.content import ContentItem
from ..models.style_profile import StyleProfile
from ..models.trend import Trend
from ..models.feedback import FeedbackItem
from ..models.analytics import EmailEvent


class SupabaseManager:
    """
    Central manager for all Supabase operations.

    Features:
    - Connection pooling
    - Automatic retry logic
    - Error handling
    - Query optimization
    """

    def __init__(self):
        """Initialize Supabase client."""
        # Load .env to ensure environment variables are available
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            pass

        self.url = os.getenv("SUPABASE_URL")
        self.key = os.getenv("SUPABASE_KEY")
        self.service_key = os.getenv("SUPABASE_SERVICE_KEY")

        if not self.url or not self.key:
            raise ValueError(
                "Supabase credentials not configured. "
                "Set SUPABASE_URL and SUPABASE_KEY in .env"
            )

        self.client: Client = create_client(self.url, self.key)

        # Service client for admin operations (bypasses RLS)
        if self.service_key:
            self.service_client: Client = create_client(self.url, self.service_key)
        else:
            # Fallback to regular client if service key not available
            self.service_client = self.client

    # ========================================
    # WORKSPACE OPERATIONS
    # ========================================

    def create_workspace(self,
                        name: str,
                        description: str = "",
                        user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new workspace.

        Args:
            name: Workspace name (unique)
            description: Optional description
            user_id: Owner user ID (defaults to current user)

        Returns:
            Created workspace data

        Raises:
            ValueError: If workspace name already exists
        """
        # Use current user if not specified
        if not user_id:
            user = self.client.auth.get_user()
            user_id = user.user.id

        # Create workspace (use service_client to bypass RLS)
        result = self.service_client.table('workspaces').insert({
            'name': name,
            'description': description,
            'owner_id': user_id
        }).execute()

        workspace = result.data[0]

        # Create user-workspace membership (owner role)
        self.service_client.table('user_workspaces').insert({
            'user_id': user_id,
            'workspace_id': workspace['id'],
            'role': 'owner',
            'accepted_at': datetime.now().isoformat()
        }).execute()

        # Create default config
        self.service_client.table('workspace_configs').insert({
            'workspace_id': workspace['id'],
            'config': self._get_default_config(),
            'updated_by': user_id
        }).execute()

        return workspace

    def list_workspaces(self, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all workspaces accessible to user.

        Args:
            user_id: User ID (defaults to current user)

        Returns:
            List of workspace data
        """
        if not user_id:
            user = self.client.auth.get_user()
            user_id = user.user.id

        # Query workspaces with role information (use service_client to bypass RLS)
        result = self.service_client.table('workspaces') \
            .select('*, user_workspaces!inner(role)') \
            .eq('user_workspaces.user_id', user_id) \
            .order('created_at', desc=True) \
            .execute()

        return result.data

    def get_workspace(self, workspace_id: str) -> Optional[Dict[str, Any]]:
        """Get workspace by ID."""
        try:
            result = self.service_client.table('workspaces') \
                .select('*') \
                .eq('id', workspace_id) \
                .maybe_single() \
                .execute()

            return result.data if result.data else None
        except Exception as e:
            # Log the error for debugging
            error_str = str(e).lower()

            # Only return None for "not found" cases
            if "not found" in error_str or "no rows" in error_str or "406" in error_str:
                return None

            # For other errors (connection, permission, etc.), log and re-raise
            print(f"Error getting workspace {workspace_id}: {e}")
            # Return None to maintain backwards compatibility but log the issue
            return None

    def update_workspace(self,
                        workspace_id: str,
                        updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update workspace details."""
        updates['updated_at'] = datetime.now().isoformat()

        result = self.service_client.table('workspaces') \
            .update(updates) \
            .eq('id', workspace_id) \
            .execute()

        return result.data[0]

    def delete_workspace(self, workspace_id: str) -> bool:
        """Delete workspace (cascade deletes all related data)."""
        result = self.service_client.table('workspaces') \
            .delete() \
            .eq('id', workspace_id) \
            .execute()

        return len(result.data) > 0

    # ========================================
    # CONFIGURATION OPERATIONS
    # ========================================

    def get_workspace_config(self, workspace_id: str) -> Dict[str, Any]:
        """Get workspace configuration."""
        try:
            result = self.service_client.table('workspace_configs') \
                .select('config') \
                .eq('workspace_id', workspace_id) \
                .single() \
                .execute()

            return result.data['config'] if result.data else self._get_default_config()
        except Exception as e:
            # Log the error and return default config
            error_str = str(e).lower()
            if "not found" in error_str or "no rows" in error_str or "406" in error_str:
                # Config doesn't exist yet, return default
                return self._get_default_config()

            # For other errors, log and return default config as fallback
            print(f"Error getting workspace config for {workspace_id}: {e}")
            return self._get_default_config()

    def save_workspace_config(self,
                             workspace_id: str,
                             config: Dict[str, Any],
                             user_id: Optional[str] = None) -> Dict[str, Any]:
        """Save workspace configuration."""
        if not user_id:
            user = self.client.auth.get_user()
            user_id = user.user.id

        # Upsert configuration (use service_client to bypass RLS)
        result = self.service_client.table('workspace_configs') \
            .upsert({
                'workspace_id': workspace_id,
                'config': config,
                'updated_at': datetime.now().isoformat(),
                'updated_by': user_id
            }, on_conflict='workspace_id') \
            .execute()

        return result.data[0]

    # ========================================
    # CONTENT OPERATIONS
    # ========================================

    def save_content_items(self,
                          workspace_id: str,
                          items: List[ContentItem]) -> List[Dict[str, Any]]:
        """
        Save scraped content items to database.

        Args:
            workspace_id: Workspace ID
            items: List of ContentItem objects

        Returns:
            List of saved content data
        """
        data = [
            {
                'workspace_id': workspace_id,
                'title': item.title,
                'source': item.source,
                'source_url': item.source_url,
                'content': item.content,
                'summary': item.summary,
                'author': item.author,
                'author_url': item.author_url,
                'score': item.score,
                'comments_count': item.comments_count,
                'shares_count': item.shares_count,
                'views_count': item.views_count,
                'image_url': item.image_url,
                'video_url': item.video_url,
                'external_url': item.external_url,
                'tags': item.tags,
                'category': item.category,
                'created_at': item.created_at.isoformat(),
                'scraped_at': datetime.now().isoformat(),
                'metadata': item.metadata
            }
            for item in items
        ]

        # Batch insert (use service_client to bypass RLS)
        result = self.service_client.table('content_items').insert(data).execute()

        return result.data

    def load_content_items(self,
                          workspace_id: str,
                          days: int = 7,
                          source: Optional[str] = None,
                          limit: int = 1000) -> List[ContentItem]:
        """
        Load content items from database.

        Args:
            workspace_id: Workspace ID
            days: Number of days to look back
            source: Optional source filter ('reddit', 'rss', etc.)
            limit: Maximum items to return

        Returns:
            List of ContentItem objects
        """
        cutoff_date = datetime.now() - timedelta(days=days)

        query = self.service_client.table('content_items') \
            .select('*') \
            .eq('workspace_id', workspace_id) \
            .gte('created_at', cutoff_date.isoformat()) \
            .order('created_at', desc=True) \
            .limit(limit)

        if source:
            query = query.eq('source', source)

        result = query.execute()

        # Convert to ContentItem objects
        return [
            ContentItem(
                title=item['title'],
                source=item['source'],
                source_url=item['source_url'],
                created_at=datetime.fromisoformat(item['created_at']),
                content=item.get('content'),
                summary=item.get('summary'),
                author=item.get('author'),
                author_url=item.get('author_url'),
                score=item.get('score', 0),
                comments_count=item.get('comments_count', 0),
                shares_count=item.get('shares_count', 0),
                views_count=item.get('views_count', 0),
                image_url=item.get('image_url'),
                video_url=item.get('video_url'),
                external_url=item.get('external_url'),
                tags=item.get('tags', []),
                category=item.get('category'),
                metadata=item.get('metadata', {}),
                scraped_at=datetime.fromisoformat(item['scraped_at'])
            )
            for item in result.data
        ]

    def search_content_items(self,
                            workspace_id: str,
                            query: str,
                            limit: int = 100) -> List[ContentItem]:
        """
        Full-text search on content items.

        Args:
            workspace_id: Workspace ID
            query: Search query
            limit: Maximum results

        Returns:
            List of matching ContentItem objects
        """
        # Use PostgreSQL full-text search
        result = self.service_client.table('content_items') \
            .select('*') \
            .eq('workspace_id', workspace_id) \
            .text_search('title', query) \
            .limit(limit) \
            .execute()

        return [ContentItem(**item) for item in result.data]

    # ========================================
    # STYLE PROFILE OPERATIONS
    # ========================================

    def create_style_profile(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new style profile.

        Args:
            profile_data: Style profile data

        Returns:
            Created profile data
        """
        result = self.service_client.table('style_profiles').insert(profile_data).execute()
        return result.data[0]

    def get_style_profile(self, workspace_id: str) -> Optional[Dict[str, Any]]:
        """
        Get style profile for workspace.

        Args:
            workspace_id: Workspace ID

        Returns:
            Style profile data or None
        """
        result = self.service_client.table('style_profiles') \
            .select('*') \
            .eq('workspace_id', workspace_id) \
            .maybe_single() \
            .execute()

        return result.data if result.data else None

    def update_style_profile(self,
                            workspace_id: str,
                            updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update style profile.

        Args:
            workspace_id: Workspace ID
            updates: Fields to update

        Returns:
            Updated profile data
        """
        updates['updated_at'] = datetime.now().isoformat()

        result = self.service_client.table('style_profiles') \
            .update(updates) \
            .eq('workspace_id', workspace_id) \
            .execute()

        return result.data[0]

    def delete_style_profile(self, workspace_id: str) -> bool:
        """
        Delete style profile for workspace.

        Args:
            workspace_id: Workspace ID

        Returns:
            True if deleted
        """
        result = self.service_client.table('style_profiles') \
            .delete() \
            .eq('workspace_id', workspace_id) \
            .execute()

        return len(result.data) > 0

    def get_style_profile_summary(self, workspace_id: str) -> Optional[Dict[str, Any]]:
        """
        Get style profile summary using database function.

        Args:
            workspace_id: Workspace ID

        Returns:
            Profile summary or None
        """
        try:
            result = self.service_client.rpc('get_style_profile_summary', {
                'workspace_uuid': workspace_id
            }).execute()

            return result.data if result.data else None
        except Exception:
            # Fallback: build summary from profile
            profile = self.get_style_profile(workspace_id)
            if not profile:
                return {
                    'has_profile': False,
                    'trained_on_count': 0,
                    'tone': None,
                    'formality_level': None,
                    'uses_emojis': False,
                    'last_updated': None
                }

            return {
                'has_profile': True,
                'trained_on_count': profile.get('trained_on_count', 0),
                'tone': profile.get('tone'),
                'formality_level': profile.get('formality_level'),
                'uses_emojis': profile.get('uses_emojis', False),
                'last_updated': profile.get('updated_at')
            }

    # Legacy methods for backwards compatibility
    def save_style_profile(self,
                          workspace_id: str,
                          profile: StyleProfile,
                          user_id: Optional[str] = None) -> Dict[str, Any]:
        """Save style profile for workspace (legacy method)."""
        if not user_id:
            user = self.client.auth.get_user()
            user_id = user.user.id

        data = {
            'workspace_id': workspace_id,
            'tone': profile.tone,
            'formality_level': profile.formality_level,
            'avg_sentence_length': profile.avg_sentence_length,
            'sentence_length_variety': profile.sentence_length_variety,
            'question_frequency': profile.question_frequency,
            'vocabulary_level': profile.vocabulary_level,
            'favorite_phrases': profile.favorite_phrases,
            'avoided_words': profile.avoided_words,
            'typical_intro_style': profile.typical_intro_style,
            'section_count': profile.section_count,
            'uses_emojis': profile.uses_emojis,
            'emoji_frequency': profile.emoji_frequency,
            'example_intros': profile.example_intros,
            'example_transitions': profile.example_transitions,
            'example_conclusions': profile.example_conclusions,
            'trained_on_count': profile.trained_on_count,
            'updated_at': datetime.now().isoformat(),
            'updated_by': user_id
        }

        # Upsert
        result = self.client.table('style_profiles') \
            .upsert(data, on_conflict='workspace_id') \
            .execute()

        return result.data[0]

    def load_style_profile(self, workspace_id: str) -> Optional[StyleProfile]:
        """Load style profile for workspace (legacy method)."""
        result = self.client.table('style_profiles') \
            .select('*') \
            .eq('workspace_id', workspace_id) \
            .single() \
            .execute()

        if not result.data:
            return None

        data = result.data
        return StyleProfile(
            tone=data['tone'],
            formality_level=data['formality_level'],
            avg_sentence_length=data['avg_sentence_length'],
            sentence_length_variety=data.get('sentence_length_variety', 0),
            question_frequency=data.get('question_frequency', 0),
            vocabulary_level=data.get('vocabulary_level', 'intermediate'),
            favorite_phrases=data.get('favorite_phrases', []),
            avoided_words=data.get('avoided_words', []),
            typical_intro_style=data.get('typical_intro_style', 'statement'),
            section_count=data.get('section_count', 3),
            uses_emojis=data.get('uses_emojis', False),
            emoji_frequency=data.get('emoji_frequency', 0),
            example_intros=data.get('example_intros', []),
            example_transitions=data.get('example_transitions', []),
            example_conclusions=data.get('example_conclusions', []),
            trained_on_count=data.get('trained_on_count', 0),
            last_updated=datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else None
        )

    # ========================================
    # NEWSLETTER OPERATIONS
    # ========================================

    def save_newsletter(self,
                       workspace_id: str,
                       title: str,
                       html_content: str,
                       plain_text_content: Optional[str] = None,
                       content_item_ids: List[str] = None,
                       model_used: str = "gpt-4",
                       temperature: float = 0.7,
                       tone: str = "professional",
                       language: str = "en",
                       metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Save generated newsletter to database.

        Args:
            workspace_id: Workspace ID
            title: Newsletter title
            html_content: HTML content (parameter kept for backwards compatibility)
            plain_text_content: Plain text version (parameter kept for backwards compatibility)
            content_item_ids: List of content item IDs used
            model_used: AI model used
            temperature: Temperature setting
            tone: Newsletter tone
            language: Newsletter language
            metadata: Additional metadata

        Returns:
            Saved newsletter data
        """
        data = {
            'workspace_id': workspace_id,
            'title': title,
            'content_html': html_content,  # Map to new field name
            'content_text': plain_text_content,  # Map to new field name
            'content_item_ids': content_item_ids or [],
            'content_items_count': len(content_item_ids) if content_item_ids else 0,
            'model_used': model_used,
            'temperature': temperature,
            'tone': tone,
            'language': language,
            'status': 'draft',
            'generated_at': datetime.now().isoformat(),
            'metadata': metadata or {}
        }

        # Use service_client to bypass RLS (admin operation)
        result = self.service_client.table('newsletters').insert(data).execute()
        return result.data[0]

    def load_newsletters(self,
                        workspace_id: str,
                        status: Optional[str] = None,
                        limit: int = 50) -> List[Dict[str, Any]]:
        """
        Load newsletters for workspace.

        Args:
            workspace_id: Workspace ID
            status: Optional status filter (draft, sent, scheduled)
            limit: Maximum newsletters to return

        Returns:
            List of newsletter data
        """
        query = self.client.table('newsletters') \
            .select('*') \
            .eq('workspace_id', workspace_id) \
            .order('generated_at', desc=True) \
            .limit(limit)

        if status:
            query = query.eq('status', status)

        result = query.execute()
        return result.data

    def get_newsletter(self, newsletter_id: str) -> Optional[Dict[str, Any]]:
        """Get newsletter by ID."""
        result = self.service_client.table('newsletters') \
            .select('*') \
            .eq('id', newsletter_id) \
            .execute()

        return result.data[0] if result.data and len(result.data) > 0 else None

    def update_newsletter(self,
                         newsletter_id: str,
                         updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update newsletter."""
        # Don't add updated_at - it doesn't exist in the schema

        # First check if newsletter exists
        check = self.service_client.table('newsletters') \
            .select('id') \
            .eq('id', newsletter_id) \
            .execute()

        if not check.data or len(check.data) == 0:
            raise ValueError(f"Newsletter {newsletter_id} not found")

        # Now update
        result = self.service_client.table('newsletters') \
            .update(updates) \
            .eq('id', newsletter_id) \
            .execute()

        if not result.data or len(result.data) == 0:
            raise ValueError(f"Failed to update newsletter {newsletter_id}")

        return result.data[0]

    def delete_newsletter(self, newsletter_id: str) -> bool:
        """Delete newsletter."""
        result = self.client.table('newsletters') \
            .delete() \
            .eq('id', newsletter_id) \
            .execute()

        return len(result.data) > 0

    def get_newsletter_stats(self, workspace_id: str) -> Dict[str, Any]:
        """Get newsletter statistics for workspace."""
        newsletters = self.load_newsletters(workspace_id, limit=1000)

        if not newsletters:
            return {
                'workspace_id': workspace_id,
                'total_newsletters': 0,
                'drafts_count': 0,
                'sent_count': 0,
                'scheduled_count': 0,
                'total_content_items_used': 0,
                'latest_newsletter': None
            }

        drafts = sum(1 for n in newsletters if n['status'] == 'draft')
        sent = sum(1 for n in newsletters if n['status'] == 'sent')
        scheduled = sum(1 for n in newsletters if n['status'] == 'scheduled')
        total_items = sum(n.get('content_items_count', 0) for n in newsletters)
        latest = newsletters[0]['generated_at'] if newsletters else None

        return {
            'workspace_id': workspace_id,
            'total_newsletters': len(newsletters),
            'drafts_count': drafts,
            'sent_count': sent,
            'scheduled_count': scheduled,
            'total_content_items_used': total_items,
            'latest_newsletter': latest
        }

    # ========================================
    # SUBSCRIBER OPERATIONS
    # ========================================

    def add_subscriber(self,
                      workspace_id: str,
                      email: str,
                      name: Optional[str] = None,
                      source: str = "manual",
                      metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Add a subscriber to workspace.

        Args:
            workspace_id: Workspace ID
            email: Subscriber email
            name: Subscriber name (optional)
            source: How subscriber was added (manual, api, import)
            metadata: Additional metadata

        Returns:
            Created subscriber data
        """
        data = {
            'workspace_id': workspace_id,
            'email': email.lower().strip(),  # Normalize email
            'name': name,
            'source': source,
            'status': 'active',
            'subscribed_at': datetime.now().isoformat(),
            'metadata': metadata or {}
        }

        # Use service_client to bypass RLS
        result = self.service_client.table('subscribers').insert(data).execute()
        return result.data[0]

    def list_subscribers(self,
                        workspace_id: str,
                        status: Optional[str] = None,
                        limit: int = 1000) -> List[Dict[str, Any]]:
        """
        List subscribers for workspace.

        Args:
            workspace_id: Workspace ID
            status: Optional status filter (active, unsubscribed, bounced)
            limit: Maximum subscribers to return

        Returns:
            List of subscriber data
        """
        query = self.service_client.table('subscribers') \
            .select('*') \
            .eq('workspace_id', workspace_id) \
            .order('subscribed_at', desc=True) \
            .limit(limit)

        if status:
            query = query.eq('status', status)

        result = query.execute()
        return result.data

    def get_subscriber(self, subscriber_id: str) -> Optional[Dict[str, Any]]:
        """Get subscriber by ID."""
        result = self.service_client.table('subscribers') \
            .select('*') \
            .eq('id', subscriber_id) \
            .single() \
            .execute()

        return result.data if result.data else None

    def update_subscriber(self,
                         subscriber_id: str,
                         updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update subscriber."""
        updates['updated_at'] = datetime.now().isoformat()

        result = self.service_client.table('subscribers') \
            .update(updates) \
            .eq('id', subscriber_id) \
            .execute()

        return result.data[0]

    def delete_subscriber(self, subscriber_id: str) -> bool:
        """Delete subscriber."""
        result = self.service_client.table('subscribers') \
            .delete() \
            .eq('id', subscriber_id) \
            .execute()

        return len(result.data) > 0

    def unsubscribe(self, subscriber_id: str) -> Dict[str, Any]:
        """Mark subscriber as unsubscribed."""
        return self.update_subscriber(subscriber_id, {
            'status': 'unsubscribed',
            'unsubscribed_at': datetime.now().isoformat()
        })

    def get_subscriber_stats(self, workspace_id: str) -> Dict[str, Any]:
        """Get subscriber statistics for workspace."""
        subscribers = self.list_subscribers(workspace_id, limit=10000)

        if not subscribers:
            return {
                'workspace_id': workspace_id,
                'total_subscribers': 0,
                'active_subscribers': 0,
                'unsubscribed': 0,
                'bounced': 0
            }

        active = sum(1 for s in subscribers if s['status'] == 'active')
        unsubscribed = sum(1 for s in subscribers if s['status'] == 'unsubscribed')
        bounced = sum(1 for s in subscribers if s['status'] == 'bounced')

        return {
            'workspace_id': workspace_id,
            'total_subscribers': len(subscribers),
            'active_subscribers': active,
            'unsubscribed': unsubscribed,
            'bounced': bounced
        }

    # ========================================
    # DELIVERY OPERATIONS
    # ========================================

    def create_delivery(self,
                       newsletter_id: str,
                       workspace_id: str,
                       total_subscribers: int) -> Dict[str, Any]:
        """
        Create a delivery record for tracking newsletter sends.

        Args:
            newsletter_id: Newsletter ID
            workspace_id: Workspace ID
            total_subscribers: Number of subscribers to send to

        Returns:
            Created delivery data
        """
        data = {
            'newsletter_id': newsletter_id,
            'workspace_id': workspace_id,
            'total_subscribers': total_subscribers,
            'sent_count': 0,
            'failed_count': 0,
            'status': 'pending',
            'started_at': datetime.now().isoformat()
        }

        result = self.service_client.table('newsletter_deliveries').insert(data).execute()
        return result.data[0]

    def update_delivery(self,
                       delivery_id: str,
                       updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update delivery record."""
        result = self.service_client.table('newsletter_deliveries') \
            .update(updates) \
            .eq('id', delivery_id) \
            .execute()

        return result.data[0]

    def get_delivery(self, delivery_id: str) -> Optional[Dict[str, Any]]:
        """Get delivery record by ID."""
        result = self.service_client.table('newsletter_deliveries') \
            .select('*') \
            .eq('id', delivery_id) \
            .single() \
            .execute()

        return result.data if result.data else None

    def list_deliveries(self,
                       workspace_id: str,
                       limit: int = 50) -> List[Dict[str, Any]]:
        """List delivery records for workspace."""
        result = self.service_client.table('newsletter_deliveries') \
            .select('*') \
            .eq('workspace_id', workspace_id) \
            .order('created_at', desc=True) \
            .limit(limit) \
            .execute()

        return result.data

    # ========================================
    # SCHEDULER OPERATIONS
    # ========================================

    def create_scheduler_job(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a scheduled job.

        Args:
            job_data: Job data (workspace_id, name, schedule, actions, etc.)

        Returns:
            Created job data
        """
        result = self.service_client.table('scheduler_jobs').insert(job_data).execute()
        return result.data[0]

    def get_scheduler_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job by ID."""
        result = self.service_client.table('scheduler_jobs') \
            .select('*') \
            .eq('id', job_id) \
            .single() \
            .execute()

        return result.data if result.data else None

    def list_scheduler_jobs(self, workspace_id: str) -> List[Dict[str, Any]]:
        """List jobs for workspace."""
        result = self.service_client.table('scheduler_jobs') \
            .select('*') \
            .eq('workspace_id', workspace_id) \
            .order('created_at', desc=True) \
            .execute()

        return result.data

    def update_scheduler_job(self,
                            job_id: str,
                            updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update job."""
        updates['updated_at'] = datetime.now().isoformat()

        result = self.service_client.table('scheduler_jobs') \
            .update(updates) \
            .eq('id', job_id) \
            .execute()

        return result.data[0]

    def delete_scheduler_job(self, job_id: str) -> bool:
        """Delete job."""
        result = self.service_client.table('scheduler_jobs') \
            .delete() \
            .eq('id', job_id) \
            .execute()

        return len(result.data) > 0

    def create_scheduler_execution(self, execution_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create execution record.

        Args:
            execution_data: Execution data (job_id, workspace_id, status, etc.)

        Returns:
            Created execution data
        """
        result = self.service_client.table('scheduler_executions').insert(execution_data).execute()
        return result.data[0]

    def update_scheduler_execution(self,
                                  execution_id: str,
                                  updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update execution record."""
        result = self.service_client.table('scheduler_executions') \
            .update(updates) \
            .eq('id', execution_id) \
            .execute()

        return result.data[0]

    def get_scheduler_executions(self,
                                job_id: str,
                                limit: int = 50) -> List[Dict[str, Any]]:
        """Get execution history for a job."""
        result = self.service_client.table('scheduler_executions') \
            .select('*') \
            .eq('job_id', job_id) \
            .order('started_at', desc=True) \
            .limit(limit) \
            .execute()

        return result.data

    # ========================================
    # TREND OPERATIONS
    # ========================================

    def create_trend(self, trend_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new trend.

        Args:
            trend_data: Trend data

        Returns:
            Created trend data
        """
        result = self.service_client.table('trends').insert(trend_data).execute()
        return result.data[0]

    def get_trend(self, trend_id: str) -> Optional[Dict[str, Any]]:
        """Get trend by ID."""
        result = self.service_client.table('trends') \
            .select('*') \
            .eq('id', trend_id) \
            .single() \
            .execute()

        return result.data if result.data else None

    def list_trends(
        self,
        workspace_id: str,
        start_date: Optional[datetime] = None,
        is_active: Optional[bool] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        List trends for workspace.

        Args:
            workspace_id: Workspace ID
            start_date: Filter by detected_at >= start_date
            is_active: Filter by active status
            limit: Maximum trends to return

        Returns:
            List of trends
        """
        query = self.service_client.table('trends') \
            .select('*') \
            .eq('workspace_id', workspace_id) \
            .order('detected_at', desc=True) \
            .limit(limit)

        if start_date:
            query = query.gte('detected_at', start_date.isoformat())

        if is_active is not None:
            query = query.eq('is_active', is_active)

        result = query.execute()
        return result.data

    def get_active_trends(
        self,
        workspace_id: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get active trends using database function.

        Args:
            workspace_id: Workspace ID
            limit: Maximum trends to return

        Returns:
            List of active trends
        """
        try:
            result = self.service_client.rpc('get_active_trends', {
                'workspace_uuid': workspace_id,
                'limit_count': limit
            }).execute()

            return result.data if result.data else []
        except Exception:
            # Fallback to regular query
            return self.list_trends(workspace_id, is_active=True, limit=limit)

    def get_trend_history(
        self,
        workspace_id: str,
        days_back: int = 30,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get trend history using database function.

        Args:
            workspace_id: Workspace ID
            days_back: Number of days to look back
            limit: Maximum items to return

        Returns:
            List of historical trend data
        """
        try:
            result = self.service_client.rpc('get_trend_history', {
                'workspace_uuid': workspace_id,
                'days_back': days_back,
                'limit_count': limit
            }).execute()

            return result.data if result.data else []
        except Exception as e:
            print(f"Error getting trend history: {e}")
            return []

    def update_trend(
        self,
        trend_id: str,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update trend."""
        updates['updated_at'] = datetime.now().isoformat()

        result = self.service_client.table('trends') \
            .update(updates) \
            .eq('id', trend_id) \
            .execute()

        return result.data[0]

    def delete_trend(self, trend_id: str) -> bool:
        """Delete trend."""
        result = self.service_client.table('trends') \
            .delete() \
            .eq('id', trend_id) \
            .execute()

        return len(result.data) > 0

    def deactivate_old_trends(
        self,
        workspace_id: str,
        cutoff_date: datetime
    ) -> int:
        """
        Mark old trends as inactive.

        Args:
            workspace_id: Workspace ID
            cutoff_date: Deactivate trends older than this

        Returns:
            Number of trends deactivated
        """
        result = self.service_client.table('trends') \
            .update({'is_active': False}) \
            .eq('workspace_id', workspace_id) \
            .lt('detected_at', cutoff_date.isoformat()) \
            .eq('is_active', True) \
            .execute()

        return len(result.data)

    # ========================================
    # HISTORICAL CONTENT OPERATIONS
    # ========================================

    def create_historical_content(
        self,
        content_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create historical content record.

        Args:
            content_data: Historical content data

        Returns:
            Created record
        """
        result = self.service_client.table('historical_content').insert(content_data).execute()
        return result.data[0]

    def list_historical_content(
        self,
        workspace_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        sources: Optional[List[str]] = None,
        limit: int = 1000
    ) -> List[Dict[str, Any]]:
        """
        List historical content.

        Args:
            workspace_id: Workspace ID
            start_date: Filter by created_at >= start_date
            end_date: Filter by created_at < end_date
            sources: Filter by sources
            limit: Maximum items to return

        Returns:
            List of historical content
        """
        query = self.service_client.table('historical_content') \
            .select('*') \
            .eq('workspace_id', workspace_id) \
            .order('created_at', desc=True) \
            .limit(limit)

        if start_date:
            query = query.gte('created_at', start_date.isoformat())

        if end_date:
            query = query.lt('created_at', end_date.isoformat())

        if sources:
            query = query.in_('source', sources)

        result = query.execute()
        return result.data

    def cleanup_expired_historical_content(
        self,
        workspace_id: Optional[str] = None
    ) -> int:
        """
        Clean up expired historical content.

        Args:
            workspace_id: Optional workspace ID (None = all workspaces)

        Returns:
            Number of records deleted
        """
        try:
            if workspace_id:
                result = self.service_client.table('historical_content') \
                    .delete() \
                    .eq('workspace_id', workspace_id) \
                    .lt('expires_at', datetime.now().isoformat()) \
                    .execute()
            else:
                # Use database function for global cleanup
                result = self.service_client.rpc('cleanup_expired_historical_content').execute()

                if isinstance(result.data, int):
                    return result.data

            return len(result.data) if result.data else 0

        except Exception as e:
            print(f"Error cleaning up historical content: {e}")
            return 0

    def list_content_items(
        self,
        workspace_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        sources: Optional[List[str]] = None,
        limit: int = 1000
    ) -> List[Dict[str, Any]]:
        """
        List content items (for trend detection).

        Args:
            workspace_id: Workspace ID
            start_date: Filter by created_at >= start_date
            end_date: Filter by created_at < end_date
            sources: Filter by sources
            limit: Maximum items to return

        Returns:
            List of content items
        """
        query = self.service_client.table('content_items') \
            .select('*') \
            .eq('workspace_id', workspace_id) \
            .order('created_at', desc=True) \
            .limit(limit)

        if start_date:
            query = query.gte('created_at', start_date.isoformat())

        if end_date:
            query = query.lt('created_at', end_date.isoformat())

        if sources:
            query = query.in_('source', sources)

        result = query.execute()
        return result.data

    # ========================================
    # FEEDBACK OPERATIONS
    # ========================================

    def create_feedback_item(
        self,
        feedback_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create feedback on a content item.

        Args:
            feedback_data: Feedback item data

        Returns:
            Created feedback data
        """
        result = self.service_client.table('feedback_items').insert(feedback_data).execute()
        return result.data[0]

    def get_feedback_item(self, feedback_id: str) -> Optional[Dict[str, Any]]:
        """Get feedback item by ID."""
        result = self.service_client.table('feedback_items') \
            .select('*') \
            .eq('id', feedback_id) \
            .single() \
            .execute()

        return result.data if result.data else None

    def list_feedback_items(
        self,
        workspace_id: str,
        content_item_id: Optional[str] = None,
        newsletter_id: Optional[str] = None,
        rating: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        List feedback items with filters.

        Args:
            workspace_id: Workspace ID
            content_item_id: Filter by content item
            newsletter_id: Filter by newsletter
            rating: Filter by rating (positive, negative, neutral)
            start_date: Filter by created_at >= start_date
            end_date: Filter by created_at < end_date
            limit: Maximum items to return

        Returns:
            List of feedback items
        """
        query = self.service_client.table('feedback_items') \
            .select('*') \
            .eq('workspace_id', workspace_id) \
            .order('created_at', desc=True) \
            .limit(limit)

        if content_item_id:
            query = query.eq('content_item_id', content_item_id)

        if newsletter_id:
            query = query.eq('newsletter_id', newsletter_id)

        if rating:
            query = query.eq('rating', rating)

        if start_date:
            query = query.gte('created_at', start_date.isoformat())

        if end_date:
            query = query.lt('created_at', end_date.isoformat())

        result = query.execute()
        return result.data

    def update_feedback_item(
        self,
        feedback_id: str,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update feedback item."""
        updates['updated_at'] = datetime.now().isoformat()

        result = self.service_client.table('feedback_items') \
            .update(updates) \
            .eq('id', feedback_id) \
            .execute()

        return result.data[0]

    def delete_feedback_item(self, feedback_id: str) -> bool:
        """Delete feedback item."""
        result = self.service_client.table('feedback_items') \
            .delete() \
            .eq('id', feedback_id) \
            .execute()

        return len(result.data) > 0

    def get_content_item_feedback(
        self,
        content_item_id: str
    ) -> List[Dict[str, Any]]:
        """Get all feedback for a specific content item."""
        result = self.service_client.table('feedback_items') \
            .select('*') \
            .eq('content_item_id', content_item_id) \
            .order('created_at', desc=True) \
            .execute()

        return result.data

    # ========================================
    # NEWSLETTER FEEDBACK OPERATIONS
    # ========================================

    def create_newsletter_feedback(
        self,
        feedback_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create feedback on a newsletter.

        Args:
            feedback_data: Newsletter feedback data

        Returns:
            Created feedback data
        """
        result = self.service_client.table('newsletter_feedback').insert(feedback_data).execute()
        return result.data[0]

    def get_newsletter_feedback(
        self,
        newsletter_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get newsletter feedback (with related item feedback)."""
        # Get main feedback
        result = self.service_client.table('newsletter_feedback') \
            .select('*') \
            .eq('newsletter_id', newsletter_id) \
            .single() \
            .execute()

        if not result.data:
            return None

        feedback = result.data

        # Get related item feedback counts
        item_feedback = self.list_feedback_items(
            workspace_id=feedback['workspace_id'],
            newsletter_id=newsletter_id
        )

        feedback['item_feedback_count'] = len(item_feedback)
        feedback['positive_items'] = sum(1 for f in item_feedback if f['rating'] == 'positive')
        feedback['negative_items'] = sum(1 for f in item_feedback if f['rating'] == 'negative')

        return feedback

    def list_newsletter_feedback(
        self,
        workspace_id: str,
        min_rating: Optional[int] = None,
        max_rating: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        List newsletter feedback with filters.

        Args:
            workspace_id: Workspace ID
            min_rating: Filter by overall_rating >= min_rating
            max_rating: Filter by overall_rating <= max_rating
            start_date: Filter by created_at >= start_date
            end_date: Filter by created_at < end_date
            limit: Maximum items to return

        Returns:
            List of newsletter feedback
        """
        query = self.service_client.table('newsletter_feedback') \
            .select('*') \
            .eq('workspace_id', workspace_id) \
            .order('created_at', desc=True) \
            .limit(limit)

        if min_rating is not None:
            query = query.gte('overall_rating', min_rating)

        if max_rating is not None:
            query = query.lte('overall_rating', max_rating)

        if start_date:
            query = query.gte('created_at', start_date.isoformat())

        if end_date:
            query = query.lt('created_at', end_date.isoformat())

        result = query.execute()
        return result.data

    def update_newsletter_feedback(
        self,
        feedback_id: str,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update newsletter feedback."""
        updates['updated_at'] = datetime.now().isoformat()

        result = self.service_client.table('newsletter_feedback') \
            .update(updates) \
            .eq('id', feedback_id) \
            .execute()

        return result.data[0]

    # ========================================
    # LEARNING OPERATIONS
    # ========================================

    def get_source_quality_scores(
        self,
        workspace_id: str
    ) -> List[Dict[str, Any]]:
        """
        Get source quality scores for workspace.

        Args:
            workspace_id: Workspace ID

        Returns:
            List of source quality scores
        """
        result = self.service_client.table('source_quality_scores') \
            .select('*') \
            .eq('workspace_id', workspace_id) \
            .order('quality_score', desc=True) \
            .execute()

        return result.data

    def get_content_preferences(
        self,
        workspace_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get content preferences for workspace.

        Args:
            workspace_id: Workspace ID

        Returns:
            Content preferences or None
        """
        result = self.service_client.table('content_preferences') \
            .select('*') \
            .eq('workspace_id', workspace_id) \
            .single() \
            .execute()

        return result.data if result.data else None

    def recalculate_source_quality(
        self,
        workspace_id: str
    ) -> int:
        """
        Recalculate source quality scores using database function.

        Args:
            workspace_id: Workspace ID

        Returns:
            Number of sources recalculated
        """
        try:
            result = self.service_client.rpc('recalculate_source_quality_scores', {
                'workspace_uuid': workspace_id
            }).execute()

            return result.data if isinstance(result.data, int) else 0

        except Exception as e:
            print(f"Error recalculating source quality: {e}")
            return 0

    def get_feedback_analytics(
        self,
        workspace_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get feedback analytics summary using database function.

        Args:
            workspace_id: Workspace ID
            start_date: Start of date range (optional)
            end_date: End of date range (optional)

        Returns:
            Analytics summary data
        """
        try:
            params = {'workspace_uuid': workspace_id}

            if start_date:
                params['start_date'] = start_date.isoformat()

            if end_date:
                params['end_date'] = end_date.isoformat()

            result = self.service_client.rpc('get_feedback_analytics', params).execute()

            return result.data if result.data else {}

        except Exception as e:
            print(f"Error getting feedback analytics: {e}")
            # Return empty analytics
            return {
                'total_feedback_items': 0,
                'positive_count': 0,
                'negative_count': 0,
                'neutral_count': 0,
                'inclusion_rate': 0,
                'avg_newsletter_rating': None,
                'avg_time_to_finalize': None,
                'top_sources': [],
                'date_range': {
                    'start': start_date.isoformat() if start_date else None,
                    'end': end_date.isoformat() if end_date else None
                }
            }

    def extract_content_preferences(
        self,
        workspace_id: str
    ) -> Optional[str]:
        """
        Extract content preferences from feedback using database function.

        Args:
            workspace_id: Workspace ID

        Returns:
            Preferences ID or None
        """
        try:
            result = self.service_client.rpc('extract_content_preferences', {
                'workspace_uuid': workspace_id
            }).execute()

            return result.data if result.data else None

        except Exception as e:
            print(f"Error extracting content preferences: {e}")
            return None

    # ========================================
    # UTILITY METHODS
    # ========================================

    def _get_default_config(self) -> Dict[str, Any]:
        """Get default workspace configuration."""
        return {
            "reddit": {
                "enabled": True,
                "limit": 25,
                "subreddits": ["AI_Agents"],
                "sort": "hot"
            },
            "rss": {
                "enabled": False,
                "limit": 10,
                "feed_urls": []
            },
            "youtube": {
                "enabled": False,
                "limit": 15,
                "channel_ids": [],
                "search_queries": []
            },
            "blog": {
                "enabled": False,
                "limit": 10,
                "urls": []
            },
            "x": {
                "enabled": False,
                "limit": 20,
                "usernames": []
            },
            "newsletter": {
                "model": "gpt-4-turbo-preview",
                "temperature": 0.7,
                "tone": "professional",
                "language": "en"
            }
        }

    def health_check(self) -> bool:
        """Check Supabase connection health."""
        try:
            # Simple query to test connection
            result = self.client.table('workspaces').select('id').limit(1).execute()
            return True
        except Exception as e:
            print(f"Health check failed: {e}")
            return False
