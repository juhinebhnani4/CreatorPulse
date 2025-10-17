/**
 * UNIVERSAL PLAYWRIGHT USER JOURNEY TEST TEMPLATE
 *
 * This template provides a flexible, reusable pattern for testing ANY user journey
 * across pages in your application. It works even with completely new pages.
 *
 * FEATURES:
 * - Page-agnostic (works with any page)
 * - Flexible element selectors (multiple fallback strategies)
 * - Automatic screenshots and logging
 * - Smart waiting and retry logic
 * - Backend verification support
 * - Error handling and recovery
 *
 * HOW TO USE:
 * 1. Copy this file to e2e/journey-{name}.spec.ts
 * 2. Update the test.describe() name
 * 3. Fill in your journey steps using the provided helper functions
 * 4. Run: npm run test:e2e journey-{name}
 *
 * EXAMPLE JOURNEYS PROVIDED:
 * - Example 1: Multi-step form submission
 * - Example 2: CRUD operations (Create, Read, Update, Delete)
 * - Example 3: Navigation and verification
 */

import { test, expect, Page } from '@playwright/test';

// ============================================================================
// CONFIGURATION - Customize these for your journey
// ============================================================================

const JOURNEY_CONFIG = {
  name: 'Your Journey Name',
  description: 'What this journey tests',
  timeout: 60000, // Global timeout for this journey
  screenshotPrefix: 'journey-template',
  enableLogging: true,
  enableScreenshots: true,
};

// ============================================================================
// UNIVERSAL HELPER FUNCTIONS - Works with ANY page
// ============================================================================

/**
 * Find element using multiple selector strategies (most flexible)
 * Tries: role → text → label → placeholder → data-testid → CSS
 */
async function findElement(
  page: Page,
  options: {
    role?: string;
    name?: string | RegExp;
    text?: string | RegExp;
    label?: string | RegExp;
    placeholder?: string | RegExp;
    testId?: string;
    css?: string;
    exact?: boolean;
  }
): Promise<any> {
  const { role, name, text, label, placeholder, testId, css, exact = false } = options;

  // Strategy 1: Role-based (most accessible)
  if (role && name) {
    const locator = page.getByRole(role as any, { name, exact });
    if (await locator.count() > 0) return locator;
  }

  // Strategy 2: Text content
  if (text) {
    const locator = page.getByText(text, { exact });
    if (await locator.count() > 0) return locator;
  }

  // Strategy 3: Label (for inputs)
  if (label) {
    const locator = page.getByLabel(label, { exact });
    if (await locator.count() > 0) return locator;
  }

  // Strategy 4: Placeholder
  if (placeholder) {
    const locator = page.getByPlaceholder(placeholder, { exact });
    if (await locator.count() > 0) return locator;
  }

  // Strategy 5: Test ID
  if (testId) {
    const locator = page.getByTestId(testId);
    if (await locator.count() > 0) return locator;
  }

  // Strategy 6: CSS selector (last resort)
  if (css) {
    const locator = page.locator(css);
    if (await locator.count() > 0) return locator;
  }

  throw new Error(`Element not found with options: ${JSON.stringify(options)}`);
}

/**
 * Navigate to a page and verify it loaded
 */
async function navigateToPage(
  page: Page,
  url: string,
  verification: {
    heading?: string | RegExp;
    text?: string | RegExp;
    url?: string | RegExp;
  },
  stepName?: string
): Promise<void> {
  const step = stepName || `Navigate to ${url}`;

  await test.step(step, async () => {
    log(`Navigating to: ${url}`);
    await page.goto(url);

    // Verify page loaded
    if (verification.heading) {
      await expect(page.locator('h1, h2, h3').first()).toContainText(verification.heading, { timeout: 10000 });
    }

    if (verification.text) {
      await expect(page.getByText(verification.text)).toBeVisible({ timeout: 10000 });
    }

    if (verification.url) {
      await page.waitForURL(verification.url, { timeout: 10000 });
    }

    await captureScreenshot(page, `${step.toLowerCase().replace(/\s+/g, '-')}`);
    log(`✓ Successfully navigated to ${url}`);
  });
}

/**
 * Fill a form field (works with any input type)
 */
async function fillField(
  page: Page,
  field: {
    label?: string | RegExp;
    placeholder?: string | RegExp;
    name?: string;
    testId?: string;
    css?: string;
  },
  value: string,
  fieldName?: string
): Promise<void> {
  const name = fieldName || 'field';

  await test.step(`Fill ${name} field`, async () => {
    log(`Filling ${name}: ${value}`);

    const element = await findElement(page, {
      label: field.label,
      placeholder: field.placeholder,
      testId: field.testId,
      css: field.css,
    });

    await element.fill(value);
    await element.blur(); // Trigger validation

    log(`✓ Filled ${name}`);
  });
}

/**
 * Click a button or link (flexible selector)
 */
async function clickElement(
  page: Page,
  element: {
    role?: string;
    name?: string | RegExp;
    text?: string | RegExp;
    testId?: string;
    css?: string;
  },
  elementName?: string
): Promise<void> {
  const name = elementName || 'element';

  await test.step(`Click ${name}`, async () => {
    log(`Clicking: ${name}`);

    const locator = await findElement(page, element);
    await locator.click();

    log(`✓ Clicked ${name}`);
  });
}

/**
 * Verify element is visible on the page
 */
async function verifyVisible(
  page: Page,
  element: {
    role?: string;
    name?: string | RegExp;
    text?: string | RegExp;
    testId?: string;
    css?: string;
  },
  elementName?: string,
  shouldBeVisible: boolean = true
): Promise<void> {
  const name = elementName || 'element';

  await test.step(`Verify ${name} is ${shouldBeVisible ? 'visible' : 'not visible'}`, async () => {
    log(`Verifying ${name} visibility: ${shouldBeVisible}`);

    const locator = await findElement(page, element);

    if (shouldBeVisible) {
      await expect(locator).toBeVisible({ timeout: 10000 });
    } else {
      await expect(locator).not.toBeVisible({ timeout: 10000 });
    }

    log(`✓ ${name} visibility verified`);
  });
}

/**
 * Wait for URL change (navigation)
 */
async function waitForNavigation(
  page: Page,
  urlPattern: string | RegExp,
  stepName?: string
): Promise<void> {
  const step = stepName || `Wait for navigation to ${urlPattern}`;

  await test.step(step, async () => {
    log(`Waiting for URL: ${urlPattern}`);
    await page.waitForURL(urlPattern, { timeout: 15000 });

    const currentUrl = page.url();
    log(`✓ Navigated to: ${currentUrl}`);

    await captureScreenshot(page, step.toLowerCase().replace(/\s+/g, '-'));
  });
}

/**
 * Wait for element to appear (for async content)
 */
async function waitForElement(
  page: Page,
  element: {
    role?: string;
    name?: string | RegExp;
    text?: string | RegExp;
    testId?: string;
    css?: string;
  },
  elementName?: string,
  timeout: number = 30000
): Promise<void> {
  const name = elementName || 'element';

  await test.step(`Wait for ${name} to appear`, async () => {
    log(`Waiting for ${name} (timeout: ${timeout}ms)`);

    const locator = await findElement(page, element);
    await expect(locator).toBeVisible({ timeout });

    log(`✓ ${name} appeared`);
  });
}

/**
 * Verify text content on page
 */
async function verifyText(
  page: Page,
  text: string | RegExp,
  shouldExist: boolean = true
): Promise<void> {
  await test.step(`Verify text: ${text}`, async () => {
    log(`Verifying text: ${text}`);

    if (shouldExist) {
      await expect(page.getByText(text)).toBeVisible({ timeout: 10000 });
    } else {
      await expect(page.getByText(text)).not.toBeVisible();
    }

    log(`✓ Text verification passed`);
  });
}

/**
 * Take screenshot with consistent naming
 */
async function captureScreenshot(page: Page, stepName: string): Promise<void> {
  if (!JOURNEY_CONFIG.enableScreenshots) return;

  const filename = `${JOURNEY_CONFIG.screenshotPrefix}-${stepName}.png`;
  await page.screenshot({
    path: `test-results/${filename}`,
    fullPage: true,
  });
}

/**
 * Log message to console (if enabled)
 */
function log(message: string): void {
  if (JOURNEY_CONFIG.enableLogging) {
    console.log(`[${JOURNEY_CONFIG.name}] ${message}`);
  }
}

/**
 * Generate unique test data
 */
function generateTestData(prefix: string = 'test'): {
  email: string;
  username: string;
  timestamp: number;
  randomId: string;
} {
  const timestamp = Date.now();
  const randomId = Math.random().toString(36).substring(7);

  return {
    email: `${prefix}-${timestamp}-${randomId}@example.com`,
    username: `${prefix}_${randomId}`,
    timestamp,
    randomId,
  };
}

/**
 * Retry an action with exponential backoff
 */
async function retryAction<T>(
  action: () => Promise<T>,
  maxRetries: number = 3,
  delayMs: number = 1000
): Promise<T> {
  let lastError: Error | undefined;

  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      return await action();
    } catch (error) {
      lastError = error as Error;
      log(`Attempt ${attempt} failed: ${lastError.message}`);

      if (attempt < maxRetries) {
        const delay = delayMs * Math.pow(2, attempt - 1);
        log(`Retrying in ${delay}ms...`);
        await new Promise(resolve => setTimeout(resolve, delay));
      }
    }
  }

  throw lastError;
}

// ============================================================================
// EXAMPLE 1: Multi-Step Form Submission Journey
// ============================================================================

test.describe('Example Journey 1: Multi-Step Form Submission', () => {
  let testData: ReturnType<typeof generateTestData>;

  test.beforeEach(() => {
    testData = generateTestData('form-test');
    log('Test data generated');
  });

  test('should complete multi-step form submission', async ({ page }) => {
    // STEP 1: Navigate to form
    await navigateToPage(
      page,
      '/',
      { heading: /welcome|home/i },
      'Visit landing page'
    );

    // STEP 2: Click "Get Started" or similar button
    await clickElement(
      page,
      { role: 'link', name: /get started|sign up|start/i },
      'Get Started button'
    );

    // STEP 3: Wait for form page to load
    await waitForNavigation(page, /register|signup/i, 'Navigate to registration');

    // STEP 4: Fill form fields
    await fillField(
      page,
      { label: /name|username/i },
      testData.username,
      'Name'
    );

    await fillField(
      page,
      { label: /email/i },
      testData.email,
      'Email'
    );

    await fillField(
      page,
      { label: /password/i },
      'SecurePass123!',
      'Password'
    );

    // STEP 5: Submit form
    await captureScreenshot(page, 'form-filled');

    await clickElement(
      page,
      { role: 'button', name: /submit|create|sign up/i },
      'Submit button'
    );

    // STEP 6: Verify success (navigation or message)
    await waitForNavigation(page, /app|dashboard|success/i, 'Redirect after submission');

    // STEP 7: Verify user is logged in
    await verifyVisible(
      page,
      { role: 'button', name: /logout|sign out|profile/i },
      'User menu',
      true
    );

    log('✅ Journey completed successfully!');
  });
});

// ============================================================================
// EXAMPLE 2: CRUD Operations Journey
// ============================================================================

test.describe('Example Journey 2: CRUD Operations', () => {
  let testData: ReturnType<typeof generateTestData>;
  let itemName: string;

  test.beforeEach(async ({ page }) => {
    testData = generateTestData('crud-test');
    itemName = `Test Item ${testData.randomId}`;

    // Assume user is already logged in
    // (You can add login steps here if needed)
  });

  test('should perform Create, Read, Update, Delete operations', async ({ page }) => {
    // ========== CREATE ==========
    await test.step('CREATE: Add new item', async () => {
      await navigateToPage(page, '/app', { heading: /dashboard/i });

      await clickElement(
        page,
        { role: 'button', name: /add|create|new/i },
        'Add new item button'
      );

      await fillField(
        page,
        { label: /name|title/i },
        itemName,
        'Item name'
      );

      await clickElement(
        page,
        { role: 'button', name: /save|create|submit/i },
        'Save button'
      );

      // Verify creation success
      await verifyText(page, /created|added|success/i);
      log(`✓ Created item: ${itemName}`);
    });

    // ========== READ ==========
    await test.step('READ: Verify item appears in list', async () => {
      await verifyText(page, itemName);
      log(`✓ Item found in list: ${itemName}`);
    });

    // ========== UPDATE ==========
    await test.step('UPDATE: Edit the item', async () => {
      const updatedName = `${itemName} (Updated)`;

      // Find and click edit button for the item
      await clickElement(
        page,
        { role: 'button', name: /edit/i },
        'Edit button'
      );

      // Update the name
      await fillField(
        page,
        { label: /name|title/i },
        updatedName,
        'Updated name'
      );

      await clickElement(
        page,
        { role: 'button', name: /save|update/i },
        'Update button'
      );

      // Verify update success
      await verifyText(page, updatedName);
      log(`✓ Updated item to: ${updatedName}`);
    });

    // ========== DELETE ==========
    await test.step('DELETE: Remove the item', async () => {
      await clickElement(
        page,
        { role: 'button', name: /delete|remove/i },
        'Delete button'
      );

      // Confirm deletion if there's a modal
      await clickElement(
        page,
        { role: 'button', name: /confirm|yes|delete/i },
        'Confirm delete button'
      );

      // Verify item is gone
      await verifyText(page, itemName, false);
      log(`✓ Deleted item: ${itemName}`);
    });

    log('✅ CRUD journey completed successfully!');
  });
});

// ============================================================================
// EXAMPLE 3: Navigation and Multi-Page Verification
// ============================================================================

test.describe('Example Journey 3: Navigation Flow', () => {
  test('should navigate through multiple pages and verify content', async ({ page }) => {
    // Page 1: Landing
    await navigateToPage(
      page,
      '/',
      { heading: /welcome/i },
      'Visit landing page'
    );

    // Page 2: Features/About
    await clickElement(
      page,
      { role: 'link', name: /features|about/i },
      'Features link'
    );

    await verifyText(page, /feature|benefit/i);

    // Page 3: Pricing (if exists)
    await clickElement(
      page,
      { role: 'link', name: /pricing|plans/i },
      'Pricing link'
    );

    await verifyText(page, /price|plan|subscription/i);

    // Page 4: Back to home
    await clickElement(
      page,
      { role: 'link', name: /home|logo/i },
      'Home link'
    );

    await waitForNavigation(page, /^\/$|\/home/);

    log('✅ Navigation journey completed!');
  });
});

// ============================================================================
// EXAMPLE 4: Error Handling and Validation
// ============================================================================

test.describe('Example Journey 4: Error Handling', () => {
  test('should handle form validation errors', async ({ page }) => {
    await navigateToPage(page, '/register', { heading: /sign up|create/i });

    // Try to submit empty form
    await clickElement(
      page,
      { role: 'button', name: /submit|create/i },
      'Submit button'
    );

    // Verify validation errors appear
    await verifyText(page, /required|invalid|error/i);

    // Fill with invalid data
    await fillField(
      page,
      { label: /email/i },
      'invalid-email',
      'Invalid email'
    );

    await clickElement(
      page,
      { role: 'button', name: /submit|create/i },
      'Submit button'
    );

    // Verify still on same page (validation failed)
    await expect(page.url()).toContain('register');

    log('✅ Error handling verified!');
  });
});

// ============================================================================
// EXAMPLE 5: Async Operations with Waiting
// ============================================================================

test.describe('Example Journey 5: Async Operations', () => {
  test('should handle async operations (loading, generation, etc.)', async ({ page }) => {
    await navigateToPage(page, '/app/dashboard', { heading: /dashboard/i });

    // Trigger async operation
    await clickElement(
      page,
      { role: 'button', name: /generate|process|start/i },
      'Start async operation'
    );

    // Wait for loading indicator to appear
    await waitForElement(
      page,
      { text: /loading|processing|generating/i },
      'Loading indicator'
    );

    // Wait for loading to complete and result to appear
    await waitForElement(
      page,
      { text: /complete|done|success|result/i },
      'Completion message',
      60000 // 60 second timeout for long operations
    );

    // Verify result is displayed
    await verifyText(page, /result|output|generated/i);

    log('✅ Async operation completed!');
  });
});

// ============================================================================
// TEMPLATE FOR YOUR OWN JOURNEY
// ============================================================================

test.describe.skip('TEMPLATE: Your Custom Journey', () => {
  let testData: ReturnType<typeof generateTestData>;

  test.beforeEach(() => {
    testData = generateTestData('custom');
  });

  test('should complete custom journey', async ({ page }) => {
    // STEP 1: Navigate to starting page
    await navigateToPage(
      page,
      '/your-page',
      { heading: /your heading/i },
      'Step 1: Description'
    );

    // STEP 2: Interact with elements
    await clickElement(
      page,
      { role: 'button', name: /button name/i },
      'Button description'
    );

    // STEP 3: Fill forms
    await fillField(
      page,
      { label: /field label/i },
      'field value',
      'Field name'
    );

    // STEP 4: Submit or save
    await clickElement(
      page,
      { role: 'button', name: /submit/i },
      'Submit'
    );

    // STEP 5: Verify result
    await waitForNavigation(page, /success-page/i);
    await verifyText(page, /success message/i);

    log('✅ Custom journey completed!');
  });
});
