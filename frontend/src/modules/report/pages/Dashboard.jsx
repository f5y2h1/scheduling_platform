import { useEffect, useState } from 'react';
import { Row, Col, Card, Spin, Table } from 'antd';
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

export default function Dashboard() {
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState(null);

  useEffect(() => {
    reportAPI.getDashboard().then(setData).finally(() => setLoading(false));
  }, []);

  if (loading) return <Spin size="large" style={{ display: 'block', marginTop: 120 }} />;
  if (!data) return null;

  const orderTrendOption = {
    tooltip: { trigger: 'axis' },
    grid: { left: 40, right: 20, top: 20, bottom: 30 },
    xAxis: { type: 'category', data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'] },
    yAxis: { type: 'value' },
    series: [
      {
        name: '订单量', type: 'line',
        data: [65, 78, 82, 95, 110, 88, 72],
        smooth: true, lineStyle: { width: 3, color: '#4f46e5' },
        itemStyle: { color: '#4f46e5' },
        areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(79,70,229,0.25)' },
          { offset: 1, color: 'rgba(79,70,229,0.02)' },
        ])},
      },
    ],
  };

  const warehouseOption = {
    tooltip: { trigger: 'item' },
    series: [{
      type: 'pie', radius: ['55%', '80%'],
      center: ['50%', '50%'],
      itemStyle: { borderRadius: 6, borderColor: '#fff', borderWidth: 3 },
      label: { show: false },
      data: [
        { value: 4500, name: '北京仓', itemStyle: { color: '#4f46e5' } },
        { value: 3800, name: '上海仓', itemStyle: { color: '#10b981' } },
        { value: 3200, name: '广州仓', itemStyle: { color: '#f59e0b' } },
        { value: 2100, name: '成都仓', itemStyle: { color: '#3b82f6' } },
      ],
    }],
  };

  const recentOrders = [
    { orderNo: 'SO20260627001', customer: '华东科技', status: 'shipped', amount: '¥12,580' },
    { orderNo: 'SO20260627002', customer: '南方制造', status: 'pending', amount: '¥8,320' },
    { orderNo: 'SO20260627003', customer: '北方电子', status: 'delivered', amount: '¥23,450' },
    { orderNo: 'SO20260627004', customer: '西部物流', status: 'processing', amount: '¥5,680' },
    { orderNo: 'SO20260627005', customer: '中部商贸', status: 'processing', amount: '¥15,900' },
  ];

  const orderColumns = [
    { title: '订单号', dataIndex: 'orderNo', key: 'orderNo' },
    { title: '客户', dataIndex: 'customer', key: 'customer' },
    { title: '状态', dataIndex: 'status', key: 'status', render: (s) => <StatusTag status={s} /> },
    { title: '金额', dataIndex: 'amount', key: 'amount' },
  ];

  return (
    <div>
      <PageHeader title="仪表盘概览" breadcrumb={[{ title: '首页' }]} />

      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} lg={6}>
          <StatCard title="今日订单" value={data.orderStats?.totalToday || 0}
            icon={<ShoppingCartOutlined />} color="#4f46e5" trend="+12.5%" trendType="up" />
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <StatCard title="SKU总数" value={data.inventoryStats?.totalSkus || 0}
            icon={<InboxOutlined />} color="#10b981" />
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <StatCard title="待调度任务" value={data.schedulingStats?.pendingTasks || 0}
            icon={<ScheduleOutlined />} color="#f59e0b" trend="-5.2%" trendType="down" />
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <StatCard title="履约完成率" value={(data.orderStats?.completedRate || 0).toFixed(1)}
            suffix="%" icon={<CarOutlined />} color="#3b82f6" trend="+2.3%" trendType="up" />
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        <Col xs={24} sm={12} lg={6}>
          <StatCard title="AI调用次数" value={data.aiStats?.todayCalls || 0}
            icon={<RobotOutlined />} color="#8b5cf6" />
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <StatCard title="AI节省成本" value={data.aiStats?.costSaved || 0}
            icon={<RobotOutlined />} color="#ec4899" />
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <StatCard title="库存预警" value={data.inventoryStats?.lowStockCount || 0}
            icon={<InboxOutlined />} color="#ef4444" />
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <StatCard title="AI方案采纳率" value={(data.schedulingStats?.aiSuggestionRate || 0).toFixed(1)}
            suffix="%" icon={<RobotOutlined />} color="#06b6d4" />
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        <Col xs={24} lg={16}>
          <Card title="📈 订单趋势（近7天）" style={{ borderRadius: 12 }}>
            <ReactEChartsCore echarts={echarts} option={orderTrendOption} style={{ height: 320 }} />
          </Card>
        </Col>
        <Col xs={24} lg={8}>
          <Card title="🏭 库存分布" style={{ borderRadius: 12 }}>
            <ReactEChartsCore echarts={echarts} option={warehouseOption} style={{ height: 320 }} />
          </Card>
        </Col>
      </Row>

      <Card title="📋 最近订单" style={{ borderRadius: 12, marginTop: 16 }}>
        <Table columns={orderColumns} dataSource={recentOrders} rowKey="orderNo" pagination={false} size="middle" />
      </Card>
    </div>
  );
}