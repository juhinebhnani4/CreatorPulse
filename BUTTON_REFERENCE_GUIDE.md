# 🖱️ Complete Button Reference & Disambiguation Guide

**Every Button Explained with User Flows**

📍 **You are here:** Button Reference Guide (Button Lookup & Disambiguation)

**Other documentation:**
- 🚀 **Quick answers & debugging** → [QUICK_START_GUIDE.md](./QUICK_START_GUIDE.md)
- 📖 **Feature deep dive & architecture** → [COMPLETE_BACKEND_FRONTEND_MAPPING.md](./COMPLETE_BACKEND_FRONTEND_MAPPING.md)
- 🔧 **Recent fixes & known issues** → [FIX_STATUS.md](./FIX_STATUS.md)

---

## 📋 Table of Contents

1. [Part 1: Quick Lookup Tables](#part-1-quick-lookup-tables)
2. [Part 2: The Confusing Duplicates (Disambiguation)](#part-2-the-confusing-duplicates)
3. [Part 3: Top 20 Button Detailed Flows](#part-3-top-20-button-detailed-flows)
4. [Part 4: All Remaining Buttons](#part-4-all-remaining-buttons)
5. [Part 5: Reverse API Lookup](#part-5-reverse-api-lookup)

---

## Part 1: Quick Lookup Tables

### 📊 By Page

#### Dashboard (app/page.tsx) - 10 Primary Buttons

| Button | Handler | API | User Flow Summary |
|--------|---------|-----|-------------------|
| "Scrape Content" | `handleScrapeContent()` | `POST /api/v1/content/scrape` | Click → 15s scraping → Toast "25 items" → Auto-generates → Opens preview |
| "Generate Newsletter" | `handleGenerateNow()` | Opens `GenerationSettingsModal` | Click → Modal opens → Pick settings → Click "Generate" in modal → API call |
| "Regenerate with New Content" | `handleGenerateNow()` | Opens `GenerationSettingsModal` | Same as "Generate" (just different wording when draft is stale) |
| "Preview Draft" | `handlePreviewDraft()` | None (local) | Click → `DraftEditorModal` opens with latest newsletter |
| "Send Now" | `handleSendNow()` | Opens `SendConfirmationModal` | Click → Modal opens → Confirm → `POST /api/v1/delivery/send` |
| "Add Source" | `handleAddSource()` | Opens `AddSourceModal` | Click → Modal opens → Pick source type → Add → `PUT /api/v1/workspaces/{id}/config` |
| "Pause Source" | `handlePauseSource(id)` | `PUT /api/v1/workspaces/{id}/config` | Click → Source disabled → Config saved |
| "Resume Source" | `handleResumeSource(id)` | `PUT /api/v1/workspaces/{id}/config` | Click → Source enabled → Config saved |
| "Edit Article" | `handleEditArticle(item)` | `PUT /api/v1/content/{id}` | Click → Article card becomes editable → Auto-saves on blur |
| "Logout" | `handleLogout()` | `POST /api/v1/auth/logout` | Click → Token cleared → Redirect to /login |

#### Content Page (app/content/page.tsx) - 8 Actions

| Action | Handler | API | User Flow Summary |
|--------|---------|-----|-------------------|
| "Scrape Now" | `handleScrape()` | `POST /api/v1/content/scrape` | Click → 15s scraping → List refreshes with new items |
| Source Filter (dropdown) | `setSourceFilter()` | `GET /api/v1/content/workspaces/{id}/sources/{source}` | Change → List filters by source type (reddit/rss/etc) |
| Days Filter (dropdown) | `setDaysFilter()` | `GET /api/v1/content/workspaces/{id}?days=N` | Change → List shows content from last N days |
| Search (input) | `setSearchQuery()` | None (local filter) | Type → List filters by title/content match |
| "Keep" (👍) | `handleFeedback(id, 'positive')` | `POST /api/v1/feedback/items/{id}/rate` | Click → Thumbs up turns green → Item scored higher in future newsletters |
| "Skip" (👎) | `handleFeedback(id, 'negative')` | `POST /api/v1/feedback/items/{id}/rate` | Click → Thumbs down turns red → Item scored lower in future newsletters |
| External Link | None (navigate) | None | Click → Opens source URL in new tab |
| Delete Item | `handleDelete(id)` | `DELETE /api/v1/content/{id}` | Click → Confirmation → Item removed |

#### History Page (app/history/page.tsx) - 10 Actions

| Button/Action | Handler | API | User Flow Summary |
|--------------|---------|-----|-------------------|
| Select All (checkbox) | `toggleSelectAll()` | None (local state) | Click → All newsletters selected/deselected |
| Select Individual (checkbox) | `toggleSelection(id)` | None (local state) | Click → Newsletter added/removed from selection |
| "Delete Selected" | `handleBulkDelete()` | `DELETE /api/v1/newsletters/{id}` (multiple) | Click → Confirmation → All selected newsletters deleted |
| "View" | `handleView(id)` | None (navigate) | Click → Navigate to newsletter detail page |
| "Edit" | `handleEdit(id)` | None (navigate) | Click → Navigate to newsletter editor (drafts only) |
| "Regenerate" | `handleRegenerate(id)` | `POST /api/v1/newsletters/generate` | Click → Generates new version with latest content |
| "Duplicate" | `handleDuplicate(id)` | `POST /api/v1/newsletters/generate` | Click → Creates copy with "(Copy)" suffix |
| "Resend" | `handleResend(id)` | Not implemented | Click → Shows toast "Coming soon" |
| "Delete" (single) | `handleDelete(id)` | `DELETE /api/v1/newsletters/{id}` | Click → Confirmation → Newsletter deleted |
| Date Filter (dropdown) | `setDateFilter()` | None (local filter) | Change → List filters by date range |

#### Subscribers Page (app/subscribers/page.tsx) - 8 Actions

| Button/Action | Handler | API | User Flow Summary |
|--------------|---------|-----|-------------------|
| "Add Subscriber" | Opens modal | `POST /api/v1/subscribers` | Click → Modal opens → Enter email → Add |
| "Import CSV" | Opens modal | `POST /api/v1/subscribers/bulk` | Click → Modal opens → Upload CSV → Parse → Import |
| "Export CSV" | `handleExportCSV()` | None (local) | Click → Downloads subscribers.csv file |
| Select All (checkbox) | `toggleSelectAll()` | None (local) | Click → All subscribers selected/deselected |
| Select Individual (checkbox) | `toggleSelection(id)` | None (local) | Click → Subscriber added/removed from selection |
| "Delete Selected" | `handleBulkDelete()` | `DELETE /api/v1/subscribers/{id}` (multiple) | Click → Confirmation → All selected deleted |
| Delete (trash icon) | `handleDelete(id)` | `DELETE /api/v1/subscribers/{id}` | Click → Confirmation → Subscriber deleted |
| Search (input) | `setSearchQuery()` | None (local) | Type → List filters by email/name |
| Status Filter (dropdown) | `setStatusFilter()` | `GET /api/v1/subscribers/workspaces/{id}?status=X` | Change → List filters by status (subscribed/unsubscribed/bounced) |

#### Settings Page (app/settings/page.tsx) - 25+ Buttons Across 10 Sections

**Note:** Settings is a hub page with 10 sidebar sections. Each section has 2-5 buttons.

| Section | Key Buttons | APIs Used |
|---------|-------------|-----------|
| **Sources** | Add Source, Edit Source, Delete Source, Test Source, Save Sources | `PUT /api/v1/workspaces/{id}/config` |
| **Schedule** | Create Schedule, Pause Job, Resume Job, Run Now, Delete Job | `POST /api/v1/scheduler`, `POST /api/v1/scheduler/{id}/pause`, etc. |
| **Subscribers** | (Same as Subscribers page - embedded here) | Subscriber APIs |
| **Email** | Save Config, Test Email | `PUT /api/v1/workspaces/{id}/config`, `POST /api/v1/delivery/send` (test) |
| **Workspace** | Update Name, Delete Workspace, Add Member, Remove Member | `PUT /api/v1/workspaces/{id}`, `DELETE /api/v1/workspaces/{id}` |
| **API Keys** | Save Keys, Test API | `PUT /api/v1/workspaces/{id}/config` |
| **Style** | Train Style, Test Style, Delete Style | `POST /api/v1/style/train`, `POST /api/v1/style/test` |
| **Trends** | Detect Trends, Delete Trend | `POST /api/v1/trends/detect`, `DELETE /api/v1/trends/{id}` |
| **Analytics** | Export Data, Recalculate Stats | `GET /api/v1/analytics/workspaces/{id}/export` |
| **Feedback** | Set Preferences | `POST /api/v1/feedback/preferences` |

*See Part 4 for detailed button list per section*

---

### 🔌 By API Endpoint (Reverse Lookup)

**"Which buttons call this API?"**

| API Endpoint | Called By Buttons | Count |
|-------------|------------------|-------|
| `POST /api/v1/content/scrape` | Dashboard "Scrape Content", Content page "Scrape Now", UnifiedSourceSetup (auto-scrape) | 3 |
| `POST /api/v1/newsletters/generate` | Dashboard "Generate", Dashboard "Regenerate", History "Regenerate", History "Duplicate", Auto-generation (after scrape) | 5 |
| `PUT /api/v1/newsletters/{id}` | Draft Editor "Save Draft", Auto-save (2-sec debounce) | 2 |
| `POST /api/v1/delivery/send` | Dashboard "Send Now", Draft Editor "Send Now", Draft Editor "Send Test", Settings "Test Email" | 4 |
| `PUT /api/v1/workspaces/{id}/config` | Settings "Save Sources", Settings "Save Email", Settings "Save API Keys", Dashboard "Pause Source", Dashboard "Resume Source", Dashboard "Add Source" | 6+ |
| `DELETE /api/v1/newsletters/{id}` | History "Delete" (single), History "Delete Selected" (bulk) | 2 |
| `POST /api/v1/subscribers` | Subscribers "Add Subscriber", Settings Subscribers "Add" | 2 |
| `POST /api/v1/subscribers/bulk` | Subscribers "Import CSV", Settings Subscribers "Import" | 2 |
| `DELETE /api/v1/subscribers/{id}` | Subscribers "Delete" (single), Subscribers "Delete Selected" (bulk) | 2 |
| `POST /api/v1/scheduler` | Settings Schedule "Create Schedule" | 1 |
| `POST /api/v1/scheduler/{id}/pause` | Settings Schedule "Pause Job" | 1 |
| `POST /api/v1/scheduler/{id}/resume` | Settings Schedule "Resume Job" | 1 |
| `POST /api/v1/scheduler/{id}/run-now` | Settings Schedule "Run Now" | 1 |
| `POST /api/v1/feedback/items/{id}/rate` | Content page "Keep" (👍), Content page "Skip" (👎) | 2 |
| `POST /api/v1/style/train` | Settings Style "Train Style" | 1 |
| `POST /api/v1/trends/detect` | Settings Trends "Detect Trends" | 1 |

---

## Part 2: The Confusing Duplicates

### 🔄 "Generate" vs "Regenerate" Confusion

**Problem:** Users see 5 different "Generate" buttons and don't understand which one does what.

#### The 5 "Generate" Buttons

**Button 1:** "Generate Draft Now" (Dashboard - empty state)
**Button 2:** "Regenerate with New Content" (Dashboard - stale state)
**Button 3:** "Regenerate Now" (Toast after scraping)
**Button 4:** "Generate" (Inside GenerationSettingsModal)
**Button 5:** Auto-generation (Hidden, triggers after scraping)

#### Reality: Only 2 Actual Actions

**Action 1:** Open the GenerationSettingsModal (Buttons 1-3)
- All three buttons just **open the modal**
- They're in different places for convenience
- NO API call happens yet

**Action 2:** Actually Generate Newsletter (Buttons 4-5)
- Button 4: User clicks "Generate" inside modal → API call
- Button 5: Automatic (1.5s after scraping) → API call

#### Detailed Flow: "Generate" Button Journey

```
User Context: Dashboard, no draft exists
  ↓
User clicks "Generate Draft Now" (Button 1)
  ↓
GenerationSettingsModal opens
  ↓
Modal shows settings:
  - Tone: [Professional|Casual|Technical|Friendly]
  - Max Items: [5-20] (slider)
  - Temperature: [0.5-1.0] (slider)
  - Custom Instructions: (textarea)
  ↓
User adjusts:
  - Tone = "Professional"
  - Max Items = 15
  - Temperature = 0.7
  ↓
User clicks "Generate" inside modal (Button 4) ← THIS is where API call happens
  ↓
Frontend:
  handleGenerateWithSettings({tone: "professional", maxItems: 15, temperature: 0.7})
    ↓
  newslettersApi.generate({workspace_id, tone, maxItems, temperature, customInstructions})
    ↓
  POST /api/v1/newsletters/generate
  {
    "workspace_id": "aec6120d-...",
    "tone": "professional",
    "max_items": 15,
    "temperature": 0.7,
    "custom_instructions": ""
  }
  ↓
Backend:
  newsletter_service.generate_newsletter(workspace_id, params)
    ↓
  Step 1: Fetch content from database (last 7 days)
    SELECT * FROM content_items WHERE workspace_id=? AND scraped_at > NOW() - INTERVAL '7 days'
    ORDER BY score DESC LIMIT 50
    ↓
  Step 2: Apply feedback ranking (boost liked +20%, penalize disliked -30%)
    ↓
  Step 3: Select top 15 items after ranking
    ↓
  Step 4: Load style profile (if trained)
    SELECT * FROM style_profiles WHERE workspace_id=?
    ↓
  Step 5: Build AI prompt
    System: "You are a newsletter writer with professional tone..."
    User: "Create newsletter from these 15 items: [summaries]"
    ↓
  Step 6: Call OpenAI API
    openai.ChatCompletion.create(
      model="gpt-4-turbo-preview",
      temperature=0.7,
      messages=[system_msg, user_msg]
    )
    ↓
  Step 7: Parse response (HTML + plain text)
    ↓
  Step 8: Save to database
    INSERT INTO newsletters (workspace_id, title, content_html, content_text, status='draft')
    INSERT INTO newsletter_content_items (newsletter_id, content_item_id) × 15
    ↓
  Returns: {success: true, newsletter: {...}}
  ↓
Frontend:
  Modal closes
    ↓
  Toast appears: "✓ Newsletter Generated"
    ↓
  DraftEditorModal opens automatically
    ↓
  User sees preview of newsletter with 15 articles
```

**Time:** ~10-15 seconds total (AI generation is the bottleneck)

#### Why Button 2 Says "Regenerate" Instead of "Generate"

**Context:** Draft already exists, but new content was scraped after the draft was created.

**Dashboard Logic:**
```typescript
if (draft exists && new_content_scraped_after_draft) {
  status = 'stale'
  button_text = "Regenerate with New Content"
  show_warning = "New content is available! Update your draft."
}
```

**User Perspective:**
- Orange/yellow warning badge
- Message: "New content is available!"
- Button says "Regenerate" (implies updating existing draft)

**Reality:**
- **Exact same action** as "Generate Draft Now"
- Opens same modal
- Calls same API
- **Creates NEW draft** (doesn't update existing one)
- Old draft is replaced (not appended)

**Why the naming is confusing:**
- Says "Regenerate" but actually creates new draft
- Users expect "update" but get "replace"
- Should say "Create New Draft with Latest Content" for clarity

#### Button 5: The Hidden Auto-Generation

**When:** Automatically triggers 1.5 seconds after scraping completes

**Code Location:** Dashboard `handleScrapeContent()` line 842

**Flow:**
```typescript
// After scraping completes
setTimeout(async () => {
  await handleGenerateWithSettings({
    tone: 'professional',
    maxItems: 15,
    temperature: 0.7,
  });
}, 1500);
```

**User Experience:**
```
User clicks "Scrape Content"
  ↓
[15 seconds pass - scraping happens]
  ↓
Toast: "✓ Scraped 25 items"
  ↓
[1.5 seconds pass - silence]
  ↓
[10 seconds pass - generating happens in background]
  ↓
Toast: "✓ Newsletter Generated"
  ↓
DraftEditorModal opens
```

**User doesn't see:**
- NO modal shown
- NO confirmation asked
- NO settings picked (uses defaults)

**Why it exists:**
- Convenience - user doesn't have to click "Generate" separately
- Reduces steps: Scrape → Generate (2 clicks) becomes just Scrape (1 click)

**Downside:**
- User loses control over settings (always uses defaults)
- Can be surprising if user didn't expect auto-generation
- Wastes API credits if user just wanted to scrape without generating

---

### 💾 "Save" Button Confusion

**Problem:** Three different "Save" buttons in different contexts do different things.

#### Save Context 1: Manual Save (Draft Editor)

**Button:** "Save" button in DraftEditorModal footer

**Handler:** `handleManualSave()`

**API:** `PUT /api/v1/newsletters/{id}`

**Flow:**
```
User edits subject line: "My Newsletter" → "This Week in AI"
  ↓
User clicks "Save" button manually
  ↓
handleManualSave()
  ↓
await newslettersApi.update(draftId, {subject_line: "This Week in AI"})
  ↓
PUT /api/v1/newsletters/{id}
{
  "subject_line": "This Week in AI"
}
  ↓
Backend: Updates title field in database (subject_line → title mapping)
  ↓
Toast: "✓ Saved - Your draft has been saved"
  ↓
Shows timestamp: "Last saved at 2:34 PM"
```

#### Save Context 2: Auto-Save (Draft Editor - Hidden)

**Button:** None (invisible, triggers automatically)

**Handler:** `useEffect()` with 2-second debounce

**API:** Same as above (`PUT /api/v1/newsletters/{id}`)

**Flow:**
```
User edits subject line: "My Newsletter" → "This Week in AI"
  ↓
[User stops typing]
  ↓
[2 seconds pass - debounce timer]
  ↓
Auto-save triggers
  ↓
await onSave({subject, items})
  ↓
PUT /api/v1/newsletters/{id}
  ↓
Shows: "Saving..." (brief indicator)
  ↓
Shows: "Last saved at 2:34 PM"
  ↓
NO toast (silent save)
```

**Why both exist:**
- Auto-save: Prevents data loss (user forgets to save)
- Manual save: User control (force save before closing)

#### Save Context 3: Save Settings (Settings Page)

**Button:** "Save Sources" / "Save Config" / "Save Keys" (various settings sections)

**Handler:** `handleSaveEmailConfig()` / `handleSaveAPIKeys()` / etc.

**API:** `PUT /api/v1/workspaces/{id}/config`

**Flow:**
```
User configures email settings:
  - Method: SMTP
  - Server: smtp.gmail.com
  - Username: myemail@gmail.com
  - Password: app_password_here
  ↓
User clicks "Save Config"
  ↓
handleSaveEmailConfig()
  ↓
await workspacesApi.updateConfig(workspaceId, {
  delivery: {
    method: 'smtp',
    smtp_server: 'smtp.gmail.com',
    smtp_username: 'myemail@gmail.com',
    smtp_password: 'app_password_here'
  }
})
  ↓
PUT /api/v1/workspaces/{id}/config
{
  "config": {
    "delivery": {...}
  }
}
  ↓
Backend: Merges new config with existing workspace config (JSONB field)
  ↓
Toast: "✓ Settings saved"
```

**Key Difference:**
- Context 1 & 2: Save **newsletter draft** (newsletters table)
- Context 3: Save **workspace settings** (workspace_configs table)
- Different APIs, different database tables, different data structures

---

### 📧 "Send" Button Confusion

**Problem:** Four "Send" variations in different places.

#### Send Variation 1: "Send Now" (Dashboard)

**Location:** Dashboard → Draft card footer (when status = 'ready')

**Handler:** `handleSendNow()`

**Flow:**
```
Click → Opens SendConfirmationModal → User confirms → POST /api/v1/delivery/send → Background send starts → Returns immediately (202)
```

**Characteristics:**
- ✅ Sends to ALL active subscribers
- ✅ Background (async) - doesn't wait for completion
- ✅ Adds tracking pixels and links
- ⏱️ Takes 5-10 minutes for 1,000 subscribers (user can navigate away)

#### Send Variation 2: "Send" Dropdown (Draft Editor)

**Location:** DraftEditorModal → Footer → "Send" dropdown with 3 options

**Options:**
- "Send Now" → Same as Variation 1
- "Send Test" → Variation 3 (below)
- "Schedule Send" → Variation 4 (below)

**Note:** This is just a menu that groups the other send variations.

#### Send Variation 3: "Send Test Email" (Test Modal)

**Location:** SendTestModal (opened from draft editor or dashboard)

**Handler:** `handleSendTest(email)`

**API:** `POST /api/v1/delivery/send` (with `test_email` parameter)

**Flow:**
```
Click → Modal opens → Enter email "myemail@example.com" → Click "Send Test"
  ↓
POST /api/v1/delivery/send
{
  "newsletter_id": "...",
  "workspace_id": "...",
  "test_email": "myemail@example.com"
}
  ↓
Backend: Sends to ONLY that email (ignores subscribers table)
  ↓
Waits for SMTP/SendGrid response (synchronous)
  ↓
[5-10 seconds pass]
  ↓
Returns: {status: "sent", recipient: "myemail@example.com"}
  ↓
Toast: "✓ Test email sent to myemail@example.com"
```

**Characteristics:**
- ✅ Sends to ONLY ONE email (specified by user)
- ✅ Synchronous (waits for completion)
- ✅ Adds tracking pixels and links
- ⏱️ Takes 5-10 seconds (user waits)

**Key Difference from Variation 1:**
- Variation 1: Async, all subscribers, returns immediately
- Variation 3: Sync, one email, waits for result

#### Send Variation 4: "Schedule Send" (Future Send)

**Location:** ScheduleSendModal

**Handler:** `handleScheduleSend(dateTime)`

**API:** `POST /api/v1/scheduler` (NOT delivery API!)

**Flow:**
```
Click → Modal opens → Pick date/time "Oct 25, 8:00 AM" → Click "Schedule"
  ↓
schedulerApi.createJob({
  workspace_id: "...",
  actions: ['send'],
  schedule: "0 8 25 10 *",  // Cron expression from date picker
  is_enabled: true
})
  ↓
POST /api/v1/scheduler
  ↓
Backend: Creates one-time scheduled job
  INSERT INTO scheduler_jobs (workspace_id, schedule, actions, is_enabled, next_run_at='2025-10-25 08:00:00')
  ↓
Returns: {job_id: "...", next_run_at: "2025-10-25T08:00:00Z"}
  ↓
Toast: "✓ Newsletter scheduled for Oct 25, 8:00 AM"
  ↓
[On Oct 25 at 8:00 AM - background worker runs job]
  ↓
POST /api/v1/delivery/send (triggered by scheduler)
  ↓
Newsletter sent to all subscribers
```

**Characteristics:**
- ✅ Creates scheduled job (doesn't send immediately)
- ✅ Uses scheduler API (different from delivery API)
- ✅ User picks exact date/time
- ⏱️ Sends at scheduled time (could be days/weeks later)

**Key Difference:**
- Variations 1-3: Send **NOW** (immediately or within seconds)
- Variation 4: Send **LATER** (scheduled for future date/time)

---

### 🔍 "Scrape" Duplicates (True Duplicates)

**Problem:** Three "Scrape" buttons in different locations.

#### Scrape Button 1: Dashboard

**Location:** Dashboard → Top right of content sources section

**Button:** "Scrape Content"

**Handler:** `handleScrapeContent()`

#### Scrape Button 2: Content Page

**Location:** Content page → Top right

**Button:** "Scrape Now"

**Handler:** `handleScrape()`

#### Scrape Button 3: UnifiedSourceSetup (Auto-Scrape)

**Location:** Dashboard → UnifiedSourceSetup component (hidden, triggered after bulk paste)

**Handler:** Auto-triggered after user pastes multiple sources

**Reality: ALL THREE ARE IDENTICAL**

They all call: `POST /api/v1/content/scrape`

**Flow (Identical for all 3):**
```
Click button (or auto-trigger)
  ↓
contentApi.scrape({workspace_id, sources: ["reddit", "rss", "blog"]})
  ↓
POST /api/v1/content/scrape
  ↓
Backend: content_service.scrape_content(workspace_id)
  ↓
For each enabled source:
  ├─ RedditScraper.scrape() → 15 items
  ├─ RSSFeedScraper.scrape() → 10 items
  └─ BlogScraper.scrape() → 5 items
  ↓
INSERT INTO content_items (30 rows)
  ↓
Returns: {total_items: 30, items_by_source: {reddit: 15, rss: 10, blog: 5}}
  ↓
Toast: "✓ Scraped 30 items from Reddit (15), RSS (10), Blog (5)"
  ↓
[If from Dashboard button] Auto-generates newsletter after 1.5s
  ↓
[If from Content page] Just refreshes list
```

**Why 3 identical buttons exist:**
- Button 1: Dashboard - Main hub, most common location
- Button 2: Content page - Convenience (user is already viewing content)
- Button 3: UnifiedSourceSetup - Automation (bulk paste sources → auto-scrape)

**These are TRULY duplicate** - no confusion, just convenience.

---

## Part 3: Top 20 Button Detailed Flows

### 🔵 Button 1: "Scrape Content" (Dashboard)

**Location:** Dashboard → Content Sources section → Top right

**Button Visual:**
- Default: Blue primary button "Scrape Content"
- Loading: Spinner + "Scraping..."
- Disabled: When no sources configured

**What User Sees:**
```
Click "Scrape Content"
  ↓
Button changes to "Scraping..." with spinner
  ↓
Toast appears: "🔄 Scraping content from 3 sources..."
  ↓
[15-30 seconds pass]
  ↓
Toast updates: "✓ Scraped 25 items from Reddit (15), RSS (10)"
  ↓
Content stats update: "25 new items (was 10, now 35 total)"
  ↓
New toast with action button:
  "✓ New Content Available - Scraped 25 items. [Regenerate Now]"
  ↓
[1.5 seconds pass - user doesn't see this]
  ↓
[10 seconds pass - generating in background]
  ↓
Toast: "✓ Newsletter Generated"
  ↓
DraftEditorModal opens automatically
  ↓
User sees preview of newsletter with 10 articles
```

**Handler Chain:**
```typescript
handleScrapeContent() {
  // Set loading state
  setIsScraping(true)

  // Show initial toast
  toast({title: "🔄 Scraping content from 3 sources..."})

  // Call API
  const result = await contentApi.scrape({
    workspace_id: currentWorkspace.id,
    sources: undefined,  // Uses all enabled sources from config
    limit_per_source: 25
  })

  // Update stats
  setContentStats(result.data)

  // Show success toast
  toast({
    title: "✓ Scraped 25 items",
    description: "Reddit (15), RSS (10)",
    action: <Button onClick={handleGenerateNow}>Regenerate Now</Button>
  })

  // Check if draft is now stale
  if (latestNewsletter && result.data.latest_scrape > latestNewsletter.generated_at) {
    setDraftStatus('stale')
  }

  // Auto-generate with default settings (1.5s delay)
  setTimeout(async () => {
    await handleGenerateWithSettings({
      tone: 'professional',
      maxItems: 15,
      temperature: 0.7
    })
  }, 1500)

  setIsScraping(false)
}
```

**Backend Processing:**
```python
# backend/services/content_service.py

async def scrape_content(workspace_id: str, sources: list = None):
    # Load workspace config
    config = await workspace_service.get_workspace_config(workspace_id)

    # Use enabled sources if not specified
    if not sources:
        sources = [s['type'] for s in config['sources'] if s['enabled']]

    results = {}

    # Scrape each source
    for source_type in sources:
        if source_type == 'reddit':
            scraper = RedditScraper(config)
            items = await scraper.scrape()  # Returns 15 items
            results['reddit'] = len(items)

            # Save to database
            for item in items:
                await db.table('content_items').insert({
                    'workspace_id': workspace_id,
                    'source': 'reddit',
                    'title': item['title'],
                    'content': item['content'],
                    'source_url': item['url'],
                    'author': item['author'],
                    'score': item['score'],
                    'scraped_at': datetime.utcnow()
                })

        # Similar for RSS, Blog, YouTube, X...

    return {
        'total_items': sum(results.values()),
        'items_by_source': results,
        'status': 'completed'
    }
```

**Time Breakdown:**
- User clicks button → API call starts: **<100ms**
- Backend scraping (3 sources in parallel): **15-30 seconds**
- Database inserts (25 items): **<1 second**
- Response returns to frontend: **<100ms**
- Auto-generate delay: **1.5 seconds**
- AI generation (OpenAI API): **10-15 seconds**
- Total time: **27-47 seconds**

**Dependencies:**
- ✅ Workspace must have at least 1 enabled source
- ✅ Reddit/RSS sources work without API keys
- ⚠️ YouTube requires `YOUTUBE_API_KEY` in .env
- ⚠️ X/Twitter requires `X_API_KEY`, `X_API_SECRET` in .env

**Edge Cases:**
1. **No sources configured:**
   - Error: "Please add content sources first"
   - Button disabled (gray)
   - Redirects to Settings → Sources

2. **No content found:**
   - Success response but 0 items
   - Toast: "No new content found. Sources may be empty or rate-limited."
   - No auto-generation (nothing to generate from)

3. **Rate limit hit:**
   - Reddit: 429 status code
   - Toast: "Rate limit exceeded. Wait 1 minute and try again."
   - Some sources succeed, others fail (partial success)

4. **Scraping fails:**
   - Network error or source down
   - Toast: "Failed to scrape Reddit. Check backend logs."
   - Other sources still process

**Related Buttons:**
- Content page → "Scrape Now" (identical functionality)
- UnifiedSourceSetup → Auto-scrape (identical functionality)

**Debug:**
- Backend log: `tail -f backend/logs/app.log` → Search for "scrape_content"
- Database check: `SELECT * FROM content_items WHERE workspace_id='...' ORDER BY scraped_at DESC LIMIT 10`
- Network tab: POST /api/v1/content/scrape → Check response payload

---

### 🔵 Button 2: "Generate Newsletter" (Dashboard)

**Location:** Dashboard → Draft card → Primary action

**Button Visual:**
- Default: Green button "Generate Draft Now"
- Stale state: Orange button "Regenerate with New Content"
- Loading: Spinner + "Generating..."

**What User Sees:**
```
Click "Generate Draft Now"
  ↓
GenerationSettingsModal opens
  ↓
Modal shows:
  - Tone dropdown: Professional | Casual | Technical | Friendly
  - Max Items slider: 5-20 (default: 10)
  - Temperature slider: 0.5-1.0 (default: 0.7)
  - Custom Instructions: (optional textarea)
  ↓
User picks:
  - Tone = Professional
  - Max Items = 15
  - Temperature = 0.7
  ↓
User clicks "Generate" button inside modal
  ↓
Modal shows loading spinner
  ↓
[10-15 seconds pass - AI is thinking]
  ↓
Modal closes
  ↓
Toast: "✓ Newsletter Generated"
  ↓
DraftEditorModal opens automatically
  ↓
User sees:
  - Subject line: "This Week in AI - Oct 23, 2025"
  - 15 articles with titles, summaries, images
  - "Edit" and "Preview" tabs
  - "Save", "Send Test", "Send Now" buttons
```

**Handler Chain:**
```typescript
// Dashboard: User clicks "Generate Draft Now"
handleGenerateNow() {
  setShowGenerationSettings(true)  // Opens modal
}

// GenerationSettingsModal: User clicks "Generate" inside modal
handleGenerate() {
  const settings = {
    tone: selectedTone,
    maxItems: maxItemsSlider,
    temperature: temperatureSlider,
    customInstructions: instructionsText
  }

  onGenerate(settings)  // Calls parent handler
}

// Dashboard: Receives settings from modal
handleGenerateWithSettings(settings) {
  setDraftStatus('generating')

  // Close modal
  setShowGenerationSettings(false)

  try {
    // Call API
    const newsletter = await newslettersApi.generate({
      workspace_id: currentWorkspace.id,
      tone: settings.tone,
      max_items: settings.maxItems,
      temperature: settings.temperature,
      custom_instructions: settings.customInstructions
    })

    // Update state
    setLatestNewsletter(newsletter)
    setDraftStatus('ready')

    // Show success
    toast({
      title: "✓ Newsletter Generated",
      description: "Your newsletter is ready to review"
    })

    // Auto-open editor
    setShowDraftEditor(true)

  } catch (error) {
    setDraftStatus('empty')
    toast({
      title: "Error",
      description: error.message,
      variant: "destructive"
    })
  }
}
```

**Backend Processing:**
```python
# backend/services/newsletter_service.py

async def generate_newsletter(workspace_id, tone, max_items, temperature, custom_instructions):
    # Step 1: Fetch recent content (last 7 days)
    content_items = await db.table('content_items') \
        .select('*') \
        .eq('workspace_id', workspace_id) \
        .gte('scraped_at', datetime.utcnow() - timedelta(days=7)) \
        .order('score', desc=True) \
        .limit(50) \
        .execute()

    if len(content_items.data) == 0:
        raise ValueError("No content found. Please scrape content first.")

    # Step 2: Apply feedback ranking
    ranked_items = await feedback_service.apply_feedback_ranking(
        workspace_id, content_items.data
    )
    # Boosts liked items +20%, penalizes disliked -30%

    # Step 3: Select top N items
    selected_items = ranked_items[:max_items]

    # Step 4: Load style profile (if exists)
    style_profile = await style_service.get_style_profile(workspace_id)

    # Step 5: Build AI prompt
    system_prompt = f"""You are a newsletter writer with {tone} tone.
    {style_profile['instructions'] if style_profile else ''}
    {custom_instructions}"""

    user_prompt = f"""Create a newsletter from these {len(selected_items)} items:

    {format_items_for_prompt(selected_items)}

    Requirements:
    - Write a catchy title
    - Create HTML content with proper formatting
    - Include all items with summaries
    - Match the {tone} tone"""

    # Step 6: Call OpenAI API
    response = await openai.ChatCompletion.acreate(
        model="gpt-4-turbo-preview",
        temperature=temperature,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )

    generated_content = response.choices[0].message.content

    # Step 7: Parse response (extract HTML and plain text)
    content_html = extract_html(generated_content)
    content_text = html_to_text(content_html)

    # Step 8: Save to database
    newsletter = await db.table('newsletters').insert({
        'workspace_id': workspace_id,
        'title': extract_title(generated_content),
        'content_html': content_html,
        'content_text': content_text,
        'model_used': 'gpt-4-turbo-preview',
        'temperature': temperature,
        'tone': tone,
        'status': 'draft',
        'generated_at': datetime.utcnow(),
        'content_items_count': len(selected_items)
    }).execute()

    newsletter_id = newsletter.data[0]['id']

    # Step 9: Link content items
    for item in selected_items:
        await db.table('newsletter_content_items').insert({
            'newsletter_id': newsletter_id,
            'content_item_id': item['id']
        }).execute()

    return newsletter.data[0]
```

**Time Breakdown:**
- User clicks → Modal opens: **<100ms**
- User picks settings → Clicks generate: **5-30 seconds** (user action)
- API call starts: **<100ms**
- Fetch content from DB: **<500ms**
- Apply feedback ranking: **<100ms**
- Load style profile: **<100ms**
- Build prompt: **<10ms**
- Call OpenAI API: **10-15 seconds** (bottleneck)
- Parse response: **<100ms**
- Save to database: **<500ms**
- Total backend time: **11-17 seconds**
- Total user experience: **16-47 seconds**

**Dependencies:**
- ✅ Content items must exist (at least 1)
- ✅ `OPENAI_API_KEY` or `OPENROUTER_API_KEY` must be set in .env
- ⚠️ Style profile is optional (works without it)
- ⚠️ Feedback data is optional (works without it)

**Edge Cases:**
1. **No content exists:**
   - Error: "No content found for workspace. Please scrape content first."
   - Suggests clicking "Scrape Content"

2. **API key missing:**
   - Error: "OpenAI API key not configured. Check .env file."
   - Detailed instructions in error message

3. **OpenAI rate limit:**
   - Error: "Rate limit exceeded. You've hit OpenAI's usage limit."
   - Suggests waiting or upgrading OpenAI plan

4. **OpenAI timeout:**
   - Error: "Request timed out after 30 seconds. Try again."
   - Retry button in toast

5. **Invalid response from AI:**
   - Error: "Failed to parse AI response. Try regenerating."
   - Logs full response for debugging

**Related Buttons:**
- Dashboard → "Regenerate with New Content" (identical, just different wording)
- Dashboard → "Regenerate Now" (in toast) (identical)
- History page → "Regenerate" (identical)
- Auto-generation (hidden) (identical, uses defaults)

**Debug:**
- Backend log: `tail -f backend/logs/app.log` → Search for "generate_newsletter"
- OpenAI dashboard: Check API usage and errors
- Database: `SELECT * FROM newsletters WHERE workspace_id='...' ORDER BY generated_at DESC LIMIT 1`
- Network tab: POST /api/v1/newsletters/generate → Check request/response

---

### 🔵 Button 3: "Send Now" (Dashboard)

**Location:** Dashboard → Draft card footer (when status = 'ready')

**Button Visual:**
- Default: Green button "Send Now" with send icon
- Disabled: When status ≠ 'ready' (draft empty/generating/stale)
- Loading: Shows "Sending..." (brief)

**What User Sees:**
```
Click "Send Now"
  ↓
SendConfirmationModal opens
  ↓
Modal shows:
  - Newsletter title: "This Week in AI - Oct 23"
  - Preview: First 200 chars of content
  - Subscriber count: "Send to 1,234 active subscribers?"
  - Warning: "⚠️ This action cannot be undone"
  - Buttons: [Cancel] [Send to 1,234 Subscribers]
  ↓
User clicks "Send to 1,234 Subscribers"
  ↓
Modal shows brief loading spinner (<1s)
  ↓
Modal closes
  ↓
Toast appears: "✓ Sending newsletter to 1,234 subscribers"
  ↓
Draft card updates:
  - Status badge: "Sent" (green)
  - "Send Now" button disappears
  - New button: "View Analytics"
  - Shows: "Sent Oct 23, 2:45 PM"
  ↓
[User can navigate away - sending happens in background]
  ↓
[5-10 minutes later - backend finishes sending to all 1,234]
  ↓
User can check Analytics page to see:
  - Sent: 1,234 (100%)
  - Delivered: 1,220 (98.9%)
  - Opened: 245 (20%) [increases over time]
  - Clicked: 98 (8%)
```

**Handler Chain:**
```typescript
// Dashboard: User clicks "Send Now"
handleSendNow() {
  if (!latestNewsletter || latestNewsletter.status !== 'draft') {
    toast({
      title: "No Draft Available",
      description: "Please generate a newsletter first"
    })
    return
  }

  setShowSendConfirmation(true)  // Opens modal
}

// SendConfirmationModal: User clicks "Confirm"
handleConfirm() {
  setIsSending(true)

  try {
    await deliveryApi.send({
      newsletter_id: newsletter.id,
      workspace_id: workspace.id
    })

    toast({
      title: "✓ Sending newsletter",
      description: `Newsletter delivery started to ${subscriberCount} subscribers`
    })

    // Refresh data to show new status
    await fetchData()

    onClose()
  } catch (error) {
    toast({
      title: "Error",
      description: error.message,
      variant: "destructive"
    })
  } finally {
    setIsSending(false)
  }
}
```

**Backend Processing:**
```python
# backend/api/v1/delivery.py

@router.post("/send")
async def send_newsletter(request: DeliveryRequest, background_tasks: BackgroundTasks):
    # Returns immediately (202 Accepted)
    background_tasks.add_task(
        delivery_service.send_newsletter,
        newsletter_id=request.newsletter_id,
        workspace_id=request.workspace_id
    )

    return {
        'status': 'sending',
        'message': 'Newsletter delivery started'
    }

# backend/services/delivery_service.py (runs in background)

async def send_newsletter(newsletter_id, workspace_id):
    # Step 1: Fetch newsletter
    newsletter = await db.table('newsletters').select('*').eq('id', newsletter_id).single().execute()
    content_html = newsletter.data['content_html']

    # Step 2: Fetch subscribers
    subscribers = await db.table('subscribers') \
        .select('*') \
        .eq('workspace_id', workspace_id) \
        .eq('status', 'subscribed') \
        .execute()

    # Step 3: For each subscriber (async loop)
    for subscriber in subscribers.data:
        try:
            # Inject tracking pixel
            html_with_tracking = inject_tracking_pixel(
                content_html,
                newsletter_id,
                subscriber['email']
            )

            # Inject click tracking
            html_with_tracking = inject_tracking_links(
                html_with_tracking,
                newsletter_id,
                subscriber['email']
            )

            # Send email (SMTP or SendGrid)
            if config['delivery']['method'] == 'smtp':
                await send_via_smtp(
                    to=subscriber['email'],
                    subject=newsletter['title'],
                    html=html_with_tracking
                )
            else:  # SendGrid
                await send_via_sendgrid(
                    to=subscriber['email'],
                    subject=newsletter['title'],
                    html=html_with_tracking
                )

            # Record success
            await db.table('delivery_logs').insert({
                'newsletter_id': newsletter_id,
                'subscriber_email': subscriber['email'],
                'status': 'sent',
                'sent_at': datetime.utcnow()
            }).execute()

            # Record analytics event
            await db.table('email_analytics_events').insert({
                'newsletter_id': newsletter_id,
                'recipient_email': subscriber['email'],
                'event_type': 'sent',
                'timestamp': datetime.utcnow()
            }).execute()

        except Exception as e:
            # Record failure
            await db.table('delivery_logs').insert({
                'newsletter_id': newsletter_id,
                'subscriber_email': subscriber['email'],
                'status': 'failed',
                'error_message': str(e),
                'sent_at': datetime.utcnow()
            }).execute()

    # Step 4: Update newsletter status
    await db.table('newsletters').update({
        'status': 'sent',
        'sent_at': datetime.utcnow()
    }).eq('id', newsletter_id).execute()
```

**Time Breakdown:**
- User clicks → Modal opens: **<100ms**
- User confirms → API call: **<100ms**
- Backend returns 202 (immediately): **<500ms**
- Modal closes, toast shows: **<100ms**
- **Total user waits: <1 second**

**Background Processing (User doesn't wait):**
- For each subscriber:
  - Inject tracking: **<10ms**
  - Send email: **200-500ms** (SMTP) or **50-100ms** (SendGrid)
  - Record logs: **<50ms**
- For 1,000 subscribers:
  - Total time: **5-10 minutes** (throttled to avoid rate limits)

**Dependencies:**
- ✅ Newsletter must be in 'draft' status
- ✅ At least 1 active subscriber must exist
- ✅ Email config (SMTP or SendGrid) must be set
- ✅ Newsletter must have `content_html` field

**Edge Cases:**
1. **No subscribers:**
   - Error: "No active subscribers found. Add subscribers first."
   - Button disabled

2. **Email not configured:**
   - Error: "Email delivery not configured. Go to Settings → Email."
   - Links to settings page

3. **Newsletter already sent:**
   - Button hidden (status ≠ 'draft')
   - Shows "Sent Oct 23, 2:45 PM" instead

4. **SMTP authentication fails:**
   - Some emails fail, others succeed
   - Shows summary: "Sent 980/1,000 (20 failed)"
   - Failed emails logged with error message

5. **Rate limit (SendGrid/SMTP):**
   - Automatically throttles sending
   - Spreads over longer time period
   - All eventually sent (unless hard failure)

**Related Buttons:**
- DraftEditorModal → "Send Now" dropdown option (identical)
- Settings → Email → "Test Email" (similar, sends to 1 email only)

**Debug:**
- Backend log: `tail -f backend/logs/app.log` → Search for "send_newsletter"
- Database: `SELECT * FROM delivery_logs WHERE newsletter_id='...' ORDER BY sent_at DESC`
- Analytics: Check `email_analytics_events` table for 'sent' events
- SMTP logs: Check Gmail "Sent" folder or SendGrid dashboard

---

### 🔵 Button 4: "Preview Draft" (Dashboard)

**Location:** Dashboard → Draft card → "Preview" button

**What User Sees:**
```
Click "Preview"
  ↓
DraftEditorModal opens
  ↓
User sees newsletter in full detail:
  - Subject line field (editable)
  - HTML preview of content
  - "Edit" tab with rich editor
  - "Preview" tab with final look
  - Footer: [Save] [Send Test] [Send Now]
```

**Handler:** `handlePreviewDraft()` → Opens modal with latest newsletter, NO API call

**Time:** Instant (<100ms)

**Dependencies:** Newsletter must exist (status = 'draft' or 'ready')

---

### 🔵 Button 5: "Add Source" (Dashboard)

**Location:** Dashboard → Content Sources section → "Add Source" button

**What User Sees:**
```
Click "Add Source"
  ↓
AddSourceModal opens with source type picker:
  [Reddit] [RSS] [YouTube] [X/Twitter] [Blog]
  ↓
User picks "Reddit"
  ↓
Modal shows Reddit-specific fields:
  - Subreddit names (comma-separated)
  - Sort by: [Hot|New|Top]
  - Limit: 25
  ↓
User enters: "MachineLearning, artificial"
  ↓
User clicks "Add Source"
  ↓
PUT /api/v1/workspaces/{id}/config (updates sources array)
  ↓
Toast: "✓ Source added: Reddit - MachineLearning, artificial"
  ↓
Dashboard sources list updates with new card
```

**API:** `PUT /api/v1/workspaces/{id}/config`

**Backend:** Merges new source into `config.sources[]` JSONB field

**Time:** <1 second

---

### 🔵 Button 6: "Pause Source" / "Resume Source" (Dashboard)

**Location:** Dashboard → Each source card → Toggle icon

**What User Sees:**
```
Click "Pause" on Reddit source
  ↓
Icon changes from ▶️ to ⏸️
  ↓
PUT /api/v1/workspaces/{id}/config (sets source.enabled = false)
  ↓
Toast: "✓ Reddit source paused"
  ↓
Next scrape will skip this source

Click "Resume" on Reddit source
  ↓
Icon changes from ⏸️ to ▶️
  ↓
PUT /api/v1/workspaces/{id}/config (sets source.enabled = true)
  ↓
Toast: "✓ Reddit source resumed"
```

**API:** Same config update, just toggles `enabled` boolean

**Time:** <500ms

---

### 🔵 Button 7: "Edit Article" (Dashboard Content Card)

**Location:** Dashboard → Content items list → Individual article card → Edit icon

**What User Sees:**
```
Click edit icon on article
  ↓
Card becomes editable:
  - Title field becomes textarea
  - Summary field becomes textarea
  - [Save] [Cancel] buttons appear
  ↓
User edits title: "Original Title" → "Better Title"
  ↓
User clicks "Save"
  ↓
PUT /api/v1/content/{id} {title: "Better Title"}
  ↓
Card returns to read-only mode
  ↓
Toast: "✓ Article updated"
```

**API:** `PUT /api/v1/content/{id}`

**Backend:** Updates content_items table

**Time:** <500ms

**Auto-save:** Also triggers on blur after 2-second debounce

---

### 🔵 Button 8: "Keep" (👍) / "Skip" (👎) - Content Page

**Location:** Content page → Each article card → Thumbs up/down icons

**What User Sees:**
```
Click 👍 on article
  ↓
Icon turns green
  ↓
POST /api/v1/feedback/items/{id}/rate {rating: 'positive'}
  ↓
No toast (silent feedback)
  ↓
Future newsletters will prioritize this item (+20% boost)

Click 👎 on article
  ↓
Icon turns red
  ↓
POST /api/v1/feedback/items/{id}/rate {rating: 'negative'}
  ↓
Future newsletters will deprioritize this item (-30% penalty)
```

**API:** `POST /api/v1/feedback/items/{id}/rate`

**Backend:** Records in feedback_ratings table, applied during generation

**Time:** <200ms

---

### 🔵 Button 9: Source Filter (Content Page)

**Location:** Content page → Top filter bar → "Source" dropdown

**What User Sees:**
```
User selects "Reddit" from dropdown
  ↓
GET /api/v1/content/workspaces/{id}/sources/reddit
  ↓
List updates to show ONLY Reddit items
  ↓
Header updates: "Showing 45 Reddit articles"
```

**API:** `GET /api/v1/content/workspaces/{id}/sources/{source}`

**Time:** <500ms

---

### 🔵 Button 10: Days Filter (Content Page)

**Location:** Content page → Top filter bar → "Days" dropdown

**What User Sees:**
```
User selects "Last 3 days" from dropdown
  ↓
GET /api/v1/content/workspaces/{id}?days=3
  ↓
List updates to show items from last 3 days only
  ↓
Header updates: "Showing 28 items from last 3 days"
```

**API:** `GET /api/v1/content/workspaces/{id}?days={N}`

**Time:** <500ms

---

### 🔵 Button 11: "Select All" (History Page)

**Location:** History page → Table header → Checkbox

**What User Sees:**
```
Click "Select All" checkbox
  ↓
All newsletter checkboxes become checked
  ↓
Local state updates (NO API call)
  ↓
"Delete Selected" button activates
  ↓
Count updates: "5 selected"
```

**Handler:** `toggleSelectAll()` - Pure local state, no API

**Time:** Instant

---

### 🔵 Button 12: "Delete Selected" (History Page)

**Location:** History page → Bulk actions bar (appears when items selected)

**What User Sees:**
```
User has 5 newsletters selected
  ↓
Click "Delete Selected"
  ↓
Confirmation modal: "Delete 5 newsletters? This cannot be undone."
  ↓
User confirms
  ↓
DELETE /api/v1/newsletters/{id} (called 5 times in parallel)
  ↓
Progress indicator: "Deleting 3 of 5..."
  ↓
Toast: "✓ Deleted 5 newsletters"
  ↓
List refreshes, selected items removed
```

**API:** `DELETE /api/v1/newsletters/{id}` (multiple parallel calls)

**Time:** 1-3 seconds (depending on count)

---

### 🔵 Button 13: "View" (History Page)

**Location:** History page → Each newsletter row → "View" button

**What User Sees:**
```
Click "View" on newsletter
  ↓
Newsletter detail modal opens
  ↓
Shows:
  - Full HTML preview
  - Sent date and time
  - "View Analytics" link
  - "Resend" button (if sent)
```

**Handler:** Opens modal, NO API call (uses data already fetched)

**Time:** Instant

---

### 🔵 Button 14: "Regenerate" (History Page)

**Location:** History page → Each newsletter row → "Regenerate" button

**What User Sees:**
```
Click "Regenerate" on old newsletter
  ↓
POST /api/v1/newsletters/generate (same as Dashboard "Generate")
  ↓
Generates NEW newsletter with current content (not old content)
  ↓
[10-15 seconds pass]
  ↓
Toast: "✓ Newsletter regenerated"
  ↓
New draft appears in History page (at top)
```

**API:** `POST /api/v1/newsletters/generate` (identical to dashboard generate)

**Time:** 10-15 seconds

**Note:** Does NOT update the old newsletter, creates a NEW one

---

### 🔵 Button 15: "Duplicate" (History Page)

**Location:** History page → Each newsletter row → "Duplicate" button

**What User Sees:**
```
Click "Duplicate" on newsletter
  ↓
Creates copy with "(Copy)" suffix
  ↓
Toast: "✓ Newsletter duplicated"
  ↓
New newsletter appears: "This Week in AI (Copy)"
  ↓
Status: draft
```

**API:** `POST /api/v1/newsletters/{id}/duplicate`

**Backend:** Copies row with new ID, same content

**Time:** <1 second

---

### 🔵 Button 16: "Add Subscriber" (Subscribers Page)

**Location:** Subscribers page → Top right → "Add Subscriber" button

**What User Sees:**
```
Click "Add Subscriber"
  ↓
AddSubscriberModal opens
  ↓
User enters:
  - Email: "john@example.com"
  - Name: "John Doe" (optional)
  ↓
User clicks "Add"
  ↓
POST /api/v1/subscribers
  {
    "workspace_id": "...",
    "email": "john@example.com",
    "name": "John Doe",
    "status": "subscribed"
  }
  ↓
Toast: "✓ Subscriber added"
  ↓
List refreshes with new subscriber
```

**API:** `POST /api/v1/subscribers`

**Time:** <500ms

**Edge Case:** If email already exists, shows error "Email already subscribed"

---

### 🔵 Button 17: "Import CSV" (Subscribers Page)

**Location:** Subscribers page → Top right → "Import CSV" button

**What User Sees:**
```
Click "Import CSV"
  ↓
ImportCSVModal opens
  ↓
Shows:
  - "Download Template" link → subscribers_template.csv
  - File upload dropzone
  - Required format: email,name,status
  ↓
User uploads file: subscribers.csv (500 rows)
  ↓
Frontend parses CSV locally
  ↓
Shows preview: "500 subscribers to import"
  ↓
User clicks "Import"
  ↓
POST /api/v1/subscribers/bulk
  {
    "workspace_id": "...",
    "subscribers": [
      {email: "user1@example.com", name: "User 1"},
      {email: "user2@example.com", name: "User 2"},
      ...
    ]
  }
  ↓
Progress bar: "Importing 300 of 500..."
  ↓
[5-10 seconds for 500 subscribers]
  ↓
Toast: "✓ Imported 498 subscribers (2 duplicates skipped)"
  ↓
List refreshes
```

**API:** `POST /api/v1/subscribers/bulk`

**Backend:** Inserts in batches of 100, skips duplicates

**Time:** 5-10 seconds for 500 subscribers

---

### 🔵 Button 18: "Export CSV" (Subscribers Page)

**Location:** Subscribers page → Top right → "Export CSV" button

**What User Sees:**
```
Click "Export CSV"
  ↓
Frontend generates CSV from current subscriber list (NO API call)
  ↓
Browser downloads: subscribers_2025-10-23.csv
  ↓
Toast: "✓ Exported 1,234 subscribers"
```

**Handler:** Local CSV generation using Papa Parse library

**Time:** Instant (uses data already fetched)

---

### 🔵 Button 19: "Delete Selected" (Subscribers Page)

**Location:** Subscribers page → Bulk actions bar

**What User Sees:**
```
User has 10 subscribers selected
  ↓
Click "Delete Selected"
  ↓
Confirmation: "Delete 10 subscribers? This cannot be undone."
  ↓
User confirms
  ↓
DELETE /api/v1/subscribers/{id} (10 parallel calls)
  ↓
Toast: "✓ Deleted 10 subscribers"
  ↓
List refreshes
```

**API:** `DELETE /api/v1/subscribers/{id}` (multiple)

**Time:** 1-2 seconds

---

### 🔵 Button 20: "Save Sources" (Settings → Sources)

**Location:** Settings page → Sources section → "Save Sources" button

**What User Sees:**
```
User configures sources:
  - Reddit: Enabled, subreddits "ai,machinelearning"
  - RSS: Enabled, feeds "https://example.com/feed"
  - YouTube: Disabled
  ↓
User clicks "Save Sources"
  ↓
PUT /api/v1/workspaces/{id}/config
  {
    "config": {
      "sources": [
        {type: "reddit", enabled: true, config: {subreddits: ["ai", "machinelearning"]}},
        {type: "rss", enabled: true, config: {feed_urls: ["https://example.com/feed"]}},
        {type: "youtube", enabled: false}
      ]
    }
  }
  ↓
Backend merges with existing config
  ↓
Toast: "✓ Sources saved"
  ↓
Dashboard sources list updates
```

**API:** `PUT /api/v1/workspaces/{id}/config`

**Backend:** Merges sources array into workspace_configs.config JSONB field

**Time:** <1 second

---

## Part 4: All Remaining Buttons

### Settings Page Buttons (Detailed)

#### Schedule Section

| Button | Handler | API | Flow |
|--------|---------|-----|------|
| "Create Schedule" | Opens modal | `POST /api/v1/scheduler` | Pick time → Cron expression → Create job |
| "Pause Job" | `handlePauseJob(id)` | `POST /api/v1/scheduler/{id}/pause` | Sets is_enabled=false |
| "Resume Job" | `handleResumeJob(id)` | `POST /api/v1/scheduler/{id}/resume` | Sets is_enabled=true |
| "Run Now" | `handleRunNow(id)` | `POST /api/v1/scheduler/{id}/run-now` | Triggers immediate execution |
| "Delete Job" | `handleDeleteJob(id)` | `DELETE /api/v1/scheduler/{id}` | Confirmation → Delete |

#### Email Section

| Button | Handler | API | Flow |
|--------|---------|-----|------|
| "Save Config" | `handleSaveEmailConfig()` | `PUT /api/v1/workspaces/{id}/config` | Updates delivery.method and SMTP/SendGrid settings |
| "Test Email" | `handleTestEmail(email)` | `POST /api/v1/delivery/send` (with test_email param) | Sends test to specified email |

#### Workspace Section

| Button | Handler | API | Flow |
|--------|---------|-----|------|
| "Update Name" | `handleUpdateName()` | `PUT /api/v1/workspaces/{id}` | Updates workspace name |
| "Delete Workspace" | `handleDeleteWorkspace()` | `DELETE /api/v1/workspaces/{id}` | Confirmation → Cascade delete all data |
| "Add Member" | `handleAddMember(email)` | `POST /api/v1/workspaces/{id}/members` | Invites user by email |
| "Remove Member" | `handleRemoveMember(id)` | `DELETE /api/v1/workspaces/{id}/members/{id}` | Removes team member |

#### API Keys Section

| Button | Handler | API | Flow |
|--------|---------|-----|------|
| "Save Keys" | `handleSaveAPIKeys()` | `PUT /api/v1/workspaces/{id}/config` | Updates api_keys in config |
| "Test OpenAI" | `handleTestOpenAI()` | `POST /api/v1/style/test` | Sends test prompt to verify key works |
| "Test SendGrid" | `handleTestSendGrid()` | `POST /api/v1/delivery/send` (test) | Sends test email via SendGrid |

#### Style Section

| Button | Handler | API | Flow |
|--------|---------|-----|------|
| "Train Style" | `handleTrainStyle(samples)` | `POST /api/v1/style/train` | Analyzes writing samples → Creates style profile |
| "Test Style" | `handleTestStyle()` | `POST /api/v1/style/test` | Generates sample text using trained style |
| "Delete Style" | `handleDeleteStyle()` | `DELETE /api/v1/style` | Removes style profile |

#### Trends Section

| Button | Handler | API | Flow |
|--------|---------|-----|------|
| "Detect Trends" | `handleDetectTrends()` | `POST /api/v1/trends/detect` | Runs TF-IDF + K-means on recent content |
| "View Trend" | Opens modal | None (local) | Shows trend details and related items |
| "Delete Trend" | `handleDeleteTrend(id)` | `DELETE /api/v1/trends/{id}` | Removes trend record |

#### Analytics Section

| Button | Handler | API | Flow |
|--------|---------|-----|------|
| "Export Data" | `handleExportAnalytics()` | `GET /api/v1/analytics/workspaces/{id}/export` | Downloads CSV with all analytics |
| "Recalculate Stats" | `handleRecalculate()` | `POST /api/v1/analytics/recalculate` | Re-aggregates all analytics data |

#### Feedback Section

| Button | Handler | API | Flow |
|--------|---------|-----|------|
| "Set Preferences" | `handleSavePreferences()` | `POST /api/v1/feedback/preferences` | Updates content/source preferences |
| "Clear Feedback" | `handleClearFeedback()` | `DELETE /api/v1/feedback` | Resets all thumbs up/down ratings |

---

### Draft Editor Modal Buttons

| Button | Location | Handler | API | Flow |
|--------|----------|---------|-----|------|
| "Save Draft" | Footer | `handleManualSave()` | `PUT /api/v1/newsletters/{id}` | Updates subject_line, content_html |
| "Send Test" | Dropdown | Opens modal | `POST /api/v1/delivery/send` (test_email) | Sends to specified email |
| "Send Now" | Dropdown | Opens modal | `POST /api/v1/delivery/send` | Sends to all subscribers |
| "Schedule Send" | Dropdown | Opens modal | `POST /api/v1/scheduler` | Creates scheduled job |
| "Preview" | Tab | None | None | Switches to preview view (local) |
| "Edit" | Tab | None | None | Switches to editor view (local) |
| "Close" | X button | None | None | Closes modal (auto-saved already) |

---

### Other Modal Buttons

#### GenerationSettingsModal
- "Generate" → `POST /api/v1/newsletters/generate`
- "Cancel" → Closes modal

#### SendConfirmationModal
- "Send to X Subscribers" → `POST /api/v1/delivery/send`
- "Cancel" → Closes modal

#### AddSourceModal
- "Add Source" → `PUT /api/v1/workspaces/{id}/config`
- "Cancel" → Closes modal

#### ManageSourcesModal
- "Save" → `PUT /api/v1/workspaces/{id}/config`
- "Delete Source" → Removes from config array
- "Close" → Closes modal

#### ImportCSVModal (Subscribers)
- "Import" → `POST /api/v1/subscribers/bulk`
- "Download Template" → Local file download
- "Cancel" → Closes modal

---

## Part 5: Reverse API Lookup (Complete)

### By API Endpoint - Which Buttons Call Each API?

#### Content APIs

**`POST /api/v1/content/scrape`** (Called by 3 buttons)
1. Dashboard → "Scrape Content"
2. Content page → "Scrape Now"
3. UnifiedSourceSetup → Auto-scrape (hidden)

**`GET /api/v1/content/workspaces/{id}`** (Called by filters)
- Content page → Days filter dropdown
- Content page → Initial load
- Dashboard → Content stats card

**`GET /api/v1/content/workspaces/{id}/sources/{source}`** (Called by 1 button)
- Content page → Source filter dropdown

**`PUT /api/v1/content/{id}`** (Called by 1 button + auto-save)
- Dashboard → "Edit Article" button
- Dashboard → Article auto-save (2s debounce after blur)

**`DELETE /api/v1/content/{id}`** (Called by 1 button)
- Content page → Delete item (trash icon)

---

#### Newsletter APIs

**`POST /api/v1/newsletters/generate`** (Called by 5 buttons)
1. Dashboard → "Generate Draft Now"
2. Dashboard → "Regenerate with New Content"
3. Dashboard → "Regenerate Now" (toast button)
4. History page → "Regenerate"
5. History page → "Duplicate"
6. Auto-generation (hidden, after scraping)

**`PUT /api/v1/newsletters/{id}`** (Called by 2 contexts)
1. DraftEditorModal → "Save Draft" (manual)
2. DraftEditorModal → Auto-save (2s debounce)

**`DELETE /api/v1/newsletters/{id}`** (Called by 2 buttons)
1. History page → "Delete" (single)
2. History page → "Delete Selected" (bulk)

**`POST /api/v1/newsletters/{id}/duplicate`** (Called by 1 button)
- History page → "Duplicate"

---

#### Delivery APIs

**`POST /api/v1/delivery/send`** (Called by 4 buttons + test variations)
1. Dashboard → "Send Now"
2. DraftEditorModal → "Send Now" dropdown
3. Settings Email → "Test Email"
4. SendTestModal → "Send Test" (with test_email param)

---

#### Subscriber APIs

**`POST /api/v1/subscribers`** (Called by 2 buttons)
1. Subscribers page → "Add Subscriber"
2. Settings Subscribers → "Add Subscriber"

**`POST /api/v1/subscribers/bulk`** (Called by 2 buttons)
1. Subscribers page → "Import CSV"
2. Settings Subscribers → "Import CSV"

**`DELETE /api/v1/subscribers/{id}`** (Called by 2 buttons)
1. Subscribers page → Delete (trash icon)
2. Subscribers page → "Delete Selected" (bulk)

**`GET /api/v1/subscribers/workspaces/{id}`** (Called by filters)
- Subscribers page → Status filter
- Subscribers page → Initial load
- Settings Subscribers → Initial load

---

#### Workspace Config APIs

**`PUT /api/v1/workspaces/{id}/config`** (Called by 6+ buttons)
1. Dashboard → "Add Source"
2. Dashboard → "Pause Source"
3. Dashboard → "Resume Source"
4. Settings Sources → "Save Sources"
5. Settings Email → "Save Config"
6. Settings API Keys → "Save Keys"
7. ManageSourcesModal → "Save"

**`PUT /api/v1/workspaces/{id}`** (Called by 1 button)
- Settings Workspace → "Update Name"

**`DELETE /api/v1/workspaces/{id}`** (Called by 1 button)
- Settings Workspace → "Delete Workspace"

---

#### Scheduler APIs

**`POST /api/v1/scheduler`** (Called by 2 buttons)
1. Settings Schedule → "Create Schedule"
2. DraftEditorModal → "Schedule Send" dropdown

**`POST /api/v1/scheduler/{id}/pause`** (Called by 1 button)
- Settings Schedule → "Pause Job"

**`POST /api/v1/scheduler/{id}/resume`** (Called by 1 button)
- Settings Schedule → "Resume Job"

**`POST /api/v1/scheduler/{id}/run-now`** (Called by 1 button)
- Settings Schedule → "Run Now"

**`DELETE /api/v1/scheduler/{id}`** (Called by 1 button)
- Settings Schedule → "Delete Job"

---

#### Feedback APIs

**`POST /api/v1/feedback/items/{id}/rate`** (Called by 2 buttons)
1. Content page → "Keep" (👍)
2. Content page → "Skip" (👎)

**`POST /api/v1/feedback/preferences`** (Called by 1 button)
- Settings Feedback → "Set Preferences"

**`DELETE /api/v1/feedback`** (Called by 1 button)
- Settings Feedback → "Clear Feedback"

---

#### Style APIs

**`POST /api/v1/style/train`** (Called by 1 button)
- Settings Style → "Train Style"

**`POST /api/v1/style/test`** (Called by 2 buttons)
1. Settings Style → "Test Style"
2. Settings API Keys → "Test OpenAI"

**`DELETE /api/v1/style`** (Called by 1 button)
- Settings Style → "Delete Style"

---

#### Trends APIs

**`POST /api/v1/trends/detect`** (Called by 1 button)
- Settings Trends → "Detect Trends"

**`DELETE /api/v1/trends/{id}`** (Called by 1 button)
- Settings Trends → "Delete Trend"

---

#### Analytics APIs

**`GET /api/v1/analytics/workspaces/{id}/export`** (Called by 1 button)
- Settings Analytics → "Export Data"

**`POST /api/v1/analytics/recalculate`** (Called by 1 button)
- Settings Analytics → "Recalculate Stats"

---

### Summary Statistics

- **Total Interactive Elements:** 100+ buttons/actions
- **Total API Endpoints Used:** 35+
- **Most Called API:** `PUT /api/v1/workspaces/{id}/config` (6+ buttons)
- **Most Confusing Button:** "Generate Newsletter" (5 variations)
- **True Duplicate Buttons:** "Scrape Content" (3 identical buttons)

---

**Last Updated:** 2025-10-23
**Total Buttons Documented:** 100+
**Version:** 1.0
