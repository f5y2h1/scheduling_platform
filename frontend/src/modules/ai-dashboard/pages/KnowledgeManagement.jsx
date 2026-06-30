import React, { useEffect, useState } from 'react';
import { usePersistedState } from '@/hooks/usePersistedState';
import {
  Row, Col, Card, Button, Input, Select, Tag, Space, Table,
  Modal, Form, Spin, Statistic, Tabs, List, Badge, message,
  Progress, Descriptions, Empty, Divider, Typography, Tooltip,
  Alert, Collapse,
} from 'antd';
import {
  SearchOutlined, PlusOutlined, DatabaseOutlined,
  ExperimentOutlined, ThunderboltOutlined, BookOutlined,
  HistoryOutlined, FileTextOutlined, DeleteOutlined,
  ReloadOutlined, RobotOutlined, ApiOutlined, CloudUploadOutlined,
  FilterOutlined, SafetyOutlined, InfoCircleOutlined,
  StarOutlined, BulbOutlined,
} from '@ant-design/icons';
import ReactEChartsCore from 'echarts-for-react/lib/core';
import * as echarts from 'echarts/core';
import { BarChart, PieChart } from 'echarts/charts';
import { GridComponent, TooltipComponent, LegendComponent } from 'echarts/components';
import { CanvasRenderer } from 'echarts/renderers';
import smartRequest from '@/services/smartRequest';

echarts.use([BarChart, PieChart, GridComponent, TooltipComponent, LegendComponent, CanvasRenderer]);

const { TextArea } = Input;
const { Text, Title, Paragraph } = Typography;

export default function KnowledgeManagement() {
  const [activeTab, setActiveTab] = useState('search');
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(false);

  // 检索状态
  const [searchQuery, setSearchQuery] = usePersistedState('knowledge_search_query', '');
  const [searchResults, setSearchResults] = useState([]);
  const [searchMode, setSearchMode] = useState('hybrid');
  const [searchTopK, setSearchTopK] = useState(5);
  const [searching, setSearching] = useState(false);
  const [minQuality, setMinQuality] = useState(0.5);

  // 文档录入状态
  const [docModalOpen, setDocModalOpen] = useState(false);
  const [docForm] = Form.useForm();
  const [saving, setSaving] = useState(false);

  // RAG问答状态
  const [ragQuery, setRagQuery] = usePersistedState('knowledge_rag_query', '');
  const [ragResult, setRagResult] = useState(null);
  const [ragLoading, setRagLoading] = useState(false);
  const [ragStrategy, setRagStrategy] = useState('hybrid');

  // 文档列表状态
  const [documents, setDocuments] = useState([]);
  const [docsLoading, setDocsLoading] = useState(false);
  const [selectedDoc, setSelectedDoc] = useState(null);

  useEffect(() => {
    fetchStats();
    fetchDocuments();
  }, []);

  const fetchDocuments = async () => {
    setDocsLoading(true);
    try {
      const res = await smartRequest.get('/knowledge/documents');
      setDocuments(res.documents || res);
    } catch (e) {
      console.error('获取文档列表失败:', e);
    }
    setDocsLoading(false);
  };

  const fetchStats = async () => {
    setLoading(true);
    try {
      const res = await smartRequest.get('/knowledge/stats');
      setStats(res);
    } catch (e) {
      console.error('获取统计失败:', e);
    }
    setLoading(false);
  };

  // ========== 检索 ==========
  const handleSearch = async () => {
    if (!searchQuery.trim()) return;
    setSearching(true);
    try {
      let endpoint = '/knowledge/search';
      let body = { query: searchQuery, top_k: searchTopK };

      // 根据模式选择接口
      if (searchMode === 'hybrid') {
        endpoint = '/knowledge/search/hybrid';
      } else if (searchMode === 'advanced') {
        endpoint = '/knowledge/search/advanced';
        body.strategy = 'hybrid';
      } else if (searchMode === 'quality') {
        endpoint = '/knowledge/search/quality';
        body.min_quality = minQuality;
      } else if (searchMode === 'category') {
        endpoint = '/knowledge/search/category';
        body.category = '调度规则';
      } else if (searchMode === 'decisions') {
        endpoint = '/knowledge/decisions/search';
        body = { scenario: searchQuery, top_k: searchTopK };
      } else if (searchMode === 'rules') {
        endpoint = '/knowledge/rules/search';
        body = { query: searchQuery, top_k: searchTopK };
      }

      const res = await smartRequest.post(endpoint, body);
      const results = Array.isArray(res) ? res : res.results || res.documents || [];
      setSearchResults(results);

      if (results.length > 0) {
        message.success(`检索到 ${results.length} 条结果`);
      } else {
        message.info('未找到相关结果');
      }
    } catch (e) {
      console.error('检索失败:', e);
      message.error('检索失败');
    }
    setSearching(false);
  };

  // ========== RAG问答 ==========
  const handleRagQuery = async () => {
    if (!ragQuery.trim()) return;
    setRagLoading(true);
    try {
      const res = await smartRequest.post('/knowledge/rag/query', {
        query: ragQuery,
        top_k: 5,
        strategy: ragStrategy,
      });
      setRagResult(res);
      message.success(
        `检索 ${res.retrievalCount} 条，置信度 ${Math.round(res.confidence * 100)}%，耗时 ${res.totalTimeMs}ms`
      );
    } catch (e) {
      console.error('RAG查询失败:', e);
      message.error('RAG查询失败');
    }
    setRagLoading(false);
  };

  // ========== 文档录入 ==========
  const handleAddDoc = async () => {
    const values = await docForm.validateFields();
    setSaving(true);
    try {
      await smartRequest.post('/knowledge/documents/advanced', values);
      message.success('文档入库成功！');
      setDocModalOpen(false);
      docForm.resetFields();
      fetchStats();
      fetchDocuments();
    } catch (e) {
      console.error('入库失败:', e);
      message.error('入库失败');
    }
    setSaving(false);
  };

  const handleInitKnowledgeBase = async () => {
    setLoading(true);
    try {
      await smartRequest.post('/knowledge/init-default');
      message.success('默认知识库初始化完成！');
      fetchStats();
      fetchDocuments();
    } catch (e) {
      console.error('初始化失败:', e);
      message.error('初始化失败');
    }
    setLoading(false);
  };

  // ========== 统计图表 ==========
  const categoryChartOption = {
    tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
    legend: { orient: 'vertical', right: 10, top: 'center' },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      center: ['40%', '50%'],
      avoidLabelOverlap: false,
      itemStyle: { borderRadius: 6, borderColor: '#fff', borderWidth: 2 },
      label: { show: false },
      emphasis: {
        label: { show: true, fontSize: 14, fontWeight: 'bold' },
      },
      data: [
        { value: 45, name: '库存策略', itemStyle: { color: '#10b981' } },
        { value: 38, name: '调度规则', itemStyle: { color: '#3b82f6' } },
        { value: 30, name: '需求预测', itemStyle: { color: '#8b5cf6' } },
        { value: 25, name: '风险规则', itemStyle: { color: '#ef4444' } },
        { value: 22, name: '成本优化', itemStyle: { color: '#f59e0b' } },
      ],
    }],
  };

  // 检索结果列配置
  const searchColumns = [
    {
      title: '相关度',
      dataIndex: 'score',
      width: 100,
      render: (v) => (
        <Progress
          percent={Math.round(v * 100)}
          size="small"
          strokeColor={v > 0.8 ? '#10b981' : v > 0.6 ? '#3b82f6' : '#f59e0b'}
        />
      ),
    },
    {
      title: '质量',
      dataIndex: 'qualityScore',
      width: 80,
      render: (v) => v ? (
        <Tag color={v >= 0.8 ? 'green' : v >= 0.6 ? 'blue' : 'orange'}>
          {Math.round(v * 100)}%
        </Tag>
      ) : '-',
    },
    {
      title: '标题',
      dataIndex: 'title',
      ellipsis: true,
      render: (v, r) => (
        <Tooltip title={v || r.payload?.scenario || r.id}>
          <Text strong>{v || r.payload?.scenario || r.id}</Text>
        </Tooltip>
      ),
    },
    {
      title: '分类',
      dataIndex: 'category',
      width: 100,
      render: (v) => v ? <Tag color="purple">{v}</Tag> : '-',
    },
    {
      title: '类型',
      dataIndex: 'retrievalType',
      width: 90,
      render: (v) => v ? (
        <Tag color={v === 'semantic' ? 'cyan' : v === 'keyword' ? 'gold' : 'green'}>
          {v === 'semantic' ? '语义' : v === 'keyword' ? '关键词' : '混合'}
        </Tag>
      ) : '-',
    },
  ];

  return (
    <div style={{ padding: '0 4px' }}>
      <Title level={2} style={{ marginBottom: 24, color: '#e2e8f0' }}>
        <BookOutlined style={{ marginRight: 8 }} />
        RAG 知识库管理
      </Title>

      {/* 统计卡片 */}
      <Row gutter={[16, 16]}>
        <Col xs={12} sm={6}>
          <Card hoverable style={{ borderRadius: 12, boxShadow: '0 2px 8px rgba(0,0,0,0.06)' }}>
            <Statistic
              title={<Text type="secondary">知识文档</Text>}
              value={stats?.knowledgeCount || 0}
              prefix={<BookOutlined style={{ color: '#6366f1' }} />}
              valueStyle={{ color: '#e2e8f0' }}
            />
          </Card>
        </Col>
        <Col xs={12} sm={6}>
          <Card hoverable style={{ borderRadius: 12, boxShadow: '0 2px 8px rgba(0,0,0,0.06)' }}>
            <Statistic
              title={<Text type="secondary">决策记录</Text>}
              value={stats?.decisionCount || 0}
              prefix={<HistoryOutlined style={{ color: '#10b981' }} />}
              valueStyle={{ color: '#e2e8f0' }}
            />
          </Card>
        </Col>
        <Col xs={12} sm={6}>
          <Card hoverable style={{ borderRadius: 12, boxShadow: '0 2px 8px rgba(0,0,0,0.06)' }}>
            <Statistic
              title={<Text type="secondary">业务规则</Text>}
              value={stats?.ruleCount || 0}
              prefix={<FileTextOutlined style={{ color: '#f59e0b' }} />}
              valueStyle={{ color: '#e2e8f0' }}
            />
          </Card>
        </Col>
        <Col xs={12} sm={6}>
          <Card hoverable style={{ borderRadius: 12, boxShadow: '0 2px 8px rgba(0,0,0,0.06)' }}>
            <Statistic
              title={<Text type="secondary">向量总数</Text>}
              value={stats?.totalVectors || 0}
              prefix={<DatabaseOutlined style={{ color: '#ec4899' }} />}
              valueStyle={{ color: '#e2e8f0' }}
            />
          </Card>
        </Col>
      </Row>

      {/* 主体内容 */}
      <Tabs
        activeKey={activeTab}
        onChange={setActiveTab}
        style={{ marginTop: 24 }}
        items={[
          {
            key: 'search',
            label: <span><SearchOutlined /> 智能检索</span>,
            children: (
              <Row gutter={16}>
                <Col xs={24} lg={14}>
                  <Card
                    title={<span><FilterOutlined /> 检索配置</span>}
                    style={{ borderRadius: 12, boxShadow: '0 2px 8px rgba(0,0,0,0.04)' }}
                    extra={
                      <Space>
                        <Select
                          value={searchMode}
                          onChange={setSearchMode}
                          style={{ width: 160 }}
                          options={[
                            { label: '🔀 混合检索', value: 'hybrid' },
                            { label: '📊 语义检索', value: 'semantic' },
                            { label: '🔤 关键词检索', value: 'keyword' },
                            { label: '⭐ 质量筛选', value: 'quality' },
                            { label: '🏷️ 分类检索', value: 'category' },
                            { label: '📜 历史决策', value: 'decisions' },
                            { label: '📋 业务规则', value: 'rules' },
                            { label: '🔬 高级检索', value: 'advanced' },
                          ]}
                        />
                        <Select
                          value={searchTopK}
                          onChange={setSearchTopK}
                          style={{ width: 90 }}
                          options={[3, 5, 10, 20].map(n => ({ label: `Top-${n}`, value: n }))}
                        />
                      </Space>
                    }
                  >
                    <Space style={{ width: '100%' }} direction="vertical" size="middle">
                      {searchMode === 'quality' && (
                        <Alert
                          type="info"
                          message={<span>质量筛选阈值：<strong>{minQuality}</strong></span>}
                          action={
                            <Select
                              value={minQuality}
                              onChange={setMinQuality}
                              style={{ width: 120 }}
                              size="small"
                              options={[
                                { label: '高 (0.8)', value: 0.8 },
                                { label: '中 (0.7)', value: 0.7 },
                                { label: '低 (0.5)', value: 0.5 },
                              ]}
                            />
                          }
                        />
                      )}

                      <TextArea
                        value={searchQuery}
                        onChange={e => setSearchQuery(e.target.value)}
                        placeholder="输入查询内容，如：安全库存计算公式、调度优先级规则、成本优化策略..."
                        rows={3}
                        style={{ borderRadius: 8 }}
                        onPressEnter={handleSearch}
                      />

                      <Button
                        type="primary"
                        icon={<SearchOutlined />}
                        loading={searching}
                        onClick={handleSearch}
                        size="large"
                        block
                      >
                        开始检索
                      </Button>
                    </Space>

                    <Divider style={{ margin: '16px 0' }} />

                    {searchResults.length > 0 ? (
                      <Table
                        dataSource={searchResults}
                        columns={searchColumns}
                        rowKey="id"
                        size="small"
                        pagination={false}
                        expandable={{
                          expandedRowRender: (r) => (
                            <div style={{ padding: 12, background: '#f9fafb', borderRadius: 8 }}>
                              <Descriptions size="small" column={2}>
                                <Descriptions.Item label="块索引">{r.chunkIndex || r.payload?.chunk_index || '-'}</Descriptions.Item>
                                <Descriptions.Item label="块类型">{r.chunkType || r.payload?.chunk_type || '-'}</Descriptions.Item>
                              </Descriptions>
                              <Paragraph
                                style={{
                                  marginTop: 12,
                                  whiteSpace: 'pre-wrap',
                                  fontSize: 13,
                                  lineHeight: 1.7,
                                  maxHeight: 200,
                                  overflow: 'auto',
                                }}
                                ellipsis={{ rows: 4, expandable: true }}
                              >
                                {r.content || r.payload?.content || r.payload?.decision || r.payload?.rule_content || '无内容'}
                              </Paragraph>
                            </div>
                          ),
                        }}
                      />
                    ) : (
                      <Empty
                        description="输入查询关键词并点击检索"
                        style={{ marginTop: 40 }}
                        image={Empty.PRESENTED_IMAGE_SIMPLE}
                      />
                    )}
                  </Card>
                </Col>

                <Col xs={24} lg={10}>
                  <Card
                    title={<span><BulbOutlined /> 知识分布</span>}
                    style={{ borderRadius: 12, boxShadow: '0 2px 8px rgba(0,0,0,0.04)' }}
                  >
                    <ReactEChartsCore
                      echarts={echarts}
                      option={categoryChartOption}
                      style={{ height: 260 }}
                    />
                  </Card>

                  <Card
                    title={<span><RobotOutlined /> RAG 增强问答</span>}
                    style={{ borderRadius: 12, boxShadow: '0 2px 8px rgba(0,0,0,0.04)', marginTop: 16 }}
                    extra={
                      <Select
                        style={{ width: 140 }}
                        placeholder="检索策略"
                        value={ragStrategy}
                        onChange={setRagStrategy}
                        options={[
                          { label: '混合检索', value: 'hybrid' },
                          { label: '语义检索', value: 'semantic' },
                          { label: '关键词检索', value: 'keyword' },
                        ]}
                      />
                    }
                  >
                    <TextArea
                      value={ragQuery}
                      onChange={e => setRagQuery(e.target.value)}
                      placeholder="输入问题，如：如何计算安全库存？调度优先级如何确定？"
                      rows={3}
                      style={{ borderRadius: 8 }}
                    />

                    <Button
                      type="primary"
                      icon={<ThunderboltOutlined />}
                      loading={ragLoading}
                      onClick={handleRagQuery}
                      style={{ marginTop: 12 }}
                      block
                    >
                      RAG 智能问答
                    </Button>

                    {ragResult && (
                      <div style={{ marginTop: 16 }}>
                        {/* 结果统计 */}
                        <Row gutter={12} style={{ marginBottom: 12 }}>
                          <Col span={6}>
                            <Statistic
                              title="检索量"
                              value={ragResult.retrievalCount}
                              suffix="条"
                              valueStyle={{ fontSize: 14 }}
                            />
                          </Col>
                          <Col span={6}>
                            <Statistic
                              title="置信度"
                              value={Math.round(ragResult.confidence * 100)}
                              suffix="%"
                              valueStyle={{ fontSize: 14, color: ragResult.confidence >= 0.7 ? '#10b981' : '#f59e0b' }}
                            />
                          </Col>
                          <Col span={6}>
                            <Statistic
                              title="检索耗时"
                              value={ragResult.retrievalTimeMs}
                              suffix="ms"
                              valueStyle={{ fontSize: 14 }}
                            />
                          </Col>
                          <Col span={6}>
                            <Statistic
                              title="总耗时"
                              value={ragResult.totalTimeMs}
                              suffix="ms"
                              valueStyle={{ fontSize: 14 }}
                            />
                          </Col>
                        </Row>

                        {/* 知识库支持状态 */}
                        {ragResult.hasKnowledgeSupport ? (
                          <Alert
                            type="success"
                            message="答案基于知识库内容生成"
                            icon={<SafetyOutlined />}
                            showIcon
                            style={{ marginBottom: 12 }}
                          />
                        ) : (
                          <Alert
                            type="warning"
                            message="知识库无相关内容，答案基于专业知识"
                            icon={<InfoCircleOutlined />}
                            showIcon
                            style={{ marginBottom: 12 }}
                          />
                        )}

                        {/* AI 回答 */}
                        <Card
                          size="small"
                          title={<span><StarOutlined /> AI 回答</span>}
                          style={{
                            background: '#fafbff',
                            borderRadius: 10,
                            borderLeft: '3px solid #6366f1',
                          }}
                        >
                          <Paragraph
                            style={{ whiteSpace: 'pre-wrap', fontSize: 13, lineHeight: 1.7, margin: 0 }}
                          >
                            {ragResult.answer}
                          </Paragraph>
                        </Card>

                        {/* 引用来源 */}
                        {ragResult.sources?.length > 0 && (
                          <Collapse
                            style={{ marginTop: 12, borderRadius: 8 }}
                            items={[
                              {
                                key: '1',
                                label: <span>引用来源 ({ragResult.sources.length})</span>,
                                children: (
                                  <List
                                    size="small"
                                    dataSource={ragResult.sources}
                                    renderItem={(s) => (
                                      <List.Item>
                                        <Space>
                                          <Tag color="blue">{s.title}</Tag>
                                          <Tag>相关度: {Math.round(s.score * 100)}%</Tag>
                                          <Tag color="purple">{s.category}</Tag>
                                          {s.type && <Tag color="cyan">{s.type}</Tag>}
                                        </Space>
                                      </List.Item>
                                    )}
                                  />
                                ),
                              },
                            ]}
                          />
                        )}
                      </div>
                    )}
                  </Card>
                </Col>
              </Row>
            ),
          },
          {
            key: 'documents',
            label: <span><CloudUploadOutlined /> 文档管理</span>,
            children: (
              <Row gutter={16}>
                <Col xs={24} lg={12}>
                  <Card
                    title={<span><FileTextOutlined /> 知识文档列表</span>}
                    style={{ borderRadius: 12, boxShadow: '0 2px 8px rgba(0,0,0,0.04)' }}
                    extra={
                      <Space>
                        <Button
                          icon={<ReloadOutlined />}
                          onClick={fetchDocuments}
                          loading={docsLoading}
                        >
                          刷新
                        </Button>
                        <Button
                          type="primary"
                          icon={<PlusOutlined />}
                          onClick={() => setDocModalOpen(true)}
                        >
                          录入文档
                        </Button>
                      </Space>
                    }
                  >
                    {docsLoading ? (
                      <div style={{ textAlign: 'center', padding: 40 }}>
                        <Spin size="large" />
                      </div>
                    ) : documents.length > 0 ? (
                      <List
                        dataSource={documents}
                        split
                        renderItem={(doc) => (
                          <List.Item
                            onClick={() => setSelectedDoc(doc)}
                            style={{
                              cursor: 'pointer',
                              backgroundColor: selectedDoc?.doc_id === doc.doc_id ? '#f0f0ff' : 'transparent',
                              borderRadius: 8,
                              padding: '12px 16px',
                            }}
                          >
                            <List.Item.Meta
                              title={
                                <span style={{ fontWeight: 500 }}>
                                  {doc.title}
                                </span>
                              }
                              description={
                                <Space>
                                  <Tag color="purple">{doc.category}</Tag>
                                  <Tag color="blue">{doc.chunk_count} 块</Tag>
                                  <Tag color={doc.avg_quality >= 0.8 ? 'green' : doc.avg_quality >= 0.6 ? 'orange' : 'red'}>
                                    质量 {Math.round(doc.avg_quality * 100)}%
                                  </Tag>
                                  {doc.source && <Tag>{doc.source}</Tag>}
                                </Space>
                              }
                            />
                            <div style={{ fontSize: 12, color: '#64748b' }}>
                              {doc.created_at?.split('T')[0]}
                            </div>
                          </List.Item>
                        )}
                      />
                    ) : (
                      <div style={{ padding: '40px 0', textAlign: 'center' }}>
                        <DatabaseOutlined style={{ fontSize: 48, color: '#d9d9d9', marginBottom: 16 }} />
                        <Paragraph style={{ color: '#64748b' }}>
                          暂无文档，点击上方按钮录入或初始化知识库
                        </Paragraph>
                        <Button
                          type="primary"
                          icon={<ReloadOutlined />}
                          onClick={handleInitKnowledgeBase}
                          loading={loading}
                          style={{ marginTop: 16 }}
                        >
                          初始化知识库
                        </Button>
                      </div>
                    )}
                  </Card>
                </Col>

                <Col xs={24} lg={12}>
                  <Card
                    title={selectedDoc ? (
                      <span><BookOutlined /> {selectedDoc.title}</span>
                    ) : (
                      <span><InfoCircleOutlined /> 文档详情</span>
                    )}
                    style={{ borderRadius: 12, boxShadow: '0 2px 8px rgba(0,0,0,0.04)' }}
                  >
                    {selectedDoc ? (
                      <div>
                        <Descriptions bordered size="small" column={2} style={{ marginBottom: 16 }}>
                          <Descriptions.Item label="文档ID">{selectedDoc.doc_id}</Descriptions.Item>
                          <Descriptions.Item label="分类">{selectedDoc.category}</Descriptions.Item>
                          <Descriptions.Item label="来源">{selectedDoc.source || '-'}</Descriptions.Item>
                          <Descriptions.Item label="分块数">{selectedDoc.chunk_count}</Descriptions.Item>
                          <Descriptions.Item label="平均质量">
                            <Tag color={selectedDoc.avg_quality >= 0.8 ? 'green' : selectedDoc.avg_quality >= 0.6 ? 'orange' : 'red'}>
                              {Math.round(selectedDoc.avg_quality * 100)}%
                            </Tag>
                          </Descriptions.Item>
                          <Descriptions.Item label="创建时间">{selectedDoc.created_at?.split('T')[0]}</Descriptions.Item>
                        </Descriptions>
                        {selectedDoc.tags?.length > 0 && (
                          <div style={{ marginBottom: 16 }}>
                            <Text type="secondary" style={{ fontSize: 12 }}>标签：</Text>
                            <Space>
                              {selectedDoc.tags.map((tag, i) => (
                                <Tag key={i}>{tag}</Tag>
                              ))}
                            </Space>
                          </div>
                        )}
                        <Divider />
                        <Title level={5}>文档内容</Title>
                        <div
                          style={{
                            whiteSpace: 'pre-wrap',
                            fontSize: 13,
                            lineHeight: 1.8,
                            maxHeight: 400,
                            overflow: 'auto',
                            background: '#fafafa',
                            padding: 16,
                            borderRadius: 8,
                            color: '#cbd5e1',
                          }}
                        >
                          {selectedDoc.full_content}
                        </div>
                      </div>
                    ) : (
                      <div style={{ padding: '60px 0', textAlign: 'center' }}>
                        <BookOutlined style={{ fontSize: 48, color: '#d9d9d9', marginBottom: 16 }} />
                        <Paragraph style={{ color: '#64748b' }}>
                          请从左侧列表选择一个文档查看详情
                        </Paragraph>
                      </div>
                    )}
                  </Card>
                </Col>
              </Row>
            ),
          },
        ]}
      />

      {/* 文档录入 Modal */}
      <Modal
        title={<span><PlusOutlined /> 录入知识文档</span>}
        open={docModalOpen}
        onCancel={() => setDocModalOpen(false)}
        onOk={handleAddDoc}
        confirmLoading={saving}
        width={720}
        destroyOnHidden
      >
        <Alert
          type="info"
          message="文档将经过智能分块（基于语义边界）和向量化处理"
          style={{ marginBottom: 16 }}
          showIcon
        />
        <Form form={docForm} layout="vertical" style={{ marginTop: 8 }}>
          <Form.Item name="title" label="文档标题" rules={[{ required: true, message: '请输入标题' }]}>
            <Input placeholder="如：安全库存计算规则" />
          </Form.Item>
          <Form.Item name="category" label="分类" rules={[{ required: true, message: '请选择分类' }]}>
            <Select
              options={[
                { label: '库存策略', value: '库存策略' },
                { label: '调度规则', value: '调度规则' },
                { label: '需求预测', value: '需求预测' },
                { label: '成本优化', value: '成本优化' },
                { label: '风险规则', value: '风险规则' },
                { label: '执行管控', value: '执行管控' },
                { label: '通用', value: '通用' },
              ]}
            />
          </Form.Item>
          <Form.Item name="content" label="文档内容" rules={[{ required: true, message: '请输入内容' }]}>
            <TextArea
              rows={12}
              placeholder="请输入文档内容（支持Markdown格式，系统将自动进行智能分块）"
            />
          </Form.Item>
          <Form.Item name="tags" label="标签">
            <Select mode="tags" placeholder="输入标签后按回车" />
          </Form.Item>
          <Form.Item name="source" label="来源">
            <Input placeholder="如：运营手册、专家经验、行业最佳实践" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}