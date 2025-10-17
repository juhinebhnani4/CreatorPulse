# Backend Tests - Setup Guide

## Quick Start (Windows)

### Option 1: Using the Helper Script (Easiest)

```bash
cd backend
tests\run_tests.bat
```

This will:
- Check if dependencies are installed
- Install missing dependencies
- Run all tests

You can also run specific tests:
```bash
tests\run_tests.bat auth           # Run only auth tests
tests\run_tests.bat workspaces     # Run only workspace tests
tests\run_tests.bat quick          # Run one quick test
```

### Option 2: Manual Setup

If you prefer to set up manually:

#### Step 1: Install Backend Dependencies

First, make sure your backend environment has all dependencies:

```bash
# From the backend directory
cd backend

# Install backend requirements
pip install -r requirements.txt

# Install test dependencies
pip install pytest pytest-asyncio httpx
```

#### Step 2: Configure Environment

Make sure you have a `.env` file in the **root directory** (not backend):

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-role-key
SECRET_KEY=your-jwt-secret-key
```

#### Step 3: Run Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run only auth tests
python -m pytest tests/integration/test_auth_api.py -v

# Run only workspace tests
python -m pytest tests/integration/test_workspaces_api.py -v

# Run a specific test
python -m pytest tests/integration/test_auth_api.py::TestSignup::test_signup_validates_email_format -v
```

## Troubleshooting

### Error: "ModuleNotFoundError: No module named 'fastapi'"

**Solution**: Install backend dependencies
```bash
pip install -r requirements.txt
```

### Error: "ModuleNotFoundError: No module named 'pytest'"

**Solution**: Install test dependencies
```bash
pip install pytest pytest-asyncio httpx
```

### Error: "Supabase credentials not configured"

**Solution**: Create a `.env` file in the root directory with your Supabase credentials.

### Tests are failing

1. **Check backend is NOT running**: Tests start their own test server
2. **Check Supabase credentials**: Make sure they're correct
3. **Try one test first**:
   ```bash
   python -m pytest tests/integration/test_auth_api.py::TestSignup::test_signup_validates_email_format -v
   ```

## Understanding the Test Output

When tests run successfully, you'll see:

```
================================ test session starts ================================
collected 15 items

tests/integration/test_auth_api.py::TestSignup::test_signup_creates_user PASSED [  6%]
tests/integration/test_auth_api.py::TestSignup::test_signup_rejects_duplicate PASSED [ 13%]
...
================================= 15 passed in 8.23s =================================
```

- **PASSED** = Test succeeded ✅
- **FAILED** = Test failed ❌
- **ERROR** = Test had an error (usually setup issue)
- **SKIPPED** = Test was skipped

## What Gets Tested

### Authentication (`test_auth_api.py`)
- User signup (email validation, password strength, duplicate check)
- User login (valid/invalid credentials)
- JWT token validation
- User info retrieval
- Logout

### Workspaces (`test_workspaces_api.py`)
- Create workspace
- List workspaces
- Get workspace details
- Update workspace
- Delete workspace
- Workspace configuration
- Authorization & isolation

## Next Steps

Once tests are running:

1. **Bookmark this guide** for future reference
2. **Run tests before deploying** to catch bugs
3. **Add new tests** when you add new features (copy existing test patterns)

## Getting Help

If you're stuck:

1. Check the error message carefully
2. Make sure all dependencies are installed
3. Verify your `.env` file has correct credentials
4. Try running one simple test first
5. Check the full documentation: [backend/tests/README.md](README.md)

## Common Commands Reference

```bash
# Install everything
pip install -r requirements.txt
pip install pytest pytest-asyncio httpx

# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/integration/test_auth_api.py -v

# Run specific test class
python -m pytest tests/integration/test_auth_api.py::TestSignup -v

# Run one test
python -m pytest tests/integration/test_auth_api.py::TestSignup::test_signup_validates_email_format -v

# Show more details on failure
python -m pytest tests/ -v -s

# Stop on first failure
python -m pytest tests/ -v -x
```

---

**Ready to test!** Start with the helper script or follow the manual setup above.
