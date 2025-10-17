# Backend API Integration Tests

Comprehensive test suite for CreatorPulse FastAPI backend.

## Overview

These integration tests verify the complete flow from API endpoints through business logic to database persistence:

```
HTTP Request → FastAPI Endpoint → Service Layer → Supabase Database
```

## Test Structure

```
backend/tests/
├── __init__.py                          # Package marker
├── conftest.py                          # Shared fixtures & helpers
├── pytest.ini                           # Pytest configuration
├── README.md                            # This file
└── integration/
    ├── __init__.py
    ├── test_auth_api.py                # Authentication endpoints
    └── test_workspaces_api.py          # Workspace CRUD endpoints
```

## Test Coverage

### Authentication API Tests (`test_auth_api.py`)

#### Signup (`/api/v1/auth/signup`)
- ✅ Creates user successfully with valid data
- ✅ Rejects duplicate email addresses
- ✅ Validates email format
- ✅ Validates password length (min 8 chars)
- ✅ Validates username length (3-50 chars)
- ✅ Requires all mandatory fields
- ✅ Verifies user created in Supabase database
- ✅ Returns valid JWT token

#### Login (`/api/v1/auth/login`)
- ✅ Authenticates with valid credentials
- ✅ Rejects invalid email
- ✅ Rejects wrong password
- ✅ Validates email format
- ✅ Returns JWT token on success

#### Get Current User (`/api/v1/auth/me`)
- ✅ Returns user info with valid token
- ✅ Rejects requests without token (401)
- ✅ Rejects invalid token (401)

#### Logout (`/api/v1/auth/logout`)
- ✅ Logs out with valid token
- ✅ Rejects requests without token (401)

### Workspace API Tests (`test_workspaces_api.py`)

#### List Workspaces (`GET /api/v1/workspaces`)
- ✅ Requires authentication
- ✅ Returns empty list for new users
- ✅ Returns user's workspaces
- ✅ Workspace isolation (users can't see others' workspaces)

#### Create Workspace (`POST /api/v1/workspaces`)
- ✅ Creates workspace successfully
- ✅ Requires authentication
- ✅ Validates name (required)
- ✅ Description is optional
- ✅ Verifies workspace in database
- ✅ Associates workspace with user

#### Get Workspace (`GET /api/v1/workspaces/{id}`)
- ✅ Returns workspace details
- ✅ Requires authentication
- ✅ Returns 404 for non-existent workspace
- ✅ Prevents unauthorized access (403/404)

#### Update Workspace (`PUT /api/v1/workspaces/{id}`)
- ✅ Updates workspace name
- ✅ Updates workspace description
- ✅ Requires authentication
- ✅ Prevents unauthorized access

#### Delete Workspace (`DELETE /api/v1/workspaces/{id}`)
- ✅ Deletes workspace successfully
- ✅ Requires authentication
- ✅ Verifies deletion in database
- ✅ Prevents unauthorized deletion

#### Workspace Configuration
- ✅ Gets workspace config
- ✅ Updates workspace config
- ✅ Requires authentication

## Installation

### 1. Install Test Dependencies

```bash
cd backend
pip install pytest pytest-asyncio httpx
```

Or add to your `requirements.txt`:
```
pytest>=7.4.0
pytest-asyncio>=0.21.0
httpx>=0.24.0
```

### 2. Configure Environment

Tests use your existing `.env` file. Ensure you have:

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-role-key
SECRET_KEY=your-jwt-secret-key
```

**Note**: Tests will create and delete test data. Use a development database, not production!

## Running Tests

### Run All Tests

```bash
# From backend directory
cd backend
pytest tests/ -v

# Or from project root
python -m pytest backend/tests/ -v
```

### Run Specific Test File

```bash
# Auth tests only
pytest tests/integration/test_auth_api.py -v

# Workspace tests only
pytest tests/integration/test_workspaces_api.py -v
```

### Run Specific Test Class

```bash
# Only signup tests
pytest tests/integration/test_auth_api.py::TestSignup -v

# Only workspace creation tests
pytest tests/integration/test_workspaces_api.py::TestCreateWorkspace -v
```

### Run Specific Test

```bash
# Single test
pytest tests/integration/test_auth_api.py::TestSignup::test_signup_creates_user_successfully -v
```

### Run with Markers

```bash
# Run only auth-related tests
pytest tests/ -m auth -v

# Run only workspace tests
pytest tests/ -m workspaces -v

# Run all integration tests
pytest tests/ -m integration -v
```

### Show Print Statements

```bash
# Show all output (print, logging, etc.)
pytest tests/ -v -s
```

### Stop on First Failure

```bash
# Stop immediately on first failure
pytest tests/ -v -x
```

### Run in Parallel (Faster)

```bash
# Install pytest-xdist
pip install pytest-xdist

# Run tests in parallel (4 workers)
pytest tests/ -v -n 4
```

## Test Output Example

```bash
$ pytest tests/integration/test_auth_api.py -v

================================ test session starts ================================
platform win32 -- Python 3.11.0, pytest-7.4.3, pluggy-1.3.0
rootdir: E:\Career coaching\100x\scraper-scripts\backend
configfile: pytest.ini
collected 15 items

tests/integration/test_auth_api.py::TestSignup::test_signup_creates_user_successfully PASSED [  6%]
tests/integration/test_auth_api.py::TestSignup::test_signup_rejects_duplicate_email PASSED [ 13%]
tests/integration/test_auth_api.py::TestSignup::test_signup_validates_email_format PASSED [ 20%]
tests/integration/test_auth_api.py::TestSignup::test_signup_validates_password_length PASSED [ 26%]
tests/integration/test_auth_api.py::TestSignup::test_signup_validates_username_length PASSED [ 33%]
tests/integration/test_auth_api.py::TestSignup::test_signup_requires_all_fields PASSED [ 40%]
tests/integration/test_auth_api.py::TestLogin::test_login_with_valid_credentials PASSED [ 46%]
tests/integration/test_auth_api.py::TestLogin::test_login_with_invalid_email PASSED [ 53%]
tests/integration/test_auth_api.py::TestLogin::test_login_with_wrong_password PASSED [ 60%]
tests/integration/test_auth_api.py::TestLogin::test_login_validates_email_format PASSED [ 66%]
tests/integration/test_auth_api.py::TestGetCurrentUser::test_get_current_user_with_valid_token PASSED [ 73%]
tests/integration/test_auth_api.py::TestGetCurrentUser::test_get_current_user_without_token PASSED [ 80%]
tests/integration/test_auth_api.py::TestGetCurrentUser::test_get_current_user_with_invalid_token PASSED [ 86%]
tests/integration/test_auth_api.py::TestLogout::test_logout_with_valid_token PASSED [ 93%]
tests/integration/test_auth_api.py::TestLogout::test_logout_without_token PASSED [100%]

================================= 15 passed in 8.23s =================================
```

## Test Fixtures

The `conftest.py` file provides shared fixtures:

### Core Fixtures

- **`test_client`**: FastAPI TestClient for making HTTP requests
- **`supabase_client`**: Supabase service client for database verification

### Authentication Fixtures

- **`test_user_credentials`**: Generate unique test credentials
- **`test_user`**: Create a test user (auto-cleanup)
- **`auth_headers`**: Get Authorization header with JWT token
- **`second_test_user`**: Create a second user for isolation testing

### Workspace Fixtures

- **`test_workspace`**: Create a test workspace (auto-cleanup)

### Helper Fixtures

- **`db_helpers`**: Database verification helpers
  - `user_exists(user_id)` - Check if user exists
  - `workspace_exists(workspace_id)` - Check if workspace exists
  - `get_user_workspaces(user_id)` - Get all user's workspaces
  - `workspace_belongs_to_user(workspace_id, user_id)` - Check ownership

## Auto-Cleanup

All fixtures automatically clean up after themselves:

- Test users are deleted after each test
- Test workspaces are deleted after each test
- Old test data (>1 hour) is cleaned up before test session starts

This ensures:
- No test data pollution
- Clean database state for each test
- No manual cleanup needed

## Writing New Tests

### Example: Testing a New Endpoint

```python
import pytest
from fastapi.testclient import TestClient

@pytest.mark.integration
@pytest.mark.your_feature
class TestYourFeature:
    """Test description."""

    def test_your_endpoint(self, test_client: TestClient, auth_headers, db_helpers):
        """
        Test description.

        Steps:
        1. Do something
        2. Verify result
        3. Check database
        """
        # Make API request
        response = test_client.post(
            "/api/v1/your-endpoint",
            headers=auth_headers,
            json={"data": "value"}
        )

        # Assert HTTP response
        assert response.status_code == 200

        # Assert response structure
        data = response.json()
        assert data["success"] is True

        # Verify in database
        assert db_helpers.your_check() is True
```

### Best Practices

1. **Use descriptive test names**: `test_signup_rejects_duplicate_email` not `test_signup_2`
2. **Document test steps**: Add docstring with numbered steps
3. **Use fixtures**: Don't create users/workspaces manually
4. **Verify database**: Don't just check HTTP response, verify data is saved
5. **Clean up**: Use fixtures for auto-cleanup
6. **Mark tests**: Use `@pytest.mark.integration` and feature markers

## Continuous Integration (CI/CD)

### GitHub Actions Example

```yaml
name: Backend Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
          pip install pytest pytest-asyncio httpx

      - name: Run tests
        env:
          SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
          SUPABASE_KEY: ${{ secrets.SUPABASE_KEY }}
          SUPABASE_SERVICE_KEY: ${{ secrets.SUPABASE_SERVICE_KEY }}
          SECRET_KEY: ${{ secrets.SECRET_KEY }}
        run: |
          cd backend
          pytest tests/ -v --tb=short
```

## Troubleshooting

### Tests Failing with "Supabase not configured"

Make sure `.env` file has:
```env
SUPABASE_URL=...
SUPABASE_KEY=...
SUPABASE_SERVICE_KEY=...
```

### Tests Failing with "User already exists"

Old test data wasn't cleaned up. Run:
```bash
pytest tests/ -v --setup-show
```

Or manually clean database:
```sql
DELETE FROM users WHERE email LIKE '%@example.com';
```

### Tests are Slow

- Use `pytest -n 4` for parallel execution
- Check Supabase network latency
- Reduce test count with markers: `pytest -m auth`

### Import Errors

Make sure you're in the `backend` directory:
```bash
cd backend
pytest tests/ -v
```

## Next Steps

1. **Add More Tests**: Content API, Newsletters API, etc.
2. **Code Coverage**: `pip install pytest-cov && pytest --cov=backend`
3. **Performance Tests**: Add load testing with `locust`
4. **Security Tests**: Test for SQL injection, XSS, etc.

## Questions?

See the test code for examples, or check the pytest documentation:
- https://docs.pytest.org/
- https://fastapi.tiangolo.com/tutorial/testing/
