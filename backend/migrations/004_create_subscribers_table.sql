-- Migration: Create subscribers table
-- Sprint: 4A
-- Purpose: Store subscriber emails per workspace for newsletter delivery

CREATE TABLE IF NOT EXISTS subscribers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,

    -- Subscriber info
    email TEXT NOT NULL,
    name TEXT,

    -- Status tracking
    status TEXT DEFAULT 'active',           -- active, unsubscribed, bounced
    source TEXT,                            -- how they subscribed (manual, api, import, etc.)

    -- Timestamps
    subscribed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    unsubscribed_at TIMESTAMPTZ,
    last_sent_at TIMESTAMPTZ,              -- Last newsletter sent to this subscriber

    -- Metadata
    metadata JSONB DEFAULT '{}',           -- Custom fields, tags, etc.

    -- Audit
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Unique constraint: one email per workspace
    CONSTRAINT unique_email_per_workspace UNIQUE(workspace_id, email)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_subscribers_workspace
    ON subscribers(workspace_id);

CREATE INDEX IF NOT EXISTS idx_subscribers_email
    ON subscribers(email);

CREATE INDEX IF NOT EXISTS idx_subscribers_status
    ON subscribers(workspace_id, status);

CREATE INDEX IF NOT EXISTS idx_subscribers_subscribed_at
    ON subscribers(workspace_id, subscribed_at DESC);

-- Enable Row Level Security
ALTER TABLE subscribers ENABLE ROW LEVEL SECURITY;

-- RLS Policy: Users can view subscribers in their workspaces
CREATE POLICY "Users can view subscribers in their workspaces"
    ON subscribers FOR SELECT
    USING (
        workspace_id IN (
            SELECT workspace_id FROM user_workspaces
            WHERE user_id = auth.uid()
        )
    );

-- RLS Policy: Users can add subscribers to their workspaces
CREATE POLICY "Users can add subscribers to their workspaces"
    ON subscribers FOR INSERT
    WITH CHECK (
        workspace_id IN (
            SELECT workspace_id FROM user_workspaces
            WHERE user_id = auth.uid()
            AND role IN ('owner', 'editor')
        )
    );

-- RLS Policy: Users can update subscribers in their workspaces
CREATE POLICY "Users can update subscribers in their workspaces"
    ON subscribers FOR UPDATE
    USING (
        workspace_id IN (
            SELECT workspace_id FROM user_workspaces
            WHERE user_id = auth.uid()
            AND role IN ('owner', 'editor')
        )
    );

-- RLS Policy: Users can delete subscribers from their workspaces
CREATE POLICY "Users can delete subscribers from their workspaces"
    ON subscribers FOR DELETE
    USING (
        workspace_id IN (
            SELECT workspace_id FROM user_workspaces
            WHERE user_id = auth.uid()
            AND role IN ('owner', 'editor')
        )
    );

-- Delivery tracking table
CREATE TABLE IF NOT EXISTS newsletter_deliveries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    newsletter_id UUID NOT NULL REFERENCES newsletters(id) ON DELETE CASCADE,
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,

    -- Delivery stats
    total_subscribers INTEGER DEFAULT 0,
    sent_count INTEGER DEFAULT 0,
    failed_count INTEGER DEFAULT 0,

    -- Status
    status TEXT DEFAULT 'pending',         -- pending, sending, completed, failed
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,

    -- Error tracking
    errors JSONB DEFAULT '[]',

    -- Metadata
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for delivery tracking
CREATE INDEX IF NOT EXISTS idx_deliveries_newsletter
    ON newsletter_deliveries(newsletter_id);

CREATE INDEX IF NOT EXISTS idx_deliveries_workspace
    ON newsletter_deliveries(workspace_id);

CREATE INDEX IF NOT EXISTS idx_deliveries_status
    ON newsletter_deliveries(status);

-- Enable RLS on deliveries
ALTER TABLE newsletter_deliveries ENABLE ROW LEVEL SECURITY;

-- RLS Policy: Users can view deliveries in their workspaces
CREATE POLICY "Users can view deliveries in their workspaces"
    ON newsletter_deliveries FOR SELECT
    USING (
        workspace_id IN (
            SELECT workspace_id FROM user_workspaces
            WHERE user_id = auth.uid()
        )
    );

-- RLS Policy: Users can create deliveries in their workspaces
CREATE POLICY "Users can create deliveries in their workspaces"
    ON newsletter_deliveries FOR INSERT
    WITH CHECK (
        workspace_id IN (
            SELECT workspace_id FROM user_workspaces
            WHERE user_id = auth.uid()
            AND role IN ('owner', 'editor')
        )
    );

-- RLS Policy: Users can update deliveries in their workspaces
CREATE POLICY "Users can update deliveries in their workspaces"
    ON newsletter_deliveries FOR UPDATE
    USING (
        workspace_id IN (
            SELECT workspace_id FROM user_workspaces
            WHERE user_id = auth.uid()
            AND role IN ('owner', 'editor')
        )
    );

-- Comments
COMMENT ON TABLE subscribers IS 'Stores subscriber emails per workspace for newsletter delivery';
COMMENT ON COLUMN subscribers.status IS 'Subscriber status: active, unsubscribed, bounced';
COMMENT ON COLUMN subscribers.source IS 'How subscriber was added: manual, api, import, etc.';

COMMENT ON TABLE newsletter_deliveries IS 'Tracks newsletter delivery batches and their status';
COMMENT ON COLUMN newsletter_deliveries.status IS 'Delivery status: pending, sending, completed, failed';
