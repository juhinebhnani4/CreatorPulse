@echo off
echo Stopping existing backend server...
taskkill /F /FI "WINDOWTITLE eq*uvicorn*" 2>NUL
taskkill /F /FI "COMMANDLINE eq*main:app*" 2>NUL

timeout /t 2 /nobreak >NUL

echo.
echo Starting backend server with auto-reload...
cd /d "%~dp0"
start "Backend Server" .venv\Scripts\python.exe -m uvicorn backend.main:app --reload --port 8000

echo.
echo Backend server starting...
echo Check the new window for logs.
pause
