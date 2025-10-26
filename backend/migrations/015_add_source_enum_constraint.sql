-- Migration 015: Add CHECK constraint for source field enum values
-- Priority: P1 - HIGH (prevents invalid source types from being stored)
-- Date: 2025-01-25
-- Author: Claude (IQ 165 Audit System)
--
-- CRITICAL ISSUE #1: NO CHECK CONSTRAINTS ON ENUM FIELDS
-- Problem: source TEXT accepts ANY string, not limited to valid scraper types
-- Impact: Could store invalid source types ('twitter', 'tweeter', 'redd1t'), breaking frontend filters
-- Fix: Add CHECK constraint to enforce valid enum values

-- Step 1: Verify current data is valid (should all pass)
DO $$
DECLARE
    invalid_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO invalid_count
    FROM content_items
    WHERE source NOT IN ('reddit', 'rss', 'youtube', 'x', 'blog');

    IF invalid_count > 0 THEN
        RAISE NOTICE 'WARNING: Found % rows with invalid source values!', invalid_count;
        RAISE NOTICE 'Run this query to see them: SELECT DISTINCT source FROM content_items WHERE source NOT IN (''reddit'', ''rss'', ''youtube'', ''x'', ''blog'');';
        -- Don't fail, just warn - let admin decide how to handle
    ELSE
        RAISE NOTICE 'OK: All existing source values are valid';
    END IF;
END $$;

-- Step 2: Add CHECK constraint for valid source types
ALTER TABLE content_items
ADD CONSTRAINT valid_source_types
CHECK (source IN ('reddit', 'rss', 'youtube', 'x', 'blog'));

-- Step 3: Create index to optimize source filtering (already exists, but ensuring)
-- This is already present from migration 002, but good to document here
-- CREATE INDEX IF NOT EXISTS idx_content_source ON content_items(workspace_id, source);

-- Verification query
SELECT
    'Migration 015 Complete' as status,
    COUNT(*) as total_rows,
    COUNT(DISTINCT source) as distinct_sources,
    array_agg(DISTINCT source ORDER BY source) as sources_in_use
FROM content_items;

COMMENT ON CONSTRAINT valid_source_types ON content_items IS
'Enforces enum-like validation: source must be one of: reddit, rss, youtube, x, blog.
Added in migration 015 to prevent data quality issues (e.g., typos like "twitter" instead of "x").
Frontend filters and scrapers assume these exact values.';
