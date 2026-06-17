#!/bin/bash

set -e

echo ""
echo "  █████╗  ██████╗ ███████╗███╗   ██╗████████╗ ██████╗██╗  ██╗ █████╗ ████████╗"
echo " ██╔══██╗██╔════╝ ██╔════╝████╗  ██║╚══██╔══╝██╔════╝██║  ██║██╔══██╗╚══██╔══╝"
echo " ███████║██║  ███╗█████╗  ██╔██╗ ██║   ██║   ██║     ███████║███████║   ██║"
echo " ██╔══██║██║   ██║██╔══╝  ██║╚██╗██║   ██║   ██║     ██╔══██║██╔══██║   ██║"
echo " ██║  ██║╚██████╔╝███████╗██║ ╚████║   ██║   ╚██████╗██║  ██║██║  ██║   ██║"
echo " ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═══╝   ╚═╝    ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝"
echo ""
echo "============================================"
echo "  本地开发环境 - 完整启动脚本"
echo "============================================"
echo ""

# 切换到项目根目录
cd "$(dirname "$0")"

# 1. 启动 Docker 基础服务
echo "[步骤 1/3] 启动 Docker 基础服务..."
echo ""

docker-compose -f docker/docker-compose-dev.yml up -d

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Docker 服务启动失败！"
    echo "请检查："
    echo "  1. Docker 是否运行"
    echo "  2. 端口是否被占用（3306, 6379, 9000）"
    echo ""
    exit 1
fi

echo ""
echo "✅ Docker 服务启动成功"
echo ""

# 等待服务完全启动
echo "⏳ 等待服务完全启动（约 20 秒）..."
sleep 20

# 2. 启动后端
echo "[步骤 2/3] 启动后端服务..."
echo ""

cd src/backend

# 检查虚拟环境
if [ ! -d ".venv" ]; then
    echo "📥 首次运行，安装后端依赖..."
    pip install uv
    uv sync
    if [ $? -ne 0 ]; then
        echo "❌ 依赖安装失败！"
        exit 1
    fi
fi

# 激活虚拟环境
source .venv/bin/activate

# 检查配置文件
if [ ! -f "agentchat/config.yaml" ]; then
    echo "📝 创建配置文件..."
    cp agentchat/config-dev.yaml agentchat/config.yaml
    echo ""
    echo "⚠️  重要：请编辑以下文件填入 API 密钥"
    echo "   文件位置：src/backend/agentchat/config.yaml"
    echo ""
    echo "需要配置的密钥："
    echo "  - multi_models.conversation_model.api_key（通义千问）"
    echo "  - multi_models.embedding.api_key（通义千问）"
    echo "  - tools.weather.api_key（高德天气，可选）"
    echo ""
    echo "配置完成后按回车继续..."
    read -r
fi

# 启动后端
echo "🚀 启动后端服务（端口 7860）..."
uvicorn agentchat.main:app --reload --host 0.0.0.0 --port 7860 &
BACKEND_PID=$!

echo "✅ 后端服务启动中..."
echo ""

# 3. 启动前端
echo "[步骤 3/3] 启动前端服务..."
echo ""

cd ../frontend

# 检查依赖
if [ ! -d "node_modules" ]; then
    echo "📥 首次运行，安装前端依赖..."
    npm install
    if [ $? -ne 0 ]; then
        echo "❌ 依赖安装失败！"
        exit 1
    fi
fi

# 启动前端
echo "🚀 启动前端服务（端口 8090）..."
npm run dev &
FRONTEND_PID=$!

echo "✅ 前端服务启动中..."
echo ""

# 等待服务启动
echo "⏳ 等待服务就绪..."
sleep 10

echo ""
echo "============================================"
echo "  ✅ AgentChat 本地开发环境启动完成！"
echo "============================================"
echo ""
echo "🌐 访问地址："
echo ""
echo "  前端界面：    http://localhost:8090"
echo "  后端API：     http://localhost:7860"
echo "  API文档：     http://localhost:7860/docs"
echo "  MinIO控制台： http://localhost:9001"
echo ""
echo "📝 开发提示："
echo ""
echo "  - 修改后端代码会自动热重载"
echo "  - 修改前端代码会自动热更新"
echo "  - 配置文件：src/backend/agentchat/config.yaml"
echo ""
echo "🛑 停止所有服务："
echo ""
echo "  按 Ctrl+C 停止所有服务"
echo "  或运行 ./stop-dev.sh"
echo ""
echo "============================================"
echo ""

# 等待子进程
wait
