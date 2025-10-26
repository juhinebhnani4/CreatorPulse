# Deployment Guide: Fix Trends Creating Duplicates

## Overview
This deployment fixes duplicate trends by:
1. Fixing frontend-backend field name mismatches
2. Adding database UNIQUE constraint
3. Implementing UPSERT logic instead of INSERT-only

## Files Modified

### Backend (3 files)
- `backend/migrations/015_add_trend_unique_constraint.sql` (NEW)
- `src/ai_newsletter/database/supabase_client.py` (+33 lines: `upsert_trend()` method)
- `backend/services/trend_service.py` (changed `create_trend()` → `upsert_trend()`)

### Frontend (4 files)
- `frontend-nextjs/src/lib/api/trends.ts` (import types from @/types/trend instead of duplicating)
- `frontend-nextjs/src/app/app/trends/page.tsx` (fix field name mismatches - PENDING)
- `frontend-nextjs/src/components/settings/trends-settings.tsx` (fix field name mismatches - PENDING)

## Critical Field Name Changes

| Old (WRONG) | New (CORRECT) | Location |
|-------------|---------------|----------|
| `content_count` | `mention_count` | All frontend components |
| `key_content_ids` | `key_content_item_ids` | All frontend components |
| `status: 'rising'\|'peak'...` | `confidence_level: 'low'\|'medium'\|'high'` + `is_active: boolean` | All frontend components |

## Deployment Steps

### Step 1: Run Cleanup Script (Supabase Dashboard)
**IMPORTANT**: Do this FIRST before applying migration!

```sql
-- 1. Open Supabase SQL Editor
-- 2. Copy contents of backend/migrations/cleanup_duplicate_trends.sql
-- 3. Run preview query (lines 20-29) to see duplicates
-- Expected: Shows ~10-15 duplicate topics

-- 4. Uncomment DELETE statement (lines 35-54)
-- 5. Execute DELETE
-- Expected: Deletes duplicate trends, keeps strongest/most recent

-- 6. Run verification query (lines 66-75)
-- Expected: Each topic appears only once per workspace
```

### Step 2: Apply Migration 015 (Supabase Dashboard)
```sql
-- Copy contents of backend/migrations/015_add_trend_unique_constraint.sql
-- Execute in Supabase SQL Editor
-- Expected output: "Migration 015 completed: UNIQUE constraint added to trends table"
```

### Step 3: Fix Frontend Components
The following components still reference outdated fields and need manual fixes:

#### File: `frontend-nextjs/src/app/app/trends/page.tsx`

**Line 236**: Remove `status` filter (field doesn't exist)
```typescript
// OLD:
<Badge variant="secondary">{trends.filter((t) => t.status === 'rising').length} rising</Badge>

// NEW:
<Badge variant="secondary">{trends.filter((t) => t.is_active && t.strength_score >= 0.7).length} high confidence</Badge>
```

**Line 331, 333**: Replace `status` with `confidence_level`
```typescript
// OLD:
{trend.status}
<span className={`w-2 h-2 rounded-full ${getStatusColor(trend.status)}`} />

// NEW:
{trend.confidence_level}
<span className={`w-2 h-2 rounded-full ${getConfidenceLevelColor(trend.confidence_level)}`} />
```

**Line 370**: Replace `content_count` with `mention_count`
```typescript
// OLD:
<p className="text-sm font-semibold">{trend.content_count}</p>

// NEW:
<p className="text-sm font-semibold">{trend.mention_count}</p>
```

**Line 403**: Replace `key_content_ids` with `key_content_item_ids`
```typescript
// OLD:
View {trend.key_content_ids.length} Related Items

// NEW:
View {trend.key_content_item_ids.length} Related Items
```

#### File: `frontend-nextjs/src/components/settings/trends-settings.tsx`

Similar fixes needed for:
- Line 247-248: Replace `status` with `confidence_level`
- Line 270: Replace `content_count` with `mention_count`

### Step 4: Deploy Backend Code
```bash
# In Railway or your deployment platform:
# 1. Push changes to Git
git add backend/migrations/015_add_trend_unique_constraint.sql
git add src/ai_newsletter/database/supabase_client.py
git add backend/services/trend_service.py
git commit -m "Fix: Prevent duplicate trends with UNIQUE constraint + UPSERT"
git push origin main

# 2. Railway auto-deploys (or trigger manual deploy)
```

### Step 5: Deploy Frontend Code
```bash
# After fixing frontend components:
git add frontend-nextjs/src/lib/api/trends.ts
git add frontend-nextjs/src/app/app/trends/page.tsx
git add frontend-nextjs/src/components/settings/trends-settings.tsx
git commit -m "Fix: Update trend field names to match backend"
git push origin main
```

### Step 6: Verification
```bash
# 1. Run trend detection twice in a row
curl -X POST https://your-backend.railway.app/api/v1/trends/detect \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"workspace_id": "YOUR_ID", "days_back": 7}'

# Wait 5 seconds
sleep 5

# Run again
curl -X POST https://your-backend.railway.app/api/v1/trends/detect \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"workspace_id": "YOUR_ID", "days_back": 7}'

# 2. Check database for duplicates
# Open Supabase SQL Editor:
SELECT topic, COUNT(*) as count
FROM trends
WHERE workspace_id = 'YOUR_ID'
GROUP BY topic
HAVING COUNT(*) > 1;

# Expected: 0 rows (no duplicates)
```

## Rollback Plan

If issues arise, rollback in reverse order:

### Rollback Backend Code
```bash
git revert HEAD  # Revert backend changes
git push origin main
```

### Rollback Migration
```sql
-- In Supabase SQL Editor:
ALTER TABLE trends DROP CONSTRAINT IF EXISTS unique_workspace_topic;
```

### Rollback Cleanup
```
-- No rollback possible (duplicates were deleted)
-- Re-run trend detection to recreate trends
```

## Testing Checklist

- [ ] Cleanup script removes duplicates
- [ ] Migration 015 applies successfully
- [ ] Backend upsert_trend() method works
- [ ] Frontend types compile without errors
- [ ] Trend detection doesn't create duplicates
- [ ] Frontend displays all fields correctly (no NaN/undefined)
- [ ] Active/inactive filtering works
- [ ] Confidence level badges display

## Support

If you encounter issues:
1. Check Supabase logs for constraint violations
2. Check Railway logs for backend errors
3. Check browser console for frontend type errors
4. Verify migration was applied: `SELECT * FROM pg_constraint WHERE conname = 'unique_workspace_topic';`

## Completion Criteria

✅ All tests pass
✅ No duplicate trends in database
✅ Frontend displays trends correctly
✅ No TypeScript errors
✅ Deployed to production

---

**Status**: Backend complete, frontend fixes pending
**Next Step**: Fix frontend component field names (Step 3)
