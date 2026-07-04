@echo off
setlocal enabledelayedexpansion

REM ============================================================
REM  KirinChat Launcher - encoding-safe version
REM  Usage: kirinchat.bat <command> [options]
REM ============================================================

if "%~1"=="" goto :help
if "%~1"=="help" goto :help
if "%~1"=="--help" goto :help
if "%~1"=="-h" goto :help
if "%~1"=="up" goto :up
if "%~1"=="down" goto :down
if "%~1"=="status" goto :status
if "%~1"=="logs" goto :logs
if "%~1"=="clean" goto :clean
if "%~1"=="build" goto :build

echo [ERROR] Unknown command: %~1
echo Run 'kirinchat.bat help' to see available commands
exit /b 2

REM ============ help ============
:help
echo.
echo   KirinChat Launcher
echo   --------------------------------------------------------
echo.
echo   Usage: kirinchat.bat ^<command^> [options]
echo.
echo   Commands:
echo     up [options]      Start services
echo       --backend-only    Start Docker + Backend only
echo       --frontend-only   Start Frontend only
echo       --build           Force rebuild Docker images
echo     down              Stop all services
echo     status            Show Docker container status
echo     logs [service]    Show logs
echo     clean             Remove Docker data volumes (needs confirm)
echo     build             Rebuild Docker images
echo     help              Show this help message
echo.
echo   Examples:
echo     kirinchat.bat up                 Start all services
echo     kirinchat.bat up --backend-only  Start backend only
echo     kirinchat.bat down               Stop all services
echo     kirinchat.bat logs backend       Show backend logs
echo.
goto :eof

REM ============ up ============
:up
set "BACKEND_ONLY=false"
set "FRONTEND_ONLY=false"
set "FORCE_BUILD=false"

:parse_up_args
shift
if "%~0"=="" goto :do_up
if "%~0"=="--backend-only" set "BACKEND_ONLY=true"
if "%~0"=="--frontend-only" set "FRONTEND_ONLY=true"
if "%~0"=="--build" set "FORCE_BUILD=true"
goto :parse_up_args

:do_up
cd /d "%~dp0"

if "%FRONTEND_ONLY%"=="true" goto :up_frontend_only

REM Check Docker
docker info >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not running. Please start Docker Desktop.
    exit /b 3
)

if "%FORCE_BUILD%"=="true" (
    echo [Step] Rebuilding Docker images...
    docker compose -f docker\docker-compose-dev.yml up --build -d
) else (
    echo [Step] Starting Docker services...
    docker compose -f docker\docker-compose-dev.yml up -d
)

echo.
echo [Step] Checking Docker containers...
docker compose -f docker\docker-compose-dev.yml ps

echo.
echo [INFO] If some containers failed to pull images, please:
echo        1. Check your network connection
echo        2. Configure a Docker registry mirror (recommended in China)
echo           In Docker Desktop - Settings - Docker Engine:
echo           "registry-mirrors": ["https://docker.mirrors.ustc.edu.cn"]
echo        3. Or pull images manually: docker pull mysql:8.0
echo.

echo [Step] Waiting for services to be ready...
timeout /t 20 >nul

if "%BACKEND_ONLY%"=="true" goto :up_backend_only

REM Start all
call :ensure_backend_deps
call :ensure_frontend_deps

echo [Step] Starting Backend (port 7860)...
cd /d "%~dp0src\backend"
call .venv\Scripts\activate.bat
start "KirinChat Backend" cmd /k "title KirinChat Backend && uvicorn kirinchat.main:app --reload --host 0.0.0.0 --port 7860"

echo [Step] Starting Frontend (port 8090)...
cd /d "%~dp0src\frontend"
start "KirinChat Frontend" cmd /k "title KirinChat Frontend && npm run dev"

echo.
echo   --------------------------------------------------------
echo   [OK] KirinChat started successfully
echo   --------------------------------------------------------
echo.
echo   Frontend:      http://localhost:8090
echo   Backend API:   http://localhost:7860
echo   API Docs:      http://localhost:7860/docs
echo   MinIO Console: http://localhost:9001
echo.
echo   Close the backend/frontend windows to stop services,
echo   or run: kirinchat.bat down
echo.
pause
goto :eof

:up_backend_only
call :ensure_backend_deps

echo [Step] Starting Backend (port 7860)...
cd /d "%~dp0src\backend"
call .venv\Scripts\activate.bat
start "KirinChat Backend" cmd /k "title KirinChat Backend && uvicorn kirinchat.main:app --reload --host 0.0.0.0 --port 7860"

echo.
echo [OK] Backend started: http://localhost:7860
echo.
pause
goto :eof

:up_frontend_only
call :ensure_frontend_deps

echo [Step] Starting Frontend (port 8090)...
cd /d "%~dp0src\frontend"
start "KirinChat Frontend" cmd /k "title KirinChat Frontend && npm run dev"
goto :eof

REM ============ down ============
:down
cd /d "%~dp0"

echo [Step] Stopping Docker services...
docker compose -f docker\docker-compose-dev.yml down

if errorlevel 1 (
    echo [ERROR] Failed to stop services.
    pause
    exit /b 1
)

echo.
echo [OK] All services stopped.
echo.
echo   Data is preserved in Docker volumes.
echo   To clean all data: kirinchat.bat clean
echo.
pause
goto :eof

REM ============ status ============
:status
cd /d "%~dp0"
docker compose -f docker\docker-compose-dev.yml ps
echo.
pause
goto :eof

REM ============ logs ============
:logs
cd /d "%~dp0"
if "%~2"=="" (
    docker compose -f docker\docker-compose-dev.yml logs -f
) else (
    docker compose -f docker\docker-compose-dev.yml logs -f %~2
)
goto :eof

REM ============ clean ============
:clean
cd /d "%~dp0"

echo [WARNING] This will delete ALL data (database, cache, files)!
set /p CONFIRM="Confirm cleanup? (y/N): "
if /i not "%CONFIRM%"=="y" (
    echo Cancelled.
    pause
    goto :eof
)

echo [Step] Removing Docker data volumes...
docker compose -f docker\docker-compose-dev.yml down -v
echo [OK] Data cleaned.
pause
goto :eof

REM ============ build ============
:build
cd /d "%~dp0"
echo [Step] Rebuilding Docker images...
docker compose -f docker\docker-compose-dev.yml up --build -d
echo [OK] Build completed.
pause
goto :eof

REM ============ helper functions ============
:ensure_backend_deps
if not exist "%~dp0src\backend\.venv" (
    echo [Step] First run, installing backend dependencies...
    cd /d "%~dp0src\backend"
    call pip install uv
    call uv sync
    echo [OK] Backend dependencies installed.
)
if not exist "%~dp0src\backend\kirinchat\config.yaml" (
    echo [Step] Creating config file...
    copy "%~dp0src\backend\agentchat\config-dev.yaml" "%~dp0src\backend\kirinchat\config.yaml"
    echo [WARNING] Default config created. Please edit: src\backend\kirinchat\config.yaml
)
cd /d "%~dp0"
goto :eof

:ensure_frontend_deps
if not exist "%~dp0src\frontend\node_modules" (
    echo [Step] First run, installing frontend dependencies...
    cd /d "%~dp0src\frontend"
    call npm install
    echo [OK] Frontend dependencies installed.
)
cd /d "%~dp0"
goto :eof
