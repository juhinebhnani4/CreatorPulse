-- ============================================================================
-- Fix ID mismatch for ssbrightaccessories@gmail.com
-- Run this in Supabase SQL Editor
-- ============================================================================

-- ISSUE: Public users table has ID 28240133... but auth/workspace tables use 0c279e58...
-- FIX: Update public.users to use the correct auth ID

-- Step 1: Verify the mismatch
SELECT
    'public.users' as table_name,
    id,
    email,
    username
FROM users
WHERE email = 'ssbrightaccessories@gmail.com'
UNION ALL
SELECT
    'workspaces.owner_id' as table_name,
    owner_id as id,
    null as email,
    null as username
FROM workspaces
WHERE owner_id::text LIKE '0c279e58%'
UNION ALL
SELECT
    'user_workspaces.user_id' as table_name,
    user_id as id,
    null as email,
    null as username
FROM user_workspaces
WHERE user_id::text LIKE '0c279e58%';

-- Step 2: Fix the ID in public.users
UPDATE users
SET id = '0c279e58-b522-406a-b8df-73b75309cdab'  -- Correct auth ID
WHERE email = 'ssbrightaccessories@gmail.com'
  AND id = '28240133-0d84-42ec-bb97-8a1428261bb0';  -- Current wrong ID

-- Step 3: Verify the fix - all IDs should match now
SELECT
    u.email,
    u.id as public_user_id,
    w.owner_id as workspace_owner_id,
    uw.user_id as user_workspace_id,
    CASE
        WHEN u.id = w.owner_id AND u.id = uw.user_id THEN '✅ ALL IDs MATCH'
        ELSE '❌ MISMATCH STILL EXISTS'
    END as status
FROM users u
LEFT JOIN workspaces w ON w.owner_id = u.id
LEFT JOIN user_workspaces uw ON uw.user_id = u.id
WHERE u.email = 'ssbrightaccessories@gmail.com';

-- Expected output: status = '✅ ALL IDs MATCH'
