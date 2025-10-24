-- =============================================================================
-- Cleanup Script: Remove Duplicate Trends (One-Time)
-- =============================================================================
-- Description:
--   Removes duplicate trends accumulated from multiple detection runs.
--   Keeps only the most recent and strongest trend for each unique topic name.
--
-- IMPORTANT: Run this BEFORE applying migration 013 and deploying decay model.
--
-- Strategy:
--   For each workspace + topic combination, keep the trend with:
--   1. Highest strength_score
--   2. If tied, most recent updated_at/created_at timestamp
--
-- Author: AI Newsletter System
-- Date: 2025-01-24
-- =============================================================================

-- Preview: See which trends will be deleted (run this first!)
SELECT
    workspace_id,
    topic,
    COUNT(*) as duplicate_count,
    ARRAY_AGG(id ORDER BY strength_score DESC, updated_at DESC) as all_trend_ids,
    ARRAY_AGG(id ORDER BY strength_score DESC, updated_at DESC)[1] as trend_to_keep
FROM trends
WHERE is_active = true
GROUP BY workspace_id, topic
HAVING COUNT(*) > 1;

-- Actual cleanup: Delete duplicate trends (keeps strongest/most recent)
-- Uncomment the DELETE statement below to execute

/*
DELETE FROM trends
WHERE id IN (
    SELECT t1.id
    FROM trends t1
    INNER JOIN (
        SELECT
            workspace_id,
            topic,
            MAX(strength_score) as max_strength,
            MAX(updated_at) as max_updated
        FROM trends
        WHERE is_active = true
        GROUP BY workspace_id, topic
        HAVING COUNT(*) > 1
    ) t2 ON t1.workspace_id = t2.workspace_id AND t1.topic = t2.topic
    WHERE NOT (
        t1.strength_score = t2.max_strength
        AND t1.updated_at = t2.max_updated
    )
);
*/

-- Alternative: Clean slate approach (deletes ALL trends, starts fresh)
-- Use this if you want to completely reset trend detection
-- Uncomment to execute:

/*
DELETE FROM trends WHERE workspace_id = 'YOUR_WORKSPACE_ID_HERE';
*/

-- Verify cleanup (should show 0 or 1 per topic)
SELECT
    workspace_id,
    topic,
    COUNT(*) as remaining_count,
    MAX(strength_score) as strength,
    MAX(updated_at) as last_updated
FROM trends
WHERE is_active = true
GROUP BY workspace_id, topic
ORDER BY workspace_id, topic;

-- =============================================================================
-- End Cleanup Script
-- =============================================================================
