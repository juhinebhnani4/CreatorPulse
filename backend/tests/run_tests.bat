@echo off
REM Backend Tests Runner Script
REM This script helps run the backend tests with the correct Python environment

echo ========================================
echo   CreatorPulse Backend Tests
echo ========================================
echo.

REM Check if we're in the backend directory
if not exist "tests\" (
    echo ERROR: Must be run from the backend directory
    echo Please run: cd backend
    echo Then run: tests\run_tests.bat
    pause
    exit /b 1
)

REM Try to find Python with FastAPI installed
echo Checking Python environment...
python -c "import fastapi; print('✓ FastAPI found')" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: FastAPI not installed in current Python environment
    echo.
    echo To fix this, you need to:
    echo 1. Activate your virtual environment with backend dependencies
    echo 2. Or install backend dependencies:
    echo    pip install -r requirements.txt
    echo    pip install pytest pytest-asyncio httpx
    echo.
    pause
    exit /b 1
)

REM Check for pytest
python -c "import pytest; print('✓ pytest found')" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: pytest not installed
    echo Installing test dependencies...
    pip install pytest pytest-asyncio httpx
    echo.
)

REM Check for environment variables
if "%SUPABASE_URL%"=="" (
    echo.
    echo WARNING: SUPABASE_URL not set
    echo Tests may fail without proper configuration
    echo Make sure you have a .env file with:
    echo   - SUPABASE_URL
    echo   - SUPABASE_KEY
    echo   - SUPABASE_SERVICE_KEY
    echo   - SECRET_KEY
    echo.
)

echo.
echo ========================================
echo   Running Tests
echo ========================================
echo.

REM Run tests based on argument
if "%1"=="" (
    echo Running all tests...
    python -m pytest tests/ -v --tb=short
) else if "%1"=="auth" (
    echo Running authentication tests...
    python -m pytest tests/integration/test_auth_api.py -v --tb=short
) else if "%1"=="workspaces" (
    echo Running workspace tests...
    python -m pytest tests/integration/test_workspaces_api.py -v --tb=short
) else if "%1"=="quick" (
    echo Running quick validation test...
    python -m pytest tests/integration/test_auth_api.py::TestSignup::test_signup_validates_email_format -v --tb=short
) else (
    echo Running specific test: %1
    python -m pytest %1 -v --tb=short
)

echo.
echo ========================================
echo   Tests Complete
echo ========================================
pause
