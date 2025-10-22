# Instructions for Claude

**READ THIS FILE FIRST** at the start of every new chat session.

---

## Critical: File Reading Priority

### PRIORITY 1 - ALWAYS READ FIRST (in order)

1. **CLAUDE.md** (root) - Primary context, 20k tokens, comprehensive overview
2. **docs/_PRIORITY_1_CONTEXT/FRONTEND_BACKEND_MAPPING.md** - Field name mappings
3. **docs/_PRIORITY_1_CONTEXT/COMMON_ERRORS.md** - Known issues and solutions
4. **docs/_PRIORITY_1_CONTEXT/TYPE_DEFINITIONS.md** - TypeScript interfaces

**These 4 files contain everything you need for 90% of tasks.**

---

## Task-Based Reading Strategy

### Frontend Error Debugging
```
1. Read: CLAUDE.md → Common Errors section
2. Read: docs/_PRIORITY_1_CONTEXT/COMMON_ERRORS.md → Frontend Errors
3. Read: docs/_PRIORITY_1_CONTEXT/FRONTEND_BACKEND_MAPPING.md
4. Read: docs/_PRIORITY_1_CONTEXT/TYPE_DEFINITIONS.md
5. Then: Read relevant component files
```

### Backend Error Debugging
```
1. Read: CLAUDE.md → Common Errors section
2. Read: docs/_PRIORITY_1_CONTEXT/COMMON_ERRORS.md → Backend API Errors
3. Then: Read relevant service file (backend/services/[name]_service.py)
```

### API Integration Issue
```
1. Read: CLAUDE.md → Frontend-Backend Mappings section
2. Read: docs/_PRIORITY_1_CONTEXT/FRONTEND_BACKEND_MAPPING.md
3. Read: docs/_PRIORITY_1_CONTEXT/TYPE_DEFINITIONS.md
4. Then: Read API route (backend/api/v1/[route].py)
```

### Type Mismatch Error
```
1. Read: docs/_PRIORITY_1_CONTEXT/TYPE_DEFINITIONS.md
2. Read: docs/_PRIORITY_1_CONTEXT/FRONTEND_BACKEND_MAPPING.md
3. Then: Read relevant frontend type file (frontend-nextjs/src/types/[type].ts)
```

### Adding New Feature
```
1. Read: CLAUDE.md → Architecture Overview + Data Flow
2. Read: CLAUDE.md → Critical File Locations
3. Then: Read relevant service and API route files
```

### Database Query Issue
```
1. Read: CLAUDE.md → Database Schema section
2. Read: docs/_PRIORITY_2_REFERENCE/DATABASE_SCHEMA.md
3. Then: backend/database.py, backend/migrations/*.sql
```

### Understanding Codebase (General)
```
1. Read: CLAUDE.md (entire file)
2. Read: All docs/_PRIORITY_1_CONTEXT/*.md files
3. Then: Explore code as needed based on CLAUDE.md file location guide
```

---

## PRIORITY 2 - READ WHEN NEEDED (Reference Only)

- `docs/_PRIORITY_2_REFERENCE/API_REFERENCE.md` - Complete endpoint catalog
- `docs/_PRIORITY_2_REFERENCE/DATABASE_SCHEMA.md` - Full schema with all 17 tables

**Only read these for deep dives or comprehensive reference.**

---

## PRIORITY 3 - DON'T READ UNLESS EXPLICITLY ASKED

- `docs/_PRIORITY_3_HISTORICAL/*.md` - Old sprint docs, analysis, TODOs
- `backend/tests/**` - Test files (unless debugging tests)
- `frontend-nextjs/e2e/**` - E2E test files
- `*.log` - Log files
- `node_modules/`, `.venv/` - Dependencies
- `.next/`, `__pycache__/` - Build artifacts

**These are low-value for general work. Skip them.**

---

## File Location Quick Reference

### Backend
```
Services (business logic):     backend/services/[name]_service.py
API routes:                    backend/api/v1/[domain].py
Models (Pydantic):             backend/models/[domain].py
Database:                      backend/database.py
Migrations:                    backend/migrations/*.sql
Config:                        backend/settings.py, backend/config/constants.py
Worker:                        backend/worker.py
```

### Frontend
```
Pages:                         frontend-nextjs/src/app/[page]/page.tsx
Components:                    frontend-nextjs/src/components/[category]/[name].tsx
API clients:                   frontend-nextjs/src/lib/api/[domain].ts
State management:              frontend-nextjs/src/lib/store/[name]-store.ts
Types:                         frontend-nextjs/src/types/[domain].ts
```

---

## Search Strategy

### Before Searching Code

1. ✅ **Check CLAUDE.md first** - Has it been answered already?
2. ✅ **Check _PRIORITY_1_CONTEXT docs** - Is there a known error/mapping?
3. ✅ **Use CLAUDE.md file location guide** - Go directly to relevant files

### When Searching Code

**Use Glob for file patterns**:
```bash
# Find service files
Glob: backend/services/*.py

# Find frontend components
Glob: frontend-nextjs/src/components/**/*.tsx

# Find type definitions
Glob: frontend-nextjs/src/types/*.ts
```

**Use Grep for code search**:
```bash
# Search in services only (not entire codebase)
Grep: pattern="function_name" path="backend/services/"

# Search in specific file type
Grep: pattern="interface Newsletter" type="ts"
```

---

## Anti-Patterns (DON'T DO THIS)

❌ **Reading all test files to understand code**
→ ✅ Read service/component files directly, skip tests unless debugging tests

❌ **Reading all documentation files at once**
→ ✅ Use CLAUDE.md as index, read specific docs only when needed

❌ **Searching entire codebase without checking context files first**
→ ✅ Check CLAUDE.md, use specific file paths from file location guide

❌ **Re-reading code files every chat session**
→ ✅ Trust CLAUDE.md information, only read code for verification/updates

❌ **Using generic error messages when debugging**
→ ✅ Reference COMMON_ERRORS.md for specific solutions

❌ **Guessing field names**
→ ✅ Check FRONTEND_BACKEND_MAPPING.md for exact field names

❌ **Reading historical docs for current context**
→ ✅ Read CLAUDE.md (updated), skip _PRIORITY_3_HISTORICAL

---

## Token Budget Management

**Target**: Use max 30k tokens (15%) for context loading, leave 170k for work

### Allocation
```
CLAUDE.md:                      ~20k tokens (must read)
_PRIORITY_1_CONTEXT docs:       ~10k tokens (read as needed)
Task-specific code files:       ~30k tokens (selective reading)
Reserve:                        ~140k tokens (responses, exploration)
```

### Reading Strategy
1. ✅ Always read CLAUDE.md (~20k tokens) - High value
2. ✅ Read 1-2 _PRIORITY_1_CONTEXT docs based on task (~5k tokens)
3. ✅ Use Grep/Glob to locate code before reading full files (~2k tokens)
4. ✅ Read only 3-5 code files per session (~20k tokens)
5. ❌ Don't read test files, historical docs, or entire modules

---

## Known Field Name Mismatches (Quick Reference)

**Always use these (backend-correct) field names:**

| ❌ Old/Incorrect | ✅ Correct (Backend) |
|------------------|----------------------|
| `sourceType` | `source` |
| `htmlContent` | `content_html` |
| `textContent` | `content_text` |
| `commentsCount` | `comments_count` |
| `sharesCount` | `shares_count` |
| `viewsCount` | `views_count` |
| `imageUrl` | `image_url` |
| `videoUrl` | `video_url` |
| `createdAt` | `created_at` |
| `scrapedAt` | `scraped_at` |

**Rule**: Always use snake_case to match PostgreSQL columns.

---

## Common Errors (Quick Reference)

| Error Code | Quick Fix |
|------------|-----------|
| **401** | Check token (expired? missing? invalid?) → Refresh or re-login |
| **403** | Check workspace access → Verify user_workspaces membership |
| **422** | Validation error → Check request body matches Pydantic model |
| **429** | Rate limit → Wait 60s and retry with exponential backoff |
| **500 (newsletter)** | Check: 1) Content exists? 2) API keys set? 3) Config valid? |
| **TypeError (frontend)** | Check: 1) Null/undefined? 2) Field name mismatch? 3) API response structure? |
| **CORS** | Update backend/middleware/cors.py origins list |
| **Hydration** | Add 'use client' + useEffect for client-only code |
| **RLS Policy** | Use service client for access checks, user client for data |

**For detailed solutions**: See `docs/_PRIORITY_1_CONTEXT/COMMON_ERRORS.md`

---

## Architecture Quick Reference

```
Frontend (Next.js 14) → HTTP/REST (Axios + JWT) → Backend (FastAPI)
    ↓                                                     ↓
Zustand State                                      Service Layer
React Query Cache                                  (12 services)
    ↓                                                     ↓
Components                                         Supabase PostgreSQL
                                                   (17 tables, RLS)
```

**Data Flow**:
1. Content Scraping: Sources → ContentService → content_items
2. Newsletter Gen: Content → AI API → newsletters
3. Email Delivery: Newsletter → SMTP/SendGrid → subscribers
4. Analytics: Email → Tracking → email_analytics_events

---

## Start-of-Chat Checklist

When starting a new chat:

1. ✅ Read `.claude/instructions.md` (this file)
2. ✅ Read `CLAUDE.md` (comprehensive context)
3. ✅ Check task type → Read relevant _PRIORITY_1_CONTEXT docs
4. ✅ Use file location guide to find relevant code files
5. ✅ Search with Grep/Glob before reading full files
6. ✅ Reference COMMON_ERRORS.md if debugging errors
7. ✅ Check FRONTEND_BACKEND_MAPPING.md if type issues

---

## When in Doubt

1. **Check CLAUDE.md first** - Most questions answered there
2. **Ask user for clarification** - Don't guess or assume
3. **Reference context docs** - They're kept up-to-date
4. **Read minimal code** - Context docs have most info
5. **Prioritize high-value files** - Skip tests, logs, historical docs

---

## Summary

**The Golden Rule**: Read CLAUDE.md first every chat, then navigate based on task using the priority system above. Trust the context files, minimize code reading, maximize efficiency.

**Key Files (memorize these)**:
- `CLAUDE.md` - Primary context (ALWAYS READ)
- `docs/_PRIORITY_1_CONTEXT/*.md` - Critical references
- `backend/services/*.py` - Business logic
- `backend/api/v1/*.py` - API routes
- `frontend-nextjs/src/app/**/*.tsx` - Pages
- `frontend-nextjs/src/components/**/*.tsx` - Components

**Expected Behavior**:
- ✅ Start every chat reading this file + CLAUDE.md
- ✅ Navigate to task-specific docs using priority system
- ✅ Reference mappings/errors before searching code
- ✅ Read 3-5 code files max per session
- ✅ Use context docs as source of truth

---

**END OF INSTRUCTIONS**