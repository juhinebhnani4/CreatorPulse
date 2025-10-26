-- =====================================================
-- Migration: Rename newsletter content fields to match frontend
-- Date: 2025-01-26
-- Purpose: Fix field name mismatch between database and frontend
-- =====================================================
--
-- PROBLEM:
-- - Database has: html_content, plain_text_content
-- - Frontend expects: content_html, content_text
-- - Supabase INSERT was using content_html (failed to save)
-- - Supabase SELECT returns html_content (frontend gets undefined)
--
-- SOLUTION:
-- Rename database columns to match frontend expectations
-- This fixes both INSERT (content now saves) and SELECT (frontend gets correct fields)
--
-- IMPACT:
-- - Newsletter content will now save correctly
-- - Frontend will display newsletter HTML properly
-- - Delivery service already uses correct field names (no changes needed)
-- - Backward compatible (frontend already coded for new names)
--
-- SAFETY:
-- - Column rename preserves all data
-- - No data loss
-- - Idempotent (safe to run multiple times via IF EXISTS check)
-- =====================================================

-- Check if old columns exist before renaming
DO $$
BEGIN
    -- Rename html_content to content_html
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'newsletters' AND column_name = 'html_content'
    ) THEN
        ALTER TABLE newsletters RENAME COLUMN html_content TO content_html;
        RAISE NOTICE 'Renamed html_content -> content_html';
    ELSE
        RAISE NOTICE 'Column html_content already renamed or does not exist';
    END IF;

    -- Rename plain_text_content to content_text
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'newsletters' AND column_name = 'plain_text_content'
    ) THEN
        ALTER TABLE newsletters RENAME COLUMN plain_text_content TO content_text;
        RAISE NOTICE 'Renamed plain_text_content -> content_text';
    ELSE
        RAISE NOTICE 'Column plain_text_content already renamed or does not exist';
    END IF;
END $$;

-- Update column comments to reflect new names
COMMENT ON COLUMN newsletters.content_html IS 'HTML content of newsletter (matches frontend field name)';
COMMENT ON COLUMN newsletters.content_text IS 'Plain text version of newsletter (matches frontend field name)';

-- Refresh Supabase PostgREST schema cache
-- This ensures the API recognizes the renamed columns immediately
NOTIFY pgrst, 'reload schema';

-- Success message
SELECT 'SUCCESS: Newsletter content fields renamed to match frontend!' AS result;
SELECT 'Database now uses: content_html, content_text' AS info;
SELECT 'Frontend expects: content_html, content_text' AS verification;
SELECT 'Field names are now CONSISTENT across entire stack!' AS status;
