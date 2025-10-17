-- Simplest Fix: Remove circular dependency completely
-- The key insight: When INSERTING a workspace, we don't need to check user_workspaces
-- We only need owner_id check

-- =============================================================================
-- STEP 1: Clean slate - drop all policies
-- =============================================================================

DROP POLICY IF EXISTS "Users can view their workspaces" ON workspaces;
DROP POLICY IF EXISTS "Owners can view their workspaces" ON workspaces;
DROP POLICY IF EXISTS "Members can view workspaces" ON workspaces;
DROP POLICY IF EXISTS "Owners can update their workspaces" ON workspaces;
DROP POLICY IF EXISTS "Users can create workspaces" ON workspaces;
DROP POLICY IF EXISTS "Owners can delete their workspaces" ON workspaces;

DROP POLICY IF EXISTS "Users can view their memberships" ON user_workspaces;
DROP POLICY IF EXISTS "Workspace owners can manage memberships" ON user_workspaces;

-- =============================================================================
-- STEP 2: Recreate workspaces policies (NO references to user_workspaces for now)
-- =============================================================================

-- Simple approach: Only owner can see/manage their workspace
-- We'll add member access later through a function
CREATE POLICY "workspace_owner_all"
    ON workspaces FOR ALL
    USING (owner_id = auth.uid())
    WITH CHECK (owner_id = auth.uid());

-- =============================================================================
-- STEP 3: Recreate user_workspaces policies
-- =============================================================================

-- Users can see their own memberships
CREATE POLICY "user_workspace_select"
    ON user_workspaces FOR SELECT
    USING (user_id = auth.uid());

-- Owners can insert/update/delete memberships for their workspaces
CREATE POLICY "user_workspace_owner_manage"
    ON user_workspaces FOR ALL
    USING (
        workspace_id IN (
            SELECT id FROM workspaces WHERE owner_id = auth.uid()
        )
    )
    WITH CHECK (
        workspace_id IN (
            SELECT id FROM workspaces WHERE owner_id = auth.uid()
        )
    );

-- =============================================================================
-- VERIFICATION
-- =============================================================================

SELECT tablename, policyname, cmd
FROM pg_policies
WHERE tablename IN ('workspaces', 'user_workspaces')
ORDER BY tablename, policyname;
