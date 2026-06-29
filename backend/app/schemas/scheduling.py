"""调度相关 Schema"""
from datetime import datetime

from pydantic import BaseModel, Field


class ScheduleTaskCreateRequest(BaseModel):
    task_type: str = Field("DISPATCH", description="任务类型")
    order_no: str | None = Field(None, description="关联订单号")
    from_warehouse_name: str | None = Field(None, description="出发仓库")
    to_warehouse_name: str | None = Field(None, description="目的仓库")
    product_name: str | None = Field(None, description="产品名称")
    quantity: int = Field(1, gt=0, description="数量")
    remark: str | None = Field(None, max_length=256, description="备注")


class ScheduleTaskUpdateRequest(BaseModel):
    status: str | None = Field(None, description="状态")
    ai_suggestion: str | None = Field(None, description="AI建议")
    ai_model_used: str | None = Field(None, description="使用的AI模型")
    approved_by: str | None = Field(None, description="审批人")
    approved_at: datetime | None = Field(None, description="审批时间")
    remark: str | None = Field(None, max_length=256, description="备注")


class ScheduleTaskResponse(BaseModel):
    id: int
    task_no: str
    task_type: str
    status: str
    order_no: str | None
    from_warehouse_name: str | None
    to_warehouse_name: str | None
    product_name: str | None
    quantity: int
    ai_suggestion: str | None
    ai_model_used: str | None
    approved_by: str | None
    approved_at: datetime | None
    remark: str | None
    created_at: datetime
    updated_at: datetime


class AISuggestRequest(BaseModel):
    model: str | None = Field(None, description="AI模型")
    query: str | None = Field(None, description="查询内容")


class AgentInvokeRequest(BaseModel):
    agent_id: str = Field(..., description="Agent ID")
    model: str | None = Field(None, description="AI模型")
    query: str = Field(..., description="查询内容")


class PipelineRunRequest(BaseModel):
    model: str | None = Field(None, description="AI模型")
    initial_query: str = Field(..., description="初始查询")