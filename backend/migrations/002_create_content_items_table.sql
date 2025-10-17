-- Migration: Create content_items table
-- Sprint: 2
-- Purpose: Store scraped content items per workspace

CREATE TABLE IF NOT EXISTS content_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,

    -- Basic content fields
    title TEXT NOT NULL,
    source TEXT NOT NULL,                  -- reddit, rss, blog, x, youtube
    source_url TEXT NOT NULL,
    content TEXT,
    summary TEXT,

    -- Author information
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

    -- Organization
    tags TEXT[] DEFAULT '{}',
    category TEXT,

    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL,       -- Original publish date
    scraped_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Metadata
    metadata JSONB DEFAULT '{}'
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_content_items_workspace
    ON content_items(workspace_id);

CREATE INDEX IF NOT EXISTS idx_content_items_source
    ON content_items(workspace_id, source);

CREATE INDEX IF NOT EXISTS idx_content_items_created_at
    ON content_items(workspace_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_content_items_scraped_at
    ON content_items(workspace_id, scraped_at DESC);

-- Full-text search index
CREATE INDEX IF NOT EXISTS idx_content_items_title_fts
    ON content_items USING gin(to_tsvector('english', title));

CREATE INDEX IF NOT EXISTS idx_content_items_content_fts
    ON content_items USING gin(to_tsvector('english', coalesce(content, '')));

-- Enable Row Level Security
ALTER TABLE content_items ENABLE ROW LEVEL SECURITY;

-- RLS Policy: Users can view content from their workspaces
CREATE POLICY "Users can view content from their workspaces"
    ON content_items FOR SELECT
    USING (
        workspace_id IN (
            SELECT workspace_id FROM user_workspaces
            WHERE user_id = auth.uid()
        )
    );

-- RLS Policy: Users can create content in their workspaces
CREATE POLICY "Users can create content in their workspaces"
    ON content_items FOR INSERT
    WITH CHECK (
        workspace_id IN (
            SELECT workspace_id FROM user_workspaces
            WHERE user_id = auth.uid()
            AND role IN ('owner', 'editor')
        )
    );

-- RLS Policy: Users can update content in their workspaces
CREATE POLICY "Users can update content in their workspaces"
    ON content_items FOR UPDATE
    USING (
        workspace_id IN (
            SELECT workspace_id FROM user_workspaces
            WHERE user_id = auth.uid()
            AND role IN ('owner', 'editor')
        )
    );

-- RLS Policy: Users can delete content from their workspaces
CREATE POLICY "Users can delete content from their workspaces"
    ON content_items FOR DELETE
    USING (
        workspace_id IN (
            SELECT workspace_id FROM user_workspaces
            WHERE user_id = auth.uid()
            AND role IN ('owner', 'editor')
        )
    );

-- Comments
COMMENT ON TABLE content_items IS 'Stores scraped content items per workspace';
COMMENT ON COLUMN content_items.source IS 'Content source: reddit, rss, blog, x, youtube';
COMMENT ON COLUMN content_items.created_at IS 'Original publish date from source';
COMMENT ON COLUMN content_items.scraped_at IS 'When this item was scraped';
