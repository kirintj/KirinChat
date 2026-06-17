#!/bin/bash

# 🛑 AgentChat 本地开发环境停止脚本

set -e

echo "🛑 停止 AgentChat 本地开发环境..."
echo ""

# 停止 Docker 服务
echo "📦 停止 Docker 基础服务..."
cd "$(dirname "$0")/docker"
docker-compose -f docker-compose-dev.yml down

echo ""
echo "✅ 所有服务已停止"
echo ""
echo "💡 提示："
echo "   数据已保留在 Docker 卷中"
echo "   完全清理数据：docker-compose -f docker-compose-dev.yml down -v"
echo ""
