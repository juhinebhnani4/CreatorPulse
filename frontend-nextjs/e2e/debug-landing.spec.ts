/**
 * Debug test to see what's actually on the landing page
 */
import { test, expect } from '@playwright/test';

test.describe('Debug Landing Page', () => {
  test('should show page content', async ({ page }) => {
    await page.goto('http://localhost:3000/');

    // Wait for page to load
    await page.waitForLoadState('networkidle');

    // Get the full page content
    const html = await page.content();
    console.log('=== FULL PAGE HTML ===');
    console.log(html);

    // Try to find h1
    const h1Elements = await page.locator('h1').all();
    console.log(`\n=== FOUND ${h1Elements.length} H1 ELEMENTS ===`);
    for (const h1 of h1Elements) {
      const text = await h1.textContent();
      const tag = await h1.evaluate(el => el.tagName);
      console.log(`<${tag}>${text}</${tag}>`);
    }

    // Try to find all headings
    const headings = await page.locator('h1, h2, h3, h4, h5, h6').all();
    console.log(`\n=== FOUND ${headings.length} TOTAL HEADINGS ===`);
    for (const heading of headings) {
      const text = await heading.textContent();
      const tag = await heading.evaluate(el => el.tagName);
      console.log(`<${tag}>${text}</${tag}>`);
    }

    // Try to find links
    const links = await page.locator('a').all();
    console.log(`\n=== FOUND ${links.length} LINKS ===`);
    for (const link of links) {
      const text = await link.textContent();
      const href = await link.getAttribute('href');
      console.log(`<a href="${href}">${text}</a>`);
    }

    // Take a screenshot
    await page.screenshot({ path: 'test-results/debug-landing.png', fullPage: true });
    console.log('\n=== Screenshot saved to test-results/debug-landing.png ===');
  });

  test('should show register page content', async ({ page }) => {
    await page.goto('http://localhost:3000/register');

    // Wait for page to load
    await page.waitForLoadState('networkidle');

    // Try to find all headings
    const headings = await page.locator('h1, h2, h3, h4, h5, h6').all();
    console.log(`\n=== REGISTER PAGE: FOUND ${headings.length} HEADINGS ===`);
    for (const heading of headings) {
      const text = await heading.textContent();
      const tag = await heading.evaluate(el => el.tagName);
      console.log(`<${tag}>${text}</${tag}>`);
    }

    // Take a screenshot
    await page.screenshot({ path: 'test-results/debug-register.png', fullPage: true });
    console.log('\n=== Screenshot saved to test-results/debug-register.png ===');
  });
});
