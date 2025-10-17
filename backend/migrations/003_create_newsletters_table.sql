-- Migration: Create newsletters table
-- Sprint: 3
-- Purpose: Store generated newsletters per workspace

CREATE TABLE IF NOT EXISTS newsletters (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    html_content TEXT NOT NULL,
    plain_text_content TEXT,

    -- Generation metadata
    content_item_ids UUID[] DEFAULT '{}',  -- Array of content_item IDs used
    content_items_count INTEGER DEFAULT 0,
    model_used TEXT,                        -- gpt-4, claude-3-sonnet, etc.
    temperature REAL,
    tone TEXT,
    language TEXT,

    -- Status
    status TEXT DEFAULT 'draft',           -- draft, sent, scheduled
    generated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    sent_at TIMESTAMPTZ,

    -- Metadata
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_newsletters_workspace
    ON newsletters(workspace_id);

CREATE INDEX IF NOT EXISTS idx_newsletters_status
    ON newsletters(workspace_id, status);

CREATE INDEX IF NOT EXISTS idx_newsletters_generated_at
    ON newsletters(workspace_id, generated_at DESC);

-- Enable Row Level Security
ALTER TABLE newsletters ENABLE ROW LEVEL SECURITY;

-- RLS Policy: Users can view their workspace newsletters
CREATE POLICY "Users can view their workspace newsletters"
    ON newsletters FOR SELECT
    USING (
        workspace_id IN (
            SELECT workspace_id FROM user_workspaces
            WHERE user_id = auth.uid()
        )
    );

-- RLS Policy: Users can create newsletters in their workspaces
CREATE POLICY "Users can create newsletters in their workspaces"
    ON newsletters FOR INSERT
    WITH CHECK (
        workspace_id IN (
            SELECT workspace_id FROM user_workspaces
            WHERE user_id = auth.uid()
            AND role IN ('owner', 'editor')
        )
    );

-- RLS Policy: Users can update their workspace newsletters
CREATE POLICY "Users can update their workspace newsletters"
    ON newsletters FOR UPDATE
    USING (
        workspace_id IN (
            SELECT workspace_id FROM user_workspaces
            WHERE user_id = auth.uid()
            AND role IN ('owner', 'editor')
        )
    );

-- RLS Policy: Users can delete their workspace newsletters
CREATE POLICY "Users can delete their workspace newsletters"
    ON newsletters FOR DELETE
    USING (
        workspace_id IN (
            SELECT workspace_id FROM user_workspaces
            WHERE user_id = auth.uid()
            AND role = 'owner'
        )
    );

-- Comments
COMMENT ON TABLE newsletters IS 'Stores generated newsletters per workspace';
COMMENT ON COLUMN newsletters.content_item_ids IS 'Array of content_item IDs that were used to generate this newsletter';
COMMENT ON COLUMN newsletters.status IS 'Newsletter status: draft, sent, scheduled';
