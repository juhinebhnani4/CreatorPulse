# First Time Setup - Backend Tests

## Before You Run Tests

The error you saw (`pytest: The term 'pytest' is not recognized`) means pytest isn't installed or isn't in your PATH. Here's how to fix it:

## Step 1: Make Sure You Have Backend Dependencies

The backend tests need your FastAPI backend dependencies. Install them:

```bash
# From the backend directory
cd backend

# Install backend dependencies
pip install -r requirements.txt
```

This installs:
- FastAPI
- Supabase client
- Pydantic
- And other backend dependencies

## Step 2: Install Test Dependencies

```bash
# Still in the backend directory
pip install pytest pytest-asyncio httpx
```

This installs:
- `pytest` - The testing framework
- `pytest-asyncio` - For async test support
- `httpx` - For HTTP requests in tests

## Step 3: Verify Installation

```bash
# Check pytest is installed
python -m pytest --version
```

You should see something like:
```
pytest 7.4.3
```

## Step 4: Check Environment Variables

Make sure you have a `.env` file in the **root directory** (not in backend):

```
E:\Career coaching\100x\scraper-scripts\.env
```

With these variables:
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-role-key
SECRET_KEY=your-jwt-secret-key
```

## Step 5: Run Your First Test!

```bash
# From the backend directory
python -m pytest tests/integration/test_auth_api.py::TestSignup::test_signup_validates_email_format -v
```

This runs ONE simple test that validates email format. It should pass quickly.

Expected output:
```
================================ test session starts ================================
collected 1 item

tests/integration/test_auth_api.py::TestSignup::test_signup_validates_email_format PASSED [100%]

================================= 1 passed in 2.34s =================================
```

## Step 6: Run All Tests

Once the first test works, run all tests:

```bash
python -m pytest tests/ -v
```

This will run all 35 tests and take about 15-20 seconds.

## Common Issues

### Issue 1: "ModuleNotFoundError: No module named 'fastapi'"

**Problem**: Backend dependencies not installed

**Fix**:
```bash
pip install -r requirements.txt
```

### Issue 2: "ModuleNotFoundError: No module named 'pytest'"

**Problem**: Test dependencies not installed

**Fix**:
```bash
pip install pytest pytest-asyncio httpx
```

### Issue 3: Tests fail with "Supabase not configured"

**Problem**: Environment variables not set

**Fix**: Create a `.env` file in the root directory with your Supabase credentials

### Issue 4: "pytest: command not found" or "not recognized"

**Problem**: pytest not in PATH

**Solution**: Use `python -m pytest` instead of just `pytest`

Always use:
```bash
python -m pytest tests/ -v
```

Not:
```bash
pytest tests/ -v  # This might not work
```

## Using the Helper Script (Windows)

If you're on Windows, you can use the helper script:

```bash
cd backend
tests\run_tests.bat
```

This script will:
1. Check if dependencies are installed
2. Install missing dependencies
3. Run the tests
4. Show you the results

## Summary

**To run tests, you need:**

1. ✅ Backend dependencies installed (`pip install -r requirements.txt`)
2. ✅ Test dependencies installed (`pip install pytest pytest-asyncio httpx`)
3. ✅ Environment variables configured (`.env` file)
4. ✅ Run with `python -m pytest` (not just `pytest`)

**Then you can run:**

```bash
# From backend directory
python -m pytest tests/ -v
```

## Next Steps

Once your first test passes:

1. ✅ Bookmark this guide
2. ✅ Read [SETUP_GUIDE.md](SETUP_GUIDE.md) for more options
3. ✅ Check [README.md](README.md) for comprehensive documentation
4. ✅ Run tests before committing code

**You're all set!** 🚀
