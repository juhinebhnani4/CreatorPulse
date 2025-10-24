-- =============================================================================
-- Migration 013: Add Trend Lifecycle Tracking Fields
-- =============================================================================
-- Description:
--   Adds optional lifecycle tracking fields to support trend decay model:
--   - last_boosted_at: Timestamp when trend was re-detected and strength boosted
--   - times_resurfaced: Counter for how many times trend re-appeared after decay
--
--   Also adds performance indexes for faster trend matching during upsert.
--
-- Author: AI Newsletter System
-- Date: 2025-01-24
-- =============================================================================

-- Add lifecycle tracking columns
ALTER TABLE trends
ADD COLUMN IF NOT EXISTS last_boosted_at TIMESTAMPTZ,
ADD COLUMN IF NOT EXISTS times_resurfaced INTEGER DEFAULT 0;

-- Add performance indexes for trend matching
-- (speeds up _find_matching_existing_trend method)
CREATE INDEX IF NOT EXISTS idx_trends_workspace_topic
ON trends(workspace_id, topic);

CREATE INDEX IF NOT EXISTS idx_trends_workspace_active
ON trends(workspace_id, is_active);

CREATE INDEX IF NOT EXISTS idx_trends_workspace_strength
ON trends(workspace_id, strength_score DESC)
WHERE is_active = true;

-- Add helpful comments
COMMENT ON COLUMN trends.last_boosted_at IS
'Last time this trend was re-detected and strength score was boosted (for "trending up" detection)';

COMMENT ON COLUMN trends.times_resurfaced IS
'Number of times this trend re-appeared after decay (detects recurring topics)';

COMMENT ON INDEX idx_trends_workspace_topic IS
'Speeds up trend name matching during upsert operations';

COMMENT ON INDEX idx_trends_workspace_active IS
'Speeds up active trend queries during decay aging process';

COMMENT ON INDEX idx_trends_workspace_strength IS
'Speeds up fetching top active trends sorted by strength';

-- =============================================================================
-- End Migration 013
-- =============================================================================
