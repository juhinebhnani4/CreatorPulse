-- ========================================
-- FIX: Newsletter table column names
-- ========================================
-- The code uses content_html/content_text but the table has html_content/plain_text_content
-- This SQL adds the columns the code expects

-- Add content_html (the column the code is actually using)
ALTER TABLE newsletters ADD COLUMN IF NOT EXISTS content_html TEXT DEFAULT '';

-- Add content_text (the column the code is actually using)
ALTER TABLE newsletters ADD COLUMN IF NOT EXISTS content_text TEXT;

-- Add other missing columns
ALTER TABLE newsletters ADD COLUMN IF NOT EXISTS content_items_count INTEGER DEFAULT 0;
ALTER TABLE newsletters ADD COLUMN IF NOT EXISTS content_item_ids UUID[] DEFAULT '{}';
ALTER TABLE newsletters ADD COLUMN IF NOT EXISTS model_used TEXT;
ALTER TABLE newsletters ADD COLUMN IF NOT EXISTS temperature REAL;
ALTER TABLE newsletters ADD COLUMN IF NOT EXISTS tone TEXT;
ALTER TABLE newsletters ADD COLUMN IF NOT EXISTS language TEXT;
ALTER TABLE newsletters ADD COLUMN IF NOT EXISTS metadata JSONB DEFAULT '{}';
ALTER TABLE newsletters ADD COLUMN IF NOT EXISTS title TEXT DEFAULT 'Newsletter';
ALTER TABLE newsletters ADD COLUMN IF NOT EXISTS status TEXT DEFAULT 'draft';
ALTER TABLE newsletters ADD COLUMN IF NOT EXISTS generated_at TIMESTAMPTZ DEFAULT NOW();
ALTER TABLE newsletters ADD COLUMN IF NOT EXISTS sent_at TIMESTAMPTZ;

-- Success message
SELECT 'All newsletter columns added successfully!' AS result;
