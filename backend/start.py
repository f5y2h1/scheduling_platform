"""
Xuni Scheduling Platform - 启动脚本
Usage: python start.py
"""
import uvicorn
from app.core.config import settings

if __name__ == "__main__":
    print(f"""
╔══════════════════════════════════════════════════╗
║     供应链智能调度平台 v2.0                       ║
║     Xuni Scheduling Platform                     ║
║     API Docs: http://localhost:{settings.PORT}/docs ║
╚══════════════════════════════════════════════════╝
""")
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
