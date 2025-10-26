-- =============================================================================
-- Migration 019: Add Size Constraints for Arrays and JSONB (FIXED FOR JSONB)
-- =============================================================================
-- Description:
--   Adds CHECK constraints to prevent performance issues from oversized data:
--   - tags JSONB array limited to 50 items (prevents massive tag lists)
--   - metadata JSONB limited to 64KB (prevents huge JSON blobs)
--
--   FIXED: Updated to work with tags as JSONB (not TEXT[])
--
-- Author: Claude (IQ 165 Audit System)
-- Date: 2025-01-25 (Fixed: 2025-01-26)
-- Priority: P2 - MEDIUM (Performance & Data Quality)
-- =============================================================================

-- Step 1: Check current data for violations (FIXED FOR JSONB)
DO $$
DECLARE
    oversized_tags_count INTEGER;
    oversized_metadata_count INTEGER;
    max_tags_length INTEGER;
    max_metadata_size INTEGER;
    sample_large_tags RECORD;
    sample_large_metadata RECORD;
BEGIN
    -- Check tags JSONB array sizes (FIXED: use jsonb_array_length instead of array_length)
    SELECT
        COUNT(*) FILTER (WHERE jsonb_typeof(tags) = 'array' AND jsonb_array_length(tags) > 50) as oversized_count,
        MAX(CASE WHEN jsonb_typeof(tags) = 'array' THEN jsonb_array_length(tags) ELSE 0 END) as max_length
    INTO oversized_tags_count, max_tags_length
    FROM content_items
    WHERE tags IS NOT NULL;

    IF oversized_tags_count > 0 THEN
        RAISE NOTICE 'WARNING: Found % items with more than 50 tags! (Max: % tags)',
            oversized_tags_count, max_tags_length;

        -- Show sample
        FOR sample_large_tags IN
            SELECT id, title, source, jsonb_array_length(tags) as tag_count
            FROM content_items
            WHERE tags IS NOT NULL
              AND jsonb_typeof(tags) = 'array'
              AND jsonb_array_length(tags) > 50
            LIMIT 3
        LOOP
            RAISE NOTICE '  - ID: %, Title: "%.30", Source: %, Tags: %',
                sample_large_tags.id,
                sample_large_tags.title,
                sample_large_tags.source,
                sample_large_tags.tag_count;
        END LOOP;

        RAISE NOTICE 'To fix: UPDATE content_items SET tags = (tags->0) || ... (truncate to first 50 elements)';
    ELSE
        RAISE NOTICE 'OK: All items have 50 or fewer tags (Max: %)', COALESCE(max_tags_length, 0);
    END IF;

    -- Check metadata JSONB sizes
    SELECT
        COUNT(*) FILTER (WHERE pg_column_size(metadata) > 65536) as oversized_count,
        MAX(pg_column_size(metadata)) as max_size
    INTO oversized_metadata_count, max_metadata_size
    FROM content_items
    WHERE metadata IS NOT NULL;

    IF oversized_metadata_count > 0 THEN
        RAISE NOTICE 'WARNING: Found % items with metadata larger than 64KB! (Max: % bytes)',
            oversized_metadata_count, max_metadata_size;

        -- Show sample
        FOR sample_large_metadata IN
            SELECT
                id,
                title,
                source,
                pg_column_size(metadata) as metadata_size
            FROM content_items
            WHERE metadata IS NOT NULL AND pg_column_size(metadata) > 65536
            LIMIT 3
        LOOP
            RAISE NOTICE '  - ID: %, Title: "%.30", Source: %, Size: % KB',
                sample_large_metadata.id,
                sample_large_metadata.title,
                sample_large_metadata.source,
                (sample_large_metadata.metadata_size / 1024)::INTEGER;
        END LOOP;

        RAISE NOTICE 'Consider reducing metadata size or storing large data elsewhere (file storage, separate table).';
    ELSE
        RAISE NOTICE 'OK: All metadata is 64KB or smaller (Max: % KB)',
            COALESCE((max_metadata_size / 1024)::INTEGER, 0);
    END IF;
END $$;

-- Step 2: Add CHECK constraint for tags JSONB array length (FIXED FOR JSONB)
-- Handles three cases: NULL, non-array JSONB, or array with <= 50 elements
ALTER TABLE content_items
ADD CONSTRAINT valid_tags_array_size
CHECK (
    tags IS NULL
    OR jsonb_typeof(tags) != 'array'
    OR jsonb_array_length(tags) <= 50
);

-- Step 3: Add CHECK constraint for metadata JSONB size
-- Note: NULL is allowed, 64KB = 65536 bytes
ALTER TABLE content_items
ADD CONSTRAINT valid_metadata_size
CHECK (metadata IS NULL OR pg_column_size(metadata) <= 65536);

-- Step 4: Add helpful comments
COMMENT ON CONSTRAINT valid_tags_array_size ON content_items IS
'Limits tags JSONB array to maximum 50 items to prevent performance degradation.

Rationale:
- Large JSONB arrays slow down PostgreSQL operations (jsonb_array_elements, contains, etc.)
- 50 tags is generous for most content (typical: 3-10 tags)
- Prevents accidental data quality issues (e.g., blog scraper extracting 100+ category tags)

Note: This constraint works with JSONB arrays. If tags is not an array (e.g., null or object),
the constraint allows it (use application-level validation for data type enforcement).

If you need more than 50 tags, consider:
- Storing full tag list in metadata JSONB
- Creating separate content_tags junction table
- Filtering to most relevant tags during scraping

Added in migration 019. Fixed for JSONB on 2025-01-26.';

COMMENT ON CONSTRAINT valid_metadata_size ON content_items IS
'Limits metadata JSONB to maximum 64KB (65,536 bytes) to prevent performance issues.

Rationale:
- Large JSONB slows down serialization/deserialization
- Typical metadata is 1-5KB (tweet data, video stats, etc.)
- 64KB is generous (allows ~50-100 fields with moderate content)
- Prevents storing large binary data or full HTML in metadata

If you need to store more than 64KB:
- Move large data to file storage (S3, etc.) and store URL in metadata
- Create separate table for large structured data
- Compress data before storing

Size calculation: pg_column_size(metadata) includes JSONB overhead (~20-30% extra).

Added in migration 019.';

-- Verification query (FIXED FOR JSONB)
SELECT
    'Migration 019 Complete' as status,
    COUNT(*) as total_items,
    -- Tags statistics (FIXED: use jsonb_array_length)
    COUNT(tags) FILTER (WHERE tags IS NOT NULL AND jsonb_typeof(tags) = 'array') as items_with_tags,
    MAX(CASE WHEN jsonb_typeof(tags) = 'array' THEN jsonb_array_length(tags) ELSE 0 END) as max_tags_count,
    ROUND(AVG(CASE WHEN jsonb_typeof(tags) = 'array' THEN jsonb_array_length(tags) ELSE 0 END)) as avg_tags_count,
    -- Metadata statistics
    COUNT(metadata) FILTER (WHERE metadata IS NOT NULL) as items_with_metadata,
    MAX(pg_column_size(metadata)) as max_metadata_bytes,
    (MAX(pg_column_size(metadata)) / 1024)::INTEGER as max_metadata_kb,
    (AVG(pg_column_size(metadata)) FILTER (WHERE metadata IS NOT NULL))::INTEGER as avg_metadata_bytes
FROM content_items;

-- =============================================================================
-- End Migration 019
-- =============================================================================