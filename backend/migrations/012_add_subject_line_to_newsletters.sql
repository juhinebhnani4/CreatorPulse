-- =====================================================
-- Migration: Add subject_line column to newsletters table
-- Purpose: Store email subject line for newsletter delivery
-- Date: 2025-10-24
-- =====================================================
--
-- BACKGROUND:
-- The subject_line column is used for email delivery.
-- It's extracted from the newsletter's <h1> tag or falls back to title.
-- This is required for sending newsletters via SMTP/SendGrid.
--
-- CHANGES:
-- - Adds subject_line TEXT column (nullable)
-- - Sets default value for existing rows (copies from title)
-- - Refreshes Supabase schema cache
--
-- SAFETY:
-- - Uses IF NOT EXISTS (idempotent, safe to run multiple times)
-- - No data loss
-- - Backward compatible
-- =====================================================

-- Add subject_line column
ALTER TABLE newsletters ADD COLUMN IF NOT EXISTS subject_line TEXT;

-- Set default value for existing rows (use title as fallback)
UPDATE newsletters
SET subject_line = title
WHERE subject_line IS NULL;

-- Add comment for documentation
COMMENT ON COLUMN newsletters.subject_line IS 'Subject line for email delivery (extracted from h1 tag or title)';

-- Refresh Supabase PostgREST schema cache
-- This ensures the API recognizes the new column immediately
NOTIFY pgrst, 'reload schema';

-- Success message
SELECT 'SUCCESS: Added subject_line column to newsletters table!' AS result;
