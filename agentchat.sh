#!/bin/bash
# KirinChat 统一启动脚本
# 用法: ./agentchat.sh <command> [options]

set -e
set -o pipefail

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
    if ! docker info &>/dev/null; then
        error "Docker 未运行，请启动 Docker Desktop"
        exit 3
    fi
}

check_compose() {
    if docker compose version &>/dev/null; then
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
        (
            cd "$BACKEND_DIR"
            if ! command -v uv &>/dev/null; then
                pip install --user uv
            fi
            uv sync
        )
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
        (
            cd "$FRONTEND_DIR"
            npm install
        )
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
    if [ -n "$FRONTEND_PID" ]; then kill "$FRONTEND_PID" 2>/dev/null || true; echo "  前端已停止"; fi
    if [ -n "$BACKEND_PID" ]; then kill "$BACKEND_PID" 2>/dev/null || true; echo "  后端已停止"; fi
    info "服务已停止"
}

# ─── 子命令: help ────────────────────────────────────────
cmd_help() {
    echo ""
    echo "  KirinChat 统一启动脚本"
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
    echo "  ✅ KirinChat 已启动"
    echo "  ─────────────────────────────────────"
    echo ""
    echo "  前端界面:    http://localhost:8090"
    echo "  后端API:     http://localhost:7860"
    echo "  API文档:     http://localhost:7860/docs"
    echo "  MinIO控制台: http://localhost:9001"
    echo ""
    echo "  按 Ctrl+C 停止所有服务"
    echo ""

    wait || true
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
