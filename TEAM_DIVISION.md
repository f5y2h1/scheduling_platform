# 供应链智能调度平台 - 团队分工文档

## 一、项目概述

本项目是一个基于 **FastAPI + React** 的供应链智能调度平台，核心功能包括：
- AI智能助手（支持自然语言对话、工具调用、工作流编排）
- 库存管理、订单管理、供应商管理
- 智能调度与履约管理
- 报表中心与数据分析
- 知识管理与检索（RAG）

## 二、团队成员与分工

### 成员 A：后端核心开发

**职责范围**：后端基础架构、核心业务API、数据库设计、权限认证

#### 负责模块

| 模块 | 路径 | 职责描述 |
|------|------|----------|
| 认证授权 | `backend/app/api/auth.py` | 用户登录、Token认证、权限校验 |
| 用户管理 | `backend/app/api/user.py` | 用户CRUD、角色管理 |
| 库存管理 | `backend/app/api/inventory.py` | 库存查询、入库/出库操作 |
| 订单管理 | `backend/app/api/order.py` | 订单创建、状态流转、查询 |
| 供应商管理 | `backend/app/api/supplier.py` | 供应商CRUD、评级管理 |
| 履约管理 | `backend/app/api/fulfillment.py` | 履约任务管理、执行追踪 |
| 报表中心 | `backend/app/api/report.py` | 数据统计、报表生成 |
| 数据库模型 | `backend/app/models/` | 所有业务表模型定义 |
| 数据仓库 | `backend/app/repositories/` | 数据访问层实现 |
| API接口定义 | `backend/app/schemas/` | 请求/响应数据结构 |
| 核心配置 | `backend/app/core/` | 配置管理、数据库连接、日志 |

#### 关键技术栈
- FastAPI、SQLAlchemy、Alembic（数据库迁移）
- JWT Token认证、OAuth2
- PostgreSQL数据库

---

### 成员 B：AI与智能模块开发

**职责范围**：AI集成、LangGraph工作流、工具调用、RAG知识检索

#### 负责模块

| 模块 | 路径 | 职责描述 |
|------|------|----------|
| AI聊天接口 | `backend/app/api/ai.py` | 智能聊天、流式对话、多模态处理 |
| 百炼客户端 | `backend/app/services/ai/bailian_client.py` | 阿里云百炼API封装、工具调用 |
| Agent编排 | `backend/app/services/ai/agent_orchestrator.py` | 多Agent协作调度 |
| LangGraph工作流 | `backend/app/services/langgraph/workflow.py` | 工作流定义、条件分支、循环 |
| 工作流节点 | `backend/app/services/langgraph/nodes.py` | 需求预测、库存检查、调度决策等节点 |
| 业务工具 | `backend/app/services/langgraph/tools.py` | 数据库操作工具（库存查询、订单查询等） |
| RAG服务 | `backend/app/services/rag/rag_service.py` | 知识检索、向量数据库操作 |
| 知识库管理 | `backend/app/api/knowledge.py` | 知识库CRUD、文档上传 |
| 调度API | `backend/app/api/scheduling.py` | 调度任务管理、工作流触发 |

#### 关键技术栈
- 阿里云百炼API（通义千问）
- LangGraph（工作流引擎）
- LangChain（工具调用）
- Qdrant（向量数据库）
- RAG检索增强生成

---

### 成员 C：前端开发

**职责范围**：前端页面开发、组件设计、用户交互、UI优化

#### 负责模块

| 模块 | 路径 | 职责描述 |
|------|------|----------|
| 布局组件 | `frontend/src/components/layout/` | MainLayout、HeaderBar、SideMenu |
| AI仪表盘 | `frontend/src/modules/ai-dashboard/` | AgentWorkflow、AIDashboard、KnowledgeManagement |
| 库存管理页 | `frontend/src/modules/inventory/` | 库存列表、出入库操作 |
| 订单管理页 | `frontend/src/modules/order/` | 订单列表、状态管理 |
| 供应商管理页 | `frontend/src/modules/supplier/` | 供应商列表、评级管理 |
| 调度中心 | `frontend/src/modules/scheduling/` | 调度任务、工作流执行 |
| 履约管理页 | `frontend/src/modules/fulfillment/` | 履约任务追踪 |
| 报表中心 | `frontend/src/modules/report/` | 数据可视化、报表展示 |
| 系统管理 | `frontend/src/modules/system/` | 登录页、用户管理 |
| 聊天组件 | `frontend/src/components/chat/ChatUI.jsx` | AI对话界面、工具调用展示 |
| 公共组件 | `frontend/src/components/common/` | StatCard、SearchBar、FormModal等 |
| API服务 | `frontend/src/services/api/` | 前端API调用封装 |
| Mock数据 | `frontend/src/services/mock/` | 开发环境模拟数据 |

#### 关键技术栈
- React、Vite
- Ant Design（UI组件库）
- React Router（路由管理）
- Zustand（状态管理）

---

## 三、协作规则

### 1. 代码规范
- 后端：遵循PEP8规范，使用类型注解
- 前端：使用ESLint，遵循React Hooks规范
- 统一使用英文命名（变量、函数、文件名）

### 2. 分支策略
- `main`：生产分支，仅用于发布
- `develop`：开发主分支
- `feature/{模块}-{功能}`：功能开发分支（如 `feature/ai-tool-calling`）

### 3. 沟通机制
- 每日站会：同步进度、阻塞问题
- 需求评审：新功能开发前确认需求
- Code Review：PR合并前必须经过至少1人审核

### 4. 接口协作
- 后端先定义API接口文档，前端根据文档开发
- 接口变更需提前通知相关人员
- 使用Postman/OpenAPI文档作为接口契约

## 四、任务优先级建议

### 第一阶段：核心功能
1. 用户认证系统（成员A）
2. 基础数据模型与CRUD（成员A）
3. AI聊天基础功能（成员B）
4. 主页面布局与导航（成员C）

### 第二阶段：智能功能
1. LangGraph工作流（成员B）
2. 工具调用系统（成员B）
3. AI仪表盘页面（成员C）
4. 库存/订单/供应商管理（成员A）

### 第三阶段：高级功能
1. RAG知识检索（成员B）
2. 报表中心（成员A+C）
3. 调度与履约（成员A+B）
4. UI优化与响应式适配（成员C）

## 五、技术架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                        前端层 (成员C)                            │
│  React + Ant Design + Vite                                      │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐              │
│  │ AI助手   │ │ 库存管理 │ │ 订单管理 │ │ 供应商   │ ...         │
│  └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘              │
└───────┼───────────┼───────────┼───────────┼───────────────────┘
        │           │           │           │
        ▼           ▼           ▼           ▼
┌─────────────────────────────────────────────────────────────────┐
│                        后端层 (成员A)                            │
│  FastAPI + SQLAlchemy                                           │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐              │
│  │ Auth    │ │ Inventory│ │ Order   │ │ Supplier│ ...         │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘              │
└──────────────────────┬─────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                        AI层 (成员B)                              │
│  LangGraph + Bailian API + RAG                                  │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐            │
│  │ Workflow     │ │ Tool Calling │ │ RAG Service  │            │
│  │ (调度工作流) │ │ (数据库操作) │ │ (知识检索)   │            │
│  └──────────────┘ └──────────────┘ └──────────────┘            │
└─────────────────────────────────────────────────────────────────┘
```

## 六、附录

### 文件变更记录
| 文件 | 修改内容 | 修改人 |
|------|----------|--------|
| `backend/app/api/ai.py` | 新增 `/chat/smart` 智能聊天接口 | 成员B |
| `backend/app/services/ai/bailian_client.py` | 更新系统提示词，添加工具描述 | 成员B |
| `backend/app/services/langgraph/tools.py` | 定义业务工具（库存、订单等） | 成员B |
| `frontend/src/components/chat/ChatUI.jsx` | 调用智能聊天接口，展示工具调用结果 | 成员C |
| `frontend/src/modules/ai-dashboard/pages/AgentWorkflow.jsx` | 布局优化、滚动修复 | 成员C |

### 运行命令
```bash
# 后端启动
cd backend && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8080

# 前端启动
cd frontend && npm run dev

# 前端构建
cd frontend && npm run build

# 数据库迁移
cd backend && alembic upgrade head
```

---

**文档版本**: v1.0  
**创建日期**: 2026-06-30  
**适用项目**: 供应链智能调度平台
