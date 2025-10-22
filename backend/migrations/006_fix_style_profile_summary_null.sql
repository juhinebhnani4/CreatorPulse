-- Migration 006 Fix: Fix get_style_profile_summary to return false instead of NULL for uses_emojis
-- Purpose: Fix Pydantic validation error when workspace has no style profile
-- Issue: BOOL_OR() returns NULL when there are no rows, but Pydantic expects boolean
-- Fix: Use COALESCE to return false instead of NULL

-- Drop and recreate the function with the fix
CREATE OR REPLACE FUNCTION get_style_profile_summary(workspace_uuid UUID)
RETURNS JSONB AS $$
DECLARE
    profile_summary JSONB;
BEGIN
    SELECT jsonb_build_object(
        'has_profile', COUNT(*) > 0,
        'trained_on_count', COALESCE(MAX(trained_on_count), 0),
        'tone', MAX(tone),
        'formality_level', MAX(formality_level),
        'uses_emojis', COALESCE(BOOL_OR(uses_emojis), false),  -- FIX: Return false instead of NULL
        'last_updated', MAX(updated_at)
    )
    INTO profile_summary
    FROM style_profiles
    WHERE workspace_id = workspace_uuid;

    RETURN profile_summary;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

SELECT 'Migration 006 Fix completed: get_style_profile_summary now returns false instead of NULL for uses_emojis' AS status;
