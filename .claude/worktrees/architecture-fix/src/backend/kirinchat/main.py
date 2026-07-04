import logging
import warnings
import redis.asyncio as aioredis
from contextlib import asynccontextmanager
from fastapi import FastAPI
from loguru import logger
from kirinchat.auth import AuthJWT
from kirinchat.auth.exceptions import AuthJWTException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from kirinchat.api.JWT import Settings as AuthJwtSettings
from kirinchat.mcp_proxy.session.manager import SessionManager
from kirinchat.middleware.rate_limiter import get_limiter, limiter
from kirinchat.middleware.trace_id_middleware import TraceIDMiddleware
from kirinchat.middleware.white_list_middleware import WhitelistMiddleware
from kirinchat.settings import init_app_settings
from kirinchat.settings import app_settings

warnings.filterwarnings("ignore")
logging.getLogger("chromadb").setLevel(logging.WARNING)


async def register_router(app: FastAPI):
    from kirinchat.api.router import router

    app.include_router(router)

    # 健康探针
    @app.get("/health")
    def check_health():
        return {'status': 'OK'}


def register_middleware(app: FastAPI):
    cors_config = app_settings.cors

    if cors_config.enabled:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=cors_config.allowed_origins,
            allow_credentials=cors_config.allow_credentials,
            allow_methods=cors_config.allowed_methods,
            allow_headers=cors_config.allowed_headers,
            max_age=cors_config.max_age,
        )

    # Trace ID 的中间件操作
    app.add_middleware(TraceIDMiddleware)

    # 注册白名单中间件
    app.add_middleware(WhitelistMiddleware)

    return app


async def init_config():
    await init_app_settings()

    # 确保配置加载完成后再初始化系统
    logger.info(f"配置加载完成，storage: {app_settings.storage}")

    from kirinchat.database.init_data import init_kirinchat_system
    await init_kirinchat_system()

def print_logo():
    from pyfiglet import Figlet

    f = Figlet(font="slant")
    print(f.renderText("Agent Chat"))

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_config()

    # 更新应用配置
    app.title = app_settings.server.name
    app.version = app_settings.server.version

    redis_client = aioredis.from_url(
        app_settings.redis.get("endpoint"),
        decode_responses=True
    )
    app.state.session_manager = SessionManager(redis_client)

    await register_router(app)
    print_logo()

    yield

    await redis_client.close()


def create_app():
    app = FastAPI(
        title="KirinChat",
        version="2.5.0",
        lifespan=lifespan
    )

    # 注册中间件（使用默认配置，lifespan 中会更新配置）
    app = register_middleware(app)

    # 配置限流
    limiter = get_limiter()
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # 配置 AuthJWT
    @AuthJWT.load_config
    def get_config():
        return AuthJwtSettings()

    # 处理 AuthJWT 异常
    @app.exception_handler(AuthJWTException)
    def authjwt_exception_handler(request, exc):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message}
        )

    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("kirinchat.main:app", host="0.0.0.0", port=7860)
