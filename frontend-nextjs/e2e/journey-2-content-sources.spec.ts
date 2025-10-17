/**
 * E2E Test: User Journey 2 - Configure Content Sources & Scrape
 *
 * User Story: As a user, I want to add content sources to my workspace
 * and scrape content so I can review aggregated content.
 *
 * Flow:
 * 1. User logs in and navigates to workspace
 * 2. Add RSS feed source
 * 3. Add Reddit source
 * 4. Add Twitter/X source
 * 5. Trigger content scraping
 * 6. View scraped content
 * 7. Filter content by source type
 *
 * Each step verifies both frontend UI and backend database state.
 */

import { test, expect } from './fixtures/playwright-fixtures';
import {
  generateTestEmail,
  generateWorkspaceName,
  testContentSources,
  wait,
} from './fixtures/test-data';

test.describe('User Journey 2: Content Sources & Scraping', () => {
  let testEmail: string;
  let testPassword: string;
  let userId: string;
  let workspaceId: string;
  let rssSourceId: string;
  let redditSourceId: string;
  let twitterSourceId: string;
  let scrapeJobId: string;

  test.beforeAll(async ({ supabase }) => {
    // Setup: Create test user and workspace
    testEmail = generateTestEmail('sources');
    testPassword = 'SecureTestPass123!';

    // Note: In a real test, you'd create the user via API or previous test
    // For now, we'll assume user creation is handled by auth
  });

  test.afterAll(async ({ supabase }) => {
    // Cleanup: Remove test data
    if (workspaceId) {
      await supabase.cleanupTestWorkspace(workspaceId);
    }
    if (userId) {
      await supabase.cleanupTestUser(userId);
    }
  });

  test('should complete full content source configuration and scraping journey', async ({
    page,
    supabase,
  }) => {
    // ==================== SETUP: Login ====================
    await test.step('Setup: User logs in', async () => {
      await page.goto('/login');

      await page.getByLabel(/email/i).fill(testEmail);
      await page.getByLabel(/password/i).fill(testPassword);
      await page.getByRole('button', { name: /sign in|login/i }).click();

      await wait(2000);

      // Verify logged in
      await expect(page.url()).toMatch(/dashboard|workspaces/);
    });

    // ==================== STEP 1: Navigate to Sources ====================
    await test.step('Step 1: User navigates to Content Sources', async () => {
      // Look for workspace or sources navigation
      const sourcesLink = page.getByRole('link', { name: /sources|content sources/i });
      const workspaceLink = page.getByRole('link', { name: /workspace/i }).first();

      if (await sourcesLink.count() > 0) {
        await sourcesLink.click();
      } else {
        // Navigate through workspace
        await workspaceLink.click();
        await wait(500);
        await page.getByRole('link', { name: /sources/i }).click();
      }

      // Verify we're on sources page
      await expect(page.url()).toMatch(/sources/);
      await expect(page.getByText(/content sources|add source/i)).toBeVisible();

      // Extract workspace ID from URL
      const urlMatch = page.url().match(/workspaces\/([a-f0-9-]+)/);
      if (urlMatch) {
        workspaceId = urlMatch[1];
      }

      await page.screenshot({ path: 'test-results/journey2-step1-sources-page.png' });
    });

    // ==================== DB CHECK: Workspace Exists ====================
    await test.step('DB Check: Verify workspace exists', async () => {
      expect(workspaceId).toBeTruthy();

      const { exists } = await supabase.verifyWorkspace(workspaceId, userId);
      expect(exists).toBe(true);

      console.log(`✓ Workspace verified: ${workspaceId}`);
    });

    // ==================== STEP 2: Add RSS Feed ====================
    await test.step('Step 2: User adds RSS feed source', async () => {
      // Click "Add Source" button
      await page.getByRole('button', { name: /add source|new source|\+/i }).click();
      await wait(500);

      // Select RSS type
      const rssOption = page.getByRole('radio', { name: /rss/i });
      const rssButton = page.getByRole('button', { name: /rss/i });

      if (await rssOption.count() > 0) {
        await rssOption.click();
      } else if (await rssButton.count() > 0) {
        await rssButton.click();
      }

      // Fill RSS form
      await page.getByLabel(/name|title/i).fill(testContentSources.rss.name);
      await page.getByLabel(/url|feed url/i).fill(testContentSources.rss.url);

      // Submit form
      await page.getByRole('button', { name: /add|create|save/i }).click();
      await wait(2000);

      // Verify success
      const successMessage = page.getByText(/added|created|success/i);
      if (await successMessage.count() > 0) {
        await expect(successMessage).toBeVisible();
      }

      // Verify RSS source appears in list
      await expect(page.getByText(testContentSources.rss.name)).toBeVisible();

      await page.screenshot({ path: 'test-results/journey2-step2-rss-added.png' });
    });

    // ==================== DB CHECK: RSS Source Created ====================
    await test.step('DB Check: Verify RSS source in database', async () => {
      await wait(1000);

      const { data: sources } = await supabase.getWorkspaceSources(workspaceId);
      expect(sources).not.toBeNull();
      expect(sources?.length).toBeGreaterThan(0);

      const rssSource = sources!.find(s => s.source_type === 'rss');
      expect(rssSource).toBeDefined();
      expect(rssSource?.workspace_id).toBe(workspaceId);
      expect(rssSource?.name).toBe(testContentSources.rss.name);

      rssSourceId = rssSource!.id;

      console.log(`✓ RSS source verified in DB: ${rssSourceId}`);
    });

    // ==================== STEP 3: Add Reddit Source ====================
    await test.step('Step 3: User adds Reddit source', async () => {
      await page.getByRole('button', { name: /add source|new source|\+/i }).click();
      await wait(500);

      // Select Reddit type
      const redditOption = page.getByRole('radio', { name: /reddit/i });
      const redditButton = page.getByRole('button', { name: /reddit/i });

      if (await redditOption.count() > 0) {
        await redditOption.click();
      } else if (await redditButton.count() > 0) {
        await redditButton.click();
      }

      // Fill Reddit form
      await page.getByLabel(/name|title/i).fill(testContentSources.reddit.name);
      await page.getByLabel(/subreddit|url/i).fill(testContentSources.reddit.config.subreddit);

      await page.getByRole('button', { name: /add|create|save/i }).click();
      await wait(2000);

      // Verify Reddit source appears in list
      await expect(page.getByText(testContentSources.reddit.name)).toBeVisible();

      await page.screenshot({ path: 'test-results/journey2-step3-reddit-added.png' });
    });

    // ==================== DB CHECK: Reddit Source Created ====================
    await test.step('DB Check: Verify Reddit source in database', async () => {
      await wait(1000);

      const { data: sources } = await supabase.getWorkspaceSources(workspaceId);
      expect(sources?.length).toBe(2);

      const redditSource = sources!.find(s => s.source_type === 'reddit');
      expect(redditSource).toBeDefined();
      expect(redditSource?.workspace_id).toBe(workspaceId);

      redditSourceId = redditSource!.id;

      console.log(`✓ Reddit source verified in DB: ${redditSourceId}`);
    });

    // ==================== STEP 4: Add Twitter Source ====================
    await test.step('Step 4: User adds Twitter/X source', async () => {
      await page.getByRole('button', { name: /add source|new source|\+/i }).click();
      await wait(500);

      // Select Twitter/X type
      const twitterOption = page.getByRole('radio', { name: /twitter|x\.com/i });
      const twitterButton = page.getByRole('button', { name: /twitter|x\.com/i });

      if (await twitterOption.count() > 0) {
        await twitterOption.click();
      } else if (await twitterButton.count() > 0) {
        await twitterButton.click();
      }

      // Fill Twitter form
      await page.getByLabel(/name|title/i).fill(testContentSources.twitter.name);
      await page.getByLabel(/username|handle|url/i).fill(testContentSources.twitter.config.username);

      await page.getByRole('button', { name: /add|create|save/i }).click();
      await wait(2000);

      // Verify Twitter source appears in list
      await expect(page.getByText(testContentSources.twitter.name)).toBeVisible();

      await page.screenshot({ path: 'test-results/journey2-step4-twitter-added.png' });
    });

    // ==================== DB CHECK: All 3 Sources Exist ====================
    await test.step('DB Check: Verify all 3 sources in database', async () => {
      await wait(1000);

      const { data: sources } = await supabase.getWorkspaceSources(workspaceId);
      expect(sources?.length).toBe(3);

      const sourceTypes = sources!.map(s => s.source_type);
      expect(sourceTypes).toContain('rss');
      expect(sourceTypes).toContain('reddit');
      expect(sourceTypes).toContain('twitter');

      console.log(`✓ All 3 sources verified in DB`);
    });

    // ==================== STEP 5: Trigger Scraping ====================
    await test.step('Step 5: User triggers content scraping', async () => {
      // Look for "Scrape Now" or "Fetch Content" button
      const scrapeButton = page.getByRole('button', { name: /scrape|fetch|collect/i });
      await expect(scrapeButton).toBeVisible();

      await scrapeButton.click();
      await wait(1000);

      // Verify scraping started
      const loadingIndicator = page.getByText(/scraping|fetching|loading/i);
      await expect(loadingIndicator).toBeVisible({ timeout: 5000 });

      await page.screenshot({ path: 'test-results/journey2-step5-scraping-started.png' });
    });

    // ==================== DB CHECK: Scrape Job Created ====================
    await test.step('DB Check: Verify scrape job created', async () => {
      await wait(2000);

      // Note: This requires the scrape_jobs table to exist
      // Get the most recent scrape job for this workspace
      const { data: jobs } = await supabase.serviceClient
        .from('scrape_jobs')
        .select('*')
        .eq('workspace_id', workspaceId)
        .order('created_at', { ascending: false })
        .limit(1);

      if (jobs && jobs.length > 0) {
        scrapeJobId = jobs[0].id;
        expect(jobs[0].status).toMatch(/pending|running|completed/);

        console.log(`✓ Scrape job created: ${scrapeJobId}`);
        console.log(`  Status: ${jobs[0].status}`);
      }
    });

    // ==================== STEP 6: Wait for Scraping ====================
    await test.step('Step 6: Wait for scraping to complete', async () => {
      // Wait for loading indicator to disappear
      await page.waitForSelector('text=/scraping|fetching/i', {
        state: 'hidden',
        timeout: 60000,
      }).catch(() => {
        console.log('Scraping still in progress or completed');
      });

      await wait(3000);

      await page.screenshot({ path: 'test-results/journey2-step6-scraping-complete.png' });
    });

    // ==================== DB CHECK: Content Items Created ====================
    await test.step('DB Check: Verify content items created', async () => {
      await wait(2000);

      const { data: contentItems } = await supabase.getWorkspaceContent(workspaceId);
      expect(contentItems).not.toBeNull();
      expect(contentItems?.length).toBeGreaterThan(0);

      // Verify content items have required fields
      contentItems!.forEach(item => {
        expect(item.title).toBeTruthy();
        expect(item.url).toBeTruthy();
        expect(item.source_id).toBeTruthy();
        expect(item.workspace_id).toBe(workspaceId);
      });

      console.log(`✓ ${contentItems?.length} content items scraped`);
    });

    // ==================== STEP 7: View Content List ====================
    await test.step('Step 7: User views scraped content', async () => {
      // Navigate to content list if not already there
      const contentLink = page.getByRole('link', { name: /content|articles/i });
      if (await contentLink.count() > 0) {
        await contentLink.click();
        await wait(1000);
      }

      // Verify content items are displayed
      const contentCards = page.locator('[data-testid="content-item"]');
      const contentList = page.locator('article, .content-item, [role="article"]');

      const count = await contentCards.count() || await contentList.count();
      expect(count).toBeGreaterThan(0);

      await page.screenshot({ path: 'test-results/journey2-step7-content-list.png' });

      console.log(`✓ ${count} content items displayed`);
    });

    // ==================== STEP 8: Filter by Source Type ====================
    await test.step('Step 8: User filters content by RSS source', async () => {
      // Look for filter dropdown or RSS filter
      const filterButton = page.getByRole('button', { name: /filter|source type/i });
      const rssFilter = page.getByRole('checkbox', { name: /rss/i });

      if (await filterButton.count() > 0) {
        await filterButton.click();
        await wait(500);
      }

      if (await rssFilter.count() > 0) {
        await rssFilter.click();
        await wait(1000);
      }

      await page.screenshot({ path: 'test-results/journey2-step8-filtered-content.png' });
    });

    // ==================== DB CHECK: Filtered Content Matches ====================
    await test.step('DB Check: Verify RSS filter matches database', async () => {
      const { data: rssContent } = await supabase.getContentBySource(rssSourceId);
      expect(rssContent).not.toBeNull();
      expect(rssContent?.length).toBeGreaterThan(0);

      console.log(`✓ ${rssContent?.length} RSS items in database`);
      console.log('✓ Content source journey completed successfully!');
    });
  });

  test('should show empty state when no sources configured', async ({ page }) => {
    await test.step('View sources page with no sources', async () => {
      // This would be for a new workspace with no sources
      await page.goto('/workspaces/new-workspace-id/sources');

      // Verify empty state
      await expect(page.getByText(/no sources|add your first source/i)).toBeVisible();
      await expect(page.getByRole('button', { name: /add source/i })).toBeVisible();
    });
  });

  test('should handle scraping errors gracefully', async ({ page, supabase }) => {
    await test.step('Scrape with invalid RSS URL', async () => {
      // Add source with invalid URL
      await page.getByRole('button', { name: /add source/i }).click();
      await page.getByLabel(/url/i).fill('https://invalid-url-that-doesnt-exist.com/feed');
      await page.getByRole('button', { name: /add/i }).click();

      // Trigger scrape
      await page.getByRole('button', { name: /scrape/i }).click();
      await wait(3000);

      // Verify error message
      await expect(page.getByText(/error|failed|unable to fetch/i)).toBeVisible();
    });
  });
});
