#!/bin/bash
set -e

echo "========================================"
echo "  本地模型推理服务启动脚本"
echo "  Embedding: BGE-M3"
echo "  Rerank: BGE-Reranker-Base"
echo "========================================"
echo

cd "$(dirname "$0")"

# 检查并安装依赖
echo "[1/2] 检查依赖..."
if ! python -c "import sentence_transformers" 2>/dev/null; then
    echo "[安装] 正在安装依赖..."
    pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
else
    echo "[完成] 依赖已安装"
fi

echo
echo "[2/2] 启动模型服务 (端口 8080)..."
echo "[提示] 首次加载模型需要一些时间，请耐心等待"
echo "[提示] 按 Ctrl+C 停止服务"
echo

python server.py \
    --embedding-path "D:/models/bge-m3" \
    --rerank-path "D:/models/bge-reranker-base" \
    --port 8080 \
    --host 127.0.0.1
