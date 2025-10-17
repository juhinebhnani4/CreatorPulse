-- Fix newsletters table schema
-- Add missing column if it doesn't exist

-- Add content_items_count column if missing
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = 'newsletters'
        AND column_name = 'content_items_count'
    ) THEN
        ALTER TABLE newsletters
        ADD COLUMN content_items_count INTEGER DEFAULT 0;

        COMMENT ON COLUMN newsletters.content_items_count
        IS 'Number of content items included in this newsletter';
    END IF;
END $$;

-- Refresh Supabase schema cache
NOTIFY pgrst, 'reload schema';
