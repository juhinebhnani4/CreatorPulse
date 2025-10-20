/**
 * PAGE OBJECT MODEL (POM) TEMPLATE
 *
 * The Page Object Model is a design pattern that creates an abstraction layer
 * between tests and page interactions. Benefits:
 * - Reusable page interactions
 * - Easy maintenance (update in one place)
 * - More readable tests
 * - Encapsulates page structure
 *
 * HOW TO USE:
 * 1. Create a class for each page/component
 * 2. Define selectors and methods for interactions
 * 3. Use in your tests instead of direct page.* calls
 *
 * EXAMPLE:
 * const loginPage = new LoginPage(page);
 * await loginPage.login('user@example.com', 'password');
 */

import { Page, Locator, expect } from '@playwright/test';

// ============================================================================
// BASE PAGE CLASS - All page objects extend this
// ============================================================================

export class BasePage {
  protected page: Page;
  protected baseUrl: string;

  constructor(page: Page, baseUrl: string = '') {
    this.page = page;
    this.baseUrl = baseUrl;
  }

  /**
   * Navigate to this page
   */
  async goto(path: string = ''): Promise<void> {
    const url = this.baseUrl + path;
    await this.page.goto(url);
  }

  /**
   * Wait for page to be fully loaded
   */
  async waitForPageLoad(): Promise<void> {
    await this.page.waitForLoadState('networkidle');
  }

  /**
   * Take screenshot of current page
   */
  async screenshot(name: string): Promise<void> {
    await this.page.screenshot({
      path: `test-results/${name}.png`,
      fullPage: true,
    });
  }

  /**
   * Check if element is visible
   */
  async isVisible(locator: Locator): Promise<boolean> {
    try {
      await locator.waitFor({ state: 'visible', timeout: 5000 });
      return true;
    } catch {
      return false;
    }
  }

  /**
   * Wait for navigation to complete
   */
  async waitForUrl(urlPattern: string | RegExp, timeout: number = 10000): Promise<void> {
    await this.page.waitForURL(urlPattern, { timeout });
  }

  /**
   * Get current URL
   */
  getCurrentUrl(): string {
    return this.page.url();
  }

  /**
   * Refresh the page
   */
  async refresh(): Promise<void> {
    await this.page.reload();
  }

  /**
   * Go back in browser history
   */
  async goBack(): Promise<void> {
    await this.page.goBack();
  }

  /**
   * Click with retry logic
   */
  async clickWithRetry(locator: Locator, maxRetries: number = 3): Promise<void> {
    for (let i = 0; i < maxRetries; i++) {
      try {
        await locator.click({ timeout: 5000 });
        return;
      } catch (error) {
        if (i === maxRetries - 1) throw error;
        await this.page.waitForTimeout(1000);
      }
    }
  }

  /**
   * Fill field with validation check
   */
  async fillAndVerify(locator: Locator, value: string): Promise<void> {
    await locator.fill(value);
    await expect(locator).toHaveValue(value);
  }
}

// ============================================================================
// LANDING PAGE - Example implementation
// ============================================================================

export class LandingPage extends BasePage {
  // Selectors (centralized)
  private selectors = {
    heading: 'h1',
    getStartedBtn: '[data-testid="get-started"], a:has-text("Get Started")',
    loginLink: 'a:has-text("Login"), a:has-text("Sign in")',
    featuresSection: '[data-testid="features"]',
  };

  constructor(page: Page) {
    super(page, '/');
  }

  // Locators (lazy-loaded)
  get heading(): Locator {
    return this.page.locator(this.selectors.heading);
  }

  get getStartedButton(): Locator {
    return this.page.locator(this.selectors.getStartedBtn).first();
  }

  get loginLink(): Locator {
    return this.page.locator(this.selectors.loginLink).first();
  }

  // Actions
  async clickGetStarted(): Promise<void> {
    await this.getStartedButton.click();
  }

  async clickLogin(): Promise<void> {
    await this.loginLink.click();
  }

  async verifyPageLoaded(): Promise<void> {
    await expect(this.heading).toBeVisible({ timeout: 10000 });
  }

  async navigateToSignup(): Promise<void> {
    await this.clickGetStarted();
    await this.waitForUrl(/register|signup/i);
  }

  async navigateToLogin(): Promise<void> {
    await this.clickLogin();
    await this.waitForUrl(/login|signin/i);
  }
}

// ============================================================================
// AUTH PAGE - Login & Registration
// ============================================================================

export class AuthPage extends BasePage {
  private selectors = {
    // Common fields
    emailInput: 'input[type="email"], input[name="email"]',
    passwordInput: 'input[type="password"], input[name="password"]',

    // Registration specific
    nameInput: 'input[name="name"], input[name="username"]',
    confirmPasswordInput: 'input[name="confirmPassword"]',
    signupButton: 'button:has-text("Create Account"), button:has-text("Sign Up")',

    // Login specific
    loginButton: 'button:has-text("Sign In"), button:has-text("Login")',

    // Links
    switchToLoginLink: 'a:has-text("Sign in"), a:has-text("Login")',
    switchToSignupLink: 'a:has-text("Sign up"), a:has-text("Register")',

    // Error messages
    errorMessage: '[role="alert"], .error, .text-red-500',
  };

  constructor(page: Page, isLogin: boolean = true) {
    super(page, isLogin ? '/login' : '/register');
  }

  // Locators
  get emailInput(): Locator {
    return this.page.locator(this.selectors.emailInput).first();
  }

  get passwordInput(): Locator {
    return this.page.locator(this.selectors.passwordInput).first();
  }

  get nameInput(): Locator {
    return this.page.locator(this.selectors.nameInput).first();
  }

  get loginButton(): Locator {
    return this.page.locator(this.selectors.loginButton).first();
  }

  get signupButton(): Locator {
    return this.page.locator(this.selectors.signupButton).first();
  }

  get errorMessage(): Locator {
    return this.page.locator(this.selectors.errorMessage).first();
  }

  // Actions - Login
  async login(email: string, password: string): Promise<void> {
    await this.fillAndVerify(this.emailInput, email);
    await this.fillAndVerify(this.passwordInput, password);
    await this.loginButton.click();
  }

  async loginAndWait(email: string, password: string, expectedUrl: string | RegExp = /app|dashboard/i): Promise<void> {
    await this.login(email, password);
    await this.waitForUrl(expectedUrl, 15000);
  }

  // Actions - Registration
  async register(name: string, email: string, password: string): Promise<void> {
    await this.fillAndVerify(this.nameInput, name);
    await this.fillAndVerify(this.emailInput, email);
    await this.fillAndVerify(this.passwordInput, password);
    await this.signupButton.click();
  }

  async registerAndWait(
    name: string,
    email: string,
    password: string,
    expectedUrl: string | RegExp = /app|dashboard/i
  ): Promise<void> {
    await this.register(name, email, password);
    await this.waitForUrl(expectedUrl, 15000);
  }

  // Verifications
  async verifyLoginPage(): Promise<void> {
    // Verify URL first (best practice)
    await expect(this.page).toHaveURL(/\/login/);

    // Use accessible selector with specific text from the app
    await expect(
      this.page.getByRole('heading', { name: /welcome back/i })
    ).toBeVisible();
  }

  async verifySignupPage(): Promise<void> {
    // Verify URL first (best practice)
    await expect(this.page).toHaveURL(/\/register/);

    // Use accessible selector with specific text from the app
    await expect(
      this.page.getByRole('heading', { name: /create your account/i })
    ).toBeVisible();
  }

  async verifyErrorShown(errorText?: string | RegExp): Promise<void> {
    await expect(this.errorMessage).toBeVisible();
    if (errorText) {
      await expect(this.errorMessage).toContainText(errorText);
    }
  }

  // Navigation
  async switchToLogin(): Promise<void> {
    await this.page.locator(this.selectors.switchToLoginLink).first().click();
    await this.waitForUrl(/login|signin/i);
  }

  async switchToSignup(): Promise<void> {
    await this.page.locator(this.selectors.switchToSignupLink).first().click();
    await this.waitForUrl(/register|signup/i);
  }
}

// ============================================================================
// DASHBOARD PAGE - Main app page
// ============================================================================

export class DashboardPage extends BasePage {
  private selectors = {
    heading: 'h1, h2',
    userMenu: '[data-testid="user-menu"], button:has-text("juhinebhnani4"), header button[type="button"]:last-child',
    logoutButton: 'button:has-text("Logout"), button:has-text("Sign Out")',
    createButton: 'button:has-text("Create"), button:has-text("Add"), button:has-text("New")',
    searchInput: 'input[type="search"], input[placeholder*="Search"]',
    navLinks: '[role="navigation"] a',
  };

  constructor(page: Page) {
    super(page, '/app');
  }

  // Locators
  get heading(): Locator {
    return this.page.locator(this.selectors.heading).first();
  }

  get userMenu(): Locator {
    return this.page.locator(this.selectors.userMenu).first();
  }

  get createButton(): Locator {
    return this.page.locator(this.selectors.createButton).first();
  }

  // Actions
  async verifyDashboardLoaded(): Promise<void> {
    // Verify URL first
    await expect(this.page).toHaveURL(/\/app/);

    // Verify heading is visible
    await expect(this.heading).toBeVisible({ timeout: 10000 });

    // Verify user menu is visible (more flexible check)
    const userMenuVisible = await this.userMenu.isVisible().catch(() => false);
    if (!userMenuVisible) {
      // If specific user menu not found, just verify we have navigation
      await expect(this.page.locator('nav')).toBeVisible();
    }
  }

  async clickCreate(): Promise<void> {
    await this.createButton.click();
  }

  async logout(): Promise<void> {
    await this.userMenu.click();
    await this.page.locator(this.selectors.logoutButton).first().click();
  }

  async search(query: string): Promise<void> {
    await this.page.locator(this.selectors.searchInput).first().fill(query);
    await this.page.keyboard.press('Enter');
  }

  async navigateToSection(sectionName: string): Promise<void> {
    await this.page.locator(this.selectors.navLinks).filter({ hasText: sectionName }).first().click();
  }
}

// ============================================================================
// MODAL/DIALOG COMPONENT - Reusable modal interactions
// ============================================================================

export class Modal {
  private page: Page;
  private selectors = {
    modal: '[role="dialog"], .modal',
    closeButton: 'button:has-text("Close"), button[aria-label="Close"]',
    confirmButton: 'button:has-text("Confirm"), button:has-text("Yes"), button:has-text("OK")',
    cancelButton: 'button:has-text("Cancel"), button:has-text("No")',
    title: '[role="dialog"] h2, .modal h2',
  };

  constructor(page: Page) {
    this.page = page;
  }

  get modal(): Locator {
    return this.page.locator(this.selectors.modal).first();
  }

  get title(): Locator {
    return this.page.locator(this.selectors.title).first();
  }

  async waitForOpen(): Promise<void> {
    await expect(this.modal).toBeVisible({ timeout: 10000 });
  }

  async close(): Promise<void> {
    await this.page.locator(this.selectors.closeButton).first().click();
  }

  async confirm(): Promise<void> {
    await this.page.locator(this.selectors.confirmButton).first().click();
  }

  async cancel(): Promise<void> {
    await this.page.locator(this.selectors.cancelButton).first().click();
  }

  async verifyTitle(expectedTitle: string | RegExp): Promise<void> {
    await expect(this.title).toContainText(expectedTitle);
  }

  async fillField(labelText: string | RegExp, value: string): Promise<void> {
    await this.page.getByLabel(labelText).fill(value);
  }
}

// ============================================================================
// FORM COMPONENT - Generic form handler
// ============================================================================

export class Form {
  private page: Page;
  private formSelector: string;

  constructor(page: Page, formSelector: string = 'form') {
    this.page = page;
    this.formSelector = formSelector;
  }

  get form(): Locator {
    return this.page.locator(this.formSelector).first();
  }

  async fillFieldByLabel(label: string | RegExp, value: string): Promise<void> {
    await this.page.getByLabel(label).fill(value);
  }

  async fillFieldByPlaceholder(placeholder: string | RegExp, value: string): Promise<void> {
    await this.page.getByPlaceholder(placeholder).fill(value);
  }

  async fillFieldByName(name: string, value: string): Promise<void> {
    await this.page.locator(`input[name="${name}"]`).fill(value);
  }

  async selectOption(label: string | RegExp, option: string): Promise<void> {
    await this.page.getByLabel(label).selectOption(option);
  }

  async checkCheckbox(label: string | RegExp): Promise<void> {
    await this.page.getByLabel(label).check();
  }

  async submit(): Promise<void> {
    await this.page.locator('button[type="submit"]').first().click();
  }

  async submitAndWait(urlPattern: string | RegExp): Promise<void> {
    await this.submit();
    await this.page.waitForURL(urlPattern, { timeout: 15000 });
  }

  async verifyErrorMessage(errorText: string | RegExp): Promise<void> {
    await expect(this.page.getByText(errorText)).toBeVisible();
  }
}

// ============================================================================
// EXAMPLE USAGE IN A TEST
// ============================================================================

/**
 * Example test showing how to use Page Objects
 */
export const exampleTest = `
import { test, expect } from '@playwright/test';
import { LandingPage, AuthPage, DashboardPage, Modal } from './page-object-template';

test.describe('Example: Using Page Objects', () => {
  test('should complete user journey with POM', async ({ page }) => {
    // Initialize page objects
    const landingPage = new LandingPage(page);
    const authPage = new AuthPage(page, false); // false = signup page
    const dashboardPage = new DashboardPage(page);
    const modal = new Modal(page);

    // Step 1: Visit landing page
    await landingPage.goto();
    await landingPage.verifyPageLoaded();
    await landingPage.screenshot('landing-page');

    // Step 2: Navigate to signup
    await landingPage.navigateToSignup();
    await authPage.verifySignupPage();

    // Step 3: Register new user
    await authPage.registerAndWait(
      'Test User',
      'test@example.com',
      'SecurePass123!'
    );

    // Step 4: Verify dashboard
    await dashboardPage.verifyDashboardLoaded();

    // Step 5: Create something (opens modal)
    await dashboardPage.clickCreate();
    await modal.waitForOpen();
    await modal.fillField(/name/i, 'Test Item');
    await modal.confirm();

    // Done!
    console.log('✅ Journey completed with Page Objects!');
  });
});
`;

// ============================================================================
// TEMPLATE FOR CREATING YOUR OWN PAGE OBJECT
// ============================================================================

export class YourPageTemplate extends BasePage {
  // 1. Define selectors (keeps them organized and easy to update)
  private selectors = {
    mainHeading: 'h1',
    primaryButton: 'button[data-testid="primary-action"]',
    inputField: 'input[name="fieldName"]',
    // Add more selectors...
  };

  constructor(page: Page) {
    super(page, '/your-page-url');
  }

  // 2. Define locators (lazy-loaded for better performance)
  get mainHeading(): Locator {
    return this.page.locator(this.selectors.mainHeading);
  }

  get primaryButton(): Locator {
    return this.page.locator(this.selectors.primaryButton);
  }

  // 3. Define actions (what users can do on this page)
  async performAction(): Promise<void> {
    await this.primaryButton.click();
  }

  async fillForm(data: { fieldName: string }): Promise<void> {
    await this.page.locator(this.selectors.inputField).fill(data.fieldName);
  }

  // 4. Define verifications (assertions about page state)
  async verifyPageLoaded(): Promise<void> {
    await expect(this.mainHeading).toBeVisible();
  }

  async verifyActionCompleted(): Promise<void> {
    await expect(this.page.getByText(/success/i)).toBeVisible();
  }
}
