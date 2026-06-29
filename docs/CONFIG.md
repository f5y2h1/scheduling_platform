# ⚙️ Xuni 平台配置说明 v2.0

---

## Python 环境

```bash
# PyCharm → Settings → Project → Python Interpreter
# 选择: Python 3.11 或 3.12
```

---

## 环境变量 (backend/.env)

| 变量 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| `BAILIAN_API_KEY` | **是** | - | 百炼 API Key |
| `DB_HOST` | 否 | localhost | PostgreSQL 主机 |
| `DB_PORT` | 否 | 5432 | PostgreSQL 端口 |
| `DB_NAME` | 否 | scheduling_platform | 数据库名 |
| `DB_USER` | 否 | postgres | 用户 |
| `DB_PASSWORD` | 否 | postgres | 密码 |
| `REDIS_HOST` | 否 | localhost | Redis 主机 |
| `QDRANT_HOST` | 否 | localhost | Qdrant 主机 |
| `JWT_SECRET` | 否 | (内置) | JWT 密钥 |

---

## LLM 模型选择

在 AI 智能看板页面或 API 中选择：

| 模型 ID | 名称 | 场景 |
|---------|------|------|
| `qwen-plus` | 通义千问-Plus | 日常推荐 |
| `qwen-max` | 通义千问-Max | 复杂推理 |
| `qwen-turbo` | 通义千问-Turbo | 快速响应 |
| `qwen2.5-72b-instruct` | 2.5-72B | 高难度分析 |
| `qwen2.5-32b-instruct` | 2.5-32B | 平衡选择 |
| `qwen2.5-14b-instruct` | 2.5-14B | 日常使用 |
| `qwen2.5-7b-instruct` | 2.5-7B | 轻量快速 |

---

## Embedding 配置

```python
EMBEDDING_MODEL = "text-embedding-v2"
VECTOR_SIZE = 1536  # 输出维度
```

---

## Qdrant 配置

| 参数 | 默认值 |
|------|--------|
| REST API | http://localhost:6333 |
| 集合数 | 3 个 |
| 距离 | Cosine |
| 默认 Top-K | 5 |
| 相似度阈值 | 0.7 |
