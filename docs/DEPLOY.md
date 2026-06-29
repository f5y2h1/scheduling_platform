# 🚀 Xuni 供应链智能调度平台 —— 部署指南

> **版本**: v2.0.0 | **更新**: 2026-06-27 | **后端**: Python FastAPI | **数据库**: Docker

---

## 📋 目录

1. [环境要求](#环境要求)
2. [快速开始（三步启动）](#快速开始)
3. [详细步骤](#详细步骤)
4. [PyCharm 配置](#pycharm配置)
5. [验证部署](#验证部署)
6. [常见问题](#常见问题)

---

## <a id="环境要求"></a>🖥️ 环境要求

| 软件 | 版本 | 用途 |
|------|------|------|
| **Python** | **3.11+** | 后端语言 |
| **pip** | 23+ | Python 包管理 |
| **Node.js** | 20+ | 前端构建 |
| **Docker Desktop** | 24+ | 运行数据库/缓存/向量库 |
| **PyCharm** | 2024+ | IDE（用于运行后端） |

---

## <a id="快速开始"></a>⚡ 快速开始（三步启动）

### Step 1: Docker Desktop 启动数据库

```bash
cd scheduling_platform/docker

# 编辑 .env，填入百炼 API Key
# BAILIAN_API_KEY=sk-your-key

# 启动 PostgreSQL + Redis + Qdrant
docker-compose up -d
```

### Step 2: PyCharm 启动 Python 后端

```bash
cd scheduling_platform/backend

# 创建虚拟环境（PyCharm 自动识别）
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env .env.local
# 编辑 .env.local → BAILIAN_API_KEY=sk-xxx

# 启动
python -m app.main
```

### Step 3: 终端启动前端

```bash
cd scheduling_platform/frontend
npm install && npm run dev
```

### 访问

| 服务 | 地址 |
|------|------|
| 前端页面 | http://localhost:3000 |
| 后端API | http://localhost:8080 |
| **Swagger文档** | **http://localhost:8080/docs** |
| ReDoc文档 | http://localhost:8080/redoc |
| Qdrant面板 | http://localhost:6333/dashboard |

### 默认账号

| 用户名 | 密码 | 角色 |
|--------|------|------|
| `admin` | `admin123` | 管理员 |
| `operator` | `admin123` | 操作员 |

---

## <a id="详细步骤"></a>📦 详细步骤

### Docker 数据库服务

```bash
cd scheduling_platform/docker
docker-compose up -d

# 服务端口：
# PostgreSQL :5432
# Redis      :6379
# Qdrant     :6333 (REST) / :6334 (gRPC)
```

### Python 后端

```bash
cd scheduling_platform/backend
python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate       # macOS/Linux
pip install -r requirements.txt
python -m app.main
```

---

## <a id="pycharm配置"></a>🔧 PyCharm 配置

### 1. 打开项目

PyCharm → Open → 选择 `scheduling_platform/backend` 目录

### 2. 配置 Python 解释器

1. File → Settings → Project → Python Interpreter
2. Add Interpreter → Virtualenv Environment → New environment
3. Location: `backend/venv`
4. Base interpreter: **Python 3.11 或 3.12**
5. OK → PyCharm 自动安装 `requirements.txt` 依赖

### 3. 运行配置

1. 右上角 → Add Configuration → Python
2. Module name: `app.main`
3. Working directory: `backend/`
4. Environment variables: 可选，已从 `.env` 加载

### 4. 启动

点击绿色 ▶ 按钮即可运行，或使用终端 `python -m app.main`

---

## <a id="验证部署"></a>✅ 验证部署

```bash
# 健康检查
curl http://localhost:8080/api/health

# 登录
curl -X POST http://localhost:8080/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# Swagger 文档
open http://localhost:8080/docs

# Qdrant
curl http://localhost:6333/health

# RAG 测试
curl -X POST http://localhost:8080/api/knowledge/search/hybrid \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"query":"安全库存计算公式","top_k":3}'
```

---

## <a id="常见问题"></a>❓ 常见问题

### Q1: 用哪个 Python 版本？

**Python 3.11 或 3.12**。在 PyCharm → Settings → Project → Python Interpreter 中设置。

### Q2: pip install 报错？

```bash
# 升级 pip
python -m pip install --upgrade pip
# 使用阿里云镜像
pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
```

### Q3: Qdrant 连接失败？

确认 Docker Desktop 已启动，且 Qdrant 容器运行中。

### Q4: AI 功能报错？

确认已配置 `BAILIAN_API_KEY` 环境变量，百炼控制台 API Key 有效。

### Q5: 数据库连接失败？

Docker Desktop 中检查 PostgreSQL 容器是否运行：
```bash
docker ps | grep postgres
```
