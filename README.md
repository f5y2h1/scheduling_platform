# 🚀 Xuni 供应链智能调度平台

> **v2.1.0** | Python FastAPI + React 18 | 阿里云百炼 AI | Qdrant RAG | Repository Pattern

面向供应链管理的智能调度平台，集成**阿里云百炼通义千问**和 **Qdrant 向量数据库**，实现从需求预测到执行管控的全链路 AI 辅助决策。

---

## ✨ 核心特性

### 架构升级 (v2.1)
- 🏗️ **Repository Pattern** — 数据访问层与业务逻辑分离，代码更易测试和维护
- 🎯 **统一异常处理** — 全局异常捕获，标准化错误响应格式
- 🐳 **Docker 容器化** — PostgreSQL、Redis、Qdrant 一键部署
- 📦 **Alembic 迁移** — 数据库 Schema 版本化管理
- ⚓ **Hooks 架构** — 自定义 useAuth / useTable / useModal 逻辑复用
- 🎨 **共享组件库** — StatCard / StatusTag / FormModal / SearchBar 等开箱即用

### AI 能力
- 🧠 **6大AI Agent** — 需求预测/库存优化/调度决策/成本优化/风险控制/执行管控
- 📚 **RAG 知识库** — Qdrant 向量检索 + 百炼 Embedding + LLM Rerank
- 🔀 **多策略检索** — 语义检索 + 分类过滤 + 决策回放 + 规则匹配

### UI/UX
- 🎨 **精致UI** — React 18 + Ant Design 5 + ECharts 深色侧边栏
- 📱 **响应式布局** — 支持桌面、平板、移动端
- ⚡ **快速构建** — Vite + 热更新，开发体验极佳

---

## 🏗️ 技术栈

| 层级 | 技术 | 版本 | 新增 |
|------|------|------|------|
| **前端框架** | React 18 | 18.3 | |
| **UI 组件库** | Ant Design 5 | 5.21 | |
| **状态管理** | Zustand | 5.0 | ⭐ |
| **构建工具** | Vite | 5.4 | |
| **图表库** | ECharts 5 | 5.5 | |
| **后端框架** | FastAPI (异步) | 0.115 | |
| **ORM** | SQLAlchemy 2.0 | 2.0.36 | |
| **数据库迁移** | Alembic | 1.14.0 | ⭐ |
| **数据库** | PostgreSQL | 16.4 | Docker |
| **缓存** | Redis | 7.4 | Docker |
| **向量库** | Qdrant | 1.11.5 | Docker |
| **AI LLM** | 百炼 DashScope | 1.21.3 | |
| **认证** | JWT | 3.3 | |

---

## 🚀 快速开始

### 1. Docker 数据库启动
```powershell
cd d:\xuni\scheduling_platform\docker
docker-compose up -d
```

### 2. 后端启动 (PyCharm)
```powershell
cd backend

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 填写数据库和百炼API密钥

# 数据库迁移
alembic upgrade head

# 启动服务
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

### 3. 前端启动 (PyCharm)
```powershell
cd frontend
npm install
npm run dev
```

**访问地址:**
- 前端: http://localhost:3000
- 后端 API: http://localhost:8080
- API 文档: http://localhost:8080/docs

**默认账号:** `admin` / `admin123`

---

## 📂 项目结构

```
scheduling_platform/
├── backend/                    # Python FastAPI
│   ├── app/
│   │   ├── main.py             # 入口 + 路由注册
│   │   ├── core/               # 核心模块 ⭐
│   │   │   ├── config.py       # Pydantic Settings
│   │   │   ├── database.py     # SQLAlchemy 异步引擎
│   │   │   ├── security.py     # JWT 认证
│   │   │   ├── logger.py       # loguru 日志
│   │   │   ├── exceptions.py   # 统一异常处理 ⭐
│   │   │   └── middleware.py   # 请求日志中间件 ⭐
│   │   ├── models/             # SQLAlchemy ORM 模型
│   │   ├── schemas/            # Pydantic 请求/响应模型
│   │   ├── repositories/       # Repository 数据访问层 ⭐
│   │   │   └── base_repository.py
│   │   ├── api/                # 10个 API 路由
│   │   ├── services/           # 业务逻辑层
│   │   │   ├── ai/             # 百炼 + 6个Agent
│   │   │   └── rag/            # Qdrant + RAG检索
│   │   └── utils/              # 工具函数
│   ├── alembic/                # Alembic 迁移 ⭐
│   ├── requirements.txt
│   └── .env.example
├── frontend/                   # React 18
│   ├── src/
│   │   ├── components/          # 共享组件库 ⭐
│   │   │   └── common/         # 通用组件
│   │   ├── hooks/             # 自定义 Hooks ⭐
│   │   ├── modules/           # 页面模块 (按功能域)
│   │   ├── services/          # API 服务
│   │   ├── store/             # Zustand 状态
│   │   └── utils/             # 工具函数
│   ├── package.json
│   └── vite.config.js
├── docker/                     # Docker Compose ⭐
│   └── docker-compose.yml      # PostgreSQL + Redis + Qdrant
└── docs/                       # 文档
    ├── ARCHITECTURE.md         # 架构设计 (v2.1)
    ├── DEPLOY.md               # 部署指南
    ├── CONFIG.md               # 配置说明
    └── DEPENDENCIES.md         # 依赖清单
```

---

## 🎨 共享组件 (Components)

| 组件 | 说明 | 特性 |
|------|------|------|
| `StatCard` | 统计卡片 | 数值/趋势/图标/颜色 |
| `StatusTag` | 状态标签 | 内置映射 + 自定义映射 |
| `FormModal` | 表单弹窗 | Form.Item 组合模式 |
| `SearchBar` | 搜索栏 | 关键词 + 筛选器 |
| `ActionButtons` | 操作按钮组 | 自动适配按钮数量 |
| `PageHeader` | 页面头部 | 标题 + 面包屑 + 扩展区 |

## ⚓ 自定义 Hooks

| Hook | 说明 | 返回值 |
|------|------|--------|
| `useAuth` | 认证管理 | user, token, login, logout, isAuthenticated |
| `useTable` | 表格分页 | data, loading, pagination, handleChange, refresh |
| `useModal` | 弹窗状态 | visible, editingId, form, show, hide, confirm |

---

## 🧠 AI 与 RAG

### 6大 Agent

| Agent | 功能 | 知识库分类 |
|-------|------|-----------|
| 💡 需求预测 | 销量预测、趋势分析 | 需求预测 |
| 📦 库存优化 | 安全库存、补货方案 | 库存策略 |
| 📋 调度决策 | 多仓分配、路径规划 | 调度规则 |
| 💰 成本优化 | 方案核算、对比推荐 | 成本优化 |
| 🛡️ 风险控制 | 风险识别、预警处置 | 风险规则 |
| 🎯 执行管控 | 任务下发、状态跟踪 | 执行管控 |

### RAG 检索管道

```
文档入库: 文本 → 智能分块(800字) → Embedding → Qdrant

检索: 查询 → Embedding → 多路召回
        ├─ 语义检索 (Cosine Top-K)
        ├─ 决策历史 (相似场景)
        └─ 业务规则 (规则库匹配)
      → 去重合并 → LLM Rerank → Top-K → 增强生成
```

### 支持的模型

`qwen-plus` / `qwen-max` / `qwen-turbo` / `qwen2.5-72b` / `qwen2.5-32b` / `qwen2.5-14b` / `qwen2.5-7b`

---

## 📖 文档

| 文档 | 说明 |
|------|------|
| [架构设计](docs/ARCHITECTURE.md) | 系统架构、Repository Pattern、Hooks 设计 |
| [部署指南](docs/DEPLOY.md) | 从零到运行（含 PyCharm 配置）|
| [配置说明](docs/CONFIG.md) | 全部配置项详解 |
| [依赖清单](docs/DEPENDENCIES.md) | 所有第三方库说明 |

---

## ⚠️ 注意事项

1. **Python 版本**: 3.11 或 3.12
2. **必须配置百炼 API Key**: 编辑 `backend/.env` → `BAILIAN_API_KEY=sk-xxx`
3. **Docker Desktop 需运行**: PostgreSQL、Redis、Qdrant
4. **首次启动自动初始化**: 默认知识库（5篇供应链文档）
5. **生产环境**: 请修改 JWT Secret 和数据库密码

---

## 更新日志

### v2.1.0 (2026-06-28)
- ✨ 新增 Repository Pattern 数据访问层
- ✨ 新增统一异常处理机制
- ✨ 新增自定义 Hooks (useAuth/useTable/useModal)
- ✨ 新增共享组件库 (StatCard/StatusTag/FormModal 等)
- ✨ 新增 Docker Compose 容器化部署
- ✨ 新增 Alembic 数据库迁移支持
- 🎨 重构 Dashboard / UserManagement / OrderManagement / InventoryManagement 页面

---

MIT License © 2026 Xuni Team
