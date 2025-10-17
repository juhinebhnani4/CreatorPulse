# Playwright MCP for E2E Testing Guide

## Overview

Playwright MCP (Model Context Protocol) allows you to interact with Playwright directly through Claude Code, enabling AI-powered browser automation and E2E testing. The Playwright MCP server is already configured in your Claude settings and ready to use.

## What is Playwright MCP?

Playwright MCP provides tools that let Claude Code:
- Navigate web pages and interact with elements
- Take screenshots and videos
- Fill forms and click buttons
- Verify page content and state
- Debug failing tests
- Generate test code from descriptions

## Configuration Status

✅ **Already Configured**: Playwright MCP is set up in your Claude config at:
```
C:\Users\Jyotsna\.claude\config.json
```

```json
"Playwright": {
  "command": "npx @playwright/mcp@latest"
}
```

## Available MCP Tools

When you request E2E testing through Claude Code, the following Playwright MCP tools are automatically available:

### 1. `playwright_navigate`
Navigate to a URL in the browser
```
Usage: Navigate to http://localhost:3000
```

### 2. `playwright_screenshot`
Take a screenshot of the current page
```
Usage: Take a screenshot of the current page
```

### 3. `playwright_click`
Click on an element using a selector
```
Usage: Click on button with text "Sign Up"
```

### 4. `playwright_fill`
Fill in form fields
```
Usage: Fill email field with "test@example.com"
```

### 5. `playwright_evaluate`
Execute JavaScript in the browser context
```
Usage: Get the page title
```

### 6. `playwright_console`
Monitor browser console logs
```
Usage: Check for console errors
```

## How to Use Playwright MCP

### Method 1: Natural Language Testing (Recommended)

Simply describe what you want to test, and Claude will use the Playwright MCP tools automatically:

**Example requests:**
```
"Test the login flow on localhost:3000"
"Navigate to the dashboard and take a screenshot"
"Check if the signup form validates email correctly"
"Fill out the workspace creation form and verify it saves"
```

### Method 2: Direct Test Execution

Ask Claude to run your existing Playwright tests using MCP for enhanced debugging:

```
"Run the user onboarding test and debug any failures"
"Execute journey-1 test and show screenshots at each step"
```

### Method 3: Test Generation

Describe a user journey and Claude will generate the test code:

```
"Generate a test for: user signs up, creates workspace, adds RSS source"
```

## Example Use Cases

### 1. Interactive Debugging Session

**You:** "Start a browser session on localhost:3000 and navigate to the signup page"

**Claude will:**
1. Use `playwright_navigate` to open http://localhost:3000
2. Use `playwright_click` to click signup button
3. Use `playwright_screenshot` to capture the page
4. Show you what it sees

### 2. Form Validation Testing

**You:** "Test the workspace creation form validation"

**Claude will:**
1. Navigate to workspace creation
2. Use `playwright_fill` with invalid data
3. Use `playwright_click` to submit
4. Use `playwright_evaluate` to check error messages
5. Report validation behavior

### 3. Full User Journey Testing

**You:** "Test the complete newsletter generation flow"

**Claude will:**
1. Navigate through each step
2. Fill forms and click buttons
3. Take screenshots at each stage
4. Verify database state (if Supabase MCP is also active)
5. Report success or failures

### 4. Visual Regression Testing

**You:** "Take screenshots of all main pages for visual comparison"

**Claude will:**
1. Navigate to each page
2. Capture screenshots
3. Save them with descriptive names
4. Compare with previous versions if available

## Integration with Your Existing Tests

Your project already has comprehensive E2E tests. Here's how Playwright MCP enhances them:

### Existing Test Files:
- [journey-1-user-onboarding.spec.ts](frontend-nextjs/e2e/journey-1-user-onboarding.spec.ts)
- [journey-2-content-sources.spec.ts](frontend-nextjs/e2e/journey-2-content-sources.spec.ts)
- [journey-3-newsletter-generation.spec.ts](frontend-nextjs/e2e/journey-3-newsletter-generation.spec.ts)

### How MCP Enhances These Tests:

1. **Interactive Debugging**: When tests fail, ask Claude to debug using MCP
2. **Visual Verification**: Get screenshots at any point without writing code
3. **Quick Checks**: Test specific scenarios without running full test suite
4. **Test Generation**: Create new tests by describing behavior

## Practical Examples

### Example 1: Quick Login Test

**You say:**
```
"Use Playwright MCP to test the login flow with email: test@example.com"
```

**Claude will:**
```
1. Navigate to http://localhost:3000/login
2. Fill email field: "test@example.com"
3. Fill password field: "password123"
4. Click "Sign In" button
5. Verify redirect to dashboard
6. Take screenshot of result
```

### Example 2: Debug Failing Test

**You say:**
```
"Journey 1 test is failing at step 4. Use MCP to navigate there and show me what's happening"
```

**Claude will:**
1. Navigate to the point of failure
2. Take screenshot
3. Check console logs
4. Inspect element states
5. Identify the issue

### Example 3: Create New Test

**You say:**
```
"Generate a test for editing workspace settings using Playwright MCP"
```

**Claude will:**
1. Explore the settings page using MCP
2. Identify form elements
3. Generate test code
4. Run test to verify it works

## Combining Playwright MCP with Supabase MCP

You have both Playwright and Supabase MCP configured. This powerful combination allows:

**Frontend + Backend Verification:**
```
You: "Test workspace creation and verify it in the database"

Claude will:
1. Use Playwright MCP to create workspace in UI
2. Use Supabase MCP to verify record in database
3. Confirm data integrity
```

## Running Your Existing Tests with MCP Benefits

### Standard Test Run (without MCP)
```bash
cd frontend-nextjs
npm run test:e2e
```

### Enhanced Test Run (with MCP via Claude)

**You say to Claude:**
```
"Run the E2E tests and help debug any failures using Playwright MCP"
```

**Benefits:**
- Automatic debugging on failures
- Screenshots at failure points
- Console log analysis
- Suggested fixes
- Interactive troubleshooting

## Common Workflows

### Workflow 1: New Feature Testing
```
1. You: "I added a new feature for bulk content deletion"
2. You: "Generate a Playwright test for this feature"
3. Claude: Uses MCP to explore UI and generates test
4. You: "Run the test"
5. Claude: Executes and reports results
```

### Workflow 2: Bug Investigation
```
1. You: "Users report login button not working"
2. You: "Use Playwright MCP to test login on localhost:3000"
3. Claude: Navigates, tests, takes screenshots
4. Claude: Identifies issue (e.g., button disabled due to validation)
5. Claude: Suggests fix
```

### Workflow 3: Visual Verification
```
1. You: "Compare dashboard layout before and after my changes"
2. You: "Take screenshot of /dashboard"
3. Claude: Captures current state
4. You: "Compare with screenshot from last week"
5. Claude: Identifies visual differences
```

## Best Practices

### 1. Start Servers First
Always ensure both frontend and backend are running:
```bash
# Terminal 1: Backend
.venv\Scripts\python.exe -m uvicorn backend.main:app --reload --port 8000

# Terminal 2: Frontend
cd frontend-nextjs
npm run dev
```

### 2. Be Specific with URLs
```
Good: "Navigate to http://localhost:3000/dashboard"
Bad: "Go to the dashboard"
```

### 3. Request Screenshots
```
"Take a screenshot after clicking submit"
```

### 4. Combine with Database Checks
```
"Create a workspace and verify it exists in Supabase"
```

### 5. Iterative Testing
```
You: "Fill the signup form"
Claude: Fills form
You: "Now submit it"
Claude: Submits
You: "Take a screenshot"
Claude: Captures result
```

## Troubleshooting

### Issue: "Browser not found"
**Solution:**
```bash
cd frontend-nextjs
npx playwright install chromium
```

### Issue: "Cannot connect to localhost:3000"
**Solution:** Ensure frontend is running:
```bash
npm run dev
```

### Issue: "Element not found"
**Solution:** Ask Claude to take a screenshot first:
```
"Take a screenshot of the current page so we can see what's there"
```

### Issue: "Timeout errors"
**Solution:** Ask Claude to wait longer:
```
"Wait for the page to fully load before clicking"
```

## Advanced Features

### 1. Network Interception
```
"Monitor API calls during workspace creation"
```

### 2. Mobile Testing
```
"Test the signup flow on mobile viewport"
```

### 3. Performance Monitoring
```
"Measure page load time for the dashboard"
```

### 4. Accessibility Testing
```
"Check if the login form is keyboard accessible"
```

## Quick Reference Commands

### Testing
```
"Test the login flow"
"Verify signup form validation"
"Check if dashboard loads correctly"
"Test workspace creation end-to-end"
```

### Debugging
```
"Debug why the submit button isn't working"
"Show me what's on the page right now"
"Check console for errors"
"Take a screenshot of the current state"
```

### Generation
```
"Generate a test for the settings page"
"Create a test for bulk content selection"
"Write a test for newsletter preview"
```

### Verification
```
"Verify the newsletter appears in the list"
"Check if the success message is shown"
"Confirm user was redirected to dashboard"
```

## Example Session

Here's a complete example of using Playwright MCP through Claude:

**You:** "Let's test the complete newsletter generation flow using Playwright MCP"

**Claude:** "I'll test the newsletter generation flow step by step using Playwright MCP."

1. **Navigation**
   - Navigate to http://localhost:3000
   - Login with test credentials
   - Screenshot: Initial login

2. **Workspace Setup**
   - Click on workspace
   - Navigate to content sources
   - Screenshot: Sources page

3. **Content Selection**
   - Select content items
   - Click "Generate Newsletter"
   - Screenshot: Generation in progress

4. **Verification**
   - Wait for generation to complete
   - Verify newsletter preview appears
   - Screenshot: Final newsletter
   - Check Supabase for newsletter record

**Result:** "✅ Newsletter generation flow working correctly. See screenshots in test-results/"

## Next Steps

1. **Try it now**: Say "Use Playwright MCP to navigate to localhost:3000 and take a screenshot"

2. **Test a feature**: Pick any feature and ask Claude to test it

3. **Debug existing tests**: Ask Claude to help debug failing tests using MCP

4. **Generate new tests**: Describe a user flow and get test code

## Resources

- **Your E2E Tests**: [frontend-nextjs/e2e/](frontend-nextjs/e2e/)
- **Test Documentation**: [E2E_QUICKSTART.md](frontend-nextjs/E2E_QUICKSTART.md)
- **Playwright Docs**: https://playwright.dev
- **MCP Documentation**: https://modelcontextprotocol.io

---

## Ready to Start?

Just ask Claude to test anything in your application:

```
"Test the user onboarding flow using Playwright MCP"
"Debug why the workspace form isn't submitting"
"Take screenshots of all main pages"
"Generate a test for content source management"
```

The Playwright MCP tools will be used automatically! 🎭✨
