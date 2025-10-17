/**
 * E2E Test: User Journey 3 - Newsletter Generation & Sending
 *
 * User Story: As a user, I want to generate and send newsletters from scraped
 * content so my subscribers receive curated content.
 *
 * Flow:
 * 1. Navigate to newsletter page
 * 2. Select content items
 * 3. Configure newsletter settings
 * 4. Generate newsletter
 * 5. Preview generated content
 * 6. Add subscribers
 * 7. Send newsletter
 * 8. Verify delivery
 *
 * Each step verifies both frontend UI and backend database state.
 */

import { test, expect } from './fixtures/playwright-fixtures';
import {
  generateTestEmail,
  testNewsletters,
  testSubscribers,
  wait,
} from './fixtures/test-data';

test.describe('User Journey 3: Newsletter Generation & Sending', () => {
  let workspaceId: string;
  let userId: string;
  let newsletterId: string;
  let contentItemIds: string[] = [];
  let subscriberIds: string[] = [];

  test.beforeAll(() => {
    // Setup would create workspace with content items
  });

  test.afterAll(async ({ supabase }) => {
    // Cleanup
    if (newsletterId) {
      await supabase.serviceClient
        .from('newsletters')
        .delete()
        .eq('id', newsletterId);
    }
    if (workspaceId) {
      await supabase.cleanupTestWorkspace(workspaceId);
    }
  });

  test('should complete full newsletter generation and sending journey', async ({
    page,
    supabase,
  }) => {
    // ==================== STEP 1: Navigate to Newsletter ====================
    await test.step('Step 1: User navigates to Newsletter page', async () => {
      await page.goto('/login');
      // Assume login is handled
      await wait(1000);

      // Navigate to newsletter section
      const newsletterLink = page.getByRole('link', { name: /newsletter|generate/i });
      await newsletterLink.click();
      await wait(1000);

      // Verify we're on newsletter page
      await expect(page.url()).toMatch(/newsletter/);
      await expect(page.getByText(/generate newsletter|create newsletter/i)).toBeVisible();

      // Extract workspace ID from URL
      const urlMatch = page.url().match(/workspaces\/([a-f0-9-]+)/);
      if (urlMatch) {
        workspaceId = urlMatch[1];
      }

      await page.screenshot({ path: 'test-results/journey3-step1-newsletter-page.png' });
    });

    // ==================== DB CHECK: Get Content Items ====================
    await test.step('DB Check: Verify content items exist for selection', async () => {
      const { data: contentItems } = await supabase.getWorkspaceContent(workspaceId);
      expect(contentItems).not.toBeNull();
      expect(contentItems?.length).toBeGreaterThan(0);

      // Store content item IDs for later verification
      contentItemIds = contentItems!.slice(0, 5).map(item => item.id);

      console.log(`✓ ${contentItems?.length} content items available`);
    });

    // ==================== STEP 2: Select Content Items ====================
    await test.step('Step 2: User selects content items for newsletter', async () => {
      // Look for content selection interface
      const contentCards = page.locator('[data-testid="content-item"]');
      const checkboxes = page.locator('input[type="checkbox"][data-content-id]');

      // Select first 5-10 items
      const checkboxCount = await checkboxes.count();
      const selectCount = Math.min(checkboxCount, 5);

      for (let i = 0; i < selectCount; i++) {
        await checkboxes.nth(i).check();
        await wait(200);
      }

      // Verify selection count is displayed
      await expect(page.getByText(new RegExp(`${selectCount} selected|${selectCount} items`))).toBeVisible();

      await page.screenshot({ path: 'test-results/journey3-step2-content-selected.png' });

      console.log(`✓ Selected ${selectCount} content items`);
    });

    // ==================== STEP 3: Configure Newsletter ====================
    await test.step('Step 3: User configures newsletter settings', async () => {
      // Click "Next" or "Configure" to go to settings
      const nextButton = page.getByRole('button', { name: /next|configure|settings/i });
      if (await nextButton.count() > 0) {
        await nextButton.click();
        await wait(500);
      }

      // Fill newsletter configuration
      await page.getByLabel(/subject|title/i).fill(testNewsletters.weekly.subject);
      await page.getByLabel(/preview text|subtitle/i).fill(testNewsletters.weekly.previewText);

      // Select tone if available
      const toneDropdown = page.getByLabel(/tone|style/i);
      if (await toneDropdown.count() > 0) {
        await toneDropdown.click();
        await page.getByRole('option', { name: /professional/i }).click();
      }

      await page.screenshot({ path: 'test-results/journey3-step3-newsletter-config.png' });
    });

    // ==================== STEP 4: Generate Newsletter ====================
    await test.step('Step 4: User generates newsletter', async () => {
      // Click "Generate" button
      const generateButton = page.getByRole('button', { name: /generate/i });
      await expect(generateButton).toBeVisible();
      await generateButton.click();

      // Verify loading state
      await expect(page.getByText(/generating|creating|processing/i)).toBeVisible({ timeout: 5000 });

      await page.screenshot({ path: 'test-results/journey3-step4-generating.png' });

      console.log('✓ Newsletter generation started');
    });

    // ==================== DB CHECK: Newsletter Record Created ====================
    await test.step('DB Check: Verify newsletter record created', async () => {
      await wait(2000);

      // Get most recent newsletter for workspace
      const { data: newsletters } = await supabase.serviceClient
        .from('newsletters')
        .select('*')
        .eq('workspace_id', workspaceId)
        .order('created_at', { ascending: false })
        .limit(1);

      expect(newsletters).not.toBeNull();
      expect(newsletters?.length).toBeGreaterThan(0);

      const newsletter = newsletters![0];
      newsletterId = newsletter.id;

      expect(newsletter.workspace_id).toBe(workspaceId);
      expect(newsletter.status).toMatch(/generating|pending|completed/);

      console.log(`✓ Newsletter record created: ${newsletterId}`);
      console.log(`  Status: ${newsletter.status}`);
    });

    // ==================== STEP 5: Wait for Generation ====================
    await test.step('Step 5: Wait for newsletter generation to complete', async () => {
      // Poll for completion
      const isCompleted = await supabase.waitForNewsletterGeneration(newsletterId, 60000);
      expect(isCompleted).toBe(true);

      // Wait for UI to update
      await wait(2000);

      // Verify completion message or preview appears
      await expect(page.getByText(/generated|preview|ready/i)).toBeVisible({ timeout: 10000 });

      await page.screenshot({ path: 'test-results/journey3-step5-generation-complete.png' });

      console.log('✓ Newsletter generation completed');
    });

    // ==================== DB CHECK: Newsletter Has Content ====================
    await test.step('DB Check: Verify newsletter has generated content', async () => {
      const hasContent = await supabase.verifyNewsletterContent(newsletterId);
      expect(hasContent).toBe(true);

      const { data: newsletter } = await supabase.verifyNewsletter(newsletterId, workspaceId);
      expect(newsletter?.content_html).toBeTruthy();
      expect(newsletter?.status).toBe('completed');
      expect(newsletter?.generated_at).toBeTruthy();

      console.log('✓ Newsletter content verified in DB');
    });

    // ==================== STEP 6: Preview Newsletter ====================
    await test.step('Step 6: User previews generated newsletter', async () => {
      // Look for preview button or automatic preview display
      const previewButton = page.getByRole('button', { name: /preview/i });
      if (await previewButton.count() > 0) {
        await previewButton.click();
        await wait(500);
      }

      // Verify newsletter content is displayed
      const previewContainer = page.locator('[data-testid="newsletter-preview"]');
      const previewFrame = page.frameLocator('iframe[title="Newsletter Preview"]');

      // Check either preview container or iframe exists
      const hasPreview = await previewContainer.count() > 0 || await page.locator('iframe').count() > 0;
      expect(hasPreview).toBe(true);

      await page.screenshot({ path: 'test-results/journey3-step6-newsletter-preview.png' });

      console.log('✓ Newsletter preview displayed');
    });

    // ==================== STEP 7: Add Subscribers ====================
    await test.step('Step 7: User adds subscribers', async () => {
      // Navigate to subscribers section
      const subscribersButton = page.getByRole('button', { name: /subscribers|recipients/i });
      const subscribersLink = page.getByRole('link', { name: /subscribers|manage/i });

      if (await subscribersButton.count() > 0) {
        await subscribersButton.click();
      } else if (await subscribersLink.count() > 0) {
        await subscribersLink.click();
      }

      await wait(1000);

      // Add subscribers
      for (const subscriber of testSubscribers) {
        const addButton = page.getByRole('button', { name: /add subscriber|\+/i });
        await addButton.click();
        await wait(500);

        await page.getByLabel(/email/i).fill(subscriber.email);
        const nameField = page.getByLabel(/name/i);
        if (await nameField.count() > 0) {
          await nameField.fill(subscriber.name);
        }

        await page.getByRole('button', { name: /add|save/i }).click();
        await wait(1000);
      }

      // Verify subscribers are shown
      for (const subscriber of testSubscribers) {
        await expect(page.getByText(subscriber.email)).toBeVisible();
      }

      await page.screenshot({ path: 'test-results/journey3-step7-subscribers-added.png' });

      console.log(`✓ Added ${testSubscribers.length} subscribers`);
    });

    // ==================== DB CHECK: Subscribers Created ====================
    await test.step('DB Check: Verify subscribers in database', async () => {
      const { data: subscribers } = await supabase.getWorkspaceSubscribers(workspaceId);
      expect(subscribers).not.toBeNull();
      expect(subscribers?.length).toBeGreaterThanOrEqual(testSubscribers.length);

      // Store subscriber IDs
      subscriberIds = subscribers!.map(s => s.id);

      // Verify each test subscriber exists
      for (const testSub of testSubscribers) {
        const found = subscribers!.find(s => s.email === testSub.email);
        expect(found).toBeDefined();
        expect(found?.workspace_id).toBe(workspaceId);
      }

      console.log(`✓ ${subscribers?.length} subscribers verified in DB`);
    });

    // ==================== STEP 8: Send Newsletter ====================
    await test.step('Step 8: User sends newsletter', async () => {
      // Navigate back to newsletter if needed
      const sendButton = page.getByRole('button', { name: /send now|send newsletter/i });
      await expect(sendButton).toBeVisible();

      // Click send
      await sendButton.click();
      await wait(500);

      // Confirm in dialog if present
      const confirmButton = page.getByRole('button', { name: /confirm|yes|send/i });
      if (await confirmButton.count() > 0) {
        await confirmButton.click();
      }

      // Verify sending started
      await expect(page.getByText(/sending|queued/i)).toBeVisible({ timeout: 5000 });

      await page.screenshot({ path: 'test-results/journey3-step8-sending.png' });

      console.log('✓ Newsletter send initiated');
    });

    // ==================== DB CHECK: Newsletter Status = Sending ====================
    await test.step('DB Check: Verify newsletter status changed to sending', async () => {
      await wait(2000);

      const isSending = await supabase.verifyNewsletterStatus(newsletterId, 'sending');
      const isSent = await supabase.verifyNewsletterStatus(newsletterId, 'sent');

      expect(isSending || isSent).toBe(true);

      console.log('✓ Newsletter status updated in DB');
    });

    // ==================== STEP 9: Verify Delivery ====================
    await test.step('Step 9: Verify email delivery status', async () => {
      // Wait for sending to complete
      await wait(5000);

      // Check for completion message
      await expect(page.getByText(/sent|delivered|completed/i)).toBeVisible({ timeout: 15000 });

      await page.screenshot({ path: 'test-results/journey3-step9-sent.png' });

      console.log('✓ Newsletter sent successfully');
    });

    // ==================== DB CHECK: Delivery Logs ====================
    await test.step('DB Check: Verify email delivery logs', async () => {
      // Check newsletter status is sent
      const { data: newsletter } = await supabase.verifyNewsletter(newsletterId, workspaceId);
      expect(newsletter?.status).toBe('sent');
      expect(newsletter?.sent_at).toBeTruthy();

      // Check delivery logs if table exists
      const { data: deliveryLogs } = await supabase.serviceClient
        .from('email_delivery_log')
        .select('*')
        .eq('newsletter_id', newsletterId);

      if (deliveryLogs) {
        expect(deliveryLogs.length).toBeGreaterThan(0);
        console.log(`✓ ${deliveryLogs.length} delivery log entries created`);
      }

      console.log('✓ Newsletter generation and sending journey completed successfully!');
    });
  });

  test('should allow editing newsletter before sending', async ({ page }) => {
    await test.step('Edit newsletter content', async () => {
      // After generation, click edit button
      const editButton = page.getByRole('button', { name: /edit/i });
      await editButton.click();
      await wait(500);

      // Modify subject
      await page.getByLabel(/subject/i).fill('Updated Subject Line');

      // Save changes
      await page.getByRole('button', { name: /save/i }).click();
      await wait(1000);

      // Verify changes saved
      await expect(page.getByText('Updated Subject Line')).toBeVisible();
    });
  });

  test('should prevent sending newsletter without subscribers', async ({ page }) => {
    await test.step('Attempt to send without subscribers', async () => {
      // On newsletter page with no subscribers
      const sendButton = page.getByRole('button', { name: /send/i });

      // Button should be disabled or show warning
      const isDisabled = await sendButton.isDisabled();
      if (!isDisabled) {
        await sendButton.click();
        // Should show error message
        await expect(page.getByText(/no subscribers|add subscribers first/i)).toBeVisible();
      }
    });
  });

  test('should allow scheduling newsletter for later', async ({ page, supabase }) => {
    await test.step('Schedule newsletter instead of immediate send', async () => {
      // After generation, look for schedule option
      const scheduleButton = page.getByRole('button', { name: /schedule/i });
      await scheduleButton.click();
      await wait(500);

      // Select date and time
      await page.getByLabel(/date/i).fill('2025-12-31');
      await page.getByLabel(/time/i).fill('09:00');

      // Confirm schedule
      await page.getByRole('button', { name: /schedule|confirm/i }).click();
      await wait(2000);

      // Verify scheduled message
      await expect(page.getByText(/scheduled|will be sent/i)).toBeVisible();
    });
  });
});
