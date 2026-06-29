"""供应商相关 Schema"""
from datetime import datetime

from pydantic import BaseModel, Field


class SupplierCreateRequest(BaseModel):
    name: str = Field(..., description="供应商名称")
    code: str | None = Field(None, description="供应商编码")
    type: str | None = Field(None, description="供应商类型")
    contact_name: str | None = Field(None, description="联系人")
    contact_phone: str | None = Field(None, max_length=20, description="联系电话")
    contact_email: str | None = Field(None, description="联系邮箱")
    address: str | None = Field(None, description="地址")
    rating: float | None = Field(None, ge=0, le=5, description="评分")
    cooperation_years: int | None = Field(None, ge=0, description="合作年限")
    on_time_delivery_rate: float | None = Field(None, ge=0, le=100, description="准时交货率")
    quality_pass_rate: float | None = Field(None, ge=0, le=100, description="质量合格率")


class SupplierUpdateRequest(BaseModel):
    name: str | None = Field(None, description="供应商名称")
    type: str | None = Field(None, description="供应商类型")
    contact_name: str | None = Field(None, description="联系人")
    contact_phone: str | None = Field(None, max_length=20, description="联系电话")
    contact_email: str | None = Field(None, description="联系邮箱")
    address: str | None = Field(None, description="地址")
    rating: float | None = Field(None, ge=0, le=5, description="评分")
    cooperation_years: int | None = Field(None, ge=0, description="合作年限")
    on_time_delivery_rate: float | None = Field(None, ge=0, le=100, description="准时交货率")
    quality_pass_rate: float | None = Field(None, ge=0, le=100, description="质量合格率")
    status: str | None = Field(None, description="状态")


class SupplierResponse(BaseModel):
    id: int
    name: str
    code: str | None
    type: str | None
    status: str
    contact_name: str | None
    contact_phone: str | None
    contact_email: str | None
    address: str | None
    rating: float | None
    cooperation_years: int | None
    on_time_delivery_rate: float | None
    quality_pass_rate: float | None
    created_at: datetime
    updated_at: datetime


class SupplierQueryRequest(BaseModel):
    keyword: str | None = None
    type: str | None = None
    status: str | None = None