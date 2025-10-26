-- =============================================================================
-- Migration 020 ROLLBACK: Remove Analytics Indexes
-- =============================================================================
-- Use this if migration 020 causes issues in production
-- (e.g., indexes taking too long to build, disk space issues)
-- Date: 2025-01-25
-- =============================================================================

-- Drop all analytics indexes added in migration 020
DROP INDEX IF EXISTS idx_content_recent_items;
DROP INDEX IF EXISTS idx_content_source_recent;
DROP INDEX IF EXISTS idx_content_score_recent;
DROP INDEX IF EXISTS idx_content_date_range_analytics;
DROP INDEX IF EXISTS idx_content_library_composite;

-- Verification - Show remaining indexes on content_items
SELECT
    'Migration 020 ROLLBACK Complete' as status,
    COUNT(*) as remaining_indexes
FROM pg_indexes
WHERE tablename = 'content_items';

SELECT
    indexname,
    indexdef
FROM pg_indexes
WHERE tablename = 'content_items'
ORDER BY indexname;

-- =============================================================================
-- End Migration 020 Rollback
-- =============================================================================
