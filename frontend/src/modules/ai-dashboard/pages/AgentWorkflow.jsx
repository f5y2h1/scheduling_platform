import React, { useEffect, useState } from 'react';
import {
  Card, Row, Col, Button, Space, Tag, Table,
  Collapse, Spin, message, Modal, Divider, Alert,
  Progress, Empty, Tooltip, Badge,
} from 'antd';
import {
  PlayCircleOutlined, HistoryOutlined, ToolOutlined,
  DeleteOutlined, ReloadOutlined, ApiOutlined,
  BulbOutlined, InboxOutlined, ScheduleOutlined,
  DollarOutlined, SafetyOutlined, ControlOutlined,
  CheckCircleOutlined, LoadingOutlined, RobotOutlined,
  DatabaseOutlined, ClockCircleOutlined, FireOutlined,
  SyncOutlined, RetweetOutlined, WarningOutlined,
} from '@ant-design/icons';
import { aiAPI } from '@/services/api';
import ChatUI from '@/components/chat/ChatUI';

const { Panel } = Collapse;

const stepConfig = [
  { key: 'demand_forecast', label: '需求预测', icon: <BulbOutlined />, color: '#8b5cf6', desc: '分析历史数据预测需求趋势' },
  { key: 'inventory_check', label: '库存检查', icon: <InboxOutlined />, color: '#06b6d4', desc: '检查当前库存状态' },
  { key: 'inventory_optimization', label: '库存优化', icon: <InboxOutlined />, color: '#10b981', desc: '计算最优库存策略' },
  { key: 'scheduling_decision', label: '调度决策', icon: <ScheduleOutlined />, color: '#3b82f6', desc: '制定智能调度方案' },
  { key: 'cost_optimization', label: '成本优化', icon: <DollarOutlined />, color: '#f59e0b', desc: '降低运营成本' },
  { key: 'risk_control', label: '风险控制', icon: <SafetyOutlined />, color: '#ef4444', desc: '识别并规避风险' },
  { key: 'execution_control', label: '执行管控', icon: <ControlOutlined />, color: '#06b6d4', desc: '监督执行落地' },
];

export default function AgentWorkflow() {
  const [tools, setTools] = useState([]);
  const [sessions, setSessions] = useState([]);
  const [sessionId, setSessionId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [currentStep, setCurrentStep] = useState(-1);
  const [result, setResult] = useState(null);
  const [selectedSession, setSelectedSession] = useState(null);
  const [sessionHistory, setSessionHistory] = useState(null);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [showWorkflowResult, setShowWorkflowResult] = useState(false);
  const [pageError, setPageError] = useState(null);

  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    try {
      const [t, s] = await Promise.all([
        aiAPI.getTools().catch(() => []),
        aiAPI.getSessions().catch(() => []),
      ]);
      setTools(t || []);
      setSessions(s || []);
    } catch (e) {
      console.error('加载数据失败:', e);
      message.error('加载数据失败');
    }
  };

  const handleRunWorkflow = async (query) => {
    if (!query.trim()) {
      message.warning('请输入调度需求');
      return;
    }
    setLoading(true);
    setResult(null);
    setCurrentStep(0);
    setShowWorkflowResult(true);
    
    const stepTimer = setInterval(() => {
      setCurrentStep(prev => {
        if (prev >= stepConfig.length) {
          clearInterval(stepTimer);
          return -1;
        }
        return prev + 1;
      });
    }, 800);

    try {
      const res = await aiAPI.runWorkflow({
        query: query,
        session_id: sessionId,
      });
      clearInterval(stepTimer);
      setCurrentStep(-1);
      setResult(res);
      if (res.session_id && !sessionId) {
        setSessionId(res.session_id);
      }
      message.success('工作流执行完成');
      loadInitialData();
    } catch (e) {
      clearInterval(stepTimer);
      setCurrentStep(-1);
      message.error('工作流执行失败');
    }
    setLoading(false);
  };

  const handleContinueSession = (sid) => {
    setSessionId(sid);
    message.info('已切换到指定会话');
  };

  const handleViewHistory = async (sid) => {
    setSelectedSession(sid);
    setHistoryLoading(true);
    try {
      const history = await aiAPI.getSession(sid);
      setSessionHistory(history);
    } catch (e) {
      message.error('获取会话历史失败');
    }
    setHistoryLoading(false);
  };

  const handleDeleteSession = async (sid) => {
    Modal.confirm({
      title: '确认删除',
      content: '确定要删除该会话记录吗？',
      onOk: async () => {
        try {
          await aiAPI.deleteSession(sid);
          message.success('删除成功');
          loadInitialData();
        } catch (e) {
          message.error('删除失败');
        }
      },
    });
  };

  const sessionColumns = [
    {
      title: '会话',
      dataIndex: 'thread_id',
      key: 'thread_id',
      render: (id) => (
        <Tag icon={<HistoryOutlined />} color="purple">{id?.slice(0, 12)}...</Tag>
      ),
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (t) => t ? new Date(t).toLocaleString() : '-',
    },
    {
      title: '操作',
      key: 'action',
      width: 180,
      render: (_, record) => (
        <Space size="small">
          <Button size="small" type="primary" ghost onClick={() => handleContinueSession(record.thread_id)}>
            继续
          </Button>
          <Button size="small" onClick={() => handleViewHistory(record.thread_id)}>
            历史
          </Button>
          <Button size="small" danger type="text" icon={<DeleteOutlined />} onClick={() => handleDeleteSession(record.thread_id)} />
        </Space>
      ),
    },
  ];

  if (pageError) {
    return (
      <div style={{ padding: 40, textAlign: 'center' }}>
        <h2 style={{ color: '#ef4444' }}>页面加载出错</h2>
        <p>{pageError.message}</p>
        <Button onClick={() => setPageError(null)}>刷新重试</Button>
      </div>
    );
  }

  return (
    <div>
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
              Agent 工作流编排
            </h1>
            <p style={{ margin: 4, color: '#666', fontSize: 14 }}>
              基于 LangGraph 的多 Agent 协作调度系统 · 支持聊天对话、语音输入、图片上传
            </p>
          </Col>
          <Col>
            <Space>
              <Tag icon={<RobotOutlined />} color="purple">LangGraph</Tag>
              <Tag icon={<DatabaseOutlined />} color="blue">记忆系统</Tag>
              <Tag icon={<ToolOutlined />} color="green">工具调用</Tag>
              <Tag icon={<SyncOutlined />} color="orange">流式对话</Tag>
            </Space>
          </Col>
        </Row>
      </div>

      <Row gutter={[24, 24]}>
        <Col xs={24} lg={16}>
          {showWorkflowResult ? (
            <>
              <Card
                style={{
                  borderRadius: 16,
                  boxShadow: '0 4px 20px rgba(0, 0, 0, 0.06)',
                  border: 'none',
                }}
                extra={
                  <Button
                    type="link"
                    icon={<ReloadOutlined />}
                    onClick={() => setShowWorkflowResult(false)}
                  >
                    返回聊天
                  </Button>
                }
              >
                {loading && (
                  <div>
                    <Card style={{ borderRadius: 16, marginBottom: 20, textAlign: 'center' }}>
                      <Row gutter={[16, 16]} justify="center">
                        {stepConfig.map((step, idx) => (
                          <Col xs={8} sm={4} key={step.key}>
                            <div style={{
                              padding: 16,
                              borderRadius: 12,
                              background: currentStep === idx
                                ? `${step.color}15`
                                : currentStep > idx
                                  ? '#f0fdf4'
                                  : '#f9fafb',
                              border: `2px solid ${
                                currentStep === idx
                                  ? step.color
                                  : currentStep > idx
                                    ? '#10b981'
                                    : '#e5e7eb'
                              }`,
                              transition: 'all 0.3s ease',
                            }}>
                              <div style={{ fontSize: 24, marginBottom: 4 }}>
                                {currentStep > idx ? (
                                  <CheckCircleOutlined style={{ color: '#10b981' }} />
                                ) : currentStep === idx ? (
                                  <LoadingOutlined style={{ color: step.color }} />
                                ) : (
                                  step.icon
                                )}
                              </div>
                              <div style={{
                                fontSize: 11,
                                fontWeight: 600,
                                color: currentStep >= idx ? step.color : '#999',
                              }}>
                                {step.label}
                              </div>
                            </div>
                          </Col>
                        ))}
                      </Row>
                      <Progress
                        percent={Math.round((currentStep / stepConfig.length) * 100)}
                        status="active"
                        stroke={{ gradient: 'linear-gradient(90deg, #667eea, #764ba2)' }}
                        style={{ marginTop: 24 }}
                      />
                      <p style={{ color: '#666', marginTop: 8 }}>
                        正在执行 {currentStep > 0 ? stepConfig[currentStep - 1]?.label : '准备中'}...
                      </p>
                    </Card>
                  </div>
                )}

                {result && (
                  <>
                    <Row gutter={16} style={{ marginBottom: 20 }}>
                      <Col span={8}>
                        <Card size="small" style={{ borderRadius: 12, textAlign: 'center', background: '#f0f9ff' }}>
                          <div style={{ fontSize: 28, fontWeight: 700, color: '#3b82f6' }}>
                            {result.iteration_count || 1}
                          </div>
                          <div style={{ fontSize: 12, color: '#666' }}>迭代次数</div>
                        </Card>
                      </Col>
                      <Col span={8}>
                        <Card size="small" style={{ borderRadius: 12, textAlign: 'center', background: result.iteration_count > 1 ? '#fef3c7' : '#f0fdf4' }}>
                          <div style={{ fontSize: 28, fontWeight: 700, color: result.iteration_count > 1 ? '#f59e0b' : '#10b981' }}>
                            {result.iteration_count > 1 ? <SyncOutlined spin /> : <CheckCircleOutlined />}
                          </div>
                          <div style={{ fontSize: 12, color: '#666' }}>
                            {result.iteration_count > 1 ? '触发循环优化' : '单次执行'}
                          </div>
                        </Card>
                      </Col>
                      <Col span={8}>
                        <Card size="small" style={{ borderRadius: 12, textAlign: 'center', background: '#faf5ff' }}>
                          <div style={{ fontSize: 28, fontWeight: 700, color: '#8b5cf6' }}>
                            {result.total_nodes || 7}
                          </div>
                          <div style={{ fontSize: 12, color: '#666' }}>执行节点数</div>
                        </Card>
                      </Col>
                    </Row>

                    {result.iteration_count > 1 && (
                      <Alert
                        message={
                          <Space>
                            <SyncOutlined spin style={{ color: '#f59e0b' }} />
                            <span>工作流执行了 <strong>{result.iteration_count}</strong> 次迭代循环优化</span>
                            <Tag color="orange">风险过高 → 重新规划</Tag>
                          </Space>
                        }
                        description={
                          <div>
                            <p style={{ margin: 0 }}>
                              当风险控制节点检测到方案风险等级为"高"时，工作流会自动回到调度决策节点重新制定方案，
                              直到风险降低或达到最大迭代次数（3次）。
                            </p>
                            <div style={{ marginTop: 8 }}>
                              <strong>执行路径：</strong>
                              {(result.execution_history || []).map((h, i) => (
                                <Tag key={i} style={{ margin: 2 }} color={h.node === 'scheduling_decision' && i > 2 ? 'orange' : 'blue'}>
                                  {h.node}
                                </Tag>
                              ))}
                            </div>
                          </div>
                        }
                        type="warning"
                        showIcon
                        icon={<WarningOutlined />}
                        style={{ marginBottom: 20, borderRadius: 12 }}
                      />
                    )}

                    <Alert
                      message="工作流执行成功"
                      description={
                        <Space>
                          <Tag icon={<DatabaseOutlined />} color="blue">会话: {result.session_id?.slice(0, 8)}...</Tag>
                          <Tag icon={<CheckCircleOutlined />} color="green">完成 {result.total_nodes} 个节点</Tag>
                        </Space>
                      }
                      type="success"
                      showIcon
                      style={{ marginBottom: 20, borderRadius: 12 }}
                    />

                    {result.tool_calls && result.tool_calls.length > 0 && (
                      <Card size="small" title={<Space><ToolOutlined /> 工具调用记录</Space>} style={{ marginBottom: 16, borderRadius: 12, background: '#fafbfc' }}>
                        {(result.tool_calls || []).map((tc, i) => (
                          <Tag key={i} color="green" style={{ marginBottom: 4 }}>
                            <ApiOutlined /> {tc.tool}: {tc.result}
                          </Tag>
                        ))}
                      </Card>
                    )}

                    <div
                      style={{
                        maxHeight: 400,
                        overflowY: 'auto',
                        marginBottom: 20,
                        borderRadius: 12,
                        border: '1px solid #f0f0f0',
                        scrollbarWidth: 'thin',
                        scrollbarColor: '#d1d5db #f3f4f6',
                      }}
                      css={{
                        '&::-webkit-scrollbar': {
                          width: '6px',
                        },
                        '&::-webkit-scrollbar-track': {
                          background: '#f3f4f6',
                          borderRadius: '3px',
                        },
                        '&::-webkit-scrollbar-thumb': {
                          background: '#d1d5db',
                          borderRadius: '3px',
                        },
                        '&::-webkit-scrollbar-thumb:hover': {
                          background: '#9ca3af',
                        },
                      }}
                    >
                      <div
                        style={{
                          padding: 16,
                          background: '#fafbfc',
                          opacity: 0.7,
                          filter: 'blur(0.3px)',
                        }}
                      >
                        <Collapse
                          defaultActiveKey={stepConfig.map(s => s.key)}
                          bordered={false}
                          items={stepConfig.map((step) => ({
                            key: step.key,
                            label: (
                              <Space>
                                <span style={{ color: step.color, opacity: 0.8 }}>{step.icon}</span>
                                <span style={{ fontWeight: 600, opacity: 0.8 }}>{step.label}</span>
                                {step.desc && (
                                  <span style={{ color: '#999', fontSize: 12, opacity: 0.6 }}>{step.desc}</span>
                                )}
                                {result.steps?.[step.key] && (
                                  <CheckCircleOutlined style={{ color: '#10b981', opacity: 0.8 }} />
                                )}
                              </Space>
                            ),
                            children: result.steps?.[step.key] ? (
                              <pre style={{
                                whiteSpace: 'pre-wrap',
                                fontSize: 12,
                                lineHeight: 1.6,
                                background: '#fff',
                                padding: 12,
                                borderRadius: 8,
                                maxHeight: 150,
                                overflow: 'auto',
                                border: '1px solid #f0f0f0',
                                color: '#666',
                                opacity: 0.85,
                              }}>
                                {typeof result.steps[step.key] === 'object' 
                                  ? JSON.stringify(result.steps[step.key], null, 2)
                                  : result.steps[step.key]}
                              </pre>
                            ) : (
                              <span style={{ color: '#999', opacity: 0.6 }}>暂无数据</span>
                            ),
                          }))}
                        />
                      </div>
                    </div>

                    {result.summary && (
                      <>
                        <Divider><span style={{ color: '#666' }}>📋 最终方案总结</span></Divider>
                        <div style={{
                          background: 'linear-gradient(135deg, #f0f9ff 0%, #ecfdf5 100%)',
                          padding: 20,
                          borderRadius: 12,
                          borderLeft: '4px solid #3b82f6',
                        }}>
                          <pre style={{
                            whiteSpace: 'pre-wrap',
                            fontSize: 14,
                            lineHeight: 1.8,
                            margin: 0,
                            color: '#1e1b4b',
                          }}>
                            {result.summary}
                          </pre>
                        </div>
                      </>
                    )}
                  </>
                )}
              </Card>
            </>
          ) : (
            <Card
              style={{
                borderRadius: 16,
                boxShadow: '0 4px 20px rgba(0, 0, 0, 0.06)',
                border: 'none',
                height: '700px',
                display: 'flex',
                flexDirection: 'column',
              }}
            >
              <ChatUI
                onWorkflowRequest={handleRunWorkflow}
                sessionId={sessionId}
                setSessionId={setSessionId}
              />
            </Card>
          )}
        </Col>

        <Col xs={24} lg={8}>
          <Card
            title={
              <Space>
                <HistoryOutlined style={{ color: '#667eea' }} />
                <span>会话历史</span>
                <Badge count={sessions.length} style={{ backgroundColor: '#667eea' }} />
              </Space>
            }
            extra={
              <Button
                size="small"
                icon={<ReloadOutlined />}
                onClick={loadInitialData}
              >
                刷新
              </Button>
            }
            style={{ borderRadius: 16, marginBottom: 24 }}
          >
            {sessions.length === 0 ? (
              <Empty
                image={Empty.PRESENTED_IMAGE_SIMPLE}
                description="暂无会话记录"
              />
            ) : (
              <Table
                dataSource={sessions}
                columns={sessionColumns}
                rowKey="thread_id"
                size="small"
                pagination={{ pageSize: 5 }}
              />
            )}
          </Card>

          <Card
            title={
              <Space>
                <ToolOutlined style={{ color: '#10b981' }} />
                <span>可用工具</span>
                <Badge count={tools.length} style={{ backgroundColor: '#10b981' }} />
              </Space>
            }
            style={{ borderRadius: 16 }}
          >
            {tools.length === 0 ? (
              <Empty description="暂无工具" />
            ) : (
              <div style={{ maxHeight: 300, overflow: 'auto' }}>
                {tools.map((tool) => (
                  <div
                    key={tool.name}
                    style={{
                      padding: '12px 16px',
                      marginBottom: 8,
                      borderRadius: 10,
                      background: '#fafbfc',
                      borderLeft: '3px solid #10b981',
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      <ApiOutlined style={{ color: '#10b981' }} />
                      <span style={{ fontWeight: 600, fontSize: 13 }}>{tool.name}</span>
                    </div>
                    <div style={{ fontSize: 12, color: '#666', marginTop: 4, marginLeft: 24 }}>
                      {tool.description}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </Card>
        </Col>
      </Row>

      <Modal
        title="会话历史详情"
        open={!!selectedSession}
        onCancel={() => setSelectedSession(null)}
        footer={null}
        width={700}
        style={{ top: 100 }}
      >
        {historyLoading ? (
          <div style={{ textAlign: 'center', padding: 40 }}>
            <Spin tip="加载历史记录..." />
          </div>
        ) : sessionHistory ? (
          <div>
            <Tag icon={<DatabaseOutlined />} color="blue">
              会话ID: {sessionHistory.session_id}
            </Tag>
            <Tag icon={<ClockCircleOutlined />} color="purple">
              记录数: {sessionHistory.count}
            </Tag>
            <Divider />
            <pre style={{
              whiteSpace: 'pre-wrap',
              fontSize: 12,
              background: '#fafbfc',
              padding: 16,
              borderRadius: 8,
              maxHeight: 400,
              overflow: 'auto',
            }}>
              {JSON.stringify(sessionHistory.history, null, 2)}
            </pre>
          </div>
        ) : null}
      </Modal>
    </div>
  );
}