import React, { useEffect, useState } from 'react';
import {
  Table, Button, Space, Tag, Modal, Form, Input, Select, InputNumber,
  Card, message, Descriptions, Spin,
} from 'antd';
import {
  PlusOutlined, RobotOutlined, CheckOutlined, PlayCircleOutlined,
} from '@ant-design/icons';
import { schedulingAPI, aiAPI } from '@/services/api';

const statusMap = {
  PENDING: { color: 'default', text: '待处理' },
  AI_SUGGESTED: { color: 'blue', text: 'AI已建议' },
  REVIEWED: { color: 'purple', text: '已审核' },
  APPROVED: { color: 'green', text: '已批准' },
  EXECUTING: { color: 'orange', text: '执行中' },
  COMPLETED: { color: 'green', text: '已完成' },
  REJECTED: { color: 'red', text: '已驳回' },
};

export default function SchedulingCenter() {
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState({ records: [], total: 0 });
  const [modalOpen, setModalOpen] = useState(false);
  const [aiModalOpen, setAiModalOpen] = useState(false);
  const [aiResult, setAiResult] = useState('');
  const [aiLoading, setAiLoading] = useState(false);
  const [models, setModels] = useState([]);
  const [selectedModel, setSelectedModel] = useState(null);
  const [currentTask, setCurrentTask] = useState(null);
  const [form] = Form.useForm();
  const [params, setParams] = useState({ page: 1, size: 20 });

  const fetchData = async () => {
    setLoading(true);
    try { setData(await schedulingAPI.list(params)); } catch (e) { /* */ }
    setLoading(false);
  };

  useEffect(() => { fetchData(); }, [params]);
  useEffect(() => { aiAPI.getModels().then(setModels).catch(() => {}); }, []);

  const handleCreate = () => { form.resetFields(); setModalOpen(true); };
  const handleSubmit = async () => {
    await schedulingAPI.create(await form.validateFields());
    message.success('调度任务创建成功');
    setModalOpen(false);
    fetchData();
  };

  const handleAiSuggest = (record) => {
    setCurrentTask(record);
    setAiResult('');
    setAiModalOpen(true);
  };

  const runAiSuggestion = async () => {
    setAiLoading(true);
    try {
      const res = await schedulingAPI.aiSuggest(currentTask.id, selectedModel);
      setAiResult(res.aiSuggestion || 'AI方案生成成功');
      message.success('AI方案已生成！');
      fetchData();
    } catch (e) { /* */ }
    setAiLoading(false);
  };

  const handleApprove = async (id, approved) => {
    await schedulingAPI.approve(id, approved, 'admin');
    message.success(approved ? '方案已批准' : '方案已驳回');
    fetchData();
  };

  const handleExecute = async (id) => {
    await schedulingAPI.execute(id);
    message.success('任务开始执行');
    fetchData();
  };

  const columns = [
    { title: '任务号', dataIndex: 'taskNo', width: 160 },
    { title: '类型', dataIndex: 'taskType', width: 100 },
    { title: '订单号', dataIndex: 'orderNo', width: 140 },
    { title: '商品', dataIndex: 'productName', width: 120 },
    { title: '数量', dataIndex: 'quantity', width: 80 },
    { title: '来源仓', dataIndex: 'fromWarehouseName', width: 100 },
    { title: '目标仓', dataIndex: 'toWarehouseName', width: 100 },
    {
      title: '状态', dataIndex: 'status', width: 100,
      render: (s) => <Tag color={statusMap[s]?.color}>{statusMap[s]?.text || s}</Tag>,
    },
    {
      title: '操作', width: 260,
      render: (_, r) => (
        <Space>
          {(r.status === 'PENDING') && (
            <Button type="primary" size="small" icon={<RobotOutlined />}
              onClick={() => handleAiSuggest(r)}>AI方案</Button>
          )}
          {r.status === 'AI_SUGGESTED' && (
            <>
              <Button type="primary" size="small" icon={<CheckOutlined />}
                onClick={() => handleApprove(r.id, true)}>批准</Button>
              <Button size="small" danger onClick={() => handleApprove(r.id, false)}>驳回</Button>
            </>
          )}
          {r.status === 'APPROVED' && (
            <Button type="primary" size="small" icon={<PlayCircleOutlined />}
              onClick={() => handleExecute(r.id)}>执行</Button>
          )}
          {r.aiModelUsed && <Tag style={{ marginLeft: 4 }}>{r.aiModelUsed}</Tag>}
        </Space>
      ),
    },
  ];

  return (
    <div>
      <Card title="📋 调度中心" extra={
        <Button type="primary" icon={<PlusOutlined />} onClick={handleCreate}>
          新建调度任务
        </Button>
      } style={{ borderRadius: 12 }}>
        <Table columns={columns} dataSource={data.records} rowKey="id"
          loading={loading} size="middle"
          pagination={{
            current: params.page, pageSize: params.size, total: data.total,
            onChange: (p, s) => setParams({ ...params, page: p, size: s }),
            showSizeChanger: true, showTotal: (t) => `共 ${t} 条`,
          }} />
      </Card>

      <Modal title="新建调度任务" open={modalOpen}
        onCancel={() => setModalOpen(false)} onOk={handleSubmit} destroyOnHidden>
        <Form form={form} layout="vertical" style={{ marginTop: 16 }}>
          <Form.Item name="orderNo" label="关联订单号" rules={[{ required: true }]}>
            <Input placeholder="请输入订单号" />
          </Form.Item>
          <Form.Item name="taskType" label="任务类型">
            <Select defaultValue="DISPATCH" options={[
              { label: '发货调度', value: 'DISPATCH' },
              { label: '补货调度', value: 'REPLENISHMENT' },
              { label: '调拨调度', value: 'TRANSFER' },
            ]} />
          </Form.Item>
          <Form.Item name="productName" label="商品名称" rules={[{ required: true }]}>
            <Input placeholder="请输入商品名称" />
          </Form.Item>
          <Form.Item name="quantity" label="数量" rules={[{ required: true }]}>
            <InputNumber min={1} style={{ width: '100%' }} />
          </Form.Item>
          <Space size={16} style={{ width: '100%' }}>
            <Form.Item name="fromWarehouseName" label="来源仓库">
              <Input placeholder="来源仓库" />
            </Form.Item>
            <Form.Item name="toWarehouseName" label="目标仓库">
              <Input placeholder="目标仓库" />
            </Form.Item>
          </Space>
        </Form>
      </Modal>

      {/* AI 方案弹窗 */}
      <Modal title="🤖 AI 调度方案生成" open={aiModalOpen}
        onCancel={() => setAiModalOpen(false)} width={720}
        footer={[
          <Button key="close" onClick={() => setAiModalOpen(false)}>关闭</Button>,
          <Button key="run" type="primary" icon={<RobotOutlined />}
            loading={aiLoading} onClick={runAiSuggestion}>
            {aiResult ? '重新生成' : '生成AI方案'}
          </Button>,
        ]}>
        <div style={{ marginBottom: 16 }}>
          <span style={{ fontWeight: 600, marginRight: 12 }}>选择模型:</span>
          <Select
            style={{ width: 280 }}
            placeholder="默认模型 (qwen-plus)"
            allowClear
            onChange={setSelectedModel}
            options={models.map((m) => ({
              label: `${m.name} (${m.id})`, value: m.id,
            }))}
          />
        </div>
        {currentTask && (
          <Descriptions bordered size="small" style={{ marginBottom: 16 }}>
            <Descriptions.Item label="任务号">{currentTask.taskNo}</Descriptions.Item>
            <Descriptions.Item label="商品">{currentTask.productName}</Descriptions.Item>
            <Descriptions.Item label="数量">{currentTask.quantity}</Descriptions.Item>
            <Descriptions.Item label="来源">{currentTask.fromWarehouseName}</Descriptions.Item>
            <Descriptions.Item label="目标">{currentTask.toWarehouseName}</Descriptions.Item>
          </Descriptions>
        )}
        {aiLoading && <Spin tip="AI 正在生成方案..." style={{ display: 'block', margin: '24px auto' }} />}
        {aiResult && (
          <Card size="small" title="AI 方案" style={{ background: '#f9fafb', borderRadius: 10 }}>
            <pre style={{ whiteSpace: 'pre-wrap', fontSize: 13, lineHeight: 1.6, margin: 0 }}>
              {aiResult}
            </pre>
          </Card>
        )}
      </Modal>
    </div>
  );
}
