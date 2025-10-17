# Universal Playwright Test Template Guide

**Complete guide to creating user journey tests for ANY page using the universal templates**

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Template Overview](#template-overview)
3. [Three Approaches to Testing](#three-approaches-to-testing)
4. [Detailed Examples](#detailed-examples)
5. [Best Practices](#best-practices)
6. [Troubleshooting](#troubleshooting)
7. [FAQ](#faq)

---

## Quick Start

### 5-Minute Test Creation

**Step 1: Copy the template**
```bash
cd frontend-nextjs/e2e
cp templates/universal-journey-template.spec.ts journey-my-feature.spec.ts
```

**Step 2: Update the configuration**
```typescript
const JOURNEY_CONFIG = {
  name: 'My Feature Journey',
  description: 'Testing my new feature',
  screenshotPrefix: 'my-feature',
  // ... rest stays the same
};
```

**Step 3: Write your test using helper functions**
```typescript
test('should complete my journey', async ({ page }) => {
  await navigateToPage(page, '/my-page', { heading: /My Page/i });
  await clickElement(page, { role: 'button', name: /Submit/i }, 'Submit button');
  await verifyText(page, /Success/i);
});
```

**Step 4: Run it**
```bash
npm run test:e2e journey-my-feature
```

**Done!** ✅

---

## Template Overview

### Available Templates

We provide **4 comprehensive templates** that work together:

| Template | Purpose | Best For |
|----------|---------|----------|
| **`universal-journey-template.spec.ts`** | Main test template with helper functions | Quick test creation, flexible testing |
| **`page-object-template.ts`** | Page Object Model (POM) pattern | Maintainable tests, reusable components |
| **`test-helpers.ts`** | Utility functions library | All tests (import helpers as needed) |
| **`journey-config-template.ts`** | JSON-driven test approach | Non-developers, standardized tests |

### Key Features

All templates provide:

✅ **Page-agnostic** - Works with ANY page, even ones that don't exist yet
✅ **Flexible selectors** - Multiple fallback strategies (role → text → label → CSS)
✅ **Smart waiting** - Auto-waits for elements, navigation, async operations
✅ **Auto-screenshots** - Captures screenshots at each step
✅ **Error recovery** - Built-in retry logic and error handling
✅ **Clear logging** - Step-by-step console output for debugging
✅ **Backend support** - Optional API/database verification

---

## Three Approaches to Testing

Choose the approach that fits your needs:

### Approach A: Functional with Helpers (Quickest)

**Best for:** Quick test creation, one-off tests, simple journeys

**File:** `universal-journey-template.spec.ts`

**Example:**
```typescript
import { navigateToPage, clickElement, fillField, verifyText } from './helpers';

test('should complete signup', async ({ page }) => {
  await navigateToPage(page, '/register', { heading: /Sign Up/i });

  await fillField(page, { label: /email/i }, 'test@example.com');
  await fillField(page, { label: /password/i }, 'SecurePass123!');

  await clickElement(page, { role: 'button', name: /Create Account/i });

  await verifyText(page, /Welcome/i);
});
```

**Pros:**
- ✅ Fastest to write
- ✅ No setup required
- ✅ Easy to understand

**Cons:**
- ❌ Less maintainable for complex tests
- ❌ Duplicated code across tests

---

### Approach B: Page Object Model (Most Maintainable)

**Best for:** Complex applications, multiple tests, team projects

**File:** `page-object-template.ts`

**Example:**
```typescript
// 1. Create page objects
class SignupPage extends BasePage {
  get emailInput() { return this.page.getByLabel(/email/i); }
  get passwordInput() { return this.page.getByLabel(/password/i); }
  get submitButton() { return this.page.getByRole('button', { name: /create/i }); }

  async signup(email: string, password: string) {
    await this.emailInput.fill(email);
    await this.passwordInput.fill(password);
    await this.submitButton.click();
  }
}

// 2. Use in tests
test('should complete signup', async ({ page }) => {
  const signupPage = new SignupPage(page);

  await signupPage.goto('/register');
  await signupPage.signup('test@example.com', 'SecurePass123!');

  await expect(page.getByText(/Welcome/i)).toBeVisible();
});
```

**Pros:**
- ✅ Highly maintainable
- ✅ Reusable across tests
- ✅ Encapsulates page logic
- ✅ Easy to update when UI changes

**Cons:**
- ❌ More upfront setup
- ❌ Requires understanding of OOP

---

### Approach C: Config-Driven (No Coding Required!)

**Best for:** Non-developers, standardized tests, data-driven testing

**File:** `journey-config-template.ts`

**Example:**
```typescript
// 1. Define journey in JSON
const signupJourney = {
  name: 'User Signup',
  description: 'Tests new user registration',
  steps: [
    {
      name: 'Navigate to signup',
      action: 'navigate',
      url: '/register'
    },
    {
      name: 'Fill email',
      action: 'fill',
      selector: { label: /email/i },
      value: 'test@example.com'
    },
    {
      name: 'Fill password',
      action: 'fill',
      selector: { label: /password/i },
      value: 'SecurePass123!'
    },
    {
      name: 'Click submit',
      action: 'click',
      selector: { role: 'button', name: /create/i }
    },
    {
      name: 'Verify success',
      action: 'verify_text',
      value: /Welcome/i
    }
  ]
};

// 2. Create test from config
createTestFromConfig(signupJourney);
```

**Pros:**
- ✅ No coding required
- ✅ Can be written by QA/PMs
- ✅ Standardized format
- ✅ Can load from JSON files

**Cons:**
- ❌ Less flexible for complex scenarios
- ❌ Limited to predefined actions

---

## Detailed Examples

### Example 1: Testing a New Page (Unknown Elements)

**Scenario:** You have a brand new page and don't know the exact selectors.

```typescript
test('should work with unknown page', async ({ page }) => {
  // Navigate using flexible verification
  await navigateToPage(
    page,
    '/new-feature',
    {
      // Try multiple possible headings
      heading: /feature|new|welcome/i
    }
  );

  // Click using flexible selector (tries multiple strategies)
  await clickElement(
    page,
    {
      role: 'button',           // First try: accessible role
      name: /continue|next/i,   // With flexible name matching
      text: /continue|next/i,   // Fallback: text content
      testId: 'continue-btn',   // Fallback: test ID
      css: '.continue-button'   // Fallback: CSS selector
    },
    'Continue button'
  );

  // Verify flexible success message
  await verifyText(page, /success|complete|done/i);
});
```

**This test will work even if:**
- The exact heading text changes
- The button text is "Continue", "Next", or "Proceed"
- The page structure is still being developed

---

### Example 2: Multi-Step Form with Dynamic Data

```typescript
test('should complete multi-step form', async ({ page }) => {
  // Generate unique test data
  const testData = generateTestData('form-test');

  // STEP 1: Personal Info
  await navigateToPage(page, '/signup', { heading: /sign up/i });

  await fillField(page, { label: /first name/i }, testData.firstName);
  await fillField(page, { label: /last name/i }, testData.lastName);
  await fillField(page, { label: /email/i }, testData.email);

  await clickElement(page, { role: 'button', name: /next|continue/i });

  // STEP 2: Account Setup
  await waitForNavigation(page, /account|step-2/i);

  await fillField(page, { label: /username/i }, testData.username);
  await fillField(page, { label: /password/i }, testData.password);

  await clickElement(page, { role: 'button', name: /create|submit/i });

  // STEP 3: Verify Success
  await waitForNavigation(page, /dashboard|welcome/i);
  await verifyText(page, new RegExp(testData.email));

  console.log(`✅ Account created: ${testData.email}`);
});
```

---

### Example 3: Testing Async Operations (Loading States)

```typescript
test('should handle async content generation', async ({ page }) => {
  await navigateToPage(page, '/app/generate', { heading: /generate/i });

  // Select content items
  await clickElement(page, { testId: 'item-1' }, 'Content item 1');
  await clickElement(page, { testId: 'item-2' }, 'Content item 2');

  // Trigger async generation
  await clickElement(page, { role: 'button', name: /generate/i });

  // Wait for loading indicator to appear
  await waitForElement(
    page,
    { text: /generating|processing/i },
    'Loading indicator'
  );

  // Wait for generation to complete (up to 60 seconds)
  await waitForElement(
    page,
    { text: /complete|ready|view result/i },
    'Completion message',
    60000  // 60 second timeout
  );

  // Verify result
  await verifyVisible(page, { testId: 'generated-content' });

  await captureScreenshot(page, 'generation-complete');
});
```

---

### Example 4: Error Handling and Validation

```typescript
test('should handle form validation errors', async ({ page }) => {
  await navigateToPage(page, '/create-item', { heading: /create/i });

  // Try to submit empty form
  await clickElement(page, { role: 'button', name: /submit|save/i });

  // Verify error messages appear
  await verifyText(page, /required|cannot be empty/i);

  // Fill with invalid data
  await fillField(page, { label: /email/i }, 'invalid-email');
  await fillField(page, { label: /age/i }, '-5');

  await clickElement(page, { role: 'button', name: /submit/i });

  // Verify specific validation errors
  await verifyText(page, /valid email/i);
  await verifyText(page, /positive number/i);

  // Verify still on same page (didn't submit)
  await verifyUrl(page, /create-item/);

  // Now fill correctly
  await fillField(page, { label: /email/i }, 'valid@example.com');
  await fillField(page, { label: /age/i }, '25');

  await clickElement(page, { role: 'button', name: /submit/i });

  // Verify success
  await waitForNavigation(page, /success|item-list/i);
  await verifyText(page, /created successfully/i);
});
```

---

### Example 5: Using Page Objects for Complex Flows

```typescript
// 1. Define page objects (one time, reuse everywhere)
class DashboardPage extends BasePage {
  get createButton() { return this.page.getByRole('button', { name: /create/i }); }
  get itemList() { return this.page.locator('[data-testid="item-list"]'); }

  async createItem(name: string) {
    await this.createButton.click();
    await this.page.getByLabel(/name/i).fill(name);
    await this.page.getByRole('button', { name: /save/i }).click();
  }

  async verifyItemExists(name: string) {
    await expect(this.itemList.getByText(name)).toBeVisible();
  }
}

// 2. Use in multiple tests
test.describe('Dashboard Operations', () => {
  let dashboardPage: DashboardPage;

  test.beforeEach(async ({ page }) => {
    dashboardPage = new DashboardPage(page);
    await dashboardPage.goto('/app');
  });

  test('should create item', async () => {
    await dashboardPage.createItem('Test Item 1');
    await dashboardPage.verifyItemExists('Test Item 1');
  });

  test('should create multiple items', async () => {
    await dashboardPage.createItem('Item A');
    await dashboardPage.createItem('Item B');
    await dashboardPage.verifyItemExists('Item A');
    await dashboardPage.verifyItemExists('Item B');
  });
});
```

---

### Example 6: Config-Driven Test (JSON)

**Create:** `e2e/configs/user-registration.json`
```json
{
  "name": "User Registration Flow",
  "description": "Tests complete user registration",
  "timeout": 30000,
  "steps": [
    {
      "name": "Visit landing page",
      "action": "navigate",
      "url": "/"
    },
    {
      "name": "Click Get Started",
      "action": "click",
      "selector": {
        "role": "link",
        "name": "Get Started"
      }
    },
    {
      "name": "Fill name",
      "action": "fill",
      "selector": { "label": "Name" },
      "value": "Test User"
    },
    {
      "name": "Fill email",
      "action": "fill",
      "selector": { "label": "Email" },
      "value": "test@example.com"
    },
    {
      "name": "Fill password",
      "action": "fill",
      "selector": { "label": "Password" },
      "value": "SecurePass123!"
    },
    {
      "name": "Submit form",
      "action": "click",
      "selector": {
        "role": "button",
        "name": "Create Account"
      }
    },
    {
      "name": "Verify success",
      "action": "verify_text",
      "value": "Welcome"
    }
  ]
}
```

**Use in test file:**
```typescript
import { runTestFromFile } from './templates/journey-config-template';

// Load and run test from JSON
runTestFromFile('./e2e/configs/user-registration.json');
```

---

## Best Practices

### 1. Selector Strategy Priority

Always use selectors in this order (most to least resilient):

```typescript
// ✅ BEST: Accessible roles (won't break on styling changes)
{ role: 'button', name: /submit/i }

// ✅ GOOD: Labels (semantic, accessible)
{ label: /email address/i }

// ⚠️ OK: Text content (can break if text changes)
{ text: /click here/i }

// ⚠️ AVOID: Test IDs (requires code changes)
{ testId: 'submit-button' }

// ❌ LAST RESORT: CSS selectors (fragile, breaks easily)
{ css: '.btn-primary' }
```

### 2. Use Flexible Text Matching

```typescript
// ❌ Bad: Exact match (breaks easily)
{ name: 'Submit Form' }

// ✅ Good: Regex with case-insensitive flag
{ name: /submit.*form/i }

// ✅ Better: Multiple acceptable variations
{ name: /submit|save|create/i }
```

### 3. Wait for Elements Properly

```typescript
// ❌ Bad: Hard-coded waits
await page.waitForTimeout(5000);

// ✅ Good: Wait for specific element
await waitForVisible(page, { text: /success/i });

// ✅ Better: Wait with custom timeout
await waitForElement(page, { text: /success/i }, 'Success message', 10000);
```

### 4. Take Strategic Screenshots

```typescript
// Take screenshots at key moments
await captureScreenshot(page, 'before-submission');
await clickElement(page, submitButton);
await captureScreenshot(page, 'after-submission');
```

### 5. Use Descriptive Names

```typescript
// ❌ Bad
await clickElement(page, { role: 'button' });

// ✅ Good
await clickElement(page, { role: 'button', name: /submit/i }, 'Submit form button');
```

### 6. Generate Unique Test Data

```typescript
// ✅ Always use unique data to avoid conflicts
const testData = generateTestData('my-test');

await fillField(page, { label: /email/i }, testData.email);
// Uses: test-1701234567890-abc123@example.com
```

### 7. Clean Up After Tests

```typescript
test.afterEach(async ({ page }) => {
  // Clean up test data
  await clearStorage(page);

  // Or call backend cleanup
  // await cleanupTestUser(testEmail);
});
```

---

## Troubleshooting

### Problem: Element not found

**Error:** `Element not found with options: {...}`

**Solutions:**

1. **Use debug mode:**
```bash
npm run test:e2e:debug
```

2. **Take screenshot before the failing step:**
```typescript
await captureScreenshot(page, 'before-click');
await clickElement(page, ...);  // Fails here
```

3. **Try multiple selector strategies:**
```typescript
await findElement(page, {
  role: 'button',
  name: /submit/i,
  text: /submit/i,  // Fallback
  css: 'button[type="submit"]'  // Last resort
});
```

4. **Wait for element to appear:**
```typescript
await waitForVisible(page, { role: 'button', name: /submit/i });
await clickElement(page, { role: 'button', name: /submit/i });
```

---

### Problem: Test times out

**Error:** `Timeout 30000ms exceeded`

**Solutions:**

1. **Increase timeout:**
```typescript
test('my test', async ({ page }) => {
  test.setTimeout(60000);  // 60 seconds
  // ... test steps
});
```

2. **Wait for network idle:**
```typescript
await navigateToPage(page, '/slow-page', { heading: /title/i });
await waitForNetworkIdle(page);
```

3. **Wait for specific loading to complete:**
```typescript
await waitForLoadingToComplete(page, '.spinner', 30000);
```

---

### Problem: Flaky tests (sometimes pass, sometimes fail)

**Solutions:**

1. **Use retry logic:**
```typescript
await retry(async () => {
  await clickElement(page, myButton);
}, { maxRetries: 3, initialDelay: 1000 });
```

2. **Wait for element to be stable:**
```typescript
await page.waitForSelector('button', { state: 'visible' });
await page.waitForTimeout(500);  // Let animations complete
await clickElement(page, { role: 'button' });
```

3. **Check for loading indicators:**
```typescript
await waitForLoadingToComplete(page);
await clickElement(page, myButton);
```

---

### Problem: Can't find the right selector

**Solution: Use the debug helper:**

```typescript
// Add this to your test to see all elements
test('debug selectors', async ({ page }) => {
  await page.goto('/my-page');

  // Log all headings
  const headings = await page.locator('h1, h2, h3').allTextContents();
  console.log('Headings:', headings);

  // Log all buttons
  const buttons = await page.locator('button').allTextContents();
  console.log('Buttons:', buttons);

  // Take screenshot
  await captureScreenshot(page, 'debug-page');
});
```

---

## FAQ

### Q: Which template should I use?

**A:** It depends:

- **Need to write a test quickly?** → Use `universal-journey-template.spec.ts`
- **Building a test suite for a large app?** → Use `page-object-template.ts`
- **Non-developer creating tests?** → Use `journey-config-template.ts`
- **Need utility functions?** → Import from `test-helpers.ts`

---

### Q: Can I mix different approaches?

**A:** Yes! They work together:

```typescript
// Mix helpers + page objects
import { generateTestData } from './templates/test-helpers';
import { AuthPage } from './page-objects/auth-page';

test('mixed approach', async ({ page }) => {
  const testData = generateTestData();  // From helpers
  const authPage = new AuthPage(page);  // Page object

  await authPage.register(testData.email, testData.password);
});
```

---

### Q: How do I test a page that doesn't exist yet?

**A:** Use flexible selectors that will match when the page is built:

```typescript
test('future page test', async ({ page }) => {
  await navigateToPage(
    page,
    '/future-feature',
    {
      heading: /feature|new/i  // Match various possible headings
    }
  );

  await clickElement(
    page,
    {
      role: 'button',
      name: /continue|next|proceed/i  // Match various button text
    }
  );

  await verifyText(page, /success|complete/i);
});
```

This test will work as long as the page has:
- A heading with "feature" or "new"
- A button with "continue", "next", or "proceed"
- Success text with "success" or "complete"

---

### Q: How do I verify backend state (database/API)?

**A:** Use the backend helpers:

```typescript
import { apiRequest } from './templates/test-helpers';

test('with backend verification', async ({ page }) => {
  // Frontend action
  await clickElement(page, { role: 'button', name: /create/i });

  // Backend verification
  const response = await apiRequest(page, '/api/items', {
    method: 'GET',
    headers: { Authorization: 'Bearer token' }
  });

  expect(response.items).toHaveLength(1);
});
```

---

### Q: Can I run tests in parallel?

**A:** Yes, but be careful with shared state:

```typescript
// playwright.config.ts
export default defineConfig({
  workers: 4,  // Run 4 tests in parallel
  fullyParallel: true,
});

// In your test: Use unique test data
test('test 1', async ({ page }) => {
  const testData = generateTestData('test1');  // Unique email
  // ... use testData.email
});
```

---

### Q: How do I test file uploads?

**A:**
```typescript
await uploadFile(
  page,
  { label: /upload/i },
  './test-files/sample.pdf'
);
```

---

### Q: How do I test multiple browser tabs?

**A:**
```typescript
const newTab = await openNewTab(page, '/new-page');
// Work in new tab
await newTab.click('...');
// Switch back
await page.bringToFront();
```

---

## Summary

### Quick Reference

| Need | Use | File |
|------|-----|------|
| Quick test | Helper functions | `universal-journey-template.spec.ts` |
| Maintainable tests | Page Objects | `page-object-template.ts` |
| Utility functions | Import helpers | `test-helpers.ts` |
| No-code tests | JSON config | `journey-config-template.ts` |

### Next Steps

1. **Start simple:** Copy `universal-journey-template.spec.ts`
2. **Write your first test** using the helper functions
3. **Run it:** `npm run test:e2e your-test`
4. **Iterate:** Add more tests as needed
5. **Refactor:** Move to Page Objects when tests grow

### Getting Help

- Check [Playwright docs](https://playwright.dev)
- Review example tests in `e2e/` folder
- Use debug mode: `npm run test:e2e:debug`
- Take screenshots at each step to see what's happening

---

**You're ready to test ANY user journey! 🎭✨**
