# Xuni 供应链智能调度平台 v3.0 — 完整项目文档

> **技术栈**：Python FastAPI + React 18 | 阿里云百炼 AI | Qdrant RAG | LangGraph Agent | 三层记忆架构

---

## 一、项目概述

Xuni 是一款面向供应链管理的**企业级 AI Agent 平台**，核心能力包括：

- 🧠 **多 Agent 协作调度**：6 大 AI Agent 通过 LangGraph 编排，自动完成需求预测→库存检查→优化→调度→成本→风险→执行的完整链路
- 📚 **RAG 知识库**：Qdrant 向量数据库 + 智能分块 + 混合检索，支撑语义搜索和知识问答
- 🔧 **自然语言操作数据库**：聊天窗口直接说"帮我查低库存商品"/"给北京仓入库100件iPhone"
- 🎙️ **全模态交互**：文本 + 语音转文字 + 图片解析（qwen3.5-omni-plus）
- 🧊 **三层记忆体系**：工作记忆（LangGraph State）+ 短期记忆（Redis+PG）+ 长期记忆（Qdrant语义搜索）
- 🎨 **现代科技风 UI**：深蓝暗色主题、粒子背景动画、毛玻璃卡片、流畅过度动效

---

## 二、架构总览

```
┌─────────────────────────────────────────────────────────────────┐
│                       Frontend (React 18 + Vite)                │
│  GlassLayout → SideMenu → ChatUI · Dashboard · Tables · Workflow│
│  framer-motion · Ant Design 5 · ECharts · TechBackground        │
├─────────────────────────────────────────────────────────────────┤
│                    Backend (FastAPI + Uvicorn)                   │
│                                                                  │
│  ┌──────────┐  ┌──────────────┐  ┌──────────────────────────┐  │
│  │ REST API │  │ AI Services   │  │ LangGraph Workflow       │  │
│  │ auth     │  │ bailian_client│  │ StateGraph (8 nodes)     │  │
│  │ user     │  │ agents (6)    │  │ · demand_forecast        │  │
│  │ order    │  │ orchestrator  │  │ · inventory_check (tool) │  │
│  │ inventory│  │ rag_service   │  │ · inventory_optimization │  │
│  │ schedule │  │               │  │ · scheduling_decision    │  │
│  │ fulfill  │  └──────────────┘  │ · cost_optimization      │  │
│  │ supplier │                    │ · risk_control            │  │
│  │ report   │  ┌──────────────┐  │ · execution_control      │  │
│  │ ai/chat  │  │ Memory System │  │ · summary                │  │
│  └──────────┘  │ short_term    │  └──────────────────────────┘  │
│                │ long_term     │                                 │
│                │ memory_manager│                                 │
│                └──────────────┘                                 │
├─────────────────────────────────────────────────────────────────┤
│                  Infrastructure (Docker)                        │
│  PostgreSQL 16  ·  Redis 7  ·  Qdrant 1.x                      │
└─────────────────────────────────────────────────────────────────┘
```

### 目录结构（核心文件）

```
scheduling_platform/
├── backend/
│   ├── app/
│   │   ├── api/                    # REST API 路由层 (10个模块)
│   │   │   ├── ai.py               # AI 聊天/工作流/记忆/多模态 (20+ 端点)
│   │   │   ├── auth.py             # JWT 认证 (login/register/refresh)
│   │   │   ├── report.py           # 数据报表 (实时数据库查询)
│   │   │   └── ...
│   │   ├── services/
│   │   │   ├── ai/
│   │   │   │   ├── bailian_client.py  # 百炼 SDK 封装 (LLM+Embedding)
│   │   │   │   ├── agents.py          # 6 大 Agent 定义
│   │   │   │   └── agent_orchestrator.py # Agent 编排器
│   │   │   ├── langgraph/
│   │   │   │   ├── workflow.py     # 工作流编译与执行
│   │   │   │   ├── nodes.py        # 8 个节点定义
│   │   │   │   ├── state.py        # 状态 TypedDict
│   │   │   │   └── tools.py        # 11 个业务工具 (@tool)
│   │   │   ├── rag/
│   │   │   │   ├── qdrant_store.py # Qdrant 客户端
│   │   │   │   ├── retriever.py    # 多路召回 + 重排序
│   │   │   │   ├── text_processor.py # 智能分块
│   │   │   │   ├── rag_service.py  # RAG 增强生成
│   │   │   │   └── knowledge_base.py # 知识库管理
│   │   │   └── memory/              # ★ 三层记忆体系 (v3.0)
│   │   │       ├── memory_manager.py # 统一协调器
│   │   │       ├── short_term.py     # 短期记忆 (Redis+PG)
│   │   │       ├── long_term.py      # 长期记忆 (PG+Qdrant)
│   │   │       └── models.py         # 记忆表模型
│   │   ├── models/                  # SQLAlchemy ORM
│   │   ├── schemas/                 # Pydantic 数据结构
│   │   └── core/                    # 配置/数据库/中间件/安全
│   ├── alembic/                     # 数据库迁移
│   ├── .env                         # 环境变量 (API密钥等)
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── layout/GlassLayout.jsx  # 主布局 (深蓝科技风)
│   │   │   ├── chat/ChatUI.jsx         # 聊天组件 (语音/图片/流式)
│   │   │   └── common/                 # 共享组件库
│   │   │       ├── StatCard.jsx        # 动效指标卡片
│   │   │       ├── TechBackground.jsx  # Canvas 粒子背景
│   │   │       ├── AnimatedCounter.jsx # 数字递增动画
│   │   │       └── ...
│   │   ├── modules/                 # 业务模块 (9 个)
│   │   ├── services/api/            # API 封装层
│   │   ├── hooks/                   # usePersistedState 等
│   │   └── store/authStore.js       # Zustand 状态管理
│   ├── vite.config.js
│   └── package.json
└── docker/
```

---

## 三、三层记忆体系 (v3.0 核心架构)

| 层级 | 存储 | 用途 | 关键实现 |
|------|------|------|----------|
| **工作记忆** | LangGraph State + PostgresSaver Checkpointer | Agent 执行状态管理，支持断点续跑 | `workflow.py` → `PostgresSaver.from_conn_string()` |
| **短期记忆** | Redis (热缓存) + PostgreSQL (持久化) | 多轮对话上下文，滑动窗口+摘要压缩 | `short_term.py` → Redis TTL 24h + PG 全量 |
| **长期记忆** | PostgreSQL (结构化) + Qdrant (向量语义) | 用户画像、历史经验检索、个性化推荐 | `long_term.py` → Embedding → Qdrant.search() |

### 记忆 API

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/ai/memory/summary` | 三层记忆概览 |
| GET | `/api/ai/memory/preferences` | 用户偏好 |
| PUT | `/api/ai/memory/preferences` | 保存偏好 |
| POST | `/api/ai/memory/search` | 语义检索历史经验 |

---

## 四、LangGraph 工作流

### 节点流程

```
ENTRY → demand_forecast → inventory_check → inventory_optimization
       → scheduling_decision → cost_optimization → risk_control
       → [should_replan?]
           ├─ replan → back to scheduling_decision (循环最多3次)
           └─ continue → execution_control
                          → [should_call_tool?]
                              ├─ call_tool → tool_execution → back to execution_control
                              └─ finish → summary → END
```

### 关键条件分支

- **should_replan**：风险等级="high" 且迭代<3 → 回到调度决策重规划
- **should_call_tool**：执行计划含"库存/订单/供应商"关键词 → 调用数据库工具

### 可用工具 (11个)

| 工具 | 功能 | 类型 |
|------|------|------|
| `query_inventory` | 查询库存列表 (支持多条件筛选) | 查询 |
| `query_low_stock` | 低库存商品查询 | 查询 |
| `query_inventory_stats` | 库存统计 (总数/低库存/缺货/积压) | 查询 |
| `query_orders` | 订单查询 (状态/客户/关键词) | 查询 |
| `query_order_stats` | 订单统计 (各状态数量) | 查询 |
| `query_suppliers` | 供应商查询 | 查询 |
| `stock_in_operation` | 入库操作 (增量+状态更新) | 写入 |
| `stock_out_operation` | 出库操作 (减量+状态更新) | 写入 |
| `create_order_operation` | 创建新订单 | 写入 |
| `update_order_status_operation` | 更新订单状态 | 写入 |
| `cancel_order_operation` | 取消订单 | 写入 |

---

## 五、API 接口清单

### 认证 (3 端点)
- `POST /api/auth/login` — 登录获取 JWT
- `POST /api/auth/register` — 注册
- `POST /api/auth/refresh` — 刷新 Token

### 业务模块 (30+ 端点)

| 模块 | 前缀 | CRUD 端点 |
|------|------|-----------|
| 用户管理 | `/api/users` | GET list / GET id / POST / PUT / DELETE |
| 订单管理 | `/api/orders` | GET list / GET id / POST / PUT / DELETE / GET stats |
| 库存管理 | `/api/inventory` | GET list / GET id / POST / PUT / POST stock-in / POST stock-out / GET alerts |
| 调度中心 | `/api/scheduling` | GET list / GET id / POST / PUT status / POST ai-suggest |
| 履约管理 | `/api/fulfillment` | GET list / GET id / POST / PUT status / PUT tracking |
| 供应商管理 | `/api/suppliers` | GET list / GET id / POST / PUT / DELETE |
| 数据报表 | `/api/reports` | GET dashboard / GET order-trend / GET inventory-overview / GET ai-usage |

### AI 智能服务 (25 端点)

| 类别 | 端点 | 说明 |
|------|------|------|
| 对话 | `POST /api/ai/chat` | 基础对话 |
| 对话 | `POST /api/ai/chat/smart` | 智能聊天 (工具调用+记忆) |
| 对话 | `POST /api/ai/chat/stream` | 流式对话 (SSE) |
| 对话 | `POST /api/ai/chat/context` | 获取上下文 |
| Agent | `POST /api/ai/agent/{id}` | 单 Agent 调用 |
| Agent | `POST /api/ai/pipeline` | 流水线编排 |
| Agent | `POST /api/ai/parallel` | 并行调用 |
| 工作流 | `POST /api/ai/workflow/scheduling` | 调度工作流 (LangGraph) |
| 记忆 | `GET /api/ai/sessions` | 会话列表 |
| 记忆 | `GET /api/ai/sessions/{id}` | 会话详情 |
| 记忆 | `DELETE /api/ai/sessions/{id}` | 删除会话 |
| 记忆 | `GET /api/ai/memory/summary` | 记忆概览 |
| 记忆 | `GET/PUT /api/ai/memory/preferences` | 偏好管理 |
| 记忆 | `POST /api/ai/memory/search` | 经验检索 |
| 工具 | `GET /api/ai/tools` | 工具列表 |
| 多模态 | `POST /api/ai/transcribe` | 语音转文字 |
| 多模态 | `POST /api/ai/analyze-image` | 图片解析 |
| 文件 | `POST /api/ai/upload` | 文件上传 |

### 知识库 (12 端点)
- `GET /api/knowledge/documents` — 文档列表
- `POST /api/knowledge/documents` — 添加文档 (含智能分块+向量化)
- `DELETE /api/knowledge/documents/{id}` — 删除文档
- `POST /api/knowledge/rag/query` — RAG 检索增强生成
- `POST /api/knowledge/decisions/search` — 决策历史搜索

---

## 六、前端页面模块

| 页面 | 路由 | 功能 |
|------|------|------|
| 登录页 | `/login` | 深蓝科技风 + 粒子背景 |
| 仪表盘 | `/dashboard` | 8 个动效 StatCard + ECharts 图表 (实时数据) |
| 订单管理 | `/orders` | Table CRUD + 搜索筛选 + 状态流转 |
| 库存管理 | `/inventory` | Table CRUD + 入库/出库操作 |
| 调度中心 | `/scheduling` | Table CRUD + AI 调度建议 |
| 履约管理 | `/fulfillment` | Table CRUD + 物流追踪 |
| 供应商管理 | `/suppliers` | Table CRUD + 评级查看 |
| 数据报表 | `/reports` | 实时统计报表 |
| AI 智能看板 | `/ai-dashboard` | 6 Agent 调用界面 |
| Agent 工作流编排 | `/ai-workflow` | 聊天 + LangGraph 工作流触发 |
| RAG 知识库 | `/knowledge` | 文档管理 + 语义检索 + RAG 问答 |
| 用户管理 | `/system/users` | 用户 CRUD + 角色管理 |

---

## 七、部署与启动

### 前置依赖

```bash
# Docker 部署数据库
docker run -d --name pg -p 5432:5432 -e POSTGRES_PASSWORD=postgres postgres:16
docker run -d --name redis -p 6379:6379 redis:7
docker run -d --name qdrant -p 6333:6333 qdrant/qdrant
```

### 后端

```bash
cd backend
pip install -r requirements.txt   # 使用 .venv 虚拟环境
# 编辑 .env 配置 BAILIAN_API_KEY=你的密钥
python start.py
# 或: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 前端

```bash
cd frontend
npm install
npm run dev    # http://localhost:3000
```

### 登录
- **管理员**：admin / admin123
- **操作员**：operator / admin123

---

## 八、关键技术决策

| 决策 | 选择 | 原因 |
|------|------|------|
| Web 框架 | FastAPI | 原生 async、自动 OpenAPI 文档、性能优异 |
| AI SDK | DashScope (百炼) | qwen3.5-omni-plus 全模态，单 SDK 覆盖 LLM+Embedding+多模态 |
| Agent 编排 | LangGraph | 有向图+条件分支+循环迭代，PostgresSaver 持久化 |
| 向量数据库 | Qdrant | REST/gRPC 双协议、COSINE 距离、过滤检索 |
| ORM | SQLAlchemy 2.0 async | 成熟的异步 ORM，原生 asyncio 支持 |
| 前端组件库 | Ant Design 5 | 企业级组件体系、丰富表单/表格/图表生态 |
| 动画 | framer-motion | 声明式动画 API，与 React 深度集成 |
| 状态管理 | Zustand | 极简 API、无 boilerplate、支持持久化 |

---

## 九、变更记录

| 版本 | 日期 | 内容 |
|------|------|------|
| v3.0 | 2026-06-30 | 三层记忆体系、现代科技风 UI 重设计、framer-motion 动效、粒子背景、全模块功能修复、文档重写 |
| v2.2 | 2026-06-29 | Repository Pattern、统一异常处理、Docker 容器化 |
| v2.0 | 2026-06-27 | LangGraph 工作流、全模态 AI、RAG 知识库 |
| v1.0 | 2026-06-25 | FastAPI+React 初始版本 |

---

*文档最后更新：2026-06-30 · 版本 v3.0*
