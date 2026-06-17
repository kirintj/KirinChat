@echo off
setlocal

echo ============================================
echo   AgentChat Frontend Development Server
echo ============================================
echo.

REM Switch to frontend directory
cd /d "%~dp0\src\frontend"

REM Check dependencies
if not exist "node_modules" (
    echo First run, installing dependencies...
    npm install
    if errorlevel 1 (
        echo ERROR: Dependencies installation failed!
        pause
        exit /b 1
    )
)

REM Start dev server
echo Starting frontend development server...
echo.
echo SUCCESS: Frontend started!
echo URL: http://localhost:8090
echo.
npm run dev

pause
