# Priority 1 Context Files

**These are the most critical documentation files. Read them first when working on this codebase.**

---

## Files in This Directory

### 1. [FRONTEND_BACKEND_MAPPING.md](./FRONTEND_BACKEND_MAPPING.md)
**Purpose**: Definitive reference for field name mappings between frontend TypeScript and backend Python/PostgreSQL.

**When to read**:
- Fixing type errors
- Implementing API clients
- Debugging "undefined property" errors
- Adding new models/types

**Key content**:
- Complete field mappings for all 10 domain models
- Known mismatches (e.g., `htmlContent` → `content_html`)
- Transformation utilities
- Common pitfalls

---

### 2. [COMMON_ERRORS.md](./COMMON_ERRORS.md)
**Purpose**: Comprehensive catalog of known errors with step-by-step solutions.

**When to read**:
- Debugging any error (401, 403, 422, 429, 500, etc.)
- Frontend crashes
- Database query failures
- Integration issues
- Deployment problems

**Key content**:
- 15+ documented error scenarios
- Root cause analysis for each
- Diagnostic commands
- Step-by-step solutions
- Prevention strategies
- Quick diagnostic flowchart

---

### 3. [TYPE_DEFINITIONS.md](./TYPE_DEFINITIONS.md)
**Purpose**: Copy-paste ready TypeScript interfaces that exactly match backend schemas.

**When to read**:
- Writing new API clients
- Creating new components
- Fixing type mismatches
- Validating request/response structures

**Key content**:
- Complete TypeScript interfaces for all models
- APIResponse<T> wrapper type
- Zod validation schemas
- Type guards and utilities
- Important notes on snake_case, nullability, etc.

---

## Reading Order

### For Most Tasks
1. Start with [CLAUDE.md](../../../CLAUDE.md) (comprehensive overview)
2. Read relevant sections from files above based on task
3. Then explore code files as needed

### For Debugging Errors
1. [COMMON_ERRORS.md](./COMMON_ERRORS.md) - Find your error
2. [FRONTEND_BACKEND_MAPPING.md](./FRONTEND_BACKEND_MAPPING.md) - If field name related
3. [TYPE_DEFINITIONS.md](./TYPE_DEFINITIONS.md) - If type related

### For New Features
1. [CLAUDE.md](../../../CLAUDE.md) - Understand architecture
2. [TYPE_DEFINITIONS.md](./TYPE_DEFINITIONS.md) - Get correct types
3. [FRONTEND_BACKEND_MAPPING.md](./FRONTEND_BACKEND_MAPPING.md) - Ensure field consistency

---

## Quick Reference Cards

### Most Common Field Mismatches
```typescript
// ❌ WRONG              ✅ CORRECT
sourceType           → source
htmlContent          → content_html
textContent          → content_text
commentsCount        → comments_count
imageUrl             → image_url
createdAt            → created_at
```

### Most Common Errors
```
401 → Token expired/missing
403 → Workspace access denied
422 → Validation error (check request body)
500 → Check logs (usually missing API keys or empty content)
TypeError → Null check / field name mismatch
CORS → Update backend/middleware/cors.py
Hydration → Add 'use client' + useEffect
```

### Quick Diagnostic Commands
```bash
# Check content exists
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/v1/content/workspaces/{id}?limit=1"

# Check workspace config
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/v1/workspaces/{id}/config"

# Check backend logs
tail -f backend/logs/app.log
```

---

## Maintenance

### When to Update These Files

**FRONTEND_BACKEND_MAPPING.md**:
- New API endpoint added
- Database schema changed
- Field renamed
- New model added

**COMMON_ERRORS.md**:
- New error pattern discovered
- Solution found for existing error
- Error no longer relevant (mark as fixed)

**TYPE_DEFINITIONS.md**:
- Database schema changed
- New model added
- Type structure changed
- Validation rules changed

### Update Process
1. Edit the relevant file
2. Update "Last Updated" date if present
3. Add entry to CLAUDE.md "Recent Changes" section
4. Commit with descriptive message

---

## Related Documentation

- **[CLAUDE.md](../../../CLAUDE.md)** - Comprehensive primary context
- **[.claude/instructions.md](../../../.claude/instructions.md)** - Reading strategy for Claude
- **[_PRIORITY_2_REFERENCE/](../_PRIORITY_2_REFERENCE/)** - Deep-dive reference docs
- **[_PRIORITY_3_HISTORICAL/](../_PRIORITY_3_HISTORICAL/)** - Old sprint docs and analysis

---

**END OF README**