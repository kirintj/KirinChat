# KirinChat 品牌重塑设计文档

**日期:** 2026-06-18
**目标:** 将 fork 的 AgentChat 项目全面重塑为 KirinChat / 麒麟智聊

## 背景

项目为 fork 自 Shy2593666979/AgentChat 的全栈 AI 对话系统（Vue 3 + FastAPI），需要：
- 替换所有品牌标识为自有品牌
- 清除原作者个人信息和 API 密钥
- 统一技术层命名

## 命名映射表

| 原值 | 新值 | 说明 |
|------|------|------|
| `AgentChat` | `KirinChat` | 英文品牌名（显示用） |
| `agentchat` | `kirinchat` | 包名/模块名/技术标识 |
| `智言平台` | `麒麟智聊平台` | 中文全称 |
| `智言` | `麒麟智聊` | 中文简称 |
| `智言小助手` | `麒麟智聊助手` | 助手角色名 |
| `智言灵寻LingSeek` | `麒麟灵寻LingSeek` | 子功能名 |
| `MingGuang Tian` | `kirin` | LICENSE 作者 |
| `tianmingguang` | `kirin` | pyproject 作者 |
| `2593666979@qq.com` | `2896651097@qq.com` | 作者邮箱 |
| `Shy2593666979` | `kirintj` | GitHub 用户名 |
| `agentchat-network` | `kirinchat-network` | Docker 网络 |
| `agentchat-mysql` | `kirinchat-mysql` | Docker 容器 |
| `agentchat-redis` | `kirinchat-redis` | Docker 容器 |
| `agentchat-backend` | `kirinchat-backend` | Docker 容器 |
| `agentchat-frontend` | `kirinchat-frontend` | Docker 容器 |
| `agentchat-minio` | `kirinchat-minio` | Docker 容器 |
| `agentchat_user` | `kirinchat_user` | MySQL 用户 |
| `agentchat-theme` | `kirinchat-theme` | localStorage key |
| `LiangTian` | (清除) | 原作者 Langfuse user_id |
| `小田` | `小麒` | 微信机器人角色名 |

## 实施方案：分两阶段

### 阶段 1：品牌、安全与链接（约 35 个文件）

不涉及 Python 包目录重命名，只做文本替换。完成后项目即可正常运行且无安全隐患。

#### 1a. 安全清理（最高优先级）

清除所有残留的原作者 API 密钥和云服务凭证：

| 文件 | 操作 |
|------|------|
| `src/backend/agentchat/config.yaml` | 所有 API key → `YOUR_XXX_API_KEY` 占位符 |
| `src/backend/agentchat/config-dev.yaml` | 同上 |
| `docker/docker_config.yaml` | 同上 |
| 以上三个文件 | 清除 Langfuse user_id、token 等个人信息 |

#### 1b. 作者与版权

| 文件 | 操作 |
|------|------|
| `LICENSE` | Copyright (c) 2024 MingGuang Tian → Copyright (c) 2024 kirin |
| `src/backend/pyproject.toml` | authors name + email 替换 |
| `src/backend/agentchat/mcp_servers/lark_mcp/pyproject.toml` | 同上 |

#### 1c. 品牌名替换

全局文本搜索替换（需注意上下文避免误替换）：

- `AgentChat` → `KirinChat`（约 30+ 处）
- `智言平台` → `麒麟智聊平台`（约 4 处）
- `智言` → `麒麟智聊`（约 8 处，注意不要重复替换已处理的"智言平台"）
- `小田` → `小麒`（微信机器人，约 3 处）

涉及文件：
- README.md, README_EN.md
- DEV_GUIDE.md, QUICKSTART.md, DOCS_INDEX.md
- 前端 .vue 文件（index.vue, login.vue, register.vue, workspace.vue, defaultPage.vue, workspacePage.vue）
- 后端 config 文件（config.yaml, config-dev.yaml, common.py）
- 脚本文件（start-all.sh/bat, start-dev.sh/bat, stop-dev.sh/bat, start-frontend.sh/bat, agentchat.sh）
- Docker 文件（docker-compose.yml, docker-compose-dev.yml, README.md, nginx_example.conf, start_linux.sh, start_win.bat, docker_config.yaml）
- 文档文件（docs/ 下各 .md 文件, scripts/README.md, scripts/start.py）

#### 1d. 外部链接更新

| 原链接 | 新链接 |
|--------|--------|
| `https://github.com/Shy2593666979/AgentChat` | `https://github.com/kirintj/KirinChat` |
| `https://github.com/Shy2593666979/AgentChat.git` | `https://github.com/kirintj/KirinChat.git` |
| `https://shy2593666979.github.io/agentchat-docs/...` | `YOUR_DOCS_URL` |
| `https://agentchat.cloud` | `YOUR_DEMO_URL` |
| 微信群链接 | 移除 |
| Star-history badge | 替换为 kirintj/KirinChat 或移除 |

#### 1e. 前端显示更新

| 文件 | 操作 |
|------|------|
| `src/frontend/package.json` | `"name": "kirinchat-frontend"` |
| `src/frontend/src/pages/login/login.vue` | logo 文字、版本信息、GitHub 链接 |
| `src/frontend/src/pages/login/register.vue` | 同上 |
| `src/frontend/src/pages/index.vue` | 品牌名 |
| `src/frontend/src/pages/workspace/workspace.vue` | logo alt text |
| `src/frontend/src/pages/workspace/defaultPage/defaultPage.vue` | 助手名称 |
| `src/frontend/src/pages/workspace/workspacePage/workspacePage.vue` | 指导手册文字 |

#### 1f. 提交

阶段 1 完成后单独提交：`rebrand(kirinchat): phase 1 - branding, security, and links`

---

### 阶段 2：技术层重命名（约 25 个文件 + 所有 .py 文件）

高风险操作：Python 包目录重命名 + 全部 import 语句更新。

#### 2a. Python 包目录重命名

```
src/backend/agentchat/ → src/backend/kirinchat/
```

#### 2b. Python import 语句更新

全局替换所有 .py 文件中的：
- `from agentchat.` → `from kirinchat.`
- `import agentchat.` → `import kirinchat.`

预估 50+ 处 import 需要更新。

#### 2c. 项目配置更新

| 文件 | 操作 |
|------|------|
| `src/backend/pyproject.toml` | `name = "kirinchat"`，更新包路径配置 |
| `src/backend/uv.lock` | 包名 `agentchat` → `kirinchat` |
| `docker/Dockerfile` | `uvicorn agentchat.main:app` → `uvicorn kirinchat.main:app` |

#### 2d. Docker 配置更新

| 文件 | 操作 |
|------|------|
| `docker/docker-compose.yml` | 容器名、网络名、数据库名、用户名、服务 URL |
| `docker/docker-compose-dev.yml` | 同上 |
| 确保容器间通信 | `VITE_API_BASE_URL: http://kirinchat-backend:7860` |

#### 2e. 脚本更新

| 文件 | 操作 |
|------|------|
| `agentchat.sh` → `kirinchat.sh` | 重命名并更新内部引用 |
| 所有 .sh / .bat 脚本 | 更新容器名引用 |

#### 2f. 验证清单

- [ ] 后端启动无 import 错误
- [ ] 前端 `npm run build` 成功
- [ ] Docker Compose 容器名正确
- [ ] 前端页面显示新品牌名
- [ ] 登录/注册页显示新品牌名
- [ ] 无残留的 "AgentChat" 或 "智言" 字样（grep 验证）

#### 2g. 提交

阶段 2 完成后单独提交：`rebrand(kirinchat): phase 2 - technical renaming`

---

## 风险与注意事项

1. **Python 包重命名**是最高风险操作 — 如果遗漏 import，运行时会报 `ModuleNotFoundError`。需要通过 grep 双重验证。
2. **中文替换**需要注意上下文 — "智言" 可能出现在复合词中，需要逐个确认而非盲目全局替换。
3. **API key 占位符**替换后需要手动填写才能使用，否则 AI 功能无法工作。
4. **uv.lock** 重命名后需要运行 `uv lock` 重新生成锁文件。
5. **Git 历史**中仍保留原作者信息 — 这是正常的 fork 行为，不需要清理。
