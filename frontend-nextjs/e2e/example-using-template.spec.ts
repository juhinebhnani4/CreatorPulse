/**
 * EXAMPLE: Using the Universal Templates
 *
 * This file demonstrates how to use the universal templates in real tests.
 * Copy this file and modify it for your own tests!
 *
 * To run: npm run test:e2e example-using-template
 */

import { test, expect } from '@playwright/test';

// ============================================================================
// APPROACH 1: Using Individual Helper Functions
// ============================================================================

import {
  generateTestData,
  navigateTo,
  clickElement,
  fillField,
  waitForUrl,
  verifyText,
  takeScreenshot,
  log,
} from './templates/test-helpers';

test.describe('Approach 1: Using Helper Functions', () => {
  test('should complete user registration using helpers', async ({ page }) => {
    // Generate unique test data
    const testData = generateTestData('helper-test');
    log(`Test data generated: ${testData.email}`);

    // Step 1: Navigate to landing page
    await navigateTo(page, '/');
    await takeScreenshot(page, 'landing-page');

    // Step 2: Click Get Started
    await clickElement(page, { role: 'link', name: /get started/i });

    // Step 3: Wait for registration page
    await waitForUrl(page, /register|signup/i);
    await takeScreenshot(page, 'registration-page');

    // Step 4: Fill registration form
    await fillField(page, { label: /name/i }, 'Test User');
    await fillField(page, { label: /email/i }, testData.email);
    await fillField(page, { label: /password/i }, testData.password);

    // Step 5: Submit
    await clickElement(page, { role: 'button', name: /create account/i });

    // Step 6: Verify success
    await waitForUrl(page, /app|dashboard/i, 15000);
    await verifyText(page, /welcome/i);

    log('✅ Registration completed successfully!');
  });
});

// ============================================================================
// APPROACH 2: Using Page Object Model
// ============================================================================

import { BasePage, AuthPage, DashboardPage } from './templates/page-object-template';

test.describe('Approach 2: Using Page Objects', () => {
  test('should login using page objects', async ({ page }) => {
    // Initialize page objects
    const authPage = new AuthPage(page, true); // true = login page

    // Navigate and login
    await authPage.goto(); // baseUrl is already set to /login in constructor
    await authPage.verifyLoginPage();

    await authPage.loginAndWait('juhinebhnani4@gmail.com', '12345678');

    // Verify on dashboard
    await expect(page).toHaveURL(/app|dashboard/i);

    console.log('✅ Login completed with Page Objects!');
  });
});

// ============================================================================
// APPROACH 3: Using Config-Driven Tests
// ============================================================================

import { createTestFromConfig, TestJourneyConfig } from './templates/journey-config-template';

// Define journey as a configuration object
const loginJourney: TestJourneyConfig = {
  name: 'Login Journey (Config-Driven)',
  description: 'Tests user login flow using configuration',
  timeout: 30000,
  steps: [
    {
      name: 'Navigate to login page',
      action: 'navigate',
      url: '/login',
    },
    {
      name: 'Fill email',
      action: 'fill',
      selector: { label: /email/i },
      value: 'test@example.com',
    },
    {
      name: 'Fill password',
      action: 'fill',
      selector: { label: /password/i },
      value: 'password123',
    },
    {
      name: 'Click login button',
      action: 'click',
      selector: { role: 'button', name: /sign in|login/i },
    },
    {
      name: 'Wait for dashboard',
      action: 'wait_for_navigation',
      urlPattern: 'app|dashboard',
      timeout: 15000,
    },
    {
      name: 'Verify logged in',
      action: 'verify_visible',
      selector: { role: 'button', name: /profile|logout/i },
    },
  ],
};

// Create test from config
createTestFromConfig(loginJourney);

// ============================================================================
// APPROACH 4: Hybrid Approach (Best of All Worlds)
// ============================================================================

test.describe('Approach 4: Hybrid (Recommended)', () => {
  test('should create and verify item using hybrid approach', async ({ page }) => {
    // Use helpers for common tasks
    const testData = generateTestData('hybrid');
    log('Starting hybrid test');

    // Login first with existing credentials
    await navigateTo(page, '/login');
    await fillField(page, { label: /email/i }, 'juhinebhnani4@gmail.com');
    await fillField(page, { label: /password/i }, '12345678');
    await clickElement(page, { role: 'button', name: /sign in/i });

    // Wait for redirect to dashboard
    await waitForUrl(page, /\/app/);

    // Use page object for complex interactions
    const dashboardPage = new DashboardPage(page);
    await dashboardPage.verifyDashboardLoaded();

    // Verify we're on the dashboard
    await verifyText(page, /Welcome back/i);

    // Take screenshot of dashboard
    await takeScreenshot(page, 'dashboard-loaded');

    // Verify navigation works - click on Content section
    await clickElement(page, { role: 'button', name: /Content/i });

    log('✅ Hybrid test completed - Dashboard verified!');
  });
});

// ============================================================================
// REAL-WORLD EXAMPLE: Complete User Journey
// ============================================================================

test.describe('Real-World Example: Complete Newsletter Creation Flow', () => {
  let testData: ReturnType<typeof generateTestData>;

  test.beforeEach(() => {
    testData = generateTestData('newsletter');
  });

  test('should create newsletter from signup to sending', async ({ page }) => {
    log('=== PHASE 1: User Registration ===');

    // 1. Register new user
    await navigateTo(page, '/register');
    await fillField(page, { label: /name/i }, 'Newsletter Creator');
    await fillField(page, { label: /email/i }, testData.email);
    await fillField(page, { label: /password/i }, testData.password);
    await clickElement(page, { role: 'button', name: /create account/i });

    await waitForUrl(page, /app/i);
    log('✓ User registered');

    log('=== PHASE 2: Add Content Sources ===');

    // 2. Add RSS source
    await clickElement(page, { role: 'button', name: /add source/i });
    await fillField(page, { label: /name/i }, 'TechCrunch AI');
    await fillField(page, { label: /url/i }, 'https://techcrunch.com/feed/');
    await clickElement(page, { role: 'button', name: /save|add/i });

    await verifyText(page, /techcrunch/i);
    log('✓ Content source added');

    log('=== PHASE 3: Generate Newsletter ===');

    // 3. Generate newsletter
    await clickElement(page, { role: 'button', name: /generate newsletter/i });

    // Wait for generation (async operation)
    await waitForUrl(page, /generating|processing/i, 30000);
    await verifyText(page, /complete|ready/i);

    await takeScreenshot(page, 'newsletter-generated');
    log('✓ Newsletter generated');

    log('=== PHASE 4: Send Newsletter ===');

    // 4. Send newsletter
    await clickElement(page, { role: 'button', name: /send now/i });

    // Confirm send modal
    await clickElement(page, { role: 'button', name: /confirm|send/i });

    await verifyText(page, /sent successfully/i);
    log('✓ Newsletter sent');

    log('✅ Complete journey finished successfully!');
  });
});

// ============================================================================
// EXAMPLE: Testing New/Unknown Page
// ============================================================================

test.describe('Example: Testing Unknown Page Structure', () => {
  test('should work even if page structure is unknown', async ({ page }) => {
    // Navigate with flexible verification
    await navigateTo(page, '/new-feature');

    // Wait for any heading
    await expect(page.locator('h1, h2, h3').first()).toBeVisible();
    await takeScreenshot(page, 'unknown-page');

    // Try to find and click primary action (flexible selector)
    try {
      await clickElement(
        page,
        {
          role: 'button',
          name: /continue|next|submit|start|begin/i,
          text: /continue|next|submit|start|begin/i,
          css: 'button[type="submit"], .primary-button, .btn-primary',
        },
        'Primary action button',
      );

      log('✓ Found and clicked primary action');
    } catch (error) {
      log('⚠ No primary action button found, skipping', 'warn');
    }

    // Verify some success indication
    const hasSuccess = await page.getByText(/success|complete|done/i).isVisible();
    if (hasSuccess) {
      log('✓ Success message found');
    } else {
      log('⚠ No success message, checking URL instead', 'warn');
      // Verify navigation occurred
      expect(page.url()).not.toContain('/new-feature');
    }
  });
});

// ============================================================================
// EXAMPLE: Data-Driven Testing
// ============================================================================

test.describe('Example: Data-Driven Testing', () => {
  const testCases = [
    { name: 'Alice', email: 'alice@example.com', expectedGreeting: 'Welcome Alice' },
    { name: 'Bob', email: 'bob@example.com', expectedGreeting: 'Welcome Bob' },
    { name: 'Charlie', email: 'charlie@example.com', expectedGreeting: 'Welcome Charlie' },
  ];

  for (const testCase of testCases) {
    test(`should register ${testCase.name}`, async ({ page }) => {
      await navigateTo(page, '/register');

      await fillField(page, { label: /name/i }, testCase.name);
      await fillField(page, { label: /email/i }, testCase.email);
      await fillField(page, { label: /password/i }, 'TestPass123!');

      await clickElement(page, { role: 'button', name: /create/i });

      await verifyText(page, new RegExp(testCase.expectedGreeting, 'i'));
      log(`✓ ${testCase.name} registered successfully`);
    });
  }
});
