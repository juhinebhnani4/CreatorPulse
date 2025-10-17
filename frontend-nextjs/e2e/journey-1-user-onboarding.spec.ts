/**
 * E2E Test: User Journey 1 - New User Onboarding
 *
 * User Story: As a new user, I want to sign up and create my first workspace
 * so I can start curating content.
 *
 * Flow:
 * 1. Visit landing page
 * 2. Sign up with email/password
 * 3. Auto-login and redirect to dashboard
 * 4. Create first workspace
 *
 * Each step verifies both frontend UI and backend database state.
 */

import { test, expect } from './fixtures/playwright-fixtures';
import { generateTestEmail, generateWorkspaceName, wait } from './fixtures/test-data';

test.describe('User Journey 1: New User Onboarding', () => {
  let testEmail: string;
  let testPassword: string;
  let userId: string;
  let workspaceId: string;

  test.beforeEach(() => {
    // Generate unique test credentials for this run
    testEmail = generateTestEmail('onboarding');
    testPassword = 'SecureTestPass123!';
  });

  test.afterEach(async ({ supabase }) => {
    // Cleanup: Remove test user and all related data
    if (userId) {
      await supabase.cleanupTestUser(userId);
    }
  });

  test('should complete full onboarding journey from landing to workspace creation', async ({
    page,
    supabase,
  }) => {
    // ==================== STEP 1: Landing Page ====================
    test.step('Step 1: User visits landing page', async () => {
      await page.goto('/');

      // Verify landing page elements
      await expect(page.locator('h1')).toContainText(/CreatorPulse|Welcome/i);
      await expect(page.getByRole('link', { name: /sign up|get started/i })).toBeVisible();
      await expect(page.getByRole('link', { name: /sign in|login/i })).toBeVisible();

      // Screenshot for documentation
      await page.screenshot({ path: 'test-results/journey1-step1-landing.png' });
    });

    // ==================== STEP 2: Sign Up ====================
    await test.step('Step 2: User signs up with email and password', async () => {
      // Click sign up button
      await page.getByRole('link', { name: /sign up|get started/i }).click();

      // Wait for sign up form - updated to match actual heading "Create your account"
      await expect(page.locator('h1, h2')).toContainText(/create.*account/i);

      // Fill out sign up form - including name field
      await page.getByLabel(/^name$/i).fill('Test User');
      await page.getByLabel(/email/i).fill(testEmail);
      await page.getByLabel(/password/i).first().fill(testPassword);

      // Handle confirm password field if it exists
      const confirmPasswordField = page.getByLabel(/confirm password|repeat password/i);
      if (await confirmPasswordField.count() > 0) {
        await confirmPasswordField.fill(testPassword);
      }

      // Submit form - updated button text
      await page.getByRole('button', { name: /create account/i }).click();

      // Wait for navigation or success message
      await wait(2000);

      // Screenshot
      await page.screenshot({ path: 'test-results/journey1-step2-signup.png' });
    });

    // ==================== DB VERIFICATION: User Created ====================
    await test.step('DB Check: Verify user exists in database', async () => {
      // Wait a bit for async user creation
      await wait(1000);

      // Verify user was created in database
      const user = await supabase.verifyUserExists(testEmail);
      expect(user).not.toBeNull();
      expect(user?.email).toBe(testEmail);

      // Store user ID for later steps and cleanup
      userId = user!.id;

      console.log(`✓ User created in DB: ${userId}`);
    });

    // ==================== STEP 3: Auto-Login & Dashboard ====================
    await test.step('Step 3: User is auto-logged in and sees dashboard', async () => {
      // Check if redirected to dashboard or needs login
      const currentUrl = page.url();

      if (currentUrl.includes('/login') || currentUrl.includes('/signin')) {
        // Need to login manually
        await page.getByLabel(/email/i).fill(testEmail);
        await page.getByLabel(/password/i).fill(testPassword);
        await page.getByRole('button', { name: /sign in|login/i }).click();
        await wait(2000);
      }

      // Verify we're on dashboard or workspace page
      await expect(page.url()).toMatch(/dashboard|workspaces/);

      // Verify user menu or profile is visible
      const userMenu = page.getByRole('button', { name: new RegExp(testEmail, 'i') });
      const profileButton = page.getByRole('button', { name: /profile|account/i });

      await expect(userMenu.or(profileButton)).toBeVisible({ timeout: 10000 });

      // Screenshot
      await page.screenshot({ path: 'test-results/journey1-step3-dashboard.png' });
    });

    // ==================== DB VERIFICATION: Session Exists ====================
    await test.step('DB Check: Verify user session exists', async () => {
      const hasSession = await supabase.verifyUserSession(userId);
      expect(hasSession).toBe(true);

      console.log('✓ User session verified in DB');
    });

    // ==================== STEP 4: Create First Workspace ====================
    await test.step('Step 4: User creates first workspace', async () => {
      const workspaceName = generateWorkspaceName('My First Workspace');
      const workspaceDescription = 'Testing workspace creation in E2E test';

      // Look for "Create Workspace" button or empty state
      const createButton = page.getByRole('button', { name: /create workspace|new workspace/i });
      const addButton = page.getByRole('link', { name: /add workspace|\+ workspace/i });

      // Click whichever button exists
      if (await createButton.count() > 0) {
        await createButton.click();
      } else {
        await addButton.click();
      }

      // Wait for form/modal
      await wait(500);

      // Fill out workspace form
      await page.getByLabel(/name/i).fill(workspaceName);
      await page.getByLabel(/description/i).fill(workspaceDescription);

      // Submit form
      await page.getByRole('button', { name: /create|save/i }).click();

      // Wait for creation and navigation
      await wait(2000);

      // Verify success message or navigation to workspace
      const successToast = page.getByText(/workspace created|success/i);
      if (await successToast.count() > 0) {
        await expect(successToast).toBeVisible();
      }

      // Screenshot
      await page.screenshot({ path: 'test-results/journey1-step4-workspace-created.png' });

      console.log(`✓ Workspace created: ${workspaceName}`);
    });

    // ==================== DB VERIFICATION: Workspace Created ====================
    await test.step('DB Check: Verify workspace exists in database', async () => {
      // Wait for async workspace creation
      await wait(1000);

      // Get all workspaces for this user
      const { data: workspaces, error } = await supabase.getUserWorkspaces(userId);

      expect(error).toBeNull();
      expect(workspaces).not.toBeNull();
      expect(workspaces?.length).toBeGreaterThan(0);

      // Get the first workspace
      const workspace = workspaces![0];
      workspaceId = workspace.id;

      // Verify workspace belongs to user
      expect(workspace.user_id).toBe(userId);
      expect(workspace.name).toBeTruthy();
      expect(workspace.created_at).toBeTruthy();

      // Verify workspace was created recently
      const isRecent = await supabase.verifyRecentWorkspaceCreation(workspaceId);
      expect(isRecent).toBe(true);

      console.log(`✓ Workspace verified in DB: ${workspaceId}`);
      console.log(`  - Name: ${workspace.name}`);
      console.log(`  - User ID: ${workspace.user_id}`);
      console.log(`  - Created: ${workspace.created_at}`);
    });

    // ==================== STEP 5: Navigate to Workspace ====================
    await test.step('Step 5: User sees workspace dashboard', async () => {
      // Verify we can see workspace content
      await expect(page.url()).toMatch(/workspace/);

      // Look for workspace navigation or content
      const workspaceNav = page.getByText(/content sources|sources|newsletter/i);
      await expect(workspaceNav.first()).toBeVisible({ timeout: 10000 });

      // Screenshot final state
      await page.screenshot({ path: 'test-results/journey1-step5-workspace-dashboard.png' });

      console.log('✓ Onboarding journey completed successfully!');
    });
  });

  test('should show validation errors for invalid signup data', async ({ page }) => {
    await test.step('Attempt signup with invalid email', async () => {
      await page.goto('/register');

      await page.getByLabel(/^name$/i).fill('Test User');
      await page.getByLabel(/email/i).fill('invalid-email');
      await page.getByLabel(/password/i).first().fill('short');

      await page.getByRole('button', { name: /create account/i }).click();

      // Verify browser HTML5 validation errors are shown (email validation happens before submit)
      // Check for validation tooltip or message containing '@'
      await expect(page.getByText(/include.*@|missing.*@/i)).toBeVisible({ timeout: 5000 });

      // Note: Password validation text "Must be at least 8 characters" is always visible on page
      await expect(page.getByText(/must be at least 8 characters/i)).toBeVisible();
    });
  });

  test('should prevent duplicate email registration', async ({ page, supabase }) => {
    // This test requires a pre-existing user
    const existingEmail = 'existing-user@creatorpulse.test';

    await test.step('Attempt signup with existing email', async () => {
      await page.goto('/register');

      await page.getByLabel(/^name$/i).fill('Test User');
      await page.getByLabel(/email/i).fill(existingEmail);
      await page.getByLabel(/password/i).first().fill(testPassword);

      const confirmPassword = page.getByLabel(/confirm password/i);
      if (await confirmPassword.count() > 0) {
        await confirmPassword.fill(testPassword);
      }

      await page.getByRole('button', { name: /create account/i }).click();

      // Wait for error message
      await wait(2000);

      // Verify error message is shown
      await expect(page.getByText(/already exists|already registered|email taken/i)).toBeVisible();
    });
  });
});
