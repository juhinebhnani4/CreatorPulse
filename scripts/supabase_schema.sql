-- CreatorPulse Database Schema for Supabase
-- Run this script in Supabase SQL Editor
-- Last Updated: 2025-01-15

-- =============================================================================
-- ENABLE EXTENSIONS
-- =============================================================================

-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =============================================================================
-- TABLE: workspaces
-- =============================================================================

CREATE TABLE IF NOT EXISTS workspaces (
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
CREATE INDEX IF NOT EXISTS idx_workspaces_owner ON workspaces(owner_id);
CREATE INDEX IF NOT EXISTS idx_workspaces_created ON workspaces(created_at DESC);

-- =============================================================================
-- TABLE: user_workspaces (Membership)
-- =============================================================================

CREATE TABLE IF NOT EXISTS user_workspaces (
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
CREATE INDEX IF NOT EXISTS idx_user_workspaces_user ON user_workspaces(user_id);
CREATE INDEX IF NOT EXISTS idx_user_workspaces_workspace ON user_workspaces(workspace_id);

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

-- =============================================================================
-- WORKSPACES RLS POLICIES
-- (Created after user_workspaces table exists)
-- =============================================================================

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

-- =============================================================================
-- TABLE: workspace_configs
-- =============================================================================

CREATE TABLE IF NOT EXISTS workspace_configs (
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
CREATE INDEX IF NOT EXISTS idx_workspace_configs_workspace ON workspace_configs(workspace_id);

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

CREATE POLICY "Editors can insert workspace configs"
    ON workspace_configs FOR INSERT
    WITH CHECK (
        workspace_id IN (
            SELECT workspace_id FROM user_workspaces
            WHERE user_id = auth.uid() AND role IN ('owner', 'editor')
        )
    );

-- =============================================================================
-- TABLE: content_items (Scraped Content)
-- =============================================================================

CREATE TABLE IF NOT EXISTS content_items (
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
CREATE INDEX IF NOT EXISTS idx_content_workspace ON content_items(workspace_id);
CREATE INDEX IF NOT EXISTS idx_content_source ON content_items(source);
CREATE INDEX IF NOT EXISTS idx_content_created ON content_items(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_content_score ON content_items(score DESC);
CREATE INDEX IF NOT EXISTS idx_content_workspace_created ON content_items(workspace_id, created_at DESC);

-- Full-text search
CREATE INDEX IF NOT EXISTS idx_content_title_search ON content_items USING GIN(to_tsvector('english', title));
CREATE INDEX IF NOT EXISTS idx_content_summary_search ON content_items USING GIN(to_tsvector('english', COALESCE(summary, '')));

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

-- =============================================================================
-- TABLE: style_profiles
-- =============================================================================

CREATE TABLE IF NOT EXISTS style_profiles (
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
CREATE INDEX IF NOT EXISTS idx_style_workspace ON style_profiles(workspace_id);

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

-- =============================================================================
-- TABLE: trends
-- =============================================================================

CREATE TABLE IF NOT EXISTS trends (
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
CREATE INDEX IF NOT EXISTS idx_trends_workspace ON trends(workspace_id);
CREATE INDEX IF NOT EXISTS idx_trends_detected ON trends(detected_at DESC);
CREATE INDEX IF NOT EXISTS idx_trends_strength ON trends(strength_score DESC);

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

-- =============================================================================
-- TABLE: feedback_items
-- =============================================================================

CREATE TABLE IF NOT EXISTS feedback_items (
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
CREATE INDEX IF NOT EXISTS idx_feedback_workspace ON feedback_items(workspace_id);
CREATE INDEX IF NOT EXISTS idx_feedback_content ON feedback_items(content_item_id);
CREATE INDEX IF NOT EXISTS idx_feedback_user ON feedback_items(user_id);
CREATE INDEX IF NOT EXISTS idx_feedback_date ON feedback_items(feedback_date DESC);

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

-- =============================================================================
-- TABLE: newsletters
-- =============================================================================

CREATE TABLE IF NOT EXISTS newsletters (
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
CREATE INDEX IF NOT EXISTS idx_newsletters_workspace ON newsletters(workspace_id);
CREATE INDEX IF NOT EXISTS idx_newsletters_generated ON newsletters(generated_at DESC);
CREATE INDEX IF NOT EXISTS idx_newsletters_creator ON newsletters(created_by);

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

-- =============================================================================
-- TABLE: analytics_events
-- =============================================================================

CREATE TABLE IF NOT EXISTS analytics_events (
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
CREATE INDEX IF NOT EXISTS idx_analytics_workspace ON analytics_events(workspace_id);
CREATE INDEX IF NOT EXISTS idx_analytics_newsletter ON analytics_events(newsletter_id);
CREATE INDEX IF NOT EXISTS idx_analytics_event_type ON analytics_events(event_type);
CREATE INDEX IF NOT EXISTS idx_analytics_event_time ON analytics_events(event_time DESC);
CREATE INDEX IF NOT EXISTS idx_analytics_recipient ON analytics_events(recipient);

-- Composite indexes for common queries
CREATE INDEX IF NOT EXISTS idx_analytics_workspace_time ON analytics_events(workspace_id, event_time DESC);
CREATE INDEX IF NOT EXISTS idx_analytics_newsletter_type ON analytics_events(newsletter_id, event_type);

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

-- =============================================================================
-- COMPLETED
-- =============================================================================

-- Success message
DO $$
BEGIN
    RAISE NOTICE 'CreatorPulse database schema created successfully!';
    RAISE NOTICE 'Next steps:';
    RAISE NOTICE '1. Verify tables in Supabase Dashboard > Table Editor';
    RAISE NOTICE '2. Test authentication with signup/signin';
    RAISE NOTICE '3. Create your first workspace';
END $$;
