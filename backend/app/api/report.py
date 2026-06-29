"""数据报表 API"""
import datetime, random
from fastapi import APIRouter, Depends
from app.models.user import User
from app.schemas.common import ApiResponse
from app.utils.auth import get_current_user

router = APIRouter()


@router.get("/dashboard")
async def dashboard(_: User = Depends(get_current_user)):
    r = random.Random()
    return ApiResponse.ok({
        "order_stats": {"total_today": r.randint(50, 250), "pending_count": r.randint(5, 35),
                         "completed_rate": round(92.5 + r.random() * 5, 1), "trend": "+12.5%"},
        "inventory_stats": {"total_skus": 1568, "low_stock_count": r.randint(3, 23),
                            "out_of_stock_count": r.randint(0, 5),
                            "turnover_rate": round(8.5 + r.random() * 3, 1)},
        "scheduling_stats": {"pending_tasks": r.randint(2, 17), "completed_today": r.randint(10, 60),
                              "ai_suggestion_rate": round(78.3 + r.random() * 10, 1),
                              "avg_cost": f"¥{1250 + r.random() * 500:.2f}"},
        "ai_stats": {"total_calls": 12580, "today_calls": r.randint(50, 250),
                     "avg_response_time": round(1.2 + r.random() * 0.8, 1),
                     "cost_saved": "¥12,580"},
    })


@router.get("/order-trend")
async def order_trend(days: int = 7, _: User = Depends(get_current_user)):
    r = random.Random()
    trend = []
    for i in range(days - 1, -1, -1):
        date = datetime.date.today() - datetime.timedelta(days=i)
        trend.append({"date": date.strftime("%m-%d"), "count": r.randint(50, 150),
                       "amount": r.randint(10000, 60000)})
    return ApiResponse.ok(trend)


@router.get("/inventory-overview")
async def inventory_overview(_: User = Depends(get_current_user)):
    return ApiResponse.ok({
        "by_warehouse": [{"name": "北京仓", "value": 4500}, {"name": "上海仓", "value": 3800},
                          {"name": "广州仓", "value": 3200}, {"name": "成都仓", "value": 2100}],
        "by_category": [{"name": "电子产品", "value": 35}, {"name": "食品饮料", "value": 25},
                         {"name": "服装鞋帽", "value": 20}, {"name": "日用品", "value": 15},
                         {"name": "其他", "value": 5}],
    })


@router.get("/scheduling-efficiency")
async def scheduling_efficiency(_: User = Depends(get_current_user)):
    return ApiResponse.ok({
        "avg_processing_time": "2.5小时", "on_time_rate": "94.8%", "cost_per_order": "¥35.2",
        "monthly_data": [{"month": "5月", "efficiency": 92.0},
                          {"month": "6月", "efficiency": 93.5},
                          {"month": "7月", "efficiency": 94.8}],
    })


@router.get("/ai-usage")
async def ai_usage(_: User = Depends(get_current_user)):
    return ApiResponse.ok({
        "total_calls": 12580,
        "by_model": [{"model": "qwen3.5-omni-plus", "calls": 8500},
                      {"model": "text-embedding-v2", "calls": 4080}],
        "by_agent": [{"agent": "需求预测", "calls": 2800}, {"agent": "库存优化", "calls": 2500},
                      {"agent": "调度决策", "calls": 3200}, {"agent": "成本优化", "calls": 1800},
                      {"agent": "风险控制", "calls": 1500}, {"agent": "执行管控", "calls": 780}],
    })


@router.get("/export/{report_type}")
async def export_report(report_type: str, _: User = Depends(get_current_user)):
    return ApiResponse.ok(f"报表导出任务已创建，类型: {report_type}，请稍后在下载中心查看")
