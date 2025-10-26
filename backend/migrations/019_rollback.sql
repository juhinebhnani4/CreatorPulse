-- =============================================================================
-- Migration 019 ROLLBACK: Remove Size Constraints
-- =============================================================================
-- Use this if migration 019 causes issues in production
-- Date: 2025-01-25
-- =============================================================================

-- Step 1: Drop tags array size constraint
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'valid_tags_array_size'
        AND conrelid = 'content_items'::regclass
    ) THEN
        ALTER TABLE content_items DROP CONSTRAINT valid_tags_array_size;
        RAISE NOTICE 'OK: Constraint valid_tags_array_size dropped successfully';
    ELSE
        RAISE NOTICE 'INFO: Constraint valid_tags_array_size does not exist';
    END IF;
END $$;

-- Step 2: Drop metadata JSONB size constraint
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'valid_metadata_size'
        AND conrelid = 'content_items'::regclass
    ) THEN
        ALTER TABLE content_items DROP CONSTRAINT valid_metadata_size;
        RAISE NOTICE 'OK: Constraint valid_metadata_size dropped successfully';
    ELSE
        RAISE NOTICE 'INFO: Constraint valid_metadata_size does not exist';
    END IF;
END $$;

-- Verification
SELECT 'Migration 019 ROLLBACK Complete' as status;

-- =============================================================================
-- End Migration 019 Rollback
-- =============================================================================
