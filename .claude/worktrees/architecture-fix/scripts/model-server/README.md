# 本地模型推理服务

本地部署 BGE-M3 (Embedding) 和 BGE-Reranker-Base (Rerank) 模型，替代远程 API 调用。

## 快速启动

### Windows
```bash
cd scripts/model-server
start-model-server.bat
```

### Linux/Mac
```bash
cd scripts/model-server
chmod +x start-model-server.sh
./start-model-server.sh
```

## 手动启动

```bash
cd scripts/model-server

# 安装依赖 (首次)
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 启动服务
python server.py \
    --embedding-path "D:/models/bge-m3" \
    --rerank-path "D:/models/bge-reranker-base" \
    --port 8080 \
    --host 127.0.0.1 \
    --device cpu   # 或 cuda (如果有 GPU)
```

## 参数说明

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--embedding-path` | `D:/models/bge-m3` | Embedding 模型路径 |
| `--rerank-path` | `D:/models/bge-reranker-base` | Rerank 模型路径 |
| `--port` | `8080` | 服务端口 |
| `--host` | `127.0.0.1` | 监听地址 |
| `--device` | 自动检测 | `cpu` 或 `cuda` |

## API 接口

### 健康检查
```
GET http://127.0.0.1:8080/health
```

### Embedding (OpenAI 兼容)
```
POST http://127.0.0.1:8080/v1/embeddings
Content-Type: application/json

{
    "model": "bge-m3",
    "input": "你好世界",
    "encoding_format": "float"
}
```

### Rerank (DashScope 兼容)
```
POST http://127.0.0.1:8080/v1/rerank
Content-Type: application/json

{
    "model": "bge-reranker-base",
    "input": {
        "query": "什么是机器学习",
        "documents": ["机器学习是AI的分支", "今天天气很好"]
    },
    "parameters": {
        "return_documents": true,
        "top_n": 5
    }
}
```

## config.yaml 配置

确保 `src/backend/agentchat/config.yaml` 中的 embedding 和 rerank 配置如下：

```yaml
multi_models:
  embedding:
    api_key: "not-needed"
    base_url: "http://127.0.0.1:8080/v1"
    model_name: "bge-m3"
  rerank:
    api_key: "not-needed"
    base_url: "http://127.0.0.1:8080/v1/rerank"
    model_name: "bge-reranker-base"
```

## 硬件建议

| 配置 | 设备 | 首次加载 | 推理速度 |
|------|------|----------|----------|
| 有 NVIDIA GPU | `--device cuda` | ~10s | 快 |
| 仅 CPU | `--device cpu` | ~30s | 较慢但可用 |

> BGE-M3 和 BGE-Reranker-Base 模型不大，CPU 也能正常运行。
