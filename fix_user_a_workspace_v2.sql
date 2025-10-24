-- ============================================================================
-- Fix user_a@test.com - COMPLETE FIX (handles missing public.users entry)
-- Run this in Supabase SQL Editor
-- ============================================================================

-- STEP 1: First, let's find the actual user_id in public.users for user_a@test.com
DO $$
DECLARE
    actual_user_id UUID;
    new_workspace_id UUID;
BEGIN
    -- Try to find user in public.users by email
    SELECT id INTO actual_user_id
    FROM users
    WHERE email = 'user_a@test.com';

    -- Check if user exists
    IF actual_user_id IS NULL THEN
        RAISE EXCEPTION '❌ ERROR: user_a@test.com not found in public.users table!

This user needs to be created first. Possible solutions:
1. User needs to sign up again (recommended if using new backend code)
2. OR manually create the public.users entry (see fix_user_a_complete.sql)

To check if user exists in auth.users, go to:
Supabase Dashboard → Authentication → Users → Search for user_a@test.com';
    END IF;

    RAISE NOTICE '✓ Found user: % (email: user_a@test.com)', actual_user_id;

    -- Create workspace
    INSERT INTO workspaces (id, name, description, owner_id, created_at, updated_at)
    VALUES (
        gen_random_uuid(),
        'Hey You''s Workspace',
        'Your default workspace',
        actual_user_id,
        NOW(),
        NOW()
    )
    RETURNING id INTO new_workspace_id;

    RAISE NOTICE '✓ Created workspace: %', new_workspace_id;

    -- Add user to user_workspaces
    INSERT INTO user_workspaces (id, user_id, workspace_id, role, invited_at, accepted_at)
    VALUES (
        gen_random_uuid(),
        actual_user_id,
        new_workspace_id,
        'owner',
        NOW(),
        NOW()
    );

    RAISE NOTICE '✓ Added user to user_workspaces';

    -- Create workspace config
    INSERT INTO workspace_configs (id, workspace_id, config, version, created_at, updated_at, updated_by)
    VALUES (
        gen_random_uuid(),
        new_workspace_id,
        '{
            "sources": [],
            "generation": {
                "model": "openai",
                "temperature": 0.7,
                "tone": "professional",
                "language": "en",
                "max_items": 10
            },
            "delivery": {
                "method": "smtp",
                "from_name": "Hey You"
            }
        }'::jsonb,
        1,
        NOW(),
        NOW(),
        actual_user_id
    );

    RAISE NOTICE '✓ Created workspace config';
    RAISE NOTICE '';
    RAISE NOTICE '========================================';
    RAISE NOTICE '✅ SUCCESS: user_a@test.com now has workspace access';
    RAISE NOTICE '========================================';
END $$;

-- STEP 2: Verify the fix
SELECT
    u.email,
    u.username,
    w.name as workspace_name,
    w.id as workspace_id,
    uw.role,
    uw.accepted_at,
    wc.config->'sources' as sources_config
FROM users u
JOIN user_workspaces uw ON u.id = uw.user_id
JOIN workspaces w ON uw.workspace_id = w.id
LEFT JOIN workspace_configs wc ON wc.workspace_id = w.id
WHERE u.email = 'user_a@test.com';

-- Expected output: 1 row showing workspace association with role='owner'
