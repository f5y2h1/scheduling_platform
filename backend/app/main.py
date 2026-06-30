"""
Xuni Scheduling Platform - Application Entry Point
供应链智能调度平台 v2.0 - Python FastAPI 版本

启动方式:
    cd backend && python -m app.main
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
"""

import sys
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError

from app.core.config import settings
from app.core.database import engine, Base
from app.core.logger import setup_logger
from app.core.middleware import request_log_middleware, exception_handler
from app.core.exceptions import AppException

setup_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 1. 数据库初始化
    from app.core.database import init_db
    await init_db()

    # 2. 知识库初始化
    from app.services.ai.agent_orchestrator import init_knowledge_base
    await init_knowledge_base()

    # 3. 三层记忆体系初始化
    await _init_memory_system()

    # 4. API 密钥自检
    api_status = await _validate_api_on_startup()

    print(f"""
╔══════════════════════════════════════════════════╗
║     供应链智能调度平台 v3.0                       ║
║     Xuni Scheduling Platform                     ║
║     Enterprise AI Agent Edition                  ║
║     API Docs: http://localhost:{settings.PORT}/docs ║
╚══════════════════════════════════════════════════╝
""")
    if not api_status["valid"]:
        print(f"""
⚠️  ╔══════════════════════════════════════════════╗
⚠️  ║  AI 服务不可用                               ║
⚠️  ║  {api_status['message'][:47]:<47s} ║
⚠️  ║  请编辑 backend/.env → BAILIAN_API_KEY        ║
⚠️  ╚══════════════════════════════════════════════╝
""")
    else:
        print(f"✅ {api_status['message']}")
    yield
    await engine.dispose()


async def _validate_api_on_startup() -> dict:
    """启动时校验百炼 API 密钥"""
    from app.services.ai.bailian_client import bailian_client
    import asyncio
    try:
        return await asyncio.to_thread(bailian_client.validate_api_key)
    except Exception as e:
        return {"valid": False, "message": str(e)[:200]}


async def _init_memory_system():
    """初始化三层记忆体系"""
    try:
        from app.services.memory.memory_manager import memory_manager
        from app.core.database import async_session_factory
        from app.services.rag.qdrant_store import qdrant_store
        from app.services.ai.bailian_client import bailian_client

        # 尝试连接 Redis
        redis_client = None
        try:
            import redis.asyncio as aioredis
            redis_client = aioredis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                password=settings.REDIS_PASSWORD or None,
                decode_responses=True,
                socket_connect_timeout=3,
            )
            await redis_client.ping()
        except Exception:
            redis_client = None

        await memory_manager.initialize(
            redis_client=redis_client,
            session_factory=async_session_factory,
            qdrant_store=qdrant_store,
            embedding_client=bailian_client,
        )
    except Exception as e:
        from app.core.logger import logger as log
        log.warning(f"记忆系统初始化部分失败（不影响核心功能）: {e}")


app = FastAPI(
    title="Xuni 供应链智能调度平台",
    description="供应链智能调度与AI辅助决策平台 API",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS 跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 请求日志中间件
app.middleware("http")(request_log_middleware)

# 全局异常处理
app.add_exception_handler(AppException, exception_handler)
app.add_exception_handler(Exception, exception_handler)

# ==================== 注册路由 ====================

from app.api.auth import router as auth_router
from app.api.user import router as user_router
from app.api.order import router as order_router
from app.api.inventory import router as inventory_router
from app.api.scheduling import router as scheduling_router
from app.api.fulfillment import router as fulfillment_router
from app.api.supplier import router as supplier_router
from app.api.report import router as report_router
from app.api.ai import router as ai_router
from app.api.knowledge import router as knowledge_router

app.include_router(auth_router, prefix="/api/auth", tags=["认证管理"])
app.include_router(user_router, prefix="/api/users", tags=["用户管理"])
app.include_router(order_router, prefix="/api/orders", tags=["订单管理"])
app.include_router(inventory_router, prefix="/api/inventory", tags=["库存管理"])
app.include_router(scheduling_router, prefix="/api/scheduling", tags=["调度中心"])
app.include_router(fulfillment_router, prefix="/api/fulfillment", tags=["履约管理"])
app.include_router(supplier_router, prefix="/api/suppliers", tags=["供应商管理"])
app.include_router(report_router, prefix="/api/reports", tags=["数据报表"])
app.include_router(ai_router, prefix="/api/ai", tags=["AI智能服务"])
app.include_router(knowledge_router, prefix="/api/knowledge", tags=["知识库管理"])


@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {"status": "ok", "version": "2.0.0", "framework": "FastAPI"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
