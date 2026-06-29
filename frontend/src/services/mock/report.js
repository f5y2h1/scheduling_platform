const r = () => Math.random();

export const mockReportData = {
  dashboard: () => ({
    orderStats: { totalToday: Math.floor(50 + r() * 200), pendingCount: Math.floor(5 + r() * 30), completedRate: +(92.5 + r() * 5).toFixed(1), trend: '+12.5%' },
    inventoryStats: { totalSkus: 1568, lowStockCount: Math.floor(3 + r() * 20), outOfStockCount: Math.floor(r() * 5), turnoverRate: +(8.5 + r() * 3).toFixed(1) },
    schedulingStats: { pendingTasks: Math.floor(2 + r() * 15), completedToday: Math.floor(10 + r() * 50), aiSuggestionRate: +(78.3 + r() * 10).toFixed(1), avgCost: `¥${(1250 + r() * 500).toFixed(2)}` },
    aiStats: { totalCalls: 12580, todayCalls: Math.floor(50 + r() * 200), avgResponseTime: +(1.2 + r() * 0.8).toFixed(1), costSaved: '¥12,580' },
  }),
  orderTrend: (days = 7) => {
    const trend = [];
    for (let i = days - 1; i >= 0; i--) {
      const date = new Date();
      date.setDate(date.getDate() - i);
      trend.push({ date: `${(date.getMonth() + 1).toString().padStart(2, '0')}-${date.getDate().toString().padStart(2, '0')}`, count: Math.floor(50 + r() * 100), amount: Math.floor(10000 + r() * 50000) });
    }
    return trend;
  },
  inventoryOverview: () => ({
    byWarehouse: [{ name: '北京仓', value: 4500 }, { name: '上海仓', value: 3800 }, { name: '广州仓', value: 3200 }, { name: '成都仓', value: 2100 }],
    byCategory: [{ name: '电子产品', value: 35 }, { name: '食品饮料', value: 25 }, { name: '服装鞋帽', value: 20 }, { name: '日用品', value: 15 }, { name: '其他', value: 5 }],
  }),
  schedulingEfficiency: () => ({
    avgProcessingTime: '2.5小时', onTimeRate: '94.8%', costPerOrder: '¥35.2',
    monthlyData: [{ month: '5月', efficiency: 92.0 }, { month: '6月', efficiency: 93.5 }, { month: '7月', efficiency: 94.8 }],
  }),
  aiUsage: () => ({
    totalCalls: 12580,
    byModel: [{ model: 'qwen3.5-omni-plus', calls: 8500 }, { model: 'text-embedding-v2', calls: 4080 }],
    byAgent: [{ agent: '需求预测', calls: 2800 }, { agent: '库存优化', calls: 2500 }, { agent: '调度决策', calls: 3200 }, { agent: '成本优化', calls: 1800 }, { agent: '风险控制', calls: 1500 }, { agent: '执行管控', calls: 780 }],
  }),
};