-- Migration 007: Create Trends Detection Tables
-- Purpose: Store detected trends and historical content for velocity analysis
-- Features:
--   - Detected trends with strength scoring
--   - Historical content tracking (7 days rolling window)
--   - Cross-source validation
--   - Trend keywords and topics
--   - Related content items for evidence
-- Relations: Many-to-one with workspaces, many-to-many with content_items

-- =============================================================================
-- DROP EXISTING (if re-running)
-- =============================================================================

DROP TABLE IF EXISTS trend_content_items CASCADE;
DROP TABLE IF EXISTS trends CASCADE;
DROP TABLE IF EXISTS historical_content CASCADE;

-- =============================================================================
-- CREATE TABLE: trends
-- =============================================================================

CREATE TABLE trends (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Foreign Keys
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,

    -- Core Attributes
    topic VARCHAR(255) NOT NULL,
    keywords TEXT[] DEFAULT ARRAY[]::TEXT[],

    -- Strength Indicators
    strength_score DECIMAL(4,3) NOT NULL CHECK (strength_score >= 0 AND strength_score <= 1),
    mention_count INTEGER DEFAULT 0,
    velocity DECIMAL(8,2) DEFAULT 0.0,

    -- Sources
    sources TEXT[] DEFAULT ARRAY[]::TEXT[],
    source_count INTEGER DEFAULT 0,

    -- Context
    explanation TEXT,
    related_topics TEXT[] DEFAULT ARRAY[]::TEXT[],

    -- Evidence (stores content item IDs)
    key_content_item_ids UUID[] DEFAULT ARRAY[]::UUID[],

    -- Time Tracking
    first_seen TIMESTAMPTZ,
    peak_time TIMESTAMPTZ,
    detected_at TIMESTAMPTZ DEFAULT NOW(),

    -- Metadata
    confidence_level VARCHAR(20) DEFAULT 'medium',
    is_active BOOLEAN DEFAULT true,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================================================
-- CREATE TABLE: historical_content
-- =============================================================================

CREATE TABLE historical_content (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Foreign Keys
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    content_item_id UUID REFERENCES content_items(id) ON DELETE SET NULL,

    -- Content Snapshot
    title TEXT NOT NULL,
    summary TEXT,
    content TEXT,
    source VARCHAR(50) NOT NULL,
    source_url TEXT,

    -- Metadata
    score INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL,
    scraped_at TIMESTAMPTZ DEFAULT NOW(),

    -- For trend detection
    keywords TEXT[] DEFAULT ARRAY[]::TEXT[],
    topic_cluster INTEGER,

    -- TTL management
    expires_at TIMESTAMPTZ DEFAULT (NOW() + INTERVAL '7 days'),

    -- Constraints
    CONSTRAINT chk_historical_content_created_at CHECK (created_at IS NOT NULL)
);

-- =============================================================================
-- CREATE TABLE: trend_content_items (junction table)
-- =============================================================================

CREATE TABLE trend_content_items (
    trend_id UUID NOT NULL REFERENCES trends(id) ON DELETE CASCADE,
    content_item_id UUID NOT NULL REFERENCES content_items(id) ON DELETE CASCADE,
    relevance_score DECIMAL(4,3) DEFAULT 0.5,

    created_at TIMESTAMPTZ DEFAULT NOW(),

    PRIMARY KEY (trend_id, content_item_id)
);

-- =============================================================================
-- INDEXES
-- =============================================================================

-- Trends indexes
CREATE INDEX idx_trends_workspace_id ON trends(workspace_id);
CREATE INDEX idx_trends_detected_at ON trends(detected_at DESC);
CREATE INDEX idx_trends_strength_score ON trends(strength_score DESC);
CREATE INDEX idx_trends_is_active ON trends(is_active);
CREATE INDEX idx_trends_workspace_topic ON trends(workspace_id, topic);
CREATE INDEX idx_trends_keywords ON trends USING gin(keywords);

-- Historical content indexes
CREATE INDEX idx_historical_content_workspace_id ON historical_content(workspace_id);
CREATE INDEX idx_historical_content_created_at ON historical_content(created_at DESC);
CREATE INDEX idx_historical_content_expires_at ON historical_content(expires_at);
CREATE INDEX idx_historical_content_source ON historical_content(source);
CREATE INDEX idx_historical_content_keywords ON historical_content USING gin(keywords);

-- Junction table indexes
CREATE INDEX idx_trend_content_items_trend_id ON trend_content_items(trend_id);
CREATE INDEX idx_trend_content_items_content_id ON trend_content_items(content_item_id);

-- =============================================================================
-- ROW LEVEL SECURITY (RLS)
-- =============================================================================

ALTER TABLE trends ENABLE ROW LEVEL SECURITY;
ALTER TABLE historical_content ENABLE ROW LEVEL SECURITY;
ALTER TABLE trend_content_items ENABLE ROW LEVEL SECURITY;

-- Policies: Trends
CREATE POLICY "Users can view their workspace trends"
    ON trends FOR SELECT
    USING (
        workspace_id IN (
            SELECT workspace_id FROM user_workspaces
            WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "Users can insert trends for their workspaces"
    ON trends FOR INSERT
    WITH CHECK (
        workspace_id IN (
            SELECT workspace_id FROM user_workspaces
            WHERE user_id = auth.uid()
            AND role IN ('owner', 'admin', 'editor')
        )
    );

CREATE POLICY "Users can update their workspace trends"
    ON trends FOR UPDATE
    USING (
        workspace_id IN (
            SELECT workspace_id FROM user_workspaces
            WHERE user_id = auth.uid()
            AND role IN ('owner', 'admin', 'editor')
        )
    );

CREATE POLICY "Users can delete their workspace trends"
    ON trends FOR DELETE
    USING (
        workspace_id IN (
            SELECT workspace_id FROM user_workspaces
            WHERE user_id = auth.uid()
            AND role IN ('owner', 'admin')
        )
    );

-- Policies: Historical Content
CREATE POLICY "Users can view their workspace historical content"
    ON historical_content FOR SELECT
    USING (
        workspace_id IN (
            SELECT workspace_id FROM user_workspaces
            WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "Users can insert historical content for their workspaces"
    ON historical_content FOR INSERT
    WITH CHECK (
        workspace_id IN (
            SELECT workspace_id FROM user_workspaces
            WHERE user_id = auth.uid()
        )
    );

-- Policies: Trend Content Items
CREATE POLICY "Users can view trend content items"
    ON trend_content_items FOR SELECT
    USING (
        trend_id IN (
            SELECT id FROM trends
            WHERE workspace_id IN (
                SELECT workspace_id FROM user_workspaces
                WHERE user_id = auth.uid()
            )
        )
    );

CREATE POLICY "Users can manage trend content items"
    ON trend_content_items FOR ALL
    USING (
        trend_id IN (
            SELECT id FROM trends
            WHERE workspace_id IN (
                SELECT workspace_id FROM user_workspaces
                WHERE user_id = auth.uid()
                AND role IN ('owner', 'admin', 'editor')
            )
        )
    );

-- =============================================================================
-- TRIGGERS
-- =============================================================================

-- Trigger: Update updated_at timestamp for trends
CREATE OR REPLACE FUNCTION update_trends_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_trends_updated_at
    BEFORE UPDATE ON trends
    FOR EACH ROW
    EXECUTE FUNCTION update_trends_updated_at();

-- =============================================================================
-- UTILITY FUNCTIONS
-- =============================================================================

-- Function: Cleanup expired historical content
CREATE OR REPLACE FUNCTION cleanup_expired_historical_content()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM historical_content
    WHERE expires_at < NOW();

    GET DIAGNOSTICS deleted_count = ROW_COUNT;

    RAISE NOTICE 'Cleaned up % expired historical content records', deleted_count;

    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function: Get active trends for workspace
CREATE OR REPLACE FUNCTION get_active_trends(workspace_uuid UUID, limit_count INTEGER DEFAULT 5)
RETURNS TABLE (
    id UUID,
    topic VARCHAR,
    strength_score DECIMAL,
    mention_count INTEGER,
    source_count INTEGER,
    confidence_level VARCHAR,
    detected_at TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        t.id,
        t.topic,
        t.strength_score,
        t.mention_count,
        t.source_count,
        t.confidence_level,
        t.detected_at
    FROM trends t
    WHERE t.workspace_id = workspace_uuid
        AND t.is_active = true
    ORDER BY t.strength_score DESC, t.detected_at DESC
    LIMIT limit_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function: Get trend history for workspace
CREATE OR REPLACE FUNCTION get_trend_history(
    workspace_uuid UUID,
    days_back INTEGER DEFAULT 30,
    limit_count INTEGER DEFAULT 50
)
RETURNS TABLE (
    detected_date DATE,
    topic VARCHAR,
    strength_score DECIMAL,
    mention_count INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        DATE(t.detected_at) as detected_date,
        t.topic,
        t.strength_score,
        t.mention_count
    FROM trends t
    WHERE t.workspace_id = workspace_uuid
        AND t.detected_at >= NOW() - (days_back || ' days')::INTERVAL
    ORDER BY t.detected_at DESC, t.strength_score DESC
    LIMIT limit_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function: Calculate trend velocity
CREATE OR REPLACE FUNCTION calculate_trend_velocity(
    workspace_uuid UUID,
    topic_text VARCHAR,
    current_mentions INTEGER
)
RETURNS DECIMAL AS $$
DECLARE
    previous_mentions INTEGER;
    velocity_value DECIMAL;
BEGIN
    -- Get mention count from 24 hours ago
    SELECT COALESCE(mention_count, 0)
    INTO previous_mentions
    FROM trends
    WHERE workspace_id = workspace_uuid
        AND topic = topic_text
        AND detected_at >= NOW() - INTERVAL '24 hours'
        AND detected_at < NOW() - INTERVAL '23 hours'
    ORDER BY detected_at DESC
    LIMIT 1;

    -- Calculate percentage increase
    IF previous_mentions > 0 THEN
        velocity_value := ((current_mentions - previous_mentions)::DECIMAL / previous_mentions) * 100;
    ELSIF current_mentions > 0 THEN
        velocity_value := 100.0; -- New topic
    ELSE
        velocity_value := 0.0;
    END IF;

    RETURN velocity_value;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- =============================================================================
-- VERIFICATION
-- =============================================================================

DO $$
BEGIN
    IF EXISTS (SELECT FROM trends LIMIT 1) THEN
        RAISE NOTICE 'Trends table created and has data';
    ELSE
        RAISE NOTICE 'Trends table created successfully (empty)';
    END IF;

    IF EXISTS (SELECT FROM historical_content LIMIT 1) THEN
        RAISE NOTICE 'Historical content table created and has data';
    ELSE
        RAISE NOTICE 'Historical content table created successfully (empty)';
    END IF;
END $$;

SELECT 'Migration 007 completed: trends and historical_content tables created' AS status;
