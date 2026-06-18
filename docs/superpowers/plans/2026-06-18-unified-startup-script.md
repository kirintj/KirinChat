# 统一启动脚本实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将项目中 12 个分散的启动/停止脚本合并为 2 个统一入口脚本 `agentchat.sh` + `agentchat.bat`，通过子命令提供所有功能。

**Architecture:** 两个平台脚本各自独立，通过子命令（up/down/status/logs/clean/build/help）统一操作 Docker、后端、前端服务。脚本内置首次运行检测（自动安装依赖、复制配置）和健康检查（替代固定 sleep）。

**Tech Stack:** Bash (sh), Windows Batch (cmd.exe), docker-compose

---

## File Structure

| 操作 | 文件 | 职责 |
|------|------|------|
| Create | `agentchat.sh` | Bash 统一入口脚本 |
| Create | `agentchat.bat` | Windows Batch 统一入口脚本 |
| Delete | `start-all.sh` | 被 `agentchat.sh up` 替代 |
| Delete | `start-all.bat` | 被 `agentchat.bat up` 替代 |
| Delete | `start-dev.sh` | 被 `agentchat.sh up --backend-only` 替代 |
| Delete | `start-dev.bat` | 被 `agentchat.bat up --backend-only` 替代 |
| Delete | `start-frontend.sh` | 被 `agentchat.sh up --frontend-only` 替代 |
| Delete | `start-frontend.bat` | 被 `agentchat.bat up --frontend-only` 替代 |
| Delete | `stop-dev.sh` | 被 `agentchat.sh down` 替代 |
| Delete | `stop-dev.bat` | 被 `agentchat.bat down` 替代 |
| Delete | `docker/start_linux.sh` | 被 `agentchat.sh build` 替代 |
| Delete | `docker/start_win.bat` | 被 `agentchat.bat build` 替代 |

---

### Task 1: 创建 agentchat.sh（Bash 统一脚本）

**Files:**
- Create: `agentchat.sh`

- [ ] **Step 1: 创建 agentchat.sh 文件**

创建完整的 Bash 统一入口脚本，包含所有子命令：up、down、status、logs、clean、build、help。

```bash
#!/bin/bash
# AgentChat 统一启动脚本
# 用法: ./agentchat.sh <command> [options]

set -e

# ─── 颜色定义 ────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ─── 项目路径 ────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"
DOCKER_DIR="$PROJECT_ROOT/docker"
BACKEND_DIR="$PROJECT_ROOT/src/backend"
FRONTEND_DIR="$PROJECT_ROOT/src/frontend"
COMPOSE_FILE="$DOCKER_DIR/docker-compose-dev.yml"

# ─── 日志函数 ────────────────────────────────────────────
info()  { echo -e "${GREEN}✅ $*${NC}"; }
warn()  { echo -e "${YELLOW}⚠️  $*${NC}"; }
error() { echo -e "${RED}❌ $*${NC}"; }
step()  { echo -e "${BLUE}[步骤]${NC} $*"; }

# ─── 依赖检查 ────────────────────────────────────────────
check_docker() {
    if ! command -v docker &>/dev/null; then
        error "Docker 未安装，请先安装 Docker"
        exit 3
    fi
    if ! docker info &>/dev/null 2>&1; then
        error "Docker 未运行，请启动 Docker Desktop"
        exit 3
    fi
}

check_compose() {
    if docker compose version &>/dev/null 2>&1; then
        COMPOSE_CMD="docker compose"
    elif command -v docker-compose &>/dev/null; then
        COMPOSE_CMD="docker-compose"
    else
        error "docker-compose 未安装"
        exit 3
    fi
}

# ─── 首次运行检测 ────────────────────────────────────────
ensure_backend_deps() {
    if [ ! -d "$BACKEND_DIR/.venv" ]; then
        step "首次运行，安装后端依赖..."
        cd "$BACKEND_DIR"
        pip install uv
        uv sync
        info "后端依赖安装完成"
    fi

    if [ ! -f "$BACKEND_DIR/agentchat/config.yaml" ]; then
        step "创建配置文件..."
        cp "$BACKEND_DIR/agentchat/config-dev.yaml" "$BACKEND_DIR/agentchat/config.yaml"
        warn "已创建默认配置文件，请编辑 src/backend/agentchat/config.yaml 填入 API 密钥"
    fi
}

ensure_frontend_deps() {
    if [ ! -d "$FRONTEND_DIR/node_modules" ]; then
        step "首次运行，安装前端依赖..."
        cd "$FRONTEND_DIR"
        npm install
        info "前端依赖安装完成"
    fi
}

# ─── 健康检查 ────────────────────────────────────────────
wait_for_healthy() {
    local max_wait=60
    local waited=0
    step "等待 Docker 服务就绪..."
    while [ $waited -lt $max_wait ]; do
        if $COMPOSE_CMD -f "$COMPOSE_FILE" ps 2>/dev/null | grep -q "healthy"; then
            info "Docker 服务已就绪"
            return 0
        fi
        sleep 3
        waited=$((waited + 3))
        echo -n "."
    done
    echo ""
    error "Docker 服务启动超时（${max_wait}秒）"
    exit 1
}

# ─── 进程追踪 ────────────────────────────────────────────
BACKEND_PID=""
FRONTEND_PID=""

cleanup() {
    echo ""
    step "正在停止服务..."
    [ -n "$FRONTEND_PID" ] && kill "$FRONTEND_PID" 2>/dev/null && echo "  前端已停止"
    [ -n "$BACKEND_PID" ] && kill "$BACKEND_PID" 2>/dev/null && echo "  后端已停止"
    info "服务已停止"
}

# ─── 子命令: help ────────────────────────────────────────
cmd_help() {
    echo ""
    echo "  AgentChat 统一启动脚本"
    echo "  ─────────────────────────────────────"
    echo ""
    echo "  用法: ./agentchat.sh <command> [options]"
    echo ""
    echo "  命令:"
    echo "    up [options]      启动服务"
    echo "      --backend-only    只启动 Docker + 后端"
    echo "      --frontend-only   只启动前端"
    echo "      --build           强制重新构建 Docker 镜像"
    echo "    down              停止所有服务"
    echo "    status            查看 Docker 容器状态"
    echo "    logs [service]    查看日志（可选: backend/frontend/mysql/redis/minio）"
    echo "    clean             清除 Docker 数据卷（需二次确认）"
    echo "    build             重新构建 Docker 镜像"
    echo "    help              显示本帮助信息"
    echo ""
    echo "  示例:"
    echo "    ./agentchat.sh up                 # 启动全部服务"
    echo "    ./agentchat.sh up --backend-only  # 只启动后端"
    echo "    ./agentchat.sh down               # 停止所有服务"
    echo "    ./agentchat.sh logs backend       # 查看后端日志"
    echo ""
}

# ─── 子命令: up ──────────────────────────────────────────
cmd_up() {
    local backend_only=false
    local frontend_only=false
    local force_build=false

    while [ $# -gt 0 ]; do
        case "$1" in
            --backend-only)  backend_only=true ;;
            --frontend-only) frontend_only=true ;;
            --build)         force_build=true ;;
            *)               error "未知选项: $1"; exit 2 ;;
        esac
        shift
    done

    if [ "$frontend_only" = true ]; then
        # 只启动前端
        ensure_frontend_deps
        step "启动前端服务（端口 8090）..."
        cd "$FRONTEND_DIR"
        npm run dev
        return
    fi

    # 启动 Docker
    check_docker
    check_compose

    if [ "$force_build" = true ]; then
        step "重新构建 Docker 镜像..."
        $COMPOSE_CMD -f "$COMPOSE_FILE" up --build -d
    else
        step "启动 Docker 基础服务（MySQL, Redis, MinIO）..."
        $COMPOSE_CMD -f "$COMPOSE_FILE" up -d
    fi

    wait_for_healthy

    if [ "$backend_only" = true ]; then
        # 只启动后端
        ensure_backend_deps
        step "启动后端服务（端口 7860）..."
        cd "$BACKEND_DIR"
        source .venv/bin/activate
        uvicorn agentchat.main:app --reload --host 0.0.0.0 --port 7860
        return
    fi

    # 启动全部
    ensure_backend_deps
    ensure_frontend_deps

    trap cleanup SIGINT SIGTERM

    step "启动后端服务（端口 7860）..."
    cd "$BACKEND_DIR"
    source .venv/bin/activate
    uvicorn agentchat.main:app --reload --host 0.0.0.0 --port 7860 &
    BACKEND_PID=$!

    step "启动前端服务（端口 8090）..."
    cd "$FRONTEND_DIR"
    npm run dev &
    FRONTEND_PID=$!

    echo ""
    echo "  ─────────────────────────────────────"
    echo "  ✅ AgentChat 已启动"
    echo "  ─────────────────────────────────────"
    echo ""
    echo "  前端界面:    http://localhost:8090"
    echo "  后端API:     http://localhost:7860"
    echo "  API文档:     http://localhost:7860/docs"
    echo "  MinIO控制台: http://localhost:9001"
    echo ""
    echo "  按 Ctrl+C 停止所有服务"
    echo ""

    wait
}

# ─── 子命令: down ────────────────────────────────────────
cmd_down() {
    check_docker
    check_compose

    step "停止 Docker 服务..."
    $COMPOSE_CMD -f "$COMPOSE_FILE" down

    info "所有服务已停止"
    echo ""
    echo "  数据已保留在 Docker 卷中"
    echo "  完全清理数据: ./agentchat.sh clean"
    echo ""
}

# ─── 子命令: status ──────────────────────────────────────
cmd_status() {
    check_docker
    check_compose

    $COMPOSE_CMD -f "$COMPOSE_FILE" ps
}

# ─── 子命令: logs ────────────────────────────────────────
cmd_logs() {
    check_docker
    check_compose

    if [ -n "$1" ]; then
        $COMPOSE_CMD -f "$COMPOSE_FILE" logs -f "$1"
    else
        $COMPOSE_CMD -f "$COMPOSE_FILE" logs -f
    fi
}

# ─── 子命令: clean ───────────────────────────────────────
cmd_clean() {
    check_docker
    check_compose

    warn "此操作将删除所有数据（数据库、缓存、文件）！"
    read -p "确认清除？(y/N) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        step "清除 Docker 数据卷..."
        $COMPOSE_CMD -f "$COMPOSE_FILE" down -v
        info "数据已清除"
    else
        echo "已取消"
    fi
}

# ─── 子命令: build ───────────────────────────────────────
cmd_build() {
    check_docker
    check_compose

    step "重新构建 Docker 镜像..."
    $COMPOSE_CMD -f "$COMPOSE_FILE" up --build -d
    info "构建完成"
}

# ─── 主入口 ──────────────────────────────────────────────
if [ $# -eq 0 ]; then
    cmd_help
    exit 0
fi

COMMAND="$1"
shift

case "$COMMAND" in
    up)      cmd_up "$@" ;;
    down)    cmd_down ;;
    status)  cmd_status ;;
    logs)    cmd_logs "$@" ;;
    clean)   cmd_clean ;;
    build)   cmd_build ;;
    help)    cmd_help ;;
    -h|--help) cmd_help ;;
    *)
        error "未知命令: $COMMAND"
        echo "运行 ./agentchat.sh help 查看可用命令"
        exit 2
        ;;
esac
```

- [ ] **Step 2: 设置可执行权限**

```bash
chmod +x agentchat.sh
```

- [ ] **Step 3: 验证 help 命令**

```bash
./agentchat.sh help
```

Expected: 显示帮助信息，列出所有子命令。

- [ ] **Step 4: Commit**

```bash
git add agentchat.sh
git commit -m "feat: add unified startup script (bash)"
```

---

### Task 2: 创建 agentchat.bat（Windows Batch 统一脚本）

**Files:**
- Create: `agentchat.bat`

- [ ] **Step 1: 创建 agentchat.bat 文件**

创建完整的 Windows Batch 统一入口脚本。

```batch
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
```

- [ ] **Step 2: 验证 help 命令**

```cmd
agentchat.bat help
```

Expected: 显示帮助信息，列出所有子命令。

- [ ] **Step 3: Commit**

```bash
git add agentchat.bat
git commit -m "feat: add unified startup script (batch)"
```

---

### Task 3: 删除旧启动脚本

**Files:**
- Delete: `start-all.sh`
- Delete: `start-all.bat`
- Delete: `start-dev.sh`
- Delete: `start-dev.bat`
- Delete: `start-frontend.sh`
- Delete: `start-frontend.bat`
- Delete: `stop-dev.sh`
- Delete: `stop-dev.bat`
- Delete: `docker/start_linux.sh`
- Delete: `docker/start_win.bat`

- [ ] **Step 1: 删除根目录旧脚本**

```bash
rm -f start-all.sh start-all.bat start-dev.sh start-dev.bat start-frontend.sh start-frontend.bat stop-dev.sh stop-dev.bat
```

- [ ] **Step 2: 删除 docker 目录旧脚本**

```bash
rm -f docker/start_linux.sh docker/start_win.bat
```

- [ ] **Step 3: 验证文件已删除**

```bash
ls start-*.sh start-*.bat stop-*.sh stop-*.bat 2>/dev/null && echo "ERROR: 旧脚本仍存在" || echo "OK: 旧脚本已全部删除"
ls docker/start_*.sh docker/start_*.bat 2>/dev/null && echo "ERROR: docker旧脚本仍存在" || echo "OK: docker旧脚本已全部删除"
```

Expected: 两行都显示 "OK"。

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "chore: remove legacy startup scripts (replaced by agentchat.sh/bat)"
```

---

### Task 4: 端到端验证

- [ ] **Step 1: 验证 Bash 脚本 help 输出**

```bash
./agentchat.sh help
```

Expected: 显示帮助信息，包含 up/down/status/logs/clean/build/help 所有子命令。

- [ ] **Step 2: 验证 Bash 脚本错误处理**

```bash
./agentchat.sh invalid_command
```

Expected: 退出码 2，显示 "未知命令" 错误。

- [ ] **Step 3: 验证 Batch 脚本 help 输出**

```cmd
agentchat.bat help
```

Expected: 显示帮助信息，与 Bash 版本一致。

- [ ] **Step 4: 验证 Batch 脚本错误处理**

```cmd
agentchat.bat invalid_command
```

Expected: 退出码 2，显示 "未知命令" 错误。

- [ ] **Step 5: 最终 Commit**

```bash
git add -A
git commit -m "docs: update references to use agentchat.sh/bat"
```
