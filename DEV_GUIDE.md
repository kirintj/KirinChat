# KirinChat 本地开发环境指南

## 🎯 开发架构

```
┌─────────────────────────────────────────┐
│  本地代码（热重载，便于调试）              │
├─────────────────────────────────────────┤
│  后端 (localhost:7860) - uvicorn         │
│  前端 (localhost:8090) - Vite            │
└─────────────────────────────────────────┘
                    ↕ 连接
┌─────────────────────────────────────────┐
│  Docker 基础服务                         │
├─────────────────────────────────────────┤
│  MySQL 8.0 (localhost:3306)            │
│  Redis 7.0 (localhost:6379)            │
│  MinIO (localhost:9000/9001)            │
└─────────────────────────────────────────┘
```

## 🚀 快速开始

### Windows 用户

#### 1️⃣ 启动开发环境
```bash
# 双击运行
start-dev.bat
```

这会自动：
- 启动 Docker 基础服务（MySQL、Redis、MinIO）
- 安装后端依赖（首次运行）
- 启动后端服务（热重载模式）

#### 2️⃣ 启动前端（新终端）
```bash
# 双击运行
start-frontend.bat
```

#### 3️⃣ 停止所有服务
```bash
# 双击运行
stop-dev.bat
```

### Linux/Mac 用户

#### 1️⃣ 启动开发环境
```bash
chmod +x start-dev.sh
./start-dev.sh
```

#### 2️⃣ 启动前端（新终端）
```bash
chmod +x start-frontend.sh
./start-frontend.sh
```

#### 3️⃣ 停止所有服务
```bash
chmod +x stop-dev.sh
./stop-dev.sh
```

---

## ⚙️ 配置步骤

### 1. 配置 API 密钥

编辑 `src/backend/agentchat/config.yaml`（首次运行会自动从 `config-dev.yaml` 复制）：

```yaml
# 必须配置
multi_models:
  conversation_model:
    api_key: "你的通义千问API密钥"  # 获取地址：https://dashscope.console.aliyun.com/
    model_name: "qwen-plus"
  
  embedding:
    api_key: "你的通义千问API密钥"
    model_name: "text-embedding-v4"

# 可选配置
tools:
  weather:
    api_key: "你的高德天气API密钥"  # 获取地址：https://console.amap.com/dev/key/app
```

### 2. 验证服务状态

启动后访问：
- ✅ 后端 API：http://localhost:7860
- ✅ API 文档：http://localhost:7860/docs
- ✅ MinIO 控制台：http://localhost:9001（用户名/密码：minioadmin/minioadmin）

---

## 🔧 开发流程

### 后端开发

```bash
# 启动后端（热重载）
cd src/backend
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uvicorn agentchat.main:app --reload --host 0.0.0.0 --port 7860

# 修改代码后会自动重启
# 查看日志：终端会实时显示
```

### 前端开发

```bash
# 启动前端
cd src/frontend
npm run dev

# 修改代码后会自动热更新
# 浏览器访问：http://localhost:8090
```

### 数据库管理

```bash
# 连接 MySQL
mysql -h localhost -P 3306 -u root -p123456 agentchat

# 查看 Redis
redis-cli -h localhost -p 6379
```

---

## 📂 文件结构

```
KirinChat/
├── docker/
│   ├── docker-compose-dev.yml  # 本地开发用
│   └── mysql/init/            # MySQL 初始化脚本
├── src/
│   ├── backend/
│   │   └── agentchat/
│   │       ├── config-dev.yaml  # 开发配置模板
│   │       └── config.yaml      # 实际配置（需创建）
│   └── frontend/
│       └── ...
├── start-dev.sh/bat          # 启动开发环境
├── start-frontend.sh/bat     # 启动前端
└── stop-dev.sh/bat           # 停止开发环境
```

---

## 🐛 常见问题

### 1. Docker 服务启动失败

**问题**：`docker-compose up` 失败

**解决**：
```bash
# 检查 Docker 是否运行
docker --version

# 清理旧容器
docker-compose -f docker/docker-compose-dev.yml down -v

# 重新启动
docker-compose -f docker/docker-compose-dev.yml up -d
```

### 2. MySQL 连接失败

**问题**：`Can't connect to MySQL server`

**解决**：
```bash
# 检查 MySQL 是否就绪
docker-compose -f docker/docker-compose-dev.yml logs mysql

# 等待 MySQL 完全启动（约 30 秒）
sleep 30

# 测试连接
mysql -h localhost -P 3306 -u root -p123456 -e "SELECT 1"
```

### 3. 端口被占用

**问题**：`Port 7860 already in use`

**解决**：
```bash
# 找到占用端口的进程
lsof -i :7860  # Linux/Mac
netstat -ano | findstr :7860  # Windows

# 终止进程或修改 config.yaml 中的端口
```

### 4. 后端依赖安装失败

**问题**：`pip install` 或 `uv sync` 失败

**解决**：
```bash
# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 或使用 uv
uv sync --index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

### 5. 前端启动失败

**问题**：`npm run dev` 失败

**解决**：
```bash
# 清理缓存
rm -rf node_modules package-lock.json
npm cache clean --force

# 重新安装
npm install
npm run dev
```

---

## 💡 开发技巧

### 1. 查看实时日志

```bash
# 后端日志（自动热重载时会显示）
# 直接在启动后端的终端查看

# Docker 服务日志
docker-compose -f docker/docker-compose-dev.yml logs -f

# 查看特定服务
docker-compose -f docker/docker-compose-dev.yml logs -f mysql
docker-compose -f docker/docker-compose-dev.yml logs -f redis
```

### 2. 数据库迁移

```bash
# 进入后端目录
cd src/backend
source .venv/bin/activate

# 运行迁移（如果有）
alembic upgrade head
```

### 3. 调试后端

```bash
# 使用 Python 调试器
import pdb; pdb.set_trace()

# 或使用 IDE 调试器（VSCode/PyCharm）
# 配置 uvicorn 启动参数：--reload --host 0.0.0.0 --port 7860
```

### 4. 清理和重建

```bash
# 完全清理 Docker 数据
docker-compose -f docker/docker-compose-dev.yml down -v

# 清理后端依赖
cd src/backend
rm -rf .venv
uv sync

# 清理前端依赖
cd src/frontend
rm -rf node_modules
npm install
```

---

## 📚 相关文档

- [项目文档](docs/)
- [API 文档](http://localhost:7860/docs)（启动后访问）
- [部署指南](docker/README.md)

---

## 🆘 获取帮助

如果遇到问题：

1. 查看本文档的常见问题部分
2. 检查 GitHub Issues
3. 查看项目 README.md

---

## ✨ 开发最佳实践

1. **代码修改**：后端代码修改后会自动热重载
2. **配置修改**：修改 `config.yaml` 后需要重启后端
3. **依赖更新**：更新依赖后需要重启服务
4. **数据库变更**：使用迁移脚本管理数据库结构
5. **版本控制**：不要提交 `config.yaml`，只提交 `config-dev.yaml`

---

**祝你开发愉快！** 🎉
