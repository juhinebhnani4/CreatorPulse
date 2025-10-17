/**
 * CONFIG-DRIVEN TEST APPROACH
 *
 * This template allows you to define tests using JSON configuration instead of code.
 * Perfect for:
 * - Non-developers who want to create tests
 * - Rapid test creation
 * - Standardized test patterns
 * - Data-driven testing
 *
 * HOW IT WORKS:
 * 1. Define your journey steps in a JSON config
 * 2. The test runner executes each step automatically
 * 3. No coding required!
 *
 * EXAMPLE:
 * See the example configurations below and in e2e/configs/ folder
 */

import { test, expect, Page } from '@playwright/test';

// ============================================================================
// TYPE DEFINITIONS FOR CONFIG
// ============================================================================

export type StepAction =
  | 'navigate'
  | 'click'
  | 'fill'
  | 'select'
  | 'check'
  | 'uncheck'
  | 'upload'
  | 'wait'
  | 'verify_visible'
  | 'verify_text'
  | 'verify_url'
  | 'verify_not_visible'
  | 'screenshot'
  | 'wait_for_navigation';

export interface Selector {
  role?: string;
  name?: string;
  text?: string;
  label?: string;
  placeholder?: string;
  testId?: string;
  css?: string;
  exact?: boolean;
}

export interface TestStep {
  name: string;
  action: StepAction;
  selector?: Selector;
  value?: string | string[];
  url?: string;
  urlPattern?: string;
  timeout?: number;
  description?: string;
  screenshot?: boolean;
}

export interface TestJourneyConfig {
  name: string;
  description: string;
  tags?: string[];
  beforeEach?: TestStep[];
  afterEach?: TestStep[];
  steps: TestStep[];
  timeout?: number;
  retries?: number;
}

// ============================================================================
// STEP EXECUTOR - Executes individual test steps
// ============================================================================

export class StepExecutor {
  constructor(private page: Page) {}

  async execute(step: TestStep): Promise<void> {
    console.log(`\n📍 ${step.name}`);
    if (step.description) {
      console.log(`   ${step.description}`);
    }

    await test.step(step.name, async () => {
      switch (step.action) {
        case 'navigate':
          await this.handleNavigate(step);
          break;
        case 'click':
          await this.handleClick(step);
          break;
        case 'fill':
          await this.handleFill(step);
          break;
        case 'select':
          await this.handleSelect(step);
          break;
        case 'check':
          await this.handleCheck(step, true);
          break;
        case 'uncheck':
          await this.handleCheck(step, false);
          break;
        case 'upload':
          await this.handleUpload(step);
          break;
        case 'wait':
          await this.handleWait(step);
          break;
        case 'wait_for_navigation':
          await this.handleWaitForNavigation(step);
          break;
        case 'verify_visible':
          await this.handleVerifyVisible(step, true);
          break;
        case 'verify_not_visible':
          await this.handleVerifyVisible(step, false);
          break;
        case 'verify_text':
          await this.handleVerifyText(step);
          break;
        case 'verify_url':
          await this.handleVerifyUrl(step);
          break;
        case 'screenshot':
          await this.handleScreenshot(step);
          break;
        default:
          throw new Error(`Unknown action: ${step.action}`);
      }

      if (step.screenshot) {
        await this.handleScreenshot(step);
      }
    });
  }

  private async findElement(selector: Selector) {
    const { role, name, text, label, placeholder, testId, css, exact = false } = selector;

    if (role && name) {
      return this.page.getByRole(role as any, { name, exact });
    }
    if (text) {
      return this.page.getByText(text, { exact });
    }
    if (label) {
      return this.page.getByLabel(label, { exact });
    }
    if (placeholder) {
      return this.page.getByPlaceholder(placeholder, { exact });
    }
    if (testId) {
      return this.page.getByTestId(testId);
    }
    if (css) {
      return this.page.locator(css);
    }

    throw new Error('No valid selector provided');
  }

  private async handleNavigate(step: TestStep): Promise<void> {
    if (!step.url) throw new Error('Navigate action requires url');
    await this.page.goto(step.url);
    await this.page.waitForLoadState('networkidle');
  }

  private async handleClick(step: TestStep): Promise<void> {
    if (!step.selector) throw new Error('Click action requires selector');
    const element = await this.findElement(step.selector);
    await element.click({ timeout: step.timeout });
  }

  private async handleFill(step: TestStep): Promise<void> {
    if (!step.selector || !step.value) {
      throw new Error('Fill action requires selector and value');
    }
    const element = await this.findElement(step.selector);
    await element.fill(step.value as string);
  }

  private async handleSelect(step: TestStep): Promise<void> {
    if (!step.selector || !step.value) {
      throw new Error('Select action requires selector and value');
    }
    const element = await this.findElement(step.selector);
    await element.selectOption(step.value);
  }

  private async handleCheck(step: TestStep, shouldCheck: boolean): Promise<void> {
    if (!step.selector) throw new Error('Check action requires selector');
    const element = await this.findElement(step.selector);

    if (shouldCheck) {
      await element.check();
    } else {
      await element.uncheck();
    }
  }

  private async handleUpload(step: TestStep): Promise<void> {
    if (!step.selector || !step.value) {
      throw new Error('Upload action requires selector and value (file path)');
    }
    const element = await this.findElement(step.selector);
    await element.setInputFiles(step.value);
  }

  private async handleWait(step: TestStep): Promise<void> {
    const timeout = step.timeout || 1000;
    await this.page.waitForTimeout(timeout);
  }

  private async handleWaitForNavigation(step: TestStep): Promise<void> {
    if (!step.urlPattern) {
      throw new Error('Wait for navigation requires urlPattern');
    }
    await this.page.waitForURL(new RegExp(step.urlPattern), {
      timeout: step.timeout || 15000,
    });
  }

  private async handleVerifyVisible(step: TestStep, shouldBeVisible: boolean): Promise<void> {
    if (!step.selector) throw new Error('Verify visible requires selector');
    const element = await this.findElement(step.selector);

    if (shouldBeVisible) {
      await expect(element).toBeVisible({ timeout: step.timeout || 10000 });
    } else {
      await expect(element).not.toBeVisible({ timeout: step.timeout || 10000 });
    }
  }

  private async handleVerifyText(step: TestStep): Promise<void> {
    if (!step.value) throw new Error('Verify text requires value');
    await expect(this.page.getByText(step.value as string)).toBeVisible({
      timeout: step.timeout || 10000,
    });
  }

  private async handleVerifyUrl(step: TestStep): Promise<void> {
    if (!step.urlPattern) throw new Error('Verify URL requires urlPattern');
    await expect(this.page).toHaveURL(new RegExp(step.urlPattern), {
      timeout: step.timeout || 10000,
    });
  }

  private async handleScreenshot(step: TestStep): Promise<void> {
    const filename = step.name.toLowerCase().replace(/\s+/g, '-');
    await this.page.screenshot({
      path: `test-results/${filename}-${Date.now()}.png`,
      fullPage: true,
    });
  }
}

// ============================================================================
// JOURNEY RUNNER - Executes entire test journey from config
// ============================================================================

export class JourneyRunner {
  private executor: StepExecutor;

  constructor(private page: Page, private config: TestJourneyConfig) {
    this.executor = new StepExecutor(page);
  }

  async runBeforeEach(): Promise<void> {
    if (!this.config.beforeEach?.length) return;

    console.log('\n🔧 Running beforeEach hooks...');
    for (const step of this.config.beforeEach) {
      await this.executor.execute(step);
    }
  }

  async runAfterEach(): Promise<void> {
    if (!this.config.afterEach?.length) return;

    console.log('\n🧹 Running afterEach hooks...');
    for (const step of this.config.afterEach) {
      await this.executor.execute(step);
    }
  }

  async run(): Promise<void> {
    console.log(`\n🚀 Starting journey: ${this.config.name}`);
    console.log(`   ${this.config.description}\n`);

    for (const step of this.config.steps) {
      await this.executor.execute(step);
    }

    console.log(`\n✅ Journey completed: ${this.config.name}`);
  }
}

// ============================================================================
// TEST FACTORY - Creates Playwright tests from config
// ============================================================================

export function createTestFromConfig(config: TestJourneyConfig): void {
  test.describe(config.name, () => {
    if (config.timeout) {
      test.setTimeout(config.timeout);
    }

    test(config.description, async ({ page }) => {
      const runner = new JourneyRunner(page, config);

      // Run beforeEach steps
      await runner.runBeforeEach();

      try {
        // Run main journey
        await runner.run();
      } finally {
        // Run afterEach steps (always run, even if test fails)
        await runner.runAfterEach();
      }
    });
  });
}

// ============================================================================
// EXAMPLE CONFIGURATIONS
// ============================================================================

/**
 * Example 1: Simple login flow
 */
export const exampleLoginJourney: TestJourneyConfig = {
  name: 'User Login Journey',
  description: 'Tests the complete login flow',
  tags: ['auth', 'smoke'],
  timeout: 30000,
  steps: [
    {
      name: 'Navigate to login page',
      action: 'navigate',
      url: '/login',
      screenshot: true,
    },
    {
      name: 'Fill email field',
      action: 'fill',
      selector: { label: /email/i },
      value: 'test@example.com',
    },
    {
      name: 'Fill password field',
      action: 'fill',
      selector: { label: /password/i },
      value: 'SecurePass123!',
    },
    {
      name: 'Click login button',
      action: 'click',
      selector: { role: 'button', name: /sign in|login/i },
    },
    {
      name: 'Wait for redirect to dashboard',
      action: 'wait_for_navigation',
      urlPattern: '/app|/dashboard',
      timeout: 15000,
    },
    {
      name: 'Verify user menu is visible',
      action: 'verify_visible',
      selector: { role: 'button', name: /profile|account/i },
    },
    {
      name: 'Take final screenshot',
      action: 'screenshot',
      screenshot: true,
    },
  ],
};

/**
 * Example 2: Registration flow with data generation
 */
export const exampleRegistrationJourney: TestJourneyConfig = {
  name: 'User Registration Journey',
  description: 'Tests new user signup process',
  tags: ['auth', 'critical'],
  steps: [
    {
      name: 'Navigate to landing page',
      action: 'navigate',
      url: '/',
    },
    {
      name: 'Click Get Started',
      action: 'click',
      selector: { role: 'link', name: /get started/i },
    },
    {
      name: 'Fill name',
      action: 'fill',
      selector: { label: /name/i },
      value: 'Test User', // You can use generateTestData() in code
    },
    {
      name: 'Fill email',
      action: 'fill',
      selector: { label: /email/i },
      value: 'test-1234@example.com',
    },
    {
      name: 'Fill password',
      action: 'fill',
      selector: { label: /password/i },
      value: 'SecurePass123!',
    },
    {
      name: 'Click create account',
      action: 'click',
      selector: { role: 'button', name: /create account/i },
    },
    {
      name: 'Wait for dashboard',
      action: 'wait_for_navigation',
      urlPattern: '/app',
    },
    {
      name: 'Verify successful registration',
      action: 'verify_visible',
      selector: { text: /welcome/i },
    },
  ],
};

/**
 * Example 3: CRUD operations
 */
export const exampleCRUDJourney: TestJourneyConfig = {
  name: 'Content Source CRUD Journey',
  description: 'Create, Read, Update, Delete content source',
  beforeEach: [
    {
      name: 'Login',
      action: 'navigate',
      url: '/login',
    },
    // Add login steps...
  ],
  steps: [
    // CREATE
    {
      name: 'Navigate to sources page',
      action: 'navigate',
      url: '/app/sources',
    },
    {
      name: 'Click Add Source button',
      action: 'click',
      selector: { role: 'button', name: /add source/i },
    },
    {
      name: 'Fill source name',
      action: 'fill',
      selector: { label: /name/i },
      value: 'Test Source',
    },
    {
      name: 'Fill source URL',
      action: 'fill',
      selector: { label: /url/i },
      value: 'https://example.com/feed',
    },
    {
      name: 'Save source',
      action: 'click',
      selector: { role: 'button', name: /save|create/i },
    },

    // READ
    {
      name: 'Verify source appears in list',
      action: 'verify_text',
      value: 'Test Source',
    },

    // UPDATE
    {
      name: 'Click edit on source',
      action: 'click',
      selector: { role: 'button', name: /edit/i },
    },
    {
      name: 'Update source name',
      action: 'fill',
      selector: { label: /name/i },
      value: 'Updated Test Source',
    },
    {
      name: 'Save changes',
      action: 'click',
      selector: { role: 'button', name: /save|update/i },
    },
    {
      name: 'Verify updated name',
      action: 'verify_text',
      value: 'Updated Test Source',
    },

    // DELETE
    {
      name: 'Click delete button',
      action: 'click',
      selector: { role: 'button', name: /delete/i },
    },
    {
      name: 'Confirm deletion',
      action: 'click',
      selector: { role: 'button', name: /confirm|yes/i },
    },
    {
      name: 'Verify source removed',
      action: 'verify_not_visible',
      selector: { text: 'Updated Test Source' },
    },
  ],
};

/**
 * Example 4: Multi-page navigation flow
 */
export const exampleNavigationJourney: TestJourneyConfig = {
  name: 'Multi-Page Navigation',
  description: 'Test navigation through multiple pages',
  steps: [
    {
      name: 'Start at home',
      action: 'navigate',
      url: '/',
    },
    {
      name: 'Go to features page',
      action: 'click',
      selector: { role: 'link', name: /features/i },
    },
    {
      name: 'Verify on features page',
      action: 'verify_url',
      urlPattern: '/features',
    },
    {
      name: 'Go to pricing',
      action: 'click',
      selector: { role: 'link', name: /pricing/i },
    },
    {
      name: 'Verify on pricing page',
      action: 'verify_url',
      urlPattern: '/pricing',
    },
    {
      name: 'Return to home',
      action: 'click',
      selector: { role: 'link', name: /home|logo/i },
    },
    {
      name: 'Verify back on home',
      action: 'verify_url',
      urlPattern: '^/$',
    },
  ],
};

// ============================================================================
// LOAD CONFIG FROM JSON FILE
// ============================================================================

/**
 * Load test configuration from JSON file
 */
export async function loadConfigFromFile(filePath: string): Promise<TestJourneyConfig> {
  const fs = await import('fs/promises');
  const content = await fs.readFile(filePath, 'utf-8');
  return JSON.parse(content) as TestJourneyConfig;
}

/**
 * Load and run test from JSON file
 */
export async function runTestFromFile(filePath: string): Promise<void> {
  const config = await loadConfigFromFile(filePath);
  createTestFromConfig(config);
}

// ============================================================================
// USAGE EXAMPLE
// ============================================================================

/**
 * Example: How to use config-driven tests in your spec file
 */

// Approach 1: Inline config
// createTestFromConfig(exampleLoginJourney);

// Approach 2: Load from JSON file
// runTestFromFile('./e2e/configs/user-registration.json');

// Approach 3: Multiple configs
// const configs = [
//   exampleLoginJourney,
//   exampleRegistrationJourney,
//   exampleCRUDJourney,
// ];
//
// configs.forEach(config => createTestFromConfig(config));

// ============================================================================
// JSON SCHEMA FOR CONFIG FILES
// ============================================================================

export const configSchema = {
  $schema: 'http://json-schema.org/draft-07/schema#',
  type: 'object',
  required: ['name', 'description', 'steps'],
  properties: {
    name: { type: 'string' },
    description: { type: 'string' },
    tags: { type: 'array', items: { type: 'string' } },
    timeout: { type: 'number' },
    retries: { type: 'number' },
    beforeEach: { type: 'array', items: { $ref: '#/definitions/step' } },
    afterEach: { type: 'array', items: { $ref: '#/definitions/step' } },
    steps: {
      type: 'array',
      items: { $ref: '#/definitions/step' },
    },
  },
  definitions: {
    step: {
      type: 'object',
      required: ['name', 'action'],
      properties: {
        name: { type: 'string' },
        action: {
          type: 'string',
          enum: [
            'navigate',
            'click',
            'fill',
            'select',
            'check',
            'uncheck',
            'upload',
            'wait',
            'wait_for_navigation',
            'verify_visible',
            'verify_not_visible',
            'verify_text',
            'verify_url',
            'screenshot',
          ],
        },
        selector: { type: 'object' },
        value: { type: ['string', 'array'] },
        url: { type: 'string' },
        urlPattern: { type: 'string' },
        timeout: { type: 'number' },
        description: { type: 'string' },
        screenshot: { type: 'boolean' },
      },
    },
  },
};
