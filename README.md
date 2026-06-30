# 🚀 Xuni 供应链智能调度平台 v3.0

> **企业级 AI Agent 平台** | FastAPI + React 18 | 阿里云百炼 | LangGraph | Qdrant | 三层记忆架构

<p align="center">
  <img src="https://img.shields.io/badge/version-3.0.0-blue" alt="version">
  <img src="https://img.shields.io/badge/python-3.12+-green" alt="python">
  <img src="https://img.shields.io/badge/node-18+-green" alt="node">
  <img src="https://img.shields.io/badge/license-MIT-blue" alt="license">
</p>

---

## 📸 项目预览

基于 React 18 + Ant Design 5 + framer-motion 的现代科技风 UI，深蓝暗色主题 + Canvas 粒子背景 + 毛玻璃卡片效果。

---

## ✨ 核心特性

### 🧠 多 Agent 智能调度
- **6 大 AI Agent**：需求预测 / 库存优化 / 调度决策 / 成本优化 / 风险控制 / 执行管控
- **LangGraph 工作流**：8 节点 DAG + 条件分支 + 循环迭代（风险过高自动重规划）
- **PostgresSaver Checkpointer**：状态持久化，支持断点续跑

### 📚 RAG 知识库
- 智能分块（标题/段落/列表感知） + MD5 去重
- 混合检索：语义（Qdrant）+ 关键词（BM25） → LLM 增强生成
- 文档管理：上传 → 分块 → 向量化 → 入库 全自动

### 🔧 自然语言操作数据库
```
"查询所有低于安全库存的商品"   → query_low_stock()
"给北京仓入库100件华为Mate70"  → stock_in_operation(1, 100)
"创建订单：客户张三买10台iPhone发往上海" → create_order_operation(...)
```

### 🧊 企业级三层记忆

| 层级 | 技术 | 作用 |
|------|------|------|
| 工作记忆 | LangGraph State + PostgresSaver | Agent 执行状态持久化 |
| 短期记忆 | Redis + PostgreSQL | 多轮对话上下文 / Session 隔离 |
| 长期记忆 | PostgreSQL + Qdrant | 用户画像 / 历史经验语义检索 |

---

## 🏗️ 技术栈

| 层 | 技术 |
|----|------|
| **AI / LLM** | qwen3.5-omni-plus · DashScope · LangGraph · LangChain |
| **后端** | Python 3.12 · FastAPI 0.115 · SQLAlchemy 2.0 · Uvicorn |
| **前端** | React 18 · Vite 5 · Ant Design 5 · framer-motion · ECharts |
| **存储** | PostgreSQL 16 · Redis 7 · Qdrant 1.x |
| **认证** | JWT · Passlib (pbkdf2_sha256) |
| **部署** | Docker Compose |

---

## 📦 快速部署

### 前提条件

- Python 3.12+
- Node.js 18+
- Docker（用于数据库容器）

### 第一步：启动数据库服务

```bash
# PostgreSQL
docker run -d --name postgres \
  -p 5432:5432 \
  -e POSTGRES_PASSWORD=postgres \
  postgres:16

# Redis
docker run -d --name redis \
  -p 6379:6379 \
  redis:7

# Qdrant 向量数据库
docker run -d --name qdrant \
  -p 6333:6333 -p 6334:6334 \
  qdrant/qdrant
```

> 也可以使用项目根目录的 `docker-compose.yml` 一键启动所有服务。

### 第二步：配置后端

```bash
# 克隆项目
git clone <your-repo-url>
cd scheduling_platform/backend

# 创建虚拟环境（推荐）
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# 或 .venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 配置 API 密钥（必须！）
# 编辑 backend/.env 文件，填写你的百炼 API Key：
# BAILIAN_API_KEY=sk-xxxxxxxxxxxxxxxx

# 启动后端服务
python start.py
# 或: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 访问 API 文档
# http://localhost:8000/docs
```

### 第三步：启动前端

```bash
cd scheduling_platform/frontend

# 安装依赖
npm install

# 开发模式启动
npm run dev

# 访问前端
# http://localhost:3000
```

### 第四步：登录

| 角色 | 用户名 | 密码 |
|------|--------|------|
| 管理员 | admin | admin123 |
| 操作员 | operator | admin123 |

---

## 📂 项目结构

```
scheduling_platform/
├── backend/
│   ├── app/
│   │   ├── api/                    # REST API (10 个模块, 60+ 端点)
│   │   │   ├── ai.py               # AI 聊天/工作流/记忆/多模态
│   │   │   ├── auth.py             # JWT 认证
│   │   │   ├── report.py           # 数据报表（真实 DB 查询）
│   │   │   └── ...
│   │   ├── services/
│   │   │   ├── ai/                 # 百炼客户端 + 6 Agent + 编排器
│   │   │   ├── langgraph/          # 工作流定义 + 8 节点 + 11 工具
│   │   │   ├── rag/                # Qdrant + 检索器 + 分块 + RAG
│   │   │   └── memory/             # 三层记忆体系
│   │   ├── models/                 # SQLAlchemy ORM (6 业务表 + 4 记忆表)
│   │   ├── schemas/                # Pydantic 数据模型
│   │   └── core/                   # 配置/数据库/中间件/安全
│   ├── .env                        # 环境变量（需自行创建配置）
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── layout/GlassLayout.jsx  # 深蓝科技风主布局
│   │   │   ├── chat/ChatUI.jsx         # 全模态聊天窗口
│   │   │   └── common/                 # StatCard · TechBackground · AnimatedCounter
│   │   ├── modules/                    # 12 个业务模块页面
│   │   ├── services/api/               # API 封装层
│   │   ├── hooks/                      # usePersistedState · useTable · useModal
│   │   └── store/authStore.js          # Zustand 状态管理
│   ├── vite.config.js
│   └── package.json
├── docker/                         # Docker 配置文件
├── PROJECT_DOCUMENTATION.md        # 完整项目文档
└── README.md
```

---

## 🔌 API 概览

| 模块 | 前缀 | 端点示例 |
|------|------|----------|
| 认证 | `/api/auth` | POST login / register / refresh |
| 用户管理 | `/api/users` | GET/POST/PUT/DELETE |
| 订单管理 | `/api/orders` | CRUD + stats |
| 库存管理 | `/api/inventory` | CRUD + stock-in/out + alerts |
| 调度中心 | `/api/scheduling` | CRUD + ai-suggest |
| 履约管理 | `/api/fulfillment` | CRUD + tracking |
| 供应商 | `/api/suppliers` | CRUD |
| 数据报表 | `/api/reports` | dashboard / trends / overview |
| AI 服务 | `/api/ai` | chat / workflow / memory / tools / multimodal |
| 知识库 | `/api/knowledge` | documents / search / RAG query |

完整 API 文档：启动后端后访问 `http://localhost:8000/docs`

---

## ⚙️ 环境变量

编辑 `backend/.env`：

```env
# 服务端口
PORT=8000
DEBUG=true

# PostgreSQL
DB_HOST=localhost
DB_PORT=5432
DB_NAME=scheduling_platform
DB_USER=postgres
DB_PASSWORD=postgres

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# Qdrant
QDRANT_HOST=localhost
QDRANT_REST_PORT=6333

# 百炼 AI（必填！）
BAILIAN_API_KEY=sk-xxxxxxxxxxxxxxxx

# JWT
JWT_SECRET=your-secret-key
```

---

## 🤝 贡献指南

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

---

## 📄 许可证

MIT License · © 2026 Xuni Team

---

*详细架构设计、技术决策、变更记录见 [PROJECT_DOCUMENTATION.md](./PROJECT_DOCUMENTATION.md)*
