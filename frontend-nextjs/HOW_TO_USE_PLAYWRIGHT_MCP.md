# How to Use Playwright MCP for E2E Testing

## Two Ways to Test with Playwright

---

## ✅ Method 1: Through Claude Code (Recommended for Interactive Testing)

**You're already set up!** Just talk to Claude (me) in this conversation.

### How It Works

1. **Playwright MCP is already configured** in your Claude settings
2. **Just ask Claude to test something** - I'll use Playwright MCP automatically
3. **No code needed** - Just describe what you want to test

### Example Requests

#### Basic Navigation & Screenshots
```
"Navigate to localhost:3000 and take a screenshot"
```

```
"Go to the dashboard and show me what's there"
```

#### Test User Flows
```
"Test the login flow with email: test@example.com and password: testpass123"
```

```
"Test User Story 3.1 - Add RSS Feed Source"
```

```
"Walk through the complete newsletter generation flow"
```

#### Debug Issues
```
"Debug why the signup button isn't working"
```

```
"Take screenshots of each step in the content scraping process"
```

```
"Check if the workspace selector is visible after login"
```

#### Form Testing
```
"Fill out the registration form and submit it"
```

```
"Test form validation on the add source modal"
```

```
"Try to submit an empty newsletter form and verify error messages"
```

#### Database Verification
```
"Create a workspace and verify it exists in the database"
```

```
"Add a subscriber and check the subscribers table"
```

### What Happens When You Ask

When you say: **"Test the login flow"**

I will automatically:
1. ✅ Navigate to http://localhost:3000/login
2. ✅ Fill in the email field
3. ✅ Fill in the password field
4. ✅ Click the sign in button
5. ✅ Take screenshots at each step
6. ✅ Verify you're redirected to dashboard
7. ✅ Check database for session
8. ✅ Report results back to you

### Before You Start

Make sure your servers are running:

```bash
# Terminal 1: Backend
cd e:\Career coaching\100x\scraper-scripts
.venv\Scripts\python.exe -m uvicorn backend.main:app --reload --port 8000

# Terminal 2: Frontend
cd frontend-nextjs
npm run dev
```

Then just start asking me to test things!

---

## ✅ Method 2: Run Existing Playwright Tests (Traditional Way)

Use this for running your pre-written test suites.

### Quick Start

```bash
# Navigate to frontend directory
cd frontend-nextjs

# Run all tests
npm run test:e2e

# Run specific journey
npm run test:e2e:journey1    # User onboarding
npm run test:e2e:journey2    # Content sources
npm run test:e2e:journey3    # Newsletter generation

# Run with UI (visual mode)
npm run test:e2e:ui

# Run in headed mode (see browser)
npm run test:e2e:headed

# Debug mode
npm run test:e2e:debug
```

### Available Test Scripts

All scripts are in `package.json`:

```json
{
  "scripts": {
    "test:e2e": "playwright test",
    "test:e2e:ui": "playwright test --ui",
    "test:e2e:headed": "playwright test --headed",
    "test:e2e:debug": "playwright test --debug",
    "test:e2e:journey1": "playwright test journey-1-user-onboarding",
    "test:e2e:journey2": "playwright test journey-2-content-sources",
    "test:e2e:journey3": "playwright test journey-3-newsletter-generation",
    "test:e2e:report": "playwright show-report"
  }
}
```

### Existing Test Files

Your current E2E tests:
- `e2e/journey-1-user-onboarding.spec.ts` - Signup, login, workspace creation
- `e2e/journey-2-content-sources.spec.ts` - Add sources, scrape content
- `e2e/journey-3-newsletter-generation.spec.ts` - Generate, edit, send newsletter
- `e2e/debug-landing.spec.ts` - Debug test for landing page
- `e2e/journey-1-simple.spec.ts` - Simplified onboarding test

---

## 🎯 Comparison: When to Use Each Method

| Task | Method 1 (Claude/MCP) | Method 2 (npm scripts) |
|------|----------------------|------------------------|
| **Quick exploratory testing** | ✅ Best choice | ❌ Need to write code first |
| **Debug a specific issue** | ✅ Best choice | ⚠️ Slower |
| **Try out a new feature** | ✅ Best choice | ❌ Need to write test |
| **Generate test code** | ✅ Can generate for you | ❌ Manual coding |
| **Automated regression testing** | ⚠️ Manual each time | ✅ Best choice |
| **CI/CD pipeline** | ❌ Not suitable | ✅ Best choice |
| **Learning the app** | ✅ Best choice | ⚠️ Harder |

---

## 💬 Example Conversation with Claude

### You Say:
```
"I want to test the complete user registration flow"
```

### Claude Responds:
```
I'll test the user registration flow using Playwright MCP. Let me walk through it:

1. Navigating to localhost:3000...
2. Clicking "Sign Up" button...
3. Filling registration form...
4. Submitting...
5. Verifying redirect to dashboard...

✅ Test Results:
- Registration form loads correctly
- Email validation works
- Password requirements enforced
- User successfully created in database
- Auto-login works
- Redirected to /app dashboard

📸 Screenshots saved to test-results/
```

---

## 🚀 Try These Examples Right Now

Copy and paste any of these into your conversation with Claude:

### Beginner Examples

```
"Navigate to localhost:3000 and show me the landing page"
```

```
"Click the Sign Up button and take a screenshot"
```

```
"Test if the email field accepts invalid emails"
```

### Intermediate Examples

```
"Test the complete login flow with email: test@example.com"
```

```
"Add a new RSS feed source: https://techcrunch.com/feed/"
```

```
"Generate a newsletter and verify it saves as a draft"
```

### Advanced Examples

```
"Test User Story 5.1: Generate Newsletter Draft (all scenarios)"
```

```
"Walk through journey 2 and take screenshots at each step"
```

```
"Debug why the workspace switcher isn't working"
```

---

## 🔧 Troubleshooting

### "Cannot connect to localhost:3000"

**Solution:** Start your frontend dev server:
```bash
cd frontend-nextjs
npm run dev
```

### "Cannot connect to localhost:8000"

**Solution:** Start your backend server:
```bash
cd ..
.venv\Scripts\python.exe -m uvicorn backend.main:app --reload --port 8000
```

### "Element not found"

**Ask Claude:**
```
"Take a screenshot of the current page so we can see what's there"
```

### "Test is timing out"

**Ask Claude:**
```
"Wait for the page to fully load before clicking"
```

Or:
```
"Increase the timeout to 30 seconds"
```

---

## 📚 Reference: Playwright MCP Tools Available

When you ask Claude to test something, these tools are used automatically:

### Navigation
- `playwright_navigate` - Go to a URL
- `playwright_goto` - Navigate to page

### Interaction
- `playwright_click` - Click elements
- `playwright_fill` - Fill form fields
- `playwright_select` - Select dropdown options
- `playwright_check` - Check checkboxes
- `playwright_press` - Press keyboard keys

### Verification
- `playwright_screenshot` - Take screenshots
- `playwright_evaluate` - Run JavaScript in browser
- `playwright_get_text` - Get element text
- `playwright_is_visible` - Check if element visible

### Debugging
- `playwright_console` - Check browser console logs
- `playwright_network` - Monitor network requests
- `playwright_errors` - Check for page errors

You don't need to know these - just describe what you want to test!

---

## 🎓 Learning Path

### Day 1: Get Familiar
```
"Navigate to localhost:3000 and take screenshots of all main pages"
```

### Day 2: Test Basic Flows
```
"Test the login and logout flow"
"Test adding a new workspace"
```

### Day 3: Test Complex Features
```
"Test User Story 3.1 - Add RSS Feed"
"Test the newsletter generation flow"
```

### Day 4: Debug Issues
```
"Debug why form submission isn't working"
"Find all buttons on the settings page"
```

### Day 5: Generate Tests
```
"Generate a Playwright test file for subscriber management"
"Create tests for all analytics features"
```

---

## 🎯 Quick Commands Reference

### Navigation & Exploration
- `"Go to [URL] and show me what's there"`
- `"Take a screenshot of the dashboard"`
- `"Navigate through all main pages"`

### Testing Specific Features
- `"Test [feature name]"`
- `"Test User Story [number]"`
- `"Verify [specific behavior]"`

### Debugging
- `"Debug why [something] isn't working"`
- `"Show me what happens when I click [button]"`
- `"Check console logs for errors"`

### Generating Tests
- `"Generate test code for [feature]"`
- `"Create a test suite for [user story]"`
- `"Write tests for all [category] features"`

---

## 💡 Pro Tips

1. **Always start both servers before testing**
   - Backend on :8000
   - Frontend on :3000

2. **Be specific in your requests**
   - Good: "Test login with email test@example.com and password pass123"
   - Less good: "Test login"

3. **Ask for screenshots to debug**
   - "Take a screenshot after each step"
   - "Show me what the page looks like right now"

4. **Use user stories as a guide**
   - "Test User Story 3.1 from COMPLETE_USER_STORIES_E2E.md"

5. **Combine with database checks**
   - "Add a workspace and verify it's in the database"

---

## 🚦 Status Check

Before you start, verify everything is ready:

### ✅ Checklist

- [ ] Backend server running on http://localhost:8000
- [ ] Frontend server running on http://localhost:3000
- [ ] Can access http://localhost:3000 in browser
- [ ] Database is accessible (Supabase)
- [ ] Playwright MCP configured in Claude (already done!)

### Quick Health Check

Ask Claude:
```
"Navigate to localhost:3000 and verify both servers are running"
```

---

## 📞 Need Help?

Just ask Claude:
- "How do I test [feature]?"
- "What can Playwright MCP do?"
- "Show me examples of testing [specific thing]"
- "I'm stuck with [problem], can you help?"

---

## 🎉 You're Ready!

Start testing now! Just tell Claude what you want to test:

```
"Let's test the complete user onboarding flow!"
```

**Remember:** You're just having a conversation with Claude. No special commands, no syntax to remember. Just describe what you want to test in plain English!
