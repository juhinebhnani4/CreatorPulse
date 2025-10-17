# Playwright Test Templates - Cheat Sheet

**Quick reference for common testing patterns**

---

## 🚀 Quick Start (Copy & Paste)

### Create New Test in 30 Seconds

```bash
# 1. Copy template
cp e2e/templates/universal-journey-template.spec.ts e2e/my-test.spec.ts

# 2. Run it
npm run test:e2e my-test
```

---

## 📋 Common Patterns

### Navigate to Page
```typescript
await navigateToPage(page, '/my-page', { heading: /My Page/i });
```

### Click Button
```typescript
await clickElement(page, { role: 'button', name: /submit/i }, 'Submit button');
```

### Fill Form Field
```typescript
await fillField(page, { label: /email/i }, 'test@example.com', 'Email');
```

### Verify Text
```typescript
await verifyText(page, /success/i);
```

### Wait for Navigation
```typescript
await waitForNavigation(page, /dashboard/i);
```

### Take Screenshot
```typescript
await captureScreenshot(page, 'step-name');
```

### Generate Test Data
```typescript
const testData = generateTestData('test');
// testData.email, testData.password, etc.
```

---

## 🎯 Selector Strategies (In Priority Order)

### 1. By Role (Best - Most Resilient)
```typescript
{ role: 'button', name: /submit/i }
{ role: 'link', name: /home/i }
{ role: 'textbox', name: /email/i }
```

### 2. By Label (Good for Forms)
```typescript
{ label: /email address/i }
{ label: /password/i }
```

### 3. By Text Content
```typescript
{ text: /click here/i }
{ text: /welcome/i }
```

### 4. By Placeholder
```typescript
{ placeholder: /search/i }
```

### 5. By Test ID
```typescript
{ testId: 'submit-button' }
```

### 6. By CSS (Last Resort)
```typescript
{ css: 'button.primary' }
```

---

## ⏱ Waiting Patterns

### Wait for Element
```typescript
await waitForElement(page, { text: /success/i }, 'Success message', 10000);
```

### Wait for URL
```typescript
await waitForUrl(page, /dashboard/i, 15000);
```

### Wait for Loading
```typescript
await waitForLoadingToComplete(page);
```

### Wait for Condition
```typescript
await waitForCondition(async () => {
  const count = await page.locator('.item').count();
  return count > 0;
});
```

### Simple Delay (Avoid This!)
```typescript
await wait(1000);  // Only use when nothing else works
```

---

## ✅ Verification Patterns

### Element Visible
```typescript
await verifyVisible(page, { role: 'button', name: /submit/i });
```

### Element Not Visible
```typescript
await verifyVisible(page, { text: /error/i }, false);
```

### Text on Page
```typescript
await verifyText(page, /welcome back/i);
```

### URL Pattern
```typescript
await verifyUrl(page, /dashboard/i);
```

### Element Count
```typescript
await verifyElementCount(page, '.item', 5);
```

---

## 📝 Complete Test Template

```typescript
import { test } from '@playwright/test';
import {
  generateTestData,
  navigateToPage,
  fillField,
  clickElement,
  waitForNavigation,
  verifyText,
} from './templates/test-helpers';

test('my test description', async ({ page }) => {
  // 1. Generate test data
  const testData = generateTestData('test');

  // 2. Navigate
  await navigateToPage(page, '/my-page', { heading: /My Page/i });

  // 3. Fill form
  await fillField(page, { label: /email/i }, testData.email);
  await fillField(page, { label: /password/i }, testData.password);

  // 4. Submit
  await clickElement(page, { role: 'button', name: /submit/i });

  // 5. Verify
  await waitForNavigation(page, /success/i);
  await verifyText(page, /welcome/i);
});
```

---

## 🔄 Common Test Flows

### Login Flow
```typescript
await navigateToPage(page, '/login', { heading: /login/i });
await fillField(page, { label: /email/i }, 'user@example.com');
await fillField(page, { label: /password/i }, 'password');
await clickElement(page, { role: 'button', name: /sign in/i });
await waitForNavigation(page, /dashboard/i);
```

### Registration Flow
```typescript
const testData = generateTestData();
await navigateToPage(page, '/register', { heading: /sign up/i });
await fillField(page, { label: /name/i }, 'Test User');
await fillField(page, { label: /email/i }, testData.email);
await fillField(page, { label: /password/i }, testData.password);
await clickElement(page, { role: 'button', name: /create account/i });
await verifyText(page, /welcome/i);
```

### Create Item Flow
```typescript
await clickElement(page, { role: 'button', name: /add|create/i });
await fillField(page, { label: /name/i }, 'New Item');
await fillField(page, { label: /description/i }, 'Description');
await clickElement(page, { role: 'button', name: /save/i });
await verifyText(page, /created successfully/i);
```

### Search Flow
```typescript
await fillField(page, { placeholder: /search/i }, 'query');
await clickElement(page, { role: 'button', name: /search/i });
await waitForElement(page, { text: /results/i });
await verifyElementCount(page, '.result-item', 5);
```

---

## 📦 Import Statements

### All Helpers
```typescript
import {
  generateTestData,
  navigateToPage,
  clickElement,
  fillField,
  waitForNavigation,
  verifyText,
  takeScreenshot,
} from './templates/test-helpers';
```

### Page Objects
```typescript
import { AuthPage, DashboardPage } from './templates/page-object-template';
```

### Config-Driven
```typescript
import { createTestFromConfig } from './templates/journey-config-template';
```

---

## 🐛 Debugging Commands

### Run in UI Mode
```bash
npm run test:e2e:ui
```

### Run in Debug Mode
```bash
npm run test:e2e:debug
```

### Run in Headed Mode (See Browser)
```bash
npm run test:e2e:headed
```

### Run Specific Test
```bash
npx playwright test my-test.spec.ts
```

### Run Single Test Case
```bash
npx playwright test my-test.spec.ts -g "should login"
```

---

## 🎨 Screenshot Helpers

### Take Screenshot
```typescript
await takeScreenshot(page, 'descriptive-name');
```

### Screenshot Before/After
```typescript
await takeScreenshot(page, 'before-submit');
await clickElement(page, submitButton);
await takeScreenshot(page, 'after-submit');
```

### Enable Auto Screenshots
```typescript
const JOURNEY_CONFIG = {
  enableScreenshots: true
};
```

---

## 🔢 Test Data Helpers

### Generate Email
```typescript
const email = generateEmail('test');
// test-1701234567-abc123@example.com
```

### Generate Username
```typescript
const username = generateUsername('user');
// user_abc123_1701234567
```

### Generate Password
```typescript
const password = generatePassword(12);
// SecureRand123!@
```

### Generate Complete Data
```typescript
const data = generateTestData('test');
// { email, username, password, firstName, lastName, ... }
```

---

## ⚙️ Configuration

### Test Timeout
```typescript
test.setTimeout(60000);  // 60 seconds
```

### Test Retry
```typescript
test.describe.configure({ retries: 2 });
```

### Skip Test
```typescript
test.skip('skipped test', async ({ page }) => {
  // ...
});
```

### Only Run This Test
```typescript
test.only('focused test', async ({ page }) => {
  // ...
});
```

---

## 🎯 Selector Examples

### Flexible Button Selector
```typescript
{
  role: 'button',
  name: /submit|save|create|continue/i,
  text: /submit|save|create|continue/i,
  testId: 'submit-btn',
  css: 'button[type="submit"]'
}
```

### Flexible Input Selector
```typescript
{
  label: /email|e-mail|email address/i,
  placeholder: /email/i,
  css: 'input[type="email"]'
}
```

### Flexible Link Selector
```typescript
{
  role: 'link',
  name: /home|homepage|start/i,
  text: /home|homepage|start/i
}
```

---

## 🔄 Retry Patterns

### Retry Click
```typescript
await retry(async () => {
  await clickElement(page, myButton);
}, { maxRetries: 3 });
```

### Retry with Custom Delay
```typescript
await retry(
  async () => await myAction(),
  {
    maxRetries: 3,
    initialDelay: 2000,
    backoffMultiplier: 2
  }
);
```

---

## 📱 Modal/Dialog Patterns

### Wait for Modal
```typescript
await waitForModal(page);
```

### Fill Modal Form
```typescript
await waitForModal(page);
await fillField(page, { label: /name/i }, 'Value');
await confirmModal(page);
```

### Close Modal
```typescript
await closeModal(page);
```

---

## 🔐 Authentication Patterns

### Set Auth Token
```typescript
await setAuthToken(page, 'token-value');
```

### Get Auth Token
```typescript
const token = await getAuthToken(page);
```

### Clear Storage
```typescript
await clearStorage(page);
```

---

## 🎭 Common Playwright Commands

### Basic Navigation
```typescript
await page.goto('/path');
await page.goBack();
await page.reload();
```

### Selectors
```typescript
page.getByRole('button', { name: /submit/i })
page.getByText(/welcome/i)
page.getByLabel(/email/i)
page.getByPlaceholder(/search/i)
page.getByTestId('submit-btn')
page.locator('.css-selector')
```

### Actions
```typescript
await element.click();
await element.fill('text');
await element.clear();
await element.selectOption('value');
await element.check();
await element.uncheck();
```

### Assertions
```typescript
await expect(element).toBeVisible();
await expect(element).toHaveText(/text/i);
await expect(element).toHaveValue('value');
await expect(page).toHaveURL(/pattern/i);
```

---

## 💡 Pro Tips

### 1. Always Use Unique Test Data
```typescript
const testData = generateTestData();  // ✅ Good
const email = 'test@example.com';     // ❌ Bad (conflicts)
```

### 2. Use Flexible Regex Matching
```typescript
{ name: /submit|save|create/i }  // ✅ Good
{ name: 'Submit Form' }          // ❌ Bad (exact match)
```

### 3. Wait for Elements, Not Timeouts
```typescript
await waitForElement(page, { text: /success/i });  // ✅ Good
await wait(5000);                                   // ❌ Bad
```

### 4. Take Screenshots at Key Steps
```typescript
await takeScreenshot(page, 'before-action');
await myAction();
await takeScreenshot(page, 'after-action');
```

### 5. Use Descriptive Names
```typescript
await clickElement(page, button, 'Submit registration form');  // ✅ Good
await clickElement(page, button);                              // ❌ OK but less clear
```

---

## 🚨 Common Mistakes to Avoid

### ❌ Don't: Hard-code waits
```typescript
await page.waitForTimeout(5000);  // Flaky!
```

### ✅ Do: Wait for specific conditions
```typescript
await waitForElement(page, { text: /success/i });
```

---

### ❌ Don't: Use fragile CSS selectors
```typescript
{ css: '.btn.btn-primary.submit-btn' }
```

### ✅ Do: Use accessible selectors
```typescript
{ role: 'button', name: /submit/i }
```

---

### ❌ Don't: Reuse test data
```typescript
const email = 'test@example.com';  // Same email in all tests
```

### ✅ Do: Generate unique data
```typescript
const testData = generateTestData();  // Unique each time
```

---

## 📚 Quick Reference Links

- **Templates:** `e2e/templates/`
- **Examples:** `e2e/example-using-template.spec.ts`
- **Guide:** `e2e/templates/TEMPLATE_GUIDE.md`
- **Helpers:** `e2e/templates/test-helpers.ts`

---

## 🎯 Decision Tree

**Which approach should I use?**

```
Need to write test quickly?
└─ Yes → Use helper functions (universal-journey-template.spec.ts)

Building large test suite?
└─ Yes → Use page objects (page-object-template.ts)

Non-developer creating tests?
└─ Yes → Use config-driven (journey-config-template.ts)

Need specific utility?
└─ Yes → Import from test-helpers.ts

Complex app with many pages?
└─ Yes → Hybrid approach (helpers + page objects)
```

---

**Print this and keep it handy! 📄✨**
