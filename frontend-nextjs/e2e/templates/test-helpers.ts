/**
 * UNIVERSAL TEST HELPERS
 *
 * Collection of reusable helper functions for Playwright tests.
 * These work with ANY page and ANY application.
 *
 * CATEGORIES:
 * - Data Generation
 * - Element Interaction
 * - Waiting & Timing
 * - Verification
 * - Navigation
 * - Screenshot & Logging
 * - Backend Integration
 * - Retry & Error Handling
 */

import { Page, Locator, expect } from '@playwright/test';

// ============================================================================
// DATA GENERATION HELPERS
// ============================================================================

/**
 * Generate unique test email address
 */
export function generateEmail(prefix: string = 'test'): string {
  const timestamp = Date.now();
  const random = Math.random().toString(36).substring(2, 8);
  return `${prefix}-${timestamp}-${random}@example.com`;
}

/**
 * Generate unique username
 */
export function generateUsername(prefix: string = 'user'): string {
  const timestamp = Date.now();
  const random = Math.random().toString(36).substring(2, 8);
  return `${prefix}_${random}_${timestamp}`;
}

/**
 * Generate random string of specified length
 */
export function generateRandomString(length: number = 10): string {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
  let result = '';
  for (let i = 0; i < length; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return result;
}

/**
 * Generate secure password
 */
export function generatePassword(length: number = 12): string {
  const lowercase = 'abcdefghijklmnopqrstuvwxyz';
  const uppercase = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
  const numbers = '0123456789';
  const special = '!@#$%^&*';
  const all = lowercase + uppercase + numbers + special;

  let password = '';
  password += lowercase[Math.floor(Math.random() * lowercase.length)];
  password += uppercase[Math.floor(Math.random() * uppercase.length)];
  password += numbers[Math.floor(Math.random() * numbers.length)];
  password += special[Math.floor(Math.random() * special.length)];

  for (let i = password.length; i < length; i++) {
    password += all[Math.floor(Math.random() * all.length)];
  }

  return password.split('').sort(() => 0.5 - Math.random()).join('');
}

/**
 * Generate test data object
 */
export function generateTestData(prefix: string = 'test'): {
  email: string;
  username: string;
  password: string;
  firstName: string;
  lastName: string;
  fullName: string;
  timestamp: number;
  randomId: string;
} {
  const timestamp = Date.now();
  const randomId = Math.random().toString(36).substring(2, 8);

  return {
    email: generateEmail(prefix),
    username: generateUsername(prefix),
    password: generatePassword(),
    firstName: `First${randomId}`,
    lastName: `Last${randomId}`,
    fullName: `First${randomId} Last${randomId}`,
    timestamp,
    randomId,
  };
}

/**
 * Generate future date
 */
export function generateFutureDate(daysAhead: number = 7): Date {
  const date = new Date();
  date.setDate(date.getDate() + daysAhead);
  return date;
}

/**
 * Format date for input fields
 */
export function formatDateForInput(date: Date): string {
  return date.toISOString().split('T')[0];
}

// ============================================================================
// ELEMENT INTERACTION HELPERS
// ============================================================================

/**
 * Find element using multiple fallback strategies
 */
export async function findElement(
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
): Promise<Locator> {
  const { role, name, text, label, placeholder, testId, css, exact = false } = options;

  // Try different strategies in order of preference
  if (role && name) {
    const locator = page.getByRole(role as any, { name, exact });
    if (await locator.count() > 0) return locator;
  }

  if (text) {
    const locator = page.getByText(text, { exact });
    if (await locator.count() > 0) return locator;
  }

  if (label) {
    const locator = page.getByLabel(label, { exact });
    if (await locator.count() > 0) return locator;
  }

  if (placeholder) {
    const locator = page.getByPlaceholder(placeholder, { exact });
    if (await locator.count() > 0) return locator;
  }

  if (testId) {
    const locator = page.getByTestId(testId);
    if (await locator.count() > 0) return locator;
  }

  if (css) {
    const locator = page.locator(css);
    if (await locator.count() > 0) return locator;
  }

  throw new Error(`Element not found with options: ${JSON.stringify(options)}`);
}

/**
 * Click element with automatic retry
 */
export async function clickElement(
  page: Page,
  selector: string | Locator,
  options: { timeout?: number; force?: boolean; retry?: number } = {}
): Promise<void> {
  const { timeout = 10000, force = false, retry = 3 } = options;
  const locator = typeof selector === 'string' ? page.locator(selector) : selector;

  for (let i = 0; i < retry; i++) {
    try {
      await locator.click({ timeout, force });
      return;
    } catch (error) {
      if (i === retry - 1) throw error;
      await wait(1000);
    }
  }
}

/**
 * Fill field with validation
 */
export async function fillField(
  page: Page,
  selector: string | Locator,
  value: string,
  options: { timeout?: number; verify?: boolean } = {}
): Promise<void> {
  const { timeout = 10000, verify = true } = options;
  const locator = typeof selector === 'string' ? page.locator(selector) : selector;

  await locator.fill(value, { timeout });

  if (verify) {
    await expect(locator).toHaveValue(value, { timeout: 5000 });
  }
}

/**
 * Select dropdown option
 */
export async function selectOption(
  page: Page,
  selector: string | Locator,
  value: string | string[]
): Promise<void> {
  const locator = typeof selector === 'string' ? page.locator(selector) : selector;
  await locator.selectOption(value);
}

/**
 * Upload file
 */
export async function uploadFile(
  page: Page,
  selector: string | Locator,
  filePath: string | string[]
): Promise<void> {
  const locator = typeof selector === 'string' ? page.locator(selector) : selector;
  await locator.setInputFiles(filePath);
}

/**
 * Clear field
 */
export async function clearField(
  page: Page,
  selector: string | Locator
): Promise<void> {
  const locator = typeof selector === 'string' ? page.locator(selector) : selector;
  await locator.clear();
}

/**
 * Type slowly (for autocomplete/search fields)
 */
export async function typeSlowly(
  page: Page,
  selector: string | Locator,
  text: string,
  delayMs: number = 100
): Promise<void> {
  const locator = typeof selector === 'string' ? page.locator(selector) : selector;
  await locator.click();
  await locator.pressSequentially(text, { delay: delayMs });
}

// ============================================================================
// WAITING & TIMING HELPERS
// ============================================================================

/**
 * Wait for specified milliseconds
 */
export async function wait(ms: number): Promise<void> {
  await new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * Wait for element to be visible
 */
export async function waitForVisible(
  page: Page,
  selector: string | Locator,
  timeout: number = 30000
): Promise<void> {
  const locator = typeof selector === 'string' ? page.locator(selector) : selector;
  await expect(locator).toBeVisible({ timeout });
}

/**
 * Wait for element to be hidden
 */
export async function waitForHidden(
  page: Page,
  selector: string | Locator,
  timeout: number = 30000
): Promise<void> {
  const locator = typeof selector === 'string' ? page.locator(selector) : selector;
  await expect(locator).toBeHidden({ timeout });
}

/**
 * Wait for loading indicator to disappear
 */
export async function waitForLoadingToComplete(
  page: Page,
  loadingSelector: string = '.loading, [data-loading="true"], .spinner, svg.animate-spin',
  timeout: number = 30000
): Promise<void> {
  try {
    await page.locator(loadingSelector).first().waitFor({ state: 'hidden', timeout });
  } catch {
    // Loading indicator might not appear if page loads very quickly
    console.log('Loading indicator not found or already hidden');
  }
}

/**
 * Wait for network to be idle
 */
export async function waitForNetworkIdle(page: Page): Promise<void> {
  await page.waitForLoadState('networkidle');
}

/**
 * Wait for URL to match pattern
 */
export async function waitForUrl(
  page: Page,
  urlPattern: string | RegExp,
  timeout: number = 15000
): Promise<void> {
  await page.waitForURL(urlPattern, { timeout });
}

/**
 * Poll for condition to be true
 */
export async function waitForCondition(
  condition: () => Promise<boolean>,
  options: {
    timeout?: number;
    interval?: number;
    errorMessage?: string;
  } = {}
): Promise<void> {
  const { timeout = 30000, interval = 1000, errorMessage = 'Condition not met within timeout' } = options;

  const startTime = Date.now();

  while (Date.now() - startTime < timeout) {
    if (await condition()) {
      return;
    }
    await wait(interval);
  }

  throw new Error(errorMessage);
}

// ============================================================================
// VERIFICATION HELPERS
// ============================================================================

/**
 * Verify element is visible
 */
export async function verifyVisible(
  page: Page,
  selector: string | Locator,
  shouldBeVisible: boolean = true
): Promise<void> {
  const locator = typeof selector === 'string' ? page.locator(selector) : selector;

  if (shouldBeVisible) {
    await expect(locator).toBeVisible();
  } else {
    await expect(locator).not.toBeVisible();
  }
}

/**
 * Verify text is on page
 */
export async function verifyText(
  page: Page,
  text: string | RegExp,
  shouldExist: boolean = true
): Promise<void> {
  if (shouldExist) {
    await expect(page.getByText(text)).toBeVisible();
  } else {
    await expect(page.getByText(text)).not.toBeVisible();
  }
}

/**
 * Verify URL matches pattern
 */
export async function verifyUrl(
  page: Page,
  pattern: string | RegExp
): Promise<void> {
  await expect(page).toHaveURL(pattern);
}

/**
 * Verify page title
 */
export async function verifyTitle(
  page: Page,
  title: string | RegExp
): Promise<void> {
  await expect(page).toHaveTitle(title);
}

/**
 * Verify element count
 */
export async function verifyElementCount(
  page: Page,
  selector: string | Locator,
  expectedCount: number
): Promise<void> {
  const locator = typeof selector === 'string' ? page.locator(selector) : selector;
  await expect(locator).toHaveCount(expectedCount);
}

/**
 * Verify element contains text
 */
export async function verifyElementText(
  page: Page,
  selector: string | Locator,
  text: string | RegExp
): Promise<void> {
  const locator = typeof selector === 'string' ? page.locator(selector) : selector;
  await expect(locator).toContainText(text);
}

/**
 * Verify input value
 */
export async function verifyInputValue(
  page: Page,
  selector: string | Locator,
  value: string | RegExp
): Promise<void> {
  const locator = typeof selector === 'string' ? page.locator(selector) : selector;
  await expect(locator).toHaveValue(value);
}

/**
 * Verify checkbox is checked
 */
export async function verifyChecked(
  page: Page,
  selector: string | Locator,
  shouldBeChecked: boolean = true
): Promise<void> {
  const locator = typeof selector === 'string' ? page.locator(selector) : selector;

  if (shouldBeChecked) {
    await expect(locator).toBeChecked();
  } else {
    await expect(locator).not.toBeChecked();
  }
}

// ============================================================================
// NAVIGATION HELPERS
// ============================================================================

/**
 * Navigate to URL and wait for load
 */
export async function navigateTo(
  page: Page,
  url: string,
  waitForLoad: boolean = true
): Promise<void> {
  await page.goto(url);

  if (waitForLoad) {
    await waitForNetworkIdle(page);
  }
}

/**
 * Go back in browser history
 */
export async function goBack(page: Page): Promise<void> {
  await page.goBack();
}

/**
 * Go forward in browser history
 */
export async function goForward(page: Page): Promise<void> {
  await page.goForward();
}

/**
 * Reload current page
 */
export async function reload(page: Page): Promise<void> {
  await page.reload();
}

/**
 * Open new tab
 */
export async function openNewTab(page: Page, url: string): Promise<Page> {
  const context = page.context();
  const newPage = await context.newPage();
  await newPage.goto(url);
  return newPage;
}

// ============================================================================
// SCREENSHOT & LOGGING HELPERS
// ============================================================================

/**
 * Take screenshot with consistent naming
 */
export async function takeScreenshot(
  page: Page,
  name: string,
  options: { fullPage?: boolean; path?: string } = {}
): Promise<void> {
  const { fullPage = true, path } = options;
  const filename = path || `test-results/${name}-${Date.now()}.png`;

  await page.screenshot({ path: filename, fullPage });
  console.log(`📸 Screenshot saved: ${filename}`);
}

/**
 * Log message with timestamp
 */
export function log(message: string, level: 'info' | 'warn' | 'error' = 'info'): void {
  const timestamp = new Date().toISOString();
  const emoji = level === 'info' ? 'ℹ️' : level === 'warn' ? '⚠️' : '❌';
  console.log(`${emoji} [${timestamp}] ${message}`);
}

/**
 * Log test step
 */
export function logStep(stepNumber: number, stepName: string): void {
  console.log(`\n📍 Step ${stepNumber}: ${stepName}`);
}

// ============================================================================
// BACKEND/API HELPERS
// ============================================================================

/**
 * Make API request
 */
export async function apiRequest(
  page: Page,
  url: string,
  options: {
    method?: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';
    headers?: Record<string, string>;
    body?: any;
  } = {}
): Promise<any> {
  const { method = 'GET', headers = {}, body } = options;

  const response = await page.request.fetch(url, {
    method,
    headers: {
      'Content-Type': 'application/json',
      ...headers,
    },
    data: body,
  });

  return await response.json();
}

/**
 * Get authentication token from browser storage
 */
export async function getAuthToken(page: Page, storageKey: string = 'token'): Promise<string | null> {
  return await page.evaluate((key) => {
    return localStorage.getItem(key) || sessionStorage.getItem(key);
  }, storageKey);
}

/**
 * Set authentication token in browser storage
 */
export async function setAuthToken(
  page: Page,
  token: string,
  storageKey: string = 'token',
  useLocalStorage: boolean = true
): Promise<void> {
  await page.evaluate(
    ({ key, value, useLocal }) => {
      if (useLocal) {
        localStorage.setItem(key, value);
      } else {
        sessionStorage.setItem(key, value);
      }
    },
    { key: storageKey, value: token, useLocal: useLocalStorage }
  );
}

/**
 * Clear all browser storage
 */
export async function clearStorage(page: Page): Promise<void> {
  await page.evaluate(() => {
    localStorage.clear();
    sessionStorage.clear();
  });
}

// ============================================================================
// RETRY & ERROR HANDLING HELPERS
// ============================================================================

/**
 * Retry action with exponential backoff
 */
export async function retry<T>(
  action: () => Promise<T>,
  options: {
    maxRetries?: number;
    initialDelay?: number;
    maxDelay?: number;
    backoffMultiplier?: number;
    onRetry?: (attempt: number, error: Error) => void;
  } = {}
): Promise<T> {
  const {
    maxRetries = 3,
    initialDelay = 1000,
    maxDelay = 10000,
    backoffMultiplier = 2,
    onRetry,
  } = options;

  let lastError: Error | undefined;

  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      return await action();
    } catch (error) {
      lastError = error as Error;

      if (attempt < maxRetries) {
        const delay = Math.min(initialDelay * Math.pow(backoffMultiplier, attempt - 1), maxDelay);

        if (onRetry) {
          onRetry(attempt, lastError);
        } else {
          log(`Retry attempt ${attempt}/${maxRetries} after ${delay}ms`, 'warn');
        }

        await wait(delay);
      }
    }
  }

  throw lastError;
}

/**
 * Try action and return null on failure instead of throwing
 */
export async function tryAction<T>(action: () => Promise<T>): Promise<T | null> {
  try {
    return await action();
  } catch (error) {
    log(`Action failed: ${(error as Error).message}`, 'error');
    return null;
  }
}

/**
 * Execute action with timeout
 */
export async function withTimeout<T>(
  action: () => Promise<T>,
  timeoutMs: number,
  errorMessage?: string
): Promise<T> {
  return await Promise.race([
    action(),
    new Promise<T>((_, reject) =>
      setTimeout(
        () => reject(new Error(errorMessage || `Action timed out after ${timeoutMs}ms`)),
        timeoutMs
      )
    ),
  ]);
}

// ============================================================================
// FORM HELPERS
// ============================================================================

/**
 * Fill entire form from data object
 */
export async function fillForm(
  page: Page,
  formData: Record<string, string>
): Promise<void> {
  for (const [field, value] of Object.entries(formData)) {
    // Try to find field by label, placeholder, or name
    const locator = await findElement(page, {
      label: new RegExp(field, 'i'),
      placeholder: new RegExp(field, 'i'),
    });

    await fillField(page, locator, value);
  }
}

/**
 * Submit form and wait for navigation
 */
export async function submitForm(
  page: Page,
  formSelector: string = 'form',
  expectedUrl?: string | RegExp
): Promise<void> {
  await page.locator(formSelector).locator('button[type="submit"]').click();

  if (expectedUrl) {
    await waitForUrl(page, expectedUrl);
  }
}

// ============================================================================
// MODAL/DIALOG HELPERS
// ============================================================================

/**
 * Wait for modal to open
 */
export async function waitForModal(
  page: Page,
  modalSelector: string = '[role="dialog"], .modal'
): Promise<void> {
  await waitForVisible(page, modalSelector);
}

/**
 * Close modal
 */
export async function closeModal(
  page: Page,
  closeButtonSelector: string = 'button:has-text("Close"), [aria-label="Close"]'
): Promise<void> {
  await clickElement(page, closeButtonSelector);
}

/**
 * Confirm modal action
 */
export async function confirmModal(
  page: Page,
  confirmButtonSelector: string = 'button:has-text("Confirm"), button:has-text("Yes"), button:has-text("OK")'
): Promise<void> {
  await clickElement(page, confirmButtonSelector);
}

// ============================================================================
// ACCESSIBILITY HELPERS
// ============================================================================

/**
 * Check for accessibility violations (requires axe-core)
 */
export async function checkAccessibility(page: Page): Promise<void> {
  // This requires @axe-core/playwright to be installed
  // npm install @axe-core/playwright
  try {
    const { injectAxe, checkA11y } = await import('@axe-core/playwright');
    await injectAxe(page);
    await checkA11y(page);
  } catch (error) {
    log('Accessibility check skipped (install @axe-core/playwright to enable)', 'warn');
  }
}

// ============================================================================
// EXPORT ALL
// ============================================================================

export const TestHelpers = {
  // Data generation
  generateEmail,
  generateUsername,
  generatePassword,
  generateTestData,
  generateRandomString,
  generateFutureDate,
  formatDateForInput,

  // Element interaction
  findElement,
  clickElement,
  fillField,
  selectOption,
  uploadFile,
  clearField,
  typeSlowly,

  // Waiting
  wait,
  waitForVisible,
  waitForHidden,
  waitForLoadingToComplete,
  waitForNetworkIdle,
  waitForUrl,
  waitForCondition,

  // Verification
  verifyVisible,
  verifyText,
  verifyUrl,
  verifyTitle,
  verifyElementCount,
  verifyElementText,
  verifyInputValue,
  verifyChecked,

  // Navigation
  navigateTo,
  goBack,
  goForward,
  reload,
  openNewTab,

  // Screenshot & logging
  takeScreenshot,
  log,
  logStep,

  // Backend/API
  apiRequest,
  getAuthToken,
  setAuthToken,
  clearStorage,

  // Retry & error handling
  retry,
  tryAction,
  withTimeout,

  // Forms
  fillForm,
  submitForm,

  // Modals
  waitForModal,
  closeModal,
  confirmModal,

  // Accessibility
  checkAccessibility,
};
