# E2E Testing Quick Start Guide

Get started with E2E testing in 5 minutes!

## What You Get

- **User Journey Tests**: Tests that follow real user flows from signup to newsletter sending
- **Database Verification**: Every UI action is verified against Supabase database
- **Playwright + Supabase**: Frontend testing with backend database checks
- **3 Complete Journeys**:
  1. User onboarding (signup → create workspace)
  2. Content sources (add sources → scrape content)
  3. Newsletter generation (select content → generate → send)

## Quick Setup

### 1. Install Dependencies
```bash
cd frontend-nextjs
npm install
npx playwright install chromium
```

### 2. Configure Test Environment

Create `.env.test.local` in `frontend-nextjs/`:

```env
# Frontend & Backend
NEXT_PUBLIC_API_URL=http://localhost:3000
API_URL=http://localhost:8000

# Supabase TEST Project (create a separate test project!)
SUPABASE_URL=https://your-test-project.supabase.co
SUPABASE_ANON_KEY=your-test-anon-key
SUPABASE_SERVICE_KEY=your-test-service-key

# NextAuth
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=test-secret-for-e2e
```

**Important**: Use a separate Supabase project for testing, NOT your production database!

### 3. Start Servers

In one terminal:
```bash
# Start backend (from project root)
.venv\Scripts\python.exe -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

In another terminal:
```bash
# Start frontend
cd frontend-nextjs
npm run dev
```

### 4. Run Tests

```bash
# Run all E2E tests
npm run test:e2e

# Or run specific journey
npm run test:e2e:journey1  # User onboarding
npm run test:e2e:journey2  # Content sources
npm run test:e2e:journey3  # Newsletter generation

# Run with UI (recommended for first time)
npm run test:e2e:ui
```

## What Happens During Tests

### Journey 1: User Onboarding
```
1. User visits landing page
   ✓ Frontend: Page renders

2. User signs up
   ✓ Frontend: Form submission
   ✓ Database: User record created in `users` table

3. User auto-logs in
   ✓ Frontend: Redirects to dashboard
   ✓ Database: Session exists in auth

4. User creates workspace
   ✓ Frontend: Workspace form submission
   ✓ Database: Workspace record created with correct user_id
```

### Journey 2: Content Sources
```
1. User adds RSS feed
   ✓ Frontend: Source appears in list
   ✓ Database: content_sources record with type='rss'

2. User adds Reddit source
   ✓ Frontend: Source appears in list
   ✓ Database: content_sources record with type='reddit'

3. User triggers scraping
   ✓ Frontend: Loading state shown
   ✓ Database: scrape_jobs record created

4. Content is scraped
   ✓ Frontend: Content items displayed
   ✓ Database: content_items records created
```

### Journey 3: Newsletter Generation
```
1. User selects content items
   ✓ Frontend: Items checked

2. User configures newsletter
   ✓ Frontend: Form filled

3. User generates newsletter
   ✓ Frontend: Generation loading state
   ✓ Database: newsletters record with status='generating'

4. Newsletter completes
   ✓ Frontend: Preview shown
   ✓ Database: newsletter.status='completed', content_html populated

5. User sends newsletter
   ✓ Frontend: Send confirmation
   ✓ Database: newsletter.status='sent', email_delivery_log entries
```

## Test Structure

Each test file follows this pattern:

```typescript
test.describe('User Journey: [Name]', () => {
  // Setup test data
  test.beforeAll(async ({ supabase }) => {
    // Create test user, workspace, etc.
  });

  // Clean up after tests
  test.afterAll(async ({ supabase }) => {
    await supabase.cleanupTestUser(userId);
  });

  test('should complete full journey', async ({ page, supabase }) => {
    // Frontend action
    await page.click('button');
    await expect(page.getByText('Success')).toBeVisible();

    // Database verification
    const { data } = await supabase.verifyRecord(id);
    expect(data).toBeDefined();
  });
});
```

## Viewing Results

### HTML Report (Automatic)
After running tests:
```bash
npm run test:e2e:report
```

### Screenshots
Find screenshots of each test step in:
```
test-results/
├── journey1-step1-landing.png
├── journey1-step2-signup.png
├── journey2-step1-sources-page.png
└── ...
```

### Video Recordings
Videos are saved for failed tests in `test-results/`

## Common Commands

```bash
# Run all tests
npm run test:e2e

# Run with UI (interactive mode)
npm run test:e2e:ui

# Run in headed mode (see browser)
npm run test:e2e:headed

# Debug specific test
npm run test:e2e:debug

# Run specific journey
npm run test:e2e:journey1
npm run test:e2e:journey2
npm run test:e2e:journey3

# View test report
npm run test:e2e:report

# Generate test code (record interactions)
npm run test:e2e:codegen
```

## Troubleshooting

### Servers Not Starting
```bash
# Check if ports are available
netstat -ano | findstr :3000
netstat -ano | findstr :8000

# Kill processes if needed
taskkill /PID <PID> /F
```

### Supabase Connection Failed
- Verify `.env.test.local` has correct credentials
- Ensure using TEST project, not production
- Check service key has proper permissions

### Tests Timing Out
- Increase timeout in `playwright.config.ts`
- Ensure backend and frontend are running
- Check network connectivity

### Element Not Found
- Run in headed mode to see what's happening: `npm run test:e2e:headed`
- Use debug mode: `npm run test:e2e:debug`
- Check if your frontend UI differs from test expectations

## Next Steps

1. **Read Full Documentation**: See [e2e/README.md](./e2e/README.md)
2. **Review User Journeys**: See [e2e/USER_JOURNEYS.md](./e2e/USER_JOURNEYS.md)
3. **Explore Supabase Helper**: See [e2e/utils/supabase-helper.ts](./e2e/utils/supabase-helper.ts)
4. **Add More Journeys**: Follow existing patterns to add new tests

## Example: Running Your First Test

```bash
# 1. Ensure servers are running
# Terminal 1: backend on :8000
# Terminal 2: frontend on :3000

# 2. Run Journey 1 in UI mode (recommended first time)
npm run test:e2e:ui

# 3. Select "journey-1-user-onboarding.spec.ts"

# 4. Click "Run" and watch the test execute

# 5. See both frontend interactions and database verifications
```

## Key Files

```
frontend-nextjs/
├── e2e/
│   ├── journey-1-user-onboarding.spec.ts     # Test: Signup → Workspace
│   ├── journey-2-content-sources.spec.ts     # Test: Sources → Scraping
│   ├── journey-3-newsletter-generation.spec.ts # Test: Generate → Send
│   ├── fixtures/
│   │   ├── playwright-fixtures.ts            # Custom fixtures
│   │   └── test-data.ts                      # Test data
│   ├── utils/
│   │   └── supabase-helper.ts                # Database verification
│   ├── USER_JOURNEYS.md                      # Journey documentation
│   └── README.md                             # Full documentation
├── playwright.config.ts                       # Playwright config
├── .env.test.local                           # Test environment (create this)
└── package.json                              # Test scripts
```

## Support

- **Playwright Docs**: https://playwright.dev
- **Supabase Docs**: https://supabase.com/docs
- **Issues**: Check test output and screenshots first
- **Debug**: Use `npm run test:e2e:debug` to step through tests

---

**You're ready to go! Run `npm run test:e2e:ui` to start testing.** 🎭✨
