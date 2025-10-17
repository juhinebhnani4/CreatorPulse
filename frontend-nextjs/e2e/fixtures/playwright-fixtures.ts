/**
 * Playwright Test Fixtures
 *
 * Extends Playwright test with custom fixtures for Supabase and test data.
 */

import { test as base, expect } from '@playwright/test';
import { supabaseHelper, SupabaseTestHelper } from '../utils/supabase-helper';

// Extend test context with custom fixtures
type TestFixtures = {
  supabase: SupabaseTestHelper;
  testStartTime: Date;
};

/**
 * Extended Playwright test with custom fixtures
 */
export const test = base.extend<TestFixtures>({
  // Supabase helper instance
  supabase: async ({}, use) => {
    await use(supabaseHelper);
  },

  // Track test start time for cleanup
  testStartTime: async ({}, use) => {
    const startTime = new Date();
    await use(startTime);
  },
});

export { expect };
