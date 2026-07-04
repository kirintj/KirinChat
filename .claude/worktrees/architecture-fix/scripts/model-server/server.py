"""
本地模型推理服务
- Embedding: BGE-M3 (OpenAI 兼容 API)
- Rerank: BGE-Reranker-Base (DashScope 兼容 API)

Lazy loading: 模型在首次请求时才加载，减少启动内存占用。

用法:
    python server.py
    python server.py --embedding-path D:/models/bge-m3 --rerank-path D:/models/bge-reranker-base --port 8080
"""

import argparse
import gc
import sys
import threading
from contextlib import asynccontextmanager
from typing import List, Union

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import numpy as np
import torch
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel, Field

# ========== 模型路径 (全局) ==========
_embedding_path: str = ""
_rerank_path: str = ""
_device: str = "cpu"

# ========== 延迟加载的模型实例 ==========
_embedding_model = None
_rerank_model = None
_embedding_lock = threading.Lock()
_rerank_lock = threading.Lock()


def get_embedding_model():
    global _embedding_model
    if _embedding_model is None:
        with _embedding_lock:
            if _embedding_model is None:  # double-check
                from sentence_transformers import SentenceTransformer
                print(f"[model] Loading Embedding: {_embedding_path} ...")
                _embedding_model = SentenceTransformer(_embedding_path, device=_device)
                print("[model] Embedding loaded OK")
    return _embedding_model


def get_rerank_model():
    global _rerank_model
    if _rerank_model is None:
        with _rerank_lock:
            if _rerank_model is None:  # double-check
                from sentence_transformers import CrossEncoder
                print(f"[model] Loading Rerank: {_rerank_path} ...")
                _rerank_model = CrossEncoder(_rerank_path, device=_device, max_length=512)
                print("[model] Rerank loaded OK")
    return _rerank_model


# ========== Request / Response ==========
class EmbeddingRequest(BaseModel):
    model: str = "bge-m3"
    input: Union[str, List[str]]
    encoding_format: str = "float"


class EmbeddingData(BaseModel):
    object: str = "embedding"
    embedding: List[float]
    index: int = 0


class EmbeddingUsage(BaseModel):
    prompt_tokens: int = 0
    total_tokens: int = 0


class EmbeddingResponse(BaseModel):
    object: str = "list"
    data: List[EmbeddingData]
    model: str = "bge-m3"
    usage: EmbeddingUsage


class RerankInput(BaseModel):
    query: str
    documents: List[str]


class RerankParameters(BaseModel):
    return_documents: bool = True
    top_n: int = 10


class RerankRequest(BaseModel):
    model: str = "bge-reranker-base"
    input: RerankInput
    parameters: RerankParameters = Field(default_factory=RerankParameters)


class RerankResult(BaseModel):
    index: int
    relevance_score: float
    document: str = None


class RerankOutput(BaseModel):
    results: List[RerankResult]


class RerankResponse(BaseModel):
    output: RerankOutput
    usage: dict = Field(default_factory=lambda: {"total_tokens": 0})


# ========== FastAPI ==========
@asynccontextmanager
async def lifespan(app: FastAPI):
    global _embedding_path, _rerank_path, _device

    parser = argparse.ArgumentParser()
    parser.add_argument("--embedding-path", default="D:/models/bge-m3")
    parser.add_argument("--rerank-path", default="D:/models/bge-reranker-base")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--device", default=None)
    args, _ = parser.parse_known_args()

    _embedding_path = args.embedding_path
    _rerank_path = args.rerank_path
    _device = args.device or ("cuda" if torch.cuda.is_available() else "cpu")

    print(f"[server] Device: {_device}")
    print(f"[server] Embedding path: {_embedding_path}")
    print(f"[server] Rerank path: {_rerank_path}")
    print(f"[server] Models will be loaded on first request (lazy)")
    print(f"[server] Ready on http://127.0.0.1:{args.port}")

    yield
    print("[server] Shutdown")


app = FastAPI(title="Local Model Server", lifespan=lifespan)


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "device": _device,
        "embedding_loaded": _embedding_model is not None,
        "rerank_loaded": _rerank_model is not None,
    }


@app.post("/v1/embeddings", response_model=EmbeddingResponse)
async def create_embeddings(request: EmbeddingRequest):
    model = get_embedding_model()
    texts = request.input if isinstance(request.input, list) else [request.input]

    embeddings = model.encode(texts, normalize_embeddings=True)

    data = [EmbeddingData(embedding=emb.tolist(), index=i) for i, emb in enumerate(embeddings)]

    return EmbeddingResponse(
        data=data,
        model=request.model,
        usage=EmbeddingUsage(
            prompt_tokens=sum(len(t.split()) for t in texts),
            total_tokens=sum(len(t.split()) for t in texts),
        ),
    )


@app.post("/v1/rerank", response_model=RerankResponse)
async def create_rerank(request: RerankRequest):
    model = get_rerank_model()
    query = request.input.query
    documents = request.input.documents
    top_n = request.parameters.top_n

    pairs = [[query, doc] for doc in documents]
    scores = model.predict(pairs, convert_to_numpy=True)

    scored_indices = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)[:top_n]

    results = []
    for idx, score in scored_indices:
        r = RerankResult(index=idx, relevance_score=float(score))
        if request.parameters.return_documents:
            r.document = documents[idx]
        results.append(r)

    return RerankResponse(output=RerankOutput(results=results))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--embedding-path", default="D:/models/bge-m3")
    parser.add_argument("--rerank-path", default="D:/models/bge-reranker-base")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--device", default=None)
    args = parser.parse_args()

    uvicorn.run(app, host=args.host, port=args.port, log_level="info")
