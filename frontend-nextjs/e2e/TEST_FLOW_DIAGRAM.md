# E2E Test Flow Visualization

## Overall Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         E2E Test Suite                              │
│                                                                     │
│  ┌───────────────┐    ┌───────────────┐    ┌──────────────────┐  │
│  │   Playwright  │───▶│   Frontend    │───▶│    Backend API   │  │
│  │  Test Runner  │    │  (Next.js)    │    │   (FastAPI)      │  │
│  └───────┬───────┘    └───────┬───────┘    └────────┬─────────┘  │
│          │                    │                      │             │
│          │                    │                      │             │
│          ▼                    ▼                      ▼             │
│  ┌───────────────┐    ┌───────────────┐    ┌──────────────────┐  │
│  │   Supabase    │◀───│  UI Actions   │◀───│  Supabase DB     │  │
│  │    Helper     │    │  Verification │    │  Verification    │  │
│  └───────────────┘    └───────────────┘    └──────────────────┘  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## Journey 1: User Onboarding Flow

```
┌──────────────┐
│ START TEST   │
└──────┬───────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────┐
│ Step 1: Visit Landing Page                                   │
├──────────────────────────────────────────────────────────────┤
│ Frontend: page.goto('/')                                     │
│ Verify:   Landing page renders                               │
│ DB Check: None                                               │
└──────┬───────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────┐
│ Step 2: User Signs Up                                        │
├──────────────────────────────────────────────────────────────┤
│ Frontend: Fill email, password → Click "Sign Up"            │
│ Verify:   Success message or redirect                        │
│ DB Check: ✓ User record created in `users` table            │
│           ✓ Verify email matches                             │
│           ✓ Store user_id for later steps                    │
└──────┬───────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────┐
│ Step 3: Auto-Login & Dashboard                               │
├──────────────────────────────────────────────────────────────┤
│ Frontend: Redirected to dashboard                            │
│ Verify:   User menu visible                                  │
│ DB Check: ✓ Session exists in `auth.sessions`               │
│           ✓ Session belongs to user_id                       │
└──────┬───────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────┐
│ Step 4: Create First Workspace                               │
├──────────────────────────────────────────────────────────────┤
│ Frontend: Click "Create Workspace" → Fill form → Submit     │
│ Verify:   Workspace appears / Success message                │
│ DB Check: ✓ Workspace record created in `workspaces`        │
│           ✓ workspace.user_id matches user_id               │
│           ✓ workspace.created_at is recent                   │
│           ✓ Store workspace_id for next journeys             │
└──────┬───────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────┐
│  END TEST    │
│  ✓ CLEANUP   │
└──────────────┘
```

## Journey 2: Content Sources Flow

```
┌──────────────┐
│ START TEST   │
│ (After J1)   │
└──────┬───────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────┐
│ Step 1: Navigate to Sources                                  │
├──────────────────────────────────────────────────────────────┤
│ Frontend: Click "Content Sources" link                       │
│ Verify:   Sources page renders                               │
│ DB Check: ✓ Workspace exists                                 │
└──────┬───────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────┐
│ Step 2: Add RSS Feed                                         │
├──────────────────────────────────────────────────────────────┤
│ Frontend: Click "Add Source" → Select RSS → Enter URL       │
│ Verify:   RSS source appears in list                         │
│ DB Check: ✓ Record in `content_sources`                     │
│           ✓ source_type = 'rss'                              │
│           ✓ workspace_id matches                             │
│           ✓ Store source_id                                  │
└──────┬───────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────┐
│ Step 3: Add Reddit Source                                    │
├──────────────────────────────────────────────────────────────┤
│ Frontend: Add Source → Select Reddit → Enter subreddit      │
│ Verify:   Reddit source appears in list                      │
│ DB Check: ✓ Record in `content_sources`                     │
│           ✓ source_type = 'reddit'                           │
└──────┬───────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────┐
│ Step 4: Add Twitter Source                                   │
├──────────────────────────────────────────────────────────────┤
│ Frontend: Add Source → Select Twitter → Enter username      │
│ Verify:   Twitter source appears in list                     │
│ DB Check: ✓ Record in `content_sources`                     │
│           ✓ source_type = 'twitter'                          │
│           ✓ Total of 3 sources for workspace                 │
└──────┬───────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────┐
│ Step 5: Trigger Scraping                                     │
├──────────────────────────────────────────────────────────────┤
│ Frontend: Click "Scrape Now" button                          │
│ Verify:   Loading indicator appears                          │
│ DB Check: ✓ Record in `scrape_jobs`                         │
│           ✓ job.status = 'pending' or 'running'              │
│           ✓ Store job_id                                     │
└──────┬───────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────┐
│ Step 6: Wait for Scraping to Complete                        │
├──────────────────────────────────────────────────────────────┤
│ Frontend: Poll for completion (loading disappears)           │
│ Verify:   Content items appear                               │
│ DB Check: ✓ job.status = 'completed'                        │
│           ✓ Records in `content_items`                       │
│           ✓ Each item has source_id, title, url             │
│           ✓ All items have workspace_id match                │
└──────┬───────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────┐
│ Step 7: Filter Content by Source                             │
├──────────────────────────────────────────────────────────────┤
│ Frontend: Select RSS filter                                  │
│ Verify:   Only RSS items shown                               │
│ DB Check: ✓ Query content_items by source_id                │
│           ✓ Count matches displayed items                    │
└──────┬───────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────┐
│  END TEST    │
│  ✓ CLEANUP   │
└──────────────┘
```

## Journey 3: Newsletter Generation Flow

```
┌──────────────┐
│ START TEST   │
│ (After J2)   │
└──────┬───────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────┐
│ Step 1-2: Select Content Items                               │
├──────────────────────────────────────────────────────────────┤
│ Frontend: Check boxes for 5-10 content items                 │
│ Verify:   Selection count displayed                          │
│ DB Check: ✓ Selected items exist in database                │
└──────┬───────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────┐
│ Step 3: Configure Newsletter                                 │
├──────────────────────────────────────────────────────────────┤
│ Frontend: Fill subject, preview text, select tone            │
│ Verify:   Form fields populated                              │
│ DB Check: None (client-side only)                            │
└──────┬───────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────┐
│ Step 4: Generate Newsletter                                  │
├──────────────────────────────────────────────────────────────┤
│ Frontend: Click "Generate" → Loading state                   │
│ Verify:   "Generating..." message shown                      │
│ DB Check: ✓ Record in `newsletters`                         │
│           ✓ newsletter.status = 'generating'                 │
│           ✓ newsletter.workspace_id matches                  │
│           ✓ Store newsletter_id                              │
└──────┬───────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────┐
│ Step 5: Wait for Generation to Complete                      │
├──────────────────────────────────────────────────────────────┤
│ Frontend: Poll for completion (loading → preview)            │
│ Verify:   Newsletter preview displayed                       │
│ DB Check: ✓ newsletter.status = 'completed'                 │
│           ✓ newsletter.content_html is populated            │
│           ✓ newsletter.generated_at timestamp set            │
└──────┬───────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────┐
│ Step 6: Add Subscribers                                      │
├──────────────────────────────────────────────────────────────┤
│ Frontend: Add 3 subscriber emails                            │
│ Verify:   Subscribers appear in list                         │
│ DB Check: ✓ Records in `subscribers`                        │
│           ✓ Each subscriber.workspace_id matches             │
│           ✓ subscriber.status = 'active'                     │
└──────┬───────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────┐
│ Step 7: Send Newsletter                                      │
├──────────────────────────────────────────────────────────────┤
│ Frontend: Click "Send Now" → Confirm                         │
│ Verify:   "Sending..." indicator                             │
│ DB Check: ✓ newsletter.status = 'sending'                   │
└──────┬───────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────┐
│ Step 8: Verify Delivery                                      │
├──────────────────────────────────────────────────────────────┤
│ Frontend: Wait for "Sent" confirmation                       │
│ Verify:   Success message displayed                          │
│ DB Check: ✓ newsletter.status = 'sent'                      │
│           ✓ newsletter.sent_at timestamp set                 │
│           ✓ Records in `email_delivery_log`                  │
│           ✓ Each delivery has newsletter_id                  │
└──────┬───────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────┐
│  END TEST    │
│  ✓ CLEANUP   │
└──────────────┘
```

## Data Flow in Tests

```
┌─────────────────────────────────────────────────────────────────┐
│                     Test Execution Flow                         │
└─────────────────────────────────────────────────────────────────┘

1. SETUP PHASE
   ├─ beforeAll() hook runs
   ├─ Generate unique test data (timestamp-based emails)
   ├─ Initialize Supabase helper
   └─ Record test start time

2. TEST EXECUTION
   For each step:
   ├─ Frontend Action
   │  ├─ User interaction (click, fill, etc.)
   │  ├─ Wait for UI update
   │  └─ Verify UI state
   │
   └─ Database Verification
      ├─ Query Supabase with service client
      ├─ Verify record exists
      ├─ Validate field values
      ├─ Check relationships (foreign keys)
      └─ Store IDs for next steps

3. CLEANUP PHASE
   ├─ afterAll() hook runs
   ├─ Delete test user (cascades to related data)
   ├─ Clean up orphaned records
   └─ Verify cleanup succeeded

4. REPORTING
   ├─ Screenshots saved for each step
   ├─ Videos saved for failed tests
   ├─ HTML report generated
   └─ Console logs with verification details
```

## Database Verification Pattern

```
┌────────────────────────────────────────────────────────────┐
│           Frontend Action → Database Verification          │
└────────────────────────────────────────────────────────────┘

FRONTEND                        DATABASE
────────                        ────────

User clicks button      ─────▶  API endpoint called
                                    │
Form submission         ─────▶  Business logic runs
                                    │
Success message         ◀─────  Database writes
                                    │
UI updates                      Record committed
                                    │
                                    ▼
Test verifies:          ◀─────  Supabase helper queries:
✓ Button clicked                ✓ SELECT * WHERE id = ?
✓ Form submitted                ✓ Verify fields match
✓ Message shown                 ✓ Check foreign keys
✓ UI updated                    ✓ Validate timestamps
                                ✓ Count related records
```

## Test Isolation Strategy

```
┌───────────────────────────────────────────────────────────┐
│                    Test Isolation                         │
└───────────────────────────────────────────────────────────┘

Test 1 (Journey 1)              Test 2 (Journey 2)
─────────────────              ─────────────────
Unique email:                  Unique email:
test-1731234567@test.com      test-1731234890@test.com
        │                              │
        ├─ Creates user               ├─ Creates user
        ├─ Creates workspace          ├─ Creates workspace
        ├─ Runs tests                 ├─ Runs tests
        └─ Cleans up ✓                └─ Cleans up ✓

NO DATA POLLUTION              NO INTERFERENCE
Test 1 data is isolated        Test 2 doesn't see Test 1 data
```

## Cleanup Flow

```
┌──────────────────────────────────────────────────────────────┐
│                    Cleanup Cascade                           │
└──────────────────────────────────────────────────────────────┘

Delete User (userId)
       │
       ├─▶ Cascade deletes workspaces (user_id FK)
       │         │
       │         ├─▶ Cascade deletes content_sources (workspace_id FK)
       │         │
       │         ├─▶ Cascade deletes content_items (workspace_id FK)
       │         │
       │         ├─▶ Cascade deletes newsletters (workspace_id FK)
       │         │         │
       │         │         └─▶ Cascade deletes email_delivery_log
       │         │
       │         ├─▶ Cascade deletes subscribers (workspace_id FK)
       │         │
       │         ├─▶ Cascade deletes schedules (workspace_id FK)
       │         │
       │         └─▶ Cascade deletes analytics_events (workspace_id FK)
       │
       └─▶ Deletes style_profiles (user_id FK)

Result: All test data removed, database clean for next test
```

## Test Results Flow

```
┌──────────────────────────────────────────────────────────────┐
│                  Test Results & Artifacts                    │
└──────────────────────────────────────────────────────────────┘

Test Run
   │
   ├─ Success Path
   │     ├─ Each step passes
   │     ├─ Screenshots saved in test-results/
   │     ├─ Console logs show verification details
   │     └─ HTML report marks as PASSED ✓
   │
   └─ Failure Path
         ├─ Step fails
         ├─ Screenshot captured at failure point
         ├─ Video recording saved
         ├─ Trace file generated
         ├─ Error stack trace logged
         └─ HTML report marks as FAILED ✗

After Test Run:
   ├─ View HTML report: npm run test:e2e:report
   ├─ Review screenshots: test-results/*.png
   ├─ Watch videos: test-results/*.webm
   └─ Analyze traces: test-results/*.zip
```

## Parallel vs Sequential Execution

```
┌──────────────────────────────────────────────────────────────┐
│              Sequential Execution (Current Setup)            │
└──────────────────────────────────────────────────────────────┘

Journey 1 ────▶ Journey 2 ────▶ Journey 3
   │               │               │
   ├─ User A       ├─ User B       ├─ User C
   ├─ DB writes    ├─ DB writes    ├─ DB writes
   └─ Cleanup ✓    └─ Cleanup ✓    └─ Cleanup ✓

WHY SEQUENTIAL?
- Better test isolation with database
- Easier debugging (one test at a time)
- No race conditions in DB writes
- Simpler cleanup logic

CAN BE PARALLEL?
- Each test uses unique data (timestamp-based)
- Tests don't share state
- Could enable: workers: 3 in playwright.config.ts
```

---

**This diagram shows the complete flow of E2E tests from user actions through database verification to cleanup and reporting.**
