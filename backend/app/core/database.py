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
    # 0. 确保所有模型已注册到 Base.metadata
    import app.models  # noqa: F401 — 触发所有模型导入

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

        # 3. 创建测试库存数据
        from sqlalchemy import func
        from app.models.inventory import Inventory
        
        inv_count = (await session.execute(
            select(func.count(Inventory.id))
        )).scalar_one()
        
        if inv_count == 0:
            test_inventories = [
                Inventory(product_id=1, product_name="苹果 iPhone 16 Pro", sku_code="IP16PRO-256G", warehouse_id=1, warehouse_name="北京仓库", quantity=500, safety_stock=100, locked_quantity=50, available_quantity=450, status="NORMAL"),
                Inventory(product_id=2, product_name="华为 Mate 70 Pro", sku_code="MATE70PRO-512G", warehouse_id=1, warehouse_name="北京仓库", quantity=80, safety_stock=100, locked_quantity=10, available_quantity=70, status="LOW"),
                Inventory(product_id=3, product_name="小米 15 Ultra", sku_code="MI15ULTRA-256G", warehouse_id=2, warehouse_name="上海仓库", quantity=200, safety_stock=50, locked_quantity=0, available_quantity=200, status="NORMAL"),
                Inventory(product_id=4, product_name="三星 Galaxy S24", sku_code="S24-128G", warehouse_id=2, warehouse_name="上海仓库", quantity=30, safety_stock=50, locked_quantity=0, available_quantity=30, status="LOW"),
                Inventory(product_id=5, product_name="OPPO Find X8", sku_code="FINDX8-256G", warehouse_id=3, warehouse_name="广州仓库", quantity=150, safety_stock=80, locked_quantity=20, available_quantity=130, status="NORMAL"),
                Inventory(product_id=6, product_name="vivo X200 Pro", sku_code="X200PRO-512G", warehouse_id=3, warehouse_name="广州仓库", quantity=40, safety_stock=60, locked_quantity=5, available_quantity=35, status="LOW"),
                Inventory(product_id=7, product_name="联想 ThinkPad X1", sku_code="TPX1-16G", warehouse_id=1, warehouse_name="北京仓库", quantity=100, safety_stock=30, locked_quantity=15, available_quantity=85, status="NORMAL"),
                Inventory(product_id=8, product_name="戴尔 XPS 15", sku_code="XPS15-32G", warehouse_id=2, warehouse_name="上海仓库", quantity=25, safety_stock=40, locked_quantity=0, available_quantity=25, status="LOW"),
            ]
            session.add_all(test_inventories)
            await session.commit()
            logger.info("✅ 测试库存数据已创建")

        # 4. 创建测试订单数据
        from app.models.order import Order
        
        order_count = (await session.execute(
            select(func.count(Order.id))
        )).scalar_one()
        
        if order_count == 0:
            test_orders = [
                Order(order_no="ORD20260601001", order_type="SALE", status="PENDING", customer_name="北京科技有限公司", product_name="华为 Mate 70 Pro", quantity=10, unit_price=8999, total_amount=89990, warehouse_name="北京仓库", shipping_address="北京市海淀区中关村大街1号"),
                Order(order_no="ORD20260601002", order_type="SALE", status="SHIPPED", customer_name="上海贸易有限公司", product_name="苹果 iPhone 16 Pro", quantity=5, unit_price=9999, total_amount=49995, warehouse_name="上海仓库", shipping_address="上海市浦东新区陆家嘴环路1000号"),
                Order(order_no="ORD20260601003", order_type="SALE", status="DELIVERED", customer_name="广州电子有限公司", product_name="小米 15 Ultra", quantity=20, unit_price=5999, total_amount=119980, warehouse_name="广州仓库", shipping_address="广州市天河区珠江新城花城大道1号"),
                Order(order_no="ORD20260601004", order_type="SALE", status="PENDING", customer_name="深圳科技有限公司", product_name="三星 Galaxy S24", quantity=8, unit_price=6499, total_amount=51992, warehouse_name="上海仓库", shipping_address="深圳市南山区科技园南路1号"),
                Order(order_no="ORD20260601005", order_type="SALE", status="CANCELLED", customer_name="成都商贸有限公司", product_name="OPPO Find X8", quantity=15, unit_price=4999, total_amount=74985, warehouse_name="广州仓库", shipping_address="成都市锦江区春熙路1号"),
            ]
            session.add_all(test_orders)
            await session.commit()
            logger.info("✅ 测试订单数据已创建")

        # 5. 创建测试供应商数据
        from app.models.supplier import Supplier
        
        supplier_count = (await session.execute(
            select(func.count(Supplier.id))
        )).scalar_one()
        
        if supplier_count == 0:
            test_suppliers = [
                Supplier(name="华为技术有限公司", code="HW001", type="电子产品", status="ACTIVE", contact_name="张三", contact_phone="13800138001", contact_email="zhangsan@huawei.com", address="深圳市龙岗区坂田华为基地", rating=4.9, cooperation_years=10, on_time_delivery_rate=99.5, quality_pass_rate=99.8),
                Supplier(name="苹果贸易(上海)有限公司", code="APL001", type="电子产品", status="ACTIVE", contact_name="李四", contact_phone="13900139002", contact_email="lisi@apple.com", address="上海市浦东新区世纪大道8号", rating=4.8, cooperation_years=8, on_time_delivery_rate=98.5, quality_pass_rate=99.5),
                Supplier(name="小米科技有限责任公司", code="MI001", type="电子产品", status="ACTIVE", contact_name="王五", contact_phone="13700137003", contact_email="wangwu@xiaomi.com", address="北京市海淀区清河中街68号", rating=4.7, cooperation_years=6, on_time_delivery_rate=97.8, quality_pass_rate=99.0),
                Supplier(name="三星电子(中国)有限公司", code="SAM001", type="电子产品", status="ACTIVE", contact_name="赵六", contact_phone="13600136004", contact_email="zhaoliu@samsung.com", address="天津市滨海新区天津港保税区", rating=4.6, cooperation_years=12, on_time_delivery_rate=98.0, quality_pass_rate=98.8),
                Supplier(name="OPPO广东移动通信有限公司", code="OPPO01", type="电子产品", status="ACTIVE", contact_name="孙七", contact_phone="13500135005", contact_email="sunqi@oppo.com", address="东莞市长安镇乌沙社区海滨路18号", rating=4.5, cooperation_years=5, on_time_delivery_rate=96.5, quality_pass_rate=98.5),
            ]
            session.add_all(test_suppliers)
            await session.commit()
            logger.info("✅ 测试供应商数据已创建")
