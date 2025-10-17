-- Migration 009: Create Analytics & Email Tracking Tables
-- Purpose: Track email engagement metrics (opens, clicks, bounces)
-- Features:
--   - Email event tracking (sent, opened, clicked, bounced, unsubscribed)
--   - Newsletter analytics summary with calculated metrics
--   - Content item performance tracking
--   - Real-time analytics via triggers
--   - Privacy-compliant tracking (GDPR/CAN-SPAM)
-- Relations: Many-to-one with workspaces, newsletters, subscribers, content_items

-- =============================================================================
-- DROP EXISTING (if re-running)
-- =============================================================================

DROP TABLE IF EXISTS email_analytics_events CASCADE;
DROP TABLE IF EXISTS newsletter_analytics_summary CASCADE;
DROP TABLE IF EXISTS content_performance CASCADE;

-- =============================================================================
-- CREATE TABLE: email_analytics_events
-- =============================================================================

CREATE TABLE email_analytics_events (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Foreign Keys
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    newsletter_id UUID NOT NULL REFERENCES newsletters(id) ON DELETE CASCADE,
    subscriber_id UUID REFERENCES subscribers(id) ON DELETE SET NULL,

    -- Event Details
    event_type VARCHAR(20) NOT NULL CHECK (event_type IN ('sent', 'delivered', 'opened', 'clicked', 'bounced', 'unsubscribed', 'spam_reported')),
    event_time TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Recipient
    recipient_email VARCHAR(255) NOT NULL,

    -- Click Tracking (for event_type = 'clicked')
    clicked_url TEXT,
    content_item_id UUID REFERENCES content_items(id) ON DELETE SET NULL,

    -- Bounce Details (for event_type = 'bounced')
    bounce_type VARCHAR(20) CHECK (bounce_type IN ('hard', 'soft', NULL)),
    bounce_reason TEXT,

    -- Context & User Agent Data
    user_agent TEXT,
    ip_address VARCHAR(45),  -- Supports IPv6
    location_city VARCHAR(100),
    location_country VARCHAR(100),
    device_type VARCHAR(50),  -- 'mobile', 'desktop', 'tablet', 'other'
    email_client VARCHAR(100),  -- 'Gmail', 'Outlook', 'Apple Mail', etc.

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================================================
-- CREATE TABLE: newsletter_analytics_summary
-- =============================================================================

CREATE TABLE newsletter_analytics_summary (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Foreign Keys
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    newsletter_id UUID NOT NULL REFERENCES newsletters(id) ON DELETE CASCADE,

    -- Delivery Metrics
    sent_count INTEGER DEFAULT 0,
    delivered_count INTEGER DEFAULT 0,
    bounced_count INTEGER DEFAULT 0,
    hard_bounces INTEGER DEFAULT 0,
    soft_bounces INTEGER DEFAULT 0,

    -- Engagement Metrics
    opened_count INTEGER DEFAULT 0,  -- Total opens (can be > unique_opens if same person opens multiple times)
    unique_opens INTEGER DEFAULT 0,  -- Distinct recipients who opened
    clicked_count INTEGER DEFAULT 0,  -- Total clicks
    unique_clicks INTEGER DEFAULT 0,  -- Distinct recipients who clicked

    -- Negative Metrics
    unsubscribed_count INTEGER DEFAULT 0,
    spam_reported_count INTEGER DEFAULT 0,

    -- Calculated Rates
    delivery_rate DECIMAL(5,4) DEFAULT 0.0,  -- delivered / sent
    open_rate DECIMAL(5,4) DEFAULT 0.0,  -- unique_opens / delivered
    click_rate DECIMAL(5,4) DEFAULT 0.0,  -- unique_clicks / delivered
    click_to_open_rate DECIMAL(5,4) DEFAULT 0.0,  -- unique_clicks / unique_opens
    bounce_rate DECIMAL(5,4) DEFAULT 0.0,  -- bounced / sent
    unsubscribe_rate DECIMAL(5,4) DEFAULT 0.0,  -- unsubscribed / delivered

    -- Engagement Score (composite metric)
    engagement_score DECIMAL(4,3) DEFAULT 0.0,  -- Weighted: 0.4*open + 0.5*click + 0.1*CTOR

    -- Timing Analytics
    avg_time_to_open_seconds INTEGER,  -- Average time from sent to first open
    avg_time_to_click_seconds INTEGER,  -- Average time from sent to first click

    -- Best Performing Times
    peak_open_hour INTEGER,  -- Hour (0-23) with most opens
    peak_click_hour INTEGER,  -- Hour (0-23) with most clicks

    -- Metadata
    last_calculated_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Ensure one summary per newsletter
    UNIQUE(newsletter_id)
);

-- =============================================================================
-- CREATE TABLE: content_performance
-- =============================================================================

CREATE TABLE content_performance (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Foreign Keys
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    content_item_id UUID NOT NULL REFERENCES content_items(id) ON DELETE CASCADE,

    -- Inclusion Metrics
    times_included INTEGER DEFAULT 0,  -- How many newsletters included this content
    times_clicked INTEGER DEFAULT 0,  -- Total clicks on this content across all newsletters
    unique_clickers INTEGER DEFAULT 0,  -- Unique recipients who clicked

    -- Performance
    avg_click_rate DECIMAL(5,4) DEFAULT 0.0,  -- Average CTR when included
    engagement_score DECIMAL(4,3) DEFAULT 0.0,  -- Quality score based on performance

    -- Newsletter-specific tracking (JSON array)
    newsletter_performances JSONB DEFAULT '[]'::jsonb,  -- [{"newsletter_id": "uuid", "clicks": 10, "ctr": 0.05}]

    -- Metadata
    first_included_at TIMESTAMPTZ,
    last_included_at TIMESTAMPTZ,
    last_calculated_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Ensure one performance record per content item per workspace
    UNIQUE(workspace_id, content_item_id)
);

-- =============================================================================
-- INDEXES
-- =============================================================================

-- Email Analytics Events indexes
CREATE INDEX idx_email_events_workspace_id ON email_analytics_events(workspace_id);
CREATE INDEX idx_email_events_newsletter_id ON email_analytics_events(newsletter_id);
CREATE INDEX idx_email_events_subscriber_id ON email_analytics_events(subscriber_id);
CREATE INDEX idx_email_events_event_type ON email_analytics_events(event_type);
CREATE INDEX idx_email_events_event_time ON email_analytics_events(event_time DESC);
CREATE INDEX idx_email_events_recipient ON email_analytics_events(recipient_email);
CREATE INDEX idx_email_events_content_item ON email_analytics_events(content_item_id);

-- Composite indexes for common queries
CREATE INDEX idx_email_events_newsletter_recipient ON email_analytics_events(newsletter_id, recipient_email);
CREATE INDEX idx_email_events_newsletter_event_type ON email_analytics_events(newsletter_id, event_type);
CREATE INDEX idx_email_events_workspace_event_time ON email_analytics_events(workspace_id, event_time DESC);

-- Newsletter Analytics Summary indexes
CREATE INDEX idx_newsletter_summary_workspace_id ON newsletter_analytics_summary(workspace_id);
CREATE INDEX idx_newsletter_summary_newsletter_id ON newsletter_analytics_summary(newsletter_id);
CREATE INDEX idx_newsletter_summary_engagement_score ON newsletter_analytics_summary(engagement_score DESC);
CREATE INDEX idx_newsletter_summary_open_rate ON newsletter_analytics_summary(open_rate DESC);

-- Content Performance indexes
CREATE INDEX idx_content_performance_workspace_id ON content_performance(workspace_id);
CREATE INDEX idx_content_performance_content_item_id ON content_performance(content_item_id);
CREATE INDEX idx_content_performance_engagement_score ON content_performance(engagement_score DESC);

-- =============================================================================
-- ROW LEVEL SECURITY (RLS)
-- =============================================================================

ALTER TABLE email_analytics_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE newsletter_analytics_summary ENABLE ROW LEVEL SECURITY;
ALTER TABLE content_performance ENABLE ROW LEVEL SECURITY;

-- Policies: Email Analytics Events
CREATE POLICY "Users can view analytics events for their workspaces"
    ON email_analytics_events FOR SELECT
    USING (
        workspace_id IN (
            SELECT workspace_id FROM user_workspaces
            WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "System can insert analytics events"
    ON email_analytics_events FOR INSERT
    WITH CHECK (true);  -- Allow tracking system to insert events

CREATE POLICY "Users can delete analytics events for their workspaces"
    ON email_analytics_events FOR DELETE
    USING (
        workspace_id IN (
            SELECT workspace_id FROM user_workspaces
            WHERE user_id = auth.uid()
        )
    );

-- Policies: Newsletter Analytics Summary
CREATE POLICY "Users can view newsletter analytics for their workspaces"
    ON newsletter_analytics_summary FOR SELECT
    USING (
        workspace_id IN (
            SELECT workspace_id FROM user_workspaces
            WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "System can manage newsletter analytics"
    ON newsletter_analytics_summary FOR ALL
    USING (true)
    WITH CHECK (true);

-- Policies: Content Performance
CREATE POLICY "Users can view content performance for their workspaces"
    ON content_performance FOR SELECT
    USING (
        workspace_id IN (
            SELECT workspace_id FROM user_workspaces
            WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "System can manage content performance"
    ON content_performance FOR ALL
    USING (true)
    WITH CHECK (true);

-- =============================================================================
-- TRIGGERS
-- =============================================================================

-- Trigger: Update updated_at timestamp for newsletter_analytics_summary
CREATE OR REPLACE FUNCTION update_newsletter_summary_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_newsletter_summary_updated_at
    BEFORE UPDATE ON newsletter_analytics_summary
    FOR EACH ROW
    EXECUTE FUNCTION update_newsletter_summary_updated_at();

-- Trigger: Update analytics summary on new event
CREATE OR REPLACE FUNCTION update_analytics_summary_on_event()
RETURNS TRIGGER AS $$
DECLARE
    sent_time TIMESTAMPTZ;
    time_diff_seconds INTEGER;
BEGIN
    -- Ensure summary record exists
    INSERT INTO newsletter_analytics_summary (workspace_id, newsletter_id)
    VALUES (NEW.workspace_id, NEW.newsletter_id)
    ON CONFLICT (newsletter_id) DO NOTHING;

    -- Update based on event type
    IF NEW.event_type = 'sent' THEN
        UPDATE newsletter_analytics_summary
        SET sent_count = sent_count + 1,
            last_calculated_at = NOW()
        WHERE newsletter_id = NEW.newsletter_id;

    ELSIF NEW.event_type = 'delivered' THEN
        UPDATE newsletter_analytics_summary
        SET delivered_count = delivered_count + 1,
            delivery_rate = (delivered_count + 1)::DECIMAL / NULLIF(sent_count, 0),
            last_calculated_at = NOW()
        WHERE newsletter_id = NEW.newsletter_id;

    ELSIF NEW.event_type = 'opened' THEN
        -- Calculate time to open
        SELECT event_time INTO sent_time
        FROM email_analytics_events
        WHERE newsletter_id = NEW.newsletter_id
        AND recipient_email = NEW.recipient_email
        AND event_type = 'sent'
        LIMIT 1;

        IF sent_time IS NOT NULL THEN
            time_diff_seconds := EXTRACT(EPOCH FROM (NEW.event_time - sent_time))::INTEGER;
        END IF;

        UPDATE newsletter_analytics_summary
        SET opened_count = opened_count + 1,
            unique_opens = (
                SELECT COUNT(DISTINCT recipient_email)
                FROM email_analytics_events
                WHERE newsletter_id = NEW.newsletter_id
                AND event_type = 'opened'
            ),
            avg_time_to_open_seconds = (
                COALESCE(avg_time_to_open_seconds, 0) * (opened_count) + COALESCE(time_diff_seconds, 0)
            ) / (opened_count + 1),
            open_rate = (
                SELECT COUNT(DISTINCT recipient_email)::DECIMAL
                FROM email_analytics_events
                WHERE newsletter_id = NEW.newsletter_id
                AND event_type = 'opened'
            ) / NULLIF(delivered_count, 0),
            last_calculated_at = NOW()
        WHERE newsletter_id = NEW.newsletter_id;

    ELSIF NEW.event_type = 'clicked' THEN
        -- Calculate time to click
        SELECT event_time INTO sent_time
        FROM email_analytics_events
        WHERE newsletter_id = NEW.newsletter_id
        AND recipient_email = NEW.recipient_email
        AND event_type = 'sent'
        LIMIT 1;

        IF sent_time IS NOT NULL THEN
            time_diff_seconds := EXTRACT(EPOCH FROM (NEW.event_time - sent_time))::INTEGER;
        END IF;

        UPDATE newsletter_analytics_summary
        SET clicked_count = clicked_count + 1,
            unique_clicks = (
                SELECT COUNT(DISTINCT recipient_email)
                FROM email_analytics_events
                WHERE newsletter_id = NEW.newsletter_id
                AND event_type = 'clicked'
            ),
            avg_time_to_click_seconds = (
                COALESCE(avg_time_to_click_seconds, 0) * (clicked_count) + COALESCE(time_diff_seconds, 0)
            ) / (clicked_count + 1),
            click_rate = (
                SELECT COUNT(DISTINCT recipient_email)::DECIMAL
                FROM email_analytics_events
                WHERE newsletter_id = NEW.newsletter_id
                AND event_type = 'clicked'
            ) / NULLIF(delivered_count, 0),
            click_to_open_rate = (
                SELECT COUNT(DISTINCT recipient_email)::DECIMAL
                FROM email_analytics_events
                WHERE newsletter_id = NEW.newsletter_id
                AND event_type = 'clicked'
            ) / NULLIF((
                SELECT COUNT(DISTINCT recipient_email)
                FROM email_analytics_events
                WHERE newsletter_id = NEW.newsletter_id
                AND event_type = 'opened'
            ), 0),
            last_calculated_at = NOW()
        WHERE newsletter_id = NEW.newsletter_id;

        -- Update content performance if content_item_id is present
        IF NEW.content_item_id IS NOT NULL THEN
            INSERT INTO content_performance (workspace_id, content_item_id, times_clicked, unique_clickers)
            VALUES (
                NEW.workspace_id,
                NEW.content_item_id,
                1,
                1
            )
            ON CONFLICT (workspace_id, content_item_id)
            DO UPDATE SET
                times_clicked = content_performance.times_clicked + 1,
                unique_clickers = (
                    SELECT COUNT(DISTINCT recipient_email)
                    FROM email_analytics_events
                    WHERE content_item_id = NEW.content_item_id
                    AND event_type = 'clicked'
                ),
                last_calculated_at = NOW();
        END IF;

    ELSIF NEW.event_type = 'bounced' THEN
        UPDATE newsletter_analytics_summary
        SET bounced_count = bounced_count + 1,
            hard_bounces = CASE WHEN NEW.bounce_type = 'hard' THEN hard_bounces + 1 ELSE hard_bounces END,
            soft_bounces = CASE WHEN NEW.bounce_type = 'soft' THEN soft_bounces + 1 ELSE soft_bounces END,
            bounce_rate = (bounced_count + 1)::DECIMAL / NULLIF(sent_count, 0),
            last_calculated_at = NOW()
        WHERE newsletter_id = NEW.newsletter_id;

    ELSIF NEW.event_type = 'unsubscribed' THEN
        UPDATE newsletter_analytics_summary
        SET unsubscribed_count = unsubscribed_count + 1,
            unsubscribe_rate = (unsubscribed_count + 1)::DECIMAL / NULLIF(delivered_count, 0),
            last_calculated_at = NOW()
        WHERE newsletter_id = NEW.newsletter_id;

    ELSIF NEW.event_type = 'spam_reported' THEN
        UPDATE newsletter_analytics_summary
        SET spam_reported_count = spam_reported_count + 1,
            last_calculated_at = NOW()
        WHERE newsletter_id = NEW.newsletter_id;
    END IF;

    -- Recalculate engagement score
    UPDATE newsletter_analytics_summary
    SET engagement_score = (
        COALESCE(open_rate, 0) * 0.4 +
        COALESCE(click_rate, 0) * 0.5 +
        COALESCE(click_to_open_rate, 0) * 0.1
    )
    WHERE newsletter_id = NEW.newsletter_id;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_analytics_summary
    AFTER INSERT ON email_analytics_events
    FOR EACH ROW
    EXECUTE FUNCTION update_analytics_summary_on_event();

-- =============================================================================
-- UTILITY FUNCTIONS
-- =============================================================================

-- Function: Recalculate analytics summary for a newsletter
CREATE OR REPLACE FUNCTION recalculate_newsletter_analytics(newsletter_uuid UUID)
RETURNS VOID AS $$
BEGIN
    -- Delete existing summary
    DELETE FROM newsletter_analytics_summary WHERE newsletter_id = newsletter_uuid;

    -- Replay all events to rebuild summary
    PERFORM update_analytics_summary_on_event()
    FROM email_analytics_events
    WHERE newsletter_id = newsletter_uuid
    ORDER BY event_time ASC;

    RAISE NOTICE 'Recalculated analytics for newsletter %', newsletter_uuid;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function: Get workspace analytics summary
CREATE OR REPLACE FUNCTION get_workspace_analytics_summary(
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
        'workspace_id', workspace_uuid,
        'date_range', json_build_object(
            'start', start_date_val,
            'end', end_date_val
        ),
        'total_newsletters', (
            SELECT COUNT(DISTINCT newsletter_id)
            FROM email_analytics_events
            WHERE workspace_id = workspace_uuid
            AND event_time BETWEEN start_date_val AND end_date_val
        ),
        'total_sent', (
            SELECT COUNT(*)
            FROM email_analytics_events
            WHERE workspace_id = workspace_uuid
            AND event_type = 'sent'
            AND event_time BETWEEN start_date_val AND end_date_val
        ),
        'total_delivered', (
            SELECT COUNT(*)
            FROM email_analytics_events
            WHERE workspace_id = workspace_uuid
            AND event_type = 'delivered'
            AND event_time BETWEEN start_date_val AND end_date_val
        ),
        'total_opened', (
            SELECT COUNT(DISTINCT newsletter_id || ':' || recipient_email)
            FROM email_analytics_events
            WHERE workspace_id = workspace_uuid
            AND event_type = 'opened'
            AND event_time BETWEEN start_date_val AND end_date_val
        ),
        'total_clicked', (
            SELECT COUNT(DISTINCT newsletter_id || ':' || recipient_email)
            FROM email_analytics_events
            WHERE workspace_id = workspace_uuid
            AND event_type = 'clicked'
            AND event_time BETWEEN start_date_val AND end_date_val
        ),
        'avg_open_rate', (
            SELECT AVG(open_rate)
            FROM newsletter_analytics_summary
            WHERE workspace_id = workspace_uuid
        ),
        'avg_click_rate', (
            SELECT AVG(click_rate)
            FROM newsletter_analytics_summary
            WHERE workspace_id = workspace_uuid
        ),
        'avg_engagement_score', (
            SELECT AVG(engagement_score)
            FROM newsletter_analytics_summary
            WHERE workspace_id = workspace_uuid
        ),
        'top_performing_content', (
            SELECT json_agg(
                json_build_object(
                    'content_item_id', content_item_id,
                    'clicks', times_clicked,
                    'engagement_score', engagement_score
                )
                ORDER BY engagement_score DESC
            )
            FROM content_performance
            WHERE workspace_id = workspace_uuid
            LIMIT 10
        )
    ) INTO result;

    RETURN result;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function: Anonymize old analytics data (privacy compliance)
CREATE OR REPLACE FUNCTION anonymize_old_analytics_data(days_old INTEGER DEFAULT 365)
RETURNS INTEGER AS $$
DECLARE
    affected_rows INTEGER;
BEGIN
    -- Anonymize email addresses and IP addresses older than specified days
    UPDATE email_analytics_events
    SET recipient_email = 'anonymized_' || LEFT(MD5(recipient_email), 8) || '@example.com',
        ip_address = NULL,
        location_city = NULL,
        user_agent = NULL
    WHERE event_time < NOW() - (days_old || ' days')::INTERVAL
    AND recipient_email NOT LIKE 'anonymized_%';

    GET DIAGNOSTICS affected_rows = ROW_COUNT;

    RAISE NOTICE 'Anonymized % old analytics records', affected_rows;
    RETURN affected_rows;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- =============================================================================
-- VERIFICATION
-- =============================================================================

DO $$
BEGIN
    IF EXISTS (SELECT FROM email_analytics_events LIMIT 1) THEN
        RAISE NOTICE 'Email analytics events table created and has data';
    ELSE
        RAISE NOTICE 'Email analytics events table created successfully (empty)';
    END IF;

    IF EXISTS (SELECT FROM newsletter_analytics_summary LIMIT 1) THEN
        RAISE NOTICE 'Newsletter analytics summary table created and has data';
    ELSE
        RAISE NOTICE 'Newsletter analytics summary table created successfully (empty)';
    END IF;

    IF EXISTS (SELECT FROM content_performance LIMIT 1) THEN
        RAISE NOTICE 'Content performance table created and has data';
    ELSE
        RAISE NOTICE 'Content performance table created successfully (empty)';
    END IF;
END $$;

SELECT 'Migration 009 completed: analytics and email tracking tables created' AS status;
