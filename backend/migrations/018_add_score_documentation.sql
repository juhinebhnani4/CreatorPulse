-- =============================================================================
-- Migration 018: Add Score Field Documentation
-- =============================================================================
-- Description:
--   Adds documentation comment to content_items.score column to clarify that
--   negative scores are VALID and intentional (e.g., Reddit downvotes, negative
--   engagement metrics from some platforms).
--
--   This is NOT a schema change, just documentation to prevent confusion.
--
-- Author: Claude (IQ 165 Audit System)
-- Date: 2025-01-25
-- Priority: P2 - MEDIUM (Documentation only)
-- =============================================================================

-- Add comprehensive comment explaining score field behavior
COMMENT ON COLUMN content_items.score IS
'Engagement score for content item. Can be POSITIVE, NEGATIVE, or NULL.

Examples:
- Reddit: Net upvotes/downvotes (can be negative if heavily downvoted)
- X/Twitter: Likes + Retweets*2 + Replies*3 (usually positive, but could be 0)
- RSS/Blog: Usually NULL or 0 (no engagement data available)
- YouTube: View count or like count (always positive)

NULL vs 0:
- NULL = No score data available (e.g., RSS feed without engagement metrics)
- 0 = Score is explicitly zero (e.g., new post with no engagement yet)
- Negative = More downvotes than upvotes (Reddit) or other negative signals

Frontend Display:
- Show negative scores as-is (don''t hide them)
- Use NULL as fallback for sorting (treat as 0 or exclude from "trending")
- Color-code: green (positive), gray (zero), red (negative)

Technical Notes:
- Type: INTEGER (PostgreSQL signed int32, range: -2,147,483,648 to 2,147,483,647)
- Default: 0 (set in migration 002)
- NOT NULL: No (NULL is allowed)
- Added in migration 002, documented in migration 018';

-- Verification query - show score distribution
SELECT
    'Migration 018 Complete (Documentation Only)' as status,
    COUNT(*) as total_items,
    COUNT(score) FILTER (WHERE score > 0) as positive_scores,
    COUNT(score) FILTER (WHERE score = 0) as zero_scores,
    COUNT(score) FILTER (WHERE score < 0) as negative_scores,
    COUNT(*) FILTER (WHERE score IS NULL) as null_scores,
    MIN(score) as min_score,
    MAX(score) as max_score,
    AVG(score)::INTEGER as avg_score
FROM content_items;

-- =============================================================================
-- End Migration 018
-- =============================================================================
