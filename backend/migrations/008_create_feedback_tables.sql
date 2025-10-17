-- Migration 008: Create Feedback & Learning Tables
-- Purpose: Enable feedback collection and learning from user preferences
-- Features:
--   - Content item feedback tracking (thumbs up/down)
--   - Newsletter-level feedback (ratings, time to finalize)
--   - Source quality scoring (learned from feedback patterns)
--   - Content preferences extraction
--   - Automatic score adjustments based on learning
-- Relations: Many-to-one with workspaces, users, content_items, newsletters

-- =============================================================================
-- DROP EXISTING (if re-running)
-- =============================================================================

DROP TABLE IF EXISTS feedback_items CASCADE;
DROP TABLE IF EXISTS newsletter_feedback CASCADE;
DROP TABLE IF EXISTS source_quality_scores CASCADE;
DROP TABLE IF EXISTS content_preferences CASCADE;

-- =============================================================================
-- CREATE TABLE: feedback_items
-- =============================================================================

CREATE TABLE feedback_items (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Foreign Keys
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    user_id UUID NOT NULL,  -- References auth.users (Supabase Auth)
    content_item_id UUID NOT NULL REFERENCES content_items(id) ON DELETE CASCADE,
    newsletter_id UUID REFERENCES newsletters(id) ON DELETE SET NULL,

    -- Feedback Data
    rating VARCHAR(20) NOT NULL CHECK (rating IN ('positive', 'negative', 'neutral')),
    included_in_final BOOLEAN DEFAULT false,

    -- Edit Tracking
    original_summary TEXT,
    edited_summary TEXT,
    edit_distance DECIMAL(4,3) DEFAULT 0.0 CHECK (edit_distance >= 0 AND edit_distance <= 1),

    -- Context
    feedback_notes TEXT,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================================================
-- CREATE TABLE: newsletter_feedback
-- =============================================================================

CREATE TABLE newsletter_feedback (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Foreign Keys
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    user_id UUID NOT NULL,  -- References auth.users (Supabase Auth)
    newsletter_id UUID NOT NULL REFERENCES newsletters(id) ON DELETE CASCADE,

    -- Overall Feedback
    overall_rating INTEGER CHECK (overall_rating >= 1 AND overall_rating <= 5),
    time_to_finalize_minutes INTEGER CHECK (time_to_finalize_minutes >= 0),

    -- Changes Made
    items_added INTEGER DEFAULT 0,
    items_removed INTEGER DEFAULT 0,
    items_edited INTEGER DEFAULT 0,

    -- User Notes
    notes TEXT,

    -- Satisfaction Indicators
    would_recommend BOOLEAN,
    draft_acceptance_rate DECIMAL(4,3) CHECK (draft_acceptance_rate >= 0 AND draft_acceptance_rate <= 1),

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Ensure one feedback per newsletter per user
    UNIQUE(newsletter_id, user_id)
);

-- =============================================================================
-- CREATE TABLE: source_quality_scores
-- =============================================================================

CREATE TABLE source_quality_scores (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Foreign Keys
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,

    -- Source Identification
    source_name VARCHAR(50) NOT NULL,

    -- Quality Metrics
    quality_score DECIMAL(4,3) NOT NULL DEFAULT 0.5 CHECK (quality_score >= 0 AND quality_score <= 1),

    -- Feedback Counts
    positive_count INTEGER DEFAULT 0,
    negative_count INTEGER DEFAULT 0,
    neutral_count INTEGER DEFAULT 0,
    total_feedback_count INTEGER DEFAULT 0,

    -- Statistics
    inclusion_rate DECIMAL(4,3) DEFAULT 0.5,  -- % of items included in final newsletters
    avg_edit_distance DECIMAL(4,3) DEFAULT 0.0,  -- Average amount of editing needed

    -- Performance Tracking
    trending_score DECIMAL(4,3) DEFAULT 0.5,  -- Recent performance (weighted)

    -- Timestamps
    last_calculated_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Ensure one score per source per workspace
    UNIQUE(workspace_id, source_name)
);

-- =============================================================================
-- CREATE TABLE: content_preferences
-- =============================================================================

CREATE TABLE content_preferences (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Foreign Keys
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,

    -- Preferred Sources (ranked by quality)
    preferred_sources TEXT[] DEFAULT ARRAY[]::TEXT[],

    -- Avoided Topics/Keywords
    avoided_topics TEXT[] DEFAULT ARRAY[]::TEXT[],
    preferred_topics TEXT[] DEFAULT ARRAY[]::TEXT[],

    -- Content Characteristics
    min_score_threshold INTEGER DEFAULT 0,
    max_score_threshold INTEGER,
    preferred_content_length_min INTEGER,
    preferred_content_length_max INTEGER,

    -- Timing Preferences
    preferred_recency_hours INTEGER DEFAULT 24,  -- How recent content should be

    -- Engagement Preferences
    min_comments_threshold INTEGER DEFAULT 0,
    preferred_engagement_type VARCHAR(50),  -- 'high_score', 'high_comments', 'balanced'

    -- Learning Metadata
    total_feedback_count INTEGER DEFAULT 0,
    confidence_level DECIMAL(4,3) DEFAULT 0.0,  -- How confident we are in these preferences

    -- Timestamps
    last_updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),

    -- Ensure one preference profile per workspace
    UNIQUE(workspace_id)
);

-- =============================================================================
-- INDEXES
-- =============================================================================

-- Feedback Items indexes
CREATE INDEX idx_feedback_items_workspace_id ON feedback_items(workspace_id);
CREATE INDEX idx_feedback_items_user_id ON feedback_items(user_id);
CREATE INDEX idx_feedback_items_content_item_id ON feedback_items(content_item_id);
CREATE INDEX idx_feedback_items_newsletter_id ON feedback_items(newsletter_id);
CREATE INDEX idx_feedback_items_rating ON feedback_items(rating);
CREATE INDEX idx_feedback_items_created_at ON feedback_items(created_at DESC);
CREATE INDEX idx_feedback_items_workspace_rating ON feedback_items(workspace_id, rating);

-- Newsletter Feedback indexes
CREATE INDEX idx_newsletter_feedback_workspace_id ON newsletter_feedback(workspace_id);
CREATE INDEX idx_newsletter_feedback_user_id ON newsletter_feedback(user_id);
CREATE INDEX idx_newsletter_feedback_newsletter_id ON newsletter_feedback(newsletter_id);
CREATE INDEX idx_newsletter_feedback_overall_rating ON newsletter_feedback(overall_rating);
CREATE INDEX idx_newsletter_feedback_created_at ON newsletter_feedback(created_at DESC);

-- Source Quality Scores indexes
CREATE INDEX idx_source_quality_scores_workspace_id ON source_quality_scores(workspace_id);
CREATE INDEX idx_source_quality_scores_source_name ON source_quality_scores(source_name);
CREATE INDEX idx_source_quality_scores_quality_score ON source_quality_scores(quality_score DESC);
CREATE INDEX idx_source_quality_scores_workspace_source ON source_quality_scores(workspace_id, source_name);

-- Content Preferences indexes
CREATE INDEX idx_content_preferences_workspace_id ON content_preferences(workspace_id);

-- =============================================================================
-- ROW LEVEL SECURITY (RLS)
-- =============================================================================

ALTER TABLE feedback_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE newsletter_feedback ENABLE ROW LEVEL SECURITY;
ALTER TABLE source_quality_scores ENABLE ROW LEVEL SECURITY;
ALTER TABLE content_preferences ENABLE ROW LEVEL SECURITY;

-- Policies: Feedback Items
CREATE POLICY "Users can view their workspace feedback items"
    ON feedback_items FOR SELECT
    USING (
        workspace_id IN (
            SELECT workspace_id FROM user_workspaces
            WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "Users can insert feedback items for their workspaces"
    ON feedback_items FOR INSERT
    WITH CHECK (
        workspace_id IN (
            SELECT workspace_id FROM user_workspaces
            WHERE user_id = auth.uid()
        )
        AND user_id = auth.uid()
    );

CREATE POLICY "Users can update their own feedback items"
    ON feedback_items FOR UPDATE
    USING (
        user_id = auth.uid()
        AND workspace_id IN (
            SELECT workspace_id FROM user_workspaces
            WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "Users can delete their own feedback items"
    ON feedback_items FOR DELETE
    USING (
        user_id = auth.uid()
        AND workspace_id IN (
            SELECT workspace_id FROM user_workspaces
            WHERE user_id = auth.uid()
        )
    );

-- Policies: Newsletter Feedback
CREATE POLICY "Users can view their workspace newsletter feedback"
    ON newsletter_feedback FOR SELECT
    USING (
        workspace_id IN (
            SELECT workspace_id FROM user_workspaces
            WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "Users can insert newsletter feedback for their workspaces"
    ON newsletter_feedback FOR INSERT
    WITH CHECK (
        workspace_id IN (
            SELECT workspace_id FROM user_workspaces
            WHERE user_id = auth.uid()
        )
        AND user_id = auth.uid()
    );

CREATE POLICY "Users can update their own newsletter feedback"
    ON newsletter_feedback FOR UPDATE
    USING (
        user_id = auth.uid()
        AND workspace_id IN (
            SELECT workspace_id FROM user_workspaces
            WHERE user_id = auth.uid()
        )
    );

-- Policies: Source Quality Scores
CREATE POLICY "Users can view their workspace source quality scores"
    ON source_quality_scores FOR SELECT
    USING (
        workspace_id IN (
            SELECT workspace_id FROM user_workspaces
            WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "System can manage source quality scores"
    ON source_quality_scores FOR ALL
    USING (true)
    WITH CHECK (true);

-- Policies: Content Preferences
CREATE POLICY "Users can view their workspace content preferences"
    ON content_preferences FOR SELECT
    USING (
        workspace_id IN (
            SELECT workspace_id FROM user_workspaces
            WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "System can manage content preferences"
    ON content_preferences FOR ALL
    USING (true)
    WITH CHECK (true);

-- =============================================================================
-- TRIGGERS
-- =============================================================================

-- Trigger: Update updated_at timestamp for feedback_items
CREATE OR REPLACE FUNCTION update_feedback_items_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_feedback_items_updated_at
    BEFORE UPDATE ON feedback_items
    FOR EACH ROW
    EXECUTE FUNCTION update_feedback_items_updated_at();

-- Trigger: Update updated_at timestamp for newsletter_feedback
CREATE OR REPLACE FUNCTION update_newsletter_feedback_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_newsletter_feedback_updated_at
    BEFORE UPDATE ON newsletter_feedback
    FOR EACH ROW
    EXECUTE FUNCTION update_newsletter_feedback_updated_at();

-- Trigger: Update source quality scores when feedback is added/updated
CREATE OR REPLACE FUNCTION update_source_quality_scores_on_feedback()
RETURNS TRIGGER AS $$
DECLARE
    source_name_var VARCHAR(50);
BEGIN
    -- Get the source name from the content item
    SELECT source INTO source_name_var
    FROM content_items
    WHERE id = NEW.content_item_id;

    -- Update or insert source quality score
    INSERT INTO source_quality_scores (workspace_id, source_name, positive_count, negative_count, neutral_count, total_feedback_count, last_calculated_at)
    VALUES (
        NEW.workspace_id,
        source_name_var,
        CASE WHEN NEW.rating = 'positive' THEN 1 ELSE 0 END,
        CASE WHEN NEW.rating = 'negative' THEN 1 ELSE 0 END,
        CASE WHEN NEW.rating = 'neutral' THEN 1 ELSE 0 END,
        1,
        NOW()
    )
    ON CONFLICT (workspace_id, source_name)
    DO UPDATE SET
        positive_count = source_quality_scores.positive_count + CASE WHEN NEW.rating = 'positive' THEN 1 ELSE 0 END,
        negative_count = source_quality_scores.negative_count + CASE WHEN NEW.rating = 'negative' THEN 1 ELSE 0 END,
        neutral_count = source_quality_scores.neutral_count + CASE WHEN NEW.rating = 'neutral' THEN 1 ELSE 0 END,
        total_feedback_count = source_quality_scores.total_feedback_count + 1,
        quality_score = (
            (source_quality_scores.positive_count + CASE WHEN NEW.rating = 'positive' THEN 1 ELSE 0 END)::DECIMAL /
            (source_quality_scores.total_feedback_count + 1)::DECIMAL
        ),
        inclusion_rate = (
            SELECT
                COUNT(*) FILTER (WHERE included_in_final = true)::DECIMAL /
                COUNT(*)::DECIMAL
            FROM feedback_items
            WHERE workspace_id = NEW.workspace_id
            AND content_item_id IN (
                SELECT id FROM content_items WHERE source = source_name_var
            )
        ),
        last_calculated_at = NOW(),
        updated_at = NOW();

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_source_quality_scores
    AFTER INSERT OR UPDATE ON feedback_items
    FOR EACH ROW
    EXECUTE FUNCTION update_source_quality_scores_on_feedback();

-- =============================================================================
-- UTILITY FUNCTIONS
-- =============================================================================

-- Function: Recalculate source quality scores for a workspace
CREATE OR REPLACE FUNCTION recalculate_source_quality_scores(workspace_uuid UUID)
RETURNS INTEGER AS $$
DECLARE
    affected_count INTEGER := 0;
    source_record RECORD;
BEGIN
    -- Loop through all sources that have feedback
    FOR source_record IN (
        SELECT
            ci.source,
            COUNT(*) FILTER (WHERE fi.rating = 'positive') as pos_count,
            COUNT(*) FILTER (WHERE fi.rating = 'negative') as neg_count,
            COUNT(*) FILTER (WHERE fi.rating = 'neutral') as neu_count,
            COUNT(*) as total_count,
            AVG(CASE WHEN fi.included_in_final THEN 1.0 ELSE 0.0 END) as inc_rate,
            AVG(fi.edit_distance) as avg_edit
        FROM feedback_items fi
        JOIN content_items ci ON fi.content_item_id = ci.id
        WHERE fi.workspace_id = workspace_uuid
        GROUP BY ci.source
    ) LOOP
        -- Update or insert source quality score
        INSERT INTO source_quality_scores (
            workspace_id,
            source_name,
            quality_score,
            positive_count,
            negative_count,
            neutral_count,
            total_feedback_count,
            inclusion_rate,
            avg_edit_distance,
            last_calculated_at
        )
        VALUES (
            workspace_uuid,
            source_record.source,
            CASE
                WHEN source_record.total_count > 0
                THEN source_record.pos_count::DECIMAL / source_record.total_count::DECIMAL
                ELSE 0.5
            END,
            source_record.pos_count,
            source_record.neg_count,
            source_record.neu_count,
            source_record.total_count,
            COALESCE(source_record.inc_rate, 0.5),
            COALESCE(source_record.avg_edit, 0.0),
            NOW()
        )
        ON CONFLICT (workspace_id, source_name)
        DO UPDATE SET
            quality_score = EXCLUDED.quality_score,
            positive_count = EXCLUDED.positive_count,
            negative_count = EXCLUDED.negative_count,
            neutral_count = EXCLUDED.neutral_count,
            total_feedback_count = EXCLUDED.total_feedback_count,
            inclusion_rate = EXCLUDED.inclusion_rate,
            avg_edit_distance = EXCLUDED.avg_edit_distance,
            last_calculated_at = NOW(),
            updated_at = NOW();

        affected_count := affected_count + 1;
    END LOOP;

    RAISE NOTICE 'Recalculated quality scores for % sources', affected_count;
    RETURN affected_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function: Extract content preferences from feedback patterns
CREATE OR REPLACE FUNCTION extract_content_preferences(workspace_uuid UUID)
RETURNS UUID AS $$
DECLARE
    preferences_id UUID;
    preferred_sources_arr TEXT[];
    avoided_topics_arr TEXT[];
    preferred_topics_arr TEXT[];
    total_feedback INTEGER;
BEGIN
    -- Get total feedback count
    SELECT COUNT(*) INTO total_feedback
    FROM feedback_items
    WHERE workspace_id = workspace_uuid;

    -- Get preferred sources (quality score > 0.6)
    SELECT ARRAY_AGG(source_name ORDER BY quality_score DESC) INTO preferred_sources_arr
    FROM source_quality_scores
    WHERE workspace_id = workspace_uuid
    AND quality_score > 0.6;

    -- Insert or update content preferences
    INSERT INTO content_preferences (
        workspace_id,
        preferred_sources,
        avoided_topics,
        preferred_topics,
        total_feedback_count,
        confidence_level,
        last_updated_at
    )
    VALUES (
        workspace_uuid,
        COALESCE(preferred_sources_arr, ARRAY[]::TEXT[]),
        COALESCE(avoided_topics_arr, ARRAY[]::TEXT[]),
        COALESCE(preferred_topics_arr, ARRAY[]::TEXT[]),
        total_feedback,
        CASE
            WHEN total_feedback >= 50 THEN 0.9
            WHEN total_feedback >= 20 THEN 0.7
            WHEN total_feedback >= 10 THEN 0.5
            ELSE 0.3
        END,
        NOW()
    )
    ON CONFLICT (workspace_id)
    DO UPDATE SET
        preferred_sources = EXCLUDED.preferred_sources,
        avoided_topics = EXCLUDED.avoided_topics,
        preferred_topics = EXCLUDED.preferred_topics,
        total_feedback_count = EXCLUDED.total_feedback_count,
        confidence_level = EXCLUDED.confidence_level,
        last_updated_at = NOW()
    RETURNING id INTO preferences_id;

    RAISE NOTICE 'Extracted preferences for workspace % (confidence: %)',
        workspace_uuid,
        CASE
            WHEN total_feedback >= 50 THEN '90%'
            WHEN total_feedback >= 20 THEN '70%'
            WHEN total_feedback >= 10 THEN '50%'
            ELSE '30%'
        END;

    RETURN preferences_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function: Get feedback analytics summary
CREATE OR REPLACE FUNCTION get_feedback_analytics(
    workspace_uuid UUID,
    start_date TIMESTAMPTZ DEFAULT NULL,
    end_date TIMESTAMPTZ DEFAULT NULL
)
RETURNS JSON AS $$
DECLARE
    result JSON;
    start_date_val TIMESTAMPTZ;
    end_date_val TIMESTAMPTZ;
BEGIN
    -- Set default date range
    start_date_val := COALESCE(start_date, NOW() - INTERVAL '30 days');
    end_date_val := COALESCE(end_date, NOW());

    SELECT json_build_object(
        'total_feedback_items', (
            SELECT COUNT(*) FROM feedback_items
            WHERE workspace_id = workspace_uuid
            AND created_at BETWEEN start_date_val AND end_date_val
        ),
        'positive_count', (
            SELECT COUNT(*) FROM feedback_items
            WHERE workspace_id = workspace_uuid
            AND rating = 'positive'
            AND created_at BETWEEN start_date_val AND end_date_val
        ),
        'negative_count', (
            SELECT COUNT(*) FROM feedback_items
            WHERE workspace_id = workspace_uuid
            AND rating = 'negative'
            AND created_at BETWEEN start_date_val AND end_date_val
        ),
        'neutral_count', (
            SELECT COUNT(*) FROM feedback_items
            WHERE workspace_id = workspace_uuid
            AND rating = 'neutral'
            AND created_at BETWEEN start_date_val AND end_date_val
        ),
        'inclusion_rate', (
            SELECT
                CASE
                    WHEN COUNT(*) > 0
                    THEN COUNT(*) FILTER (WHERE included_in_final = true)::DECIMAL / COUNT(*)::DECIMAL
                    ELSE 0
                END
            FROM feedback_items
            WHERE workspace_id = workspace_uuid
            AND created_at BETWEEN start_date_val AND end_date_val
        ),
        'avg_newsletter_rating', (
            SELECT AVG(overall_rating)
            FROM newsletter_feedback
            WHERE workspace_id = workspace_uuid
            AND created_at BETWEEN start_date_val AND end_date_val
        ),
        'avg_time_to_finalize', (
            SELECT AVG(time_to_finalize_minutes)
            FROM newsletter_feedback
            WHERE workspace_id = workspace_uuid
            AND created_at BETWEEN start_date_val AND end_date_val
        ),
        'top_sources', (
            SELECT json_agg(
                json_build_object(
                    'source', source_name,
                    'quality_score', quality_score,
                    'feedback_count', total_feedback_count
                )
                ORDER BY quality_score DESC
            )
            FROM source_quality_scores
            WHERE workspace_id = workspace_uuid
            LIMIT 5
        ),
        'date_range', json_build_object(
            'start', start_date_val,
            'end', end_date_val
        )
    ) INTO result;

    RETURN result;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- =============================================================================
-- VERIFICATION
-- =============================================================================

DO $$
BEGIN
    IF EXISTS (SELECT FROM feedback_items LIMIT 1) THEN
        RAISE NOTICE 'Feedback items table created and has data';
    ELSE
        RAISE NOTICE 'Feedback items table created successfully (empty)';
    END IF;

    IF EXISTS (SELECT FROM newsletter_feedback LIMIT 1) THEN
        RAISE NOTICE 'Newsletter feedback table created and has data';
    ELSE
        RAISE NOTICE 'Newsletter feedback table created successfully (empty)';
    END IF;

    IF EXISTS (SELECT FROM source_quality_scores LIMIT 1) THEN
        RAISE NOTICE 'Source quality scores table created and has data';
    ELSE
        RAISE NOTICE 'Source quality scores table created successfully (empty)';
    END IF;

    IF EXISTS (SELECT FROM content_preferences LIMIT 1) THEN
        RAISE NOTICE 'Content preferences table created and has data';
    ELSE
        RAISE NOTICE 'Content preferences table created successfully (empty)';
    END IF;
END $$;

SELECT 'Migration 008 completed: feedback and learning tables created' AS status;
