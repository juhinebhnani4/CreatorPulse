-- Migration: Add unique constraint to prevent duplicate content
-- Description: Prevents the same content from being saved multiple times when scraping runs repeatedly
-- Date: 2025-01-20

-- Step 1: Remove existing duplicates (keep only the first occurrence of each unique content)
-- This uses a CTE to identify duplicates and delete all but the earliest one
WITH duplicates AS (
  SELECT
    id,
    ROW_NUMBER() OVER (
      PARTITION BY workspace_id, source, source_url
      ORDER BY scraped_at ASC
    ) as row_num
  FROM content_items
)
DELETE FROM content_items
WHERE id IN (
  SELECT id FROM duplicates WHERE row_num > 1
);

-- Step 2: Add unique constraint to prevent future duplicates
-- This ensures that each unique content item (identified by workspace + source + URL)
-- can only appear once in the database
ALTER TABLE content_items
ADD CONSTRAINT unique_content_per_workspace
UNIQUE (workspace_id, source, source_url);

-- Step 3: Add index to improve query performance on the unique constraint
CREATE INDEX IF NOT EXISTS idx_content_unique
ON content_items (workspace_id, source, source_url);

-- Note: If this migration fails due to existing duplicates, you may need to:
-- 1. Manually review and clean duplicate content
-- 2. Run the DELETE query separately first
-- 3. Then run the ALTER TABLE to add the constraint
