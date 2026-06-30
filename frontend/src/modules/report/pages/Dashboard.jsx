import { useEffect, useState } from 'react';
import { Row, Col, Card, Spin, Table, Empty } from 'antd';
import {
  ShoppingCartOutlined, InboxOutlined, ScheduleOutlined,
  CarOutlined, RobotOutlined,
} from '@ant-design/icons';
import ReactEChartsCore from 'echarts-for-react/lib/core';
import * as echarts from 'echarts/core';
import { LineChart, BarChart, PieChart } from 'echarts/charts';
import { GridComponent, TooltipComponent, LegendComponent } from 'echarts/components';
import { CanvasRenderer } from 'echarts/renderers';
import { reportAPI } from '@/services/api';
import { StatCard, StatusTag, PageHeader } from '@/components/common';

echarts.use([LineChart, BarChart, PieChart, GridComponent, TooltipComponent, LegendComponent, CanvasRenderer]);

const COLORS = ['#4f46e5', '#10b981', '#f59e0b', '#3b82f6', '#ef4444', '#8b5cf6'];

export default function Dashboard() {
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState(null);
  const [trend, setTrend] = useState([]);
  const [inventoryOverview, setInventoryOverview] = useState(null);

  useEffect(() => {
    Promise.all([
      reportAPI.getDashboard(),
      reportAPI.getOrderTrend(7).catch(() => []),
      reportAPI.getInventoryOverview().catch(() => null),
    ]).then(([d, t, inv]) => {
      setData(d);
      setTrend(t);
      setInventoryOverview(inv);
    }).finally(() => setLoading(false));
  }, []);

  if (loading) return <Spin size="large" style={{ display: 'block', marginTop: 120 }} />;
  if (!data) return <Empty description="无法加载数据" style={{ marginTop: 80 }} />;

  // === 订单趋势图（真实数据） ===
  const orderTrendOption = {
    tooltip: { trigger: 'axis' },
    grid: { left: 40, right: 20, top: 20, bottom: 30 },
    xAxis: { type: 'category', data: trend.map(t => t.date) },
    yAxis: { type: 'value', minInterval: 1 },
    series: [{
      name: '订单量', type: 'line',
      data: trend.map(t => t.count),
      smooth: true, lineStyle: { width: 3, color: '#4f46e5' },
      itemStyle: { color: '#4f46e5' },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(79,70,229,0.25)' },
          { offset: 1, color: 'rgba(79,70,229,0.02)' },
        ]),
      },
    }],
  };

  // === 仓库库存分布图（真实数据） ===
  const warehouses = inventoryOverview?.byWarehouse || [];
  const warehouseOption = {
    tooltip: { trigger: 'item', formatter: '{b}: {c} 件 ({d}%)' },
    series: [{
      type: 'pie', radius: ['55%', '80%'],
      center: ['50%', '50%'],
      itemStyle: { borderRadius: 6, borderColor: '#fff', borderWidth: 3 },
      label: { show: false },
      data: warehouses.length > 0
        ? warehouses.map((w, i) => ({
            value: w.totalQty,
            name: w.name,
            itemStyle: { color: COLORS[i % COLORS.length] },
          }))
        : [{ value: 1, name: '无数据', itemStyle: { color: '#d9d9d9' } }],
    }],
  };

  // === 库存状态分布图 ===
  const statusData = inventoryOverview?.byStatus || [];
  const statusChartOption = {
    tooltip: { trigger: 'axis' },
    grid: { left: 40, right: 20, top: 10, bottom: 30 },
    xAxis: { type: 'category', data: statusData.map(s => {
      const labels = { NORMAL: '正常', LOW: '低库存', OVERSTOCK: '积压', OUT_OF_STOCK: '缺货' };
      return labels[s.status] || s.status;
    }) },
    yAxis: { type: 'value', minInterval: 1 },
    series: [{
      name: 'SKU 数量', type: 'bar',
      data: statusData.map((s, i) => ({
        value: s.count,
        itemStyle: { color: COLORS[i % COLORS.length], borderRadius: [6, 6, 0, 0] },
      })),
      barWidth: 30,
    }],
  };

  const stats = data.orderStats || {};
  const invStats = data.inventoryStats || {};
  const schStats = data.schedulingStats || {};

  return (
    <div>
      <PageHeader title="仪表盘概览" breadcrumb={[{ title: '首页' }]} />

      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} lg={6}>
          <StatCard title="订单总数" value={stats.totalOrders || 0}
            icon={<ShoppingCartOutlined />} color="#4f46e5" />
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <StatCard title="SKU总数" value={invStats.totalSkus || 0}
            icon={<InboxOutlined />} color="#10b981" />
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <StatCard title="待调度任务" value={schStats.pendingTasks || 0}
            icon={<ScheduleOutlined />} color="#f59e0b" />
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <StatCard title="订单完成率" value={stats.completedRate || 0}
            suffix="%" icon={<CarOutlined />} color="#3b82f6" />
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        <Col xs={24} sm={12} lg={6}>
          <StatCard title="待处理订单" value={stats.pendingCount || 0}
            icon={<ShoppingCartOutlined />} color="#ef4444" />
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <StatCard title="库存预警（低库存）" value={invStats.lowStockCount || 0}
            icon={<InboxOutlined />} color="#ef4444" />
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <StatCard title="缺货商品" value={invStats.outOfStockCount || 0}
            icon={<InboxOutlined />} color="#dc2626" />
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <StatCard title="调度任务总数" value={schStats.totalTasks || 0}
            icon={<ScheduleOutlined />} color="#06b6d4" />
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        <Col xs={24} lg={12}>
          <Card title="📈 订单趋势（近7天）" style={{ borderRadius: 12 }}>
            {trend.length > 0 ? (
              <ReactEChartsCore echarts={echarts} option={orderTrendOption} style={{ height: 320 }} />
            ) : (
              <Empty description="暂无订单数据" style={{ padding: 60 }} />
            )}
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card title="🏭 仓库库存分布" style={{ borderRadius: 12 }}>
            {warehouses.length > 0 ? (
              <ReactEChartsCore echarts={echarts} option={warehouseOption} style={{ height: 320 }} />
            ) : (
              <Empty description="暂无仓库数据" style={{ padding: 60 }} />
            )}
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        <Col xs={24} lg={12}>
          <Card title="📊 库存状态分布" style={{ borderRadius: 12 }}>
            {statusData.length > 0 ? (
              <ReactEChartsCore echarts={echarts} option={statusChartOption} style={{ height: 280 }} />
            ) : (
              <Empty description="暂无状态数据" style={{ padding: 60 }} />
            )}
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card title="🤖 AI 智能服务" style={{ borderRadius: 12 }}>
            <div style={{ padding: '30px 20px', textAlign: 'center' }}>
              <div style={{ fontSize: 60, marginBottom: 12 }}>🧠</div>
              <h3 style={{ margin: 0, color: '#e2e8f0', fontSize: 18 }}>
                企业级三层记忆架构 AI Agent
              </h3>
              <p style={{ color: '#94a3b8', marginTop: 8, fontSize: 13, lineHeight: 1.8 }}>
                支持多 Agent 协作调度 · 自然语言工具调用<br />
                RAG 知识库检索 · 全模态语音/图片交互<br />
                工作记忆 + 短期记忆 + 长期记忆 三级体系
              </p>
              <div style={{
                marginTop: 16, padding: 12, borderRadius: 10,
                background: '#f0f9ff', border: '1px solid #bae6fd',
              }}>
                <span style={{ fontSize: 13, color: '#0369a1' }}>
                  🚀 前往 <strong>AI智能服务</strong> 体验智能调度工作流
                </span>
              </div>
            </div>
          </Card>
        </Col>
      </Row>
    </div>
  );
}
