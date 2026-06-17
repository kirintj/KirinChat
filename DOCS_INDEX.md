# 📚 AgentChat 文档索引

## 🚀 快速开始

- **[QUICKSTART.md](QUICKSTART.md)** - 快速参考卡（推荐先看）
- **[DEV_GUIDE.md](DEV_GUIDE.md)** - 完整开发指南

## 📦 启动脚本

### Windows
- `start-all.bat` - 一键启动所有服务（推荐）
- `start-dev.bat` - 启动 Docker + 后端
- `start-frontend.bat` - 启动前端
- `stop-dev.bat` - 停止所有服务

### Linux/Mac
- `start-all.sh` - 一键启动所有服务（推荐）
- `start-dev.sh` - 启动 Docker + 后端
- `start-frontend.sh` - 启动前端
- `stop-dev.sh` - 停止所有服务

## 📖 项目文档

- **[README.md](README.md)** - 项目介绍和功能说明
- **[LICENSE](LICENSE)** - MIT 许可证

## 🐳 Docker 相关

- **[docker/README.md](docker/README.md)** - Docker 部署指南
- **[docker/docker-compose.yml](docker/docker-compose.yml)** - 生产环境配置
- **[docker/docker-compose-dev.yml](docker/docker-compose-dev.yml)** - 开发环境配置

## 💻 源代码

### 后端
- **[src/backend/agentchat/main.py](src/backend/agentchat/main.py)** - 后端入口
- **[src/backend/agentchat/config-dev.yaml](src/backend/agentchat/config-dev.yaml)** - 配置模板
- **[src/backend/requirements.txt](src/backend/requirements.txt)** - Python 依赖

### 前端
- **[src/frontend/package.json](src/frontend/package.json)** - Node.js 依赖

## 📝 配置文件

- **[src/backend/agentchat/config.yaml](src/backend/agentchat/config.yaml)** - 实际配置（需创建）
  - 数据库连接
  - AI 模型 API 密钥
  - 工具配置
  - 存储配置

## 🔧 开发工具

### IDE 配置
- VSCode 推荐安装 Python、Vite、ESLint 扩展
- PyCharm 可直接导入项目

### 调试工具
- **Swagger UI**：http://localhost:7860/docs
- **MinIO Console**：http://localhost:9001
- **MySQL Workbench**：连接 localhost:3306

## 📊 访问地址

| 服务 | 地址 | 用途 |
|------|------|------|
| 前端 | http://localhost:8090 | 用户界面 |
| 后端 | http://localhost:7860 | API 服务 |
| API 文档 | http://localhost:7860/docs | 接口测试 |
| MinIO | http://localhost:9001 | 文件管理 |
| MySQL | localhost:3306 | 数据库 |
| Redis | localhost:6379 | 缓存 |

## 🎯 开发流程

```
1. 阅读 QUICKSTART.md 了解快速启动
2. 运行 start-all.bat/sh 启动环境
3. 编辑 config.yaml 配置 API 密钥
4. 访问 http://localhost:8090 开始开发
5. 修改代码 → 自动热重载
6. 查看 DEV_GUIDE.md 了解详细信息
```

## 🐛 问题排查

1. **启动失败** → 查看 [DEV_GUIDE.md#常见问题](DEV_GUIDE.md#常见问题)
2. **端口冲突** → 修改 config.yaml 或终止占用进程
3. **依赖问题** → 使用国内镜像或清理重装
4. **Docker 问题** → 检查 Docker 状态或清理容器

## 📞 获取帮助

- 查看 [DEV_GUIDE.md](DEV_GUIDE.md) 的常见问题部分
- 检查 GitHub Issues
- 查看项目 README.md

---

**快速开始**：运行 `start-all.bat` (Windows) 或 `./start-all.sh` (Linux/Mac)
