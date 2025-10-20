# When Playwright Tests Fail - Complete Troubleshooting Guide

**Common failure scenarios and how to fix them**

---

## 🚨 Common Failure Scenarios

### 1. Element Not Found Errors

**Error Message:**
```
Error: Element not found with options: { role: 'button', name: /submit/i }
Timeout 10000ms exceeded
```

**When This Happens:**
- Element doesn't exist on the page
- Element is hidden or not visible
- Element is still loading
- Selector is incorrect
- Page structure changed

**How to Fix:**

```typescript
// ❌ Problem: Element not found immediately
await clickElement(page, { role: 'button', name: /submit/i });

// ✅ Solution 1: Wait for element first
await waitForElement(page, { role: 'button', name: /submit/i });
await clickElement(page, { role: 'button', name: /submit/i });

// ✅ Solution 2: Increase timeout
await clickElement(page, { role: 'button', name: /submit/i }, 'Submit', { timeout: 20000 });

// ✅ Solution 3: Use multiple selector strategies
await clickElement(page, {
  role: 'button',
  name: /submit|save|create/i,
  text: /submit|save|create/i,
  testId: 'submit-btn',
  css: 'button[type="submit"]'
});

// ✅ Solution 4: Wait for page to load
await waitForNetworkIdle(page);
await clickElement(page, { role: 'button', name: /submit/i });
```

**Debug Steps:**
```typescript
// Take screenshot to see what's on page
await takeScreenshot(page, 'before-click');

// Log all buttons on page
const buttons = await page.locator('button').allTextContents();
console.log('Available buttons:', buttons);

// Check if element exists but is hidden
const isHidden = await page.locator('button').first().isHidden();
console.log('Is hidden:', isHidden);
```

---

### 2. Timeout Errors

**Error Message:**
```
Error: Test timeout of 30000ms exceeded
```

**When This Happens:**
- Test takes longer than configured timeout
- Waiting for element that never appears
- Network request hanging
- Infinite loading state
- Backend not responding

**How to Fix:**

```typescript
// ✅ Solution 1: Increase test timeout
test('slow test', async ({ page }) => {
  test.setTimeout(60000);  // 60 seconds
  // ... test steps
});

// ✅ Solution 2: Increase specific action timeout
await waitForElement(page, { text: /success/i }, 'Success', 60000);

// ✅ Solution 3: Check for loading states
await waitForLoadingToComplete(page, '.spinner', 30000);

// ✅ Solution 4: Add timeout to navigation
await page.goto('/slow-page', { timeout: 60000 });

// ✅ Solution 5: Use retry with timeout
await withTimeout(
  async () => await myAction(),
  45000,
  'Action timed out after 45 seconds'
);
```

**Debug Steps:**
```typescript
// Check network activity
await page.waitForLoadState('networkidle', { timeout: 30000 });

// Check if loading indicator is stuck
const isLoading = await page.locator('.loading').isVisible();
console.log('Still loading:', isLoading);

// Monitor console errors
page.on('console', msg => console.log('PAGE LOG:', msg.text()));
```

---

### 3. Navigation Failures

**Error Message:**
```
Error: page.waitForURL: Expected URL pattern /dashboard/i, but got /login
```

**When This Happens:**
- Redirected to different page (e.g., login)
- Authentication failed
- Authorization denied
- URL doesn't match expected pattern
- Page crashed or error occurred

**How to Fix:**

```typescript
// ❌ Problem: Expected redirect didn't happen
await clickElement(page, submitButton);
await waitForUrl(page, /dashboard/i);

// ✅ Solution 1: Check current URL first
await clickElement(page, submitButton);
await page.waitForTimeout(1000);
console.log('Current URL:', page.url());
// Then decide what to verify

// ✅ Solution 2: Handle conditional navigation
await clickElement(page, submitButton);
await page.waitForTimeout(2000);

if (page.url().includes('login')) {
  console.log('Redirected to login - authentication failed');
  // Handle login
} else if (page.url().includes('dashboard')) {
  console.log('Successfully navigated to dashboard');
}

// ✅ Solution 3: Use flexible URL matching
await waitForUrl(page, /dashboard|app|home/i);

// ✅ Solution 4: Check for error messages first
const hasError = await page.getByText(/error|failed/i).isVisible().catch(() => false);
if (hasError) {
  const errorText = await page.getByText(/error|failed/i).textContent();
  throw new Error(`Navigation failed: ${errorText}`);
}
```

**Debug Steps:**
```typescript
// Log navigation events
page.on('framenavigated', frame => {
  console.log('Navigated to:', frame.url());
});

// Take screenshot before and after
await takeScreenshot(page, 'before-navigation');
await clickElement(page, submitButton);
await page.waitForTimeout(2000);
await takeScreenshot(page, 'after-navigation');
```

---

### 4. Form Validation Errors

**Error Message:**
```
Error: Expected to navigate to /success, but stayed on /form
```

**When This Happens:**
- Form validation preventing submission
- Required fields not filled
- Invalid data format
- JavaScript validation errors
- Backend validation errors

**How to Fix:**

```typescript
// ❌ Problem: Form doesn't submit
await fillField(page, { label: /email/i }, 'invalid-email');
await clickElement(page, { role: 'button', name: /submit/i });
await waitForUrl(page, /success/i);  // Fails - still on form page

// ✅ Solution 1: Check for validation errors
await fillField(page, { label: /email/i }, 'invalid-email');
await clickElement(page, { role: 'button', name: /submit/i });

// Check if error message appears
const hasError = await page.getByText(/invalid|error|required/i).isVisible().catch(() => false);
if (hasError) {
  console.log('Validation error detected - fixing data');
  await fillField(page, { label: /email/i }, 'valid@example.com');
  await clickElement(page, { role: 'button', name: /submit/i });
}

// ✅ Solution 2: Verify form filled correctly
await fillField(page, { label: /email/i }, testData.email);
// Verify it was actually filled
await expect(page.getByLabel(/email/i)).toHaveValue(testData.email);

// ✅ Solution 3: Wait for validation to complete
await fillField(page, { label: /email/i }, testData.email);
await page.waitForTimeout(500);  // Let validation run
await clickElement(page, { role: 'button', name: /submit/i });

// ✅ Solution 4: Use valid test data
const testData = generateTestData();  // Generates valid email format
await fillField(page, { label: /email/i }, testData.email);
```

**Debug Steps:**
```typescript
// Check form state
const formHTML = await page.locator('form').innerHTML();
console.log('Form HTML:', formHTML);

// Check for disabled submit button
const isDisabled = await page.getByRole('button', { name: /submit/i }).isDisabled();
console.log('Submit button disabled:', isDisabled);

// Look for validation messages
const validationMessages = await page.locator('[role="alert"], .error').allTextContents();
console.log('Validation messages:', validationMessages);
```

---

### 5. Flaky Tests (Intermittent Failures)

**Error Message:**
```
Sometimes passes, sometimes fails with various errors
```

**When This Happens:**
- Race conditions (test runs faster than page loads)
- Network timing issues
- Animation/transition delays
- Async operations completing at different speeds
- State pollution from previous tests

**How to Fix:**

```typescript
// ❌ Problem: Flaky test
test('flaky test', async ({ page }) => {
  await page.goto('/dashboard');
  await page.click('button');  // Sometimes fails
  await expect(page.getByText('Success')).toBeVisible();
});

// ✅ Solution 1: Add proper waits
test('stable test', async ({ page }) => {
  await page.goto('/dashboard');
  await waitForNetworkIdle(page);
  await waitForLoadingToComplete(page);

  const button = page.locator('button');
  await button.waitFor({ state: 'visible' });
  await button.click();

  await expect(page.getByText('Success')).toBeVisible({ timeout: 10000 });
});

// ✅ Solution 2: Use retry logic
test('test with retry', async ({ page }) => {
  await page.goto('/dashboard');

  await retry(async () => {
    await clickElement(page, { role: 'button', name: /submit/i });
  }, { maxRetries: 3, initialDelay: 1000 });
});

// ✅ Solution 3: Isolate tests
test.beforeEach(async ({ page }) => {
  // Clear state before each test
  await clearStorage(page);
  await page.goto('/');
});

test.afterEach(async ({ page }) => {
  // Cleanup after each test
  await clearStorage(page);
});

// ✅ Solution 4: Wait for element to be stable
test('wait for stability', async ({ page }) => {
  await page.goto('/dashboard');

  const button = page.locator('button');
  await button.waitFor({ state: 'visible' });
  await page.waitForTimeout(500);  // Let animations complete
  await button.click();
});
```

**Debug Steps:**
```typescript
// Run test multiple times to identify flakiness
// In playwright.config.ts:
export default defineConfig({
  retries: 2,  // Retry failed tests
});

// Add detailed logging
test('debug flaky test', async ({ page }) => {
  page.on('console', msg => console.log('CONSOLE:', msg.text()));
  page.on('pageerror', error => console.log('ERROR:', error));

  // Log each step
  log('Step 1: Navigate');
  await page.goto('/dashboard');

  log('Step 2: Wait for load');
  await waitForNetworkIdle(page);

  log('Step 3: Click button');
  await clickElement(page, { role: 'button' });
});
```

---

### 6. Backend/API Failures

**Error Message:**
```
Error: Request failed with status 500
Error: Network request failed
```

**When This Happens:**
- Backend server not running
- API endpoint doesn't exist
- Authentication token expired
- Database connection failed
- API rate limiting

**How to Fix:**

```typescript
// ✅ Solution 1: Check backend is running
test.beforeAll(async () => {
  // Ping backend health endpoint
  const response = await fetch('http://localhost:8000/health');
  if (!response.ok) {
    throw new Error('Backend server not running! Start it first.');
  }
});

// ✅ Solution 2: Handle API errors gracefully
test('with API error handling', async ({ page }) => {
  page.on('response', response => {
    if (response.status() >= 400) {
      console.log(`API Error: ${response.status()} ${response.url()}`);
    }
  });

  await page.goto('/dashboard');

  // Check for error messages on page
  const hasError = await page.getByText(/error|failed|unavailable/i).isVisible().catch(() => false);
  if (hasError) {
    throw new Error('Backend API error detected');
  }
});

// ✅ Solution 3: Wait for API calls to complete
test('wait for API', async ({ page }) => {
  await page.goto('/dashboard');

  // Wait for specific API call
  await page.waitForResponse(
    response => response.url().includes('/api/data') && response.status() === 200,
    { timeout: 30000 }
  );

  // Now proceed with test
  await verifyText(page, /data loaded/i);
});

// ✅ Solution 4: Mock API if backend unavailable
test('with API mocking', async ({ page }) => {
  // Intercept API calls
  await page.route('**/api/data', route => {
    route.fulfill({
      status: 200,
      body: JSON.stringify({ items: [] })
    });
  });

  await page.goto('/dashboard');
});
```

---

### 7. Authentication/Authorization Failures

**Error Message:**
```
Error: Redirected to /login instead of /dashboard
Error: 401 Unauthorized
```

**When This Happens:**
- User not logged in
- Session expired
- Auth token invalid
- Cookies not set
- CORS issues

**How to Fix:**

```typescript
// ✅ Solution 1: Login before each test
test.beforeEach(async ({ page }) => {
  // Login
  await page.goto('/login');
  await fillField(page, { label: /email/i }, 'test@example.com');
  await fillField(page, { label: /password/i }, 'password');
  await clickElement(page, { role: 'button', name: /sign in/i });
  await waitForUrl(page, /dashboard/i);
});

// ✅ Solution 2: Set auth token directly
test.beforeEach(async ({ page }) => {
  await page.goto('/');
  await setAuthToken(page, 'your-auth-token', 'authToken');
  await page.reload();
});

// ✅ Solution 3: Use persistent authentication
test.use({
  storageState: 'auth.json'  // Reuse auth across tests
});

// ✅ Solution 4: Handle session expiry
test('handle expired session', async ({ page }) => {
  await page.goto('/dashboard');

  // Check if redirected to login
  await page.waitForTimeout(1000);
  if (page.url().includes('/login')) {
    // Re-login
    await fillField(page, { label: /email/i }, 'test@example.com');
    await fillField(page, { label: /password/i }, 'password');
    await clickElement(page, { role: 'button', name: /sign in/i });
    await waitForUrl(page, /dashboard/i);
  }
});
```

---

### 8. Selector Changes (Page Structure Changed)

**Error Message:**
```
Error: Element with role 'button' and name /submit/i not found
```

**When This Happens:**
- UI was refactored
- Button text changed
- Element role changed
- CSS classes changed
- Component library updated

**How to Fix:**

```typescript
// ❌ Problem: Brittle selector
await clickElement(page, { css: '.btn-primary-submit' });

// ✅ Solution 1: Use flexible selectors with fallbacks
await clickElement(page, {
  role: 'button',
  name: /submit|save|create|continue/i,  // Multiple possible texts
  text: /submit|save|create|continue/i,
  testId: 'submit-btn',
  css: 'button[type="submit"]'
});

// ✅ Solution 2: Update Page Object once
class MyPage extends BasePage {
  get submitButton() {
    // Update selector in one place
    return this.page.getByRole('button', { name: /new text/i });
  }
}

// ✅ Solution 3: Use data-testid attributes
// In your component:
// <button data-testid="submit-btn">Submit</button>

await clickElement(page, { testId: 'submit-btn' });

// ✅ Solution 4: Debug what's actually on page
const buttons = await page.locator('button').allTextContents();
console.log('Available buttons:', buttons);
// Then update selector based on what you find
```

---

### 9. Environment-Specific Failures

**Error Message:**
```
Works locally, fails in CI/CD
Works on Mac, fails on Windows
```

**When This Happens:**
- Different base URLs
- Environment variables not set
- File path differences (Windows vs Unix)
- Timezone differences
- Different browser versions

**How to Fix:**

```typescript
// ✅ Solution 1: Use environment-specific config
// playwright.config.ts
export default defineConfig({
  use: {
    baseURL: process.env.BASE_URL || 'http://localhost:3000',
  },
});

// ✅ Solution 2: Check environment before running
test.beforeAll(async () => {
  if (!process.env.API_URL) {
    throw new Error('API_URL environment variable not set!');
  }
});

// ✅ Solution 3: Use cross-platform paths
import path from 'path';

const filePath = path.join(__dirname, 'test-data', 'file.txt');
// Instead of: './test-data/file.txt' (Unix) or '.\\test-data\\file.txt' (Windows)

// ✅ Solution 4: Set timeout for CI
// In CI, tests may run slower
export default defineConfig({
  timeout: process.env.CI ? 60000 : 30000,
});
```

---

### 10. Memory/Performance Issues

**Error Message:**
```
Error: Out of memory
Test suite took too long to complete
```

**When This Happens:**
- Too many parallel tests
- Memory leaks in tests
- Large screenshots/videos
- Browser contexts not cleaned up

**How to Fix:**

```typescript
// ✅ Solution 1: Limit parallel tests
// playwright.config.ts
export default defineConfig({
  workers: process.env.CI ? 1 : 2,  // Fewer workers in CI
});

// ✅ Solution 2: Clean up after each test
test.afterEach(async ({ page }) => {
  await clearStorage(page);
  await page.close();
});

// ✅ Solution 3: Disable unnecessary features
export default defineConfig({
  use: {
    video: 'retain-on-failure',  // Only record failed tests
    screenshot: 'only-on-failure',
  },
});

// ✅ Solution 4: Increase timeout for large test suites
export default defineConfig({
  timeout: 60000,
  globalTimeout: 600000,  // 10 minutes for entire suite
});
```

---

## 🔍 Debug Toolkit

### Essential Debug Commands

```bash
# Run in UI mode (best for debugging)
npm run test:e2e:ui

# Run in debug mode (step through test)
npm run test:e2e:debug

# Run headed (see browser)
npm run test:e2e:headed

# Run specific test
npx playwright test my-test.spec.ts -g "test name"

# Update snapshots
npx playwright test --update-snapshots

# Show trace
npx playwright show-trace trace.zip
```

### Debug Code Patterns

```typescript
// 1. Add detailed logging
test('debug test', async ({ page }) => {
  log('Step 1: Navigate');
  await page.goto('/dashboard');

  log('Step 2: Take screenshot');
  await takeScreenshot(page, 'dashboard');

  log('Current URL: ' + page.url());

  log('Step 3: Find button');
  const buttons = await page.locator('button').allTextContents();
  log('Available buttons: ' + JSON.stringify(buttons));
});

// 2. Pause execution
test('pause test', async ({ page }) => {
  await page.goto('/dashboard');
  await page.pause();  // Opens Playwright Inspector
  // Test pauses here - you can inspect page
});

// 3. Console logging
test('console logging', async ({ page }) => {
  page.on('console', msg => console.log('PAGE:', msg.text()));
  page.on('pageerror', err => console.log('ERROR:', err));

  await page.goto('/dashboard');
});

// 4. Network monitoring
test('network monitoring', async ({ page }) => {
  page.on('request', request => {
    console.log('Request:', request.url());
  });

  page.on('response', response => {
    console.log('Response:', response.status(), response.url());
  });

  await page.goto('/dashboard');
});

// 5. Screenshot everything
test('screenshot debugging', async ({ page }) => {
  await takeScreenshot(page, '1-start');
  await page.goto('/dashboard');
  await takeScreenshot(page, '2-after-nav');
  await clickElement(page, button);
  await takeScreenshot(page, '3-after-click');
});
```

---

## 📋 Failure Prevention Checklist

### Before Writing Tests

- [ ] Backend server is running
- [ ] Frontend dev server is running
- [ ] Environment variables are set
- [ ] Test database is configured
- [ ] Authentication is working

### When Writing Tests

- [ ] Use flexible selectors (role → text → testId → CSS)
- [ ] Add proper waits (elements, navigation, loading)
- [ ] Generate unique test data
- [ ] Handle async operations
- [ ] Add error handling
- [ ] Take screenshots at key steps
- [ ] Clean up after tests

### When Tests Fail

- [ ] Run in debug mode first
- [ ] Check screenshot to see page state
- [ ] Verify selectors match page structure
- [ ] Check console for errors
- [ ] Verify backend is responding
- [ ] Check network tab for failed requests
- [ ] Try with increased timeout
- [ ] Isolate the failing step

---

## 🎯 Quick Fix Reference

| Error | Quick Fix |
|-------|-----------|
| Element not found | Add `waitForElement()` |
| Timeout | Increase timeout or add wait |
| Navigation failed | Check for redirects/errors |
| Form not submitting | Check validation errors |
| Flaky test | Add proper waits, use retry |
| API error | Verify backend is running |
| Auth failed | Login before test |
| Selector changed | Update to flexible selector |
| CI failure | Check environment vars |
| Performance | Reduce parallel workers |

---

## 💡 Pro Tips

1. **Always run in UI mode first when debugging**
   ```bash
   npm run test:e2e:ui
   ```

2. **Use `page.pause()` to inspect at any point**
   ```typescript
   await page.pause();
   ```

3. **Check screenshots before investigating code**
   - They show exactly what Playwright saw

4. **Use flexible regex selectors**
   ```typescript
   { name: /submit|save|create/i }
   ```

5. **Add retry logic for flaky operations**
   ```typescript
   await retry(() => myAction(), { maxRetries: 3 });
   ```

6. **Enable trace on failure**
   ```typescript
   // playwright.config.ts
   use: {
     trace: 'on-first-retry',
   }
   ```

---

**Remember:** Most test failures are due to timing issues. Add proper waits and your tests will be much more stable! ✨
