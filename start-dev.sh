#!/bin/bash

# 🚀 AgentChat 本地开发启动脚本
# 启动 Docker 基础服务 + 本地代码

set -e

echo "🐳 AgentChat 本地开发环境启动..."
echo ""

# 切换到 docker 目录
cd "$(dirname "$0")/docker"

# 1. 启动 Docker 基础服务
echo "📦 启动 Docker 基础服务（MySQL、Redis、MinIO）..."
docker-compose -f docker-compose-dev.yml up -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 15

# 2. 检查服务状态
echo "📊 检查服务状态..."
docker-compose -f docker-compose-dev.yml ps

echo ""
echo "✅ Docker 基础服务已启动"
echo ""

# 3. 启动后端
echo "🚀 启动后端服务..."
cd ../src/backend

# 检查虚拟环境
if [ ! -d ".venv" ]; then
    echo "📥 首次运行，安装依赖..."
    pip install uv
    uv sync
fi

# 激活虚拟环境
source .venv/bin/activate

# 复制开发配置（如果不存在）
if [ ! -f "agentchat/config.yaml" ]; then
    cp agentchat/config-dev.yaml agentchat/config.yaml
    echo "⚠️  已创建默认配置文件，请编辑 src/backend/agentchat/config.yaml 填入 API 密钥"
fi

# 启动后端（带热重载）
echo "🔄 启动后端（热重载模式）..."
uvicorn agentchat.main:app --reload --host 0.0.0.0 --port 7860 &
BACKEND_PID=$!

echo ""
echo "✅ 本地开发环境启动完成！"
echo ""
echo "🌐 访问地址："
echo "  后端API:  http://localhost:7860"
echo "  API文档:  http://localhost:7860/docs"
echo "  MinIO控制台: http://localhost:9001"
echo ""
echo "📝 开发提示："
echo "  - 修改后端代码会自动热重载"
echo "  - 前端需要另外启动：cd src/frontend && npm run dev"
echo ""
echo "🛑 停止所有服务："
echo "  Ctrl+C 停止后端"
echo "  docker-compose -f docker/docker-compose-dev.yml down"
echo ""

# 等待后端进程
wait $BACKEND_PID
