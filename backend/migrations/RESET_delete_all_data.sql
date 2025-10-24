-- ==========================================
-- COMPLETE DATABASE RESET SCRIPT
-- ==========================================
-- WARNING: This script deletes ALL data (including users) from the database
-- while preserving the table structure.
--
-- USE CASE: Fresh development reset, testing, or complete data wipe
--
-- SAFETY: Wrapped in a transaction - will rollback if any errors occur
--
-- EXECUTION: Run this in Supabase SQL Editor
--
-- LAST UPDATED: 2025-01-24
-- ==========================================

BEGIN;

-- ==========================================
-- STEP 1: Delete child tables (no dependencies)
-- ==========================================

-- Analytics events (tracking data)
DELETE FROM email_analytics_events;
SELECT 'Deleted ' || COUNT(*) || ' email analytics events' AS result FROM email_analytics_events;

-- Scheduler executions (job history)
DELETE FROM scheduler_executions;
SELECT 'Deleted ' || COUNT(*) || ' scheduler executions' AS result FROM scheduler_executions;

-- Feedback items (content feedback)
DELETE FROM feedback_items;
SELECT 'Deleted ' || COUNT(*) || ' feedback items' AS result FROM feedback_items;

-- Newsletter feedback
DELETE FROM newsletter_feedback;
SELECT 'Deleted ' || COUNT(*) || ' newsletter feedback' AS result FROM newsletter_feedback;

-- ==========================================
-- STEP 2: Delete parent tables with dependencies
-- ==========================================

-- Content performance (references content_items)
DELETE FROM content_performance;
SELECT 'Deleted ' || COUNT(*) || ' content performance records' AS result FROM content_performance;

-- Newsletter analytics summary (references newsletters)
DELETE FROM newsletter_analytics_summary;
SELECT 'Deleted ' || COUNT(*) || ' newsletter analytics summaries' AS result FROM newsletter_analytics_summary;

-- Newsletters (referenced by analytics, feedback)
DELETE FROM newsletters;
SELECT 'Deleted ' || COUNT(*) || ' newsletters' AS result FROM newsletters;

-- Content items (referenced by feedback, analytics)
DELETE FROM content_items;
SELECT 'Deleted ' || COUNT(*) || ' content items' AS result FROM content_items;

-- Subscribers (referenced by analytics)
DELETE FROM subscribers;
SELECT 'Deleted ' || COUNT(*) || ' subscribers' AS result FROM subscribers;

-- Scheduler jobs (referenced by scheduler_executions)
DELETE FROM scheduler_jobs;
SELECT 'Deleted ' || COUNT(*) || ' scheduler jobs' AS result FROM scheduler_jobs;

-- Trends
DELETE FROM trends;
SELECT 'Deleted ' || COUNT(*) || ' trends' AS result FROM trends;

-- Style profiles
DELETE FROM style_profiles;
SELECT 'Deleted ' || COUNT(*) || ' style profiles' AS result FROM style_profiles;

-- Source quality scores (feedback-derived)
DELETE FROM source_quality_scores;
SELECT 'Deleted ' || COUNT(*) || ' source quality scores' AS result FROM source_quality_scores;

-- Content preferences (feedback-derived)
DELETE FROM content_preferences;
SELECT 'Deleted ' || COUNT(*) || ' content preferences' AS result FROM content_preferences;

-- ==========================================
-- STEP 3: Delete workspace-related data
-- ==========================================

-- Workspace configurations
DELETE FROM workspace_configs;
SELECT 'Deleted ' || COUNT(*) || ' workspace configs' AS result FROM workspace_configs;

-- User-workspace memberships
DELETE FROM user_workspaces;
SELECT 'Deleted ' || COUNT(*) || ' user-workspace memberships' AS result FROM user_workspaces;

-- Workspaces (parent of almost everything)
DELETE FROM workspaces;
SELECT 'Deleted ' || COUNT(*) || ' workspaces' AS result FROM workspaces;

-- ==========================================
-- STEP 4: Delete users
-- ==========================================

-- Public user profiles (custom table)
DELETE FROM public.users;
SELECT 'Deleted ' || COUNT(*) || ' user profiles (public.users)' AS result FROM public.users;

-- Authentication users (Supabase Auth)
-- NOTE: This requires service_role privileges in Supabase
DELETE FROM auth.users;
SELECT 'Deleted ' || COUNT(*) || ' auth users (auth.users)' AS result FROM auth.users;

-- ==========================================
-- STEP 5: Reset sequences (optional - for clean IDs on next inserts)
-- ==========================================
-- Note: Only needed if any tables use SERIAL/BIGSERIAL instead of UUIDs
-- CreatorPulse uses UUIDs everywhere, so this section is informational only

-- Example (if you had serial IDs):
-- ALTER SEQUENCE workspaces_id_seq RESTART WITH 1;

-- ==========================================
-- FINAL VERIFICATION
-- ==========================================

SELECT
    'DATABASE RESET COMPLETE' AS status,
    (SELECT COUNT(*) FROM auth.users) AS remaining_users,
    (SELECT COUNT(*) FROM workspaces) AS remaining_workspaces,
    (SELECT COUNT(*) FROM content_items) AS remaining_content_items,
    (SELECT COUNT(*) FROM newsletters) AS remaining_newsletters,
    (SELECT COUNT(*) FROM subscribers) AS remaining_subscribers;

-- ==========================================
-- COMMIT TRANSACTION
-- ==========================================
-- If you see any errors above, run ROLLBACK; instead of COMMIT;
-- Otherwise, run COMMIT; to make changes permanent

COMMIT;

-- ==========================================
-- POST-EXECUTION NOTES
-- ==========================================
-- 1. All data has been deleted
-- 2. All table structures remain intact
-- 3. All indexes, constraints, and RLS policies are preserved
-- 4. You can now:
--    - Re-register users via /api/v1/auth/signup
--    - Create new workspaces
--    - Start fresh with clean data
--
-- 5. To verify cleanup:
--    SELECT table_name, (xpath('/row/cnt/text()',
--           query_to_xml(format('SELECT COUNT(*) AS cnt FROM %I', table_name), false, true, '')))[1]::text::int AS row_count
--    FROM information_schema.tables
--    WHERE table_schema = 'public'
--    ORDER BY table_name;
-- ==========================================
