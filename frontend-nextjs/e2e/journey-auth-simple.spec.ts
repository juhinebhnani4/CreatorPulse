/**
 * E2E Test: Simple Auth Flow with Existing User
 *
 * Tests authentication using existing user credentials:
 * - Email: juhinebhnani4@gmail.com
 * - Password: 12345678
 *
 * Tests:
 * 1. Login with remember me
 * 2. Forgot password flow
 * 3. Design preservation
 */

import { test, expect } from './fixtures/playwright-fixtures';

test.describe('Auth Flow - Existing User', () => {
  const testEmail = 'juhinebhnani4@gmail.com';
  const testPassword = '12345678';

  test.beforeEach(async ({ page }) => {
    // Clear localStorage before each test
    await page.goto('/');
    await page.evaluate(() => localStorage.clear());
  });

  test('should login with remember me enabled', async ({ page }) => {
    await test.step('Navigate to login page', async () => {
      await page.goto('/login');
      await expect(page).toHaveURL('/login');
      console.log('✓ On login page');
    });

    await test.step('Fill login form with remember me', async () => {
      // Fill email
      await page.fill('[data-testid="email-input"]', testEmail);

      // Fill password
      await page.fill('[data-testid="password-input"]', testPassword);

      // Check Remember Me checkbox
      const rememberMeCheckbox = page.locator('[data-testid="remember-me-checkbox"]');
      await expect(rememberMeCheckbox).toBeVisible();
      await rememberMeCheckbox.click();

      console.log('✓ Form filled with remember me checked');
    });

    await test.step('Submit login and verify success', async () => {
      await page.click('[data-testid="login-button"]');

      // Wait for redirect to dashboard
      await expect(page).toHaveURL('/app', { timeout: 10000 });
      console.log('✓ Login successful, redirected to dashboard');
    });

    await test.step('Verify Remember Me data saved to localStorage', async () => {
      const rememberMe = await page.evaluate(() => localStorage.getItem('rememberMe'));
      const savedEmail = await page.evaluate(() => localStorage.getItem('userEmail'));

      expect(rememberMe).toBe('true');
      expect(savedEmail).toBe(testEmail);

      console.log('✓ Remember Me data saved to localStorage');
      console.log(`  - rememberMe: ${rememberMe}`);
      console.log(`  - userEmail: ${savedEmail}`);
    });

    await test.step('Verify Remember Me persists after page reload', async () => {
      await page.reload();
      await page.waitForTimeout(1000);

      // Should still be logged in
      await expect(page).toHaveURL('/app');

      // Remember Me data should still be there
      const rememberMe = await page.evaluate(() => localStorage.getItem('rememberMe'));
      const savedEmail = await page.evaluate(() => localStorage.getItem('userEmail'));

      expect(rememberMe).toBe('true');
      expect(savedEmail).toBe(testEmail);

      console.log('✓ Remember Me data persisted after reload');
    });
  });

  test('should NOT save Remember Me when unchecked', async ({ page }) => {
    await test.step('Navigate to login and fill form WITHOUT remember me', async () => {
      await page.goto('/login');

      await page.fill('[data-testid="email-input"]', testEmail);
      await page.fill('[data-testid="password-input"]', testPassword);

      // Verify Remember Me is NOT checked (default state)
      const isChecked = await page.locator('[data-testid="remember-me-checkbox"]').isChecked();
      expect(isChecked).toBe(false);

      console.log('✓ Remember Me checkbox unchecked (default)');
    });

    await test.step('Login and verify no localStorage data', async () => {
      await page.click('[data-testid="login-button"]');
      await expect(page).toHaveURL('/app', { timeout: 10000 });

      const rememberMe = await page.evaluate(() => localStorage.getItem('rememberMe'));
      const savedEmail = await page.evaluate(() => localStorage.getItem('userEmail'));

      expect(rememberMe).toBeNull();
      expect(savedEmail).toBeNull();

      console.log('✓ Remember Me data NOT saved (as expected)');
    });
  });

  test('should navigate to forgot password page', async ({ page }) => {
    await test.step('Navigate to login page', async () => {
      await page.goto('/login');
      console.log('✓ On login page');
    });

    await test.step('Click forgot password link', async () => {
      const forgotPasswordLink = page.locator('[data-testid="forgot-password-link"]');
      await expect(forgotPasswordLink).toBeVisible();
      await expect(forgotPasswordLink).toHaveText('Forgot password?');

      await forgotPasswordLink.click();

      await expect(page).toHaveURL('/forgot-password', { timeout: 5000 });
      console.log('✓ Navigated to forgot password page');
    });

    await test.step('Verify forgot password page elements', async () => {
      // Check heading (actual text is "Reset your password")
      const heading = page.locator('h2');
      await expect(heading).toBeVisible();
      const headingText = await heading.textContent();
      console.log(`✓ Heading found: "${headingText}"`);

      // Check description
      const description = page.locator('[data-testid="forgot-password-description"]');
      await expect(description).toBeVisible();

      // Check email input
      const emailInput = page.locator('[data-testid="forgot-password-email"]');
      await expect(emailInput).toBeVisible();

      // Check submit button
      const submitButton = page.locator('[data-testid="forgot-password-submit"]');
      await expect(submitButton).toBeVisible();

      console.log('✓ All forgot password page elements present');
    });

    await test.step('Submit forgot password email', async () => {
      await page.fill('[data-testid="forgot-password-email"]', testEmail);
      await page.click('[data-testid="forgot-password-submit"]');

      // Wait for success message
      await expect(page.locator('[data-testid="reset-email-sent-message"]')).toBeVisible({ timeout: 5000 });

      console.log('✓ Password reset email submitted');

      const successMessage = await page.locator('[data-testid="reset-email-sent-message"]').textContent();
      console.log(`✓ Success message: ${successMessage}`);
    });

    await test.step('Navigate back to login', async () => {
      const backToLoginLink = page.locator('[data-testid="back-to-login-link"]');
      await expect(backToLoginLink).toBeVisible();
      await backToLoginLink.click();

      await expect(page).toHaveURL('/login', { timeout: 5000 });
      console.log('✓ Navigated back to login page');
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

  test('should preserve login page design aesthetic', async ({ page }) => {
    await page.goto('/login');

    await test.step('Verify login form card exists', async () => {
      const loginForm = await page.$('[data-testid="login-form"]');
      expect(loginForm).not.toBeNull();
      console.log('✓ Login form found');
    });

    await test.step('Verify logo and branding', async () => {
      // Check for CreatorPulse branding
      const branding = await page.$('text=CreatorPulse');
      expect(branding).not.toBeNull();
      console.log('✓ CreatorPulse branding present');
    });

    await test.step('Verify Remember Me and Forgot Password elements', async () => {
      // Remember Me checkbox
      const rememberMeCheckbox = await page.$('[data-testid="remember-me-checkbox"]');
      expect(rememberMeCheckbox).not.toBeNull();

      const rememberMeLabel = await page.$('label[for="remember-me"]');
      expect(rememberMeLabel).not.toBeNull();

      const labelClasses = await rememberMeLabel!.getAttribute('class');
      expect(labelClasses).toContain('text-sm');
      expect(labelClasses).toContain('font-medium');

      // Forgot Password link
      const forgotPasswordLink = await page.$('[data-testid="forgot-password-link"]');
      expect(forgotPasswordLink).not.toBeNull();

      const linkClasses = await forgotPasswordLink!.getAttribute('class');
      expect(linkClasses).toContain('text-primary');
      expect(linkClasses).toContain('hover:underline');

      console.log('✓ Remember Me and Forgot Password styling preserved');
    });

    await test.step('Verify button styling', async () => {
      const loginButton = await page.$('[data-testid="login-button"]');
      expect(loginButton).not.toBeNull();

      const buttonClasses = await loginButton!.getAttribute('class');
      expect(buttonClasses).toContain('w-full');

      console.log('✓ Button styling preserved');
    });
  });

  test('should preserve forgot password page design', async ({ page }) => {
    await page.goto('/forgot-password');

    await test.step('Verify page layout', async () => {
      // Should have container with proper layout
      const container = await page.$('.min-h-screen');
      expect(container).not.toBeNull();

      const containerClasses = await container!.getAttribute('class');
      expect(containerClasses).toContain('flex');
      expect(containerClasses).toContain('items-center');
      expect(containerClasses).toContain('justify-center');

      console.log('✓ Forgot password page layout preserved');
    });

    await test.step('Verify branding', async () => {
      const branding = await page.$('text=CreatorPulse');
      expect(branding).not.toBeNull();
      console.log('✓ CreatorPulse branding present');
    });

    await test.step('Verify submit button styling', async () => {
      const submitButton = await page.$('[data-testid="forgot-password-submit"]');
      expect(submitButton).not.toBeNull();

      const buttonClasses = await submitButton!.getAttribute('class');
      expect(buttonClasses).toContain('w-full');

      console.log('✓ Submit button styling preserved');
    });
  });
});
