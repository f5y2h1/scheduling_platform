"""库存相关 Schema"""
from datetime import datetime

from pydantic import BaseModel, Field


class InventoryCreateRequest(BaseModel):
    product_id: int | None = Field(None, description="产品ID")
    product_name: str = Field(..., description="产品名称")
    sku_code: str | None = Field(None, description="SKU编码")
    warehouse_id: int | None = Field(None, description="仓库ID")
    warehouse_name: str | None = Field(None, description="仓库名称")
    quantity: int = Field(0, ge=0, description="库存数量")
    safety_stock: int = Field(0, ge=0, description="安全库存")
    locked_quantity: int = Field(0, ge=0, description="锁定数量")
    available_quantity: int = Field(0, ge=0, description="可用数量")


class InventoryUpdateRequest(BaseModel):
    quantity: int | None = Field(None, ge=0, description="库存数量")
    safety_stock: int | None = Field(None, ge=0, description="安全库存")
    locked_quantity: int | None = Field(None, ge=0, description="锁定数量")
    available_quantity: int | None = Field(None, ge=0, description="可用数量")
    status: str | None = Field(None, description="状态")
    last_check_date: datetime | None = Field(None, description="最后盘点日期")


class InventoryResponse(BaseModel):
    id: int
    product_id: int | None
    product_name: str | None
    sku_code: str | None
    warehouse_id: int | None
    warehouse_name: str | None
    quantity: int
    safety_stock: int
    locked_quantity: int
    available_quantity: int
    status: str
    last_check_date: datetime | None
    created_at: datetime
    updated_at: datetime


class InventoryQueryRequest(BaseModel):
    keyword: str | None = None
    warehouse_id: int | None = None
    status: str | None = None


class InventoryStatsResponse(BaseModel):
    total_items: int
    low_stock_items: int
    total_quantity: int