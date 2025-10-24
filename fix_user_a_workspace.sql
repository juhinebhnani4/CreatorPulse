-- ============================================================================
-- Fix user_a@test.com - Create workspace and grant access
-- Run this in Supabase SQL Editor
-- ============================================================================

-- Step 1: Create workspace for user_a@test.com
DO $$
DECLARE
    new_workspace_id UUID;
    user_a_id UUID := 'f215f33b-f355-43df-82f9-b41e1bd1c072';
BEGIN
    -- Create workspace
    INSERT INTO workspaces (id, name, description, owner_id, created_at, updated_at)
    VALUES (
        gen_random_uuid(),
        'Hey You''s Workspace',
        'Your default workspace',
        user_a_id,
        NOW(),
        NOW()
    )
    RETURNING id INTO new_workspace_id;

    RAISE NOTICE 'Created workspace: %', new_workspace_id;

    -- Add user to user_workspaces
    INSERT INTO user_workspaces (id, user_id, workspace_id, role, invited_at, accepted_at)
    VALUES (
        gen_random_uuid(),
        user_a_id,
        new_workspace_id,
        'owner',
        NOW(),
        NOW()
    );

    RAISE NOTICE 'Added user to user_workspaces';

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
        user_a_id
    );

    RAISE NOTICE 'Created workspace config';
    RAISE NOTICE 'SUCCESS: user_a@test.com now has workspace access';
END $$;

-- Step 2: Verify the fix
SELECT
    u.email,
    u.username,
    w.name as workspace_name,
    w.id as workspace_id,
    uw.role,
    uw.accepted_at,
    wc.config->'sources' as sources_count
FROM users u
JOIN user_workspaces uw ON u.id = uw.user_id
JOIN workspaces w ON uw.workspace_id = w.id
LEFT JOIN workspace_configs wc ON wc.workspace_id = w.id
WHERE u.email = 'user_a@test.com';

-- Expected output: 1 row showing workspace association with role='owner'
