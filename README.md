<div align="center">

# 🦄 KirinChat

**一个基于大语言模型的现代化智能对话系统，支持多Agent协作、知识库检索、工具调用和MCP服务器集成**

[![GitHub Stars](https://img.shields.io/github/stars/kirintj/KirinChat.svg?style=flat-square&logo=github)](https://github.com/kirintj/KirinChat/stargazers)
[![GitHub Forks](https://img.shields.io/github/forks/kirintj/KirinChat.svg?style=flat-square&logo=github)](https://github.com/kirintj/KirinChat/network/members)
[![GitHub Issues](https://img.shields.io/github/issues/kirintj/KirinChat.svg?style=flat-square&logo=github)](https://github.com/kirintj/KirinChat/issues)
[![GitHub Pull Requests](https://img.shields.io/github/issues-pr/kirintj/KirinChat.svg?style=flat-square&logo=github)](https://github.com/kirintj/KirinChat/pulls)
[![License](https://img.shields.io/github/license/kirintj/KirinChat.svg?style=flat-square)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.12+-blue.svg?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Vue](https://img.shields.io/badge/vue-3.4+-4FC08D.svg?style=flat-square&logo=vue.js&logoColor=white)](https://vuejs.org/)
[![FastAPI](https://img.shields.io/badge/fastapi-0.115+-009688.svg?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)

[English](./README_EN.md) | 简体中文

</div>

---

## 📖 项目介绍

KirinChat 是一个基于大语言模型构建的现代化智能对话系统，采用前后端分离架构，为企业和开发者提供强大的AI对话能力。

### 解决的问题

- 降低AI对话系统开发门槛，提供开箱即用的解决方案
- 解决多轮对话上下文丢失问题，实现智能记忆管理
- 简化AI工具集成流程，支持可视化配置和动态加载
- 提供人机协同工作模式，在自动化流程中保留人工干预能力

### 核心功能

- 🤖 **智能Agent系统** - 支持多Agent协作，具备推理和决策能力
- 📚 **知识库检索** - 基于RAG技术实现精准知识检索和问答
- 🔧 **工具生态** - 内置多种实用工具，支持自定义扩展
- 🔌 **MCP集成** - 支持Model Context Protocol服务器，实现动态工具加载
- 🧠 **三层记忆架构** - 短期保留上下文，历史自动总结，长期记录用户偏好
- 👥 **人机协同** - 基于HITL对话式生成MCP Server，关键节点可人工介入
- 📊 **数据看板** - 实时监控Agent、模型调用情况和Token使用量
- 🎙️ **语音面试** - 支持语音交互的智能面试系统

### 适用场景

- 企业智能客服系统
- AI助手应用开发
- 知识库问答平台
- 自动化工作流编排
- 智能面试评估系统
- AI工具集成平台

---

## ✨ 核心特性

### 技术亮点

1. **智能对话引擎**
   - 支持多模型生态（OpenAI、通义千问等）
   - 流式响应，实时输出
   - 思考过程可视化
   - 上下文智能管理

2. **先进的RAG系统**
   - 多格式文档支持（PDF、Word、Markdown等）
   - 智能语义分块
   - 向量检索（Milvus/ChromaDB）
   - 知识库热更新

3. **灵活的Agent框架**
   - 多Agent协作机制
   - 任务自动化编排
   - Sub-Agent动态调度
   - 工具链式调用

4. **企业级架构**
   - 前后端分离，易于扩展
   - Docker容器化部署
   - 异步高性能处理
   - 细粒度权限控制

5. **创新的人机协同**
   - 对话式MCP Server生成
   - 关键决策节点人工介入
   - 动态配置与实时交互
   - 可控的自动化流程

---

## 📦 环境依赖

### 系统要求

| 依赖项 | 版本要求 | 说明 |
|--------|----------|------|
| Python | >= 3.12 | 后端运行环境 |
| Node.js | >= 18 | 前端构建环境 |
| MySQL | >= 8.0 | 主数据库 |
| Redis | >= 7.0 | 缓存和消息队列 |
| Docker | >= 20.10 | 容器化部署（可选） |

### 后端核心依赖

- FastAPI 0.121+ - 高性能异步Web框架
- LangChain 1.2+ - LLM应用开发框架
- ChromaDB/Milvus - 向量数据库
- Celery - 异步任务队列
- MinIO/OSS - 对象存储

### 前端核心依赖

- Vue 3.4+ - 渐进式JavaScript框架
- Pinia - 状态管理
- Vite 5 - 构建工具
- TypeScript - 类型安全
- ECharts - 数据可视化

---

## ⚙️ 快速部署 & 安装

### 方式一：Docker一键部署（推荐）

```bash
# 1. 克隆项目
git clone https://github.com/kirintj/KirinChat.git
cd KirinChat

# 2. 配置环境变量
cp docker/docker_config.yaml.example docker/docker_config.yaml
vim docker/docker_config.yaml  # 编辑配置文件

# 3. 启动服务
cd docker
docker-compose up --build -d

# 4. 访问应用
# 前端：http://localhost:5173
# 后端API文档：http://localhost:8000/docs
```

### 方式二：本地部署

#### 后端启动

```bash
# 1. 进入后端目录
cd src/backend

# 2. 创建虚拟环境（推荐使用uv）
pip install uv
uv venv
source .venv/bin/activate  # Linux/Mac
# 或 .venv\Scripts\activate  # Windows

# 3. 安装依赖
uv sync
# 或 pip install -r requirements.txt

# 4. 配置环境变量
cp config-dev.yaml.example config-dev.yaml
vim config-dev.yaml  # 编辑配置文件

# 5. 启动服务
uvicorn kirinchat.main:app --reload --host 0.0.0.0 --port 8000
```

#### 前端启动

```bash
# 1. 进入前端目录
cd src/frontend

# 2. 安装依赖
npm install

# 3. 启动开发服务器
npm run dev

# 4. 访问 http://localhost:5173
```

<details>
<summary>📋 配置文件示例</summary>

```yaml
# config-dev.yaml 示例
database:
  host: localhost
  port: 3306
  user: root
  password: your_password
  database: kirinchat

redis:
  host: localhost
  port: 6379
  password: ""

llm:
  openai:
    api_key: "your-openai-api-key"
    base_url: "https://api.openai.com/v1"
  dashscope:
    api_key: "your-dashscope-api-key"

vector_store:
  type: chromadb  # 或 milvus
  chromadb:
    path: ./data/chromadb
  milvus:
    host: localhost
    port: 19530

storage:
  type: minio  # 或 oss
  minio:
    endpoint: localhost:9000
    access_key: minioadmin
    secret_key: minioadmin
    bucket: kirinchat
```

</details>

---

## 🚀 使用示例

### 基础对话示例

```python
from kirinchat.core.llm import ChatLLM
from kirinchat.core.memory import MemoryManager

# 初始化LLM和记忆管理器
llm = ChatLLM(model="gpt-4")
memory = MemoryManager(user_id="user_123")

# 带记忆的多轮对话
messages = memory.get_context()
messages.append({"role": "user", "content": "你好，请介绍一下自己"})

response = llm.chat(messages)
memory.save_message("assistant", response.content)

print(response.content)
```

### Agent调用示例

```python
from kirinchat.core.agent import Agent
from kirinchat.tools import WeatherTool, SearchTool

# 创建Agent并绑定工具
agent = Agent(
    name="智能助手",
    llm=ChatLLM(model="gpt-4"),
    tools=[WeatherTool(), SearchTool()]
)

# 执行任务
result = agent.run("查询北京今天天气，并搜索附近的餐厅推荐")
print(result)
```

### 知识库检索示例

```python
from kirinchat.core.knowledge import KnowledgeBase

# 初始化知识库
kb = KnowledgeBase(name="product_docs")

# 上传文档
kb.upload_document("./docs/product.pdf")

# 检索问答
answer = kb.query("产品的退款政策是什么？")
print(answer)
```

### API调用示例

```bash
# 健康检查
curl http://localhost:8000/api/v1/health

# 创建对话（需要认证）
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Authorization: Bearer your-token" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "你好",
    "agent_id": "default",
    "stream": false
  }'
```

---

## 📂 项目目录结构

```
KirinChat/
├── src/
│   ├── backend/                    # 后端服务
│   │   ├── kirinchat/
│   │   │   ├── api/               # API接口层
│   │   │   │   └── v1/           # API版本
│   │   │   ├── core/             # 核心业务逻辑
│   │   │   │   ├── agent/        # Agent实现
│   │   │   │   ├── llm/          # LLM集成
│   │   │   │   ├── memory/       # 记忆管理
│   │   │   │   └── knowledge/    # 知识库
│   │   │   ├── tools/            # 内置工具
│   │   │   ├── models/           # 数据模型
│   │   │   ├── schemas/          # Pydantic Schemas
│   │   │   ├── services/         # 业务服务层
│   │   │   ├── common/           # 公共模块
│   │   │   │   ├── async_task/   # 异步任务
│   │   │   │   ├── file_storage/ # 文件存储
│   │   │   │   └── security/     # 安全认证
│   │   │   ├── database/         # 数据库相关
│   │   │   ├── config/           # 配置管理
│   │   │   └── utils/            # 工具函数
│   │   ├── pyproject.toml        # Python项目配置
│   │   └── uv.lock              # 依赖锁定文件
│   │
│   └── frontend/                   # 前端应用
│       ├── src/
│       │   ├── apis/             # API调用封装
│       │   ├── components/       # 组件库
│       │   │   ├── ui/          # 基础UI组件
│       │   │   ├── dialog/      # 对话框组件
│       │   │   └── ...          # 业务组件
│       │   ├── pages/           # 页面组件
│       │   │   ├── conversation/# 对话页面
│       │   │   ├── knowledge/   # 知识库页面
│       │   │   ├── agent/       # Agent配置
│       │   │   └── ...          # 其他页面
│       │   ├── router/          # 路由配置
│       │   ├── store/           # 状态管理
│       │   ├── styles/          # 样式文件
│       │   └── utils/           # 工具函数
│       ├── package.json          # 前端依赖
│       └── vite.config.ts        # Vite配置
│
├── docker/                         # Docker配置
│   ├── docker-compose.yml         # 容器编排
│   ├── docker_config.yaml         # Docker环境配置
│   └── mysql/                     # MySQL初始化
│
├── tests/                          # 测试代码
│   └── backend/                   # 后端测试
│
├── docs/                           # 项目文档
│   ├── reference/                 # 技术文档
│   └── development/               # 开发指南
│
├── scripts/                        # 辅助脚本
├── README.md                       # 项目说明
├── LICENSE                         # 开源协议
├── DEV_GUIDE.md                    # 开发指南
└── QUICKSTART.md                   # 快速开始
```

### 目录说明

- **src/backend** - FastAPI后端服务，提供RESTful API和WebSocket支持
- **src/frontend** - Vue 3前端应用，采用Pinia状态管理和Vue Router路由
- **docker** - Docker容器化部署配置，支持一键启动
- **tests** - 单元测试和集成测试代码
- **docs** - 项目文档，包括技术文档和开发指南
- **scripts** - 辅助脚本，用于模型服务、数据迁移等

---

## 📝 配置说明

### 核心配置项

<details>
<summary>📋 数据库配置（必填）</summary>

```yaml
database:
  host: "localhost"        # 数据库地址
  port: 3306              # 端口
  user: "root"            # 用户名
  password: "your_pwd"    # 密码
  database: "kirinchat"   # 数据库名
```

</details>

<details>
<summary>📋 LLM配置（必填）</summary>

```yaml
llm:
  # OpenAI配置
  openai:
    api_key: "sk-xxx"              # API密钥
    base_url: "https://api.openai.com/v1"  # API地址（可选）
    model: "gpt-4"                 # 默认模型

  # 通义千问配置
  dashscope:
    api_key: "sk-xxx"              # API密钥
    model: "qwen-turbo"            # 默认模型

  # 其他兼容OpenAI的模型
  custom:
    api_key: "xxx"
    base_url: "https://your-api.com/v1"
    model: "your-model"
```

</details>

<details>
<summary>📋 向量数据库配置（必填）</summary>

```yaml
vector_store:
  type: "chromadb"  # 可选: chromadb / milvus

  # ChromaDB配置（开发环境推荐）
  chromadb:
    path: "./data/chromadb"

  # Milvus配置（生产环境推荐）
  milvus:
    host: "localhost"
    port: 19530
    collection_prefix: "kirinchat_"
```

</details>

<details>
<summary>📋 Redis配置（必填）</summary>

```yaml
redis:
  host: "localhost"
  port: 6379
  password: ""           # 无密码留空
  db: 0
  cache_ttl: 3600       # 缓存过期时间（秒）
```

</details>

<details>
<summary>📋 对象存储配置（可选）</summary>

```yaml
storage:
  type: "minio"  # 可选: minio / oss

  # MinIO配置
  minio:
    endpoint: "localhost:9000"
    access_key: "minioadmin"
    secret_key: "minioadmin"
    bucket: "kirinchat"
    secure: false

  # 阿里云OSS配置
  oss:
    access_key_id: "xxx"
    access_key_secret: "xxx"
    endpoint: "oss-cn-hangzhou.aliyuncs.com"
    bucket: "kirinchat"
```

</details>

<details>
<summary>📋 安全配置（必填）</summary>

```yaml
security:
  secret_key: "your-secret-key-here"  # JWT密钥
  algorithm: "HS256"
  access_token_expire_minutes: 1440   # Token过期时间
```

</details>

### 配置优先级

1. 环境变量（最高优先级）
2. `config-dev.yaml`（开发环境）
3. `config-prod.yaml`（生产环境）
4. 默认配置（最低优先级）

---

## 🧪 测试方式

### 运行单元测试

```bash
# 进入后端目录
cd src/backend

# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_chat.py

# 运行并生成覆盖率报告
pytest --cov=kirinchat --cov-report=html

# 查看覆盖率报告
open htmlcov/index.html
```

### 运行集成测试

```bash
# 确保服务已启动
# 运行集成测试
pytest tests/integration/ -v
```

### 前端测试

```bash
# 进入前端目录
cd src/frontend

# 运行类型检查
npm run lint

# 运行构建测试
npm run build
```

### API测试

```bash
# 使用curl测试健康检查
curl http://localhost:8000/health

# 使用curl测试对话接口
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-token" \
  -d '{"message": "测试消息"}'

# 查看API文档
open http://localhost:8000/docs
```

### 调试技巧

```bash
# 后端日志查看
tail -f logs/kirinchat.log

# Docker日志查看
docker-compose logs -f backend

# 进入容器调试
docker exec -it kirinchat-backend bash
```

---

## ❓ 常见问题 FAQ

<details>
<summary><b>Q1: 启动时提示"数据库连接失败"怎么办？</b></summary>

**原因**：数据库配置错误或MySQL服务未启动

**解决方案**：
1. 检查 `config-dev.yaml` 中的数据库配置
2. 确保MySQL服务已启动：
   ```bash
   # Docker方式
   docker-compose up -d mysql

   # 系统服务方式
   sudo systemctl start mysql
   ```
3. 验证数据库连接：
   ```bash
   mysql -h localhost -u root -p
   ```

</details>

<details>
<summary><b>Q2: 前端启动后页面空白？</b></summary>

**原因**：后端服务未启动或API地址配置错误

**解决方案**：
1. 确保后端服务已启动：`http://localhost:8000/docs`
2. 检查前端环境变量配置：
   ```env
   VITE_API_BASE_URL=http://localhost:8000
   ```
3. 清除浏览器缓存后重试

</details>

<details>
<summary><b>Q3: 向量数据库初始化失败？</b></summary>

**原因**：ChromaDB路径无权限或Milvus服务未启动

**解决方案**：
1. ChromaDB：
   ```bash
   # 确保目录存在且有写权限
   mkdir -p ./data/chromadb
   chmod 755 ./data/chromadb
   ```
2. Milvus：
   ```bash
   # 检查Milvus服务状态
   docker-compose ps milvus

   # 查看日志
   docker-compose logs milvus
   ```

</details>

<details>
<summary><b>Q4: LLM调用超时怎么办？</b></summary>

**原因**：网络问题或API密钥错误

**解决方案**：
1. 检查网络连接和代理设置
2. 验证API密钥是否正确
3. 调整超时配置：
   ```yaml
   llm:
     timeout: 60  # 增加超时时间
     max_retries: 3  # 增加重试次数
   ```
4. 如果使用国内模型，确保使用正确的API地址

</details>

<details>
<summary><b>Q5: Docker部署时前端无法连接后端？</b></summary>

**原因**：容器网络配置问题

**解决方案**：
1. 检查 `docker-compose.yml` 中的网络配置
2. 确保服务名称正确：
   ```yaml
   # docker-compose.yml
   services:
     backend:
       networks:
         - kirinchat
     frontend:
       environment:
         - VITE_API_BASE_URL=http://backend:8000
       networks:
         - kirinchat
   ```
3. 重建容器：
   ```bash
   docker-compose down
   docker-compose up --build -d
   ```

</details>

<details>
<summary><b>Q6: 如何切换不同的LLM模型？</b></summary>

**解决方案**：
1. 在配置文件中添加模型配置：
   ```yaml
   llm:
     openai:
       api_key: "sk-xxx"
       model: "gpt-4"  # 或 gpt-3.5-turbo
     dashscope:
       api_key: "sk-xxx"
       model: "qwen-plus"  # 或 qwen-turbo
   ```
2. 在创建Agent时指定模型：
   ```python
   agent = Agent(llm=ChatLLM(model="gpt-4"))
   ```
3. 前端可以在设置页面切换默认模型

</details>

<details>
<summary><b>Q7: 如何添加自定义工具？</b></summary>

**解决方案**：
1. 创建工具类：
   ```python
   from kirinchat.tools.base import BaseTool

   class MyTool(BaseTool):
       name = "my_tool"
       description = "我的自定义工具"

       async def run(self, params: dict) -> str:
           # 实现工具逻辑
           return "工具执行结果"
   ```
2. 注册工具：
   ```python
   from kirinchat.tools import register_tool
   register_tool(MyTool())
   ```
3. 或者通过Swagger/OpenAPI文件导入工具

</details>

---

## 🤝 贡献指南

我们欢迎所有形式的贡献，包括但不限于：问题反馈、功能建议、代码贡献、文档改进。

### 贡献流程

1. **Fork 项目**
   ```bash
   # 点击页面右上角的 Fork 按钮
   ```

2. **克隆你的 Fork**
   ```bash
   git clone https://github.com/YOUR_USERNAME/KirinChat.git
   cd KirinChat
   ```

3. **创建特性分支**
   ```bash
   git checkout -b feature/amazing-feature
   ```

4. **提交更改**
   ```bash
   git add .
   git commit -m "feat: add amazing feature"
   ```

5. **推送分支**
   ```bash
   git push origin feature/amazing-feature
   ```

6. **创建 Pull Request**
   - 访问你的 Fork 页面
   - 点击 "New Pull Request"
   - 填写PR描述，说明改动内容

### 代码提交规范

我们遵循 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Type 类型：**
- `feat`: 新功能
- `fix`: Bug修复
- `docs`: 文档更新
- `style`: 代码格式调整（不影响功能）
- `refactor`: 代码重构
- `perf`: 性能优化
- `test`: 测试相关
- `chore`: 构建/工具相关

**示例：**
```
feat(chat): 支持多轮对话记忆

- 添加短期记忆管理
- 实现历史对话总结
- 优化上下文窗口

Closes #123
```

### 开发规范

- 后端代码遵循 PEP 8 规范
- 前端代码使用 ESLint + Prettier
- 提交前运行测试：`pytest`
- 确保代码通过类型检查：`npm run lint`

### 报告问题

- 使用 GitHub Issues 报告 Bug
- 提供详细的复现步骤和环境信息
- 附上相关日志和错误信息

---

## 📜 开源协议

本项目采用 [MIT License](LICENSE) 开源许可证。

```
MIT License

Copyright (c) 2024 KirinChat

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 🙏 致谢

感谢以下开源项目和贡献者：

- [LangChain](https://github.com/langchain-ai/langchain) - LLM应用开发框架
- [FastAPI](https://github.com/tiangolo/fastapi) - 高性能Web框架
- [Vue.js](https://github.com/vuejs/vue) - 渐进式JavaScript框架
- [ChromaDB](https://github.com/chroma-core/chroma) - 向量数据库
- [Milvus](https://github.com/milvus-io/milvus) - 向量数据库
- [MinIO](https://github.com/minio/minio) - 对象存储

感谢所有为 KirinChat 做出贡献的开发者！

---

## 📞 联系我们

- **GitHub Issues**: [提交问题](https://github.com/kirintj/KirinChat/issues)
- **GitHub Discussions**: [参与讨论](https://github.com/kirintj/KirinChat/discussions)
- **Email**: 2896651097@qq.com

---

## ⭐ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=kirintj/KirinChat&type=Date)](https://star-history.com/#kirintj/KirinChat&Date)

---

<div align="center">

**如果这个项目对你有帮助，请给我们一个 ⭐️**

*让更多的人发现这个项目，一起构建AI的未来！*

*Made with ❤️ by the KirinChat Team*

</div>

---

## 📚 附录

### README 美化小技巧

1. **添加动态徽章**
   - 使用 [Shields.io](https://shields.io/) 生成自定义徽章
   - 示例：`![Custom Badge](https://img.shields.io/badge/自定义-徽章-blue)`

2. **使用表情符号**
   - 标题前添加表情符号增加可读性
   - 常用：📦 🚀 ⚙️ ❓ 🤝 📜

3. **添加目录导航**
   - 使用 `[TOC]` 或手动生成目录
   - GitHub 自动支持目录跳转

4. **代码高亮**
   - 指定语言类型：```python, ```bash, ```javascript
   - 使用 `diff` 显示代码变更

5. **折叠块使用**
   - 长配置、日志使用 `<details>` 折叠
   - 保持页面简洁

6. **添加项目图表**
   - 使用 Mermaid 绘制流程图
   - 使用 ASCII 字符绘制简单图表

### GitHub 徽章生成地址

- **Shields.io**: https://shields.io/
- **徽章生成器**: https://badgen.net/
- **GitHub Stats**: https://github.com/anuraghazra/github-readme-stats
- **Star History**: https://star-history.com/
- **贡献者图表**: https://contrib.rocks/
- **仓库模板**: https://github.com/othneildrew/Best-README-Template
- **Awesome README**: https://github.com/matiassingers/awesome-readme

### Markdown 语法参考

- **GitHub Docs**: https://docs.github.com/en/get-started/writing-on-github
- **Markdown Guide**: https://www.markdownguide.org/
- **CommonMark**: https://commonmark.org/help/

