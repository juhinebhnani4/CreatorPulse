-- =====================================================
-- Complete fix for newsletters table
-- Adds all missing columns that should exist according to schema
-- Safe to run multiple times (uses IF NOT EXISTS)
-- =====================================================

-- Add content_items_count
ALTER TABLE newsletters ADD COLUMN IF NOT EXISTS content_items_count INTEGER DEFAULT 0;
COMMENT ON COLUMN newsletters.content_items_count IS 'Number of content items included in this newsletter';

-- Add content_item_ids
ALTER TABLE newsletters ADD COLUMN IF NOT EXISTS content_item_ids UUID[] DEFAULT '{}';
COMMENT ON COLUMN newsletters.content_item_ids IS 'Array of content_item IDs that were used to generate this newsletter';

-- Add model_used
ALTER TABLE newsletters ADD COLUMN IF NOT EXISTS model_used TEXT;
COMMENT ON COLUMN newsletters.model_used IS 'AI model used (gpt-4, claude-3-sonnet, etc.)';

-- Add temperature
ALTER TABLE newsletters ADD COLUMN IF NOT EXISTS temperature REAL;
COMMENT ON COLUMN newsletters.temperature IS 'Temperature parameter used for generation';

-- Add tone
ALTER TABLE newsletters ADD COLUMN IF NOT EXISTS tone TEXT;
COMMENT ON COLUMN newsletters.tone IS 'Tone of the newsletter (professional, casual, etc.)';

-- Add language
ALTER TABLE newsletters ADD COLUMN IF NOT EXISTS language TEXT;
COMMENT ON COLUMN newsletters.language IS 'Language of the newsletter (en, es, fr, etc.)';

-- Add metadata
ALTER TABLE newsletters ADD COLUMN IF NOT EXISTS metadata JSONB DEFAULT '{}';
COMMENT ON COLUMN newsletters.metadata IS 'Additional metadata for the newsletter';

-- Add html_content
ALTER TABLE newsletters ADD COLUMN IF NOT EXISTS html_content TEXT DEFAULT '';
COMMENT ON COLUMN newsletters.html_content IS 'HTML content of the newsletter';

-- Add plain_text_content
ALTER TABLE newsletters ADD COLUMN IF NOT EXISTS plain_text_content TEXT;
COMMENT ON COLUMN newsletters.plain_text_content IS 'Plain text version of the newsletter';

-- Add title
ALTER TABLE newsletters ADD COLUMN IF NOT EXISTS title TEXT DEFAULT 'Newsletter';
COMMENT ON COLUMN newsletters.title IS 'Title of the newsletter';

-- Add status
ALTER TABLE newsletters ADD COLUMN IF NOT EXISTS status TEXT DEFAULT 'draft';
COMMENT ON COLUMN newsletters.status IS 'Newsletter status: draft, sent, scheduled';

-- Add generated_at
ALTER TABLE newsletters ADD COLUMN IF NOT EXISTS generated_at TIMESTAMPTZ DEFAULT NOW();
COMMENT ON COLUMN newsletters.generated_at IS 'When the newsletter was generated';

-- Add sent_at
ALTER TABLE newsletters ADD COLUMN IF NOT EXISTS sent_at TIMESTAMPTZ;
COMMENT ON COLUMN newsletters.sent_at IS 'When the newsletter was sent';

-- Refresh Supabase PostgREST schema cache
NOTIFY pgrst, 'reload schema';

-- Success message
SELECT 'SUCCESS: All columns added to newsletters table!' AS result;
