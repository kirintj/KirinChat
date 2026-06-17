#!/bin/bash

# 🎨 AgentChat 前端开发启动脚本

set -e

echo "🎨 启动 AgentChat 前端开发服务器..."
echo ""

# 切换到前端目录
cd "$(dirname "$0")/src/frontend"

# 检查依赖
if [ ! -d "node_modules" ]; then
    echo "📥 首次运行，安装依赖..."
    npm install
fi

# 启动开发服务器
echo "🚀 启动前端开发服务器..."
npm run dev

echo ""
echo "✅ 前端启动完成！"
echo "🌐 访问地址：http://localhost:8090"
echo ""
