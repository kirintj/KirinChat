@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul 2>&1

REM AgentChat 统一启动脚本
REM 用法: agentchat.bat <command> [options]

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

echo [ERROR] 未知命令: %~1
echo 运行 agentchat.bat help 查看可用命令
exit /b 2

REM ─── help ──────────────────────────────────────────────
:help
echo.
echo   AgentChat 统一启动脚本
echo   ─────────────────────────────────────
echo.
echo   用法: agentchat.bat ^<command^> [options]
echo.
echo   命令:
echo     up [options]      启动服务
echo       --backend-only    只启动 Docker + 后端
echo       --frontend-only   只启动前端
echo       --build           强制重新构建 Docker 镜像
echo     down              停止所有服务
echo     status            查看 Docker 容器状态
echo     logs [service]    查看日志
echo     clean             清除 Docker 数据卷（需二次确认）
echo     build             重新构建 Docker 镜像
echo     help              显示本帮助信息
echo.
echo   示例:
echo     agentchat.bat up                 启动全部服务
echo     agentchat.bat up --backend-only  只启动后端
echo     agentchat.bat down               停止所有服务
echo     agentchat.bat logs backend       查看后端日志
echo.
goto :eof

REM ─── up ────────────────────────────────────────────────
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

REM 检查 Docker
docker info >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker 未运行，请启动 Docker Desktop
    exit /b 3
)

if "%FORCE_BUILD%"=="true" (
    echo [步骤] 重新构建 Docker 镜像...
    docker compose -f docker\docker-compose-dev.yml up --build -d
) else (
    echo [步骤] 启动 Docker 基础服务...
    docker compose -f docker\docker-compose-dev.yml up -d
)

if errorlevel 1 (
    echo [ERROR] Docker 服务启动失败
    pause
    exit /b 1
)

echo [步骤] 等待服务就绪...
timeout /t 20 >nul

if "%BACKEND_ONLY%"=="true" goto :up_backend_only

REM 启动全部
call :ensure_backend_deps
call :ensure_frontend_deps

echo [步骤] 启动后端服务（端口 7860）...
cd /d "%~dp0src\backend"
call .venv\Scripts\activate.bat
start "AgentChat Backend" cmd /k "title AgentChat Backend && uvicorn agentchat.main:app --reload --host 0.0.0.0 --port 7860"

echo [步骤] 启动前端服务（端口 8090）...
cd /d "%~dp0src\frontend"
start "AgentChat Frontend" cmd /k "title AgentChat Frontend && npm run dev"

timeout /t 5 >nul

echo.
echo   ─────────────────────────────────────
echo   ✅ AgentChat 已启动
echo   ─────────────────────────────────────
echo.
echo   前端界面:    http://localhost:8090
echo   后端API:     http://localhost:7860
echo   API文档:     http://localhost:7860/docs
echo   MinIO控制台: http://localhost:9001
echo.
echo   关闭后端和前端窗口停止服务
echo   或运行 agentchat.bat down
echo.
pause
goto :eof

:up_backend_only
call :ensure_backend_deps

echo [步骤] 启动后端服务（端口 7860）...
cd /d "%~dp0src\backend"
call .venv\Scripts\activate.bat
start "AgentChat Backend" cmd /k "title AgentChat Backend && uvicorn agentchat.main:app --reload --host 0.0.0.0 --port 7860"

echo.
echo ✅ 后端已启动: http://localhost:7860
echo.
pause
goto :eof

:up_frontend_only
call :ensure_frontend_deps

echo [步骤] 启动前端服务（端口 8090）...
cd /d "%~dp0src\frontend"
npm run dev
goto :eof

REM ─── down ──────────────────────────────────────────────
:down
cd /d "%~dp0"

echo [步骤] 停止 Docker 服务...
docker compose -f docker\docker-compose-dev.yml down

if errorlevel 1 (
    echo [ERROR] 停止服务失败
    pause
    exit /b 1
)

echo.
echo ✅ 所有服务已停止
echo.
echo   数据已保留在 Docker 卷中
echo   完全清理数据: agentchat.bat clean
echo.
pause
goto :eof

REM ─── status ────────────────────────────────────────────
:status
cd /d "%~dp0"
docker compose -f docker\docker-compose-dev.yml ps
echo.
pause
goto :eof

REM ─── logs ──────────────────────────────────────────────
:logs
cd /d "%~dp0"
if "%~2"=="" (
    docker compose -f docker\docker-compose-dev.yml logs -f
) else (
    docker compose -f docker\docker-compose-dev.yml logs -f %~2
)
goto :eof

REM ─── clean ─────────────────────────────────────────────
:clean
cd /d "%~dp0"

echo [警告] 此操作将删除所有数据（数据库、缓存、文件）！
set /p CONFIRM="确认清除？(y/N): "
if /i not "%CONFIRM%"=="y" (
    echo 已取消
    pause
    goto :eof
)

echo [步骤] 清除 Docker 数据卷...
docker compose -f docker\docker-compose-dev.yml down -v
echo ✅ 数据已清除
pause
goto :eof

REM ─── build ─────────────────────────────────────────────
:build
cd /d "%~dp0"
echo [步骤] 重新构建 Docker 镜像...
docker compose -f docker\docker-compose-dev.yml up --build -d
echo ✅ 构建完成
pause
goto :eof

REM ─── 辅助函数 ──────────────────────────────────────────
:ensure_backend_deps
if not exist "%~dp0src\backend\.venv" (
    echo [步骤] 首次运行，安装后端依赖...
    cd /d "%~dp0src\backend"
    call pip install uv
    call uv sync
    echo ✅ 后端依赖安装完成
)
if not exist "%~dp0src\backend\agentchat\config.yaml" (
    echo [步骤] 创建配置文件...
    copy "%~dp0src\backend\agentchat\config-dev.yaml" "%~dp0src\backend\agentchat\config.yaml"
    echo [警告] 已创建默认配置文件，请编辑 src\backend\agentchat\config.yaml
)
goto :eof

:ensure_frontend_deps
if not exist "%~dp0src\frontend\node_modules" (
    echo [步骤] 首次运行，安装前端依赖...
    cd /d "%~dp0src\frontend"
    call npm install
    echo ✅ 前端依赖安装完成
)
goto :eof
