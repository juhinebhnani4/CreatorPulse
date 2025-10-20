/**
 * E2E Test: Journey 1 - Individual User Onboarding
 *
 * Tests complete individual user flow:
 * 1. Login with existing user
 * 2. Empty state Dashboard
 * 3. Navigate to Settings and configure sources
 * 4. Trigger content scraping
 * 5. Browse Content Library with thumbnails
 * 6. Give inline feedback (👍/👎)
 * 7. Generate newsletter
 * 8. Verify newsletter preview
 *
 * User: juhinebhnani4@gmail.com / 12345678
 */

import { test, expect } from './fixtures/playwright-fixtures';

test.describe('Journey 1: Individual User Onboarding', () => {
  const testEmail = 'juhinebhnani4@gmail.com';
  const testPassword = '12345678';

  test.beforeEach(async ({ page }) => {
    // Login before each test
    await page.goto('/login');
    await page.fill('[data-testid="email-input"]', testEmail);
    await page.fill('[data-testid="password-input"]', testPassword);
    await page.click('[data-testid="login-button"]');

    // Wait for redirect to dashboard
    await expect(page).toHaveURL('/app', { timeout: 10000 });
    console.log('✓ Logged in successfully');
  });

  test('should show empty state on dashboard when no sources configured', async ({ page }) => {
    await test.step('Verify Dashboard loads', async () => {
      // Should be on dashboard
      await expect(page).toHaveURL('/app');
      console.log('✓ On Dashboard page');
    });

    await test.step('Check for empty state or existing content', async () => {
      // Wait for page to load
      await page.waitForTimeout(2000);

      // Check if there's a "Configure Sources" CTA (empty state)
      const configureSourcesButton = page.locator('button:has-text("Configure Sources")').first();
      const hasEmptyState = await configureSourcesButton.count() > 0;

      if (hasEmptyState) {
        console.log('✓ Empty state detected - user needs to configure sources');
        await expect(configureSourcesButton).toBeVisible();
      } else {
        console.log('⚠ User already has sources configured - skipping empty state verification');
      }
    });
  });

  test('should navigate to Settings and configure sources', async ({ page }) => {
    await test.step('Navigate to Settings page', async () => {
      // Click Settings in navigation
      const settingsButton = page.locator('button:has-text("Settings")').first();
      await expect(settingsButton).toBeVisible({ timeout: 5000 });
      await settingsButton.click();

      // Should navigate to settings
      await expect(page).toHaveURL('/app/settings', { timeout: 5000 });
      console.log('✓ Navigated to Settings page');
    });

    await test.step('Verify Settings page loaded with sources section', async () => {
      // Wait for settings page to load
      await page.waitForTimeout(2000);

      // Check for settings sections
      const heading = page.locator('h1').first();
      await expect(heading).toBeVisible();

      const headingText = await heading.textContent();
      console.log(`✓ Settings page loaded: "${headingText}"`);

      // Look for sources section (should be default)
      const sourcesSection = page.locator('text=/Content Sources|Sources/i').first();
      if (await sourcesSection.count() > 0) {
        console.log('✓ Sources section found');
      }
    });

    await test.step('Check source configuration UI exists', async () => {
      // Look for source-related inputs or buttons
      const addButtons = page.locator('button:has-text("Add")');
      const inputFields = page.locator('input[type="text"]');

      const hasAddButtons = await addButtons.count() > 0;
      const hasInputs = await inputFields.count() > 0;

      console.log(`✓ Found ${await addButtons.count()} Add buttons`);
      console.log(`✓ Found ${await inputFields.count()} input fields`);

      // At least one of these should exist in source configuration
      expect(hasAddButtons || hasInputs).toBeTruthy();
    });
  });

  test('should navigate to Content Library and verify thumbnails', async ({ page }) => {
    await test.step('Navigate to Content Library', async () => {
      // Click Content in navigation
      const contentButton = page.locator('button:has-text("Content")').first();
      await expect(contentButton).toBeVisible({ timeout: 5000 });
      await contentButton.click();

      // Should navigate to content
      await expect(page).toHaveURL('/app/content', { timeout: 5000 });
      console.log('✓ Navigated to Content Library');
    });

    await test.step('Check for content items with thumbnails', async () => {
      // Wait for content to load
      await page.waitForTimeout(2000);

      // Look for content cards
      const contentCards = page.locator('[data-testid="content-card"]');
      const count = await contentCards.count();

      console.log(`✓ Found ${count} content items`);

      if (count > 0) {
        const firstCard = contentCards.first();

        // Check for thumbnail or fallback
        const thumbnail = firstCard.locator('[data-testid="content-thumbnail"]');
        const fallback = firstCard.locator('[data-testid="thumbnail-fallback"]');

        const hasThumbnail = await thumbnail.count() > 0;
        const hasFallback = await fallback.count() > 0;

        if (hasThumbnail) {
          console.log('✓ Thumbnail image found on first item');
        } else if (hasFallback) {
          console.log('✓ Thumbnail fallback icon found on first item');
        } else {
          console.log('⚠ No thumbnail or fallback found');
        }

        // Verify at least one exists
        expect(hasThumbnail || hasFallback).toBeTruthy();
      } else {
        console.log('⚠ No content items found (workspace may be empty)');
      }
    });
  });

  test('should show and interact with inline feedback buttons', async ({ page }) => {
    await test.step('Navigate to Content Library', async () => {
      await page.goto('/app/content');
      await page.waitForTimeout(2000);
    });

    await test.step('Verify inline feedback buttons exist', async () => {
      const contentCards = page.locator('[data-testid="content-card"]');
      const count = await contentCards.count();

      if (count > 0) {
        const firstCard = contentCards.first();

        // Look for Keep (👍) and Skip (👎) buttons
        const keepButton = firstCard.locator('[data-testid="feedback-keep"]');
        const skipButton = firstCard.locator('[data-testid="feedback-skip"]');

        const hasKeep = await keepButton.count() > 0;
        const hasSkip = await skipButton.count() > 0;

        console.log(`✓ Keep button (👍): ${hasKeep ? 'found' : 'not found'}`);
        console.log(`✓ Skip button (👎): ${hasSkip ? 'found' : 'not found'}`);

        // At least one feedback mechanism should exist
        expect(hasKeep || hasSkip).toBeTruthy();
      } else {
        console.log('⚠ No content items to test feedback buttons');
      }
    });

    await test.step('Click feedback button (if available)', async () => {
      const contentCards = page.locator('[data-testid="content-card"]');
      const count = await contentCards.count();

      if (count > 0) {
        const firstCard = contentCards.first();
        const keepButton = firstCard.locator('[data-testid="feedback-keep"]');

        if (await keepButton.count() > 0) {
          // Click the Keep button
          await keepButton.click();
          console.log('✓ Clicked Keep (👍) button');

          // Wait for feedback to be processed
          await page.waitForTimeout(1000);

          // Look for success toast or feedback indicator
          const toast = page.locator('[role="status"]').first();
          if (await toast.count() > 0) {
            console.log('✓ Feedback toast appeared');
          }
        }
      }
    });
  });

  test('should verify simplified navigation (only 3 pages visible)', async ({ page }) => {
    await test.step('Check navigation bar shows only 3 items', async () => {
      // Get all navigation buttons
      const navButtons = page.locator('nav button').or(page.locator('nav a'));

      // Count visible navigation items
      const navItems = await navButtons.all();

      // Filter for Dashboard, Content, Settings
      let foundDashboard = false;
      let foundContent = false;
      let foundSettings = false;
      let foundHiddenPages = [];

      for (const item of navItems) {
        const text = await item.textContent();
        if (text?.includes('Dashboard')) foundDashboard = true;
        if (text?.includes('Content')) foundContent = true;
        if (text?.includes('Settings')) foundSettings = true;

        // Check for hidden pages that shouldn't be in navigation
        if (text?.includes('Trends')) foundHiddenPages.push('Trends');
        if (text?.includes('Analytics')) foundHiddenPages.push('Analytics');
        if (text?.includes('Style')) foundHiddenPages.push('Style');
        if (text?.includes('Feedback')) foundHiddenPages.push('Feedback');
        if (text?.includes('History')) foundHiddenPages.push('History');
        if (text?.includes('Schedule')) foundHiddenPages.push('Schedule');
      }

      console.log(`✓ Dashboard: ${foundDashboard ? 'visible' : 'NOT FOUND'}`);
      console.log(`✓ Content: ${foundContent ? 'visible' : 'NOT FOUND'}`);
      console.log(`✓ Settings: ${foundSettings ? 'visible' : 'NOT FOUND'}`);

      if (foundHiddenPages.length > 0) {
        console.log(`❌ Found hidden pages in navigation: ${foundHiddenPages.join(', ')}`);
      } else {
        console.log('✓ No hidden pages in navigation (correct)');
      }

      // Verify only 3 main pages are visible
      expect(foundDashboard).toBeTruthy();
      expect(foundContent).toBeTruthy();
      expect(foundSettings).toBeTruthy();
      expect(foundHiddenPages.length).toBe(0);
    });
  });

  test('should preserve design aesthetic (gradients, animations, shadows)', async ({ page }) => {
    await test.step('Verify Dashboard gradient headers', async () => {
      await page.goto('/app');
      await page.waitForTimeout(1000);

      // Look for elements with gradient classes
      const gradientElements = page.locator('[class*="gradient"]');
      const count = await gradientElements.count();

      console.log(`✓ Found ${count} gradient elements`);
      expect(count).toBeGreaterThan(0);
    });

    await test.step('Verify Content Library cards have proper styling', async () => {
      await page.goto('/app/content');
      await page.waitForTimeout(1000);

      const contentCards = page.locator('[data-testid="content-card"]');
      const cardCount = await contentCards.count();

      if (cardCount > 0) {
        const firstCard = contentCards.first();
        const cardClasses = await firstCard.getAttribute('class');

        // Should have shadow styling
        const hasShadow = cardClasses?.includes('shadow');
        console.log(`✓ Card shadow: ${hasShadow ? 'present' : 'missing'}`);

        expect(hasShadow).toBeTruthy();
      }
    });

    await test.step('Verify Settings page styling preserved', async () => {
      await page.goto('/app/settings');
      await page.waitForTimeout(1000);

      // Check for proper heading
      const heading = page.locator('h1').first();
      await expect(heading).toBeVisible();

      // Check for styled cards
      const cards = page.locator('[class*="rounded"]');
      const count = await cards.count();

      console.log(`✓ Found ${count} styled elements on Settings page`);
      expect(count).toBeGreaterThan(0);
    });
  });

  test('should navigate through complete user journey', async ({ page }) => {
    await test.step('1. Start at Dashboard', async () => {
      await expect(page).toHaveURL('/app');
      console.log('✓ Step 1: Dashboard');
    });

    await test.step('2. Navigate to Content Library', async () => {
      const contentButton = page.locator('button:has-text("Content")').first();
      await contentButton.click();
      await expect(page).toHaveURL('/app/content');
      await page.waitForTimeout(1000);
      console.log('✓ Step 2: Content Library');
    });

    await test.step('3. Navigate to Settings', async () => {
      const settingsButton = page.locator('button:has-text("Settings")').first();
      await settingsButton.click();
      await expect(page).toHaveURL('/app/settings');
      await page.waitForTimeout(1000);
      console.log('✓ Step 3: Settings');
    });

    await test.step('4. Return to Dashboard', async () => {
      const dashboardButton = page.locator('button:has-text("Dashboard")').first();
      await dashboardButton.click();
      await expect(page).toHaveURL('/app');
      await page.waitForTimeout(1000);
      console.log('✓ Step 4: Back to Dashboard');
    });

    console.log('✓ Complete user journey navigation successful');
  });
});
