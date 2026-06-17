@echo off
setlocal enabledelayedexpansion

echo.
echo  AgentChat Local Development Environment
echo ============================================
echo.

REM Switch to project root directory
cd /d "%~dp0"

REM 1. Start Docker services
echo [Step 1/3] Starting Docker services...
echo.

docker-compose -f docker/docker-compose-dev.yml up -d

if errorlevel 1 (
    echo.
    echo ERROR: Docker services failed to start!
    echo Please check:
    echo   1. Docker Desktop is running
    echo   2. Ports are not in use (3306, 6379, 9000)
    echo.
    pause
    exit /b 1
)

echo.
echo SUCCESS: Docker services started
echo.

REM Wait for services to start
echo Waiting for services to start (20 seconds)...
timeout /t 20 >nul

REM 2. Start backend
echo [Step 2/3] Starting backend service...
echo.

cd src\backend

REM Check virtual environment
if not exist ".venv" (
    echo First run, installing backend dependencies...
    call pip install uv
    call uv sync
    if errorlevel 1 (
        echo ERROR: Dependencies installation failed!
        pause
        exit /b 1
    )
)

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Check config file
if not exist "agentchat\config.yaml" (
    echo Creating config file...
    copy agentchat\config-dev.yaml agentchat\config.yaml
    echo.
    echo IMPORTANT: Please edit this file to add API keys
    echo    File location: src\backend\agentchat\config.yaml
    echo.
    echo Required configurations:
    echo   - multi_models.conversation_model.api_key
    echo   - multi_models.embedding.api_key
    echo   - tools.weather.api_key (optional)
    echo.
    notepad agentchat\config.yaml
    echo.
    echo Press any key to continue after configuration...
    pause >nul
)

REM Start backend
echo Starting backend service (port 7860)...
start "AgentChat Backend" cmd /k "title AgentChat Backend && uvicorn agentchat.main:app --reload --host 0.0.0.0 --port 7860"

echo Backend service starting...
echo.

REM 3. Start frontend
echo [Step 3/3] Starting frontend service...
echo.

cd ..\frontend

REM Check dependencies
if not exist "node_modules" (
    echo First run, installing frontend dependencies...
    call npm install
    if errorlevel 1 (
        echo ERROR: Dependencies installation failed!
        pause
        exit /b 1
    )
)

REM Start frontend
echo Starting frontend service (port 8090)...
start "AgentChat Frontend" cmd /k "title AgentChat Frontend && npm run dev"

echo Frontend service starting...
echo.

REM Wait for services to start
echo Waiting for services to be ready...
timeout /t 10 >nul

echo.
echo ============================================
echo   SUCCESS: AgentChat local environment started!
echo ============================================
echo.
echo Access URLs:
echo.
echo   Frontend:      http://localhost:8090
echo   Backend API:   http://localhost:7860
echo   API Docs:      http://localhost:7860/docs
echo   MinIO Console: http://localhost:9001
echo.
echo Development Tips:
echo.
echo   - Backend code changes will auto-reload
echo   - Frontend code changes will auto-update
echo   - Config file: src\backend\agentchat\config.yaml
echo.
echo Stop all services:
echo.
echo   1. Close backend and frontend windows
echo   2. Run stop-dev.bat
echo.
echo ============================================
echo.

pause
