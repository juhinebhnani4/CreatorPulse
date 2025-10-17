@echo off
REM Migration 009 Runner for Windows
REM This script helps you run the analytics tables migration

echo ========================================================================
echo SPRINT 8: Analytics Tables Migration
echo ========================================================================
echo.

REM Check if migration file exists
if not exist "backend\migrations\009_create_analytics_tables.sql" (
    echo ERROR: Migration file not found!
    echo Make sure you're running this from the project root directory.
    pause
    exit /b 1
)

echo Migration file found: backend\migrations\009_create_analytics_tables.sql
echo.

REM Check if psql is installed
where psql >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo [OK] psql is installed
    echo.

    REM Extract Supabase URL from .env
    for /f "tokens=2 delims==" %%a in ('findstr "SUPABASE_URL" .env 2^>nul') do set SUPABASE_URL=%%a

    if defined SUPABASE_URL (
        echo Found Supabase URL: %SUPABASE_URL%

        REM Extract project reference
        for /f "tokens=2 delims=/." %%a in ("%SUPABASE_URL%") do set PROJECT_REF=%%a

        if defined PROJECT_REF (
            echo Project Reference: %PROJECT_REF%
            echo.
            echo ========================================================================
            echo RUNNING MIGRATION
            echo ========================================================================
            echo.
            echo You will be prompted for your database password.
            echo Get it from: Supabase Dashboard ^> Settings ^> Database
            echo.

            REM Run the migration
            psql -h db.%PROJECT_REF%.supabase.co -p 5432 -U postgres -d postgres -f backend\migrations\009_create_analytics_tables.sql

            if %ERRORLEVEL% EQU 0 (
                echo.
                echo ========================================================================
                echo SUCCESS! Migration completed successfully.
                echo ========================================================================
                echo.
                echo Next steps:
                echo 1. Start the backend server: python -m uvicorn backend.main:app --reload
                echo 2. Test the analytics endpoints
                echo 3. Check SPRINT_8_COMPLETE.md for testing guide
                echo.
            ) else (
                echo.
                echo ========================================================================
                echo ERROR: Migration failed!
                echo ========================================================================
                echo.
                echo Check the error messages above.
                echo Common issues:
                echo - Incorrect database password
                echo - Connection timeout (check internet)
                echo - Tables already exist (migration already run)
                echo.
            )
        ) else (
            echo ERROR: Could not extract project reference from SUPABASE_URL
            goto :manual_instructions
        )
    ) else (
        echo WARNING: Could not find SUPABASE_URL in .env
        goto :manual_instructions
    )
) else (
    echo [!] psql is not installed or not in PATH
    echo.
    goto :manual_instructions
)

pause
exit /b 0

:manual_instructions
echo ========================================================================
echo ALTERNATIVE: Use Supabase Dashboard (Easiest!)
echo ========================================================================
echo.
echo 1. Go to: https://supabase.com/dashboard
echo 2. Select your project
echo 3. Click "SQL Editor" in the left sidebar
echo 4. Click "+ New Query"
echo 5. Copy and paste the content of:
echo    backend\migrations\009_create_analytics_tables.sql
echo 6. Click "Run"
echo.
echo Full instructions: See MIGRATION_009_INSTRUCTIONS.md
echo.
pause
exit /b 1
