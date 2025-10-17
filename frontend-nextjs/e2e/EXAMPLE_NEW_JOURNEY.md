# How to Add a New E2E User Journey

This guide shows you how to create a new E2E test following the existing patterns.

## Example: Journey 4 - Analytics & Feedback

Let's create a test for viewing analytics and providing feedback.

### Step 1: Document the Journey

Add to `USER_JOURNEYS.md`:

```markdown
## Journey 4: View Analytics & Provide Feedback
**User Story**: As a user, I want to see newsletter performance and provide feedback on content.

### Steps:
1. **Navigate to Analytics** → User clicks "Analytics"
   - Frontend: Navigate to `/workspaces/[id]/analytics`
   - DB Check: Query `analytics_events` for workspace

2. **View Open Rates** → User sees email opens
   - Frontend: Display open rate chart
   - DB Check: Count `event_type = 'email_opened'`

3. **Rate Content** → User upvotes/downvotes items
   - Frontend: Click thumbs up/down
   - DB Check: Verify `user_feedback` table has record

4. **View Style Profile** → System learns preferences
   - Frontend: Navigate to "My Style Profile"
   - DB Check: Verify `style_profiles` updated
```

### Step 2: Create Test File

Create `e2e/journey-4-analytics-feedback.spec.ts`:

```typescript
/**
 * E2E Test: User Journey 4 - Analytics & Feedback
 *
 * User Story: As a user, I want to see newsletter performance
 * and provide feedback on content quality.
 */

import { test, expect } from './fixtures/playwright-fixtures';
import { wait } from './fixtures/test-data';

test.describe('User Journey 4: Analytics & Feedback', () => {
  let workspaceId: string;
  let userId: string;
  let newsletterId: string;
  let contentItemId: string;

  // Setup: Create workspace with newsletter and analytics data
  test.beforeAll(async ({ supabase }) => {
    // TODO: Setup test data
    // - Create user
    // - Create workspace
    // - Create newsletter with analytics events
    // - Create content items
  });

  // Cleanup after tests
  test.afterAll(async ({ supabase }) => {
    if (workspaceId) {
      await supabase.cleanupTestWorkspace(workspaceId);
    }
    if (userId) {
      await supabase.cleanupTestUser(userId);
    }
  });

  test('should complete full analytics and feedback journey', async ({
    page,
    supabase,
  }) => {
    // ==================== STEP 1: Navigate to Analytics ====================
    await test.step('Step 1: User navigates to Analytics page', async () => {
      // Login first
      await page.goto('/login');
      // ... login logic ...

      // Navigate to analytics
      const analyticsLink = page.getByRole('link', { name: /analytics|stats/i });
      await analyticsLink.click();
      await wait(1000);

      // Verify we're on analytics page
      await expect(page.url()).toMatch(/analytics/);
      await expect(page.getByText(/analytics|statistics/i)).toBeVisible();

      // Extract workspace ID from URL
      const urlMatch = page.url().match(/workspaces\/([a-f0-9-]+)/);
      if (urlMatch) {
        workspaceId = urlMatch[1];
      }

      await page.screenshot({
        path: 'test-results/journey4-step1-analytics-page.png'
      });
    });

    // ==================== DB CHECK: Analytics Events Exist ====================
    await test.step('DB Check: Verify analytics events in database', async () => {
      const { data: events } = await supabase.getNewsletterAnalytics(newsletterId);

      expect(events).not.toBeNull();
      expect(events?.length).toBeGreaterThan(0);

      console.log(`✓ ${events?.length} analytics events found`);
    });

    // ==================== STEP 2: View Open Rates ====================
    await test.step('Step 2: User views email open rates', async () => {
      // Look for open rate metrics
      const openRateCard = page.getByText(/open rate|opens/i);
      await expect(openRateCard).toBeVisible();

      // Verify percentage is displayed
      const percentageRegex = /\d+(\.\d+)?%/;
      await expect(page.getByText(percentageRegex)).toBeVisible();

      await page.screenshot({
        path: 'test-results/journey4-step2-open-rates.png'
      });
    });

    // ==================== DB CHECK: Count Open Events ====================
    await test.step('DB Check: Verify open events count matches display', async () => {
      const openCount = await supabase.countEventsByType(
        newsletterId,
        'email_opened'
      );

      expect(openCount).toBeGreaterThan(0);

      console.log(`✓ ${openCount} email open events in database`);
    });

    // ==================== STEP 3: View Click Rates ====================
    await test.step('Step 3: User views link click rates', async () => {
      const clickRateCard = page.getByText(/click rate|clicks/i);
      await expect(clickRateCard).toBeVisible();

      await page.screenshot({
        path: 'test-results/journey4-step3-click-rates.png'
      });
    });

    // ==================== DB CHECK: Count Click Events ====================
    await test.step('DB Check: Verify click events in database', async () => {
      const clickCount = await supabase.countEventsByType(
        newsletterId,
        'link_clicked'
      );

      console.log(`✓ ${clickCount} link click events in database`);
    });

    // ==================== STEP 4: Navigate to Content ====================
    await test.step('Step 4: User navigates to content list', async () => {
      const contentLink = page.getByRole('link', { name: /content|articles/i });
      await contentLink.click();
      await wait(1000);

      await expect(page.url()).toMatch(/content/);
    });

    // ==================== STEP 5: Provide Positive Feedback ====================
    await test.step('Step 5: User upvotes a content item', async () => {
      // Find first content item
      const contentItem = page.locator('[data-testid="content-item"]').first();
      await expect(contentItem).toBeVisible();

      // Click upvote button
      const upvoteButton = contentItem.getByRole('button', {
        name: /upvote|thumbs up|like/i
      });
      await upvoteButton.click();
      await wait(1000);

      // Verify feedback registered
      await expect(page.getByText(/feedback saved|thank you/i)).toBeVisible();

      await page.screenshot({
        path: 'test-results/journey4-step5-upvote.png'
      });
    });

    // ==================== DB CHECK: Feedback Record Created ====================
    await test.step('DB Check: Verify feedback in database', async () => {
      // Get content item ID from page
      const contentItemElement = page.locator('[data-testid="content-item"]').first();
      contentItemId = await contentItemElement.getAttribute('data-content-id') || '';

      // Verify feedback record
      const { exists } = await supabase.verifyFeedback(userId, contentItemId);
      expect(exists).toBe(true);

      console.log(`✓ Feedback record created for content ${contentItemId}`);
    });

    // ==================== STEP 6: Provide Negative Feedback ====================
    await test.step('Step 6: User downvotes another content item', async () => {
      const secondItem = page.locator('[data-testid="content-item"]').nth(1);

      const downvoteButton = secondItem.getByRole('button', {
        name: /downvote|thumbs down|dislike/i
      });
      await downvoteButton.click();
      await wait(1000);

      await page.screenshot({
        path: 'test-results/journey4-step6-downvote.png'
      });
    });

    // ==================== STEP 7: View Style Profile ====================
    await test.step('Step 7: User views their style profile', async () => {
      // Navigate to profile/settings
      const profileButton = page.getByRole('button', { name: /profile|account/i });
      await profileButton.click();
      await wait(500);

      const styleProfileLink = page.getByRole('link', {
        name: /style profile|preferences/i
      });

      if (await styleProfileLink.count() > 0) {
        await styleProfileLink.click();
        await wait(1000);

        // Verify style profile page
        await expect(page.getByText(/style profile|preferences/i)).toBeVisible();

        await page.screenshot({
          path: 'test-results/journey4-step7-style-profile.png'
        });
      }
    });

    // ==================== DB CHECK: Style Profile Updated ====================
    await test.step('DB Check: Verify style profile reflects feedback', async () => {
      const { data: styleProfile } = await supabase.getUserStyleProfile(userId);

      if (styleProfile) {
        expect(styleProfile.user_id).toBe(userId);
        expect(styleProfile.updated_at).toBeTruthy();

        console.log('✓ Style profile exists and updated');
      }

      console.log('✓ Analytics and feedback journey completed successfully!');
    });
  });

  // Additional test cases
  test('should show empty state when no analytics data', async ({ page }) => {
    await test.step('View analytics with no data', async () => {
      await page.goto('/workspaces/new-workspace/analytics');

      await expect(page.getByText(/no data|no analytics/i)).toBeVisible();
    });
  });

  test('should allow filtering analytics by date range', async ({ page }) => {
    await test.step('Filter analytics by last 7 days', async () => {
      // ... date filter logic ...
    });
  });
});
```

### Step 3: Add Supabase Helper Methods (if needed)

If you need new database verification methods, add them to `utils/supabase-helper.ts`:

```typescript
/**
 * Get feedback count for a user
 */
async getFeedbackCount(userId: string): Promise<number> {
  const { data } = await this.serviceClient
    .from('user_feedback')
    .select('id')
    .eq('user_id', userId);

  return data?.length || 0;
}

/**
 * Verify analytics event was logged
 */
async verifyEventLogged(
  newsletterId: string,
  eventType: string,
  userId: string
): Promise<boolean> {
  const { data } = await this.serviceClient
    .from('analytics_events')
    .select('id')
    .eq('newsletter_id', newsletterId)
    .eq('event_type', eventType)
    .eq('user_id', userId)
    .single();

  return !!data;
}
```

### Step 4: Add Test Script

Add to `package.json`:

```json
{
  "scripts": {
    "test:e2e:journey4": "playwright test journey-4-analytics-feedback"
  }
}
```

### Step 5: Update Documentation

Update `e2e/README.md`:

```markdown
### Individual Journeys
```bash
# Journey 4: Analytics & Feedback
npm run test:e2e:journey4
```

### Step 6: Run Your New Test

```bash
# Run in UI mode first
npm run test:e2e:ui

# Or run directly
npm run test:e2e:journey4

# Or with debug
npx playwright test journey-4-analytics-feedback --debug
```

## Checklist for New Journey

- [ ] Document journey in `USER_JOURNEYS.md`
- [ ] Create test file: `journey-N-name.spec.ts`
- [ ] Follow naming convention: `journey-[number]-[kebab-case-name].spec.ts`
- [ ] Use `test.step()` for each action
- [ ] Add DB verification after each frontend action
- [ ] Include setup in `test.beforeAll()`
- [ ] Include cleanup in `test.afterAll()`
- [ ] Add screenshots at key steps
- [ ] Add helper methods to `supabase-helper.ts` if needed
- [ ] Add npm script to `package.json`
- [ ] Update `e2e/README.md`
- [ ] Test in UI mode first
- [ ] Verify cleanup works (check database after test)

## Common Patterns

### Pattern 1: Wait for Async Operation
```typescript
// Frontend shows loading
await expect(page.getByText(/processing/i)).toBeVisible();

// Wait for DB operation to complete
const isComplete = await supabase.waitForOperation(id, 30000);
expect(isComplete).toBe(true);

// Frontend shows completion
await expect(page.getByText(/completed/i)).toBeVisible();
```

### Pattern 2: Form Submission + DB Verify
```typescript
// Fill and submit form
await page.getByLabel(/name/i).fill('Test Name');
await page.getByRole('button', { name: /submit/i }).click();

// Verify frontend feedback
await expect(page.getByText(/success/i)).toBeVisible();

// Verify database record
const { data } = await supabase.verifyRecord(id);
expect(data.name).toBe('Test Name');
```

### Pattern 3: List Operations
```typescript
// Frontend: Add items to list
for (const item of items) {
  await page.click('button[aria-label="Add"]');
  await page.fill('input', item.name);
  await page.click('button[type="submit"]');
}

// DB: Verify all items in database
const { data } = await supabase.getItems(parentId);
expect(data?.length).toBe(items.length);
```

### Pattern 4: Navigation Flow
```typescript
// Step 1: Start page
await page.goto('/start');
await test.step('Step 1: Start page', async () => {
  await expect(page.locator('h1')).toContainText('Start');
});

// Step 2: Navigate to next
await page.click('text=Next');
await test.step('Step 2: Next page', async () => {
  await expect(page.url()).toMatch(/next/);
});

// Step 3: Complete
await page.click('text=Finish');
await test.step('Step 3: Completion', async () => {
  await expect(page.getByText(/done/i)).toBeVisible();
});
```

## Tips

1. **Start Simple**: Copy an existing journey and modify it
2. **Run in UI Mode**: Use `npm run test:e2e:ui` to develop interactively
3. **Use Codegen**: Run `npm run test:e2e:codegen` to record interactions
4. **Debug with Screenshots**: Add screenshots liberally during development
5. **Test Cleanup**: Always verify cleanup works by checking database
6. **Flexible Selectors**: Use regex for text matching: `/sign up|create account/i`
7. **Wait Strategies**: Add explicit waits for async operations
8. **Isolation**: Each test should be independent and not rely on previous tests

## Resources

- Existing journeys in `e2e/journey-*.spec.ts`
- Supabase helper API in `e2e/utils/supabase-helper.ts`
- Test fixtures in `e2e/fixtures/`
- Full documentation in `e2e/README.md`

---

**Ready to create your own journey? Copy this example and customize!** 🚀
