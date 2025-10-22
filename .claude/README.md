# .claude Directory

This directory contains configuration and instructions for Claude (AI assistant) to effectively work with this codebase.

---

## Files in This Directory

### [instructions.md](./instructions.md)
**Purpose**: Explicit reading priority directives that Claude follows at the start of every chat.

**Contains**:
- Priority 1/2/3 file classification
- Task-based reading strategies (frontend error, backend error, new feature, etc.)
- Token budget management (200k total, 30k for context)
- File location quick reference
- Anti-patterns to avoid
- Common error quick reference

**When Claude reads this**: At the very start of every new chat session (before reading CLAUDE.md)

---

## How It Works

### The Reading Hierarchy

```
1. .claude/instructions.md    ← Reading strategy (you are here)
   ↓
2. CLAUDE.md                   ← Comprehensive primary context
   ↓
3. docs/_PRIORITY_1_CONTEXT/   ← Critical references (as needed)
   ├─ FRONTEND_BACKEND_MAPPING.md
   ├─ COMMON_ERRORS.md
   └─ TYPE_DEFINITIONS.md
   ↓
4. Relevant code files         ← Targeted reading (3-5 files max)
```

### Priority System

**Priority 1** (Always read):
- CLAUDE.md
- docs/_PRIORITY_1_CONTEXT/*.md

**Priority 2** (Read as needed):
- docs/_PRIORITY_2_REFERENCE/*.md

**Priority 3** (Skip unless asked):
- docs/_PRIORITY_3_HISTORICAL/*.md
- Test files
- Build artifacts
- Dependencies

---

## For Users: How to Use

### Starting a New Chat

**Option 1: Let Claude navigate automatically**
```
"Fix the newsletter generation 500 error"
```
Claude will:
1. Read .claude/instructions.md
2. Read CLAUDE.md
3. Identify task type (backend error)
4. Read COMMON_ERRORS.md
5. Provide solution

**Option 2: Explicit context loading**
```
Context: Read CLAUDE.md and COMMON_ERRORS.md

Task: Debug 500 error on POST /api/v1/newsletters
```

**Option 3: Minimal (for quick questions)**
```
Quick question: What's the correct field name for newsletter HTML content?
```
Claude will check CLAUDE.md quick reference → answer: `content_html`

### Giving Context Mid-Chat

If Claude seems lost or needs more info:
```
Read docs/_PRIORITY_1_CONTEXT/FRONTEND_BACKEND_MAPPING.md for field name mappings
```

---

## For Claude: Quick Start Guide

### Every New Chat
1. ✅ Read `.claude/instructions.md` (THIS FILE'S PARENT)
2. ✅ Read `CLAUDE.md` (comprehensive context)
3. ✅ Identify task type (error? feature? understanding?)
4. ✅ Read relevant Priority 1 docs (1-2 files)
5. ✅ Use file location guide to find code
6. ✅ Search before reading full files

### Token Budget
- .claude/instructions.md: ~3k tokens
- CLAUDE.md: ~20k tokens
- Priority 1 docs: ~5-10k tokens
- Code files: ~20-30k tokens
- Reserve: ~140k tokens

### When in Doubt
1. Check CLAUDE.md quick reference sections
2. Check COMMON_ERRORS.md if debugging
3. Check FRONTEND_BACKEND_MAPPING.md if type issue
4. Ask user for clarification

---

## Maintenance

### When to Update

**instructions.md**:
- Priority classification changes
- New task-based strategies needed
- Token budget adjustment
- New anti-patterns discovered

**Frequency**: Quarterly or after major architectural changes

### How to Update

```bash
# Edit instructions
vim .claude/instructions.md

# Test with Claude in new chat
# "Read .claude/instructions.md and summarize the priority system"

# Commit changes
git add .claude/instructions.md
git commit -m "Update Claude instructions"
```

---

## Integration with Other Files

### instructions.md → CLAUDE.md
- instructions.md: "Read CLAUDE.md first"
- CLAUDE.md: Comprehensive context (architecture, mappings, errors)

### instructions.md → _PRIORITY_1_CONTEXT
- instructions.md: Task-based navigation ("Frontend error? Read COMMON_ERRORS.md")
- _PRIORITY_1_CONTEXT: Detailed references

### instructions.md → .claudeignore
- instructions.md: "Skip test files, dependencies"
- .claudeignore: Explicit exclusion list

---

## Examples

### Example 1: Frontend Type Error

**User**: "Getting TypeError: Cannot read property 'content_html' of undefined"

**Claude Process**:
1. Reads instructions.md → "Frontend error" strategy
2. Reads CLAUDE.md → Quick reference section
3. Reads COMMON_ERRORS.md → "TypeError" section
4. Finds: "Check field name mismatch"
5. Reads FRONTEND_BACKEND_MAPPING.md → Confirms `content_html` is correct
6. Provides solution: "Add null check: `newsletter?.content_html`"

**Files Read**: 4 (instructions, CLAUDE, COMMON_ERRORS, MAPPING)
**Code Files Read**: 0
**Time**: ~2 minutes

---

### Example 2: Adding New Feature

**User**: "Add a feature to export analytics to CSV"

**Claude Process**:
1. Reads instructions.md → "Adding new feature" strategy
2. Reads CLAUDE.md → Architecture, Data Flow, File Locations
3. Identifies: Need AnalyticsService, new API endpoint
4. Reads TYPE_DEFINITIONS.md → Get AnalyticsEvent interface
5. Reads backend/services/analytics_service.py → Understand current implementation
6. Implements feature in service + API route

**Files Read**: 3 context + 1 code
**Code Files Read**: 1 (analytics_service.py)
**Time**: ~5 minutes

---

### Example 3: Understanding Codebase (New Developer)

**User**: "Explain how newsletter generation works"

**Claude Process**:
1. Reads instructions.md → "Understanding codebase" strategy
2. Reads CLAUDE.md → Entire file
3. Finds "Data Flow" section → Newsletter Generation Flow
4. Provides explanation with file references
5. No code reading needed (all in CLAUDE.md)

**Files Read**: 2 (instructions, CLAUDE)
**Code Files Read**: 0
**Time**: ~1 minute

---

## Benefits

✅ **Consistent Navigation**: Claude always follows same priority system
✅ **Efficient Token Use**: Read high-value files first
✅ **Fast Error Resolution**: Known errors documented
✅ **Scalable**: Add new strategies as project grows
✅ **Self-Documenting**: Instructions explain themselves

---

## Troubleshooting

### Claude Not Following Instructions

**Symptoms**: Claude reads random files, doesn't check CLAUDE.md

**Solution**: Explicitly reference at chat start:
```
Follow .claude/instructions.md. Read CLAUDE.md first, then help with [task].
```

### Instructions Out of Date

**Symptoms**: Referenced files don't exist, strategies don't match current workflow

**Solution**: Review and update instructions.md quarterly

### Token Budget Exceeded

**Symptoms**: Claude hits 200k token limit before completing task

**Solution**:
- Reduce context file sizes (move details to Priority 2)
- Adjust token allocation in instructions.md
- Split large tasks into smaller chats

---

## Summary

This directory ensures Claude:
1. ✅ Reads the right files in the right order
2. ✅ Prioritizes critical information
3. ✅ Uses tokens efficiently
4. ✅ Provides consistent, high-quality assistance

**Key File**: [instructions.md](./instructions.md) - Read this to understand the full system.

---

**For more info, see**: [CONTEXT_SYSTEM_SETUP.md](../CONTEXT_SYSTEM_SETUP.md)

**END OF README**