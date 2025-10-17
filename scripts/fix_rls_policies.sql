-- Fix RLS Policy Infinite Recursion Issue
-- Run this in Supabase SQL Editor to fix the circular dependency

-- Drop the problematic policy
DROP POLICY IF EXISTS "Workspace owners can manage memberships" ON user_workspaces;

-- Recreate it to check owner_id directly from the workspaces table without circular reference
-- We need to use a different approach: owners can manage memberships if they own the workspace
CREATE POLICY "Workspace owners can manage memberships"
    ON user_workspaces FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM workspaces w
            WHERE w.id = user_workspaces.workspace_id
            AND w.owner_id = auth.uid()
        )
    );
