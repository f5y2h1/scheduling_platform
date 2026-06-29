"""
数据传输对象层 (Schema Layer)
定义 API 请求/响应的数据结构，用于数据验证和序列化

设计原则：
1. 使用 Pydantic 进行数据验证
2. 请求模型与响应模型分离
3. 字段描述清晰，便于 API 文档生成
4. 支持分页查询参数
"""

from .common import ApiResponse, PageResult, TokenData
from .auth import LoginRequest, RegisterRequest, UserInfo, LoginResponse, TokenRefreshRequest
from .user import (
    UserCreateRequest, UserUpdateRequest, UserResponse, UserQueryRequest
)
from .order import (
    OrderCreateRequest, OrderUpdateRequest, OrderResponse,
    OrderQueryRequest, OrderStatsResponse
)
from .inventory import (
    InventoryCreateRequest, InventoryUpdateRequest, InventoryResponse,
    InventoryQueryRequest, InventoryStatsResponse
)
from .fulfillment import (
    FulfillmentCreateRequest, FulfillmentUpdateRequest, FulfillmentResponse,
    FulfillmentStatsResponse
)
from .supplier import (
    SupplierCreateRequest, SupplierUpdateRequest, SupplierResponse,
    SupplierQueryRequest
)
from .scheduling import (
    ScheduleTaskCreateRequest, ScheduleTaskUpdateRequest, ScheduleTaskResponse,
    AISuggestRequest, AgentInvokeRequest, PipelineRunRequest
)

__all__ = [
    # Common
    "ApiResponse",
    "PageResult",
    "TokenData",
    # Auth
    "LoginRequest",
    "RegisterRequest",
    "UserInfo",
    "LoginResponse",
    "TokenRefreshRequest",
    # User
    "UserCreateRequest",
    "UserUpdateRequest",
    "UserResponse",
    "UserQueryRequest",
    # Order
    "OrderCreateRequest",
    "OrderUpdateRequest",
    "OrderResponse",
    "OrderQueryRequest",
    "OrderStatsResponse",
    # Inventory
    "InventoryCreateRequest",
    "InventoryUpdateRequest",
    "InventoryResponse",
    "InventoryQueryRequest",
    "InventoryStatsResponse",
    # Fulfillment
    "FulfillmentCreateRequest",
    "FulfillmentUpdateRequest",
    "FulfillmentResponse",
    "FulfillmentStatsResponse",
    # Supplier
    "SupplierCreateRequest",
    "SupplierUpdateRequest",
    "SupplierResponse",
    "SupplierQueryRequest",
    # Scheduling
    "ScheduleTaskCreateRequest",
    "ScheduleTaskUpdateRequest",
    "ScheduleTaskResponse",
    "AISuggestRequest",
    "AgentInvokeRequest",
    "PipelineRunRequest",
]