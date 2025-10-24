-- ============================================================================
-- Diagnose user_a@test.com issue
-- Run this in Supabase SQL Editor to understand the problem
-- ============================================================================

-- Step 1: Check if user exists in public.users table
SELECT
    'public.users' as table_name,
    id,
    email,
    username,
    created_at
FROM users
WHERE email = 'user_a@test.com';

-- Step 2: Check if user exists in auth.users (Supabase Auth)
-- Note: You may need to use Supabase Dashboard > Authentication > Users to check this
-- Or run this if you have access:
-- SELECT id, email, created_at FROM auth.users WHERE email = 'user_a@test.com';

-- Step 3: List ALL users in public.users to find the correct ID
SELECT
    id,
    email,
    username,
    created_at
FROM users
ORDER BY created_at DESC
LIMIT 10;

-- Step 4: Check for orphaned auth.users (in auth table but not in public.users)
-- This requires cross-schema query - may not work depending on permissions
SELECT
    au.id as auth_id,
    au.email as auth_email,
    au.created_at as auth_created,
    pu.id as public_id,
    pu.email as public_email,
    CASE
        WHEN pu.id IS NULL THEN '❌ ORPHANED (auth exists, public missing)'
        WHEN au.id != pu.id THEN '⚠️ ID MISMATCH'
        ELSE '✅ OK'
    END as status
FROM auth.users au
LEFT JOIN public.users pu ON au.email = pu.email
WHERE au.email IN ('user_a@test.com', 'juhinebhnani4@gmail.com', 'ssbrightaccessories@gmail.com')
ORDER BY au.created_at DESC;
