# FastAPI 核心知识点

## 核心特性
- 基于 Starlette（ASGI）和 Pydantic
- 自动生成 OpenAPI 文档（Swagger/ReDoc）
- 类型提示驱动参数验证
- 依赖注入系统

## 路由与参数
- 路径参数、查询参数、请求体
- Pydantic 模型验证（Field/validator）
- 嵌套模型、可选参数
- Header/Cookie 参数

## 依赖注入
- Depends() 函数
- 多层依赖嵌套
- yield 依赖（资源管理）
- 全局依赖 app.dependency

## 中间件
- CORSMiddleware
- 自定义中间件（BaseHTTPMiddleware）
- 中间件执行顺序

## 异步支持
- async def 路由（异步 I/O）
- sync def 路由（自动线程池）
- 后台任务 BackgroundTasks
- WebSocket 支持

## 安全认证
- OAuth2 + JWT
- SecurityDepends
- API Key 认证
