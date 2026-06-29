"""
Xuni Scheduling Platform - Application Entry Point
供应链智能调度平台 v2.0 - Python FastAPI 版本

启动方式:
    python -m app.main
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
"""

import sys
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
    from app.core.database import init_db
    await init_db()
    from app.services.ai.agent_orchestrator import init_knowledge_base
    await init_knowledge_base()
    print(f"""
╔══════════════════════════════════════════════════╗
║     供应链智能调度平台 v2.0                       ║
║     Xuni Scheduling Platform                     ║
║     Python FastAPI Edition                       ║
║     API Docs: http://localhost:{settings.PORT}/docs ║
╚══════════════════════════════════════════════════╝
""")
    yield
    await engine.dispose()


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
