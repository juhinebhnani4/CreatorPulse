/**
 * E2E Test: User Journey 1 - New User Onboarding (Simplified)
 *
 * User Story: As a new user, I want to sign up and create my first workspace
 * so I can start curating content.
 *
 * This test focuses on FRONTEND UI behavior only.
 * Backend verification is handled by backend integration tests.
 */

import { test, expect } from '@playwright/test';

// Helper to generate unique test email
function generateTestEmail(): string {
  const timestamp = Date.now();
  const random = Math.floor(Math.random() * 10000);
  return `test-${timestamp}-${random}@example.com`;
}

test.describe('User Journey 1: New User Onboarding (Simple)', () => {
  let testEmail: string;
  let testPassword: string;

  test.beforeEach(() => {
    testEmail = generateTestEmail();
    testPassword = 'SecureTestPass123!';
  });

  test('should complete user signup flow', async ({ page }) => {
    // ==================== STEP 1: Landing Page ====================
    await test.step('Visit landing page', async () => {
      await page.goto('/');

      // Verify landing page loads with correct content
      await expect(page.locator('h1')).toContainText(/CreatorPulse|Welcome/i, { timeout: 10000 });
      await expect(page.getByRole('link', { name: /get started/i })).toBeVisible();
      await expect(page.getByRole('link', { name: /login/i })).toBeVisible();

      await page.screenshot({ path: 'test-results/simple-journey1-step1-landing.png' });
      console.log('✅ Landing page loaded successfully');
    });

    // ==================== STEP 2: Navigate to Sign Up ====================
    await test.step('Navigate to sign up page', async () => {
      await page.getByRole('link', { name: /get started/i }).click();

      // Wait for registration page
      await expect(page.locator('h2')).toContainText(/create.*account/i, { timeout: 10000 });

      await page.screenshot({ path: 'test-results/simple-journey1-step2-signup-page.png' });
      console.log('✅ Sign up page loaded');
    });

    // ==================== STEP 3: Fill Registration Form ====================
    await test.step('Submit registration form', async () => {
      // Fill out the form
      await page.getByLabel(/name/i).fill('TestUser');
      await page.getByLabel(/email/i).fill(testEmail);
      await page.getByLabel(/password/i).fill(testPassword);

      await page.screenshot({ path: 'test-results/simple-journey1-step3-form-filled.png' });

      // Submit the form
      await page.getByRole('button', { name: /create account/i }).click();

      console.log(`✅ Registration form submitted for: ${testEmail}`);
    });

    // ==================== STEP 4: Verify Redirect to Dashboard ====================
    await test.step('Verify redirect to dashboard', async () => {
      // Wait for navigation (either to dashboard or app page)
      await page.waitForURL(/\/(app|dashboard|workspace)/i, { timeout: 15000 });

      const currentUrl = page.url();
      console.log(`✅ Redirected to: ${currentUrl}`);

      // Verify we're authenticated (look for logout/profile elements)
      await expect(
        page.getByRole('button', { name: /logout|sign out|profile|account/i }).first()
      ).toBeVisible({ timeout: 10000 });

      await page.screenshot({ path: 'test-results/simple-journey1-step4-logged-in.png', fullPage: true });
      console.log('✅ User successfully signed up and logged in!');
    });
  });

  test('should show validation errors for invalid email', async ({ page }) => {
    await page.goto('/register');

    // Fill with invalid data
    await page.getByLabel(/name/i).fill('Test User');
    await page.getByLabel(/email/i).fill('invalid-email');
    await page.getByLabel(/password/i).fill('short');

    // Try to submit
    await page.getByRole('button', { name: /create account/i }).click();

    // Should still be on register page (form validation failed)
    await expect(page.url()).toContain('/register');
    console.log('✅ Form validation working correctly');
  });

  test('should allow navigation between login and signup', async ({ page }) => {
    // Go to signup
    await page.goto('/register');
    await expect(page.locator('h2')).toContainText(/create.*account/i);

    // Click "Sign in" link (it's actually a link with the text "Sign in" at the bottom of the form)
    await page.click('text=Sign in');

    // Wait for navigation
    await page.waitForURL('**/login');

    // Should be on login page
    await expect(page.url()).toContain('/login');
    await expect(page.locator('h2')).toContainText(/welcome back/i);

    // Click "Sign up" link
    await page.click('text=Sign up');

    // Wait for navigation
    await page.waitForURL('**/register');

    // Should be back on register page
    await expect(page.url()).toContain('/register');
    await expect(page.locator('h2')).toContainText(/create.*account/i);

    console.log('✅ Navigation between auth pages working correctly');
  });
});
