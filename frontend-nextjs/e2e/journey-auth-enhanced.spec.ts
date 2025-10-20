/**
 * E2E Test: Enhanced Auth Flow (Login + Forgot Password)
 *
 * Tests complete authentication journey:
 * 1. Login with email/password
 * 2. Remember Me checkbox functionality
 * 3. Forgot Password link navigation
 * 4. Password reset email submission
 * 5. LocalStorage persistence for Remember Me
 * 6. Database verification of user sessions
 *
 * Critical: Tests auth UX enhancements (remember me, forgot password)
 */

import { test, expect } from './fixtures/playwright-fixtures';
import { generateTestEmail, wait } from './fixtures/test-data';

test.describe('Enhanced Auth Flow - Login & Password Reset', () => {
  let testEmail: string;
  let testPassword: string;
  let userId: string;

  test.beforeEach(async ({ page }) => {
    // Generate test credentials
    testEmail = generateTestEmail('auth-enhanced-test');
    testPassword = 'SecureTestPass123!';

    // Clear localStorage before each test
    await page.goto('/');
    await page.evaluate(() => localStorage.clear());
  });

  test.afterEach(async ({ supabase }) => {
    // Cleanup test data
    if (userId) {
      console.log(`[Cleanup] Removing test user: ${testEmail}`);
      await supabase.cleanupTestUser(userId);
    }
  });

  test('should register and login with remember me enabled', async ({ page, supabase }) => {
    await test.step('Register new test user', async () => {
      await page.goto('/register');
      await page.fill('[data-testid="name-input"]', 'Test User');
      await page.fill('input[type="email"]', testEmail);
      await page.fill('input[type="password"]', testPassword);
      await page.click('button[type="submit"]');

      // Wait for redirect to dashboard
      await expect(page).toHaveURL('/app', { timeout: 10000 });

      // Get user ID from database
      const user = await supabase.verifyUserExists(testEmail);
      expect(user).not.toBeNull();
      userId = user!.id;
      console.log(`✓ Test user created: ${testEmail} (${userId})`);
    });

    await test.step('Logout and navigate to login page', async () => {
      // Click logout button
      await page.click('[data-testid="user-menu-trigger"]');
      await page.click('[data-testid="logout-button"]');

      // Should redirect to login
      await expect(page).toHaveURL('/login', { timeout: 5000 });
      console.log('✓ Logged out successfully');
    });

    await test.step('Login with Remember Me enabled', async () => {
      // Fill login form
      await page.fill('[data-testid="email-input"]', testEmail);
      await page.fill('[data-testid="password-input"]', testPassword);

      // Check Remember Me checkbox
      const rememberMeCheckbox = page.locator('[data-testid="remember-me-checkbox"]');
      await expect(rememberMeCheckbox).toBeVisible();
      await rememberMeCheckbox.click();

      console.log('✓ Remember Me checkbox checked');

      // Submit login form
      await page.click('[data-testid="login-button"]');

      // Wait for redirect to dashboard
      await expect(page).toHaveURL('/app', { timeout: 10000 });
      console.log('✓ Login successful');
    });

    await test.step('Verify Remember Me data in localStorage', async () => {
      // Get localStorage data
      const rememberMe = await page.evaluate(() => localStorage.getItem('rememberMe'));
      const savedEmail = await page.evaluate(() => localStorage.getItem('userEmail'));

      // Verify values
      expect(rememberMe).toBe('true');
      expect(savedEmail).toBe(testEmail);

      console.log('✓ Remember Me data saved to localStorage');
      console.log(`  - rememberMe: ${rememberMe}`);
      console.log(`  - userEmail: ${savedEmail}`);
    });

    await test.step('Verify Remember Me persists after page reload', async () => {
      // Reload the page
      await page.reload();
      await wait(1000);

      // Should still be logged in (token in localStorage)
      await expect(page).toHaveURL('/app');

      // Remember Me data should still be there
      const rememberMe = await page.evaluate(() => localStorage.getItem('rememberMe'));
      const savedEmail = await page.evaluate(() => localStorage.getItem('userEmail'));

      expect(rememberMe).toBe('true');
      expect(savedEmail).toBe(testEmail);

      console.log('✓ Remember Me data persisted after reload');
    });
  });

  test('should NOT save Remember Me data when unchecked', async ({ page, supabase }) => {
    await test.step('Register new test user', async () => {
      await page.goto('/register');
      await page.fill('[data-testid="name-input"]', 'Test User No Remember');
      await page.fill('input[type="email"]', testEmail);
      await page.fill('input[type="password"]', testPassword);
      await page.click('button[type="submit"]');

      await expect(page).toHaveURL('/app', { timeout: 10000 });

      const user = await supabase.verifyUserExists(testEmail);
      userId = user!.id;
      console.log(`✓ Test user created: ${testEmail}`);
    });

    await test.step('Logout', async () => {
      await page.click('[data-testid="user-menu-trigger"]');
      await page.click('[data-testid="logout-button"]');
      await expect(page).toHaveURL('/login');
    });

    await test.step('Login WITHOUT Remember Me', async () => {
      await page.fill('[data-testid="email-input"]', testEmail);
      await page.fill('[data-testid="password-input"]', testPassword);

      // Verify Remember Me checkbox is NOT checked
      const isChecked = await page.locator('[data-testid="remember-me-checkbox"]').isChecked();
      expect(isChecked).toBe(false);

      console.log('✓ Remember Me checkbox is unchecked (default)');

      // Submit login form
      await page.click('[data-testid="login-button"]');
      await expect(page).toHaveURL('/app', { timeout: 10000 });
    });

    await test.step('Verify Remember Me data NOT in localStorage', async () => {
      const rememberMe = await page.evaluate(() => localStorage.getItem('rememberMe'));
      const savedEmail = await page.evaluate(() => localStorage.getItem('userEmail'));

      // Should be null or removed
      expect(rememberMe).toBeNull();
      expect(savedEmail).toBeNull();

      console.log('✓ Remember Me data NOT saved (as expected)');
    });
  });

  test('should navigate to Forgot Password page and submit email', async ({ page }) => {
    await test.step('Navigate to Login page', async () => {
      await page.goto('/login');
      await expect(page).toHaveURL('/login');
      console.log('✓ On login page');
    });

    await test.step('Click Forgot Password link', async () => {
      const forgotPasswordLink = page.locator('[data-testid="forgot-password-link"]');
      await expect(forgotPasswordLink).toBeVisible();
      await expect(forgotPasswordLink).toHaveText('Forgot password?');

      await forgotPasswordLink.click();

      // Should navigate to forgot password page
      await expect(page).toHaveURL('/forgot-password', { timeout: 5000 });
      console.log('✓ Navigated to forgot password page');
    });

    await test.step('Verify Forgot Password page elements', async () => {
      // Should have heading
      await expect(page.locator('h2')).toContainText('Reset Password');

      // Should have description
      const description = page.locator('[data-testid="forgot-password-description"]');
      await expect(description).toBeVisible();

      // Should have email input
      const emailInput = page.locator('[data-testid="forgot-password-email"]');
      await expect(emailInput).toBeVisible();

      // Should have submit button
      const submitButton = page.locator('[data-testid="forgot-password-submit"]');
      await expect(submitButton).toBeVisible();

      console.log('✓ All forgot password page elements present');
    });

    await test.step('Submit forgot password email', async () => {
      const testResetEmail = generateTestEmail('password-reset-test');

      // Fill email
      await page.fill('[data-testid="forgot-password-email"]', testResetEmail);

      // Submit form
      await page.click('[data-testid="forgot-password-submit"]');

      // Wait for success message
      await expect(page.locator('[data-testid="reset-email-sent-message"]')).toBeVisible({ timeout: 5000 });

      console.log('✓ Password reset email submitted');
      console.log(`  - Email: ${testResetEmail}`);

      // Should show success state
      const successMessage = await page.locator('[data-testid="reset-email-sent-message"]').textContent();
      expect(successMessage).toContain('Check your email');

      console.log('✓ Success message displayed');
    });

    await test.step('Navigate back to login from success state', async () => {
      // Click back to login link
      const backToLoginLink = page.locator('[data-testid="back-to-login-link"]');
      await expect(backToLoginLink).toBeVisible();
      await backToLoginLink.click();

      // Should navigate back to login
      await expect(page).toHaveURL('/login', { timeout: 5000 });
      console.log('✓ Navigated back to login page');
    });
  });

  test('should preserve login page design aesthetic', async ({ page }) => {
    await page.goto('/login');

    await test.step('Verify gradient branding preserved', async () => {
      // Check logo exists
      const logo = await page.$('div:has-text("CP")');
      expect(logo).not.toBeNull();

      const logoClasses = await logo!.getAttribute('class');
      expect(logoClasses).toContain('bg-primary');
      expect(logoClasses).toContain('rounded-lg');

      console.log('✓ Logo gradient and styling preserved');
    });

    await test.step('Verify form card styling preserved', async () => {
      const form = await page.$('[data-testid="login-form"]');
      expect(form).not.toBeNull();

      // Card should have proper styling
      const card = await page.$('.min-h-screen');
      expect(card).not.toBeNull();

      const cardClasses = await card!.getAttribute('class');
      expect(cardClasses).toContain('bg-muted/20');

      console.log('✓ Card background styling preserved');
    });

    await test.step('Verify button styling preserved', async () => {
      const loginButton = await page.$('[data-testid="login-button"]');
      expect(loginButton).not.toBeNull();

      const buttonClasses = await loginButton!.getAttribute('class');
      expect(buttonClasses).toContain('w-full');

      // Get computed styles
      const bgColor = await loginButton!.evaluate((el) => window.getComputedStyle(el).backgroundColor);

      // Should have styling (not default)
      expect(bgColor).not.toBe('rgba(0, 0, 0, 0)');
      expect(bgColor).not.toBe('');

      console.log('✓ Button styling preserved');
    });

    await test.step('Verify Remember Me and Forgot Password styling', async () => {
      // Remember Me checkbox should have proper label styling
      const rememberMeLabel = await page.$('label[for="remember-me"]');
      expect(rememberMeLabel).not.toBeNull();

      const labelClasses = await rememberMeLabel!.getAttribute('class');
      expect(labelClasses).toContain('text-sm');
      expect(labelClasses).toContain('font-medium');

      // Forgot Password link should have primary color
      const forgotPasswordLink = await page.$('[data-testid="forgot-password-link"]');
      const linkClasses = await forgotPasswordLink!.getAttribute('class');
      expect(linkClasses).toContain('text-primary');
      expect(linkClasses).toContain('hover:underline');

      console.log('✓ Remember Me and Forgot Password styling preserved');
    });

    await test.step('Verify no CSS breaking changes from test IDs', async () => {
      // Test IDs should be invisible (data attributes only)
      const emailInput = await page.$('[data-testid="email-input"]');

      // Get computed styles
      const padding = await emailInput!.evaluate((el) => window.getComputedStyle(el).padding);
      const borderRadius = await emailInput!.evaluate((el) => window.getComputedStyle(el).borderRadius);

      // Should have styling
      expect(padding).not.toBe('0px');
      expect(borderRadius).not.toBe('0px');

      console.log('✓ No CSS breaking changes detected');
    });
  });

  test('should show login error for invalid credentials', async ({ page }) => {
    await page.goto('/login');

    await test.step('Submit invalid credentials', async () => {
      await page.fill('[data-testid="email-input"]', 'nonexistent@example.com');
      await page.fill('[data-testid="password-input"]', 'wrongpassword');
      await page.click('[data-testid="login-button"]');

      // Wait for error message
      const errorMessage = page.locator('[data-testid="login-error"]');
      await expect(errorMessage).toBeVisible({ timeout: 5000 });

      const errorText = await errorMessage.textContent();
      expect(errorText).toBeTruthy();

      console.log('✓ Login error message displayed');
      console.log(`  - Error: ${errorText}`);
    });

    await test.step('Verify error styling', async () => {
      const errorMessage = await page.$('[data-testid="login-error"]');

      const errorClasses = await errorMessage!.getAttribute('class');
      expect(errorClasses).toContain('text-destructive');
      expect(errorClasses).toContain('bg-destructive/10');

      console.log('✓ Error styling preserved');
    });
  });

  test('should preserve forgot password page design aesthetic', async ({ page }) => {
    await page.goto('/forgot-password');

    await test.step('Verify page layout and branding', async () => {
      // Should have logo
      const logo = await page.$('div:has-text("CP")');
      expect(logo).not.toBeNull();

      // Should have centered card layout
      const container = await page.$('.min-h-screen');
      expect(container).not.toBeNull();

      const containerClasses = await container!.getAttribute('class');
      expect(containerClasses).toContain('flex');
      expect(containerClasses).toContain('items-center');
      expect(containerClasses).toContain('justify-center');

      console.log('✓ Forgot password page layout preserved');
    });

    await test.step('Verify form card styling', async () => {
      const card = await page.$('[data-testid="forgot-password-card"]');
      expect(card).not.toBeNull();

      // Should have card styling
      const cardClasses = await card!.getAttribute('class');
      expect(cardClasses).toBeTruthy();

      console.log('✓ Forgot password card styling preserved');
    });

    await test.step('Verify submit button gradient', async () => {
      const submitButton = await page.$('[data-testid="forgot-password-submit"]');
      expect(submitButton).not.toBeNull();

      const buttonClasses = await submitButton!.getAttribute('class');
      expect(buttonClasses).toContain('w-full');

      // Get background color
      const bgColor = await submitButton!.evaluate((el) => window.getComputedStyle(el).backgroundColor);
      expect(bgColor).not.toBe('rgba(0, 0, 0, 0)');

      console.log('✓ Submit button styling preserved');
    });
  });
});
