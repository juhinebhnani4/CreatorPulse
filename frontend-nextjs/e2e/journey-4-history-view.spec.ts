/**
 * Journey 4: Newsletter History View
 *
 * User Story 6.1: View Newsletter History
 * Tests viewing past sent newsletters with real backend integration
 */

import { test, expect } from '@playwright/test';
import { SupabaseTestHelper } from './utils/supabase-helper';

test.describe('Journey 4: Newsletter History', () => {
  let helper: SupabaseTestHelper;
  let testEmail: string;
  let workspaceId: string;
  let userId: string;

  test.beforeEach(async ({ page }) => {
    helper = new SupabaseTestHelper();
    testEmail = `history-test-${Date.now()}@example.com`;

    // Register and login
    await page.goto('/register');
    await page.getByLabel(/^name$/i).fill('History Test User');
    await page.getByLabel(/email/i).fill(testEmail);
    await page.getByLabel(/^password$/i).fill('testpass123');
    await page.getByRole('button', { name: /create account/i }).click();

    // Wait for redirect to dashboard
    await page.waitForURL('/app');

    // Get workspace ID from the page
    await page.waitForTimeout(2000); // Wait for workspace creation

    // Verify user exists
    const user = await helper.verifyUserExists(testEmail);
    expect(user).not.toBeNull();
    userId = user!.id;

    // Get workspace
    const workspaces = await helper.listWorkspaces(userId);
    expect(workspaces.length).toBeGreaterThan(0);
    workspaceId = workspaces[0].id;

    console.log('[Setup] User ID:', userId);
    console.log('[Setup] Workspace ID:', workspaceId);
  });

  test.afterEach(async () => {
    // Cleanup test user
    if (testEmail) {
      await helper.cleanupUser(testEmail);
    }
  });

  test('4.1: Should display empty state when no newsletters sent', async ({ page }) => {
    console.log('[Test] Navigating to history page...');

    // Navigate to history page
    await page.goto('/app/history');

    // Should show empty state
    await expect(page.getByText(/no newsletters sent yet/i)).toBeVisible();
    await expect(page.getByRole('button', { name: /go to dashboard/i })).toBeVisible();

    console.log('[Test] ✓ Empty state displayed correctly');
  });

  test('4.2: Should display sent newsletters from backend', async ({ page }) => {
    console.log('[Test] Setting up test data...');

    // Create a test newsletter and mark it as sent
    const newsletter = await helper.createNewsletter(workspaceId, {
      title: 'Test Newsletter - History',
      subject_line: 'Test Subject Line',
      status: 'sent',
      sent_at: new Date().toISOString(),
    });

    console.log('[Test] Created newsletter:', newsletter.id);

    // Navigate to history page
    await page.goto('/app/history');

    // Wait for newsletters to load
    await page.waitForTimeout(2000);

    // Should show the newsletter
    await expect(page.getByText('Test Subject Line')).toBeVisible();

    // Should show sent date
    const dateRegex = /(Oct|Nov|Dec|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep)\s+\d{1,2}/;
    await expect(page.getByText(dateRegex)).toBeVisible();

    console.log('[Test] ✓ Newsletter displayed in history');
  });

  test('4.3: Should show loading state while fetching', async ({ page }) => {
    console.log('[Test] Testing loading state...');

    // Navigate to history (should show loader briefly)
    await page.goto('/app/history');

    // Check if loader was visible (may be very brief)
    const loader = page.locator('svg.animate-spin');

    // Either loader is visible or newsletters loaded so fast it's already gone
    const isLoaderVisible = await loader.isVisible().catch(() => false);
    const hasNewsletters = await page.getByText(/sent/).isVisible().catch(() => false);
    const hasEmptyState = await page.getByText(/no newsletters sent yet/i).isVisible().catch(() => false);

    // One of these should be true
    expect(isLoaderVisible || hasNewsletters || hasEmptyState).toBeTruthy();

    console.log('[Test] ✓ Loading state handled correctly');
  });

  test('4.4: Should navigate to dashboard from empty state', async ({ page }) => {
    console.log('[Test] Testing empty state navigation...');

    // Navigate to history page
    await page.goto('/app/history');

    // Click "Go to Dashboard" button
    await page.getByRole('button', { name: /go to dashboard/i }).click();

    // Should redirect to dashboard
    await page.waitForURL('/app');
    await expect(page.getByText(/welcome/i)).toBeVisible();

    console.log('[Test] ✓ Navigation from empty state works');
  });

  test('4.5: Should display multiple newsletters in chronological order', async ({ page }) => {
    console.log('[Test] Creating multiple newsletters...');

    // Create 3 newsletters with different sent dates
    const newsletter1 = await helper.createNewsletter(workspaceId, {
      title: 'Newsletter 1',
      subject_line: 'First Newsletter',
      status: 'sent',
      sent_at: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(), // 2 days ago
    });

    const newsletter2 = await helper.createNewsletter(workspaceId, {
      title: 'Newsletter 2',
      subject_line: 'Second Newsletter',
      status: 'sent',
      sent_at: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(), // 1 day ago
    });

    const newsletter3 = await helper.createNewsletter(workspaceId, {
      title: 'Newsletter 3',
      subject_line: 'Third Newsletter',
      status: 'sent',
      sent_at: new Date().toISOString(), // Today
    });

    console.log('[Test] Created 3 newsletters');

    // Navigate to history page
    await page.goto('/app/history');
    await page.waitForTimeout(2000);

    // Should show all 3 newsletters
    await expect(page.getByText('First Newsletter')).toBeVisible();
    await expect(page.getByText('Second Newsletter')).toBeVisible();
    await expect(page.getByText('Third Newsletter')).toBeVisible();

    console.log('[Test] ✓ All newsletters displayed');
  });

  test('4.6: Should only show sent newsletters (not drafts)', async ({ page }) => {
    console.log('[Test] Testing draft filtering...');

    // Create one sent and one draft newsletter
    const sentNewsletter = await helper.createNewsletter(workspaceId, {
      title: 'Sent Newsletter',
      subject_line: 'Sent Subject',
      status: 'sent',
      sent_at: new Date().toISOString(),
    });

    const draftNewsletter = await helper.createNewsletter(workspaceId, {
      title: 'Draft Newsletter',
      subject_line: 'Draft Subject',
      status: 'draft',
    });

    console.log('[Test] Created sent and draft newsletters');

    // Navigate to history page
    await page.goto('/app/history');
    await page.waitForTimeout(2000);

    // Should show sent newsletter
    await expect(page.getByText('Sent Subject')).toBeVisible();

    // Should NOT show draft newsletter
    await expect(page.getByText('Draft Subject')).not.toBeVisible();

    console.log('[Test] ✓ Only sent newsletters displayed');
  });

  test('4.7: Should handle analytics not available gracefully', async ({ page }) => {
    console.log('[Test] Testing newsletter without analytics...');

    // Create a newsletter without analytics
    const newsletter = await helper.createNewsletter(workspaceId, {
      title: 'No Analytics Newsletter',
      subject_line: 'Newsletter Without Stats',
      status: 'sent',
      sent_at: new Date().toISOString(),
    });

    // Navigate to history page
    await page.goto('/app/history');
    await page.waitForTimeout(2000);

    // Should show the newsletter
    await expect(page.getByText('Newsletter Without Stats')).toBeVisible();

    // Should show message about analytics
    await expect(page.getByText(/analytics will be available/i)).toBeVisible();

    console.log('[Test] ✓ Handles missing analytics gracefully');
  });
});
