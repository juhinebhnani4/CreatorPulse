# Priority 2: Reference Documentation

**Last Updated**: 2025-01-22

## Purpose

Priority 2 files are **comprehensive reference guides** that provide deep dives into specific aspects of the CreatorPulse codebase. Read these when you need detailed understanding of a particular domain.

**When to Read**: After reading CLAUDE.md and Priority 1 Context files, when you need in-depth knowledge about:
- Frontend architecture and component patterns
- API endpoint specifications
- Database schema details
- Advanced configuration options

---

## Available Reference Docs

### 1. FRONTEND_ARCHITECTURE.md (~8,000 words)
**Read When**: Working on frontend features, understanding page structure, or debugging UI issues

**Contains**:
- Complete frontend architecture overview
- Technology stack (Next.js 14, TypeScript, TailwindCSS, Zustand)
- **Settings Page Architecture** - Deep dive on unified Settings hub with 10 sections
- Complete page structure and routing
- Component architecture patterns
- State management strategies
- Visual design system
- Key user flows
- API integration patterns
- File organization

**Key Sections**:
- Settings Page Architecture (Essential: Sources, Schedule, Subscribers, Email, Workspace | Advanced: API Keys, Style, Trends, Analytics, Feedback)
- Why duplicate pages exist (Settings sections + dedicated pages for future)
- Component breakdown (Dashboard, Settings, Modals, Layout, UI primitives)

---

### 2. SETTINGS_COMPONENTS.md (~6,000 words)
**Read When**: Working on any of the 10 Settings sections or their corresponding components

**Contains**:
- Detailed reference for each Settings section
- Component file locations
- Props and TypeScript interfaces
- API endpoints used by each section
- Configuration structures
- User actions and workflows
- Status indicators
- Code examples

**The 10 Settings Sections**:
1. 📱 Content Sources (`sources-settings.tsx`)
2. ⏰ Schedule Settings (`schedule-settings.tsx`)
3. 👥 Subscribers (`subscribers-settings.tsx`)
4. 📧 Email Configuration (`email-settings.tsx`)
5. 🏢 Workspace (`workspace-settings.tsx`)
6. 🔑 API Keys (`api-keys-settings.tsx`)
7. ✍️ Writing Style (`style-settings.tsx`)
8. 🔥 Trends Detection (`trends-settings.tsx`)
9. 📊 Analytics (`analytics-settings.tsx`)
10. 💬 Feedback Loop (`feedback-settings.tsx`)

---

### 3. API_REFERENCE.md (Planned)
**Read When**: Working with backend API endpoints or debugging API integration issues

**Will Contain**:
- Complete API endpoint catalog
- Request/response schemas
- Authentication requirements
- Error response formats
- Rate limiting details
- WebSocket endpoints

---

### 4. DATABASE_SCHEMA.md (Planned)
**Read When**: Working with database migrations, understanding data relationships, or debugging data issues

**Will Contain**:
- Complete PostgreSQL schema
- Table relationships and foreign keys
- Row-Level Security (RLS) policies
- Indexes and constraints
- Migration history
- Supabase-specific configurations

---

## Reading Strategy

### For Frontend Work
```
1. CLAUDE.md (Frontend section)
2. Priority 1: FRONTEND_BACKEND_MAPPING.md
3. Priority 2: FRONTEND_ARCHITECTURE.md
4. Priority 2: SETTINGS_COMPONENTS.md (if working on Settings)
```

### For Full-Stack Feature Implementation
```
1. CLAUDE.md (Overview + Quick Reference)
2. Priority 1: TYPE_DEFINITIONS.md
3. Priority 1: FRONTEND_BACKEND_MAPPING.md
4. Priority 2: FRONTEND_ARCHITECTURE.md
5. Priority 2: API_REFERENCE.md (when available)
```

### For Database Work
```
1. CLAUDE.md (Architecture section)
2. Priority 1: TYPE_DEFINITIONS.md
3. Priority 2: DATABASE_SCHEMA.md (when available)
```

### For Settings Page Work
```
1. CLAUDE.md (Frontend Pages Quick Reference)
2. Priority 2: FRONTEND_ARCHITECTURE.md (Settings section)
3. Priority 2: SETTINGS_COMPONENTS.md (specific section you're working on)
```

---

## Navigation

- **Up**: [../README.md](../README.md) - Docs directory index
- **Sibling**: [../_PRIORITY_1_CONTEXT/](../_PRIORITY_1_CONTEXT/) - Essential context files
- **Root**: [../../CLAUDE.md](../../CLAUDE.md) - Primary context

---

## Maintenance

**Update Frequency**: When major architectural changes occur (e.g., new page added, Settings structure changed, major refactoring)

**Who Updates**: Developer making the architectural change should update corresponding reference doc

**Auto-Updates**: Not automated. Manual updates required for accuracy.

---

## Token Budget

- **FRONTEND_ARCHITECTURE.md**: ~15,000 tokens
- **SETTINGS_COMPONENTS.md**: ~12,000 tokens
- **Total Priority 2 Docs**: ~27,000 tokens (when API_REFERENCE and DATABASE_SCHEMA added: ~50,000 tokens)

**Strategy**: Only read relevant Priority 2 docs based on task type. Don't read all at once.

---

## Notes

- Priority 2 docs are **reference materials**, not quick guides
- They provide the "why" and "how" behind architectural decisions
- When in doubt, check CLAUDE.md first for quick answers
- Use Priority 2 docs for deep understanding and complex implementations
