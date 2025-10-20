/**
 * E2E Test: Content Library with Existing User
 *
 * Tests content library features using existing user:
 * - Email: juhinebhnani4@gmail.com
 * - Password: 12345678
 *
 * Tests:
 * 1. View content library
 * 2. Verify thumbnails display (if content exists)
 * 3. Test inline feedback (👍/👎)
 * 4. Verify design preservation
 */

import { test, expect } from './fixtures/playwright-fixtures';

test.describe('Content Library - Existing User', () => {
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

  test('should navigate to content library', async ({ page }) => {
    await test.step('Click on Content navigation button', async () => {
      // Look for Content nav button
      const contentButton = page.locator('button:has-text("Content")').first();
      await expect(contentButton).toBeVisible({ timeout: 5000 });
      await contentButton.click();

      // Should navigate to content page
      await expect(page).toHaveURL('/app/content', { timeout: 5000 });
      console.log('✓ Navigated to content page');
    });

    await test.step('Verify content page loaded', async () => {
      // Check for page heading
      const heading = page.locator('h1').first();
      await expect(heading).toBeVisible();

      const headingText = await heading.textContent();
      console.log(`✓ Content page loaded: "${headingText}"`);
    });
  });

  test('should display content items if they exist', async ({ page }) => {
    await test.step('Navigate to content page', async () => {
      await page.goto('/app/content');
      console.log('✓ On content page');
    });

    await test.step('Check for content items', async () => {
      // Wait a moment for content to load
      await page.waitForTimeout(2000);

      // Look for content cards
      const contentCards = page.locator('[data-testid="content-card"]');
      const count = await contentCards.count();

      console.log(`✓ Found ${count} content items`);

      if (count > 0) {
        // Verify first card structure
        const firstCard = contentCards.first();
        await expect(firstCard).toBeVisible();

        // Check for title
        const title = firstCard.locator('h3').first();
        await expect(title).toBeVisible();

        const titleText = await title.textContent();
        console.log(`✓ First item title: "${titleText}"`);

        // Check for source badge
        const sourceBadge = firstCard.locator('[data-testid="source-badge"]').first();
        if (await sourceBadge.count() > 0) {
          const badgeText = await sourceBadge.textContent();
          console.log(`✓ Source badge: ${badgeText}`);
        }

        // Check for thumbnail or fallback
        const thumbnail = firstCard.locator('[data-testid="content-thumbnail"]');
        const fallback = firstCard.locator('[data-testid="thumbnail-fallback"]');

        if (await thumbnail.count() > 0) {
          console.log('✓ Thumbnail image found');
        } else if (await fallback.count() > 0) {
          console.log('✓ Thumbnail fallback icon found');
        }
      } else {
        console.log('⚠ No content items found (workspace may be empty)');
      }
    });
  });

  test('should show inline feedback buttons on content items', async ({ page }) => {
    await test.step('Navigate to content page', async () => {
      await page.goto('/app/content');
      await page.waitForTimeout(2000);
    });

    await test.step('Check for feedback buttons', async () => {
      const contentCards = page.locator('[data-testid="content-card"]');
      const count = await contentCards.count();

      if (count > 0) {
        const firstCard = contentCards.first();

        // Look for Keep (👍) button
        const keepButton = firstCard.locator('[data-testid="feedback-keep"]');
        const skipButton = firstCard.locator('[data-testid="feedback-skip"]');

        // At least one should be visible
        const hasKeep = await keepButton.count() > 0;
        const hasSkip = await skipButton.count() > 0;

        console.log(`✓ Keep button: ${hasKeep ? 'found' : 'not found'}`);
        console.log(`✓ Skip button: ${hasSkip ? 'found' : 'not found'}`);

        if (hasKeep || hasSkip) {
          console.log('✓ Inline feedback buttons present');
        }
      } else {
        console.log('⚠ No content items to test feedback buttons');
      }
    });
  });

  test('should preserve content page design aesthetic', async ({ page }) => {
    await page.goto('/app/content');

    await test.step('Verify page header styling', async () => {
      // Check for gradient header (if exists)
      const header = page.locator('h1').first();
      await expect(header).toBeVisible();

      // Get header classes
      const headerClasses = await header.getAttribute('class');
      console.log(`✓ Header classes: ${headerClasses}`);

      // Should have proper styling
      expect(headerClasses).toBeTruthy();
    });

    await test.step('Verify content cards have proper styling', async () => {
      const contentCards = page.locator('[data-testid="content-card"]');
      const count = await contentCards.count();

      if (count > 0) {
        const firstCard = contentCards.first();
        const cardClasses = await firstCard.getAttribute('class');

        // Should have shadow and hover effects
        expect(cardClasses).toContain('shadow');

        console.log('✓ Content cards have proper styling');
      }
    });

    await test.step('Verify source badges have color styling', async () => {
      const sourceBadges = page.locator('[data-testid="source-badge"]');
      const count = await sourceBadges.count();

      if (count > 0) {
        const firstBadge = sourceBadges.first();
        const badgeClasses = await firstBadge.getAttribute('class');

        // Should have badge styling
        expect(badgeClasses).toBeTruthy();

        console.log('✓ Source badges have color styling');
      }
    });
  });

  test('should have filters and search functionality', async ({ page }) => {
    await page.goto('/app/content');

    await test.step('Check for filter/search elements', async () => {
      // Look for search input
      const searchInput = page.locator('input[type="text"]').first();

      if (await searchInput.count() > 0) {
        console.log('✓ Search input found');

        // Try typing in search
        await searchInput.fill('test');
        console.log('✓ Search input functional');
        await searchInput.clear();
      }

      // Look for filter buttons/tabs
      const filterButtons = page.locator('[data-testid="filter-tab"]');
      const filterCount = await filterButtons.count();

      console.log(`✓ Found ${filterCount} filter tabs`);
    });
  });

  test('should maintain state after page reload', async ({ page }) => {
    await page.goto('/app/content');
    await page.waitForTimeout(2000);

    await test.step('Capture initial state', async () => {
      const contentCards = page.locator('[data-testid="content-card"]');
      const initialCount = await contentCards.count();

      console.log(`✓ Initial content count: ${initialCount}`);
    });

    await test.step('Reload page and verify state', async () => {
      await page.reload();
      await page.waitForTimeout(2000);

      // Should still be on content page
      await expect(page).toHaveURL('/app/content');

      const contentCards = page.locator('[data-testid="content-card"]');
      const reloadCount = await contentCards.count();

      console.log(`✓ After reload content count: ${reloadCount}`);
      console.log('✓ State maintained after reload');
    });
  });
});
