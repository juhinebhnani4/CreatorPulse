# Playwright Test Templates

**Universal, reusable templates for testing ANY user journey across pages**

## 📋 What's Inside

This folder contains production-ready Playwright test templates that work with **any page**, even ones that don't exist yet!

### Templates

| File | Purpose | When to Use |
|------|---------|-------------|
| **[universal-journey-template.spec.ts](./universal-journey-template.spec.ts)** | Main test template with helper functions | Quick test creation, flexible testing |
| **[page-object-template.ts](./page-object-template.ts)** | Page Object Model (POM) pattern | Maintainable tests, large applications |
| **[test-helpers.ts](./test-helpers.ts)** | 60+ utility functions | All tests (import as needed) |
| **[journey-config-template.ts](./journey-config-template.ts)** | JSON-driven test approach | Non-developers, standardized tests |
| **[TEMPLATE_GUIDE.md](./TEMPLATE_GUIDE.md)** | Complete guide with examples | Learning, reference |

---

## 🚀 Quick Start (30 seconds)

### Option 1: Copy & Modify Template

```bash
# 1. Copy template
cp e2e/templates/universal-journey-template.spec.ts e2e/my-test.spec.ts

# 2. Edit the config section
# Update: name, description, screenshotPrefix

# 3. Write your test using helper functions
# See examples in the template file

# 4. Run it
npm run test:e2e my-test
```

### Option 2: Use Config-Driven Approach (No Code!)

```bash
# 1. Copy example config
cp e2e/configs/example-journey.json e2e/configs/my-journey.json

# 2. Edit the JSON file with your steps

# 3. Create test file
echo 'import { runTestFromFile } from "./templates/journey-config-template";
runTestFromFile("./e2e/configs/my-journey.json");' > e2e/my-journey.spec.ts

# 4. Run it
npm run test:e2e my-journey
```

---

## 📚 Key Features

### ✅ Works with ANY Page

The templates use flexible selectors that try multiple strategies:

```typescript
// This will find the button even if implementation changes
await clickElement(page, {
  role: 'button',           // Try accessible role first
  name: /submit|save/i,     // Flexible text matching
  text: /submit|save/i,     // Fallback to text content
  testId: 'submit-btn',     // Fallback to test ID
  css: 'button[type="submit"]' // Last resort
});
```

### ✅ Smart Waiting

No more flaky tests due to timing issues:

```typescript
// Auto-waits for element to appear
await waitForElement(page, { text: /success/i }, 'Success message');

// Waits for async operations
await waitForLoadingToComplete(page);

// Waits for navigation
await waitForUrl(page, /dashboard/i);
```

### ✅ Automatic Screenshots

Every step can capture screenshots for debugging:

```typescript
await captureScreenshot(page, 'step-name');
// Saved to: test-results/step-name.png
```

### ✅ Flexible Data Generation

Create unique test data automatically:

```typescript
const testData = generateTestData('my-test');
// Returns: {
//   email: 'my-test-1701234567-abc123@example.com',
//   username: 'my-test_abc123_1701234567',
//   password: 'SecurePass123!',
//   ...
// }
```

---

## 📖 Examples

### Example 1: Simple Form Test

```typescript
import { navigateToPage, fillField, clickElement, verifyText } from './templates/test-helpers';

test('should submit contact form', async ({ page }) => {
  await navigateToPage(page, '/contact', { heading: /contact/i });

  await fillField(page, { label: /name/i }, 'John Doe');
  await fillField(page, { label: /email/i }, 'john@example.com');
  await fillField(page, { label: /message/i }, 'Hello!');

  await clickElement(page, { role: 'button', name: /send/i });

  await verifyText(page, /thank you/i);
});
```

### Example 2: Using Page Objects

```typescript
import { AuthPage, DashboardPage } from './page-objects';

test('should login and view dashboard', async ({ page }) => {
  const authPage = new AuthPage(page, true); // true = login page
  const dashboardPage = new DashboardPage(page);

  await authPage.goto();
  await authPage.loginAndWait('user@example.com', 'password');

  await dashboardPage.verifyDashboardLoaded();
});
```

### Example 3: Config-Driven Test

Create `my-journey.json`:
```json
{
  "name": "My Test",
  "description": "Testing my feature",
  "steps": [
    { "name": "Visit page", "action": "navigate", "url": "/my-page" },
    { "name": "Click button", "action": "click", "selector": { "role": "button", "name": "Submit" } },
    { "name": "Verify success", "action": "verify_text", "value": "Success" }
  ]
}
```

Use it:
```typescript
import { runTestFromFile } from './templates/journey-config-template';
runTestFromFile('./e2e/configs/my-journey.json');
```

---

## 🎯 When to Use Each Template

### Use Universal Template (`universal-journey-template.spec.ts`) when:
- ✅ You need to write tests quickly
- ✅ Testing a new feature
- ✅ Tests are relatively simple (< 20 steps)
- ✅ You're comfortable with TypeScript

### Use Page Objects (`page-object-template.ts`) when:
- ✅ Building a comprehensive test suite
- ✅ Multiple tests interact with the same pages
- ✅ Application is complex with many pages
- ✅ Tests need to be highly maintainable
- ✅ Working in a team

### Use Config-Driven (`journey-config-template.ts`) when:
- ✅ QA/PM needs to write tests without coding
- ✅ Tests follow standardized patterns
- ✅ Need data-driven testing (same flow, different data)
- ✅ Tests are simple and linear

### Use Test Helpers (`test-helpers.ts`) when:
- ✅ Always! Import specific functions you need
- ✅ Creating custom test utilities
- ✅ Need specific utilities (data generation, waiting, etc.)

---

## 🔧 Helper Functions Reference

### Data Generation
```typescript
generateEmail(prefix)           // Unique email
generateUsername(prefix)        // Unique username
generatePassword(length)        // Secure password
generateTestData(prefix)        // Complete test data object
```

### Navigation
```typescript
navigateTo(page, url)           // Navigate and wait
waitForUrl(page, pattern)       // Wait for URL change
goBack(page)                    // Browser back
reload(page)                    // Refresh page
```

### Element Interaction
```typescript
clickElement(page, selector)    // Click with retry
fillField(page, selector, value) // Fill and verify
selectOption(page, selector, value) // Select dropdown
uploadFile(page, selector, path) // Upload file
typeSlowly(page, selector, text) // Type with delay
```

### Waiting
```typescript
wait(ms)                        // Simple delay
waitForVisible(page, selector)  // Wait for element
waitForHidden(page, selector)   // Wait for hidden
waitForLoadingToComplete(page)  // Wait for loading
waitForCondition(fn, options)   // Custom condition
```

### Verification
```typescript
verifyVisible(page, selector)   // Check visibility
verifyText(page, text)          // Check text on page
verifyUrl(page, pattern)        // Verify URL
verifyElementCount(page, selector, count) // Count elements
```

### Screenshots & Logging
```typescript
takeScreenshot(page, name)      // Capture screenshot
log(message, level)             // Log with timestamp
logStep(number, name)           // Log test step
```

---

## 📝 Best Practices

### 1. Use Flexible Selectors
```typescript
// ❌ Bad - Fragile
{ css: '.btn-primary' }

// ✅ Good - Resilient
{ role: 'button', name: /submit/i }
```

### 2. Generate Unique Test Data
```typescript
// ✅ Always use unique data
const testData = generateTestData('test');
await fillField(page, { label: /email/i }, testData.email);
```

### 3. Take Strategic Screenshots
```typescript
// Before and after important actions
await takeScreenshot(page, 'before-submit');
await clickElement(page, submitButton);
await takeScreenshot(page, 'after-submit');
```

### 4. Wait for Elements (Not Timeouts)
```typescript
// ❌ Bad
await page.waitForTimeout(5000);

// ✅ Good
await waitForVisible(page, { text: /success/i });
```

### 5. Use Descriptive Names
```typescript
await clickElement(
  page,
  { role: 'button', name: /submit/i },
  'Submit registration form'  // Clear description
);
```

---

## 🐛 Troubleshooting

### Element Not Found
1. Use `npm run test:e2e:debug` to inspect
2. Take screenshot before failing step
3. Try multiple selector strategies
4. Wait for element to appear first

### Test Timeouts
1. Increase timeout: `test.setTimeout(60000)`
2. Wait for loading to complete
3. Check network idle: `await waitForNetworkIdle(page)`

### Flaky Tests
1. Use retry logic: `await retry(action, { maxRetries: 3 })`
2. Wait for elements to stabilize
3. Check for loading indicators

---

## 📖 Full Documentation

See **[TEMPLATE_GUIDE.md](./TEMPLATE_GUIDE.md)** for:
- Detailed examples
- Complete API reference
- Advanced patterns
- FAQ
- Troubleshooting guide

---

## 🎓 Learning Path

1. **Start Here:** Read this README
2. **Try It:** Copy and run `universal-journey-template.spec.ts`
3. **Learn More:** Read [TEMPLATE_GUIDE.md](./TEMPLATE_GUIDE.md)
4. **Reference:** Browse helper functions in [test-helpers.ts](./test-helpers.ts)
5. **Advanced:** Study Page Objects in [page-object-template.ts](./page-object-template.ts)

---

## 📞 Support

- **Playwright Docs:** https://playwright.dev
- **Template Guide:** [TEMPLATE_GUIDE.md](./TEMPLATE_GUIDE.md)
- **Examples:** See `e2e/journey-*.spec.ts` files
- **Debug Mode:** `npm run test:e2e:debug`

---

**Happy Testing! 🎭✨**

The templates are designed to make testing ANY user journey simple and maintainable.
