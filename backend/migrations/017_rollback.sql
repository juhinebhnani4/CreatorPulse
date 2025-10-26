-- =============================================================================
-- Migration 017 ROLLBACK: Remove Content Length CHECK Constraint
-- =============================================================================
-- Use this if migration 017 causes issues in production
-- Date: 2025-01-25
-- =============================================================================

-- Step 1: Verify constraint exists before trying to drop it
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'valid_content_length'
        AND conrelid = 'content_items'::regclass
    ) THEN
        -- Step 2: Drop the CHECK constraint
        ALTER TABLE content_items DROP CONSTRAINT valid_content_length;
        RAISE NOTICE 'OK: Constraint valid_content_length dropped successfully';
    ELSE
        RAISE NOTICE 'INFO: Constraint valid_content_length does not exist, nothing to rollback';
    END IF;
END $$;

-- Verification
SELECT 'Migration 017 ROLLBACK Complete' as status;

-- =============================================================================
-- End Migration 017 Rollback
-- =============================================================================
