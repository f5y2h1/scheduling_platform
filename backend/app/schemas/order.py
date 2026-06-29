"""订单相关 Schema"""
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class OrderCreateRequest(BaseModel):
    order_type: str = Field("SALE", description="订单类型")
    customer_name: str = Field(..., description="客户名称")
    product_name: str = Field(..., description="产品名称")
    quantity: int = Field(..., gt=0, description="数量")
    unit_price: Decimal | None = Field(None, description="单价")
    total_amount: Decimal | None = Field(None, description="总金额")
    warehouse_name: str | None = Field(None, description="仓库名称")
    shipping_address: str | None = Field(None, description="收货地址")
    required_date: datetime | None = Field(None, description="要求交付日期")
    remark: str | None = Field(None, max_length=256, description="备注")


class OrderUpdateRequest(BaseModel):
    status: str | None = Field(None, description="订单状态")
    warehouse_name: str | None = Field(None, description="仓库名称")
    shipped_date: datetime | None = Field(None, description="发货日期")
    delivered_date: datetime | None = Field(None, description="送达日期")
    remark: str | None = Field(None, max_length=256, description="备注")


class OrderResponse(BaseModel):
    id: int
    order_no: str
    order_type: str
    status: str
    customer_name: str | None
    product_name: str | None
    quantity: int
    unit_price: Decimal | None
    total_amount: Decimal | None
    warehouse_name: str | None
    shipping_address: str | None
    required_date: datetime | None
    shipped_date: datetime | None
    delivered_date: datetime | None
    remark: str | None
    created_by: str | None
    created_at: datetime
    updated_at: datetime


class OrderQueryRequest(BaseModel):
    keyword: str | None = None
    status: str | None = None
    order_type: str | None = None


class OrderStatsResponse(BaseModel):
    pending: int
    processing: int
    shipped: int
    delivered: int
    cancelled: int
    total_amount: float