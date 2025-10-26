-- =============================================================================
-- DEPLOYMENT SCRIPT: Fix Trends Creating Duplicates
-- =============================================================================
-- Description:
--   Complete deployment script that combines cleanup + migration 015.
--   Run this ONCE in Supabase SQL Editor to fix trend duplicates.
--
-- What this does:
--   1. Previews duplicate trends that will be deleted
--   2. Removes duplicate trends (keeps strongest/most recent)
--   3. Adds UNIQUE constraint to prevent future duplicates
--   4. Verifies constraint was created successfully
--
-- Author: AI Newsletter System
-- Date: 2025-01-25
-- Expected Duration: 5-10 seconds
-- =============================================================================

-- =============================================================================
-- STEP 1: Preview Duplicate Trends
-- =============================================================================
-- This shows which trends will be deleted (run preview only first!)

DO $$
DECLARE
    duplicate_count INTEGER;
BEGIN
    RAISE NOTICE '=============================================================================';
    RAISE NOTICE 'STEP 1: Checking for duplicate trends...';
    RAISE NOTICE '=============================================================================';

    SELECT COUNT(*) INTO duplicate_count
    FROM (
        SELECT workspace_id, topic, COUNT(*) as cnt
        FROM trends
        GROUP BY workspace_id, topic
        HAVING COUNT(*) > 1
    ) duplicates;

    IF duplicate_count > 0 THEN
        RAISE NOTICE 'Found % duplicate (workspace_id, topic) combinations', duplicate_count;
        RAISE NOTICE 'Preview of trends to be cleaned up:';
    ELSE
        RAISE NOTICE 'No duplicates found - database is clean!';
    END IF;
END $$;

-- Show details of duplicates (for your review)
SELECT
    workspace_id,
    topic,
    COUNT(*) as duplicate_count,
    ARRAY_AGG(id ORDER BY strength_score DESC, updated_at DESC) as all_trend_ids,
    (ARRAY_AGG(id ORDER BY strength_score DESC, updated_at DESC))[1] as trend_to_keep,
    MAX(strength_score) as best_strength,
    MAX(updated_at) as most_recent
FROM trends
WHERE is_active = true
GROUP BY workspace_id, topic
HAVING COUNT(*) > 1
ORDER BY workspace_id, topic;

-- =============================================================================
-- STEP 2: Remove Duplicate Trends
-- =============================================================================
-- Keeps only the strongest/most recent trend for each (workspace_id, topic)

DO $$
DECLARE
    deleted_count INTEGER;
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '=============================================================================';
    RAISE NOTICE 'STEP 2: Removing duplicate trends...';
    RAISE NOTICE '=============================================================================';

    -- Delete duplicates (keep strongest/most recent)
    WITH duplicates_to_keep AS (
        SELECT DISTINCT ON (workspace_id, topic)
            id
        FROM trends
        WHERE is_active = true
        ORDER BY workspace_id, topic, strength_score DESC, updated_at DESC
    ),
    duplicates_to_delete AS (
        SELECT t.id
        FROM trends t
        WHERE t.is_active = true
        AND t.id NOT IN (SELECT id FROM duplicates_to_keep)
        AND EXISTS (
            SELECT 1
            FROM trends t2
            WHERE t2.workspace_id = t.workspace_id
            AND t2.topic = t.topic
            AND t2.id != t.id
        )
    )
    DELETE FROM trends
    WHERE id IN (SELECT id FROM duplicates_to_delete);

    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RAISE NOTICE 'Deleted % duplicate trends', deleted_count;

    IF deleted_count = 0 THEN
        RAISE NOTICE 'No duplicates were found to delete';
    END IF;
END $$;

-- =============================================================================
-- STEP 3: Add UNIQUE Constraint
-- =============================================================================
-- Prevents future duplicates

DO $$
DECLARE
    constraint_exists BOOLEAN;
    duplicate_check INTEGER;
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '=============================================================================';
    RAISE NOTICE 'STEP 3: Adding UNIQUE constraint...';
    RAISE NOTICE '=============================================================================';

    -- Final check: Verify no duplicates remain
    SELECT COUNT(*) INTO duplicate_check
    FROM (
        SELECT workspace_id, topic, COUNT(*) as cnt
        FROM trends
        GROUP BY workspace_id, topic
        HAVING COUNT(*) > 1
    ) duplicates;

    IF duplicate_check > 0 THEN
        RAISE EXCEPTION
            'Migration blocked: % duplicate (workspace_id, topic) combinations still exist! Re-run cleanup step.',
            duplicate_check;
    END IF;

    -- Check if constraint already exists
    SELECT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'unique_workspace_topic'
        AND conrelid = 'trends'::regclass
    ) INTO constraint_exists;

    IF constraint_exists THEN
        RAISE NOTICE 'Constraint unique_workspace_topic already exists - skipping';
    ELSE
        -- Add UNIQUE constraint
        ALTER TABLE trends
        ADD CONSTRAINT unique_workspace_topic UNIQUE (workspace_id, topic);

        RAISE NOTICE 'Created UNIQUE constraint: unique_workspace_topic on (workspace_id, topic)';
    END IF;

    -- Add comment
    COMMENT ON CONSTRAINT unique_workspace_topic ON trends IS
    'Prevents duplicate trends for same topic within a workspace. Enables UPSERT operations (on_conflict=workspace_id,topic).';

END $$;

-- =============================================================================
-- STEP 4: Verification
-- =============================================================================

DO $$
DECLARE
    constraint_exists BOOLEAN;
    remaining_duplicates INTEGER;
    total_trends INTEGER;
    active_trends INTEGER;
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '=============================================================================';
    RAISE NOTICE 'STEP 4: Verifying deployment...';
    RAISE NOTICE '=============================================================================';

    -- Check constraint exists
    SELECT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'unique_workspace_topic'
        AND conrelid = 'trends'::regclass
    ) INTO constraint_exists;

    IF NOT constraint_exists THEN
        RAISE EXCEPTION 'FAILED: Constraint was not created';
    END IF;

    -- Check for remaining duplicates
    SELECT COUNT(*) INTO remaining_duplicates
    FROM (
        SELECT workspace_id, topic, COUNT(*) as cnt
        FROM trends
        GROUP BY workspace_id, topic
        HAVING COUNT(*) > 1
    ) duplicates;

    -- Get trend counts
    SELECT COUNT(*) INTO total_trends FROM trends;
    SELECT COUNT(*) INTO active_trends FROM trends WHERE is_active = true;

    -- Report results
    RAISE NOTICE '✅ Constraint exists: unique_workspace_topic';
    RAISE NOTICE '✅ Remaining duplicates: % (should be 0)', remaining_duplicates;
    RAISE NOTICE '✅ Total trends in database: %', total_trends;
    RAISE NOTICE '✅ Active trends: %', active_trends;

    IF remaining_duplicates = 0 AND constraint_exists THEN
        RAISE NOTICE '';
        RAISE NOTICE '=============================================================================';
        RAISE NOTICE '✅ SUCCESS: Deployment completed successfully!';
        RAISE NOTICE '=============================================================================';
        RAISE NOTICE 'What changed:';
        RAISE NOTICE '  - Removed duplicate trends (kept strongest/most recent)';
        RAISE NOTICE '  - Added UNIQUE constraint on (workspace_id, topic)';
        RAISE NOTICE '  - Future trend detection will UPSERT instead of creating duplicates';
        RAISE NOTICE '';
        RAISE NOTICE 'Next steps:';
        RAISE NOTICE '  1. Restart backend (to pick up scheduler fix)';
        RAISE NOTICE '  2. Test dashboard → Recent Activity should load without errors';
        RAISE NOTICE '  3. Run trend detection twice → Should not create duplicates';
    ELSE
        RAISE EXCEPTION 'FAILED: Verification failed (duplicates=%, constraint=%)',
            remaining_duplicates, constraint_exists;
    END IF;
END $$;

-- Final verification query (shows current state)
SELECT
    workspace_id,
    topic,
    COUNT(*) as count,
    MAX(strength_score) as strength,
    MAX(updated_at) as last_updated
FROM trends
WHERE is_active = true
GROUP BY workspace_id, topic
ORDER BY workspace_id, topic;

-- =============================================================================
-- End Deployment Script
-- =============================================================================
-- Status: ✅ Ready to run in Supabase SQL Editor
-- Expected Result: All duplicates removed, UNIQUE constraint added
-- Rollback: ALTER TABLE trends DROP CONSTRAINT IF EXISTS unique_workspace_topic;
-- =============================================================================
