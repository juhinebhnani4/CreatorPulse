-- Migration 015 ROLLBACK: Remove source enum CHECK constraint
-- Use this if migration 015 causes issues in production
-- Date: 2025-01-25

-- Step 1: Verify constraint exists before trying to drop it
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'valid_source_types'
        AND conrelid = 'content_items'::regclass
    ) THEN
        -- Step 2: Drop the CHECK constraint
        ALTER TABLE content_items DROP CONSTRAINT valid_source_types;
        RAISE NOTICE 'OK: Constraint valid_source_types dropped successfully';
    ELSE
        RAISE NOTICE 'INFO: Constraint valid_source_types does not exist, nothing to rollback';
    END IF;
END $$;

-- Verification
SELECT 'Migration 015 ROLLBACK Complete' as status;
