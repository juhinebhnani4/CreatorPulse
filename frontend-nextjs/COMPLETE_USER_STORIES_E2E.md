# Complete User Stories for E2E Testing
## CreatorPulse - AI Newsletter Platform

**Last Updated:** 2025-10-17
**Purpose:** Comprehensive user stories for end-to-end testing with Playwright MCP
**Coverage:** All frontend features and user interactions
**Architecture:** See [FRONTEND_BACKEND_MAPPING.md](../FRONTEND_BACKEND_MAPPING.md) for complete endpoint mapping

---

## Frontend Architecture (Current Implementation)

### **Actual Routes & Pages**

```
/ (Landing Page)                         ✅ IMPLEMENTED
├── /login                              ✅ IMPLEMENTED
├── /register                           ✅ IMPLEMENTED
└── /app (Protected - Requires Auth)
    ├── /app (Dashboard)                ✅ IMPLEMENTED
    ├── /app/settings                   ✅ IMPLEMENTED (10 setting sections)
    └── /app/history                    ✅ IMPLEMENTED (connected to backend)
```

### **Backend Integration Status**

| Feature Area | Frontend | Backend API | Integration Status |
|-------------|----------|-------------|-------------------|
| **Authentication** | ✅ Pages exist | ✅ 4 endpoints | ✅ 100% Connected |
| **Workspaces** | ✅ Dashboard | ✅ 7 endpoints | ✅ 100% Connected |
| **Content Scraping** | ✅ Dashboard | ✅ 3 endpoints | ✅ 66% Connected |
| **Newsletter Generation** | ✅ Dashboard | ✅ 6 endpoints | ✅ 66% Connected |
| **Delivery** | ✅ Modals | ✅ 4 endpoints | ✅ 100% Connected |
| **Scheduling** | ✅ Settings/Dashboard | ✅ 6 endpoints | ✅ 50% Connected |
| **Subscribers** | ✅ Settings | ✅ 8 endpoints | ❌ 0% Connected |
| **Newsletter History** | ✅ History page | ✅ GET /newsletters/... | ✅ 100% Connected |
| **Style Training** | ✅ Settings | ✅ 4 endpoints | ❌ 0% Connected |
| **Trends Detection** | ✅ Settings | ✅ 4 endpoints | ❌ 0% Connected |
| **Feedback Loop** | ❌ Not built | ✅ 4 endpoints | ❌ 0% Connected |

**Summary:**
- **5/12 feature areas** are fully connected to backend (42%)
- **2/12 areas** are partially connected (17%)
- **4/12 areas** have frontend UI but no backend connection (33%)
- **1/12 areas** has backend but no frontend UI

### **Missing Pages (Backend exists, no frontend)**

1. ❌ `/app/content` - Content browser and selection
2. ❌ `/app/subscribers` - Subscriber management
3. ❌ `/app/analytics` - Detailed analytics dashboard
4. ❌ `/app/trends` - Trends visualization

### **Incomplete Pages (Frontend exists, backend not connected)**

1. ⚠️ `/app/settings` - Most setting sections are placeholders (only Sources/Schedule partially connected)

---

## Table of Contents

1. [Authentication & Onboarding](#1-authentication--onboarding)
2. [Workspace Management](#2-workspace-management)
3. [Content Sources Management](#3-content-sources-management)
4. [Content Discovery & Scraping](#4-content-discovery--scraping)
5. [Newsletter Generation](#5-newsletter-generation)
6. [Newsletter Delivery](#6-newsletter-delivery)
7. [Scheduling & Automation](#7-scheduling--automation)
8. [Subscriber Management](#8-subscriber-management)
9. [Analytics & Tracking](#9-analytics--tracking)
10. [Style & Writing Profile](#10-style--writing-profile)
11. [Trends Detection](#11-trends-detection)
12. [Feedback Loop](#12-feedback-loop)
13. [Settings & Configuration](#13-settings--configuration)

---

## 1. Authentication & Onboarding

### Story 1.1: User Registration
**As a** new user
**I want to** create an account with email and password
**So that** I can access the platform and save my work

#### Acceptance Criteria
- [ ] User can access the registration page from landing page
- [ ] Email validation is enforced (valid format required)
- [ ] Password requirements are displayed (min 8 characters)
- [ ] Password confirmation field matches password
- [ ] Registration creates a user record in the database
- [ ] User is automatically logged in after successful registration
- [ ] Duplicate email addresses are rejected with clear error message
- [ ] Success message is shown after registration

#### Test Scenarios
```typescript
// Scenario 1: Successful registration
1. Navigate to landing page (/)
2. Click "Sign Up" button
3. Fill email: "newuser@test.com"
4. Fill password: "SecurePass123!"
5. Fill confirm password: "SecurePass123!"
6. Click "Create Account"
7. Verify redirect to dashboard
8. Verify user exists in database
9. Verify session is created

// Scenario 2: Validation errors
1. Navigate to /register
2. Fill email: "invalid-email"
3. Fill password: "short"
4. Click "Create Account"
5. Verify error: "Invalid email format"
6. Verify error: "Password must be at least 8 characters"

// Scenario 3: Duplicate email
1. Register with existing email
2. Verify error: "Email already registered"
```

#### Database Verification
```sql
-- Verify user created
SELECT * FROM users WHERE email = 'newuser@test.com';

-- Verify session exists
SELECT * FROM auth.sessions WHERE user_id = [user_id];
```

---

### Story 1.2: User Login
**As a** registered user
**I want to** log in with my credentials
**So that** I can access my workspaces and content

#### Acceptance Criteria
- [ ] User can access login page
- [ ] Email and password fields are present
- [ ] Valid credentials allow login
- [ ] Invalid credentials show error message
- [ ] User is redirected to dashboard after login
- [ ] Session persists across page refreshes
- [ ] "Forgot password" link is available
- [ ] User can log out from any page

#### Test Scenarios
```typescript
// Scenario 1: Successful login
1. Navigate to /login
2. Fill email: "existing@test.com"
3. Fill password: "correctpassword"
4. Click "Sign In"
5. Verify redirect to /app (dashboard)
6. Verify user menu shows email
7. Verify workspace selector is visible

// Scenario 2: Invalid credentials
1. Navigate to /login
2. Fill email: "user@test.com"
3. Fill password: "wrongpassword"
4. Click "Sign In"
5. Verify error: "Invalid credentials"
6. Verify user remains on login page

// Scenario 3: Session persistence
1. Login successfully
2. Refresh page
3. Verify still logged in
4. Verify dashboard loads correctly
```

---

### Story 1.3: First-Time User Onboarding
**As a** first-time user
**I want to** see a guided onboarding flow
**So that** I understand how to set up my newsletter

#### Acceptance Criteria
- [ ] Welcome screen appears after first login
- [ ] Setup progress indicator shows 0% initially
- [ ] Steps include: Add sources, Generate newsletter, Add subscribers
- [ ] User can skip onboarding
- [ ] Onboarding status is saved
- [ ] Completed steps are marked with checkmarks
- [ ] User can return to onboarding later

#### Test Scenarios
```typescript
// Scenario 1: Complete onboarding
1. Login as new user
2. See welcome screen
3. Click "Get Started"
4. Add first RSS source
5. Verify setup progress: 33%
6. Generate first newsletter
7. Verify setup progress: 66%
8. Add first subscriber
9. Verify setup progress: 100%
10. See congratulations message

// Scenario 2: Skip onboarding
1. Login as new user
2. Click "Skip for now"
3. Verify on main dashboard
4. Verify can access "Setup Guide" from settings
```

---

## 2. Workspace Management

### Story 2.1: Create Workspace
**As a** user
**I want to** create a new workspace
**So that** I can manage separate newsletters for different projects

#### Acceptance Criteria
- [ ] "Create Workspace" button is visible
- [ ] Modal opens with workspace creation form
- [ ] Required fields: Name (max 50 characters)
- [ ] Optional fields: Description
- [ ] Workspace is created in database
- [ ] User is switched to new workspace automatically
- [ ] New workspace has default configuration
- [ ] Success message is shown

#### Test Scenarios
```typescript
// Scenario 1: Create workspace successfully
1. Click "Create Workspace" button
2. Fill name: "Tech Newsletter"
3. Fill description: "Weekly tech updates"
4. Click "Create"
5. Verify success message
6. Verify workspace selector shows "Tech Newsletter"
7. Verify database has new workspace record
8. Verify workspace.user_id matches current user

// Scenario 2: Validation errors
1. Click "Create Workspace"
2. Leave name empty
3. Click "Create"
4. Verify error: "Workspace name is required"

// Scenario 3: Duplicate workspace name
1. Create workspace "My Newsletter"
2. Create another workspace "My Newsletter"
3. Verify workspace created with unique ID
```

#### Database Verification
```sql
-- Verify workspace created
SELECT * FROM workspaces
WHERE name = 'Tech Newsletter' AND user_id = [user_id];

-- Verify default config exists
SELECT * FROM workspace_config WHERE workspace_id = [workspace_id];
```

---

### Story 2.2: Switch Between Workspaces
**As a** user with multiple workspaces
**I want to** easily switch between them
**So that** I can work on different newsletters

#### Acceptance Criteria
- [ ] Workspace dropdown shows all user's workspaces
- [ ] Current workspace is highlighted
- [ ] Clicking workspace switches context immediately
- [ ] All data (sources, content, drafts) updates
- [ ] Switching is instant (<1 second)
- [ ] Last active workspace is remembered

#### Test Scenarios
```typescript
// Scenario 1: Switch workspaces
1. Create workspace "Tech News"
2. Create workspace "Marketing Digest"
3. Add source to "Tech News"
4. Switch to "Marketing Digest"
5. Verify no sources displayed
6. Switch back to "Tech News"
7. Verify source is still there
8. Verify workspace indicator updates

// Scenario 2: Data isolation
1. In workspace A: Add 3 sources
2. Switch to workspace B
3. Verify 0 sources shown
4. Add 2 sources to workspace B
5. Switch to workspace A
6. Verify still shows 3 sources
```

---

## 3. Content Sources Management

### Story 3.1: Add RSS Feed Source
**As a** user
**I want to** add RSS feed URLs as content sources
**So that** I can aggregate blog posts and articles

#### Acceptance Criteria
- [ ] "Add Source" button opens modal
- [ ] Source type selector includes "RSS Feed"
- [ ] URL field validates RSS feed format
- [ ] Custom name can be provided
- [ ] Source is saved to database
- [ ] Source appears in sources list immediately
- [ ] Can set scraping frequency
- [ ] Can enable/disable source

#### Test Scenarios
```typescript
// Scenario 1: Add valid RSS feed
1. Navigate to dashboard
2. Click "Add Source"
3. Select "RSS Feed"
4. Fill URL: "https://techcrunch.com/feed/"
5. Fill name: "TechCrunch"
6. Select frequency: "Daily"
7. Click "Add Source"
8. Verify success message
9. Verify source appears in list
10. Verify database record created

// Scenario 2: Invalid URL
1. Click "Add Source"
2. Select "RSS Feed"
3. Fill URL: "not-a-valid-url"
4. Click "Add Source"
5. Verify error: "Invalid URL format"

// Scenario 3: Duplicate source
1. Add source: "https://blog.example.com/feed"
2. Try to add same URL again
3. Verify warning: "Source already exists"
```

#### Database Verification
```sql
-- Verify source created
SELECT * FROM content_sources
WHERE workspace_id = [workspace_id]
AND source_type = 'rss'
AND url = 'https://techcrunch.com/feed/';

-- Verify scraping schedule
SELECT * FROM scrape_schedules WHERE source_id = [source_id];
```

---

### Story 3.2: Add Reddit Source
**As a** user
**I want to** add Reddit subreddits as sources
**So that** I can track trending discussions

#### Acceptance Criteria
- [ ] Can select "Reddit" as source type
- [ ] Subreddit name field (r/subreddit format)
- [ ] Can filter by post type (hot/top/new)
- [ ] Can set time range (day/week/month)
- [ ] Source validates subreddit exists
- [ ] Preview shows recent posts
- [ ] Source is saved with correct configuration

#### Test Scenarios
```typescript
// Scenario 1: Add Reddit source
1. Click "Add Source"
2. Select "Reddit"
3. Fill subreddit: "r/MachineLearning"
4. Select filter: "Hot"
5. Select timeframe: "Week"
6. Click "Preview"
7. Verify 5-10 posts displayed
8. Click "Add Source"
9. Verify source in list
10. Verify database record

// Scenario 2: Invalid subreddit
1. Add Reddit source
2. Fill subreddit: "r/ThisDoesNotExist12345"
3. Click "Preview"
4. Verify error: "Subreddit not found"

// Scenario 3: Multiple Reddit sources
1. Add r/programming
2. Add r/webdev
3. Add r/javascript
4. Verify all 3 sources in list
5. Verify each has unique configuration
```

---

### Story 3.3: Add Twitter/X Source
**As a** user
**I want to** add Twitter accounts as sources
**So that** I can curate tweets and threads

#### Acceptance Criteria
- [ ] Can select "Twitter" as source type
- [ ] Username field (with @username format)
- [ ] Can filter tweets/retweets/replies
- [ ] Can set minimum engagement threshold
- [ ] Shows preview of recent tweets
- [ ] Handles API rate limits gracefully

#### Test Scenarios
```typescript
// Scenario 1: Add Twitter source
1. Click "Add Source"
2. Select "Twitter/X"
3. Fill username: "@elonmusk"
4. Select filters: "Tweets only"
5. Set min likes: 1000
6. Click "Preview"
7. Verify recent tweets displayed
8. Click "Add Source"
9. Verify source saved

// Scenario 2: API rate limit
1. Add 10 Twitter sources quickly
2. Verify warning: "API rate limit approaching"
3. Verify sources still added
4. Verify queued for next scrape window
```

---

### Story 3.4: Add YouTube Channel Source
**As a** user
**I want to** add YouTube channels as sources
**So that** I can curate video content

#### Acceptance Criteria
- [ ] Can select "YouTube" as source type
- [ ] Channel URL or handle input
- [ ] Can filter by video type (recent/popular)
- [ ] Shows channel preview with subscriber count
- [ ] Validates YouTube API key exists
- [ ] Stores channel metadata

#### Test Scenarios
```typescript
// Scenario 1: Add YouTube source
1. Click "Add Source"
2. Select "YouTube"
3. Fill channel: "@mkbhd"
4. Click "Validate Channel"
5. Verify channel preview: Subscriber count, recent videos
6. Click "Add Source"
7. Verify source in list
8. Verify database record with channel_id

// Scenario 2: Missing API key
1. Remove YouTube API key from settings
2. Try to add YouTube source
3. Verify error: "YouTube API key required"
4. Verify link to settings page
```

---

### Story 3.5: Edit Existing Source
**As a** user
**I want to** modify source settings
**So that** I can adjust scraping parameters

#### Acceptance Criteria
- [ ] Can click "Edit" on any source
- [ ] Modal shows current configuration
- [ ] Can change all editable fields
- [ ] Changes are saved immediately
- [ ] Source list updates instantly
- [ ] Database record is updated

#### Test Scenarios
```typescript
// Scenario 1: Edit source settings
1. Click "Edit" on RSS source
2. Change name: "TechCrunch" → "TC News"
3. Change frequency: "Daily" → "Every 6 hours"
4. Click "Save"
5. Verify source list shows new name
6. Verify next scrape time updated

// Scenario 2: Disable source temporarily
1. Edit source
2. Toggle "Active" switch off
3. Save changes
4. Verify source shown as "Inactive"
5. Verify not included in next scrape
```

---

### Story 3.6: Delete Source
**As a** user
**I want to** remove sources I no longer need
**So that** I can keep my sources list clean

#### Acceptance Criteria
- [ ] Can click "Delete" on any source
- [ ] Confirmation dialog appears
- [ ] Deleting removes source and associated content
- [ ] Cannot be undone (clear warning)
- [ ] Success message after deletion
- [ ] Source disappears from list immediately

#### Test Scenarios
```typescript
// Scenario 1: Delete source with confirmation
1. Click "Delete" on source
2. See confirmation: "Delete [Source Name]? This cannot be undone."
3. Click "Cancel"
4. Verify source still exists
5. Click "Delete" again
6. Click "Confirm Delete"
7. Verify success message
8. Verify source removed from list
9. Verify database record deleted

// Scenario 2: Delete cascade
1. Add source
2. Scrape content (10 items)
3. Delete source
4. Verify all 10 content items also deleted
```

#### Database Verification
```sql
-- Verify cascade delete
SELECT * FROM content_items WHERE source_id = [deleted_source_id];
-- Should return 0 rows

SELECT * FROM content_sources WHERE id = [deleted_source_id];
-- Should return 0 rows
```

---

## 4. Content Discovery & Scraping

### Story 4.1: Manual Content Scraping
**As a** user
**I want to** manually trigger content scraping
**So that** I can get fresh content immediately

#### Acceptance Criteria
- [ ] "Scrape Now" button is visible on dashboard
- [ ] Clicking triggers scrape for all active sources
- [ ] Loading indicator shows progress
- [ ] Can scrape individual source vs all sources
- [ ] New content appears in content list
- [ ] Scrape job is logged in database
- [ ] Error handling for failed scrapes

#### Test Scenarios
```typescript
// Scenario 1: Scrape all sources
1. Add 3 sources (RSS, Reddit, Twitter)
2. Click "Scrape All Sources"
3. Verify loading indicator: "Scraping 3 sources..."
4. Wait for completion (~10-30 seconds)
5. Verify success: "Found 45 new items"
6. Verify content list shows new items
7. Verify scrape_jobs record in database

// Scenario 2: Scrape single source
1. Click "..." menu on specific source
2. Click "Scrape Now"
3. Verify loading for that source only
4. Verify new content from that source

// Scenario 3: Scrape with errors
1. Add invalid RSS feed
2. Click "Scrape All"
3. Verify partial success: "2/3 sources succeeded"
4. Verify error details shown
5. Verify successful sources still have content
```

#### Database Verification
```sql
-- Verify scrape job created
SELECT * FROM scrape_jobs
WHERE workspace_id = [workspace_id]
ORDER BY created_at DESC LIMIT 1;

-- Verify content items created
SELECT COUNT(*) FROM content_items
WHERE workspace_id = [workspace_id]
AND created_at > [scrape_start_time];
```

---

### Story 4.2: View Content List
**As a** user
**I want to** browse all scraped content
**So that** I can see what's available for my newsletter

#### Acceptance Criteria
- [ ] Content list shows all items from all sources
- [ ] Each item displays: Title, Source, Date, Engagement score
- [ ] Items are sorted by date (newest first) by default
- [ ] Can filter by source
- [ ] Can filter by date range
- [ ] Can search by keyword
- [ ] Pagination for large lists (50 per page)
- [ ] Can select items for newsletter

#### Test Scenarios
```typescript
// Scenario 1: Browse content
1. Navigate to dashboard
2. Verify content list loads
3. Verify items show: Title, preview, source icon, date
4. Verify "Load More" button if >50 items
5. Click on item to expand full content
6. Verify source URL is clickable

// Scenario 2: Filter by source
1. Click "Filter" dropdown
2. Select "Reddit" source
3. Verify only Reddit content shown
4. Verify count: "Showing 23 Reddit items"
5. Clear filter
6. Verify all sources shown again

// Scenario 3: Search content
1. Type "machine learning" in search box
2. Verify real-time filtering
3. Verify highlights search terms
4. Verify empty state if no matches

// Scenario 4: Date range filter
1. Click "Date Range" filter
2. Select "Last 7 days"
3. Verify only content from past week
4. Select "Custom range"
5. Pick specific dates
6. Verify content filtered correctly
```

---

### Story 4.3: Content Item Details
**As a** user
**I want to** view full details of a content item
**So that** I can decide if it's worth including

#### Acceptance Criteria
- [ ] Clicking item opens detail modal/panel
- [ ] Shows full title, summary, and content
- [ ] Shows metadata: Source, URL, published date, author
- [ ] Shows engagement metrics (likes, comments, shares)
- [ ] "Open Source" button opens original URL
- [ ] Can add to newsletter from detail view
- [ ] Can mark as favorite/bookmark

#### Test Scenarios
```typescript
// Scenario 1: View item details
1. Click on content item
2. Verify modal opens with full details
3. Verify title, summary, metadata displayed
4. Verify "View Original" link works
5. Verify engagement stats (if available)
6. Close modal

// Scenario 2: Add to newsletter from details
1. Open item details
2. Click "Add to Newsletter"
3. Verify checkmark appears
4. Verify item added to draft count
5. Verify can remove again
```

---

## 5. Newsletter Generation

### Story 5.1: Generate Newsletter Draft
**As a** user
**I want to** generate a newsletter draft from scraped content
**So that** I can review and edit before sending

#### Acceptance Criteria
- [ ] "Generate Newsletter" button is visible
- [ ] Can select which content items to include
- [ ] AI generates cohesive newsletter with intro/outro
- [ ] Draft shows in HTML preview
- [ ] Can edit title and description
- [ ] Draft is saved automatically
- [ ] Generation takes <30 seconds

#### Test Scenarios
```typescript
// Scenario 1: Generate with default selection
1. Navigate to dashboard
2. Verify "Generate Newsletter" button enabled
3. Click "Generate Newsletter"
4. Verify loading: "AI is writing your newsletter..."
5. Wait for completion
6. Verify draft preview shown
7. Verify intro paragraph exists
8. Verify content items formatted correctly
9. Verify outro/footer present

// Scenario 2: Generate with custom selection
1. Select 8 specific content items
2. Click "Generate Newsletter"
3. Verify only selected items included
4. Verify AI summary mentions all topics
5. Verify correct order/grouping

// Scenario 3: Customize before generating
1. Click "Generate Newsletter"
2. In generation modal:
   - Set title: "Weekly AI Updates"
   - Set tone: "Conversational"
   - Set length: "Short (5 min read)"
3. Click "Generate"
4. Verify draft matches specifications
```

#### Database Verification
```sql
-- Verify draft created
SELECT * FROM newsletters
WHERE workspace_id = [workspace_id]
AND status = 'draft'
ORDER BY created_at DESC LIMIT 1;

-- Verify content associations
SELECT * FROM newsletter_content_items
WHERE newsletter_id = [draft_id];
```

---

### Story 5.2: Edit Newsletter Draft
**As a** user
**I want to** edit the AI-generated draft
**So that** I can customize it before sending

#### Acceptance Criteria
- [ ] Can edit title inline
- [ ] Can edit intro paragraph
- [ ] Can edit each content item section
- [ ] Can reorder content items (drag & drop)
- [ ] Can remove content items
- [ ] Can add new content items
- [ ] Changes save automatically
- [ ] "Undo" feature available

#### Test Scenarios
```typescript
// Scenario 1: Edit draft text
1. Open newsletter draft
2. Click on title to edit
3. Change title: "Weekly Digest" → "AI Weekly"
4. Verify auto-save indicator
5. Refresh page
6. Verify changes persisted

// Scenario 2: Reorder content
1. Open draft in editor
2. Drag content item from position 3 to position 1
3. Verify new order saved
4. Verify preview updates instantly

// Scenario 3: Remove content item
1. Hover over content item
2. Click "Remove" (X button)
3. Verify confirmation dialog
4. Confirm removal
5. Verify item removed from draft
6. Verify item still available in content pool

// Scenario 4: Add content to draft
1. Open "Available Content" panel
2. Browse content items
3. Click "Add" on item
4. Verify item appears in draft
5. Verify can position it anywhere
```

---

### Story 5.3: Newsletter Preview
**As a** user
**I want to** preview how the newsletter will look
**So that** I can ensure it's ready before sending

#### Acceptance Criteria
- [ ] "Preview" button shows newsletter as recipients will see it
- [ ] Preview renders HTML correctly
- [ ] Shows mobile and desktop views
- [ ] All links are functional
- [ ] Images load correctly
- [ ] Styling matches brand guidelines
- [ ] Can switch between edit and preview modes

#### Test Scenarios
```typescript
// Scenario 1: View desktop preview
1. Click "Preview" button
2. Verify full HTML render
3. Verify header/logo visible
4. Verify all content sections render
5. Verify footer with unsubscribe link
6. Click links to verify they work

// Scenario 2: View mobile preview
1. In preview mode
2. Click "Mobile View" toggle
3. Verify responsive layout
4. Verify readable font sizes
5. Verify images scale correctly
6. Verify no horizontal scroll

// Scenario 3: Send test email
1. In preview mode
2. Click "Send Test Email"
3. Enter email address
4. Click "Send"
5. Verify success message
6. Check inbox for test email
7. Verify email looks correct
```

---

## 6. Newsletter Delivery

### Story 6.1: Send Newsletter Immediately
**As a** user
**I want to** send my newsletter immediately
**So that** my subscribers get it right away

#### Acceptance Criteria
- [ ] "Send Now" button available on finalized drafts
- [ ] Shows subscriber count before sending
- [ ] Confirmation dialog with send summary
- [ ] Progress indicator during send
- [ ] Success confirmation with delivery stats
- [ ] Email delivery is logged
- [ ] Newsletter status changes to "sent"

#### Test Scenarios
```typescript
// Scenario 1: Send newsletter successfully
1. Finalize newsletter draft
2. Click "Send Now"
3. Verify confirmation dialog
4. Verify shows: "Send to 156 subscribers?"
5. Click "Confirm Send"
6. Verify progress: "Sending... 45/156"
7. Wait for completion
8. Verify success: "Sent to 154 subscribers (2 bounced)"
9. Verify newsletter status: "Sent"
10. Verify sent_at timestamp in database

// Scenario 2: Cancel send
1. Click "Send Now"
2. In confirmation dialog, click "Cancel"
3. Verify send does not proceed
4. Verify newsletter stays in draft status

// Scenario 3: Send with no subscribers
1. Try to send newsletter
2. Verify error: "No subscribers. Add subscribers first."
3. Verify "Add Subscribers" link present
```

#### Database Verification
```sql
-- Verify newsletter sent
SELECT * FROM newsletters
WHERE id = [newsletter_id]
AND status = 'sent'
AND sent_at IS NOT NULL;

-- Verify delivery logs
SELECT COUNT(*) FROM email_delivery_log
WHERE newsletter_id = [newsletter_id];

-- Verify subscriber recipients
SELECT * FROM email_delivery_log
WHERE newsletter_id = [newsletter_id]
AND status = 'delivered';
```

---

### Story 6.2: Schedule Newsletter for Later
**As a** user
**I want to** schedule my newsletter for a future date/time
**So that** it sends at an optimal time

#### Acceptance Criteria
- [ ] "Schedule Send" option available
- [ ] Date and time picker
- [ ] Time zone selector
- [ ] Preview of when newsletter will send
- [ ] Can edit or cancel scheduled send
- [ ] Notification before send (optional)
- [ ] Automatic send at scheduled time

#### Test Scenarios
```typescript
// Scenario 1: Schedule newsletter
1. Click "Schedule Send"
2. Select date: Tomorrow
3. Select time: 9:00 AM
4. Select timezone: "America/New_York"
5. Verify preview: "Will send on Jan 21, 2025 at 9:00 AM EST"
6. Click "Schedule"
7. Verify success: "Scheduled for Jan 21 at 9:00 AM"
8. Verify newsletter status: "scheduled"
9. Verify scheduled_for timestamp in database

// Scenario 2: Edit scheduled send
1. View scheduled newsletter
2. Click "Edit Schedule"
3. Change time to 10:00 AM
4. Save changes
5. Verify updated schedule time

// Scenario 3: Cancel scheduled send
1. View scheduled newsletter
2. Click "Cancel Schedule"
3. Confirm cancellation
4. Verify status changes to "draft"
5. Verify scheduled_for is cleared
```

---

## 7. Scheduling & Automation

### Story 7.1: Create Recurring Schedule
**As a** user
**I want to** set up automatic newsletter generation and sending
**So that** I don't have to manually create each issue

#### Acceptance Criteria
- [ ] Can create recurring schedule (daily/weekly/monthly)
- [ ] Can set specific day of week (for weekly)
- [ ] Can set time of day
- [ ] Can configure auto-generation parameters
- [ ] Can enable/disable schedule
- [ ] Schedule status visible on dashboard
- [ ] Preview of next scheduled run

#### Test Scenarios
```typescript
// Scenario 1: Create weekly schedule
1. Navigate to Settings → Schedule
2. Click "Create Schedule"
3. Select frequency: "Weekly"
4. Select day: "Monday"
5. Select time: "9:00 AM"
6. Configure: "Auto-generate and send"
7. Click "Create Schedule"
8. Verify schedule created
9. Verify next run shown: "Next Monday at 9:00 AM"

// Scenario 2: Create daily digest
1. Create schedule
2. Select frequency: "Daily"
3. Select time: "6:00 AM"
4. Select content criteria: "Top 10 items from yesterday"
5. Save schedule
6. Verify schedule active

// Scenario 3: Disable schedule temporarily
1. View existing schedule
2. Toggle "Active" switch off
3. Verify schedule paused
4. Verify next run shows "Paused"
```

#### Database Verification
```sql
-- Verify schedule created
SELECT * FROM schedules
WHERE workspace_id = [workspace_id]
AND is_active = true;

-- Verify schedule configuration
SELECT frequency, day_of_week, time_of_day, next_run_at
FROM schedules WHERE id = [schedule_id];
```

---

### Story 7.2: View Schedule History
**As a** user
**I want to** see past scheduled sends
**So that** I can track automation performance

#### Acceptance Criteria
- [ ] History tab shows all scheduled sends
- [ ] Shows success/failure status
- [ ] Shows delivery statistics
- [ ] Can view generated content
- [ ] Can filter by date range
- [ ] Can export history to CSV

#### Test Scenarios
```typescript
// Scenario 1: View schedule history
1. Navigate to Settings → Schedule → History
2. Verify list of past scheduled sends
3. Verify each entry shows:
   - Date/time sent
   - Status (success/failed)
   - Subscriber count
   - Open/click rates (if available)
4. Click on entry to see full details

// Scenario 2: Filter history
1. In history view
2. Select date range: "Last 30 days"
3. Verify only recent sends shown
4. Filter by status: "Failed"
5. Verify only failed sends shown
```

---

## 8. Subscriber Management

### Story 8.1: Add Subscribers Manually
**As a** user
**I want to** add subscriber email addresses
**So that** they receive my newsletters

#### Acceptance Criteria
- [ ] Can add single subscriber with email
- [ ] Can add multiple subscribers (CSV import)
- [ ] Email validation on entry
- [ ] Can add first name, last name (optional)
- [ ] Can assign tags/segments
- [ ] Duplicate detection
- [ ] Confirmation after adding

#### Test Scenarios
```typescript
// Scenario 1: Add single subscriber
1. Navigate to Settings → Subscribers
2. Click "Add Subscriber"
3. Fill email: "subscriber@example.com"
4. Fill name: "John Doe"
5. Add tag: "Early Adopter"
6. Click "Add"
7. Verify subscriber appears in list
8. Verify database record created

// Scenario 2: Bulk import CSV
1. Click "Import CSV"
2. Upload CSV file with 50 emails
3. Verify preview shows all emails
4. Verify duplicates flagged
5. Click "Import All"
6. Verify success: "Added 48 subscribers (2 duplicates skipped)"

// Scenario 3: Duplicate email handling
1. Try to add existing email
2. Verify warning: "Email already subscribed"
3. Option to update existing record
```

#### Database Verification
```sql
-- Verify subscriber created
SELECT * FROM subscribers
WHERE workspace_id = [workspace_id]
AND email = 'subscriber@example.com';

-- Verify subscriber count
SELECT COUNT(*) FROM subscribers
WHERE workspace_id = [workspace_id]
AND status = 'active';
```

---

### Story 8.2: Manage Subscriber List
**As a** user
**I want to** view and manage my subscribers
**So that** I can maintain a clean list

#### Acceptance Criteria
- [ ] Subscriber list shows all subscribers
- [ ] Can search subscribers by email/name
- [ ] Can filter by status (active/unsubscribed)
- [ ] Can filter by tags
- [ ] Can edit subscriber details
- [ ] Can remove subscribers
- [ ] Shows subscription date

#### Test Scenarios
```typescript
// Scenario 1: View subscriber list
1. Navigate to Subscribers tab
2. Verify list shows all subscribers
3. Verify columns: Email, Name, Status, Joined Date
4. Verify pagination for >50 subscribers
5. Verify total count displayed

// Scenario 2: Search subscribers
1. Type "john" in search box
2. Verify real-time filtering
3. Verify all "John" matches shown
4. Clear search
5. Verify full list restored

// Scenario 3: Edit subscriber
1. Click "Edit" on subscriber
2. Update name
3. Add new tag
4. Save changes
5. Verify updates reflected immediately

// Scenario 4: Remove subscriber
1. Select subscriber
2. Click "Remove"
3. Confirm removal
4. Verify subscriber removed from list
5. Verify status set to "removed" (not deleted)
```

---

### Story 8.3: Unsubscribe Management
**As a** subscriber
**I want to** easily unsubscribe from emails
**So that** I stop receiving them

#### Acceptance Criteria
- [ ] Unsubscribe link in every email
- [ ] Unsubscribe page confirms action
- [ ] One-click unsubscribe (no login required)
- [ ] Confirmation message shown
- [ ] User can resubscribe if desired
- [ ] Unsubscribe logged in database

#### Test Scenarios
```typescript
// Scenario 1: Unsubscribe via email link
1. Receive newsletter email
2. Click "Unsubscribe" link in footer
3. Verify unsubscribe confirmation page loads
4. Click "Confirm Unsubscribe"
5. Verify success: "You've been unsubscribed"
6. Verify no longer receives emails
7. Verify database status: "unsubscribed"

// Scenario 2: Resubscribe
1. After unsubscribing
2. Click "Resubscribe" link
3. Verify confirmation
4. Verify status changes to "active"
5. Verify receives future emails
```

---

## 9. Analytics & Tracking

### Story 9.1: View Newsletter Analytics
**As a** user
**I want to** see open and click rates for my newsletters
**So that** I can measure engagement

#### Acceptance Criteria
- [ ] Analytics dashboard shows key metrics
- [ ] Metrics include: Open rate, Click rate, Delivery rate
- [ ] Can view analytics per newsletter
- [ ] Can view aggregate analytics (all newsletters)
- [ ] Charts show trends over time
- [ ] Can filter by date range

#### Test Scenarios
```typescript
// Scenario 1: View newsletter analytics
1. Navigate to Analytics page
2. Verify key metrics displayed:
   - Total subscribers: 156
   - Avg open rate: 42.3%
   - Avg click rate: 12.1%
   - Total newsletters sent: 12
3. Verify charts render correctly
4. Verify data updates daily

// Scenario 2: View specific newsletter analytics
1. Click on specific newsletter
2. Verify detailed metrics:
   - Sent: 156
   - Delivered: 154 (98.7%)
   - Opened: 65 (42.2%)
   - Clicked: 18 (11.7%)
   - Bounced: 2 (1.3%)
3. Verify top clicked links shown
4. Verify click map for content items

// Scenario 3: Date range filtering
1. Select "Last 30 days"
2. Verify metrics update
3. Select "Custom range"
4. Pick specific dates
5. Verify filtered analytics
```

---

### Story 9.2: Export Analytics Data
**As a** user
**I want to** export analytics data
**So that** I can create custom reports

#### Acceptance Criteria
- [ ] Can export to CSV format
- [ ] Can export to PDF report
- [ ] Export includes all key metrics
- [ ] Can select date range for export
- [ ] Export downloads automatically
- [ ] Filename includes date range

#### Test Scenarios
```typescript
// Scenario 1: Export CSV
1. Navigate to Analytics
2. Select date range
3. Click "Export to CSV"
4. Verify download starts
5. Verify filename: "analytics_2025-01-01_2025-01-31.csv"
6. Open CSV
7. Verify all metrics included

// Scenario 2: Generate PDF report
1. Click "Generate Report"
2. Verify PDF generation progress
3. Download PDF
4. Verify includes:
   - Summary metrics
   - Charts/graphs
   - Newsletter list with stats
   - Top performing content
```

---

### Story 9.3: Track Link Performance
**As a** user
**I want to** see which links get the most clicks
**So that** I know what content resonates

#### Acceptance Criteria
- [ ] Shows top 10 most clicked links
- [ ] Shows click count per link
- [ ] Shows unique clicks vs total clicks
- [ ] Can see link performance per newsletter
- [ ] Can see which content items drive clicks
- [ ] Links have click-through rate displayed

#### Test Scenarios
```typescript
// Scenario 1: View top links
1. Navigate to Analytics → Links
2. Verify top 10 links listed
3. Verify each shows:
   - URL/title
   - Total clicks
   - Unique clicks
   - Click rate
4. Verify sorted by total clicks (descending)

// Scenario 2: Link performance by newsletter
1. Select specific newsletter
2. View links in that newsletter
3. Verify each content item shows clicks
4. Identify top performing items
```

---

## 10. Style & Writing Profile

### Story 10.1: Train AI on Writing Style
**As a** user
**I want to** train the AI on my writing style
**So that** generated newsletters match my voice

#### Acceptance Criteria
- [ ] Can upload past newsletter samples
- [ ] Can paste text samples (20+ required)
- [ ] AI analyzes writing patterns
- [ ] Shows style profile summary
- [ ] Profile includes tone, sentence length, vocabulary
- [ ] Can retrain with new samples
- [ ] Generated content uses learned style

#### Test Scenarios
```typescript
// Scenario 1: Upload writing samples
1. Navigate to Settings → Writing Style
2. Click "Train Style"
3. Paste 25 newsletter samples
4. Separate with "---"
5. Click "Analyze Style"
6. Verify progress: "Analyzing 25 samples..."
7. Wait for completion
8. Verify style profile shown:
   - Tone: Conversational
   - Avg sentence length: 15 words
   - Formality: 35%
   - Uses emojis: Yes
9. Click "Save Profile"

// Scenario 2: Insufficient samples
1. Paste only 5 samples
2. Try to analyze
3. Verify warning: "Need at least 10 samples for accurate training"
4. Verify can still save (with lower confidence)

// Scenario 3: Verify style applied
1. Train style profile
2. Generate new newsletter
3. Verify draft matches style:
   - Similar sentence lengths
   - Similar tone
   - Uses characteristic phrases
```

---

### Story 10.2: Customize Newsletter Tone
**As a** user
**I want to** choose the tone for my newsletter
**So that** it matches my brand voice

#### Acceptance Criteria
- [ ] Tone selector with options: Professional, Casual, Technical, Humorous
- [ ] Can set default tone per workspace
- [ ] Can override tone per newsletter
- [ ] Preview shows how tone affects content
- [ ] Saved tone preference persists

#### Test Scenarios
```typescript
// Scenario 1: Set default tone
1. Navigate to Settings → Writing Style
2. Select tone: "Conversational"
3. Set formality slider: 30%
4. Save settings
5. Generate newsletter
6. Verify casual, friendly tone in draft

// Scenario 2: Override tone for single newsletter
1. Start generating newsletter
2. In generation options, select "Professional"
3. Generate
4. Verify more formal language used
5. Next newsletter uses default tone again
```

---

## 11. Trends Detection

### Story 11.1: View Detected Trends
**As a** user
**I want to** see emerging trends in my content sources
**So that** I can write about hot topics early

#### Acceptance Criteria
- [ ] Trends section shows 3-5 detected trends
- [ ] Each trend shows: Topic, strength score, sources
- [ ] Trend explanation provided
- [ ] Can click to see related content
- [ ] Trends update daily
- [ ] Can add trend to newsletter

#### Test Scenarios
```typescript
// Scenario 1: View trends dashboard
1. Navigate to Content → Trends
2. Verify 3-5 trends displayed
3. For each trend verify:
   - Topic name
   - Strength indicator (🔥 or 📈)
   - Number of mentions
   - Number of sources
   - AI-generated explanation
4. Click on trend
5. Verify related content items shown

// Scenario 2: Add trend to newsletter
1. View trend details
2. Click "Add to Newsletter"
3. Verify trend section added to draft
4. Verify includes:
   - Trend title
   - Explanation
   - 3-5 related items
```

---

### Story 11.2: Configure Trend Detection
**As a** user
**I want to** adjust trend detection settings
**So that** I get relevant trends for my niche

#### Acceptance Criteria
- [ ] Can set minimum confidence threshold
- [ ] Can require cross-source validation
- [ ] Can exclude certain topics/keywords
- [ ] Can set trend velocity sensitivity
- [ ] Settings persist per workspace

#### Test Scenarios
```typescript
// Scenario 1: Adjust trend sensitivity
1. Navigate to Settings → Trends
2. Set confidence threshold: 60%
3. Enable "Cross-source validation"
4. Set min sources: 2
5. Save settings
6. Verify next trend detection uses new settings

// Scenario 2: Exclude topics
1. In settings, add excluded keywords: "cryptocurrency"
2. Save
3. Verify trends about crypto no longer appear
```

---

## 12. Feedback Loop

### Story 12.1: Rate Content Items
**As a** user
**I want to** thumbs up/down content items
**So that** the AI learns my preferences

#### Acceptance Criteria
- [ ] Each content item has 👍 👎 buttons
- [ ] Clicking records feedback immediately
- [ ] Visual confirmation of rating
- [ ] Can change rating
- [ ] Feedback influences future content selection
- [ ] Feedback persists across sessions

#### Test Scenarios
```typescript
// Scenario 1: Rate content positively
1. View content item
2. Click 👍 (thumbs up)
3. Verify button turns green
4. Verify feedback saved to database
5. Generate next newsletter
6. Verify more similar content appears

// Scenario 2: Rate content negatively
1. View content item
2. Click 👎 (thumbs down)
3. Verify button turns red
4. Verify feedback saved
5. Verify similar content appears less

// Scenario 3: Change rating
1. Rate item with 👍
2. Click 👎
3. Verify rating updates
4. Verify database updated
```

#### Database Verification
```sql
-- Verify feedback recorded
SELECT * FROM user_feedback
WHERE user_id = [user_id]
AND content_id = [content_id];

-- Check feedback influences scoring
SELECT AVG(rating) as quality_score
FROM user_feedback
WHERE source_id = [source_id];
```

---

### Story 12.2: View Learning Stats
**As a** user
**I want to** see how the AI is learning from my feedback
**So that** I can track improvement

#### Acceptance Criteria
- [ ] Learning dashboard shows feedback stats
- [ ] Shows source quality scores based on feedback
- [ ] Shows preferred content types
- [ ] Shows improvement over time
- [ ] Can reset learning data

#### Test Scenarios
```typescript
// Scenario 1: View learning dashboard
1. Navigate to Settings → Learning
2. Verify stats displayed:
   - Total feedback items: 156
   - Positive: 98 (63%)
   - Negative: 58 (37%)
3. Verify source quality scores:
   - TechCrunch: 85%
   - Reddit r/programming: 72%
4. Verify content preferences shown

// Scenario 2: Track improvement
1. View "Acceptance Rate Over Time" chart
2. Verify upward trend
3. Verify starts around 40%, improves to 70%+

// Scenario 3: Reset learning
1. Click "Reset Learning Data"
2. Confirm action
3. Verify all feedback cleared
4. Verify fresh start for learning
```

---

## 13. Settings & Configuration

### Story 13.1: Configure API Keys
**As a** user
**I want to** set up API keys for integrations
**So that** the platform can access external services

#### Acceptance Criteria
- [ ] Settings page for API keys
- [ ] Can add: OpenAI, SendGrid, YouTube, Twitter keys
- [ ] Keys are masked after entry (●●●●●)
- [ ] Can test connection for each key
- [ ] Keys stored securely (encrypted)
- [ ] Can delete/update keys

#### Test Scenarios
```typescript
// Scenario 1: Add OpenAI key
1. Navigate to Settings → API Keys
2. Click "Add OpenAI Key"
3. Paste key: "sk-abc123..."
4. Click "Save"
5. Click "Test Connection"
6. Verify success: "✓ Connected to OpenAI"

// Scenario 2: Invalid key handling
1. Enter invalid API key
2. Click "Test Connection"
3. Verify error: "Invalid API key"
4. Verify key not saved until valid

// Scenario 3: Update key
1. Click "Edit" on existing key
2. Replace with new key
3. Test connection
4. Save if valid
```

---

### Story 13.2: Configure Email Settings
**As a** user
**I want to** set up email delivery settings
**So that** newsletters send from my domain

#### Acceptance Criteria
- [ ] Can choose provider: SMTP or SendGrid
- [ ] SMTP fields: Host, port, username, password
- [ ] SendGrid fields: API key
- [ ] Can set "From" name and email
- [ ] Can set reply-to email
- [ ] Can customize email footer
- [ ] Send test email to verify setup

#### Test Scenarios
```typescript
// Scenario 1: Configure SendGrid
1. Navigate to Settings → Email
2. Select provider: "SendGrid"
3. Enter API key
4. Set from name: "Tech Weekly"
5. Set from email: "newsletter@example.com"
6. Set reply-to: "hello@example.com"
7. Click "Save"
8. Click "Send Test Email"
9. Verify test email received
10. Verify correct from/reply-to addresses

// Scenario 2: Configure SMTP
1. Select provider: "SMTP"
2. Fill in SMTP details:
   - Host: smtp.gmail.com
   - Port: 587
   - Username: user@gmail.com
   - Password: ●●●●●
3. Test connection
4. Verify success or error message
```

---

### Story 13.3: Customize Newsletter Template
**As a** user
**I want to** customize the newsletter HTML template
**So that** emails match my brand

#### Acceptance Criteria
- [ ] Template editor with live preview
- [ ] Can customize: Colors, fonts, logo
- [ ] Can edit header and footer
- [ ] Can add custom CSS
- [ ] Changes apply to all future newsletters
- [ ] Can save multiple templates
- [ ] Can revert to default template

#### Test Scenarios
```typescript
// Scenario 1: Customize brand colors
1. Navigate to Settings → Template
2. Click "Customize Template"
3. Change primary color: #007bff → #FF6B35
4. Change background: #ffffff → #F5F5F5
5. Upload logo image
6. Verify live preview updates
7. Click "Save Template"
8. Generate newsletter
9. Verify uses new colors/logo

// Scenario 2: Edit footer
1. In template editor
2. Edit footer text
3. Add social media links
4. Add company address
5. Preview changes
6. Save
7. Verify appears in next newsletter

// Scenario 3: Create multiple templates
1. Save current as "Tech Style"
2. Click "New Template"
3. Create "Marketing Style"
4. Switch between templates
5. Verify each has independent settings
```

---

## E2E Test Coverage Map

### Priority Levels
- **P0 (Critical)**: Core user flows that must work
- **P1 (High)**: Important features users expect
- **P2 (Medium)**: Nice-to-have features
- **P3 (Low)**: Edge cases and advanced features

### Legend
- ✅ **Implemented** - Frontend + Backend + E2E test working
- ⚠️ **Partial** - Some parts working, but incomplete
- 🔧 **Backend Only** - Backend exists but no frontend
- 🎨 **Frontend Only** - UI exists but not connected to backend
- ❌ **Blocked** - Cannot implement without dependencies
- ⏳ **Planned** - Not started

### Test Coverage

| User Story | Priority | Frontend | Backend | E2E Test | Status | Blocker |
|------------|----------|----------|---------|----------|--------|---------|
| **1. Authentication** |
| 1.1 User Registration | P0 | ✅ `/register` | ✅ POST /auth/signup | ✅ journey-1 | ✅ Working | - |
| 1.2 User Login | P0 | ✅ `/login` | ✅ POST /auth/login | ✅ journey-1 | ✅ Working | - |
| 1.3 Onboarding Flow | P1 | 🎨 Dashboard | ❌ No backend | ⏳ Planned | 🎨 UI Only | No backend logic |
| **2. Workspaces** |
| 2.1 Create Workspace | P0 | ✅ Dashboard | ✅ POST /workspaces | ✅ journey-1 | ✅ Working | - |
| 2.2 Switch Workspaces | P1 | ⚠️ Selector | ✅ GET /workspaces | ⏳ Planned | ⚠️ Partial | Need multi-workspace test |
| **3. Content Sources** |
| 3.1 Add RSS Source | P0 | ✅ Dashboard | ✅ Config API | ✅ journey-2 | ✅ Working | - |
| 3.2 Add Reddit Source | P0 | ✅ Dashboard | ✅ Config API | ✅ journey-2 | ✅ Working | - |
| 3.3 Add Twitter Source | P1 | ✅ Dashboard | ✅ Config API | ⏳ Planned | ✅ Working | Need API keys |
| 3.4 Add YouTube Source | P2 | ✅ Dashboard | ✅ Config API | ⏳ Planned | ✅ Working | Need API keys |
| 3.5 Edit Source | P1 | ✅ Dashboard | ✅ Config API | ⏳ Planned | ✅ Working | - |
| 3.6 Delete Source | P1 | ✅ Dashboard | ✅ Config API | ⏳ Planned | ✅ Working | - |
| **4. Content Discovery** |
| 4.1 Manual Scraping | P0 | ✅ Dashboard | ✅ POST /content/scrape | ✅ journey-2 | ✅ Working | - |
| 4.2 View Content List | P0 | ❌ No page | ✅ GET /content/workspaces/{id} | ❌ No test | 🔧 Backend Only | No frontend page |
| 4.3 Content Details | P1 | ❌ No page | ✅ GET /content/... | ❌ No test | 🔧 Backend Only | No frontend page |
| **5. Newsletter Generation** |
| 5.1 Generate Draft | P0 | ✅ Dashboard | ✅ POST /newsletters/generate | ✅ journey-3 | ✅ Working | - |
| 5.2 Edit Draft | P0 | ✅ Modal | ✅ PUT /newsletters/{id} | ✅ journey-3 | ✅ Working | - |
| 5.3 Preview Newsletter | P1 | ✅ Modal | ✅ GET /newsletters/{id} | ⏳ Planned | ✅ Working | - |
| **6. Delivery** |
| 6.1 Send Immediately | P0 | ✅ Modal | ✅ POST /delivery/send | ✅ journey-5 | ✅ Working | - |
| 6.2 Send Test Email | P0 | ✅ Modal | ✅ POST /delivery/send-sync | ✅ journey-5 | ✅ Working | - |
| 6.3 Schedule Send | P1 | ✅ Modal | ✅ POST /scheduler/.../run-now | ✅ journey-5 | ✅ Working | - |
| **7. Scheduling** |
| 7.1 Recurring Schedule | P1 | 🎨 Settings | ✅ POST /scheduler/daily | ❌ No test | 🎨 UI Only | Settings not connected |
| 7.2 Schedule History | P2 | ❌ No UI | ✅ GET /scheduler/... | ❌ No test | 🔧 Backend Only | No frontend UI |
| **8. Subscribers** |
| 8.1 Add Subscribers | P0 | 🎨 Settings | ✅ POST /subscribers | ❌ No test | 🎨 UI Only | Settings not connected |
| 8.2 Manage List | P1 | 🎨 Settings | ✅ GET /subscribers/... | ❌ No test | 🎨 UI Only | Settings not connected |
| 8.3 Unsubscribe | P1 | ❌ No page | ✅ POST /subscribers/.../unsubscribe | ❌ No test | 🔧 Backend Only | Public unsubscribe page needed |
| **9. Newsletter History & Analytics** |
| 9.1 View Newsletter History | P1 | ✅ `/app/history` | ✅ GET /newsletters/... | ✅ journey-4 | ✅ Working | - |
| 9.2 Export Data | P2 | ❌ No UI | ✅ GET /analytics/.../export | ❌ No test | 🔧 Backend Only | No export button |
| 9.3 Link Tracking | P2 | ❌ No UI | ✅ GET /analytics/... | ❌ No test | 🔧 Backend Only | No frontend display |
| **10. Writing Style** |
| 10.1 Train Style | P1 | 🎨 Settings | ✅ POST /style/train | ❌ No test | 🎨 UI Only | Settings not connected |
| 10.2 Customize Tone | P2 | 🎨 Settings | ✅ PUT /style/... | ❌ No test | 🎨 UI Only | Settings not connected |
| **11. Trends** |
| 11.1 View Trends | P1 | 🎨 Settings | ✅ GET /trends/... | ❌ No test | 🎨 UI Only | Settings not connected |
| 11.2 Configure Detection | P2 | 🎨 Settings | ✅ PUT /trends/.../config | ❌ No test | 🎨 UI Only | Settings not connected |
| **12. Feedback** |
| 12.1 Rate Content | P1 | ❌ No UI | ✅ POST /feedback | ❌ No test | 🔧 Backend Only | No thumbs up/down UI |
| 12.2 Learning Stats | P2 | 🎨 Settings | ✅ GET /feedback/.../stats | ❌ No test | 🎨 UI Only | Settings not connected |
| **13. Settings** |
| 13.1 API Keys | P0 | 🎨 Settings | ❌ No backend | ❌ No test | 🎨 UI Only | API keys stored in config? |
| 13.2 Email Settings | P0 | 🎨 Settings | ❌ No backend | ❌ No test | 🎨 UI Only | Email config in workspace? |
| 13.3 Custom Template | P2 | 🎨 Settings | ❌ No backend | ❌ No test | 🎨 UI Only | Template customization needed |

### Summary by Status
- ✅ **Fully Working:** 12 stories (35%) ← **UPDATED!**
- ⚠️ **Partially Working:** 2 stories (6%)
- 🎨 **Frontend Only:** 10 stories (29%)
- 🔧 **Backend Only:** 7 stories (21%)
- ❌ **Not Started:** 3 stories (9%)

### Recently Completed ✨
- ✅ **Story 9.1: View Newsletter History** - History page now connected to backend, displays real sent newsletters
  - Frontend: [frontend-nextjs/src/app/app/history/page.tsx](../src/app/app/history/page.tsx)
  - E2E Tests: [frontend-nextjs/e2e/journey-4-history-view.spec.ts](../e2e/journey-4-history-view.spec.ts)
  - Status: Fully working with 7 test scenarios

- ✅ **Stories 6.1, 6.2, 6.3: Newsletter Delivery** - Delivery API now fully connected to UI
  - Frontend: [frontend-nextjs/src/app/app/page.tsx](../src/app/app/page.tsx) (modals)
  - API: [frontend-nextjs/src/lib/api/delivery.ts](../src/lib/api/delivery.ts)
  - E2E Tests: [frontend-nextjs/e2e/journey-5-delivery.spec.ts](../e2e/journey-5-delivery.spec.ts)
  - Features: Send Now, Send Test Email, Schedule Send
  - Status: Fully working with 7 test scenarios

---

## Using These User Stories with Playwright MCP

### Approach 1: Natural Language Testing

Simply tell Claude which user story to test:

```
"Test User Story 3.1: Add RSS Feed Source using Playwright MCP"
```

Claude will:
1. Navigate to the page
2. Perform all test steps
3. Verify acceptance criteria
4. Check database state
5. Report results

### Approach 2: Generate Test Code

```
"Generate Playwright test code for User Story 5.1: Generate Newsletter Draft"
```

Claude will create a complete test file with all scenarios.

### Approach 3: Debug Existing Tests

```
"Journey 2 is failing at the scraping step. Use Playwright MCP to debug"
```

Claude will:
1. Navigate to failure point
2. Take screenshots
3. Check element states
4. Identify the issue
5. Suggest fixes

---

## Quick Reference: Test Commands

### Run Specific Story Tests
```bash
# Test authentication flow
npm run test:e2e journey-1

# Test content sources
npm run test:e2e journey-2

# Test newsletter generation
npm run test:e2e journey-3
```

### Using Playwright MCP via Claude
```
"Test the complete user registration flow"
"Verify workspace switching works correctly"
"Check if email delivery settings save properly"
"Debug why content scraping is timing out"
```

---

## Coverage Goals

### Sprint 1 (Current)
- ✅ Core authentication (Stories 1.1, 1.2)
- ✅ Workspace creation (Story 2.1)
- ✅ Basic source management (Stories 3.1, 3.2)
- ✅ Content scraping (Story 4.1)
- ✅ Newsletter generation (Stories 5.1, 5.2)
- ✅ Email delivery (Story 6.1)
- ✅ Subscriber management (Story 8.1)

### Sprint 2 (Planned)
- ⏳ Advanced source types (Stories 3.3, 3.4)
- ⏳ Source editing/deletion (Stories 3.5, 3.6)
- ⏳ Schedule management (Stories 7.1, 7.2)
- ⏳ Analytics basics (Story 9.1)

### Sprint 3 (Future)
- ⏳ Writing style training (Story 10.1)
- ⏳ Trends detection (Story 11.1)
- ⏳ Feedback loop (Stories 12.1, 12.2)
- ⏳ Advanced analytics (Stories 9.2, 9.3)

---

**Total User Stories:** 33
**Implemented E2E Tests:** 8 (24%)
**Planned Tests:** 25 (76%)

Use this document as your complete reference for E2E testing with Playwright MCP!
