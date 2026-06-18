# 统一启动脚本设计

## 概述

将项目中 12 个分散的启动脚本合并为 2 个统一入口脚本：`agentchat.sh`（Bash）和 `agentchat.bat`（Windows Batch），通过子命令提供所有功能。

## 删除的文件

| 文件 | 原功能 |
|------|--------|
| `start-all.sh` / `start-all.bat` | 全部启动（Docker + 后端 + 前端） |
| `start-dev.sh` / `start-dev.bat` | Docker + 后端启动 |
| `start-frontend.sh` / `start-frontend.bat` | 前端启动 |
| `stop-dev.sh` / `stop-dev.bat` | 停止服务 |
| `docker/start_linux.sh` | Docker 全量构建启动 |
| `docker/start_win.bat` | Docker 全量构建启动 |

## 保留的文件

| 文件 | 原因 |
|------|------|
| `scripts/model-server/start-model-server.sh` | 独立工具，启动参数与主服务无关 |
| `scripts/model-server/start-model-server.bat` | 同上 |
| `docker/docker-compose.yml` | Docker 编排配置，不是启动脚本 |
| `docker/docker-compose-dev.yml` | 开发环境 Docker 编排配置 |

## 新文件

- `agentchat.sh` — Bash 版本（Linux/macOS/Git Bash）
- `agentchat.bat` — Batch 版本（Windows 原生）

## 子命令设计

### `up [options]`

启动服务。

| 选项 | 功能 |
|------|------|
| （无） | 启动全部：Docker + 后端 + 前端 |
| `--backend-only` | 只启动 Docker + 后端 |
| `--frontend-only` | 只启动前端 |
| `--build` | 强制重新构建 Docker 镜像 |

### `down`

停止所有服务（Docker + 后端 + 前端进程）。

### `status`

查看 Docker 容器运行状态。

### `logs [service]`

查看服务日志。可选指定服务名（backend/frontend/mysql/redis/minio）。

### `clean`

清除 Docker 数据卷（危险操作，二次确认）。等效于 `docker-compose -f docker-compose-dev.yml down -v`。

### `build`

重新构建 Docker 镜像（不启动）。

### `help`

显示帮助信息，列出所有子命令及用法。

## 行为规范

### 首次运行检测

- **Python 依赖**：若 `src/backend/.venv` 不存在，自动运行 `pip install uv && uv sync`
- **配置文件**：若 `src/backend/agentchat/config.yaml` 不存在，从 `config-dev.yaml` 复制
- **Node 依赖**：若 `src/frontend/node_modules` 不存在，自动运行 `npm install`

### 服务启动顺序

```
1. Docker 基础服务（MySQL, Redis, MinIO）
2. 等待容器健康（healthcheck 通过，最多 60 秒）
3. 后端服务（uvicorn, 端口 7860）
4. 前端服务（npm run dev, 端口 8090）
```

### 信号处理

- `Ctrl+C`：同时停止后端和前端子进程，然后退出
- 使用 `trap` 捕获 SIGINT/SIGTERM

### 平台差异

| 功能 | Bash (.sh) | Batch (.bat) |
|------|-----------|-------------|
| 子命令解析 | `case` 语句 | `if`/`goto` |
| 后台进程 | `&` + `$!` | `start "title" cmd /k` |
| 进程清理 | `trap` + `kill` | `taskkill` |
| 健康检查循环 | `curl` + `sleep` 循环 | `curl` + `timeout` 循环 |

## 退出码

| 码 | 含义 |
|----|------|
| 0 | 成功 |
| 1 | 一般错误 |
| 2 | 用法错误（未知子命令） |
| 3 | 依赖检查失败（Docker 未运行等） |
