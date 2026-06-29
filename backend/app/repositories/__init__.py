"""
数据访问层 (Repository Layer)
提供统一的数据访问接口，与具体数据库实现解耦

设计原则：
1. Repository 模式：封装数据库访问逻辑
2. 单一职责：每个 Repository 只负责一个实体
3. 依赖注入：通过构造函数注入数据库会话
4. 类型安全：使用泛型保证类型检查
"""

from .base_repository import BaseRepository
from .user_repository import UserRepository
from .order_repository import OrderRepository
from .inventory_repository import InventoryRepository
from .fulfillment_repository import FulfillmentRepository
from .supplier_repository import SupplierRepository
from .schedule_task_repository import ScheduleTaskRepository

__all__ = [
    "BaseRepository",
    "UserRepository",
    "OrderRepository",
    "InventoryRepository",
    "FulfillmentRepository",
    "SupplierRepository",
    "ScheduleTaskRepository",
]