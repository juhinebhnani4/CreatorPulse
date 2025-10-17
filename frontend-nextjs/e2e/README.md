# CreatorPulse E2E Testing Guide

## Overview

This directory contains end-to-end (E2E) tests for CreatorPulse that test complete user journeys from frontend interactions to database verification. Each test follows a real user flow and verifies both the UI state and the corresponding database changes.

## Architecture

```
e2e/
├── fixtures/
│   ├── playwright-fixtures.ts    # Custom Playwright test fixtures
│   └── test-data.ts               # Test data and helper functions
├── utils/
│   └── supabase-helper.ts         # Supabase database verification utilities
├── journey-1-user-onboarding.spec.ts
├── journey-2-content-sources.spec.ts
├── journey-3-newsletter-generation.spec.ts
├── USER_JOURNEYS.md               # Complete user journey documentation
└── README.md                      # This file
```

## Key Features

### 1. **User Journey-Based Testing**
Tests follow actual user workflows from start to finish:
- Journey 1: New user signup → Create workspace
- Journey 2: Add content sources → Scrape content
- Journey 3: Generate newsletter → Send to subscribers
- Journey 4: View analytics → Provide feedback (to be added)

### 2. **Linked Frontend + Database Verification**
Every user action is verified in both layers:
```typescript
// Example: User creates workspace
await page.getByRole('button', { name: /create workspace/i }).click();

// ✓ Frontend: Verify UI updates
await expect(page.getByText('Workspace created')).toBeVisible();

// ✓ Database: Verify record exists
const { data } = await supabase.verifyWorkspace(workspaceId, userId);
expect(data.user_id).toBe(userId);
```

### 3. **Supabase Integration**
Uses Supabase MCP and client library to:
- Verify database state after each action
- Check relationships and foreign keys
- Validate timestamps and data integrity
- Clean up test data after tests

## Setup

### Prerequisites

1. **Supabase Test Project**
   - Create a separate Supabase project for testing (DO NOT use production!)
   - Run all database migrations on test project
   - Get test project credentials

2. **Environment Variables**
   - Copy `.env.test.local.example` to `.env.test.local`
   - Fill in Supabase test project credentials
   - Set backend API URL

3. **Install Dependencies**
   ```bash
   npm install
   ```

4. **Install Playwright Browsers**
   ```bash
   npx playwright install
   ```

### Configuration

Edit `.env.test.local`:

```env
# Frontend
NEXT_PUBLIC_API_URL=http://localhost:3000

# Backend API
API_URL=http://localhost:8000

# Supabase TEST Project (not production!)
SUPABASE_URL=https://your-test-project.supabase.co
SUPABASE_ANON_KEY=your-test-anon-key
SUPABASE_SERVICE_KEY=your-test-service-key

# Test Configuration
TEST_TIMEOUT=60000
TEST_HEADLESS=true
```

## Running Tests

### All Tests
```bash
npm run test:e2e
```

### Individual Journeys
```bash
# Journey 1: User Onboarding
npm run test:e2e:journey1

# Journey 2: Content Sources
npm run test:e2e:journey2

# Journey 3: Newsletter Generation
npm run test:e2e:journey3
```

### Interactive Mode
```bash
# Run with Playwright UI
npm run test:e2e:ui

# Run in headed mode (see browser)
npm run test:e2e:headed

# Debug mode (step through)
npm run test:e2e:debug
```

### View Test Report
```bash
npm run test:e2e:report
```

## Test Structure

### Anatomy of a Test Journey

```typescript
test.describe('User Journey: [Name]', () => {
  // Setup: Create test data
  test.beforeAll(async ({ supabase }) => {
    // Initialize test user, workspace, etc.
  });

  // Cleanup: Remove test data
  test.afterAll(async ({ supabase }) => {
    await supabase.cleanupTestUser(userId);
  });

  test('should complete full journey', async ({ page, supabase }) => {
    // ==================== STEP 1: [Action] ====================
    await test.step('Step 1: User does something', async () => {
      await page.click('button');
      await expect(page.getByText('Success')).toBeVisible();
    });

    // ==================== DB VERIFICATION ====================
    await test.step('DB Check: Verify database state', async () => {
      const { data } = await supabase.verifyRecord(id);
      expect(data).toBeDefined();
    });

    // ... more steps ...
  });
});
```

### Key Patterns

#### 1. **Frontend Interaction**
```typescript
// Click buttons with flexible selectors
await page.getByRole('button', { name: /create|add|save/i }).click();

// Fill forms
await page.getByLabel(/email/i).fill('test@example.com');

// Wait for navigation
await page.waitForURL(/dashboard/);

// Verify UI elements
await expect(page.getByText('Success')).toBeVisible();
```

#### 2. **Database Verification**
```typescript
// Verify record exists
const { exists } = await supabase.verifyWorkspace(workspaceId, userId);
expect(exists).toBe(true);

// Check relationships
const { data } = await supabase.getWorkspaceSources(workspaceId);
expect(data?.length).toBe(3);

// Validate timestamps
const isRecent = await supabase.verifyRecentWorkspaceCreation(workspaceId);
expect(isRecent).toBe(true);
```

#### 3. **Waiting for Async Operations**
```typescript
// Wait for scrape job to complete
const isComplete = await supabase.waitForScrapeJobCompletion(jobId, 30000);
expect(isComplete).toBe(true);

// Wait for newsletter generation
const isGenerated = await supabase.waitForNewsletterGeneration(newsletterId);
expect(isGenerated).toBe(true);
```

## Supabase Helper Methods

### User Verification
- `verifyUserExists(email)` - Check if user exists
- `verifyUserSession(userId)` - Check active session
- `getUserByEmail(email)` - Get user record

### Workspace Verification
- `verifyWorkspace(workspaceId, userId)` - Check workspace ownership
- `getUserWorkspaces(userId)` - Get all user workspaces
- `verifyRecentWorkspaceCreation(workspaceId)` - Check timestamp

### Content Source Verification
- `verifyContentSource(sourceId, workspaceId)` - Check source exists
- `getWorkspaceSources(workspaceId)` - Get all sources
- `verifySourceType(sourceId, expectedType)` - Check source type

### Content Items Verification
- `verifyContentItem(contentId)` - Check item exists
- `getWorkspaceContent(workspaceId)` - Get all content
- `getContentBySource(sourceId)` - Get content by source
- `verifyContentItemFields(contentId)` - Check required fields

### Newsletter Verification
- `verifyNewsletter(newsletterId, workspaceId)` - Check newsletter exists
- `verifyNewsletterStatus(newsletterId, status)` - Check status
- `verifyNewsletterContent(newsletterId)` - Check has HTML content
- `waitForNewsletterGeneration(newsletterId)` - Wait for completion

### Analytics Verification
- `getNewsletterAnalytics(newsletterId)` - Get all events
- `countEventsByType(newsletterId, eventType)` - Count specific events
- `verifyAnalyticsEvent(eventType, metadata)` - Check event exists

### Cleanup
- `cleanupTestUser(userId)` - Delete user and related data
- `cleanupTestWorkspace(workspaceId)` - Delete workspace and related data
- `cleanupTestDataAfter(timestamp)` - Delete all data after timestamp

## Best Practices

### 1. **Test Isolation**
- Each test should be independent
- Use unique test data (timestamps in emails/names)
- Clean up after each test

### 2. **Realistic User Flows**
- Follow actual user journeys
- Don't skip steps
- Include error cases

### 3. **Wait Strategies**
- Use Playwright's auto-waiting when possible
- Add explicit waits for async operations
- Poll database for completion of long-running tasks

### 4. **Selectors**
- Prefer semantic selectors (`getByRole`, `getByLabel`)
- Use regex for flexible matching: `/sign up|create account/i`
- Add `data-testid` to frontend components for stability

### 5. **Screenshots**
- Capture screenshots at key steps
- Use descriptive filenames
- Store in `test-results/` directory

### 6. **Database Safety**
- Always use test database, never production
- Use service key for verification (bypasses RLS)
- Clean up test data after runs

## Debugging

### View Test in Browser
```bash
npm run test:e2e:headed
```

### Debug Specific Test
```bash
npx playwright test journey-1-user-onboarding --debug
```

### Generate Test Code
Use Playwright's codegen to record interactions:
```bash
npm run test:e2e:codegen
```

### View Trace
If test fails, view trace file:
```bash
npx playwright show-trace trace.zip
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: E2E Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - run: npm ci
      - run: npx playwright install --with-deps
      - run: npm run test:e2e
        env:
          SUPABASE_URL: ${{ secrets.SUPABASE_TEST_URL }}
          SUPABASE_ANON_KEY: ${{ secrets.SUPABASE_TEST_ANON_KEY }}
          SUPABASE_SERVICE_KEY: ${{ secrets.SUPABASE_TEST_SERVICE_KEY }}
      - uses: actions/upload-artifact@v3
        if: always()
        with:
          name: playwright-report
          path: playwright-report/
```

## Troubleshooting

### Tests Timing Out
- Increase timeout in `playwright.config.ts`
- Check if backend/frontend servers started
- Verify database connection

### Database Verification Failing
- Ensure using test database credentials
- Check RLS policies allow service key access
- Verify migrations ran on test database

### Element Not Found
- Add explicit waits: `await wait(1000)`
- Use more flexible selectors with regex
- Check if element is in iframe or shadow DOM

## Contributing

When adding new tests:

1. **Document the user journey** in `USER_JOURNEYS.md`
2. **Create test file** following naming convention: `journey-N-name.spec.ts`
3. **Add test script** to `package.json`
4. **Update this README** with new journey description
5. **Add cleanup logic** in `afterAll` hook

## Resources

- [Playwright Documentation](https://playwright.dev)
- [Supabase Client Library](https://supabase.com/docs/reference/javascript/introduction)
- [User Journeys Documentation](./USER_JOURNEYS.md)
- [Test Data Fixtures](./fixtures/test-data.ts)
- [Supabase Helper API](./utils/supabase-helper.ts)

---

**Happy Testing! 🎭**
