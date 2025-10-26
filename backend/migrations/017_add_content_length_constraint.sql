-- =============================================================================
-- Migration 017: Add Content Length CHECK Constraint
-- =============================================================================
-- Description:
--   Adds CHECK constraint to enforce minimum content length of 100 characters.
--   This prevents invalid items from bypassing validation and being stored.
--
--   CRITICAL ISSUE #2 from Audit: Database allows NULL or ANY length content,
--   but scraper validation requires 100+ chars. This creates validation bypass
--   risk if save_content_items() is called directly.
--
-- Author: Claude (IQ 165 Audit System)
-- Date: 2025-01-25
-- Priority: P2 - MEDIUM
-- =============================================================================

-- Step 1: Check current data for violations
DO $$
DECLARE
    invalid_count INTEGER;
    sample_invalid RECORD;
BEGIN
    -- Count items with content < 100 chars (excluding NULL which is allowed)
    SELECT COUNT(*) INTO invalid_count
    FROM content_items
    WHERE content IS NOT NULL AND LENGTH(content) < 100;

    IF invalid_count > 0 THEN
        RAISE NOTICE 'WARNING: Found % rows with content shorter than 100 characters!', invalid_count;

        -- Show sample of invalid items for debugging
        FOR sample_invalid IN
            SELECT id, title, source, LENGTH(content) as content_len
            FROM content_items
            WHERE content IS NOT NULL AND LENGTH(content) < 100
            LIMIT 5
        LOOP
            RAISE NOTICE '  - ID: %, Title: "%.30", Source: %, Length: %',
                sample_invalid.id,
                sample_invalid.title,
                sample_invalid.source,
                sample_invalid.content_len;
        END LOOP;

        RAISE NOTICE 'These items will need to be fixed or deleted before adding constraint.';
        RAISE NOTICE 'To fix: UPDATE content_items SET content = NULL WHERE content IS NOT NULL AND LENGTH(content) < 100;';
        -- Don't fail, let admin decide
    ELSE
        RAISE NOTICE 'OK: All existing content items meet 100-character minimum (or are NULL)';
    END IF;
END $$;

-- Step 2: Add CHECK constraint for minimum content length
-- Note: NULL is allowed (some items may not have full content, only summary)
ALTER TABLE content_items
ADD CONSTRAINT valid_content_length
CHECK (content IS NULL OR LENGTH(content) >= 100);

-- Step 3: Add helpful comment
COMMENT ON CONSTRAINT valid_content_length ON content_items IS
'Enforces minimum content length of 100 characters (or NULL).
This matches the validation logic in BaseScraper.validate_item() and prevents
invalid items from being saved if validation is bypassed.

NULL content is allowed for items that have only a summary (e.g., tweet-length content).
Added in migration 017 as part of P2 fixes from comprehensive audit.';

-- Verification query
SELECT
    'Migration 017 Complete' as status,
    COUNT(*) as total_items,
    COUNT(content) as items_with_content,
    COUNT(*) FILTER (WHERE content IS NULL) as items_null_content,
    MIN(LENGTH(content)) FILTER (WHERE content IS NOT NULL) as min_content_length,
    AVG(LENGTH(content)) FILTER (WHERE content IS NOT NULL)::INTEGER as avg_content_length
FROM content_items;

-- =============================================================================
-- End Migration 017
-- =============================================================================
