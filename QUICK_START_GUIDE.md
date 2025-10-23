# 🚀 Quick Start Guide

**Get Answers in 30 Seconds**

📍 **You are here:** Quick Start Guide (START HERE)

**Other documentation:**
- 🖱️ **Button details & disambiguation** → [BUTTON_REFERENCE_GUIDE.md](./BUTTON_REFERENCE_GUIDE.md)
- 📖 **Feature deep dive & architecture** → [COMPLETE_BACKEND_FRONTEND_MAPPING.md](./COMPLETE_BACKEND_FRONTEND_MAPPING.md)
- 🔧 **Recent fixes & known issues** → [FIX_STATUS.md](./FIX_STATUS.md)

---

## 🎯 I Want To...

### ❓ Fix a Button That's Not Working

1. **Find your button** in [Button Quick Reference](#-button-quick-reference) below
2. **Check which API it calls** (right column)
3. **Open browser DevTools** → Console tab → Look for red errors
4. **Match the error** in [Common Issues](#-common-issues--quick-fixes) section
5. **If not found** → Go to [BUTTON_REFERENCE_GUIDE.md](./BUTTON_REFERENCE_GUIDE.md) for detailed flow

**Example:**
- Button: "Send Now" not working
- API: `POST /api/v1/delivery/send`
- Console error: "Email delivery not configured"
- Fix: Go to Settings → Email Configuration → Add SMTP credentials

---

### ❓ Understand How a Feature Works

1. **Find the feature** in list below:
   - Authentication → [Full Details](./COMPLETE_BACKEND_FRONTEND_MAPPING.md#1-authentication)
   - Content Scraping → [Full Details](./COMPLETE_BACKEND_FRONTEND_MAPPING.md#3-content-scraping)
   - Newsletter Generation → [Full Details](./COMPLETE_BACKEND_FRONTEND_MAPPING.md#4-newsletters)
   - Email Sending → [Full Details](./COMPLETE_BACKEND_FRONTEND_MAPPING.md#6-delivery-email-sending)
   - Scheduling → [Full Details](./COMPLETE_BACKEND_FRONTEND_MAPPING.md#7-scheduler-automation)
   - Analytics → [Full Details](./COMPLETE_BACKEND_FRONTEND_MAPPING.md#8-analytics)

2. **Read the "What It Does" section** (plain English explanation)
3. **Follow the data flow diagram** (shows button → API → database → response)

---

### ❓ Debug a Failed API Call

1. **Open browser DevTools** → Network tab
2. **Find the failed request** (red, status 400/500)
   - Click on it
   - Go to "Payload" tab to see what was sent
   - Go to "Response" tab to see error message
3. **Look up the endpoint** in [API Quick Reference](#-api-quick-reference) below
4. **Check backend logs:**
   ```bash
   tail -f backend/logs/app.log
   ```
5. **Common patterns:**
   - 401 Unauthorized → Token expired, re-login
   - 404 Not Found → Resource doesn't exist (check ID)
   - 400 Bad Request → Invalid data sent (check Payload tab)
   - 500 Internal Server Error → Backend bug (check logs)

---

### ❓ Understand "Why Are There Multiple Generate Buttons?"

There ARE multiple buttons with similar names that do **different things**.

**Quick Answer:**
- "Generate Draft Now" → Opens settings modal
- "Regenerate with New Content" → Opens settings modal (same as above)
- "Generate" (inside modal) → Actually calls the API
- Auto-generation (hidden) → Happens automatically after scraping

**Full Explanation:** [BUTTON_REFERENCE_GUIDE.md → Part 2: Disambiguation](./BUTTON_REFERENCE_GUIDE.md#part-2-the-confusing-duplicates)

---

## 🖱️ Button Quick Reference

**Top 30 Most Used Buttons**

| Button Label | Page Location | API Endpoint | Where to Debug |
|-------------|---------------|--------------|----------------|
| **"Scrape Content"** | Dashboard | `POST /api/v1/content/scrape` | backend/services/content_service.py:47 |
| **"Generate Newsletter"** | Dashboard | Opens modal → `POST /api/v1/newsletters/generate` | backend/services/newsletter_service.py:189 |
| **"Regenerate with New Content"** | Dashboard (stale state) | Opens modal → `POST /api/v1/newsletters/generate` | Same as above |
| **"Preview Draft"** | Dashboard | None (opens modal locally) | frontend/components/modals/draft-editor-modal.tsx |
| **"Send Now"** | Dashboard | `POST /api/v1/delivery/send` | backend/services/delivery_service.py:89 |
| **"Send Test"** | Draft Editor Modal | `POST /api/v1/delivery/send` (with test_email) | Same as above |
| **"Save Draft"** | Draft Editor Modal | `PUT /api/v1/newsletters/{id}` | backend/api/v1/newsletters.py:373 |
| **"Add Source"** | Dashboard | Opens modal → `PUT /api/v1/workspaces/{id}/config` | backend/services/workspace_service.py |
| **"Pause Source"** | Dashboard (per source) | `PUT /api/v1/workspaces/{id}/config` | Same as above |
| **"Resume Source"** | Dashboard (per source) | `PUT /api/v1/workspaces/{id}/config` | Same as above |
| **"Scrape Now"** | Content Page | `POST /api/v1/content/scrape` | backend/services/content_service.py:47 |
| **"Keep" (👍)** | Content Page | `POST /api/v1/feedback/items/{id}/rate` | backend/services/feedback_service.py |
| **"Skip" (👎)** | Content Page | `POST /api/v1/feedback/items/{id}/rate` | Same as above |
| **"Add Subscriber"** | Subscribers Page | `POST /api/v1/subscribers` | backend/api/v1/subscribers.py:34 |
| **"Import CSV"** | Subscribers Page | `POST /api/v1/subscribers/bulk` | backend/api/v1/subscribers.py:58 |
| **"Export CSV"** | Subscribers Page | None (local download) | frontend CSV generation |
| **"Delete Selected"** | Subscribers Page | `DELETE /api/v1/subscribers/{id}` (multiple) | backend/api/v1/subscribers.py |
| **"View"** | History Page | Navigate to newsletter detail | None (navigation) |
| **"Edit"** | History Page (drafts) | Navigate to newsletter editor | None (navigation) |
| **"Regenerate"** | History Page | `POST /api/v1/newsletters/generate` | backend/services/newsletter_service.py:189 |
| **"Duplicate"** | History Page | `POST /api/v1/newsletters/generate` | Same as above |
| **"Delete"** | History Page | `DELETE /api/v1/newsletters/{id}` | backend/api/v1/newsletters.py |
| **"Save Sources"** | Settings → Sources | `PUT /api/v1/workspaces/{id}/config` | backend/services/workspace_service.py |
| **"Save Config"** | Settings → Email | `PUT /api/v1/workspaces/{id}/config` | Same as above |
| **"Test Email"** | Settings → Email | `POST /api/v1/delivery/send` (test) | backend/services/delivery_service.py:89 |
| **"Create Schedule"** | Settings → Schedule | `POST /api/v1/scheduler` | backend/api/v1/scheduler.py:29 |
| **"Pause Job"** | Settings → Schedule | `POST /api/v1/scheduler/{id}/pause` | backend/api/v1/scheduler.py |
| **"Resume Job"** | Settings → Schedule | `POST /api/v1/scheduler/{id}/resume` | backend/api/v1/scheduler.py |
| **"Run Now"** | Settings → Schedule | `POST /api/v1/scheduler/{id}/run-now` | backend/api/v1/scheduler.py |
| **"Train Style"** | Settings → Style | `POST /api/v1/style/train` | backend/services/style_service.py |

**See all 100+ buttons:** [BUTTON_REFERENCE_GUIDE.md](./BUTTON_REFERENCE_GUIDE.md)

---

## 🔌 API Quick Reference

**Top 20 Most Used Endpoints**

| HTTP Method | Endpoint | What It Does | Frontend File | Backend File |
|------------|----------|--------------|---------------|--------------|
| `POST` | `/api/v1/auth/login` | Log in with email/password | src/lib/api/auth.ts:6 | backend/api/v1/auth.py:70 |
| `POST` | `/api/v1/auth/signup` | Create new account | src/lib/api/auth.ts:20 | backend/api/v1/auth.py:87 |
| `GET` | `/api/v1/workspaces` | List user's workspaces | src/lib/api/workspaces.ts:5 | backend/api/v1/workspaces.py:23 |
| `PUT` | `/api/v1/workspaces/{id}/config` | Save workspace settings | src/lib/api/workspaces.ts:54 | backend/api/v1/workspaces.py:135 |
| `POST` | `/api/v1/content/scrape` | Fetch content from sources | src/lib/api/content.ts:101 | backend/api/v1/content.py:22 |
| `GET` | `/api/v1/content/workspaces/{id}` | List scraped content | src/lib/api/content.ts:61 | backend/api/v1/content.py:75 |
| `GET` | `/api/v1/content/workspaces/{id}/stats` | Get content statistics | src/lib/api/content.ts:71 | backend/api/v1/content.py:130 |
| `POST` | `/api/v1/newsletters/generate` | Generate newsletter with AI | src/lib/api/newsletters.ts:23 | backend/api/v1/newsletters.py:27 |
| `GET` | `/api/v1/newsletters/workspaces/{id}` | List newsletters | src/lib/api/newsletters.ts:5 | backend/api/v1/newsletters.py:213 |
| `PUT` | `/api/v1/newsletters/{id}` | Update newsletter (save draft) | src/lib/api/newsletters.ts:53 | backend/api/v1/newsletters.py:329 |
| `DELETE` | `/api/v1/newsletters/{id}` | Delete newsletter | src/lib/api/newsletters.ts:61 | backend/api/v1/newsletters.py:401 |
| `POST` | `/api/v1/delivery/send` | Send newsletter to subscribers | src/lib/api/delivery.ts:10 | backend/api/v1/delivery.py:19 |
| `POST` | `/api/v1/subscribers` | Add single subscriber | src/lib/api/subscribers.ts:48 | backend/api/v1/subscribers.py:34 |
| `POST` | `/api/v1/subscribers/bulk` | Import multiple subscribers | src/lib/api/subscribers.ts:57 | backend/api/v1/subscribers.py:80 |
| `GET` | `/api/v1/subscribers/workspaces/{id}` | List subscribers | src/lib/api/subscribers.ts:13 | backend/api/v1/subscribers.py:115 |
| `DELETE` | `/api/v1/subscribers/{id}` | Delete subscriber | src/lib/api/subscribers.ts:75 | backend/api/v1/subscribers.py:201 |
| `POST` | `/api/v1/scheduler` | Create scheduled job | src/lib/api/scheduler.ts:16 | backend/api/v1/scheduler.py:29 |
| `GET` | `/api/v1/analytics/workspaces/{id}/summary` | Get analytics summary | src/lib/api/analytics.ts:121 | backend/api/v1/analytics.py:251 |
| `POST` | `/api/v1/feedback/items/{id}/rate` | Rate content (like/dislike) | src/lib/api/feedback.ts | backend/api/v1/feedback.py |
| `GET` | `/track/pixel/{token}.png` | Track email open (1x1 image) | N/A (email clients) | backend/api/tracking.py |

**See all 80+ endpoints:** [COMPLETE_BACKEND_FRONTEND_MAPPING.md → API Reference](./COMPLETE_BACKEND_FRONTEND_MAPPING.md#feature-mapping)

---

## ⚠️ Common Issues & Quick Fixes

### 1. ❌ "No fields to update" (Newsletter Save)

**Where:** Saving newsletter draft subject line

**Error Message:** `{"detail":"No fields to update"}`

**Cause:** Backend bug (recently fixed) - `subject_line` not mapped to `title` correctly

**Quick Fix:**
- ✅ **Already fixed!** Backend was restarted with fix loaded
- If still seeing error: Refresh browser, clear cache
- **Details:** [FIX_STATUS.md → Newsletter Update Bug](./FIX_STATUS.md#fix-2-newsletter-update-bug-fix)

---

### 2. ⏱️ Dashboard Loading 6+ Seconds (Analytics Slow)

**Where:** Dashboard page takes forever to load

**Cause:** Analytics summary query was inefficient (7 subqueries)

**Quick Fix:**
- ✅ **Already fixed!** Migration 011 applied (6-7s → <500ms)
- If still slow: Check backend logs for errors
- **Details:** [FIX_STATUS.md → Analytics Optimization](./FIX_STATUS.md#fix-1-analytics-performance-optimization)

---

### 3. ❌ "Failed to generate newsletter" (No Content)

**Where:** After clicking "Generate Newsletter"

**Error Message:** `"No content found for workspace"`

**Cause:** No content items exist in database (scraping never ran)

**Quick Fix:**
1. Click "Scrape Content" first
2. Wait 15-30 seconds for scraping to complete
3. Then click "Generate Newsletter"

---

### 4. ❌ "anthropic package required" (Claude AI)

**Where:** Generating newsletter with Claude

**Error Message:** `ImportError: anthropic package required`

**Cause:** Missing Python package

**Quick Fix:**
```bash
pip install anthropic
```
**Or** use OpenAI instead (GPT-4) - it's already configured

---

### 5. 🔐 401 Unauthorized (Token Expired)

**Where:** Any API call

**Error Message:** `{"detail":"Not authenticated"}`

**Cause:** JWT token expired (30 minute lifetime)

**Quick Fix:**
1. Log out
2. Log back in
3. Token refreshed automatically

---

### 6. ❌ "Email delivery not configured"

**Where:** Sending newsletter

**Cause:** SMTP or SendGrid credentials not set

**Quick Fix:**
1. Go to Settings → Email Configuration
2. Choose SMTP or SendGrid
3. Enter credentials
4. Click "Test Email" to verify
5. Click "Save Config"

---

### 7. ❌ YouTube/X Scraper Not Working

**Where:** Scraping content

**Error Message:** `"YouTube API client not initialized"` or `"X API client not initialized"`

**Cause:** Missing API keys

**Quick Fix:**
1. Get API keys:
   - YouTube: https://console.cloud.google.com/
   - X/Twitter: https://developer.twitter.com/
2. Add to `.env` file:
   ```
   YOUTUBE_API_KEY=AIzaSy...
   X_API_KEY=abcd1234...
   X_API_SECRET=secret123...
   ```
3. Restart backend

**Or** use Reddit/RSS/Blog sources (no API keys needed)

---

### 8. ❌ CORS Error (Network Request Blocked)

**Where:** Any API call from frontend

**Error Message:** `"Blocked by CORS policy"`

**Cause:** Backend not allowing frontend origin

**Quick Fix:**
1. Check `.env.local` has correct backend URL
2. Check backend `CORS_ORIGINS` includes frontend URL
3. Restart both frontend and backend

---

### 9. ⚠️ Hydration Error (Next.js)

**Where:** Page load in development

**Error Message:** `"Text content does not match server-rendered HTML"`

**Cause:** Client-side and server-side rendering mismatch

**Quick Fix:**
- Usually safe to ignore in development
- Refresh page
- If persists: Check for dynamic content rendered on server

---

### 10. ❌ "Workspace not found" (403)

**Where:** Trying to access workspace data

**Cause:** User not a member of the workspace

**Quick Fix:**
1. Check you're logged in with correct account
2. Workspace owner must add you as member
3. Or switch to a workspace you own

---

**See all errors:** [COMPLETE_BACKEND_FRONTEND_MAPPING.md → Common Errors](./COMPLETE_BACKEND_FRONTEND_MAPPING.md#common-errors-quick-reference)

---

## 📚 When to Use Which Document

### Use QUICK_START_GUIDE.md (This Doc) When:
✅ You need an answer RIGHT NOW
✅ You want to find a button quickly
✅ You got an error and need quick fix
✅ You're new and don't know where to start

### Use BUTTON_REFERENCE_GUIDE.md When:
✅ You need detailed button flow (what happens step-by-step)
✅ You're confused about duplicate buttons (Generate vs Regenerate)
✅ You want to see user perspective (what user sees on screen)
✅ You need to understand timing (how long things take)

### Use COMPLETE_BACKEND_FRONTEND_MAPPING.md When:
✅ You want to understand a feature deeply
✅ You're adding a new feature
✅ You need database schema info
✅ You want to see all API endpoints for a module
✅ You need type definitions

### Use FIX_STATUS.md When:
✅ You want to know what was recently fixed
✅ You're testing new fixes
✅ You want to see known issues list

---

## 🔧 Quick Debugging Workflow

**Problem → Solution in 5 Steps:**

```
1. Identify What's Broken
   ↓
   Button not working? → Check Button Quick Reference
   API failing? → Check API Quick Reference
   Error message? → Check Common Issues

2. Get Exact Error
   ↓
   Open DevTools → Console + Network tab
   Copy error message

3. Look Up Error
   ↓
   Search in Common Issues section (above)
   Or search in COMPLETE_BACKEND_FRONTEND_MAPPING.md

4. Check Backend Logs
   ↓
   tail -f backend/logs/app.log
   Look for matching error timestamp

5. Apply Fix
   ↓
   Follow the fix instructions
   Restart backend if needed
   Clear browser cache
   Test again
```

---

## 🎓 Learning Path for Beginners

### Week 1: Core Features
**Day 1-2:** Authentication
- Read: [COMPLETE_BACKEND_FRONTEND_MAPPING.md → Authentication](./COMPLETE_BACKEND_FRONTEND_MAPPING.md#1-authentication)
- Try: Log in, log out, check localStorage for token

**Day 3-4:** Content Scraping
- Read: [COMPLETE_BACKEND_FRONTEND_MAPPING.md → Content Scraping](./COMPLETE_BACKEND_FRONTEND_MAPPING.md#3-content-scraping)
- Try: Configure Reddit source, scrape content, view items

**Day 5-7:** Newsletter Generation
- Read: [COMPLETE_BACKEND_FRONTEND_MAPPING.md → Newsletters](./COMPLETE_BACKEND_FRONTEND_MAPPING.md#4-newsletters)
- Try: Generate newsletter, preview, edit draft

### Week 2: Advanced Features
**Day 8-10:** Email Delivery
- Configure SMTP/SendGrid
- Send test email
- Send to subscribers

**Day 11-12:** Scheduling
- Create scheduled job
- Test "run now" feature

**Day 13-14:** Analytics
- Track email opens
- Track clicks
- View dashboard stats

---

## 💡 Pro Tips

### Debugging Faster
1. **Keep DevTools open** - Console + Network tabs always visible
2. **Use backend logs** - `tail -f backend/logs/app.log` in separate terminal
3. **Check database directly** - Use Supabase dashboard SQL editor for quick queries
4. **Test in isolation** - Test one button at a time, not entire flows

### Understanding Flows Faster
1. **Start with data flow diagrams** - ASCII art in COMPLETE_BACKEND_FRONTEND_MAPPING.md
2. **Follow one request** - Pick one button, trace it from click → response
3. **Use browser Network tab** - See exact payload and response
4. **Read example requests** - Copy-paste format from docs

### Fixing Bugs Faster
1. **Check recent fixes first** - FIX_STATUS.md lists what was just fixed
2. **Verify backend restarted** - Old code might still be running
3. **Clear browser cache** - Old JavaScript might be cached
4. **Check environment variables** - Missing API keys cause many errors

---

**Last Updated:** 2025-10-23
**Version:** 1.0
**Maintained By:** Documentation system (auto-updated with code changes)
