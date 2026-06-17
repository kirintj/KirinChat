@echo off
setlocal

echo ============================================
echo   AgentChat Local Development Startup
echo ============================================
echo.

REM Switch to project root directory
cd /d "%~dp0"

REM 1. Start Docker services
echo [1/4] Starting Docker services (MySQL, Redis, MinIO)...
docker-compose -f docker/docker-compose-dev.yml up -d

if errorlevel 1 (
    echo ERROR: Docker startup failed!
    pause
    exit /b 1
)

REM Wait for services to start
echo [2/4] Waiting for services to start...
timeout /t 15 >nul

REM 3. Check service status
echo [3/4] Checking service status...
docker-compose -f docker/docker-compose-dev.yml ps

echo.
echo SUCCESS: Docker services started
echo.

REM 4. Start backend
echo [4/4] Starting backend service...
cd src\backend

REM Check virtual environment
if not exist ".venv" (
    echo First run, installing dependencies...
    pip install uv
    uv sync
)

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Copy dev config if not exists
if not exist "agentchat\config.yaml" (
    copy agentchat\config-dev.yaml agentchat\config.yaml
    echo IMPORTANT: Config file created, please edit src\backend\agentchat\config.yaml
    pause
)

REM Start backend
echo Starting backend (hot reload mode)...
start "AgentChat Backend" cmd /k "uvicorn agentchat.main:app --reload --host 0.0.0.0 --port 7860"

echo.
echo SUCCESS: Local development environment started!
echo.
echo Access URLs:
echo   Backend API:      http://localhost:7860
echo   API Docs:         http://localhost:7860/docs
echo   MinIO Console:    http://localhost:9001
echo.
echo Development Tips:
echo   - Backend code will auto-reload on changes
echo   - Start frontend separately: cd src\frontend ^& npm run dev
echo.
echo Stop all services:
echo   1. Close backend window
echo   2. docker-compose -f docker\docker-compose-dev.yml down
echo.

pause
