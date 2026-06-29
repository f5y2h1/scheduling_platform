# Xuni 供应链智能调度平台 v2.0

## 一、项目概述

Xuni 供应链智能调度平台是一款基于 **FastAPI + React** 技术栈的企业级供应链管理系统，集成了 **LangGraph 多Agent编排**、**RAG检索增强生成**、**全模态AI能力**（语音转文字、图片解析）等前沿技术，为企业提供智能化的供应链调度解决方案。

---

## 二、行业痛点分析

### 2.1 传统供应链管理面临的核心痛点

| 痛点类别 | 具体问题 | 业务影响 |
|----------|----------|----------|
| **需求预测不准确** | 依赖人工经验判断，缺乏数据驱动 | 库存积压或缺货，成本增加15-30% |
| **库存管理低效** | 实时库存状态不透明，安全库存设置不合理 | 资金占用过高，缺货率上升 |
| **调度决策复杂** | 多因素权衡困难（成本、时效、风险），人工决策耗时长 | 响应慢，错失最佳调度时机 |
| **成本优化困难** | 物流成本构成复杂，缺乏系统化优化手段 | 物流成本占比高，利润空间被压缩 |
| **风险响应滞后** | 供应链风险识别依赖人工，预警不及时 | 突发风险导致交付中断，损失巨大 |
| **信息孤岛** | 各业务系统数据不互通，决策缺乏全局视角 | 协同效率低，重复工作多 |
| **知识传承难** | 业务专家经验难以沉淀，新人上手慢 | 决策质量不稳定，依赖少数专家 |
| **沟通效率低** | 跨部门沟通依赖邮件/会议，信息传递不及时 | 响应周期长，客户满意度下降 |

### 2.2 本平台解决的核心需求

| 需求编号 | 需求描述 | 解决方式 | 预期效果 |
|----------|----------|----------|----------|
| REQ-001 | 基于历史数据和市场趋势进行精准需求预测 | 需求预测Agent + RAG知识库检索 | 预测准确率提升20-30% |
| REQ-002 | 实时监控库存状态，智能预警低库存商品 | 库存检查工具 + 风险控制Agent | 缺货率降低15%，库存周转天数缩短10% |
| REQ-003 | 自动化生成调度方案，综合考虑成本、时效、风险 | LangGraph多Agent协作工作流 | 调度决策时间从小时级缩短至分钟级 |
| REQ-004 | 多维度成本分析与优化建议 | 成本优化Agent + 数据分析工具 | 物流成本降低8-15% |
| REQ-005 | 实时风险监测与预警，提前制定应对方案 | 风险控制Agent + 循环迭代检查 | 风险响应时间缩短50% |
| REQ-006 | 统一数据中台，打破信息孤岛 | 集中式数据库 + API标准化接口 | 跨部门协同效率提升40% |
| REQ-007 | 业务知识沉淀与智能问答 | Qdrant向量数据库 + RAG检索增强 | 新人上手周期缩短60% |
| REQ-008 | 高效沟通与快速响应 | 全模态AI聊天窗口（语音/图片/文本） | 沟通效率提升30% |

### 2.3 典型应用场景

#### 场景一：智能调度决策

**业务背景**：某电商企业大促期间订单量激增，需要快速制定仓库调度方案

**传统方式**：
1. 人工统计各仓库库存
2. 人工分析订单分布
3. 手动制定调度方案
4. 逐级审批
5. **耗时：4-8小时**

**本平台方式**：
1. 用户在聊天窗口描述需求："双11大促期间，北京仓库存紧张，请制定调货方案"
2. 系统自动触发LangGraph工作流：
   - 需求预测Agent分析订单趋势
   - 库存检查工具获取各仓库实时数据
   - 库存优化Agent计算最优调货量
   - 调度决策Agent生成调货方案
   - 成本优化Agent评估运输成本
   - 风险控制Agent检查潜在风险
3. 循环迭代直到方案满足所有约束条件
4. 输出完整调度方案和AI建议
5. **耗时：5-10分钟**

**价值**：决策效率提升90%，方案质量更优

#### 场景二：语音快速下单

**业务背景**：仓库管理员在作业现场需要快速创建出库单

**传统方式**：
1. 返回办公室
2. 打开电脑登录系统
3. 手动填写出库信息
4. 提交审核
5. **耗时：15-30分钟**

**本平台方式**：
1. 使用手机访问聊天窗口
2. 点击麦克风说出需求："从上海仓出库100件华为Mate60发往北京仓"
3. 语音转文字（qwen3.5-omni-plus）自动识别并解析
4. 系统自动生成出库单草稿
5. 管理员确认后提交
6. **耗时：1-2分钟**

**价值**：操作效率提升90%，减少现场-办公室往返

#### 场景三：图片解析入库

**业务背景**：供应商送货到仓，仓管员需要快速录入商品信息

**传统方式**：
1. 查看纸质送货单
2. 逐项录入商品名称、数量、规格
3. 核对条码
4. 提交入库单
5. **耗时：每件商品3-5分钟**

**本平台方式**：
1. 用手机拍摄送货单照片
2. 上传至聊天窗口
3. 图片解析（qwen3.5-omni-plus）自动识别商品信息
4. 系统自动生成入库单草稿
5. 仓管员核对确认后提交
6. **耗时：整单1-2分钟**

**价值**：入库效率提升80%，减少录入错误

#### 场景四：知识问答

**业务背景**：新入职调度员遇到业务问题需要咨询

**传统方式**：
1. 查找文档（分散在多个系统）
2. 找不到答案时询问老员工
3. 等待回复
4. **耗时：不确定，可能几小时**

**本平台方式**：
1. 在聊天窗口直接提问："供应商延迟交货的处理流程是什么？"
2. RAG检索知识库相关文档
3. LLM整理并生成清晰回答
4. 引用来源文档便于深入了解
5. **耗时：10-30秒**

**价值**：知识获取效率提升95%，减少对老员工的依赖

---

## 三、技术栈

### 3.1 后端技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| **Python** | 3.11+ | 编程语言 |
| **FastAPI** | 0.115.6 | Web框架 |
| **Uvicorn** | 0.34.0 | ASGI服务器 |
| **SQLAlchemy** | 2.0.36 | ORM框架（异步模式） |
| **PostgreSQL** | - | 关系型数据库（Docker部署） |
| **Redis** | 5.2.1 | 缓存数据库（Docker部署） |
| **Qdrant** | 1.12.2 | 向量数据库（Docker部署） |
| **LangGraph** | 0.2.45 | 多Agent编排框架 |
| **LangChain** | 0.3.86 | AI工具链 |
| **DashScope** | 1.21.0 | 阿里云百炼API客户端 |
| **Alembic** | 1.14.0 | 数据库迁移 |
| **Pydantic** | 2.10.3 | 数据验证 |
| **python-jose** | 3.3.0 | JWT认证 |
| **passlib** | 1.7.4 | 密码加密 |

### 3.2 前端技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| **React** | 18.3.1 | 前端框架 |
| **Vite** | 5.4.8 | 构建工具 |
| **React Router** | 6.26.2 | 路由管理 |
| **Ant Design** | 5.21.4 | UI组件库 |
| **Zustand** | 5.0.0 | 状态管理 |
| **Axios** | 1.7.7 | HTTP客户端 |
| **Recharts** | 2.13.0 | 图表组件 |
| **ECharts** | 5.5.1 | 数据可视化 |
| **react-markdown** | 9.0.1 | Markdown渲染 |

### 3.3 AI模型配置

| 模型类型 | 模型名称 | 用途 |
|----------|----------|------|
| **LLM** | `qwen3.5-omni-plus` | 默认对话模型、多模态处理 |
| **Embedding** | `text-embedding-v2` | 文本向量化（不变） |

---

## 四、项目架构

### 4.1 后端架构

```
backend/
├── app/
│   ├── api/              # REST API 路由层
│   │   ├── auth.py       # 认证管理
│   │   ├── user.py       # 用户管理
│   │   ├── order.py      # 订单管理
│   │   ├── inventory.py  # 库存管理
│   │   ├── scheduling.py # 调度中心
│   │   ├── fulfillment.py# 履约管理
│   │   ├── supplier.py   # 供应商管理
│   │   ├── report.py     # 数据报表
│   │   ├── ai.py         # AI智能服务
│   │   └── knowledge.py  # 知识库管理
│   ├── services/         # 业务逻辑层
│   │   ├── ai/           # AI服务
│   │   │   ├── bailian_client.py    # 百炼API客户端
│   │   │   ├── agent_orchestrator.py # Agent编排器
│   │   │   └── agents.py             # 6大业务Agent
│   │   ├── langgraph/    # LangGraph多Agent编排
│   │   │   ├── workflow.py   # 工作流定义与编译
│   │   │   ├── nodes.py      # 节点定义（含循环逻辑）
│   │   │   ├── state.py      # 状态定义
│   │   │   ├── tools.py      # 工具定义（@tool装饰器）
│   │   │   └── mcp.py        # MCP协议集成
│   │   └── rag/          # RAG检索增强生成
│   │       ├── rag_service.py      # RAG服务
│   │       ├── knowledge_base.py   # 知识库管理
│   │       └── qdrant_store.py     # Qdrant存储
│   ├── repositories/     # 数据访问层（Repository模式）
│   ├── models/           # SQLAlchemy模型定义
│   ├── schemas/          # Pydantic数据结构
│   ├── core/             # 核心配置
│   │   ├── config.py     # 配置管理
│   │   ├── database.py   # 数据库连接
│   │   ├── logger.py     # 日志配置
│   │   └── middleware.py # 中间件
│   └── utils/            # 工具函数
├── alembic/              # 数据库迁移
├── logs/                 # 日志文件
└── requirements.txt      # 依赖列表
```

### 4.2 前端架构

```
frontend/
├── src/
│   ├── components/       # 共享组件
│   │   ├── chat/         # 聊天组件（语音、图片、流式响应）
│   │   ├── layout/       # 布局组件（毛玻璃效果）
│   │   └── common/       # 通用组件
│   ├── modules/          # 业务模块
│   │   ├── ai-dashboard/     # AI智能服务（工作流编排、知识库）
│   │   ├── order/            # 订单管理
│   │   ├── inventory/        # 库存管理
│   │   ├── scheduling/       # 调度中心
│   │   ├── fulfillment/      # 履约管理
│   │   ├── supplier/         # 供应商管理
│   │   ├── report/           # 数据报表
│   │   └── system/           # 系统管理（登录、用户）
│   ├── services/         # API服务层
│   │   ├── api/          # 各模块API封装
│   │   └── smartRequest.py # 请求封装（含流式响应）
│   ├── store/            # Zustand状态管理
│   ├── hooks/            # 自定义Hooks
│   └── utils/            # 工具函数
├── vite.config.js        # Vite配置（含代理）
└── package.json          # 依赖配置
```

---

## 五、核心功能模块

### 5.1 认证管理

| 功能 | API接口 | 说明 |
|------|---------|------|
| 用户登录 | `POST /api/auth/login` | JWT令牌认证 |
| 用户登出 | `POST /api/auth/logout` | 清除令牌 |
| 刷新令牌 | `POST /api/auth/refresh` | 获取新令牌 |
| 健康检查 | `GET /api/health` | 服务状态检测 |

### 5.2 订单管理

| 功能 | API接口 | 说明 |
|------|---------|------|
| 订单列表 | `GET /api/orders` | 分页查询、状态筛选、关键词搜索 |
| 订单详情 | `GET /api/orders/{id}` | 获取单个订单 |
| 创建订单 | `POST /api/orders` | 新建订单 |
| 更新订单 | `PUT /api/orders/{id}` | 修改订单信息 |
| 删除订单 | `DELETE /api/orders/{id}` | 删除订单 |
| 订单统计 | `GET /api/orders/stats` | 统计各状态订单数量 |

### 5.3 库存管理

| 功能 | API接口 | 说明 |
|------|---------|------|
| 库存列表 | `GET /api/inventory` | 分页查询、状态筛选 |
| 库存详情 | `GET /api/inventory/{id}` | 获取库存详情 |
| 入库管理 | `POST /api/inventory/inbound` | 商品入库 |
| 出库管理 | `POST /api/inventory/outbound` | 商品出库 |
| 库存统计 | `GET /api/inventory/stats` | 库存统计信息 |

### 5.4 调度中心

| 功能 | API接口 | 说明 |
|------|---------|------|
| 任务列表 | `GET /api/scheduling` | 调度任务列表 |
| 任务详情 | `GET /api/scheduling/{id}` | 任务详情 |
| 创建任务 | `POST /api/scheduling` | 创建调度任务 |
| AI调度建议 | `POST /api/scheduling/ai-suggest` | 获取AI调度建议 |
| 审批任务 | `PUT /api/scheduling/{id}/approve` | 审批调度任务 |

### 5.5 履约管理

| 功能 | API接口 | 说明 |
|------|---------|------|
| 履约单列表 | `GET /api/fulfillment` | 履约单查询 |
| 创建履约单 | `POST /api/fulfillment` | 新建履约单 |
| 更新状态 | `PUT /api/fulfillment/{id}` | 更新履约状态 |

### 5.6 供应商管理

| 功能 | API接口 | 说明 |
|------|---------|------|
| 供应商列表 | `GET /api/suppliers` | 分页查询 |
| 供应商详情 | `GET /api/suppliers/{id}` | 获取详情 |
| 创建供应商 | `POST /api/suppliers` | 新建供应商 |
| 更新供应商 | `PUT /api/suppliers/{id}` | 修改信息 |
| 删除供应商 | `DELETE /api/suppliers/{id}` | 删除供应商 |

### 5.7 数据报表

| 功能 | API接口 | 说明 |
|------|---------|------|
| 仪表盘 | `GET /api/reports/dashboard` | 核心指标展示 |
| 订单报表 | `GET /api/reports/orders` | 订单统计报表 |
| 库存报表 | `GET /api/reports/inventory` | 库存统计报表 |
| 调度报表 | `GET /api/reports/scheduling` | 调度统计报表 |

### 5.8 AI智能服务（核心亮点）

#### 4.8.1 多Agent工作流编排

基于 **LangGraph** 实现的供应链调度工作流，包含以下节点：

| 节点名称 | 功能 | Agent |
|----------|------|-------|
| `demand_forecast_node` | 需求预测 | 需求预测Agent |
| `inventory_check_node` | 库存检查 | 调用库存查询工具 |
| `inventory_optimization_node` | 库存优化 | 库存优化Agent |
| `scheduling_decision_node` | 调度决策 | 调度决策Agent |
| `cost_optimization_node` | 成本优化 | 成本优化Agent |
| `risk_control_node` | 风险控制 | 风险控制Agent |
| `execution_control_node` | 执行管控 | 执行管控Agent |
| `summary_node` | 结果汇总 | - |

**循环机制**：工作流包含条件分支判断节点 `should_replan` 和 `should_call_tool`，支持循环迭代直到满足条件。

**记忆系统**：使用 `PostgresSaver` 作为 Checkpointer，持久化工作流状态，支持断点续跑。

#### 4.8.2 业务工具调用

使用 LangChain `@tool` 装饰器封装的业务工具：

| 工具名称 | 功能 |
|----------|------|
| `query_inventory` | 查询库存信息 |
| `query_low_stock` | 查询低库存商品 |
| `query_orders` | 查询订单信息 |
| `query_suppliers` | 查询供应商信息 |
| `query_schedule_tasks` | 查询调度任务 |
| `weather_query` | 天气查询（备用） |
| `logistics_tracking` | 物流追踪（备用） |

#### 4.8.3 全模态AI能力

基于 **qwen3.5-omni-plus** 模型实现：

| 功能 | API接口 | 说明 |
|------|---------|------|
| 语音转文字 | `POST /api/ai/transcribe` | 支持 wav/mp3/m4a 等格式 |
| 图片解析 | `POST /api/ai/analyze-image` | 支持 jpg/png/gif 等格式 |
| 流式对话 | `POST /api/ai/chat/stream` | 实时AI响应 |

#### 4.8.4 聊天界面功能

- ✅ 文本输入
- ✅ 语音转文字（浏览器原生 + AI模型备选）
- ✅ 图片上传解析（自动调用 qwen3.5-omni-plus）
- ✅ 上下文管理（滑动窗口+摘要压缩，保留最近10轮）
- ✅ 流式响应展示

#### 4.8.5 会话管理

| 功能 | API接口 | 说明 |
|------|---------|------|
| 会话列表 | `GET /api/ai/sessions` | 获取历史会话 |
| 会话详情 | `GET /api/ai/sessions/{id}` | 获取会话历史 |
| 删除会话 | `DELETE /api/ai/sessions/{id}` | 删除会话 |

### 5.9 知识库管理

| 功能 | API接口 | 说明 |
|------|---------|------|
| 文档列表 | `GET /api/knowledge` | 知识库文档列表 |
| 文档详情 | `GET /api/knowledge/{id}` | 获取文档详情 |
| 上传文档 | `POST /api/knowledge` | 上传并向量化 |
| 删除文档 | `DELETE /api/knowledge/{id}` | 删除文档 |
| 知识检索 | `POST /api/knowledge/search` | 语义搜索 |

**RAG检索增强生成**：多路召回 + 上下文构建 + LLM增强生成

---

## 六、需求满足分析

### 6.1 核心需求

| 需求类别 | 具体需求 | 实现方案 |
|----------|----------|----------|
| **供应链管理** | 订单全生命周期管理 | Order CRUD + 状态流转 |
| **库存管理** | 实时库存监控、出入库管理 | Inventory CRUD + 低库存预警 |
| **智能调度** | AI辅助调度决策 | LangGraph多Agent工作流 |
| **成本优化** | 物流成本优化建议 | 成本优化Agent + 工具调用 |
| **风险控制** | 供应链风险预警 | 风险控制Agent |
| **数据分析** | 可视化报表展示 | Recharts + ECharts |

### 6.2 AI能力需求

| 需求 | 实现方案 |
|------|----------|
| 多Agent协作 | LangGraph StateGraph + 条件分支 + 循环迭代 |
| 记忆系统 | PostgresSaver Checkpointer + 上下文管理器 |
| 工具调用 | LangChain @tool 装饰器 + MCP协议集成 |
| 语音转文字 | qwen3.5-omni-plus 全模态模型 |
| 图片解析 | qwen3.5-omni-plus 全模态模型 |
| 知识库问答 | RAG检索增强生成 |

### 6.3 技术架构需求

| 需求 | 实现方案 |
|------|----------|
| 前后端分离 | FastAPI + React 独立部署 |
| 异步处理 | SQLAlchemy asyncio + asyncpg |
| 数据持久化 | PostgreSQL + Qdrant向量数据库 |
| 缓存 | Redis |
| 数据库迁移 | Alembic |
| 认证授权 | JWT + Passlib |

---

## 七、部署与启动

### 7.1 后端启动

```bash
# 进入后端目录
cd backend

# 安装依赖
pip install -r requirements.txt

# 设置环境变量（在 .env 文件中配置）
# BAILIAN_API_KEY=your-api-key

# 启动服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080

# 访问 API 文档
http://localhost:8080/docs
```

### 7.2 前端启动

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 访问前端页面
http://localhost:3000
```

### 7.3 Docker部署（数据库）

```bash
# PostgreSQL、Redis、Qdrant 使用 Docker 部署
docker-compose up -d
```

### 7.4 登录信息

- **用户名**：admin
- **密码**：admin123

---

## 八、关键特性

1. **LangGraph循环迭代**：工作流支持条件分支和循环，通过 `should_replan` 判断是否需要重新规划
2. **全模态AI**：基于 qwen3.5-omni-plus 实现语音转文字和图片解析
3. **RAG检索增强**：知识库语义搜索 + LLM增强生成
4. **工具调用系统**：使用 LangChain @tool 装饰器封装业务操作
5. **记忆系统**：Checkpointer持久化 + 上下文管理器
6. **流式对话**：FastAPI StreamingResponse + 前端EventSource
7. **毛玻璃UI风格**：现代化渐变背景 + 浮动卡片设计

---

## 九、文件变更记录

| 文件 | 变更内容 |
|------|----------|
| `backend/app/core/config.py` | 添加 qwen3.5-omni-plus 为默认模型和多模态模型 |
| `backend/app/services/ai/bailian_client.py` | 添加 `transcribe_audio()` 和 `analyze_image()` 方法 |
| `backend/app/api/ai.py` | 新增 `/api/ai/transcribe` 和 `/api/ai/analyze-image` 接口 |
| `backend/app/services/langgraph/workflow.py` | 优化工具加载，移除耗时的MCP远程调用 |
| `frontend/src/services/api/ai.js` | 新增 `transcribeAudio()` 和 `analyzeImage()` API方法 |
| `frontend/src/components/chat/ChatUI.jsx` | 修复图标导入错误，图片上传后自动解析内容 |
| `frontend/src/services/smartRequest.js` | 增加请求超时时间至30秒 |
| `frontend/src/App.jsx` | 添加ErrorBoundary错误捕获组件 |

---

*文档生成时间：2026-06-29*
*版本：v2.0*