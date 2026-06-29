/**
 * AI 智能看板页面
 * 特点：现代化卡片布局、流畅动画、清晰的工作流可视化
 * 模型选择已移除，默认使用 qwen-plus
 */
import React, { useEffect, useState } from 'react';
import {
  Row, Col, Card, Input, Button, Space, Tag, Spin,
  Collapse, Avatar, Timeline, Badge, Divider,
} from 'antd';
import {
  RobotOutlined, ThunderboltOutlined, SendOutlined,
  ReloadOutlined, ApiOutlined, ExperimentOutlined,
  BulbOutlined, SafetyOutlined, ControlOutlined,
  DollarOutlined, InboxOutlined, ScheduleOutlined,
  CheckCircleOutlined, FireOutlined,
} from '@ant-design/icons';
import { aiAPI } from '@/services/api';

const { TextArea } = Input;

const agentIcons = {
  demand_forecast: <BulbOutlined />,
  inventory_optimization: <InboxOutlined />,
  scheduling_decision: <ScheduleOutlined />,
  cost_optimization: <DollarOutlined />,
  risk_control: <SafetyOutlined />,
  execution_control: <ControlOutlined />,
};

const agentColors = {
  demand_forecast: '#8b5cf6',
  inventory_optimization: '#10b981',
  scheduling_decision: '#3b82f6',
  cost_optimization: '#f59e0b',
  risk_control: '#ef4444',
  execution_control: '#06b6d4',
};

export default function AIDashboard() {
  const [agents, setAgents] = useState([]);
  const [selectedAgent, setSelectedAgent] = useState(null);
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [pipelineResult, setPipelineResult] = useState(null);
  const [pipelineLoading, setPipelineLoading] = useState(false);

  useEffect(() => {
    aiAPI.getAgents()
      .then(setAgents)
      .catch(() => {});
  }, []);

  const handleInvokeAgent = async () => {
    if (!selectedAgent) { return; }
    if (!query.trim()) { return; }
    setLoading(true);
    setResult(null);
    try {
      const res = await aiAPI.invokeAgent(selectedAgent, {
        // model 参数已隐藏，默认使用 qwen-plus
        query: query,
      });
      setResult(res);
    } catch (e) { /* */ }
    setLoading(false);
  };

  const handleRunPipeline = async () => {
    if (!query.trim()) { return; }
    setPipelineLoading(true);
    setPipelineResult(null);
    try {
      const res = await aiAPI.runPipeline({
        // model 参数已隐藏，默认使用 qwen-plus
        query: query,
      });
      setPipelineResult(res);
    } catch (e) { /* */ }
    setPipelineLoading(false);
  };

  const stepLabels = [
    { key: 'demandForecast', label: '需求预测', icon: <BulbOutlined />, color: '#8b5cf6' },
    { key: 'inventoryOptimization', label: '库存优化', icon: <InboxOutlined />, color: '#10b981' },
    { key: 'schedulingDecision', label: '调度决策', icon: <ScheduleOutlined />, color: '#3b82f6' },
    { key: 'costOptimization', label: '成本优化', icon: <DollarOutlined />, color: '#f59e0b' },
    { key: 'riskControl', label: '风险控制', icon: <SafetyOutlined />, color: '#ef4444' },
    { key: 'executionControl', label: '执行管控', icon: <ControlOutlined />, color: '#06b6d4' },
  ];

  return (
    <div>
      {/* 页面标题 */}
      <div style={{ marginBottom: 24 }}>
        <Row align="middle" gutter={16}>
          <Col>
            <div style={{
              width: 56,
              height: 56,
              borderRadius: 16,
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: 28,
              boxShadow: '0 8px 24px rgba(102, 126, 234, 0.35)',
            }}>
              <RobotOutlined style={{ color: '#fff' }} />
            </div>
          </Col>
          <Col flex="auto">
            <h1 style={{ margin: 0, fontSize: 24, fontWeight: 700, color: '#1e1b4b' }}>
              AI 智能看板
            </h1>
            <p style={{ margin: 4, color: '#666', fontSize: 14 }}>
              多 Agent 协作的智能调度系统
            </p>
          </Col>
        </Row>
      </div>

      {/* Agent 卡片 */}
      <Card
        title={
          <Space>
            <RobotOutlined style={{ color: '#667eea' }} />
            <span>业务 Agent 列表</span>
          </Space>
        }
        style={{ borderRadius: 16, marginBottom: 24 }}
      >
        <Row gutter={[12, 12]}>
          {agents.map((agent) => (
            <Col xs={24} sm={12} md={8} lg={4} key={agent.id}>
              <Card
                hoverable
                size="small"
                style={{
                  borderRadius: 12,
                  textAlign: 'center',
                  borderColor: selectedAgent === agent.id ? agentColors[agent.id] || '#4f46e5' : undefined,
                  borderWidth: selectedAgent === agent.id ? 2 : 1,
                  background: selectedAgent === agent.id ? `${agentColors[agent.id]}08` : undefined,
                  cursor: 'pointer',
                  transition: 'all 0.2s',
                }}
                onClick={() => setSelectedAgent(selectedAgent === agent.id ? null : agent.id)}
              >
                <div style={{
                  fontSize: 28,
                  color: agentColors[agent.id] || '#4f46e5',
                  marginBottom: 8,
                }}>
                  {agentIcons[agent.id] || <ExperimentOutlined />}
                </div>
                <div style={{ fontWeight: 600, fontSize: 13, marginBottom: 4 }}>{agent.name}</div>
                <div style={{ fontSize: 11, color: '#888' }}>{agent.description}</div>
                {selectedAgent === agent.id && (
                  <Tag color={agentColors[agent.id]} style={{ marginTop: 8 }}>
                    已选择
                  </Tag>
                )}
              </Card>
            </Col>
          ))}
        </Row>
      </Card>

      {/* Agent 调用区域 */}
      <Row gutter={[24, 24]}>
        <Col xs={24} lg={14}>
          <Card
            title={
              <Space>
                <RobotOutlined style={{ color: '#4f46e5' }} />
                <span>Agent 推理测试</span>
                {selectedAgent && (
                  <Tag color={agentColors[selectedAgent]}>
                    {agents.find(a => a.id === selectedAgent)?.name}
                  </Tag>
                )}
              </Space>
            }
            style={{ borderRadius: 16 }}
          >
            <Space direction="vertical" size="middle" style={{ width: '100%' }}>
              <div>
                <div style={{ fontWeight: 600, marginBottom: 8, color: '#1e1b4b' }}>
                  <FireOutlined style={{ color: '#ef4444', marginRight: 8 }} />
                  输入查询内容
                </div>
                <TextArea
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="输入查询内容，如：预测下周华为Mate 60在北京仓的需求量"
                  rows={3}
                  style={{ borderRadius: 12, fontSize: 15 }}
                />
              </div>

              <Space>
                <Button
                  type="primary"
                  icon={<SendOutlined />}
                  loading={loading}
                  onClick={handleInvokeAgent}
                  disabled={!selectedAgent}
                  style={{
                    borderRadius: 10,
                    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                    border: 'none',
                  }}
                >
                  调用 Agent
                </Button>
                <Button
                  icon={<ThunderboltOutlined />}
                  loading={pipelineLoading}
                  onClick={handleRunPipeline}
                  style={{
                    borderRadius: 10,
                    borderColor: '#8b5cf6',
                    color: '#8b5cf6',
                  }}
                >
                  运行全流程流水线
                </Button>
              </Space>
            </Space>

            {/* Agent 结果展示 */}
            {loading && (
              <div style={{ textAlign: 'center', padding: 40 }}>
                <Spin tip="AI 正在推理..." />
              </div>
            )}
            {result && (
              <Card
                size="small"
                title={
                  <Space>
                    <CheckCircleOutlined style={{ color: '#10b981' }} />
                    <span>推理结果</span>
                  </Space>
                }
                style={{
                  background: '#fafbff',
                  borderRadius: 12,
                  marginTop: 16,
                  borderLeft: '4px solid #4f46e5',
                }}
              >
                <pre style={{
                  whiteSpace: 'pre-wrap',
                  fontSize: 13,
                  lineHeight: 1.7,
                  margin: 0,
                  maxHeight: 400,
                  overflow: 'auto',
                }}>
                  {typeof result.result === 'string' ? result.result : JSON.stringify(result, null, 2)}
                </pre>
              </Card>
            )}
          </Card>
        </Col>

        <Col xs={24} lg={10}>
          <Card
            title={
              <Space>
                <ApiOutlined style={{ color: '#10b981' }} />
                <span>Agent 说明</span>
              </Space>
            }
            style={{ borderRadius: 16 }}
          >
            <Timeline
              items={[
                { color: '#8b5cf6', children: (
                  <div>
                    <strong style={{ color: '#8b5cf6' }}>需求预测 Agent</strong>
                    <p style={{ margin: '4px 0', fontSize: 12, color: '#666' }}>
                      分析历史数据，预测未来需求趋势
                    </p>
                  </div>
                )},
                { color: '#10b981', children: (
                  <div>
                    <strong style={{ color: '#10b981' }}>库存优化 Agent</strong>
                    <p style={{ margin: '4px 0', fontSize: 12, color: '#666' }}>
                      计算最优库存策略，降低库存成本
                    </p>
                  </div>
                )},
                { color: '#3b82f6', children: (
                  <div>
                    <strong style={{ color: '#3b82f6' }}>调度决策 Agent</strong>
                    <p style={{ margin: '4px 0', fontSize: 12, color: '#666' }}>
                      制定智能调度方案，优化资源分配
                    </p>
                  </div>
                )},
                { color: '#f59e0b', children: (
                  <div>
                    <strong style={{ color: '#f59e0b' }}>成本优化 Agent</strong>
                    <p style={{ margin: '4px 0', fontSize: 12, color: '#666' }}>
                      分析成本结构，提出优化建议
                    </p>
                  </div>
                )},
                { color: '#ef4444', children: (
                  <div>
                    <strong style={{ color: '#ef4444' }}>风险控制 Agent</strong>
                    <p style={{ margin: '4px 0', fontSize: 12, color: '#666' }}>
                      识别潜在风险，提供预警方案
                    </p>
                  </div>
                )},
                { color: '#06b6d4', children: (
                  <div>
                    <strong style={{ color: '#06b6d4' }}>执行管控 Agent</strong>
                    <p style={{ margin: '4px 0', fontSize: 12, color: '#666' }}>
                      监督执行落地，确保方案实施
                    </p>
                  </div>
                )},
              ]}
            />
          </Card>
        </Col>
      </Row>

      {/* 流水线结果 */}
      {pipelineLoading && (
        <Card style={{ borderRadius: 16, marginTop: 24, textAlign: 'center' }}>
          <Spin tip="全流程Agent流水线运行中 (6/6)..." />
        </Card>
      )}
      {pipelineResult && (
        <Card
          title={
            <Space>
              <ThunderboltOutlined style={{ color: '#8b5cf6' }} />
              <span>Agent 流水线结果</span>
            </Space>
          }
          style={{ borderRadius: 16, marginTop: 24 }}
        >
          <Timeline
            items={stepLabels.map((step) => ({
              color: step.color,
              dot: step.icon,
              children: (
                <Collapse
                  ghost
                  items={[{
                    key: step.key,
                    label: <span style={{ fontWeight: 600 }}>{step.label}</span>,
                    children: (
                      <pre style={{
                        whiteSpace: 'pre-wrap',
                        fontSize: 12,
                        lineHeight: 1.6,
                        maxHeight: 200,
                        overflow: 'auto',
                        background: '#f9fafb',
                        padding: 12,
                        borderRadius: 8,
                      }}>
                        {typeof pipelineResult[step.key] === 'string'
                          ? pipelineResult[step.key]
                          : JSON.stringify(pipelineResult[step.key], null, 2)}
                      </pre>
                    ),
                  }]}
                />
              ),
            }))}
          />
        </Card>
      )}
    </div>
  );
}
