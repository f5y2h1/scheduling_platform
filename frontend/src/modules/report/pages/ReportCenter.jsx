import React, { useEffect, useState } from 'react';
import { Row, Col, Card, Table, Button, Spin } from 'antd';
import { DownloadOutlined } from '@ant-design/icons';
import ReactEChartsCore from 'echarts-for-react/lib/core';
import * as echarts from 'echarts/core';
import { LineChart, BarChart } from 'echarts/charts';
import { GridComponent, TooltipComponent, LegendComponent } from 'echarts/components';
import { CanvasRenderer } from 'echarts/renderers';
import { reportAPI } from '@/services/api';

echarts.use([LineChart, BarChart, GridComponent, TooltipComponent, LegendComponent, CanvasRenderer]);

export default function ReportCenter() {
  const [loading, setLoading] = useState(false);
  const [efficiency, setEfficiency] = useState(null);
  const [aiUsage, setAiUsage] = useState(null);
  const [trend, setTrend] = useState([]);

  useEffect(() => {
    setLoading(true);
    Promise.all([
      reportAPI.getSchedulingEfficiency(),
      reportAPI.getAiUsage(),
      reportAPI.getOrderTrend(30),
    ]).then(([e, a, t]) => {
      setEfficiency(e);
      setAiUsage(a);
      setTrend(t);
    }).finally(() => setLoading(false));
  }, []);

  const trendOption = {
    tooltip: { trigger: 'axis' },
    grid: { left: 50, right: 20, top: 20, bottom: 30 },
    xAxis: { type: 'category', data: trend.map((t) => t.date) },
    yAxis: { type: 'value' },
    series: [
      { name: '订单量', type: 'line', data: trend.map((t) => t.count),
        smooth: true, lineStyle: { width: 2, color: '#4f46e5' },
        areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(79,70,229,0.2)' },
          { offset: 1, color: 'rgba(79,70,229,0.02)' },
        ])},
      },
    ],
  };

  const efficiencyOption = {
    tooltip: { trigger: 'axis' },
    grid: { left: 50, right: 20, top: 20, bottom: 30 },
    xAxis: { type: 'category', data: efficiency?.monthlyData?.map((d) => d.month) || [] },
    yAxis: { type: 'value', min: 85, max: 100 },
    series: [{
      name: '调度效率(%)', type: 'bar',
      data: efficiency?.monthlyData?.map((d) => d.efficiency) || [],
      itemStyle: { borderRadius: [6, 6, 0, 0], color: '#4f46e5' },
      barWidth: 40,
    }],
  };

  const aiColumns = [
    { title: 'Agent', dataIndex: 'agent', key: 'agent' },
    { title: '调用次数', dataIndex: 'calls', key: 'calls',
      render: (v) => v?.toLocaleString() },
  ];
  const modelColumns = [
    { title: '模型', dataIndex: 'model', key: 'model' },
    { title: '调用次数', dataIndex: 'calls', key: 'calls',
      render: (v) => v?.toLocaleString() },
  ];

  if (loading) return <Spin size="large" style={{ display: 'block', marginTop: 120 }} />;

  return (
    <div>
      <h2 style={{ marginBottom: 24, color: '#e2e8f0', fontSize: 22, fontWeight: 700 }}>
        📊 数据报表中心
      </h2>

      <Row gutter={[16, 16]}>
        <Col xs={24} lg={12}>
          <Card title="📈 30天订单趋势" style={{ borderRadius: 12 }}>
            <ReactEChartsCore echarts={echarts} option={trendOption} style={{ height: 300 }} />
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card title="📊 调度效率趋势" style={{ borderRadius: 12 }}>
            <ReactEChartsCore echarts={echarts} option={efficiencyOption} style={{ height: 300 }} />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        <Col xs={24} lg={12}>
          <Card title="🤖 AI Agent 调用分布" style={{ borderRadius: 12 }}>
            <Table columns={aiColumns} dataSource={aiUsage?.byAgent || []}
              rowKey="agent" pagination={false} size="small" />
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card title="🔧 AI 模型使用分布" style={{ borderRadius: 12 }}
            extra={<Button size="small" icon={<DownloadOutlined />}>导出</Button>}>
            <Table columns={modelColumns} dataSource={aiUsage?.byModel || []}
              rowKey="model" pagination={false} size="small" />
          </Card>
        </Col>
      </Row>

      <Card title="📋 关键指标汇总" style={{ borderRadius: 12, marginTop: 16 }}>
        <Row gutter={24}>
          <Col span={6}><strong>平均处理时间:</strong> {efficiency?.avgProcessingTime || '-'}</Col>
          <Col span={6}><strong>准时率:</strong> {efficiency?.onTimeRate || '-'}</Col>
          <Col span={6}><strong>单均成本:</strong> {efficiency?.costPerOrder || '-'}</Col>
          <Col span={6}><strong>AI总调用:</strong> {aiUsage?.totalCalls?.toLocaleString() || '-'}</Col>
        </Row>
      </Card>
    </div>
  );
}
