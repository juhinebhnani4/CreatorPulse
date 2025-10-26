-- =============================================================================
-- Migration 015: Add UNIQUE Constraint to Prevent Duplicate Trends
-- =============================================================================
-- Description:
--   Adds UNIQUE constraint on (workspace_id, topic) to prevent duplicate trends.
--   This enables UPSERT operations and prevents duplicate topic detection.
--
-- IMPORTANT: Run cleanup_duplicate_trends.sql BEFORE this migration!
--
-- Author: AI Newsletter System
-- Date: 2025-01-24
-- =============================================================================

-- Prerequisite Check: Verify no duplicates exist
DO $$
DECLARE
    duplicate_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO duplicate_count
    FROM (
        SELECT workspace_id, topic, COUNT(*) as cnt
        FROM trends
        GROUP BY workspace_id, topic
        HAVING COUNT(*) > 1
    ) duplicates;

    IF duplicate_count > 0 THEN
        RAISE EXCEPTION
            'Migration blocked: % duplicate (workspace_id, topic) combinations found. Run cleanup_duplicate_trends.sql first!',
            duplicate_count;
    ELSE
        RAISE NOTICE 'Prerequisite check passed: No duplicates found';
    END IF;
END $$;

-- Add UNIQUE constraint
ALTER TABLE trends
ADD CONSTRAINT unique_workspace_topic UNIQUE (workspace_id, topic);

-- Add helpful comment
COMMENT ON CONSTRAINT unique_workspace_topic ON trends IS
'Prevents duplicate trends for same topic within a workspace. Enables UPSERT operations (on_conflict=workspace_id,topic).';

-- Verify constraint was created
DO $$
DECLARE
    constraint_exists BOOLEAN;
BEGIN
    SELECT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'unique_workspace_topic'
        AND conrelid = 'trends'::regclass
    ) INTO constraint_exists;

    IF constraint_exists THEN
        RAISE NOTICE 'SUCCESS: unique_workspace_topic constraint created';
    ELSE
        RAISE EXCEPTION 'FAILED: Constraint was not created';
    END IF;
END $$;

-- =============================================================================
-- Test the constraint (verify it blocks duplicates)
-- =============================================================================

-- This should fail if constraint is working:
-- INSERT INTO trends (workspace_id, topic, strength_score, mention_count, velocity)
-- VALUES (
--     (SELECT workspace_id FROM trends LIMIT 1),
--     (SELECT topic FROM trends LIMIT 1),
--     0.5, 10, 5.0
-- );
-- Expected error: duplicate key value violates unique constraint "unique_workspace_topic"

-- =============================================================================
-- Rollback Instructions (if needed)
-- =============================================================================

-- To rollback this migration (remove constraint):
-- ALTER TABLE trends DROP CONSTRAINT IF EXISTS unique_workspace_topic;

-- =============================================================================
-- End Migration 015
-- =============================================================================

SELECT 'Migration 015 completed: UNIQUE constraint added to trends table' AS status;
