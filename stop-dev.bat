@echo off
setlocal

echo ============================================
echo   AgentChat Local Environment Stop
echo ============================================
echo.

REM Switch to project root directory
cd /d "%~dp0"

REM Stop Docker services
echo Stopping Docker services...
docker-compose -f docker/docker-compose-dev.yml down

if errorlevel 1 (
    echo ERROR: Failed to stop services!
    pause
    exit /b 1
)

echo.
echo SUCCESS: All services stopped
echo.
echo Note: Data is preserved in Docker volumes
echo To completely clean data: docker-compose -f docker\docker-compose-dev.yml down -v
echo.

pause
