# Fresh Start Testing Guide

## Situation: All database data deleted ✅

This is **PERFECT** for testing! We have:
- ✅ Clean database (no conflicting data)
- ✅ Backend running with new code (workspace auto-creation)
- ✅ All fixes deployed and ready

---

## Quick Test: Create New User & Verify Auto-Workspace

### Test 1: Sign Up New User

**Option A: Via Frontend** (Recommended)
1. Open http://localhost:3000
2. Click "Sign Up" or go to `/register`
3. Fill in:
   - Email: `testuser@test.com`
   - Password: `Test123!`
   - Username: `testuser`
4. Click "Sign Up"

**Option B: Via API**
```bash
curl -X POST http://localhost:8000/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@test.com",
    "password": "Test123!",
    "username": "testuser"
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "data": {
    "user_id": "...",
    "email": "testuser@test.com",
    "username": "testuser",
    "token": "eyJ...",
    "expires_at": "..."
  }
}
```

---

### Test 2: Check Backend Logs

**Look for these messages in backend logs:**

```
✓ User created in public.users table: testuser@test.com
✓ Created default workspace: {uuid} for user testuser
```

**How to check logs:**
- If running in terminal: Look at the console output
- If running in background: Use BashOutput tool with shell ID

**What this proves:**
- ✅ User created successfully
- ✅ Workspace auto-creation triggered
- ✅ Our new code is working!

---

### Test 3: Verify in Database

**Run this SQL in Supabase:**

```sql
-- Check user was created
SELECT id, email, username, created_at
FROM users
WHERE email = 'testuser@test.com';

-- Check workspace was created
SELECT
    u.email,
    u.username,
    w.name as workspace_name,
    w.description,
    uw.role,
    wc.config->'sources' as sources
FROM users u
JOIN user_workspaces uw ON u.id = uw.user_id
JOIN workspaces w ON uw.workspace_id = w.id
LEFT JOIN workspace_configs wc ON wc.workspace_id = w.id
WHERE u.email = 'testuser@test.com';
```

**Expected Results:**

**Query 1** - User exists:
```
id      | email               | username  | created_at
--------|---------------------|-----------|-------------------
{uuid}  | testuser@test.com   | testuser  | 2025-10-24 ...
```

**Query 2** - Workspace created:
```
email             | username  | workspace_name         | role   | sources
------------------|-----------|------------------------|--------|----------
testuser@test.com | testuser  | testuser's Workspace   | owner  | []
```

---

### Test 4: Login & Access Dashboard

**Login with new user:**

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@test.com",
    "password": "Test123!"
  }'
```

**Get workspaces:**

```bash
curl -X GET http://localhost:8000/api/v1/workspaces \
  -H "Authorization: Bearer {token_from_login}"
```

**Expected:**
```json
{
  "success": true,
  "data": [
    {
      "id": "...",
      "name": "testuser's Workspace",
      "description": "Your default workspace",
      "role": "owner",
      "created_at": "..."
    }
  ]
}
```

---

### Test 5: Try to Access Content Stats (Should Work Now!)

```bash
curl -X GET http://localhost:8000/api/v1/content/workspaces/{workspace_id}/stats \
  -H "Authorization: Bearer {token}"
```

**Expected:**
- **If no content scraped yet**: 404 with "No content items available" (CORRECT!)
- **If content exists**: 200 OK with stats
- **Should NOT get**: 403 "Access denied" ✅

---

### Test 6: Full User Flow

**Via Frontend:**

1. ✅ Sign up → Should redirect to dashboard
2. ✅ See "Setup Progress 1/2" or similar
3. ✅ Workspace selector shows "testuser's Workspace"
4. ✅ Go to Settings → Add sources (Reddit, RSS, etc.)
5. ✅ Click "Save Sources" → No errors
6. ✅ Click "Save & Generate Newsletter" → Should work!
7. ✅ Dashboard shows draft newsletter

**All steps should work without any 403 errors!**

---

## What Success Looks Like

### ✅ Backend Logs Show:
```
✓ User created in public.users table: testuser@test.com
✓ Created default workspace: abc123... for user testuser
```

### ✅ Database Shows:
- 1 user in `public.users`
- 1 workspace in `workspaces` (owner = user_id)
- 1 entry in `user_workspaces` (role = 'owner')
- 1 entry in `workspace_configs` (sources = [])

### ✅ API Responses:
- GET /workspaces → 200 OK (1 workspace)
- GET /content/.../stats → 200 or 404 (NOT 403!)
- POST /content/scrape → Works without errors

### ✅ Frontend Shows:
- User can access dashboard
- Workspace selector shows their workspace
- No "Access denied" errors
- Can add sources and generate newsletters

---

## If Something Goes Wrong

### Issue 1: No workspace created (logs don't show "Created default workspace")

**Possible causes:**
- Backend not restarted with new code
- Workspace creation code threw exception

**Fix:**
1. Check backend logs for errors
2. Restart backend: `taskkill /F /IM python.exe && .venv\Scripts\python.exe -m uvicorn backend.main:app --reload`
3. Delete test user and try again

### Issue 2: Still getting 403 errors

**Possible causes:**
- User not added to user_workspaces table
- Wrong workspace_id being used

**Debug:**
```sql
-- Check if user has workspace access
SELECT * FROM user_workspaces WHERE user_id = '{user_id}';

-- Should return 1 row with role='owner'
```

### Issue 3: Workspace created but config missing

**Not critical** - workspace will work, just won't have default config

**Optional fix:**
```sql
INSERT INTO workspace_configs (workspace_id, config, ...)
VALUES ('{workspace_id}', '{"sources": [], ...}'::jsonb, ...);
```

---

## Multi-User Test (Optional)

**To verify multi-tenancy:**

1. Create User A: `usera@test.com`
2. Create User B: `userb@test.com`
3. Login as User A, get their workspace_id
4. Login as User B, try to access User A's workspace_id
5. **Expected**: 403 "Access denied: User not in workspace" ✅

---

## Next Steps After Successful Test

1. ✅ Confirm workspace auto-creation works
2. ✅ Delete test users if needed (or keep for testing)
3. ✅ Create your real user account
4. ✅ Start using the application normally
5. 🎉 Everything should work as expected!

---

## Summary

**With clean database + deployed fixes:**
- New signups → Auto-create workspace ✅
- Users immediately have access ✅
- No 403 errors ✅
- Multi-tenancy secure ✅
- "Save & Generate" button works ✅

**Just sign up a new user and everything should work!** 🚀