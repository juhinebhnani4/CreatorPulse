# Developer Quick Reference Checklist

**Print this and keep it visible while coding!**

---

## 🎯 Before Starting Any Project

- [ ] Choose tech stack (research 1-2 days, decide once)
- [ ] Design database schema (tables, relationships, constraints)
- [ ] Sketch UI wireframes (even on paper!)
- [ ] Design modular architecture (create base templates for similar components)
- [ ] Create .env.example template
- [ ] Set up Git repository with .gitignore

---

## 💻 When Adding a New Feature

### Planning
- [ ] Sketch the UI (paper, Figma, screenshot)
- [ ] Design database changes (migrations)
- [ ] Create field name mapping (frontend ↔ backend ↔ database)
- [ ] List dependencies needed

### Building
- [ ] Build ONE small piece at a time
- [ ] Create UI component with FAKE data first
- [ ] Test UI thoroughly
- [ ] Build backend endpoint
- [ ] Test endpoint (Postman/curl)

### Integration
- [ ] Connect frontend to backend
- [ ] Test with real data
- [ ] Test with empty data
- [ ] Test error conditions
- [ ] Add loading states
- [ ] Add error messages
- [ ] Add success confirmations

### Finishing
- [ ] Test on mobile/tablet
- [ ] Add docstrings/comments
- [ ] Update API documentation
- [ ] Create migration file if database changed
- [ ] Write tests (unit + integration)

---

## 🔧 When Debugging (Check in Order!)

### 1. User's Screen
- [ ] Can you reproduce the error?
- [ ] What happens when you click?
- [ ] What SHOULD happen?

### 2. Browser Console (F12)
- [ ] Any red errors? Which file/line?
- [ ] Any yellow warnings?
- [ ] Any network failures?

### 3. Network Tab (F12)
- [ ] Which request failed?
- [ ] Status code? (200=good, 401=auth, 403=forbidden, 500=server error)
- [ ] What does response body say?

### 4. Backend Logs ⭐ MOST IMPORTANT
- [ ] Read FULL stack trace (don't skim!)
- [ ] Which file and line number?
- [ ] Exact error message?
- [ ] Copy and Google the exact error

### 5. Compare Working Code
- [ ] Find similar code that WORKS
- [ ] What's different line-by-line?
- [ ] Copy the working pattern

### Still Stuck?
- [ ] Google the EXACT error message
- [ ] Check library documentation
- [ ] Search GitHub issues
- [ ] Ask for help (30 min rule!)

---

## 📚 When Using a New Library

### Before Writing Code
- [ ] Read "Getting Started" documentation
- [ ] Find official examples
- [ ] Check version compatibility
- [ ] Check parameter naming requirements

### First Integration
- [ ] Copy official example EXACTLY
- [ ] Make it work with dummy data
- [ ] Test it works before customizing
- [ ] Understand error messages

### After It Works
- [ ] Customize ONE thing at a time
- [ ] Test after EACH change
- [ ] Document any gotchas you find
- [ ] Add to requirements.txt/package.json

---

## ⚠️ Common Mistakes to Avoid

### Field Names
- [ ] Frontend and backend use SAME field names
- [ ] Check: `sample_count` vs `trained_on_count`
- [ ] Check: `htmlContent` vs `content_html`
- [ ] Search ALL files before renaming

### Time & Dates
- [ ] Use `datetime.now(timezone.utc)` NOT `datetime.now()`
- [ ] All database timestamps have timezone
- [ ] Check null values for `scraped_at`, `created_at`

### Authentication
- [ ] Token stored under ONE name everywhere
- [ ] Check: `token` vs `auth_token` vs `access_token`
- [ ] Verify token expiry handling
- [ ] Test 401 error handling

### Database
- [ ] Use `service_client` for backend operations
- [ ] Use `client` only for user-facing queries
- [ ] Understand RLS policies
- [ ] Add indexes on foreign keys

### Library Integration
- [ ] Parameter names must match library requirements
- [ ] Example: slowapi needs `request: Request` (exact name!)
- [ ] Check decorator order matters
- [ ] Test rate limiting works

---

## ✅ Pre-Deployment Checklist

### Code Quality
- [ ] `npx tsc --noEmit` (TypeScript compiles)
- [ ] `pytest` (backend tests pass)
- [ ] No `console.log()` in production code
- [ ] No commented-out code
- [ ] Code is formatted (Black, Prettier)

### Environment
- [ ] `.env.example` is up-to-date
- [ ] All secrets in `.env` (not in code)
- [ ] `.env` in `.gitignore`
- [ ] Required env vars validated on startup

### Security
- [ ] Authentication works
- [ ] Authorization checked on all endpoints
- [ ] Rate limiting enabled
- [ ] CORS properly configured
- [ ] RLS policies active on database

### User Experience
- [ ] All buttons show loading states
- [ ] Error messages are helpful (not technical)
- [ ] Success confirmations appear
- [ ] Empty states have guidance ("Click here to start!")
- [ ] Mobile layout tested

### Performance
- [ ] Database indexes on foreign keys
- [ ] Large queries are paginated
- [ ] API responses cached where appropriate
- [ ] Images optimized

### Documentation
- [ ] README has setup instructions
- [ ] API endpoints documented
- [ ] Complex functions have docstrings
- [ ] Environment variables explained

### Rollback Plan
- [ ] Feature flags implemented
- [ ] Can disable new feature without deploy
- [ ] Previous version tagged in Git
- [ ] Database migrations are reversible
- [ ] Can deploy previous version in <5 minutes

---

## 🚀 Daily Workflow

### Morning
- [ ] Pull latest code: `git pull`
- [ ] Check for merge conflicts
- [ ] Read team updates
- [ ] Plan today's ONE feature

### During Development
- [ ] Commit often (every 30-60 min)
- [ ] Test after every small change
- [ ] Write helpful commit messages
- [ ] Push at least once a day

### Before Committing
- [ ] Code compiles without errors
- [ ] Tests pass
- [ ] No debugging code (console.log, etc.)
- [ ] Formatting is correct

### Before Logging Off
- [ ] Push your code
- [ ] Update task status
- [ ] Document any blockers
- [ ] Clean up workspace

---

## 💡 Quick Tips

**Time Savers:**
- ✅ Read error messages COMPLETELY
- ✅ Compare with working code FIRST
- ✅ Test after EVERY small change
- ✅ Build frontend before backend
- ✅ Document as you go (not later!)

**Time Wasters:**
- ❌ "I'll add tests later"
- ❌ "This is a small change, no need to test"
- ❌ "I'll document when done"
- ❌ "I don't need to read the docs"
- ❌ "I'll refactor later"

**The 30-Minute Rule:**
- Stuck for 30 minutes? ASK FOR HELP!
- Don't waste 2 hours on something someone else solved in 5 minutes

**The Rubber Duck Rule:**
- Explain your problem out loud (even to a rubber duck!)
- You'll often solve it while explaining

---

## 🆘 Emergency Contacts

**When Something Breaks in Production:**
1. Check feature flags - can we disable it?
2. Check recent deployments - what changed?
3. Check error logs - what's the actual error?
4. Can we rollback to previous version?
5. Communicate with team and users

**Rollback Command:**
```bash
# Git: Deploy previous version
git checkout <previous-tag>
git push -f

# Heroku: Rollback last deploy
heroku rollback

# Feature flags: Disable feature
heroku config:set ENABLE_NEW_FEATURE=false
```

---

**Last Updated:** October 24, 2025
**Print Date:** __________
**Developer:** __________

**Remember: This checklist is built from real mistakes. Use it! 🎯**
