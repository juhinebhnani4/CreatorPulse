# CreatorPulse E2E User Journeys

## Overview
This document defines the complete user journeys tested in E2E tests.
Each step includes frontend action + database verification.

---

## Journey 1: New User Onboarding
**User Story**: As a new user, I want to sign up and create my first workspace so I can start curating content.

### Steps:
1. **Landing Page** → User visits homepage
   - Frontend: Renders landing/login page
   - DB Check: No action yet

2. **Sign Up** → User clicks "Sign Up" and fills form
   - Frontend: Fill email, password, submit form
   - DB Check: Verify `users` table has new user record
   - DB Check: Verify `user_id` is generated

3. **Auto Login** → User is automatically logged in
   - Frontend: Redirected to dashboard
   - DB Check: Verify session token exists
   - DB Check: Verify `auth.users` has session

4. **Create First Workspace** → User creates workspace
   - Frontend: Click "Create Workspace", enter name & description
   - DB Check: Verify `workspaces` table has new record
   - DB Check: Verify `workspace.user_id` matches logged-in user
   - DB Check: Verify `workspace.created_at` timestamp

---

## Journey 2: Configure Content Sources
**User Story**: As a user, I want to add content sources to my workspace so I can aggregate content.

### Steps:
1. **Navigate to Sources** → User clicks "Content Sources"
   - Frontend: Navigate to `/workspaces/[id]/sources`
   - DB Check: Verify workspace exists and user has access

2. **Add RSS Feed** → User adds first RSS feed
   - Frontend: Click "Add Source", select "RSS", enter URL
   - DB Check: Verify `content_sources` table has new record
   - DB Check: Verify `source.workspace_id` matches current workspace
   - DB Check: Verify `source.source_type = 'rss'`

3. **Add Reddit Source** → User adds Reddit subreddit
   - Frontend: Select "Reddit", enter subreddit name
   - DB Check: Verify second `content_sources` record created
   - DB Check: Verify `source.source_type = 'reddit'`

4. **Add Twitter/X Source** → User adds Twitter account
   - Frontend: Select "Twitter", enter username
   - DB Check: Verify third `content_sources` record created
   - DB Check: Verify `source.source_type = 'twitter'`

5. **Verify Sources List** → User sees all sources
   - Frontend: Display all 3 sources in list
   - DB Check: Query returns exactly 3 sources for workspace

---

## Journey 3: Scrape Content
**User Story**: As a user, I want to scrape content from my sources so I can review it.

### Steps:
1. **Trigger Scrape** → User clicks "Scrape Now"
   - Frontend: Click scrape button, show loading state
   - DB Check: Verify `scrape_jobs` table has new job
   - DB Check: Verify `job.status = 'pending'`

2. **Wait for Scraping** → System scrapes content
   - Frontend: Poll for job status, show progress
   - DB Check: Verify `job.status` changes to 'running'
   - DB Check: Verify `job.status` eventually becomes 'completed'

3. **View Scraped Content** → User sees content list
   - Frontend: Display content items with previews
   - DB Check: Verify `content_items` table has new records
   - DB Check: Verify `content_item.workspace_id` matches
   - DB Check: Verify each item has `source_id`, `title`, `url`

4. **Filter Content** → User filters by source type
   - Frontend: Select "RSS" filter
   - DB Check: Query filtered results match source type

---

## Journey 4: Generate Newsletter
**User Story**: As a user, I want to generate a newsletter from scraped content so I can send it to subscribers.

### Steps:
1. **Navigate to Newsletter** → User clicks "Generate Newsletter"
   - Frontend: Navigate to `/workspaces/[id]/newsletter`
   - DB Check: Verify workspace exists

2. **Select Content** → User selects content items
   - Frontend: Check boxes for 5-10 content items
   - DB Check: Verify selected items exist in `content_items`

3. **Configure Newsletter** → User sets newsletter options
   - Frontend: Enter subject, preview text, tone
   - DB Check: No action yet (client-side only)

4. **Generate** → User clicks "Generate Newsletter"
   - Frontend: Show loading, call generation API
   - DB Check: Verify `newsletters` table has new record
   - DB Check: Verify `newsletter.workspace_id` matches
   - DB Check: Verify `newsletter.status = 'generating'`

5. **View Generated Newsletter** → System generates content
   - Frontend: Poll for completion, show preview
   - DB Check: Verify `newsletter.status = 'completed'`
   - DB Check: Verify `newsletter.content_html` is populated
   - DB Check: Verify `newsletter.generated_at` timestamp

6. **Preview Newsletter** → User reviews newsletter
   - Frontend: Display HTML preview
   - DB Check: Verify newsletter content matches items

---

## Journey 5: Send Newsletter
**User Story**: As a user, I want to send my newsletter to subscribers so they receive my curated content.

### Steps:
1. **Add Subscribers** → User adds email addresses
   - Frontend: Click "Manage Subscribers", enter emails
   - DB Check: Verify `subscribers` table has new records
   - DB Check: Verify `subscriber.workspace_id` matches

2. **Send Newsletter** → User clicks "Send Now"
   - Frontend: Confirm dialog, click send
   - DB Check: Verify `newsletter.status = 'sending'`
   - DB Check: Verify `email_delivery_log` records created

3. **Verify Delivery** → System sends emails
   - Frontend: Show delivery progress
   - DB Check: Verify `newsletter.status = 'sent'`
   - DB Check: Verify `email_delivery_log.status = 'delivered'`
   - DB Check: Verify `newsletter.sent_at` timestamp

---

## Journey 6: Schedule Newsletter
**User Story**: As a user, I want to schedule newsletters to send automatically so I don't have to manually trigger them.

### Steps:
1. **Navigate to Schedule** → User clicks "Schedule"
   - Frontend: Navigate to `/workspaces/[id]/schedule`
   - DB Check: Verify workspace exists

2. **Create Schedule** → User sets up recurring schedule
   - Frontend: Select frequency (daily/weekly), time, day
   - DB Check: Verify `schedules` table has new record
   - DB Check: Verify `schedule.workspace_id` matches
   - DB Check: Verify `schedule.frequency`, `schedule.next_run_at`

3. **Enable Schedule** → User activates schedule
   - Frontend: Toggle "Active" switch
   - DB Check: Verify `schedule.is_active = true`

---

## Journey 7: View Analytics
**User Story**: As a user, I want to see newsletter performance so I can improve engagement.

### Steps:
1. **Navigate to Analytics** → User clicks "Analytics"
   - Frontend: Navigate to `/workspaces/[id]/analytics`
   - DB Check: Query `analytics_events` for workspace

2. **View Open Rates** → User sees email opens
   - Frontend: Display open rate chart
   - DB Check: Verify `event_type = 'email_opened'` count
   - DB Check: Calculate open rate percentage

3. **View Click Rates** → User sees link clicks
   - Frontend: Display click rate chart
   - DB Check: Verify `event_type = 'link_clicked'` count
   - DB Check: Verify `metadata` contains clicked URLs

4. **View Top Content** → User sees best performing content
   - Frontend: Display top clicked items
   - DB Check: Join `analytics_events` with `content_items`
   - DB Check: Group by content_id and count clicks

---

## Journey 8: User Feedback Loop
**User Story**: As a user, I want to provide feedback on content quality so the system learns my preferences.

### Steps:
1. **Rate Content** → User upvotes/downvotes items
   - Frontend: Click thumbs up/down on content item
   - DB Check: Verify `user_feedback` table has record
   - DB Check: Verify `feedback.user_id` and `feedback.content_id`
   - DB Check: Verify `feedback.rating` (1 or -1)

2. **View Style Profile** → System learns preferences
   - Frontend: Navigate to "My Style Profile"
   - DB Check: Verify `style_profiles` table has record
   - DB Check: Verify aggregated preferences from feedback

3. **Apply Preferences** → Next generation uses profile
   - Frontend: Generate new newsletter
   - DB Check: Verify generation uses `style_profile_id`

---

## Test Data Cleanup Strategy

After each journey:
1. Delete test user from `auth.users`
2. Cascade delete workspaces (triggers delete on related tables)
3. Delete orphaned records from:
   - `content_sources`
   - `content_items`
   - `newsletters`
   - `subscribers`
   - `schedules`
   - `analytics_events`
   - `user_feedback`
   - `style_profiles`

## Database Verification Patterns

### Pattern 1: Record Creation
```typescript
// Verify record exists with expected data
const record = await supabase
  .from('table_name')
  .select('*')
  .eq('id', recordId)
  .single();

expect(record.data).toBeDefined();
expect(record.data.field).toBe(expectedValue);
```

### Pattern 2: Foreign Key Relationships
```typescript
// Verify relationship integrity
const child = await supabase
  .from('child_table')
  .select('*, parent_table(*)')
  .eq('id', childId)
  .single();

expect(child.data.parent_table).toBeDefined();
expect(child.data.parent_id).toBe(child.data.parent_table.id);
```

### Pattern 3: Timestamps
```typescript
// Verify timestamps are set correctly
const record = await supabase
  .from('table_name')
  .select('created_at, updated_at')
  .eq('id', recordId)
  .single();

expect(new Date(record.data.created_at)).toBeInstanceOf(Date);
expect(record.data.created_at).toBeLessThanOrEqual(Date.now());
```

### Pattern 4: Cascade Deletes
```typescript
// Verify cascading deletes work
await supabase.from('parent_table').delete().eq('id', parentId);

const children = await supabase
  .from('child_table')
  .select('*')
  .eq('parent_id', parentId);

expect(children.data).toHaveLength(0);
```
