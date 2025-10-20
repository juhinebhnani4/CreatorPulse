/**
 * E2E Test: Content Library with Thumbnails & Inline Feedback
 *
 * Tests complete user journey:
 * 1. Content scraping with thumbnail extraction
 * 2. Thumbnail display in UI
 * 3. Fallback icons for items without thumbnails
 * 4. Inline feedback (👍/👎) submission
 * 5. Database verification of all actions
 *
 * Critical: Tests invisible backend logic (thumbnail extraction, feedback processing)
 */

import { test, expect } from './fixtures/playwright-fixtures';
import { generateTestEmail, wait } from './fixtures/test-data';

test.describe('Content Library - Thumbnails & Inline Feedback', () => {
  let testEmail: string;
  let testPassword: string;
  let userId: string;
  let workspaceId: string;

  test.beforeEach(async ({ page, supabase }) => {
    // Generate test credentials
    testEmail = generateTestEmail('content-thumbnail-test');
    testPassword = 'SecureTestPass123!';

    // Register user via UI (tests auth flow simultaneously)
    await test.step('Setup: Register test user', async () => {
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

    await test.step('Setup: Get workspace ID', async () => {
      // Auto-created workspace should exist
      const workspaces = await supabase.listWorkspaces(userId);
      expect(workspaces.length).toBeGreaterThan(0);
      workspaceId = workspaces[0].id;
      console.log(`✓ Workspace ID: ${workspaceId}`);
    });
  });

  test.afterEach(async ({ supabase }) => {
    // Cleanup test data
    if (userId) {
      console.log(`[Cleanup] Removing test user: ${testEmail}`);
      await supabase.cleanupTestUser(userId);
    }
  });

  test('should display thumbnails for scraped content items', async ({ page, supabase }) => {
    await test.step('Navigate to content page', async () => {
      await page.click('a[href="/app/content"]');
      await expect(page).toHaveURL('/app/content');
      console.log('✓ Navigated to content page');
    });

    await test.step('Trigger content scraping', async () => {
      // Click "Scrape Now" button
      const scrapeButton = page.locator('button:has-text("Scrape Now")');
      await expect(scrapeButton).toBeVisible({ timeout: 5000 });
      await scrapeButton.click();

      // Wait for scraping to start
      await expect(page.locator('text=Scraping...')).toBeVisible({ timeout: 5000 });
      console.log('✓ Scraping started');

      // Wait for scraping to complete (up to 30 seconds)
      await expect(page.locator('text=Scraping...')).toBeHidden({ timeout: 30000 });
      console.log('✓ Scraping completed');

      // Wait a bit for UI to update
      await wait(2000);
    });

    await test.step('Verify content cards are displayed', async () => {
      // Wait for content cards to appear
      await page.waitForSelector('[data-testid="content-card"]', { timeout: 10000 });

      const contentCards = await page.$$('[data-testid="content-card"]');
      expect(contentCards.length).toBeGreaterThan(0);
      console.log(`✓ Found ${contentCards.length} content cards`);
    });

    await test.step('Verify thumbnails are displayed', async () => {
      // Get all thumbnails (actual images, not fallbacks)
      const thumbnails = await page.$$('[data-testid="content-thumbnail"]');

      // Should have at least some thumbnails (YouTube, Blogs usually have them)
      expect(thumbnails.length).toBeGreaterThan(0);
      console.log(`✓ Found ${thumbnails.length} thumbnails`);

      // Verify first thumbnail loaded successfully
      const firstThumbnail = thumbnails[0];
      const imageLoaded = await firstThumbnail.evaluate((img: HTMLImageElement) => {
        return img.complete && img.naturalHeight > 0;
      });
      expect(imageLoaded).toBe(true);
      console.log('✓ First thumbnail loaded successfully');

      // Get thumbnail src for verification
      const src = await firstThumbnail.getAttribute('src');
      expect(src).toBeTruthy();
      expect(src).toMatch(/^https?:\/\//);
      console.log(`✓ Thumbnail URL is valid: ${src?.substring(0, 50)}...`);
    });

    await test.step('DB Verification: Content items have thumbnails in database', async () => {
      const { data: content, error } = await supabase.getWorkspaceContent(workspaceId);

      expect(error).toBeNull();
      expect(content).not.toBeNull();
      expect(content!.length).toBeGreaterThan(0);

      // Filter items with thumbnails
      const itemsWithThumbnails = content!.filter(item => item.image_url);
      expect(itemsWithThumbnails.length).toBeGreaterThan(0);

      // Verify thumbnail URLs are valid
      itemsWithThumbnails.forEach(item => {
        expect(item.image_url).toMatch(/^https?:\/\//);
      });

      console.log(`✓ Database: ${itemsWithThumbnails.length}/${content!.length} items have thumbnails`);
    });
  });

  test('should show fallback icons for items without thumbnails', async ({ page }) => {
    await test.step('Navigate to content page and scrape', async () => {
      await page.goto('/app/content');

      // Trigger scraping
      await page.click('button:has-text("Scrape Now")');
      await expect(page.locator('text=Scraping...')).toBeVisible();
      await expect(page.locator('text=Scraping...')).toBeHidden({ timeout: 30000 });

      await wait(2000);
    });

    await test.step('Verify fallback icons are displayed', async () => {
      // Wait for content cards
      await page.waitForSelector('[data-testid="content-card"]', { timeout: 10000 });

      // Find fallback thumbnails (items without images)
      const fallbacks = await page.$$('[data-testid="thumbnail-fallback"]');

      if (fallbacks.length > 0) {
        console.log(`✓ Found ${fallbacks.length} items with fallback icons`);

        // Verify fallback has source-specific background color
        const fallback = fallbacks[0];
        const bgColor = await fallback.evaluate((el) => {
          return window.getComputedStyle(el).backgroundColor;
        });

        // Should have a background color (not transparent)
        expect(bgColor).not.toBe('rgba(0, 0, 0, 0)');
        expect(bgColor).not.toBe('');
        console.log(`✓ Fallback has background color: ${bgColor}`);

        // Verify icon element is present
        const icon = await fallback.$('svg');
        expect(icon).not.toBeNull();
        console.log('✓ Fallback icon (ImageIcon) is present');
      } else {
        console.log('✓ All items have thumbnails (no fallbacks needed)');
      }
    });
  });

  test('should display source badges with correct colors and icons', async ({ page }) => {
    await page.goto('/app/content');

    // Scrape content
    await page.click('button:has-text("Scrape Now")');
    await expect(page.locator('text=Scraping...')).toBeVisible();
    await expect(page.locator('text=Scraping...')).toBeHidden({ timeout: 30000 });

    await wait(2000);

    await test.step('Verify source badges exist and have icons', async () => {
      await page.waitForSelector('[data-testid="source-badge"]', { timeout: 10000 });

      const badges = await page.$$('[data-testid="source-badge"]');
      expect(badges.length).toBeGreaterThan(0);
      console.log(`✓ Found ${badges.length} source badges`);

      // Verify each badge has proper content
      for (const badge of badges.slice(0, 5)) {  // Check first 5
        const text = await badge.textContent();

        // Should have emoji icon
        const hasEmoji = /🔴|🟠|🔵|🟢|🟣/.test(text || '');
        expect(hasEmoji).toBe(true);

        // Should have source name
        const hasSourceName = /reddit|rss|youtube|twitter|x|blog/i.test(text || '');
        expect(hasSourceName).toBe(true);
      }

      console.log('✓ All badges have emoji icons and source names');
    });
  });

  test('should submit inline feedback and save to database', async ({ page, supabase }) => {
    await page.goto('/app/content');

    // Scrape content first
    await page.click('button:has-text("Scrape Now")');
    await expect(page.locator('text=Scraping...')).toBeVisible();
    await expect(page.locator('text=Scraping...')).toBeHidden({ timeout: 30000 });
    await wait(2000);

    await test.step('Wait for content to load', async () => {
      await page.waitForSelector('[data-testid="content-card"]', { timeout: 10000 });
      console.log('✓ Content cards loaded');
    });

    await test.step('Submit positive feedback (thumbs up)', async () => {
      // Get first content card
      const firstCard = await page.$('[data-testid="content-card"]');
      expect(firstCard).not.toBeNull();

      const itemId = await firstCard!.getAttribute('data-item-id');
      expect(itemId).toBeTruthy();
      console.log(`✓ First content item ID: ${itemId}`);

      // Click "Keep" button
      const keepButton = await firstCard!.$('[data-testid="feedback-keep-button"]');
      expect(keepButton).not.toBeNull();
      await keepButton!.click();

      // Wait for success toast
      await expect(page.locator('text=Feedback Recorded')).toBeVisible({ timeout: 5000 });
      console.log('✓ Success toast displayed');

      // Wait for async processing
      await wait(2000);

      // DB Verification: Feedback saved correctly
      await test.step('DB Verification: Positive feedback saved', async () => {
        // Query feedback table (note: table name might be 'feedback' or 'user_feedback')
        const { data: feedbackData, error } = await supabase.serviceClient
          .from('feedback')
          .select('*')
          .eq('content_item_id', itemId)
          .eq('workspace_id', workspaceId);

        if (error) {
          console.warn('Feedback table query error:', error);
          // Try alternative table name
          const { data: altData } = await supabase.serviceClient
            .from('user_feedback')
            .select('*')
            .eq('content_item_id', itemId);

          if (altData && altData.length > 0) {
            expect(altData[0].rating).toBe(5);  // Positive = 5 stars
            console.log('✓ Positive feedback saved to database (user_feedback table)');
            return;
          }
        }

        expect(error).toBeNull();
        expect(feedbackData).not.toBeNull();
        expect(feedbackData!.length).toBeGreaterThan(0);

        const feedback = feedbackData![0];
        expect(feedback.rating).toBe(5);  // Positive = 5 stars
        expect(feedback.feedback_type).toBe('content_quality');
        expect(feedback.workspace_id).toBe(workspaceId);

        console.log('✓ Positive feedback verified in database');
        console.log(`  - Rating: ${feedback.rating}`);
        console.log(`  - Type: ${feedback.feedback_type}`);
      });
    });

    await test.step('Submit negative feedback (thumbs down)', async () => {
      // Get second content card
      const cards = await page.$$('[data-testid="content-card"]');
      expect(cards.length).toBeGreaterThan(1);

      const secondCard = cards[1];
      const itemId = await secondCard.getAttribute('data-item-id');
      expect(itemId).toBeTruthy();

      // Click "Skip" button
      const skipButton = await secondCard.$('[data-testid="feedback-skip-button"]');
      expect(skipButton).not.toBeNull();
      await skipButton!.click();

      // Wait for toast
      await expect(page.locator('text=Feedback Recorded')).toBeVisible({ timeout: 5000 });
      console.log('✓ Negative feedback success toast displayed');

      await wait(2000);

      // DB Verification: Negative feedback saved
      await test.step('DB Verification: Negative feedback saved', async () => {
        const { data: feedbackData } = await supabase.serviceClient
          .from('feedback')
          .select('*')
          .eq('content_item_id', itemId)
          .eq('workspace_id', workspaceId);

        if (!feedbackData || feedbackData.length === 0) {
          // Try alternative table
          const { data: altData } = await supabase.serviceClient
            .from('user_feedback')
            .select('*')
            .eq('content_item_id', itemId);

          if (altData && altData.length > 0) {
            expect(altData[0].rating).toBe(1);  // Negative = 1 star
            console.log('✓ Negative feedback saved to database');
            return;
          }
        }

        expect(feedbackData).not.toBeNull();
        expect(feedbackData!.length).toBeGreaterThan(0);

        const feedback = feedbackData![0];
        expect(feedback.rating).toBe(1);  // Negative = 1 star

        console.log('✓ Negative feedback verified in database');
        console.log(`  - Rating: ${feedback.rating}`);
      });
    });
  });

  test('should preserve design aesthetic (gradients, animations, shadows)', async ({ page }) => {
    await page.goto('/app/content');

    await test.step('Verify header gradient preserved', async () => {
      const header = await page.$('h1');
      if (header) {
        const classes = await header.getAttribute('class');
        // Should have gradient classes
        const hasGradient = classes?.includes('bg-gradient') || classes?.includes('gradient');
        expect(hasGradient).toBe(true);
        console.log('✓ Header gradient classes preserved');
      }
    });

    await test.step('Verify button gradient preserved', async () => {
      const scrapeBtn = await page.$('button:has-text("Scrape Now")');
      expect(scrapeBtn).not.toBeNull();

      const btnClasses = await scrapeBtn!.getAttribute('class');
      expect(btnClasses).toContain('bg-gradient-warm');
      console.log('✓ Scrape button gradient preserved');
    });

    await test.step('Verify card animations preserved', async () => {
      // Scrape to get content cards
      await page.click('button:has-text("Scrape Now")');
      await expect(page.locator('text=Scraping...')).toBeVisible();
      await expect(page.locator('text=Scraping...')).toBeHidden({ timeout: 30000 });
      await wait(2000);

      const card = await page.$('[data-testid="content-card"]');
      expect(card).not.toBeNull();

      const cardClasses = await card!.getAttribute('class');
      expect(cardClasses).toContain('animate-slide-up');
      console.log('✓ Card animations preserved');

      const cardStyle = await card!.getAttribute('style');
      expect(cardStyle).toContain('animationDelay');
      console.log('✓ Staggered animation delays preserved');
    });

    await test.step('Verify shadows and hover effects', async () => {
      const card = await page.$('[data-testid="content-card"]');
      const cardClasses = await card!.getAttribute('class');

      expect(cardClasses).toContain('shadow-md');
      expect(cardClasses).toContain('hover:shadow-lg');
      expect(cardClasses).toContain('transition-shadow');

      console.log('✓ Shadow and hover effects preserved');
    });

    await test.step('Verify no CSS breaking changes', async () => {
      // Check that test IDs don't affect styling
      const card = await page.$('[data-testid="content-card"]');

      // Get computed styles
      const bgColor = await card!.evaluate((el) => window.getComputedStyle(el).backgroundColor);
      const borderRadius = await card!.evaluate((el) => window.getComputedStyle(el).borderRadius);

      // Should have styling (not default browser styles)
      expect(bgColor).not.toBe('rgba(0, 0, 0, 0)');
      expect(borderRadius).not.toBe('0px');

      console.log('✓ No CSS breaking changes detected');
    });
  });
});
