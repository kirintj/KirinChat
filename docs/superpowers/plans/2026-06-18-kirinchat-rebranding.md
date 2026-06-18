# KirinChat 品牌重塑实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 fork 的 AgentChat 项目全面重塑为 KirinChat / 麒麟智聊，清除原作者所有个人信息和 API 密钥

**Architecture:** 分两阶段：Phase 1 做品牌文本替换（安全、显示名、链接），Phase 2 做 Python 包目录重命名（高风险的 import 全量替换）。每阶段独立提交，独立验证。

**Tech Stack:** Python 3.12+, Vue 3, FastAPI, Docker, sed (批量文本替换)

---

## Phase 1: 品牌、安全与链接

### Task 1: 安全清理 — 清除所有 API 密钥

**Files:**
- Modify: `src/backend/agentchat/config.yaml`
- Modify: `src/backend/agentchat/config-dev.yaml`
- Modify: `docker/docker_config.yaml`

- [ ] **Step 1: 清理 config.yaml 中的 API 密钥**

Read `src/backend/agentchat/config.yaml`，将以下字段的值替换为占位符：

```yaml
# Line 23, 28, 33, 38, 43: DashScope/通义千问 API keys
api_key: "YOUR_DASHSCOPE_API_KEY"

# Line 64: 天气 API key
api_key: "YOUR_WEATHER_API_KEY"

# Line 68: Tavily API key
api_key: "YOUR_TAVILY_API_KEY"

# Line 71: Google API key
api_key: "YOUR_GOOGLE_API_KEY"

# Line 74: 快递 API key
api_key: "YOUR_DELIVERY_API_KEY"

# Line 134-135: WeChat app_id 和 secret
app_id: "YOUR_WECHAT_APP_ID"
secret: "YOUR_WECHAT_SECRET"

# Line 141-142: Langfuse keys
public_key: "YOUR_LANGFUSE_PUBLIC_KEY"
secret_key: "YOUR_LANGFUSE_SECRET_KEY"
```

同时清除个人信息：
```yaml
# Line 133: WeChat token
token: "YOUR_WECHAT_TOKEN"

# Line 143: Langfuse user_id
user_id: "kirin"
```

- [ ] **Step 2: 清理 config-dev.yaml 中的个人信息**

Read `src/backend/agentchat/config-dev.yaml`，替换：
```yaml
# Line 110: WeChat token
token: "YOUR_WECHAT_TOKEN"

# Line 120: Langfuse user_id
user_id: "kirin"
```

- [ ] **Step 3: 清理 docker_config.yaml 中的 API 密钥**

Read `docker/docker_config.yaml`，替换所有 API key 为占位符（与 Step 1 相同的模式），以及：
```yaml
# Line 133: WeChat token
token: "YOUR_WECHAT_TOKEN"

# Line 143: Langfuse user_id
user_id: "kirin"
```

- [ ] **Step 4: 验证无残留密钥**

Run: `grep -rn "tp-cvi4\|sk-fc40\|sk-6d47\|fac0ad46\|tvly-dev\|cdc3b207\|df695c94\|wxf76887\|063c4df1\|pk-lf-\|sk-lf-\|LiangTian" src/backend/agentchat/config*.yaml docker/docker_config.yaml`
Expected: 无匹配结果

- [ ] **Step 5: 提交**

```bash
git add src/backend/agentchat/config.yaml src/backend/agentchat/config-dev.yaml docker/docker_config.yaml
git commit -m "security: remove leaked API keys and personal info from config files"
```

---

### Task 2: 作者信息与版权

**Files:**
- Modify: `LICENSE:3`
- Modify: `src/backend/pyproject.toml:2,5`
- Modify: `src/backend/agentchat/mcp_servers/lark_mcp/pyproject.toml:6`

- [ ] **Step 1: 更新 LICENSE**

Edit `LICENSE`:
```
# Before:
Copyright (c) 2024 MingGuang Tian

# After:
Copyright (c) 2024 kirin
```

- [ ] **Step 2: 更新 pyproject.toml**

Edit `src/backend/pyproject.toml`:
```toml
# Before (line 2):
name = "agentchat"
# After:
name = "kirinchat"

# Before (line 5):
authors = [{ name = "tianmingguang", email = "2593666979@qq.com" }]
# After:
authors = [{ name = "kirin", email = "2896651097@qq.com" }]
```

- [ ] **Step 3: 更新 lark_mcp pyproject.toml**

Edit `src/backend/agentchat/mcp_servers/lark_mcp/pyproject.toml`:
```toml
# Before (line 6):
{name = "Mingguang.Tian",email = "2593666979@qq.com"}
# After:
{name = "kirin",email = "2896651097@qq.com"}
```

- [ ] **Step 4: 提交**

```bash
git add LICENSE src/backend/pyproject.toml src/backend/agentchat/mcp_servers/lark_mcp/pyproject.toml
git commit -m "rebrand: update author info and copyright to kirin"
```

---

### Task 3: 后端品牌名替换（config + schemas）

**Files:**
- Modify: `src/backend/agentchat/config.yaml:6`
- Modify: `src/backend/agentchat/config-dev.yaml:8`
- Modify: `docker/docker_config.yaml:6`
- Modify: `src/backend/agentchat/schemas/common.py:82`

- [ ] **Step 1: 替换 config 中的品牌名**

三个 config 文件中的 `name: "AgentChat"` → `name: "KirinChat"`

同时替换数据库名（config.yaml line 12-13, config-dev.yaml line 13-14, docker_config.yaml line 12-13）：
- `agentchat` → `kirinchat`（仅在 MySQL 连接字符串的数据库名部分）

替换 OSS bucket 名（保持原作者的 OSS URL 不变 — 这些是原作者托管的图片资源，你暂时仍需使用）：
- `bucket_name: "agentchat"` 保持不变（因为你还没有自己的 OSS bucket）

替换 Langfuse trace_name：
- `trace_name: "agentchat"` → `trace_name: "kirinchat"`

- [ ] **Step 2: 替换 schemas/common.py**

Edit `src/backend/agentchat/schemas/common.py`:
```python
# Before (line 82):
name: str = "AgentChat"
# After:
name: str = "KirinChat"
```

- [ ] **Step 3: 验证**

Run: `grep -rn '"AgentChat"' src/backend/agentchat/config*.yaml docker/docker_config.yaml src/backend/agentchat/schemas/common.py`
Expected: 无匹配

- [ ] **Step 4: 提交**

```bash
git add src/backend/agentchat/config.yaml src/backend/agentchat/config-dev.yaml docker/docker_config.yaml src/backend/agentchat/schemas/common.py
git commit -m "rebrand: update backend config brand name to KirinChat"
```

---

### Task 4: 前端品牌名替换（Vue 组件 + HTML）

**Files:**
- Modify: `src/frontend/index.html:7`
- Modify: `src/frontend/package.json:2`
- Modify: `src/frontend/src/pages/login/login.vue:107,158,160`
- Modify: `src/frontend/src/pages/login/register.vue:110,185,187`
- Modify: `src/frontend/src/pages/index.vue:27,199`
- Modify: `src/frontend/src/pages/workspace/workspace.vue:272`
- Modify: `src/frontend/src/pages/workspace/defaultPage/defaultPage.vue:396,398,400,449`
- Modify: `src/frontend/src/pages/workspace/workspacePage/workspacePage.vue:484`

- [ ] **Step 1: 替换 index.html 标题**

```html
<!-- Before (line 7): -->
<title>智言平台</title>
<!-- After: -->
<title>麒麟智聊平台</title>
```

- [ ] **Step 2: 替换 package.json**

```json
// Before (line 2):
"name": "agentchat-frontend"
// After:
"name": "kirinchat-frontend"
```

- [ ] **Step 3: 替换 login.vue**

```html
<!-- Line 107: -->
<!-- Before: -->  <span class="logo-text">AgentChat</span>
<!-- After: -->   <span class="logo-text">KirinChat</span>

<!-- Line 158: -->
<!-- Before: -->  <div class="version-badge" title="AgentChat 版本">v2.5.0</div>
<!-- After: -->   <div class="version-badge" title="KirinChat 版本">v2.5.0</div>

<!-- Line 160: -->
<!-- Before: -->  <a href="https://github.com/Shy2593666979/AgentChat" target="_blank"
<!-- After: -->   <a href="https://github.com/kirintj/KirinChat" target="_blank"
```

- [ ] **Step 4: 替换 register.vue**

```html
<!-- Line 110: -->
<!-- Before: -->  <span class="logo-text">AgentChat</span>
<!-- After: -->   <span class="logo-text">KirinChat</span>

<!-- Line 185: -->
<!-- Before: -->  <div class="version-badge" title="AgentChat 版本">v2.5.0</div>
<!-- After: -->   <div class="version-badge" title="KirinChat 版本">v2.5.0</div>

<!-- Line 187: -->
<!-- Before: -->  <a href="https://github.com/Shy2593666979/AgentChat" target="_blank"
<!-- After: -->   <a href="https://github.com/kirintj/KirinChat" target="_blank"
```

- [ ] **Step 5: 替换 index.vue**

```javascript
// Line 27:
// Before: const itemName = ref("智言平台")
// After:  const itemName = ref("麒麟智聊平台")

// Line 199:
// Before: <div class="brand-name" @click="godefault">AgentChat</div>
// After:  <div class="brand-name" @click="godefault">KirinChat</div>
```

- [ ] **Step 6: 替换 workspace.vue**

```html
<!-- Line 272: -->
<!-- Before: -->  <img src="../../assets/agentchat.svg" alt="智言平台" class="brand-logo-img" />
<!-- After: -->   <img src="../../assets/agentchat.svg" alt="麒麟智聊平台" class="brand-logo-img" />
```

> 注意：`agentchat.svg` 文件名暂不改（Phase 2 统一处理），只改 alt text。

- [ ] **Step 7: 替换 defaultPage.vue**

```html
<!-- Line 396: -->
<!-- Before: -->  <img src="../../../assets/robot.svg" alt="智言" class="avatar" />
<!-- After: -->   <img src="../../../assets/robot.svg" alt="麒麟智聊" class="avatar" />

<!-- Line 398: -->
<!-- Before: -->  <h1 class="welcome-title">我是智言小助手，很高兴见到你！</h1>
<!-- After: -->   <h1 class="welcome-title">我是麒麟智聊助手，很高兴见到你！</h1>

<!-- Line 400-401: -->
<!-- Before: -->  欢迎体验智言灵寻LingSeek，一位懂得完成复杂任务的Agent助理~
<!-- After: -->   欢迎体验麒麟灵寻LingSeek，一位懂得完成复杂任务的Agent助理~

<!-- Line 449: -->
<!-- Before: -->  placeholder="给智言发消息，让智言帮你完成任务~"
<!-- After: -->   placeholder="给麒麟智聊发消息，让麒麟智聊帮你完成任务~"
```

- [ ] **Step 8: 替换 workspacePage.vue**

```html
<!-- Line 484: -->
<!-- Before: -->  <span class="editor-title">智言指导手册</span>
<!-- After: -->   <span class="editor-title">麒麟智聊指导手册</span>
```

- [ ] **Step 9: 验证**

Run: `grep -rn "AgentChat\|智言" src/frontend/src/ src/frontend/index.html src/frontend/package.json`
Expected: 仅 `agentchat.svg` 文件引用（这是文件名，Phase 2 处理）

- [ ] **Step 10: 提交**

```bash
git add src/frontend/
git commit -m "rebrand: update frontend brand name to KirinChat / 麒麟智聊"
```

---

### Task 5: 微信机器人角色名替换

**Files:**
- Modify: `src/backend/agentchat/api/v1/wechat.py:17-18,84,158`

- [ ] **Step 1: 替换 wechat.py 中的角色名**

Read `src/backend/agentchat/api/v1/wechat.py`，将 `"小田"` 替换为 `"小麒"`（约 3 处）。

- [ ] **Step 2: 替换 agentchat.cloud 链接**

Edit `src/backend/agentchat/api/services/wechat.py:91`:
```python
# Before:
f"您的微信账号为：{from_user}, 可在www.agentchat.cloud网站中使用微信账号注册查看您的聊天记录"
# After:
f"您的微信账号为：{from_user}, 可在网站中使用微信账号注册查看您的聊天记录"
```

- [ ] **Step 3: 提交**

```bash
git add src/backend/agentchat/api/v1/wechat.py src/backend/agentchat/api/services/wechat.py
git commit -m "rebrand: update wechat bot persona name and remove external domain"
```

---

### Task 6: 脚本文件品牌名替换

**Files:**
- Modify: `agentchat.sh` (lines 2, 118, 121, 136-139, 211, 236, 307)
- Modify: `start-all.sh` (lines 6-11, 120, 134)
- Modify: `start-all.bat` (lines 5, 79, 103, 114, 128)
- Modify: `start-dev.sh` (lines 3, 8)
- Modify: `start-dev.bat` (lines 5)
- Modify: `stop-dev.sh` (lines 3, 7)
- Modify: `stop-dev.bat` (line 5)
- Modify: `start-frontend.sh` (lines 3, 7)
- Modify: `start-frontend.bat` (line 5)

> 注意：脚本中的 `uvicorn agentchat.main:app` 和配置文件路径 `agentchat/config.yaml` 在 Phase 2 包重命名时一并处理，Phase 1 只处理品牌显示文字。

- [ ] **Step 1: 批量替换脚本中的显示名**

使用 sed 批量替换（仅替换显示文字，不替换模块路径）：

```bash
# agentchat.sh — 显示名
sed -i 's/AgentChat 统一启动脚本/KirinChat 统一启动脚本/g' agentchat.sh
sed -i 's/AgentChat 已启动/KirinChat 已启动/g' agentchat.sh

# start-all.sh — ASCII art banner 和显示名
# 需要手动将 ASCII art 中的 "AGENTCHAT" 改为 "KIRINCHAT"（lines 6-11）
sed -i 's/AgentChat 本地开发环境启动完成/KirinChat 本地开发环境启动完成/g' start-all.sh

# start-all.bat
sed -i 's/AgentChat Local Development Environment/KirinChat Local Development Environment/g' start-all.bat
sed -i 's/AgentChat Backend/KirinChat Backend/g' start-all.bat
sed -i 's/AgentChat Frontend/KirinChat Frontend/g' start-all.bat
sed -i 's/AgentChat local environment/KirinChat local environment/g' start-all.bat

# start-dev.sh
sed -i 's/AgentChat 本地开发启动脚本/KirinChat 本地开发启动脚本/g' start-dev.sh
sed -i 's/AgentChat 本地开发环境启动/KirinChat 本地开发环境启动/g' start-dev.sh

# start-dev.bat
sed -i 's/AgentChat Local Development Startup/KirinChat Local Development Startup/g' start-dev.bat

# stop-dev.sh
sed -i 's/AgentChat 本地开发环境停止脚本/KirinChat 本地开发环境停止脚本/g' stop-dev.sh
sed -i 's/停止 AgentChat/停止 KirinChat/g' stop-dev.sh

# stop-dev.bat
sed -i 's/AgentChat Local Environment Stop/KirinChat Local Environment Stop/g' stop-dev.bat

# start-frontend.sh
sed -i 's/AgentChat 前端开发启动脚本/KirinChat 前端开发启动脚本/g' start-frontend.sh
sed -i 's/启动 AgentChat 前端/启动 KirinChat 前端/g' start-frontend.sh

# start-frontend.bat
sed -i 's/AgentChat Frontend Development Server/KirinChat Frontend Development Server/g' start-frontend.bat
```

- [ ] **Step 2: 提交**

```bash
git add agentchat.sh start-all.sh start-all.bat start-dev.sh start-dev.bat stop-dev.sh stop-dev.bat start-frontend.sh start-frontend.bat
git commit -m "rebrand: update shell scripts display name to KirinChat"
```

---

### Task 7: Docker 文件品牌名替换

**Files:**
- Modify: `docker/docker-compose.yml`
- Modify: `docker/docker-compose-dev.yml`
- Modify: `docker/README.md`
- Modify: `docker/nginx_example.conf`
- Modify: `docker/start_linux.sh`
- Modify: `docker/start_win.bat`

> 注意：Dockerfile 中的模块路径 (`agentchat.main:app`) 和 COPY 路径在 Phase 2 处理。

- [ ] **Step 1: 替换 docker-compose.yml**

```bash
sed -i 's/agentchat-network/kirinchat-network/g' docker/docker-compose.yml
sed -i 's/agentchat-mysql/kirinchat-mysql/g' docker/docker-compose.yml
sed -i 's/agentchat-redis/kirinchat-redis/g' docker/docker-compose.yml
sed -i 's/agentchat-backend/kirinchat-backend/g' docker/docker-compose.yml
sed -i 's/agentchat-frontend/kirinchat-frontend/g' docker/docker-compose.yml
sed -i 's/agentchat-minio/kirinchat-minio/g' docker/docker-compose.yml
sed -i 's/agentchat_user/kirinchat_user/g' docker/docker-compose.yml
sed -i 's/MYSQL_DATABASE: agentchat/MYSQL_DATABASE: kirinchat/g' docker/docker-compose.yml
```

- [ ] **Step 2: 替换 docker-compose-dev.yml**

```bash
sed -i 's/AgentChat-network/KirinChat-network/g' docker/docker-compose-dev.yml
sed -i 's/AgentChat-mysql/KirinChat-mysql/g' docker/docker-compose-dev.yml
sed -i 's/AgentChat-redis/KirinChat-redis/g' docker/docker-compose-dev.yml
sed -i 's/AgentChat-minio/KirinChat-minio/g' docker/docker-compose-dev.yml
sed -i 's/agentchat_user/kirinchat_user/g' docker/docker-compose-dev.yml
sed -i 's/MYSQL_DATABASE: agentchat/MYSQL_DATABASE: kirinchat/g' docker/docker-compose-dev.yml
```

- [ ] **Step 3: 替换 Docker 辅助脚本和文档**

```bash
# start_linux.sh
sed -i 's/AgentChat Docker 启动脚本/KirinChat Docker 启动脚本/g' docker/start_linux.sh
sed -i 's/启动 AgentChat Docker/启动 KirinChat Docker/g' docker/start_linux.sh
sed -i 's/AgentChat 启动完成/KirinChat 启动完成/g' docker/start_linux.sh

# start_win.bat
sed -i 's/Starting AgentChat/Starting KirinChat/g' docker/start_win.bat
sed -i 's/AgentChat started/KirinChat started/g' docker/start_win.bat

# nginx_example.conf
sed -i 's/AgentChat 前端 Nginx/KirinChat 前端 Nginx/g' docker/nginx_example.conf

# docker/README.md
sed -i 's/AgentChat Docker 部署指南/KirinChat Docker 部署指南/g' docker/README.md
sed -i 's/一键部署 AgentChat/一键部署 KirinChat/g' docker/README.md
sed -i 's/部署 AgentChat/部署 KirinChat/g' docker/README.md
sed -i 's/agentchat-backend/kirinchat-backend/g' docker/README.md
sed -i 's/agentchat-frontend/kirinchat-frontend/g' docker/README.md
# 数据库连接字符串中的数据库名
sed -i 's|/agentchat|/kirinchat|g' docker/README.md
```

- [ ] **Step 4: 验证 Docker 文件**

Run: `grep -rn "agentchat\|AgentChat" docker/ | grep -v "agentchat.oss\|agentchat\.cloud"`
Expected: 仅 Dockerfile 中的模块路径残留（Phase 2 处理）

- [ ] **Step 5: 提交**

```bash
git add docker/
git commit -m "rebrand: update Docker configs to KirinChat"
```

---

### Task 8: README 和文档品牌名替换

**Files:**
- Modify: `README.md`
- Modify: `README_EN.md`
- Modify: `DEV_GUIDE.md`
- Modify: `QUICKSTART.md`
- Modify: `DOCS_INDEX.md`
- Modify: `scripts/README.md`
- Modify: `scripts/start.py`
- Modify: `src/backend/README.md`

- [ ] **Step 1: 替换 README.md**

```bash
# 品牌名
sed -i 's/AgentChat/KirinChat/g' README.md
sed -i 's/agentchat-frontend/kirinchat-frontend/g' README.md
sed -i 's/agentchat-backend/kirinchat-backend/g' README.md

# GitHub 链接
sed -i 's|github.com/Shy2593666979/AgentChat|github.com/kirintj/KirinChat|g' README.md
sed -i 's|github.com/Shy2593666979/agentchat-docs|github.com/kirintj/kirinchat-docs|g' README.md

# 文档站链接
sed -i 's|shy2593666979.github.io/agentchat-docs|kirintj.github.io/kirinchat-docs|g' README.md

# 体验站
sed -i 's|agentchat\.cloud|YOUR_DEMO_URL|g' README.md

# 作者信息
sed -i 's/the KirinChat Author MingGuang Tian/the KirinChat Author kirin/g' README.md

# 目录名
sed -i 's/cd KirinChat/cd KirinChat/g' README.md

# Star history badge
sed -i 's|Shy2593666979/KirinChat|kirintj/KirinChat|g' README.md
```

- [ ] **Step 2: 替换 README_EN.md**

```bash
sed -i 's/AgentChat/KirinChat/g' README_EN.md
sed -i 's/agentchat-frontend/kirinchat-frontend/g' README_EN.md
sed -i 's/agentchat-backend/kirinchat-backend/g' README_EN.md
sed -i 's|github.com/Shy2593666979/AgentChat|github.com/kirintj/KirinChat|g' README_EN.md
sed -i 's|github.com/Shy2593666979/agentchat-docs|github.com/kirintj/kirinchat-docs|g' README_EN.md
sed -i 's|shy2593666979.github.io/agentchat-docs|kirintj.github.io/kirinchat-docs|g' README_EN.md
sed -i 's|agentchat\.cloud|YOUR_DEMO_URL|g' README_EN.md
sed -i 's/the KirinChat Author MingGuang Tian/the KirinChat Author kirin/g' README_EN.md
sed -i 's|Shy2593666979/KirinChat|kirintj/KirinChat|g' README_EN.md
```

- [ ] **Step 3: 替换其他文档**

```bash
# DEV_GUIDE.md
sed -i 's/AgentChat 本地开发环境指南/KirinChat 本地开发环境指南/g' DEV_GUIDE.md
sed -i 's|src/backend/agentchat/config\.yaml|src/backend/agentchat/config.yaml|g' DEV_GUIDE.md
sed -i 's/uvicorn agentchat\.main:app/uvicorn agentchat.main:app/g' DEV_GUIDE.md
sed -i 's|mysql.*agentchat|mysql ... kirinchat|g' DEV_GUIDE.md
sed -i 's/AgentChat\//KirinChat\//g' DEV_GUIDE.md
sed -i 's|── agentchat/|── agentchat/|g' DEV_GUIDE.md

# QUICKSTART.md
sed -i 's/AgentChat 本地开发/KirinChat 本地开发/g' QUICKSTART.md
sed -i 's/AgentChat\//KirinChat\//g' QUICKSTART.md

# DOCS_INDEX.md
sed -i 's/AgentChat 文档索引/KirinChat 文档索引/g' DOCS_INDEX.md
sed -i 's|src/backend/agentchat/|src/backend/agentchat/|g' DOCS_INDEX.md

# scripts/README.md
sed -i 's/AgentChat 快速启动指南/KirinChat 快速启动指南/g' scripts/README.md
sed -i 's/启动 AgentChat/启动 KirinChat/g' scripts/README.md
sed -i 's/AgentChat\//KirinChat\//g' scripts/README.md

# src/backend/README.md
sed -i 's/AgentChat 后端技术文档/KirinChat 后端技术文档/g' src/backend/README.md
sed -i 's/AgentChat 后端/KirinChat 后端/g' src/backend/README.md
sed -i 's/name: "AgentChat"/name: "KirinChat"/g' src/backend/README.md
sed -i 's|/agentchat"|/kirinchat"|g' src/backend/README.md
sed -i 's/bucket_name: "agentchat"/bucket_name: "kirinchat"/g' src/backend/README.md
sed -i 's/uvicorn agentchat\.main:app/uvicorn agentchat.main:app/g' src/backend/README.md
```

> 注意：Phase 1 文档中的 `agentchat/main.py` 等路径暂不改（Phase 2 改目录后再回来更新）

- [ ] **Step 4: 验证**

Run: `grep -rn "Shy2593666979\|MingGuang\|2593666979@qq" README.md README_EN.md LICENSE src/backend/pyproject.toml`
Expected: 无匹配

- [ ] **Step 5: 提交**

```bash
git add README.md README_EN.md DEV_GUIDE.md QUICKSTART.md DOCS_INDEX.md scripts/README.md src/backend/README.md
git commit -m "rebrand: update documentation brand name to KirinChat"
```

---

### Task 9: Phase 1 最终验证

- [ ] **Step 1: 全局残留检查**

```bash
# 检查仍有 "AgentChat" 的文件（排除 .git, .venv, node_modules, docs/superpowers）
grep -rn "AgentChat" --include="*.py" --include="*.vue" --include="*.yaml" --include="*.yml" --include="*.json" --include="*.html" --include="*.sh" --include="*.bat" --include="*.md" --include="*.toml" . \
  | grep -v ".venv/" | grep -v "node_modules/" | grep -v ".git/" | grep -v "docs/superpowers/"
```

预期残留（Phase 2 处理）：
- `uvicorn agentchat.main:app` 模块路径（脚本、Dockerfile）
- Python `from agentchat.xxx` import 语句
- `src/backend/agentchat/` 目录名
- `agentchat.svg` 文件名
- `package-lock.json` 中的包名

- [ ] **Step 2: 检查 API key 残留**

```bash
grep -rn "tp-cvi4\|sk-fc40\|sk-6d47\|fac0ad46\|tvly-dev-RM\|cdc3b207\|df695c94\|wxf76887\|063c4df1\|pk-lf-q3e\|sk-lf-q3e\|LiangTian" . --include="*.yaml" --include="*.yml" | grep -v ".venv/" | grep -v ".git/"
```
Expected: 无匹配

---

## Phase 2: 技术层重命名

### Task 10: Python 包目录重命名

**风险最高操作**

- [ ] **Step 1: 重命名目录**

```bash
cd D:/HuaweiMoveData/Users/28966/Desktop/AgentChat
git mv src/backend/agentchat src/backend/kirinchat
```

- [ ] **Step 2: 验证目录已重命名**

```bash
ls src/backend/kirinchat/main.py
```
Expected: 文件存在

- [ ] **Step 3: 提交（仅目录重命名）**

```bash
git add -A
git commit -m "rebrand: rename Python package directory agentchat -> kirinchat"
```

---

### Task 11: Python import 全量替换

**184 个文件，500+ 处 import**

- [ ] **Step 1: 使用 sed 批量替换所有 .py 文件中的 import**

```bash
cd D:/HuaweiMoveData/Users/28966/Desktop/AgentChat

# 替换 from agentchat.xxx → from kirinchat.xxx
find src/backend/kirinchat -name "*.py" -exec sed -i 's/from agentchat\./from kirinchat./g' {} +

# 替换 import agentchat.xxx → import kirinchat.xxx
find src/backend/kirinchat -name "*.py" -exec sed -i 's/import agentchat\./import kirinchat./g' {} +
```

- [ ] **Step 2: 特殊情况 — 字符串中的 agentchat 路径**

`src/backend/kirinchat/api/services/wechat.py:50` 有一个文件路径字符串：
```python
# Before:
"media": open(image_path or "agentchat/config/default.jpg", "rb")
# After:
"media": open(image_path or "kirinchat/config/default.jpg", "rb")
```

`src/backend/kirinchat/settings.py` 可能有配置路径引用：
```bash
grep -n "agentchat" src/backend/kirinchat/settings.py
```
如有残留，手动替换。

- [ ] **Step 3: 全面验证无残留 import**

```bash
grep -rn "from agentchat\.\|import agentchat\." src/backend/kirinchat/ --include="*.py"
```
Expected: 无匹配

- [ ] **Step 4: 检查是否有相对 import 以外的 agentchat 引用**

```bash
grep -rn "\"agentchat\|'agentchat" src/backend/kirinchat/ --include="*.py"
```
检查结果中是否有字符串引用需要替换。

- [ ] **Step 5: 提交**

```bash
git add -A
git commit -m "rebrand: update all Python imports agentchat -> kirinchat"
```

---

### Task 12: pyproject.toml 和 uv.lock 更新

**Files:**
- Modify: `src/backend/pyproject.toml`
- Regenerate: `src/backend/uv.lock`

- [ ] **Step 1: 验证 pyproject.toml 已在 Task 2 中更新**

```bash
grep "name" src/backend/pyproject.toml | head -1
```
Expected: `name = "kirinchat"`

- [ ] **Step 2: 检查 pyproject.toml 中是否有包路径配置**

```bash
grep -n "agentchat" src/backend/pyproject.toml
```
如有 `packages = [{include = "agentchat"}]` 之类的配置，改为 `kirinchat`。

- [ ] **Step 3: 重新生成 uv.lock**

```bash
cd src/backend
uv lock
```

- [ ] **Step 4: 提交**

```bash
git add src/backend/pyproject.toml src/backend/uv.lock
git commit -m "rebrand: update package lock file for kirinchat"
```

---

### Task 13: Dockerfile 和 scripts 更新

**Files:**
- Modify: `docker/Dockerfile:71,81`
- Modify: `scripts/start.py:66`
- Rename: `agentchat.sh` → `kirinchat.sh`

- [ ] **Step 1: 更新 Dockerfile**

```dockerfile
# Line 71 - Before:
COPY docker/docker_config.yaml /app/agentchat/config.yaml
# After:
COPY docker/docker_config.yaml /app/kirinchat/config.yaml

# Line 81 - Before:
CMD ["uvicorn", "agentchat.main:app", "--host", "0.0.0.0", "--port", "7860"]
# After:
CMD ["uvicorn", "kirinchat.main:app", "--host", "0.0.0.0", "--port", "7860"]
```

- [ ] **Step 2: 更新 scripts/start.py**

```python
# Line 66 - Before:
["uvicorn", "agentchat.main:app", "--port", "7860"],
# After:
["uvicorn", "kirinchat.main:app", "--port", "7860"],
```

- [ ] **Step 3: 更新所有脚本中的 uvicorn 模块路径**

```bash
sed -i 's/uvicorn agentchat\.main:app/uvicorn kirinchat.main:app/g' agentchat.sh start-all.sh start-all.bat start-dev.sh start-dev.bat

# 更新配置文件路径引用
sed -i 's|src/backend/agentchat/config|src/backend/kirinchat/config|g' agentchat.sh start-all.sh start-all.bat DEV_GUIDE.md DOCS_INDEX.md
sed -i 's|src\\backend\\agentchat\\config|src\\backend\\kirinchat\\config|g' start-all.bat
```

- [ ] **Step 4: 重命名 agentchat.sh → kirinchat.sh**

```bash
git mv agentchat.sh kirinchat.sh
```

更新 `kirinchat.sh` 内部自引用：
```bash
sed -i 's/agentchat\.sh/kirinchat.sh/g' kirinchat.sh
```

- [ ] **Step 5: 提交**

```bash
git add docker/Dockerfile scripts/start.py kirinchat.sh start-all.sh start-all.bat start-dev.sh start-dev.bat DEV_GUIDE.md DOCS_INDEX.md
git commit -m "rebrand: update module paths agentchat -> kirinchat in Dockerfile and scripts"
```

---

### Task 14: 前端资源文件重命名

**Files:**
- Rename: `src/frontend/src/assets/agentchat.svg` → `src/frontend/src/assets/kirinchat.svg`
- Modify: `src/frontend/src/pages/workspace/workspace.vue:272`

- [ ] **Step 1: 重命名 SVG 文件**

```bash
git mv src/frontend/src/assets/agentchat.svg src/frontend/src/assets/kirinchat.svg
```

- [ ] **Step 2: 更新引用**

```bash
sed -i 's/agentchat\.svg/kirinchat.svg/g' src/frontend/src/pages/workspace/workspace.vue
```

- [ ] **Step 3: 提交**

```bash
git add src/frontend/src/assets/ src/frontend/src/pages/workspace/workspace.vue
git commit -m "rebrand: rename agentchat.svg to kirinchat.svg"
```

---

### Task 15: 文档路径更新（Phase 2 部分）

**Files:**
- Modify: `README.md`, `README_EN.md`, `DEV_GUIDE.md`, `QUICKSTART.md`, `DOCS_INDEX.md`, `scripts/README.md`, `src/backend/README.md`

- [ ] **Step 1: 更新文档中的目录路径**

```bash
# 所有文档中 agentchat/ 目录引用 → kirinchat/
sed -i 's|backend/agentchat/|backend/kirinchat/|g' README.md README_EN.md DEV_GUIDE.md QUICKSTART.md DOCS_INDEX.md scripts/README.md src/backend/README.md
sed -i 's|── agentchat/|── kirinchat/|g' DEV_GUIDE.md QUICKSTART.md DOCS_INDEX.md scripts/README.md src/backend/README.md
sed -i 's|backend/agentchat|backend/kirinchat|g' DOCS_INDEX.md
sed -i 's|agentchat/main\.py|kirinchat/main.py|g' scripts/README.md src/backend/README.md
```

- [ ] **Step 2: 提交**

```bash
git add README.md README_EN.md DEV_GUIDE.md QUICKSTART.md DOCS_INDEX.md scripts/README.md src/backend/README.md
git commit -m "rebrand: update directory paths in documentation"
```

---

### Task 16: package-lock.json 更新

**Files:**
- Modify: `src/frontend/package-lock.json`

- [ ] **Step 1: 重新生成 package-lock.json**

```bash
cd src/frontend
npm install
```

这会根据更新后的 `package.json`（`kirinchat-frontend`）自动更新 lock 文件。

- [ ] **Step 2: 提交**

```bash
git add src/frontend/package-lock.json
git commit -m "rebrand: regenerate package-lock.json with kirinchat-frontend"
```

---

### Task 17: Phase 2 最终验证

- [ ] **Step 1: 全局 agentchat 残留扫描**

```bash
cd D:/HuaweiMoveData/Users/28966/Desktop/AgentChat
grep -rn "agentchat\|AgentChat" --include="*.py" --include="*.vue" --include="*.yaml" --include="*.yml" --include="*.json" --include="*.html" --include="*.sh" --include="*.bat" --include="*.md" --include="*.toml" . \
  | grep -v ".venv/" | grep -v "node_modules/" | grep -v ".git/" | grep -v "docs/superpowers/" | grep -v "uv.lock"
```

预期可接受的残留：
- `agentchat.oss-cn-beijing.aliyuncs.com`（原作者的 OSS 图片资源 URL，暂保留）
- `docs/superpowers/` 下的设计文档（历史记录）

- [ ] **Step 2: 智言残留扫描**

```bash
grep -rn "智言" --include="*.py" --include="*.vue" --include="*.yaml" --include="*.html" --include="*.md" . \
  | grep -v ".venv/" | grep -v "node_modules/" | grep -v ".git/" | grep -v "docs/superpowers/"
```
Expected: 无匹配

- [ ] **Step 3: 作者信息残留扫描**

```bash
grep -rn "MingGuang\|Shy2593666979\|2593666979@qq\|LiangTian\|小田" . \
  --include="*.py" --include="*.vue" --include="*.yaml" --include="*.yml" --include="*.json" \
  --include="*.html" --include="*.sh" --include="*.bat" --include="*.md" --include="*.toml" \
  | grep -v ".venv/" | grep -v "node_modules/" | grep -v ".git/" | grep -v "docs/superpowers/"
```
Expected: 无匹配

- [ ] **Step 4: 前端构建测试**

```bash
cd src/frontend
npm run build
```
Expected: 构建成功，无错误

- [ ] **Step 5: Python import 测试（如果环境允许）**

```bash
cd src/backend
python -c "from kirinchat.settings import app_settings; print(app_settings)"
```
Expected: 正常输出，无 ModuleNotFoundError

---

## 验收清单

- [ ] 所有 API 密钥已替换为占位符
- [ ] LICENSE 作者已改为 kirin
- [ ] 前端显示 "KirinChat" / "麒麟智聊"
- [ ] README 链接指向 kirintj/KirinChat
- [ ] Docker 容器名全部更新
- [ ] Python 包目录已重命名为 kirinchat
- [ ] 所有 import 语句已更新
- [ ] 前端 build 成功
- [ ] 无残留的 "AgentChat"、"智言"、原作者信息（除 OSS URL 和历史设计文档）
