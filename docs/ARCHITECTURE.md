# 🏗️ Xuni 供应链智能调度平台 —— 架构设计 v2.1

> Python FastAPI Edition | React 18 | Repository Pattern | Docker Containerized

---

## 总体架构

```
┌──────────────────────────────────────────────────────┐
│              访问层：React 18 + Ant Design 5            │
│    ┌─────────────┬──────────────┬──────────────────┐ │
│    │ 共享组件库   │ 自定义Hooks │ 模块化页面组件    │ │
│    │ StatCard    │ useAuth     │ Dashboard        │ │
│    │ StatusTag   │ useTable    │ UserManagement   │ │
│    │ FormModal   │ useModal    │ OrderManagement  │ │
│    │ SearchBar   │             │ InventoryManagement│ │
│    └─────────────┴──────────────┴──────────────────┘ │
├──────────────────────────────────────────────────────┤
│              接入层：Vite Proxy / Nginx                 │
├──────────────────────────────────────────────────────┤
│           服务层：Python FastAPI (异步)                  │
│  ┌────────────────────────────────────────────────┐  │
│  │              Repository Pattern                  │  │
│  │  BaseRepository<T> ──► 具体Repository继承       │  │
│  │    ├── get() / list() / create()               │  │
│  │    ├── update() / delete() / count()           │  │
│  └────────────────────────────────────────────────┘  │
│  ┌────────┬────────┬────────┬────────┬────────┐     │
│  │用户服务│订单服务│库存服务│调度服务│履约服务│     │
│  ├────────┼────────┼────────┼────────┼────────┤     │
│  │供应商  │报表服务│        │        │        │     │
│  └────────┴────────┴────────┴────────┴────────┘     │
├──────────────────────────────────────────────────────┤
│             AI能力层 (百炼 + Qdrant)                    │
│  ┌──────────────────────────────────────────────┐   │
│  │ BailianClient (LLM + Embedding)                │   │
│  │ 6 Agents (BaseAgent → 继承)                    │   │
│  │ AgentOrchestrator (单/流水线/并行)               │   │
│  │ QdrantVectorStore + KnowledgeBase + RAGService │   │
│  └──────────────────────────────────────────────┘   │
├──────────────────────────────────────────────────────┤
│         数据层：PostgreSQL + Redis + Qdrant            │
│              (Docker Compose 容器化部署)                │
└──────────────────────────────────────────────────────┘
```

---

## 技术栈

| 层 | 技术 | 版本 | 说明 |
|----|------|------|------|
| 后端框架 | FastAPI (异步) | 0.115 | ASGI 高性能异步框架 |
| ORM | SQLAlchemy 2.0 (async) | 2.0.36 | 异步数据库操作 |
| 数据库 | PostgreSQL | 16.4 | Docker 容器化部署 |
| 缓存 | Redis | 7.4 | Docker 容器化部署 |
| 向量库 | Qdrant | 1.11.5 | Docker 容器化部署 |
| 数据库迁移 | Alembic | 1.14.0 | Schema 版本化管理 |
| AI LLM | 百炼 DashScope | 1.21.3 | 通义千问系列模型 |
| AI Embedding | text-embedding-v2 | 1536维 | 文本向量化 |
| 认证 | python-jose (JWT) | 3.3 | Token 认证 |
| 前端框架 | React 18 | 18.3 | 函数式组件 + Hooks |
| UI 组件库 | Ant Design 5 | 5.21 | 企业级 UI 组件 |
| 状态管理 | Zustand | 5.0 | 轻量级状态管理 |
| 构建工具 | Vite | 5.4 | 快速开发构建 |
| 图表库 | ECharts 5 | 5.5 | 数据可视化 |
| 数据路由 | React Router 6 | 6.26 | SPA 路由管理 |

---

## 后端模块结构 (Repository Pattern)

```
backend/app/
├── main.py              # FastAPI 入口 + 路由注册
├── core/
│   ├── config.py        # Pydantic Settings（环境变量）
│   ├── database.py      # SQLAlchemy async engine + session
│   ├── security.py      # JWT create/verify
│   ├── logger.py        # loguru 日志
│   ├── exceptions.py    # 统一异常处理 (AppException)
│   └── middleware.py   # 请求日志 + 全局异常处理
├── models/              # SQLAlchemy ORM 模型
│   ├── user.py / order.py / inventory.py
│   ├── schedule_task.py / fulfillment.py / supplier.py
├── schemas/             # Pydantic 请求/响应模型
│   ├── __init__.py      # 统一导出所有 Schema
│   ├── common.py        # ApiResponse / PageResult
│   ├── auth.py          # LoginRequest / RegisterRequest
│   ├── user.py          # UserCreate / UserUpdate / UserResponse
│   ├── order.py         # OrderCreate / OrderUpdate / OrderResponse
│   └── ...
├── repositories/         # 数据访问层 (Repository Pattern) ⭐新增
│   ├── base_repository.py  # BaseRepository<T> 泛型基类
│   ├── user_repository.py  # UserRepository
│   ├── order_repository.py # OrderRepository
│   └── ...
├── services/
│   ├── ai/
│   │   ├── bailian_client.py    # 百炼 LLM+Embedding
│   │   ├── agents.py            # 6大Agent
│   │   └── agent_orchestrator.py # 编排引擎
│   ├── rag/
│   │   ├── qdrant_store.py      # Qdrant CRUD+检索
│   │   ├── knowledge_base.py    # 知识库管理+分块
│   │   └── rag_service.py       # RAG检索增强
│   └── ...                      # 业务服务层
├── api/                 # FastAPI Router
│   ├── auth.py / user.py / order.py / inventory.py
│   ├── scheduling.py / fulfillment.py / supplier.py
│   ├── report.py / ai.py / knowledge.py
└── utils/
    └── auth.py          # FastAPI Depends 认证
```

### Repository Pattern 核心实现

```python
# base_repository.py - 泛型 CRUD 基类
class BaseRepository(Generic[ModelType]):
    def __init__(self, model: type[ModelType], db: AsyncSession)
    async def get(self, id: int) -> Optional[ModelType]
    async def list(self, skip, limit, **filters) -> List[ModelType]
    async def create(self, obj: ModelType) -> ModelType
    async def update(self, id: int, data: dict) -> Optional[ModelType]
    async def delete(self, id: int) -> bool
    async def count(self, **filters) -> int
```

### 统一异常处理

```python
# exceptions.py
class AppException(Exception):
    def __init__(self, code: int = 500, message: str = "服务器内部错误")

class AuthenticationError(AppException):  # 401
class AuthorizationError(AppException):   # 403
class NotFoundError(AppException):        # 404
class ValidationError(AppException):      # 422
class BusinessError(AppException):        # 400
```

---

## 前端模块结构 (Hooks + Components)

```
frontend/src/
├── components/          # 共享组件库 ⭐新增
│   ├── common/           # 通用组件
│   │   ├── __init__.js  # 统一导出
│   │   ├── StatCard.jsx  # 统计卡片 (数值/趋势/图标)
│   │   ├── StatusTag.jsx # 状态标签 (支持自定义映射)
│   │   ├── FormModal.jsx # 表单弹窗 (Form.Item 组合)
│   │   ├── SearchBar.jsx # 搜索栏 (关键词+筛选)
│   │   ├── ActionButtons.jsx # 操作按钮组
│   │   └── PageHeader.jsx   # 页面头部 + 面包屑
│   └── layout/
│       ├── MainLayout.jsx   # 主布局
│       ├── SideMenu.jsx     # 侧边菜单
│       └── HeaderBar.jsx    # 顶部导航
├── hooks/               # 自定义 Hooks ⭐新增
│   ├── __init__.js      # 统一导出
│   ├── useAuth.js       # 认证管理 (登录/登出/Token)
│   ├── useTable.js      # 表格数据分页加载
│   └── useModal.js      # 弹窗状态管理
├── modules/             # 页面模块 (按功能域划分)
│   ├── auth/            # 认证模块
│   │   └── pages/
│   │       └── Login.jsx
│   ├── system/          # 系统管理
│   │   └── pages/
│   │       └── UserManagement.jsx
│   ├── order/           # 订单管理
│   │   └── pages/
│   │       └── OrderManagement.jsx
│   ├── inventory/       # 库存管理
│   │   └── pages/
│   │       └── InventoryManagement.jsx
│   ├── scheduling/      # 调度中心
│   ├── fulfillment/     # 履约管理
│   ├── supplier/        # 供应商管理
│   ├── report/          # 数据报表
│   │   └── pages/
│   │       └── Dashboard.jsx
│   ├── ai-dashboard/    # AI智能看板
│   └── knowledge/       # RAG知识库
├── services/
│   ├── api.js          # Axios 实例 + 拦截器
│   └── modules/         # API 模块化封装
│       ├── auth.js
│       ├── user.js
│       ├── order.js
│       └── ...
├── store/               # Zustand 状态管理
│   └── authStore.js    # 认证状态
├── utils/
│   └── theme.js         # 主题配置
├── App.jsx              # 路由配置
└── main.jsx             # React 入口
```

### 共享组件使用示例

```jsx
// 统计卡片
<StatCard
  title="今日订单"
  value={data.orderStats.totalToday}
  icon={<ShoppingCartOutlined />}
  color="#4f46e5"
  trend="+12.5%"
  trendType="up"
/>

// 状态标签
<StatusTag status="pending" />
<StatusTag status="shipped" customMap={{ shipped: { color: 'blue', label: '运输中' } }} />

// 表单弹窗
<FormModal visible={visible} title="新建订单" onCancel={hide} onOk={handleSubmit} form={form}>
  <FormModal.Item name="customerName" label="客户名称" rules={[{ required: true }]}>
    <Input />
  </FormModal.Item>
</FormModal>

// 页面头部
<PageHeader title="用户管理" breadcrumb={[{ title: '系统管理' }, { title: '用户管理' }]} extra={<Button>操作</Button>} />
```

### 自定义 Hooks 使用示例

```jsx
// useTable - 表格数据管理
const { data, loading, pagination, handleChange, refresh } = useTable(orderAPI.list, { page: 1, size: 20 });

// useModal - 弹窗状态管理
const { visible, editingId, form, show, hide, confirm, isEditing } = useModal({ role: 'USER' });
show(null, { role: 'USER' });  // 新建
show(id, record);              // 编辑
confirm(handleSubmit);          // 确认提交

// useAuth - 认证管理
const { user, token, login, logout, isAuthenticated } = useAuth();
```

---

## Docker 容器化部署

```yaml
# docker/docker-compose.yml
services:
  postgres:
    image: postgres:16.4-alpine
    container_name: xuni-postgres
    ports: ["5432:5432"]
    volumes: [postgres_data:/var/lib/postgresql/data]

  redis:
    image: redis:7.4-alpine
    container_name: xuni-redis
    ports: ["6379:6379"]

  qdrant:
    image: qdrant/qdrant:v1.11.5
    container_name: xuni-qdrant
    ports: ["6333:6333", "6334:6334"]
    volumes: [qdrant_data:/qdrant/storage]
```

**启动命令:**
```powershell
cd d:\xuni\scheduling_platform\docker
docker-compose up -d
```

---

## Alembic 数据库迁移

```powershell
# 初始化
cd backend
alembic init alembic

# 生成迁移
alembic revision --autogenerate -m "add user table"

# 执行迁移
alembic upgrade head

# 回滚
alembic downgrade -1
```

---

## RAG 检索管道

```
文档入库: 文本 → 智能分块(800字) → Embedding → Qdrant

检索: 查询 → Embedding → 多路召回
        ├─ 语义检索 (Cosine Top-K)
        ├─ 决策历史 (相似场景)
        └─ 业务规则 (规则库匹配)
      → 去重合并 → LLM Rerank → Top-K → 增强生成
```

---

## API 路由一览

| 路由 | 模块 | 说明 |
|------|------|------|
| POST /api/auth/login | 认证 | 登录 |
| POST /api/auth/register | 认证 | 注册 |
| POST /api/auth/refresh | 认证 | 刷新Token |
| GET/POST /api/users | 用户管理 | 用户CRUD |
| GET/POST /api/orders | 订单管理 | 订单CRUD |
| GET/POST /api/inventory | 库存管理 | 库存CRUD |
| POST /api/scheduling/{id}/ai-suggest | AI调度 | AI调度方案 |
| GET/POST /api/fulfillment | 履约管理 | 履约CRUD |
| POST /api/ai/agent/{id} | AI服务 | Agent推理 |
| POST /api/ai/pipeline | AI服务 | 全流程流水线 |
| POST /api/knowledge/search/hybrid | 知识库 | 混合检索 |
| POST /api/knowledge/rag/query | 知识库 | RAG问答 |
| GET /api/reports/dashboard | 报表 | 仪表盘数据 |

---

## 项目启动指南

### 1. Docker 数据库启动
```powershell
cd d:\xuni\scheduling_platform\docker
docker-compose up -d
```

### 2. 后端启动 (PyCharm)
```powershell
cd d:\xuni\scheduling_platform\backend

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 填写数据库和百炼API密钥

# 运行数据库迁移
alembic upgrade head

# 启动服务
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

### 3. 前端启动 (PyCharm)
```powershell
cd d:\xuni\scheduling_platform\frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
# 访问 http://localhost:3000
```

---

## 架构亮点

1. **Repository Pattern** - 数据访问与业务逻辑分离，便于单元测试和代码复用
2. **统一异常处理** - 全局异常捕获，标准化错误响应格式
3. **Docker 容器化** - 数据库服务一键部署，环境一致性保障
4. **Alembic 迁移** - 数据库 Schema 版本化管理，安全变更
5. **React Hooks** - 自定义 Hooks 提取逻辑复用，组件更简洁
6. **共享组件库** - 统一 UI 风格，减少重复代码
7. **AI 多Agent** - 需求预测、库存优化、调度决策、成本优化、风险控制、执行管控
8. **RAG 增强** - 结合企业知识库，提升 AI 回答准确性
