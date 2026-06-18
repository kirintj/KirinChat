# 🚀 KirinChat 本地开发 - 快速参考

## ⚡ 一键启动

### Windows
```bash
start-all.bat        # 完整启动（Docker + 后端 + 前端）
```

### Linux/Mac
```bash
chmod +x start-all.sh
./start-all.sh       # 完整启动
```

---

## 📦 分步启动

### Windows

```bash
# 1. 启动 Docker 基础服务
start-dev.bat

# 2. 启动前端（新终端）
start-frontend.bat

# 3. 停止所有服务
stop-dev.bat
```

### Linux/Mac

```bash
# 1. 启动 Docker + 后端
chmod +x start-dev.sh
./start-dev.sh

# 2. 启动前端（新终端）
chmod +x start-frontend.sh
./start-frontend.sh

# 3. 停止所有服务
chmod +x stop-dev.sh
./stop-dev.sh
```

---

## 🌐 访问地址

| 服务 | 地址 | 说明 |
|------|------|------|
| 前端界面 | http://localhost:8090 | 主界面 |
| 后端API | http://localhost:7860 | REST API |
| API文档 | http://localhost:7860/docs | Swagger |
| MinIO控制台 | http://localhost:9001 | 对象存储（minioadmin/minioadmin） |
| MySQL | localhost:3306 | 数据库（root/123456） |
| Redis | localhost:6379 | 缓存 |

---

## ⚙️ 配置文件

**位置**：`src/backend/agentchat/config.yaml`

**必需配置**：
```yaml
multi_models:
  conversation_model:
    api_key: "你的通义千问API密钥"
  embedding:
    api_key: "你的通义千问API密钥"
```

**获取 API 密钥**：
- 通义千问：https://dashscope.console.aliyun.com/
- 高德天气：https://console.amap.com/dev/key/app

---

## 🔧 常见操作

### 查看日志

```bash
# Docker 服务日志
docker-compose -f docker/docker-compose-dev.yml logs -f

# 后端日志
# 直接在后端启动终端查看

# 特定服务
docker-compose -f docker/docker-compose-dev.yml logs -f mysql
docker-compose -f docker/docker-compose-dev.yml logs -f redis
```

### 重启服务

```bash
# 重启 Docker 服务
docker-compose -f docker/docker-compose-dev.yml restart

# 重启后端
# 按 Ctrl+C 停止，然后重新启动

# 重启前端
# 按 Ctrl+C 停止，然后 npm run dev
```

### 清理数据

```bash
# 停止并清理 Docker 数据
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

## 🐛 故障排查

### 1. 端口被占用

```bash
# 找到占用端口的进程
# Linux/Mac
lsof -i :7860

# Windows
netstat -ano | findstr :7860

# 终止进程或修改 config.yaml 中的端口
```

### 2. Docker 启动失败

```bash
# 检查 Docker 状态
docker --version
docker ps

# 清理旧容器
docker-compose -f docker/docker-compose-dev.yml down -v

# 重新启动
docker-compose -f docker/docker-compose-dev.yml up -d
```

### 3. MySQL 连接失败

```bash
# 等待 MySQL 完全启动
sleep 30

# 测试连接
mysql -h localhost -P 3306 -u root -p123456 -e "SELECT 1"

# 查看 MySQL 日志
docker-compose -f docker/docker-compose-dev.yml logs mysql
```

### 4. 依赖安装失败

```bash
# 使用国内镜像（Python）
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 使用国内镜像（Node）
npm config set registry https://registry.npmmirror.com
npm install
```

---

## 💡 开发技巧

1. **热重载**：后端和前端都支持代码修改后自动重载
2. **配置修改**：修改 `config.yaml` 后需要重启后端
3. **数据库管理**：使用 MySQL Workbench 或命令行连接
4. **API 测试**：访问 http://localhost:7860/docs 使用 Swagger
5. **文件存储**：MinIO 控制台可以管理上传的文件

---

## 📂 重要文件

```
KirinChat/
├── start-all.bat/sh          # 一键启动（推荐）
├── start-dev.bat/sh          # 启动 Docker + 后端
├── start-frontend.bat/sh     # 启动前端
├── stop-dev.bat/sh           # 停止所有服务
├── DEV_GUIDE.md              # 完整开发指南
├── docker/
│   └── docker-compose-dev.yml  # Docker 配置
└── src/
    ├── backend/
    │   └── agentchat/
    │       ├── config-dev.yaml  # 配置模板
    │       └── config.yaml      # 实际配置（需创建）
    └── frontend/
        └── package.json
```

---

## 🎯 开发流程

```
启动开发环境
    ↓
编辑 config.yaml（填入 API 密钥）
    ↓
启动 start-all.bat/sh
    ↓
访问 http://localhost:8090
    ↓
修改代码 → 自动热重载
    ↓
测试功能 → API 文档 http://localhost:7860/docs
    ↓
完成开发 → stop-dev.bat/sh
```

---

## 📚 更多文档

- **完整指南**：[DEV_GUIDE.md](DEV_GUIDE.md)
- **项目文档**：[README.md](README.md)
- **Docker 配置**：[docker/README.md](docker/README.md)

---

**祝你开发愉快！** 🎉

有问题？查看 [DEV_GUIDE.md](DEV_GUIDE.md) 的常见问题部分
