"""履约相关 Schema"""
from datetime import datetime

from pydantic import BaseModel, Field


class FulfillmentCreateRequest(BaseModel):
    order_no: str = Field(..., description="订单号")
    type: str = Field("DELIVERY", description="履约类型")
    carrier_name: str | None = Field(None, description="承运商名称")
    tracking_number: str | None = Field(None, description="运单号")
    warehouse_name: str | None = Field(None, description="仓库名称")
    origin_address: str | None = Field(None, description="发货地址")
    destination_address: str | None = Field(None, description="收货地址")
    estimated_delivery: datetime | None = Field(None, description="预计送达时间")


class FulfillmentUpdateRequest(BaseModel):
    status: str | None = Field(None, description="状态")
    carrier_name: str | None = Field(None, description="承运商名称")
    tracking_number: str | None = Field(None, description="运单号")
    logistics_info: str | None = Field(None, description="物流信息")
    actual_delivery: datetime | None = Field(None, description="实际送达时间")
    signed_at: datetime | None = Field(None, description="签收时间")
    signed_by: str | None = Field(None, description="签收人")


class FulfillmentResponse(BaseModel):
    id: int
    fulfillment_no: str
    order_no: str | None
    type: str
    status: str
    carrier_name: str | None
    tracking_number: str | None
    warehouse_name: str | None
    origin_address: str | None
    destination_address: str | None
    logistics_info: str | None
    estimated_delivery: datetime | None
    actual_delivery: datetime | None
    signed_at: datetime | None
    signed_by: str | None
    created_at: datetime
    updated_at: datetime


class FulfillmentStatsResponse(BaseModel):
    pending: int
    in_transit: int
    signed: int