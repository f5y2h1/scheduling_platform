"""
数据库引擎与会话管理
SQLAlchemy 2.0 异步模式
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings
from app.core.logger import logger

# 异步引擎
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
)

# 会话工厂
async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """SQLAlchemy 声明式基类"""
    pass


async def get_db() -> AsyncSession:
    """获取数据库会话（FastAPI 依赖注入）
    
    采用手动事务管理方式，避免 async with session.begin() 导致的 greenlet_spawn 问题。
    路由函数中通过 db.commit() 提交事务，异常时自动回滚。
    """
    async with async_session_factory() as session:
        yield session


async def init_db():
    """初始化数据库表 + 默认用户"""
    # 1. 建表
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("数据库表初始化完成")

    # 2. 创建默认测试账号
    from passlib.context import CryptContext
    from sqlalchemy import select
    from app.models.user import User

    # pbkdf2_sha256：无密码长度限制，成熟稳定，passlib 内置
    pwd = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

    async with async_session_factory() as session:
        admin_exists = (await session.execute(
            select(User).where(User.username == "admin")
        )).scalar_one_or_none()

        if not admin_exists:
            session.add(User(
                username="admin",
                password=pwd.hash("admin123"),
                real_name="系统管理员",
                email="admin@xuni.com",
                role="ADMIN",
                status=1,
            ))
            logger.info("✅ 默认管理员已创建: admin / admin123")
        elif not admin_exists.password.startswith("$pbkdf2"):
            # 旧格式哈希（bcrypt/bcrypt_sha256），重置为 pbkdf2_sha256
            admin_exists.password = pwd.hash("admin123")
            session.add(admin_exists)
            logger.info("🔧 管理员密码已更新为 pbkdf2_sha256 格式")

        op_exists = (await session.execute(
            select(User).where(User.username == "operator")
        )).scalar_one_or_none()

        if not op_exists:
            session.add(User(
                username="operator",
                password=pwd.hash("admin123"),
                real_name="操作员",
                email="operator@xuni.com",
                role="OPERATOR",
                status=1,
            ))
            logger.info("✅ 默认操作员已创建: operator / admin123")
        elif not op_exists.password.startswith("$pbkdf2"):
            op_exists.password = pwd.hash("admin123")
            session.add(op_exists)
            logger.info("🔧 操作员密码已更新为 pbkdf2_sha256 格式")

        await session.commit()
