-- =============================================================================
-- Migration 016: Add Trend Status Field
-- =============================================================================
-- Description:
--   Adds 'status' column to trends table to track trend lifecycle.
--   Status values: emerging, rising, hot, peak, declining
--
--   Industry-standard 5-stage lifecycle model used by Twitter, Google Trends.
--
-- Author: AI Newsletter System
-- Date: 2025-01-25
-- =============================================================================

-- Add status column with DEFAULT and NOT NULL
ALTER TABLE trends
ADD COLUMN IF NOT EXISTS status VARCHAR(20) NOT NULL DEFAULT 'emerging'
CHECK (status IN ('emerging', 'rising', 'hot', 'peak', 'declining'));

-- Create index for status queries (speeds up filtering by status)
CREATE INDEX IF NOT EXISTS idx_trends_status
ON trends(workspace_id, status);

-- Create composite index for common query pattern (active trends sorted by strength)
CREATE INDEX IF NOT EXISTS idx_trends_active_strength_status
ON trends(workspace_id, is_active, strength_score DESC, status)
WHERE is_active = true;

-- Backfill existing trends with computed status based on current strength_score
-- Uses simple strength-based classification (will be refined by backend percentile logic)
UPDATE trends
SET status = CASE
    WHEN strength_score >= 0.9 THEN 'peak'
    WHEN strength_score >= 0.75 THEN 'hot'
    WHEN strength_score >= 0.6 THEN 'rising'
    ELSE 'emerging'
END
WHERE status = 'emerging';  -- Only update rows that still have default value

-- Add helpful comment
COMMENT ON COLUMN trends.status IS
'Trend lifecycle status computed by backend:
- emerging: New or weak trend (strength < 60%)
- rising: Growing trend with momentum (60-75%)
- hot: Viral trend with high engagement (75-90%)
- peak: Saturated trend at maximum strength (90%+)
- declining: Fading trend losing momentum (backend computes based on velocity)';

COMMENT ON INDEX idx_trends_status IS
'Speeds up queries filtering trends by status (e.g., showing only "hot" trends)';

COMMENT ON INDEX idx_trends_active_strength_status IS
'Optimizes common query: active trends sorted by strength with status filter';

-- =============================================================================
-- End Migration 016
-- =============================================================================
