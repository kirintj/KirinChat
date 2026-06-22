# 异步编程知识点

## asyncio 基础
- 事件循环（Event Loop）是核心调度器
- 协程（Coroutine）用 async/await 定义
- Task 是对协程的封装，可并发执行
- Future 是底层结果容器

## 并发模型对比
- 多线程 threading：适合 I/O 密集，受 GIL 限制
- 多进程 multiprocessing：适合 CPU 密集，开销大
- 协程 asyncio：单线程高并发，适合大量 I/O
- 异步库：aiohttp/aiomysql/aioredis

## 常见陷阱
- 在 async 函数中调用阻塞函数（用 run_in_executor）
- 忘记 await（返回协程对象而非结果）
- 未正确处理异常（gather 的 return_exceptions）
- 事件循环嵌套（nest_asyncio 或重构）

## 实践模式
- 信号量控制并发数 asyncio.Semaphore
- 超时控制 asyncio.wait_for
- 后台任务 asyncio.create_task
- 异步上下文管理器 async with
- 异步迭代器 async for
