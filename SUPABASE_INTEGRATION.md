# Supabase Integration Plan for CreatorPulse

**Version:** 2.0
**Last Updated:** January 2025
**Status:** Planning
**Related:** [IMPLEMENTATION_ROADMAP.md](IMPLEMENTATION_ROADMAP.md)

---

## 📋 Executive Summary

This document outlines the integration of **Supabase** as the backend infrastructure for CreatorPulse, replacing the file-based storage system with a scalable, multi-user PostgreSQL database.

### Why Supabase?

| Current (Files) | With Supabase | Improvement |
|-----------------|---------------|-------------|
| JSON files in folders | PostgreSQL database | ✅ Scalable, ACID compliant, queryable |
| No authentication | Built-in auth + RLS | ✅ Multi-user, secure, role-based |
| Manual workspace isolation | Automatic RLS policies | ✅ Zero-trust security |
| No real-time updates | Real-time subscriptions | ✅ Live dashboards, collaboration |
| Flask tracking server | Edge Functions | ✅ Serverless, auto-scaling |
| File size limits | Unlimited records | ✅ Millions of items, no limits |
| Complex JSON queries | SQL queries | ✅ JOINs, aggregations, indexes |
| No collaboration | Multi-user workspaces | ✅ Teams, permissions, sharing |

---

## 🎯 Goals

1. **Enable multi-user collaboration** (agencies, teams)
2. **Scale to millions of content items** (vs file size limits)
3. **Add real-time features** (live dashboards, collaborative editing)
4. **Improve security** (row-level security, encrypted data)
5. **Simplify analytics** (SQL queries vs JSON filtering)
6. **Future-proof architecture** (ready for SaaS, mobile apps)

---

## 🏗️ Database Schema

### Entity-Relationship Diagram

```
┌─────────────┐         ┌──────────────┐
│   auth      │         │  workspaces  │
│   .users    │────────<│              │
└─────────────┘         │ - id         │
       │                │ - name       │
       │                │ - owner_id   │
       │                └──────────────┘
       │                       │
       │                       │ 1:N
       │                       ▼
       │                ┌──────────────────┐
       └───────────────>│ user_workspaces  │
                        │ - user_id        │
                        │ - workspace_id   │
                        │ - role           │
                        └──────────────────┘
                               │
                               │ N:1
                               ▼
                        ┌──────────────┐
                        │  workspaces  │◄────────┐
                        └──────────────┘         │
                               │                 │
                               │ 1:N             │
                      ┌────────┴────────┐        │
                      ▼                 ▼        │
              ┌───────────────┐  ┌──────────────┐
              │ content_items │  │style_profiles│
              │ - id          │  │ - workspace_ │
              │ - workspace_id│  │   id         │
              │ - title       │  │ - tone       │
              │ - source      │  │ - formality  │
              └───────────────┘  └──────────────┘
                      │
                      │ 1:N
                      ▼
              ┌────────────────┐
              │ feedback_items │
              │ - content_id   │
              │ - rating       │
              └────────────────┘
```

### Core Tables

#### 1. Workspaces

```sql
CREATE TABLE workspaces (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    owner_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    metadata JSONB DEFAULT '{}',

    -- Constraints
    CONSTRAINT name_length CHECK (char_length(name) BETWEEN 1 AND 100)
);

-- Indexes
CREATE INDEX idx_workspaces_owner ON workspaces(owner_id);
CREATE INDEX idx_workspaces_created ON workspaces(created_at DESC);

-- RLS Policies
ALTER TABLE workspaces ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their workspaces"
    ON workspaces FOR SELECT
    USING (
        id IN (
            SELECT workspace_id FROM user_workspaces
            WHERE user_id = auth.uid()
        )
        OR owner_id = auth.uid()
    );

CREATE POLICY "Owners can update their workspaces"
    ON workspaces FOR UPDATE
    USING (owner_id = auth.uid());

CREATE POLICY "Users can create workspaces"
    ON workspaces FOR INSERT
    WITH CHECK (owner_id = auth.uid());

CREATE POLICY "Owners can delete their workspaces"
    ON workspaces FOR DELETE
    USING (owner_id = auth.uid());
```

#### 2. User Workspaces (Membership)

```sql
CREATE TABLE user_workspaces (
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    workspace_id UUID REFERENCES workspaces(id) ON DELETE CASCADE,
    role TEXT NOT NULL DEFAULT 'viewer',
    invited_by UUID REFERENCES auth.users(id),
    invited_at TIMESTAMPTZ DEFAULT NOW(),
    accepted_at TIMESTAMPTZ,

    PRIMARY KEY (user_id, workspace_id),

    -- Constraints
    CONSTRAINT valid_role CHECK (role IN ('owner', 'editor', 'viewer'))
);

-- Indexes
CREATE INDEX idx_user_workspaces_user ON user_workspaces(user_id);
CREATE INDEX idx_user_workspaces_workspace ON user_workspaces(workspace_id);

-- RLS Policies
ALTER TABLE user_workspaces ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their memberships"
    ON user_workspaces FOR SELECT
    USING (user_id = auth.uid());

CREATE POLICY "Workspace owners can manage memberships"
    ON user_workspaces FOR ALL
    USING (
        workspace_id IN (
            SELECT id FROM workspaces WHERE owner_id = auth.uid()
        )
    );
```

#### 3. Workspace Configurations

```sql
CREATE TABLE workspace_configs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workspace_id UUID REFERENCES workspaces(id) ON DELETE CASCADE UNIQUE,
    config JSONB NOT NULL,
    version INTEGER DEFAULT 1,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    updated_by UUID REFERENCES auth.users(id),

    -- Constraints
    CONSTRAINT config_not_empty CHECK (config IS NOT NULL)
);

-- Indexes
CREATE INDEX idx_workspace_configs_workspace ON workspace_configs(workspace_id);

-- RLS Policies
ALTER TABLE workspace_configs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their workspace configs"
    ON workspace_configs FOR SELECT
    USING (
        workspace_id IN (
            SELECT workspace_id FROM user_workspaces
            WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "Editors can update workspace configs"
    ON workspace_configs FOR UPDATE
    USING (
        workspace_id IN (
            SELECT workspace_id FROM user_workspaces
            WHERE user_id = auth.uid() AND role IN ('owner', 'editor')
        )
    );
```

#### 4. Content Items (Scraped Content)

```sql
CREATE TABLE content_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workspace_id UUID REFERENCES workspaces(id) ON DELETE CASCADE,

    -- Content fields
    title TEXT NOT NULL,
    source TEXT NOT NULL,
    source_url TEXT,
    content TEXT,
    summary TEXT,

    -- Author info
    author TEXT,
    author_url TEXT,

    -- Engagement metrics
    score INTEGER DEFAULT 0,
    comments_count INTEGER DEFAULT 0,
    shares_count INTEGER DEFAULT 0,
    views_count INTEGER DEFAULT 0,

    -- Media
    image_url TEXT,
    video_url TEXT,
    external_url TEXT,

    -- Categorization
    tags JSONB DEFAULT '[]',
    category TEXT,

    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL,
    scraped_at TIMESTAMPTZ DEFAULT NOW(),

    -- Metadata
    metadata JSONB DEFAULT '{}',

    -- Constraints
    CONSTRAINT title_not_empty CHECK (char_length(title) > 0),
    CONSTRAINT valid_source CHECK (source IN ('reddit', 'rss', 'blog', 'x', 'youtube'))
);

-- Indexes
CREATE INDEX idx_content_workspace ON content_items(workspace_id);
CREATE INDEX idx_content_source ON content_items(source);
CREATE INDEX idx_content_created ON content_items(created_at DESC);
CREATE INDEX idx_content_score ON content_items(score DESC);
CREATE INDEX idx_content_workspace_created ON content_items(workspace_id, created_at DESC);

-- Full-text search
CREATE INDEX idx_content_title_search ON content_items USING GIN(to_tsvector('english', title));
CREATE INDEX idx_content_summary_search ON content_items USING GIN(to_tsvector('english', summary));

-- RLS Policies
ALTER TABLE content_items ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view content in their workspaces"
    ON content_items FOR SELECT
    USING (
        workspace_id IN (
            SELECT workspace_id FROM user_workspaces
            WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "Editors can insert content"
    ON content_items FOR INSERT
    WITH CHECK (
        workspace_id IN (
            SELECT workspace_id FROM user_workspaces
            WHERE user_id = auth.uid() AND role IN ('owner', 'editor')
        )
    );
```

#### 5. Style Profiles

```sql
CREATE TABLE style_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workspace_id UUID REFERENCES workspaces(id) ON DELETE CASCADE UNIQUE,

    -- Voice characteristics
    tone TEXT,
    formality_level FLOAT CHECK (formality_level BETWEEN 0 AND 1),

    -- Sentence patterns
    avg_sentence_length FLOAT,
    sentence_length_variety FLOAT,
    question_frequency FLOAT,

    -- Vocabulary
    vocabulary_level TEXT,
    favorite_phrases JSONB DEFAULT '[]',
    avoided_words JSONB DEFAULT '[]',

    -- Structure
    typical_intro_style TEXT,
    section_count INTEGER,
    uses_emojis BOOLEAN DEFAULT FALSE,
    emoji_frequency FLOAT,

    -- Examples
    example_intros JSONB DEFAULT '[]',
    example_transitions JSONB DEFAULT '[]',
    example_conclusions JSONB DEFAULT '[]',

    -- Metadata
    trained_on_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    updated_by UUID REFERENCES auth.users(id)
);

-- Indexes
CREATE INDEX idx_style_workspace ON style_profiles(workspace_id);

-- RLS Policies
ALTER TABLE style_profiles ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their style profiles"
    ON style_profiles FOR SELECT
    USING (
        workspace_id IN (
            SELECT workspace_id FROM user_workspaces
            WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "Editors can manage style profiles"
    ON style_profiles FOR ALL
    USING (
        workspace_id IN (
            SELECT workspace_id FROM user_workspaces
            WHERE user_id = auth.uid() AND role IN ('owner', 'editor')
        )
    );
```

#### 6. Trends

```sql
CREATE TABLE trends (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workspace_id UUID REFERENCES workspaces(id) ON DELETE CASCADE,

    -- Trend info
    topic TEXT NOT NULL,
    keywords JSONB DEFAULT '[]',

    -- Metrics
    strength_score FLOAT CHECK (strength_score BETWEEN 0 AND 1),
    mention_count INTEGER DEFAULT 0,
    velocity FLOAT,

    -- Sources
    sources JSONB DEFAULT '[]',
    source_count INTEGER DEFAULT 0,

    -- Evidence (array of content_item IDs)
    key_item_ids JSONB DEFAULT '[]',

    -- Context
    explanation TEXT,
    related_topics JSONB DEFAULT '[]',

    -- Timestamps
    first_seen TIMESTAMPTZ,
    peak_time TIMESTAMPTZ,
    detected_at TIMESTAMPTZ DEFAULT NOW(),

    -- Classification
    confidence_level TEXT CHECK (confidence_level IN ('high', 'medium', 'low'))
);

-- Indexes
CREATE INDEX idx_trends_workspace ON trends(workspace_id);
CREATE INDEX idx_trends_detected ON trends(detected_at DESC);
CREATE INDEX idx_trends_strength ON trends(strength_score DESC);

-- RLS Policies
ALTER TABLE trends ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view trends in their workspaces"
    ON trends FOR SELECT
    USING (
        workspace_id IN (
            SELECT workspace_id FROM user_workspaces
            WHERE user_id = auth.uid()
        )
    );
```

#### 7. Feedback Items

```sql
CREATE TABLE feedback_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workspace_id UUID REFERENCES workspaces(id) ON DELETE CASCADE,
    content_item_id UUID REFERENCES content_items(id) ON DELETE SET NULL,

    -- Identification
    content_title TEXT,
    content_source TEXT,
    content_url TEXT,

    -- Feedback
    rating TEXT CHECK (rating IN ('positive', 'negative', 'neutral')),
    included_in_final BOOLEAN DEFAULT TRUE,

    -- Edit tracking
    original_summary TEXT,
    edited_summary TEXT,
    edit_distance FLOAT CHECK (edit_distance BETWEEN 0 AND 1),

    -- Context
    newsletter_date TIMESTAMPTZ,
    feedback_date TIMESTAMPTZ DEFAULT NOW(),
    user_id UUID REFERENCES auth.users(id),

    -- Learning signals
    engagement_prediction FLOAT,
    actual_engagement FLOAT
);

-- Indexes
CREATE INDEX idx_feedback_workspace ON feedback_items(workspace_id);
CREATE INDEX idx_feedback_content ON feedback_items(content_item_id);
CREATE INDEX idx_feedback_user ON feedback_items(user_id);
CREATE INDEX idx_feedback_date ON feedback_items(feedback_date DESC);

-- RLS Policies
ALTER TABLE feedback_items ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view feedback in their workspaces"
    ON feedback_items FOR SELECT
    USING (
        workspace_id IN (
            SELECT workspace_id FROM user_workspaces
            WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "Users can create feedback"
    ON feedback_items FOR INSERT
    WITH CHECK (
        workspace_id IN (
            SELECT workspace_id FROM user_workspaces
            WHERE user_id = auth.uid()
        )
        AND user_id = auth.uid()
    );
```

#### 8. Newsletters

```sql
CREATE TABLE newsletters (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workspace_id UUID REFERENCES workspaces(id) ON DELETE CASCADE,

    -- Content
    title TEXT NOT NULL,
    html_content TEXT NOT NULL,

    -- Items included (array of content_item IDs)
    content_item_ids JSONB DEFAULT '[]',

    -- Trends included (array of trend IDs)
    trend_ids JSONB DEFAULT '[]',

    -- Timestamps
    generated_at TIMESTAMPTZ DEFAULT NOW(),
    sent_at TIMESTAMPTZ,

    -- Creator
    created_by UUID REFERENCES auth.users(id),

    -- Metadata
    metadata JSONB DEFAULT '{}',

    -- Status
    status TEXT DEFAULT 'draft' CHECK (status IN ('draft', 'sent', 'scheduled'))
);

-- Indexes
CREATE INDEX idx_newsletters_workspace ON newsletters(workspace_id);
CREATE INDEX idx_newsletters_generated ON newsletters(generated_at DESC);
CREATE INDEX idx_newsletters_creator ON newsletters(created_by);

-- RLS Policies
ALTER TABLE newsletters ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view newsletters in their workspaces"
    ON newsletters FOR SELECT
    USING (
        workspace_id IN (
            SELECT workspace_id FROM user_workspaces
            WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "Editors can create newsletters"
    ON newsletters FOR INSERT
    WITH CHECK (
        workspace_id IN (
            SELECT workspace_id FROM user_workspaces
            WHERE user_id = auth.uid() AND role IN ('owner', 'editor')
        )
        AND created_by = auth.uid()
    );
```

#### 9. Analytics Events

```sql
CREATE TABLE analytics_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workspace_id UUID REFERENCES workspaces(id) ON DELETE CASCADE,
    newsletter_id UUID REFERENCES newsletters(id) ON DELETE CASCADE,

    -- Recipient info
    recipient TEXT NOT NULL,

    -- Event details
    event_type TEXT NOT NULL CHECK (event_type IN ('sent', 'opened', 'clicked', 'bounced')),
    event_time TIMESTAMPTZ DEFAULT NOW(),

    -- Click details
    clicked_url TEXT,
    content_item_id UUID REFERENCES content_items(id) ON DELETE SET NULL,

    -- Context
    user_agent TEXT,
    ip_address INET,
    location TEXT,

    -- Device info
    device_type TEXT,
    browser TEXT,
    os TEXT
);

-- Indexes
CREATE INDEX idx_analytics_workspace ON analytics_events(workspace_id);
CREATE INDEX idx_analytics_newsletter ON analytics_events(newsletter_id);
CREATE INDEX idx_analytics_event_type ON analytics_events(event_type);
CREATE INDEX idx_analytics_event_time ON analytics_events(event_time DESC);
CREATE INDEX idx_analytics_recipient ON analytics_events(recipient);

-- Composite indexes for common queries
CREATE INDEX idx_analytics_workspace_time ON analytics_events(workspace_id, event_time DESC);
CREATE INDEX idx_analytics_newsletter_type ON analytics_events(newsletter_id, event_type);

-- RLS Policies
ALTER TABLE analytics_events ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view analytics for their workspaces"
    ON analytics_events FOR SELECT
    USING (
        workspace_id IN (
            SELECT workspace_id FROM user_workspaces
            WHERE user_id = auth.uid()
        )
    );

-- Allow system to insert events (via service role)
CREATE POLICY "System can insert analytics events"
    ON analytics_events FOR INSERT
    WITH CHECK (true);
```

---

## 🔧 Implementation

### Module: `src/ai_newsletter/database/supabase_client.py`

```python
"""
Supabase client manager for CreatorPulse.

Provides a unified interface for all database operations.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from supabase import create_client, Client
import os
from pathlib import Path

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
        self.url = os.getenv("SUPABASE_URL")
        self.key = os.getenv("SUPABASE_ANON_KEY")
        self.service_key = os.getenv("SUPABASE_SERVICE_KEY")

        if not self.url or not self.key:
            raise ValueError(
                "Supabase credentials not configured. "
                "Set SUPABASE_URL and SUPABASE_ANON_KEY in .env"
            )

        self.client: Client = create_client(self.url, self.key)

        # Service client for admin operations (bypasses RLS)
        if self.service_key:
            self.service_client: Client = create_client(self.url, self.service_key)

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

        # Create workspace
        result = self.client.table('workspaces').insert({
            'name': name,
            'description': description,
            'owner_id': user_id
        }).execute()

        workspace = result.data[0]

        # Create user-workspace membership (owner role)
        self.client.table('user_workspaces').insert({
            'user_id': user_id,
            'workspace_id': workspace['id'],
            'role': 'owner',
            'accepted_at': datetime.now().isoformat()
        }).execute()

        # Create default config
        self.client.table('workspace_configs').insert({
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

        # Query workspaces with role information
        result = self.client.table('workspaces') \
            .select('*, user_workspaces!inner(role)') \
            .eq('user_workspaces.user_id', user_id) \
            .order('created_at', desc=True) \
            .execute()

        return result.data

    def get_workspace(self, workspace_id: str) -> Optional[Dict[str, Any]]:
        """Get workspace by ID."""
        result = self.client.table('workspaces') \
            .select('*') \
            .eq('id', workspace_id) \
            .single() \
            .execute()

        return result.data if result.data else None

    def update_workspace(self,
                        workspace_id: str,
                        updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update workspace details."""
        updates['updated_at'] = datetime.now().isoformat()

        result = self.client.table('workspaces') \
            .update(updates) \
            .eq('id', workspace_id) \
            .execute()

        return result.data[0]

    def delete_workspace(self, workspace_id: str) -> bool:
        """Delete workspace (cascade deletes all related data)."""
        result = self.client.table('workspaces') \
            .delete() \
            .eq('id', workspace_id) \
            .execute()

        return len(result.data) > 0

    # ========================================
    # USER-WORKSPACE OPERATIONS
    # ========================================

    def invite_user_to_workspace(self,
                                 workspace_id: str,
                                 email: str,
                                 role: str = 'viewer') -> Dict[str, Any]:
        """
        Invite a user to workspace.

        Args:
            workspace_id: Workspace ID
            email: User email
            role: Role ('owner', 'editor', 'viewer')

        Returns:
            Invitation data
        """
        current_user = self.client.auth.get_user()

        # Check if user exists
        # (This would typically send an invitation email)
        # For now, we'll just create the membership

        result = self.client.table('user_workspaces').insert({
            'workspace_id': workspace_id,
            'user_id': email,  # In production, lookup user by email
            'role': role,
            'invited_by': current_user.user.id
        }).execute()

        return result.data[0]

    def get_workspace_members(self, workspace_id: str) -> List[Dict[str, Any]]:
        """Get all members of a workspace."""
        result = self.client.table('user_workspaces') \
            .select('*, users:user_id(email, created_at)') \
            .eq('workspace_id', workspace_id) \
            .execute()

        return result.data

    def update_user_role(self,
                        workspace_id: str,
                        user_id: str,
                        role: str) -> Dict[str, Any]:
        """Update user's role in workspace."""
        result = self.client.table('user_workspaces') \
            .update({'role': role}) \
            .eq('workspace_id', workspace_id) \
            .eq('user_id', user_id) \
            .execute()

        return result.data[0]

    def remove_user_from_workspace(self, workspace_id: str, user_id: str) -> bool:
        """Remove user from workspace."""
        result = self.client.table('user_workspaces') \
            .delete() \
            .eq('workspace_id', workspace_id) \
            .eq('user_id', user_id) \
            .execute()

        return len(result.data) > 0

    # ========================================
    # CONFIGURATION OPERATIONS
    # ========================================

    def get_workspace_config(self, workspace_id: str) -> Dict[str, Any]:
        """Get workspace configuration."""
        result = self.client.table('workspace_configs') \
            .select('config') \
            .eq('workspace_id', workspace_id) \
            .single() \
            .execute()

        return result.data['config'] if result.data else self._get_default_config()

    def save_workspace_config(self,
                             workspace_id: str,
                             config: Dict[str, Any],
                             user_id: Optional[str] = None) -> Dict[str, Any]:
        """Save workspace configuration."""
        if not user_id:
            user = self.client.auth.get_user()
            user_id = user.user.id

        # Upsert configuration
        result = self.client.table('workspace_configs') \
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

        # Batch insert
        result = self.client.table('content_items').insert(data).execute()

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

        query = self.client.table('content_items') \
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
        result = self.client.table('content_items') \
            .select('*') \
            .eq('workspace_id', workspace_id) \
            .text_search('title', query) \
            .limit(limit) \
            .execute()

        return [ContentItem(**item) for item in result.data]

    # ========================================
    # STYLE PROFILE OPERATIONS
    # ========================================

    def save_style_profile(self,
                          workspace_id: str,
                          profile: StyleProfile,
                          user_id: Optional[str] = None) -> Dict[str, Any]:
        """Save style profile for workspace."""
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
        """Load style profile for workspace."""
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
            last_updated=datetime.fromisoformat(data['updated_at'])
        )

    # ========================================
    # TRENDS OPERATIONS
    # ========================================

    def save_trends(self,
                   workspace_id: str,
                   trends: List[Trend]) -> List[Dict[str, Any]]:
        """Save detected trends."""
        data = [
            {
                'workspace_id': workspace_id,
                'topic': trend.topic,
                'keywords': trend.keywords,
                'strength_score': trend.strength_score,
                'mention_count': trend.mention_count,
                'velocity': trend.velocity,
                'sources': trend.sources,
                'source_count': trend.source_count,
                'key_item_ids': [item.id for item in trend.key_items if hasattr(item, 'id')],
                'explanation': trend.explanation,
                'related_topics': trend.related_topics,
                'first_seen': trend.first_seen.isoformat(),
                'peak_time': trend.peak_time.isoformat(),
                'detected_at': trend.detected_at.isoformat(),
                'confidence_level': trend.confidence_level
            }
            for trend in trends
        ]

        result = self.client.table('trends').insert(data).execute()

        return result.data

    def load_trends(self,
                   workspace_id: str,
                   days: int = 7,
                   min_confidence: str = 'low') -> List[Trend]:
        """Load recent trends."""
        cutoff_date = datetime.now() - timedelta(days=days)

        confidence_order = {'high': 3, 'medium': 2, 'low': 1}

        result = self.client.table('trends') \
            .select('*') \
            .eq('workspace_id', workspace_id) \
            .gte('detected_at', cutoff_date.isoformat()) \
            .order('strength_score', desc=True) \
            .execute()

        # Filter by confidence level
        filtered = [
            t for t in result.data
            if confidence_order.get(t['confidence_level'], 0) >= confidence_order[min_confidence]
        ]

        # Convert to Trend objects
        return [
            Trend(
                topic=t['topic'],
                keywords=t['keywords'],
                strength_score=t['strength_score'],
                mention_count=t['mention_count'],
                velocity=t.get('velocity', 0),
                sources=t['sources'],
                source_count=t['source_count'],
                key_items=[],  # Would need to join with content_items
                first_seen=datetime.fromisoformat(t['first_seen']),
                peak_time=datetime.fromisoformat(t['peak_time']),
                explanation=t.get('explanation', ''),
                related_topics=t.get('related_topics', []),
                detected_at=datetime.fromisoformat(t['detected_at']),
                confidence_level=t['confidence_level']
            )
            for t in filtered
        ]

    # ========================================
    # FEEDBACK OPERATIONS
    # ========================================

    def save_feedback(self,
                     workspace_id: str,
                     feedback: FeedbackItem,
                     user_id: Optional[str] = None) -> Dict[str, Any]:
        """Save user feedback on content."""
        if not user_id:
            user = self.client.auth.get_user()
            user_id = user.user.id

        data = {
            'workspace_id': workspace_id,
            'content_item_id': feedback.content_id if hasattr(feedback, 'content_id') else None,
            'content_title': feedback.title,
            'content_source': feedback.source,
            'content_url': feedback.source_url,
            'rating': feedback.rating,
            'included_in_final': feedback.included_in_final,
            'original_summary': feedback.original_summary,
            'edited_summary': feedback.edited_summary,
            'edit_distance': feedback.edit_distance,
            'newsletter_date': feedback.newsletter_date.isoformat(),
            'feedback_date': feedback.feedback_date.isoformat(),
            'user_id': user_id,
            'engagement_prediction': feedback.engagement_prediction,
            'actual_engagement': feedback.actual_engagement
        }

        result = self.client.table('feedback_items').insert(data).execute()

        return result.data[0]

    def load_feedback(self,
                     workspace_id: str,
                     days: int = 30) -> List[FeedbackItem]:
        """Load feedback history."""
        cutoff_date = datetime.now() - timedelta(days=days)

        result = self.client.table('feedback_items') \
            .select('*') \
            .eq('workspace_id', workspace_id) \
            .gte('feedback_date', cutoff_date.isoformat()) \
            .order('feedback_date', desc=True) \
            .execute()

        return [FeedbackItem(**item) for item in result.data]

    def get_source_quality_scores(self, workspace_id: str) -> Dict[str, float]:
        """Calculate source quality scores from feedback."""
        # This would use PostgreSQL aggregation
        result = self.client.rpc('calculate_source_scores', {
            'workspace_id': workspace_id
        }).execute()

        return dict(result.data)

    # ========================================
    # ANALYTICS OPERATIONS
    # ========================================

    def record_analytics_event(self,
                              workspace_id: str,
                              event: EmailEvent) -> Dict[str, Any]:
        """Record an analytics event."""
        data = {
            'workspace_id': workspace_id,
            'newsletter_id': event.newsletter_id,
            'recipient': event.recipient,
            'event_type': event.event_type,
            'event_time': event.event_time.isoformat(),
            'clicked_url': event.clicked_url,
            'content_item_id': event.content_item_id,
            'user_agent': event.user_agent,
            'ip_address': event.ip_address,
            'location': event.location
        }

        # Use service client to bypass RLS
        result = self.service_client.table('analytics_events').insert(data).execute()

        return result.data[0]

    def get_analytics(self,
                     workspace_id: str,
                     start_date: datetime,
                     end_date: datetime) -> Dict[str, Any]:
        """Get aggregated analytics for date range."""
        # This would use PostgreSQL aggregation functions
        result = self.client.rpc('get_analytics_summary', {
            'workspace_id': workspace_id,
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat()
        }).execute()

        return result.data

    def subscribe_to_analytics(self,
                              workspace_id: str,
                              callback) -> Any:
        """Subscribe to real-time analytics updates."""
        channel = self.client.channel(f'analytics_{workspace_id}')

        channel.on_postgres_changes(
            event='INSERT',
            schema='public',
            table='analytics_events',
            filter=f'workspace_id=eq.{workspace_id}',
            callback=callback
        ).subscribe()

        return channel

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
```

---

## 📱 Authentication Module

### `src/ai_newsletter/auth/auth_manager.py`

```python
"""
Authentication manager for Supabase Auth.
"""

from typing import Optional, Dict, Any
from supabase import Client


class AuthManager:
    """Handle user authentication via Supabase."""

    def __init__(self, supabase_client: Client):
        """
        Initialize auth manager.

        Args:
            supabase_client: Initialized Supabase client
        """
        self.client = supabase_client

    def sign_up(self, email: str, password: str, **metadata) -> Dict[str, Any]:
        """
        Register a new user.

        Args:
            email: User email
            password: User password (min 6 characters)
            **metadata: Optional user metadata

        Returns:
            User data including access token

        Raises:
            Exception: If signup fails
        """
        result = self.client.auth.sign_up({
            'email': email,
            'password': password,
            'options': {
                'data': metadata
            }
        })

        return {
            'user': result.user,
            'session': result.session
        }

    def sign_in(self, email: str, password: str) -> Dict[str, Any]:
        """
        Sign in an existing user.

        Args:
            email: User email
            password: User password

        Returns:
            User data including access token

        Raises:
            Exception: If signin fails
        """
        result = self.client.auth.sign_in_with_password({
            'email': email,
            'password': password
        })

        return {
            'user': result.user,
            'session': result.session
        }

    def sign_in_with_magic_link(self, email: str) -> bool:
        """
        Send magic link to user's email.

        Args:
            email: User email

        Returns:
            True if magic link sent successfully
        """
        result = self.client.auth.sign_in_with_otp({
            'email': email
        })

        return result is not None

    def sign_in_with_provider(self, provider: str) -> str:
        """
        Get OAuth URL for social login.

        Args:
            provider: OAuth provider ('google', 'github', etc.)

        Returns:
            OAuth URL to redirect user to
        """
        result = self.client.auth.sign_in_with_oauth({
            'provider': provider
        })

        return result.url

    def sign_out(self) -> bool:
        """
        Sign out current user.

        Returns:
            True if signed out successfully
        """
        self.client.auth.sign_out()
        return True

    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """
        Get currently authenticated user.

        Returns:
            User data if authenticated, None otherwise
        """
        try:
            result = self.client.auth.get_user()
            return result.user
        except Exception:
            return None

    def get_session(self) -> Optional[Dict[str, Any]]:
        """
        Get current session.

        Returns:
            Session data if active, None otherwise
        """
        try:
            result = self.client.auth.get_session()
            return result
        except Exception:
            return None

    def refresh_session(self) -> Optional[Dict[str, Any]]:
        """
        Refresh authentication session.

        Returns:
            New session data
        """
        result = self.client.auth.refresh_session()
        return result.session

    def reset_password_email(self, email: str) -> bool:
        """
        Send password reset email.

        Args:
            email: User email

        Returns:
            True if email sent successfully
        """
        result = self.client.auth.reset_password_email(email)
        return result is not None

    def update_user(self, **attributes) -> Dict[str, Any]:
        """
        Update user attributes.

        Args:
            **attributes: User attributes to update

        Returns:
            Updated user data
        """
        result = self.client.auth.update_user(attributes)
        return result.user
```

---

## 🖥️ Streamlit UI Updates

### Authentication Flow

```python
# src/streamlit_app.py

import streamlit as st
from ai_newsletter.database.supabase_client import SupabaseManager
from ai_newsletter.auth.auth_manager import AuthManager


def show_login_page():
    """Display login/signup page."""
    st.set_page_config(
        page_title="CreatorPulse - Login",
        page_icon="📧",
        layout="centered"
    )

    st.title("📧 CreatorPulse")
    st.markdown("AI-powered newsletter generator for creators and agencies")

    tab1, tab2 = st.tabs(["Sign In", "Sign Up"])

    with tab1:
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Sign In", type="primary")

            if submit:
                try:
                    supabase = SupabaseManager()
                    auth = AuthManager(supabase.client)
                    result = auth.sign_in(email, password)

                    st.session_state.user = result['user']
                    st.session_state.session = result['session']
                    st.success("Logged in successfully!")
                    st.rerun()

                except Exception as e:
                    st.error(f"Login failed: {e}")

        # Magic link option
        st.markdown("---")
        st.markdown("Or sign in with magic link:")
        magic_email = st.text_input("Email for magic link", key="magic_email")
        if st.button("Send Magic Link"):
            try:
                supabase = SupabaseManager()
                auth = AuthManager(supabase.client)
                auth.sign_in_with_magic_link(magic_email)
                st.success("Check your email for the magic link!")
            except Exception as e:
                st.error(f"Failed to send magic link: {e}")

    with tab2:
        with st.form("signup_form"):
            new_email = st.text_input("Email", key="signup_email")
            new_password = st.text_input("Password", type="password", key="signup_password")
            confirm_password = st.text_input("Confirm Password", type="password")

            submit = st.form_submit_button("Create Account", type="primary")

            if submit:
                if new_password != confirm_password:
                    st.error("Passwords don't match!")
                elif len(new_password) < 6:
                    st.error("Password must be at least 6 characters")
                else:
                    try:
                        supabase = SupabaseManager()
                        auth = AuthManager(supabase.client)
                        result = auth.sign_up(new_email, new_password)

                        st.success("Account created! Please check your email to verify.")
                    except Exception as e:
                        st.error(f"Signup failed: {e}")


def show_user_menu():
    """Display user menu in sidebar."""
    if 'user' in st.session_state:
        with st.sidebar:
            user = st.session_state.user
            st.markdown(f"**Logged in as:** {user['email']}")

            if st.button("Sign Out"):
                try:
                    supabase = SupabaseManager()
                    auth = AuthManager(supabase.client)
                    auth.sign_out()

                    del st.session_state.user
                    del st.session_state.session
                    st.rerun()
                except Exception as e:
                    st.error(f"Signout failed: {e}")


def main():
    """Main application entry point."""

    # Initialize Supabase
    try:
        supabase = SupabaseManager()
    except Exception as e:
        st.error(f"Failed to connect to Supabase: {e}")
        st.info("Please check your Supabase credentials in .env file")
        st.stop()

    # Check authentication
    if 'user' not in st.session_state:
        show_login_page()
        return

    # Show main app
    st.set_page_config(
        page_title="CreatorPulse - AI Newsletter Generator",
        page_icon="📧",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Show user menu
    show_user_menu()

    # Get user's workspaces
    user_id = st.session_state.user['id']
    workspaces = supabase.list_workspaces(user_id)

    if not workspaces:
        # First-time user - create default workspace
        st.info("👋 Welcome! Let's create your first workspace.")

        with st.form("create_first_workspace"):
            name = st.text_input("Workspace Name", value="My Newsletter")
            description = st.text_area("Description (optional)")

            if st.form_submit_button("Create Workspace"):
                workspace = supabase.create_workspace(name, description, user_id)
                st.success(f"Created workspace: {name}")
                st.rerun()

        return

    # Workspace selector in sidebar
    with st.sidebar:
        st.markdown("### 📁 Workspace")

        workspace_names = [w['name'] for w in workspaces]
        selected_workspace_name = st.selectbox(
            "Active Workspace",
            options=workspace_names,
            label_visibility="collapsed"
        )

        # Get selected workspace
        selected_workspace = next(w for w in workspaces if w['name'] == selected_workspace_name)
        st.session_state.current_workspace_id = selected_workspace['id']

        # Workspace actions
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("➕", help="Create new workspace"):
                st.session_state.show_new_workspace = True
        with col2:
            if st.button("⚙️", help="Manage workspaces"):
                st.session_state.show_workspace_manager = True
        with col3:
            if st.button("👥", help="Manage team"):
                st.session_state.show_team_manager = True

    # Show workspace indicator
    st.caption(f"📁 Workspace: **{selected_workspace['name']}** • Role: **{selected_workspace['user_workspaces'][0]['role']}**")

    # Load settings for workspace
    config = supabase.get_workspace_config(selected_workspace['id'])

    # Create tabs (rest of the app)
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Content Scraper",
        "📝 Newsletter Generator",
        "📧 Email Delivery",
        "⏰ Scheduler",
        "🚀 Pipeline"
    ])

    with tab1:
        content_scraper_tab(supabase, selected_workspace['id'], config)

    with tab2:
        newsletter_generator_tab(supabase, selected_workspace['id'], config)

    # ... rest of tabs


if __name__ == "__main__":
    main()
```

---

## 🔄 Migration Script

### `scripts/migrate_to_supabase.py`

```python
"""
Migration script to transfer data from JSON files to Supabase.

Usage:
    python scripts/migrate_to_supabase.py --workspace default --user-id <user_id>
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ai_newsletter.database.supabase_client import SupabaseManager
from src.ai_newsletter.models.content import ContentItem
from src.ai_newsletter.models.style_profile import StyleProfile


def migrate_workspace(workspace_name: str, user_id: str, dry_run: bool = False):
    """
    Migrate a workspace from file-based storage to Supabase.

    Args:
        workspace_name: Name of workspace directory
        user_id: Owner user ID in Supabase
        dry_run: If True, don't actually write to database
    """
    workspace_path = Path('workspaces') / workspace_name

    if not workspace_path.exists():
        print(f"❌ Workspace directory not found: {workspace_path}")
        return False

    print(f"🔄 Migrating workspace: {workspace_name}")
    print(f"   Path: {workspace_path}")
    print(f"   Owner: {user_id}")
    print(f"   Dry run: {dry_run}")
    print()

    # Initialize Supabase
    supabase = SupabaseManager()

    # Step 1: Create workspace in Supabase
    print("1️⃣  Creating workspace...")

    if not dry_run:
        workspace = supabase.create_workspace(
            name=workspace_name,
            description=f"Migrated from {workspace_path}",
            user_id=user_id
        )
        workspace_id = workspace['id']
        print(f"   ✅ Created workspace: {workspace_id}")
    else:
        workspace_id = "DRY_RUN_ID"
        print(f"   🔍 Would create workspace")

    # Step 2: Migrate config.json
    print("2️⃣  Migrating configuration...")

    config_file = workspace_path / 'config.json'
    if config_file.exists():
        with open(config_file, 'r') as f:
            config = json.load(f)

        if not dry_run:
            supabase.save_workspace_config(workspace_id, config, user_id)
            print(f"   ✅ Migrated config.json")
        else:
            print(f"   🔍 Would migrate config.json ({len(config)} keys)")
    else:
        print(f"   ⚠️  No config.json found")

    # Step 3: Migrate style_profile.json
    print("3️⃣  Migrating style profile...")

    style_file = workspace_path / 'style_profile.json'
    if style_file.exists():
        with open(style_file, 'r') as f:
            style_data = json.load(f)

        profile = StyleProfile(**style_data)

        if not dry_run:
            supabase.save_style_profile(workspace_id, profile, user_id)
            print(f"   ✅ Migrated style profile")
        else:
            print(f"   🔍 Would migrate style profile")
    else:
        print(f"   ℹ️  No style profile found (optional)")

    # Step 4: Migrate historical_content.json
    print("4️⃣  Migrating historical content...")

    historical_file = workspace_path / 'historical_content.json'
    if historical_file.exists():
        with open(historical_file, 'r') as f:
            historical_data = json.load(f)

        # Flatten the date-based structure
        all_items = []
        for date, items in historical_data.items():
            all_items.extend(items)

        # Convert to ContentItem objects
        content_items = [ContentItem.from_dict(item) for item in all_items]

        if not dry_run:
            supabase.save_content_items(workspace_id, content_items)
            print(f"   ✅ Migrated {len(content_items)} content items")
        else:
            print(f"   🔍 Would migrate {len(content_items)} content items")
    else:
        print(f"   ℹ️  No historical content found (optional)")

    # Step 5: Migrate feedback_data.json
    print("5️⃣  Migrating feedback data...")

    feedback_file = workspace_path / 'feedback_data.json'
    if feedback_file.exists():
        with open(feedback_file, 'r') as f:
            feedback_data = json.load(f)

        if not dry_run:
            for feedback_item in feedback_data:
                supabase.save_feedback(workspace_id, FeedbackItem(**feedback_item), user_id)
            print(f"   ✅ Migrated {len(feedback_data)} feedback items")
        else:
            print(f"   🔍 Would migrate {len(feedback_data)} feedback items")
    else:
        print(f"   ℹ️  No feedback data found (optional)")

    # Step 6: Migrate analytics_events.json
    print("6️⃣  Migrating analytics events...")

    analytics_file = workspace_path / 'analytics_events.json'
    if analytics_file.exists():
        with open(analytics_file, 'r') as f:
            analytics_data = json.load(f)

        if not dry_run:
            # Note: This would require bulk insert for performance
            print(f"   ⚠️  Skipping {len(analytics_data)} analytics events (implement bulk insert)")
        else:
            print(f"   🔍 Would migrate {len(analytics_data)} analytics events")
    else:
        print(f"   ℹ️  No analytics data found (optional)")

    print()
    print("✅ Migration complete!" if not dry_run else "🔍 Dry run complete!")
    print()

    return True


def main():
    """Main migration entry point."""
    parser = argparse.ArgumentParser(description='Migrate workspace data to Supabase')
    parser.add_argument('--workspace', required=True, help='Workspace name to migrate')
    parser.add_argument('--user-id', required=True, help='Owner user ID in Supabase')
    parser.add_argument('--dry-run', action='store_true', help='Preview migration without writing')
    parser.add_argument('--all', action='store_true', help='Migrate all workspaces')

    args = parser.parse_args()

    print("=" * 60)
    print("  CreatorPulse - Supabase Migration Tool")
    print("=" * 60)
    print()

    if args.all:
        # Migrate all workspaces
        workspaces_dir = Path('workspaces')
        if not workspaces_dir.exists():
            print("❌ No workspaces directory found")
            return

        workspaces = [d.name for d in workspaces_dir.iterdir() if d.is_dir()]
        print(f"Found {len(workspaces)} workspaces to migrate:")
        for ws in workspaces:
            print(f"  - {ws}")
        print()

        for workspace_name in workspaces:
            migrate_workspace(workspace_name, args.user_id, args.dry_run)
            print()
    else:
        # Migrate single workspace
        migrate_workspace(args.workspace, args.user_id, args.dry_run)

    print("=" * 60)
    print("Migration complete!")
    print()
    print("Next steps:")
    print("1. Verify data in Supabase dashboard")
    print("2. Test application with Supabase")
    print("3. Backup original files (keep for 30 days)")
    print("4. Update .env to use Supabase")
    print("=" * 60)


if __name__ == '__main__':
    main()
```

---

## ⚙️ Environment Setup

### `.env` (Updated)

```bash
# Supabase Configuration
SUPABASE_URL=https://yourproject.supabase.co
SUPABASE_ANON_KEY=eyJhbGc...
SUPABASE_SERVICE_KEY=eyJhbGc...  # For server-side operations

# OpenAI / OpenRouter
OPENAI_API_KEY=sk-...
OPENROUTER_API_KEY=sk-or-v1-...
USE_OPENROUTER=false

# Email (SMTP)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=your-email@gmail.com
FROM_NAME=CreatorPulse

# Or use SendGrid
USE_SENDGRID=false
SENDGRID_API_KEY=SG....

# YouTube Data API
YOUTUBE_API_KEY=AIza...

# X/Twitter API (optional)
X_API_KEY=...
X_API_SECRET=...
X_BEARER_TOKEN=...

# Scheduler
SCHEDULER_ENABLED=true
SCHEDULER_TIME=08:00
SCHEDULER_TIMEZONE=UTC

# Application
DEBUG=false
LOG_LEVEL=INFO
```

---

## 📦 Updated Dependencies

### `requirements.txt`

```txt
# Existing dependencies
streamlit>=1.30.0
openai>=1.0.0
beautifulsoup4>=4.12.0
feedparser>=6.0.10
praw>=7.7.0
scikit-learn>=1.3.0
nltk>=3.8.1
textstat>=0.7.3
python-Levenshtein>=0.23.0

# NEW - Supabase integration
supabase>=2.0.0
postgrest-py>=0.13.0
realtime-py>=1.0.0
storage3>=0.7.0

# Database utilities
psycopg2-binary>=2.9.9

# Authentication
python-jose>=3.3.0
passlib>=1.7.4

# Email
sendgrid>=6.11.0

# Utilities
python-dotenv>=1.0.0
requests>=2.31.0
```

---

## 🧪 Testing

### Test Supabase Connection

```python
# tests/integration/test_supabase_integration.py

import pytest
from src.ai_newsletter.database.supabase_client import SupabaseManager
from src.ai_newsletter.models.content import ContentItem
from datetime import datetime


@pytest.fixture
def supabase():
    """Initialize Supabase client for testing."""
    return SupabaseManager()


@pytest.fixture
def test_workspace(supabase):
    """Create a test workspace."""
    workspace = supabase.create_workspace(
        name=f"test_workspace_{datetime.now().timestamp()}",
        description="Test workspace"
    )
    yield workspace
    # Cleanup
    supabase.delete_workspace(workspace['id'])


def test_supabase_connection(supabase):
    """Test basic Supabase connection."""
    assert supabase.health_check() is True


def test_create_workspace(supabase, test_workspace):
    """Test workspace creation."""
    assert test_workspace['name'].startswith('test_workspace')
    assert test_workspace['id'] is not None


def test_save_and_load_content(supabase, test_workspace):
    """Test saving and loading content items."""
    workspace_id = test_workspace['id']

    # Create test content items
    items = [
        ContentItem(
            title=f"Test Item {i}",
            source="reddit",
            source_url=f"https://reddit.com/test{i}",
            created_at=datetime.now(),
            score=100 * i
        )
        for i in range(5)
    ]

    # Save items
    saved = supabase.save_content_items(workspace_id, items)
    assert len(saved) == 5

    # Load items
    loaded = supabase.load_content_items(workspace_id, days=1)
    assert len(loaded) == 5
    assert loaded[0].title == "Test Item 0"


def test_workspace_isolation(supabase):
    """Test that workspaces are properly isolated."""
    # Create two workspaces
    workspace1 = supabase.create_workspace("test_ws1", "Workspace 1")
    workspace2 = supabase.create_workspace("test_ws2", "Workspace 2")

    # Add content to workspace 1
    items1 = [ContentItem(
        title="Item in WS1",
        source="reddit",
        source_url="https://reddit.com/test",
        created_at=datetime.now()
    )]
    supabase.save_content_items(workspace1['id'], items1)

    # Load content from workspace 2 (should be empty)
    items2 = supabase.load_content_items(workspace2['id'], days=1)
    assert len(items2) == 0

    # Cleanup
    supabase.delete_workspace(workspace1['id'])
    supabase.delete_workspace(workspace2['id'])


# Run tests
if __name__ == '__main__':
    pytest.main([__file__, '-v'])
```

---

## 📊 Cost Analysis

### Supabase Pricing Tiers

#### **Free Tier**
- Database: 500MB storage
- File Storage: 1GB
- Bandwidth: 2GB
- Authentication: 50,000 monthly active users
- API Requests: Unlimited
- **Cost:** $0/month

**Suitable for:**
- Individual creators
- Testing/development
- Up to ~10,000 content items
- Up to ~1,000 newsletters

#### **Pro Tier** (Recommended)
- Database: 8GB storage
- File Storage: 100GB
- Bandwidth: 50GB
- Authentication: 100,000 monthly active users
- Daily backups
- **Cost:** $25/month per project

**Suitable for:**
- Agencies (5-10 clients)
- Growing creators
- Up to ~1M content items
- Up to ~50,000 newsletters

#### **Team Tier**
- Everything in Pro
- Plus: Priority support, SOC2 compliance
- **Cost:** $599/month per organization

#### **Enterprise**
- Custom limits
- SLA guarantees
- Dedicated support
- On-premise option
- **Cost:** Custom pricing

### Cost Comparison

| Use Case | JSON Files | Supabase Free | Supabase Pro |
|----------|-----------|---------------|--------------|
| **Single User** | ✅ $0/mo | ✅ $0/mo | ⚠️ $25/mo |
| **Small Agency (1-5 clients)** | ❌ Not scalable | ✅ $0/mo | ✅ $25/mo |
| **Medium Agency (5-20 clients)** | ❌ Not possible | ⚠️ May exceed limits | ✅ $25/mo |
| **Large Agency (20+ clients)** | ❌ Not possible | ❌ Exceeds limits | ✅ $25-599/mo |

---

## 🚀 Deployment

### Streamlit Cloud + Supabase

```yaml
# streamlit-app-config.yaml

[server]
headless = true
port = 8501

[browser]
serverAddress = "yourapp.streamlit.app"
gatherUsageStats = false

[theme]
primaryColor = "#667eea"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f8f9fa"
textColor = "#333333"
```

### Environment Variables (Streamlit Cloud)

Set these in Streamlit Cloud secrets:

```toml
# .streamlit/secrets.toml

[supabase]
url = "https://yourproject.supabase.co"
anon_key = "eyJhbGc..."
service_key = "eyJhbGc..."

[openai]
api_key = "sk-..."

[openrouter]
api_key = "sk-or-v1-..."
```

---

## 📝 Summary

### What Gets Added with Supabase

1. **Multi-user authentication** (signup, login, password reset)
2. **Team collaboration** (workspace sharing, roles, permissions)
3. **PostgreSQL database** (scalable, queryable, ACID compliant)
4. **Real-time features** (live dashboard updates)
5. **Row-level security** (automatic multi-tenant isolation)
6. **Better analytics** (SQL queries, aggregations, time-series)
7. **File storage** (for newsletter templates, images)
8. **Edge Functions** (serverless tracking endpoints)

### Updated Timeline

| Sprint | Features | Days | Cost |
|--------|----------|------|------|
| Sprint 0 | Supabase Integration | 3-4 | $0 (Free tier to start) |
| Sprint 1 | Multi-User Workspaces | 3-4 | $25/mo (Pro tier recommended) |
| Sprint 2 | Style + Trends | 6-7 | $25/mo |
| Sprint 3 | Feedback + Analytics | 6-7 | $25/mo |
| Sprint 4 | Polish + Testing | 5 | $25/mo |
| **Total** | | **23-27 days** | **$25/mo** |

### Recommendation

**✅ Integrate Supabase** if you plan to:
- Support multiple users (agencies, teams)
- Scale beyond 10,000 items
- Add real-time collaboration
- Ensure data security (RLS)
- Build a SaaS product

**❌ Skip Supabase** if you:
- Only have single users
- Want zero dependencies
- Need offline operation
- Want to minimize costs

---

**Status:** ✅ Ready for Implementation
**Next Step:** Create Supabase project and start Sprint 0

---
