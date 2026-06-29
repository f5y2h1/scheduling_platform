# 📦 Xuni 供应链智能调度平台 —— 依赖清单

> **Python 3.11+** | 相当于 `requirements.txt` 的详细说明

---

## 后端依赖（Python / pip）

> 配置文件：`backend/requirements.txt`
> Python 版本：**3.11 或 3.12**

### 安装命令

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 完整依赖列表

| 依赖 | 版本 | 用途 |
|------|------|------|
| **Web 框架** | | |
| fastapi | 0.115.6 | 高性能异步 Web 框架 |
| uvicorn[standard] | 0.34.0 | ASGI 服务器 |
| **数据库** | | |
| sqlalchemy[asyncio] | 2.0.36 | 异步 ORM |
| asyncpg | 0.30.0 | PostgreSQL 异步驱动 |
| psycopg2-binary | 2.9.10 | PostgreSQL 同步驱动 |
| alembic | 1.14.0 | 数据库迁移工具 |
| **缓存** | | |
| redis | 5.2.1 | Redis 客户端 |
| **认证** | | |
| python-jose[cryptography] | 3.3.0 | JWT Token |
| passlib[bcrypt] | 1.7.4 | 密码哈希 |
| python-multipart | 0.0.18 | 表单解析 |
| **数据验证** | | |
| pydantic | 2.10.3 | 数据模型校验 |
| pydantic-settings | 2.7.0 | 环境变量加载 |
| **AI / 百炼** | | |
| dashscope | 1.21.3 | 阿里云百炼 SDK |
| **向量数据库** | | |
| qdrant-client | 1.12.2 | Qdrant Python 客户端 |
| **工具** | | |
| httpx | 0.28.1 | HTTP 请求 |
| python-dotenv | 1.0.1 | .env 文件加载 |
| loguru | 0.7.3 | 日志库 |

---

## 前端依赖（JavaScript / npm）

> 配置文件：`frontend/package.json`
> Node.js 版本：**20+**

### 安装命令

```bash
cd frontend
npm install
```

### 运行时依赖

| 依赖 | 版本 | 用途 |
|------|------|------|
| react | ^18.3.1 | UI 框架 |
| react-dom | ^18.3.1 | React DOM |
| react-router-dom | ^6.26.2 | 路由 |
| antd | ^5.21.4 | UI 组件库 |
| @ant-design/icons | ^5.5.1 | 图标 |
| axios | ^1.7.7 | HTTP 请求 |
| zustand | ^5.0.0 | 状态管理 |
| echarts | ^5.5.1 | 数据可视化 |
| echarts-for-react | ^3.0.2 | ECharts React |
| dayjs | ^1.11.13 | 日期处理 |
| recharts | ^2.13.0 | React 图表 |

### 开发依赖

| 依赖 | 版本 |
|------|------|
| vite | ^5.4.8 |
| @vitejs/plugin-react | ^4.3.2 |

---

## Docker 镜像

| 镜像 | 版本 | 用途 |
|------|------|------|
| postgres | 16.4-alpine | 业务数据库 |
| redis | 7.4-alpine | 缓存 |
| qdrant/qdrant | v1.11.5 | 向量数据库 |

---

> 📝 所有依赖均为 2026 年较稳定版本
