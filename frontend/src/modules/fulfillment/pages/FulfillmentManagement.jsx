import React, { useEffect, useState } from 'react';
import { Table, Button, Space, Tag, Modal, Form, Input, Select, Card, message, Descriptions } from 'antd';
import { PlusOutlined, EyeOutlined } from '@ant-design/icons';
import { fulfillmentAPI } from '@/services/api';

const statusMap = {
  PENDING: { color: 'default', text: '待处理' },
  PICKING: { color: 'blue', text: '拣货中' },
  PACKED: { color: 'cyan', text: '已打包' },
  SHIPPED: { color: 'purple', text: '已发货' },
  IN_TRANSIT: { color: 'orange', text: '运输中' },
  DELIVERED: { color: 'green', text: '已送达' },
  SIGNED: { color: 'green', text: '已签收' },
};

export default function FulfillmentManagement() {
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState({ records: [], total: 0 });
  const [modalOpen, setModalOpen] = useState(false);
  const [trackModalOpen, setTrackModalOpen] = useState(false);
  const [current, setCurrent] = useState(null);
  const [form] = Form.useForm();
  const [trackForm] = Form.useForm();
  const [params, setParams] = useState({ page: 1, size: 20 });

  const fetchData = async () => {
    setLoading(true);
    try { setData(await fulfillmentAPI.list(params)); } catch (e) { /* */ }
    setLoading(false);
  };

  useEffect(() => { fetchData(); }, [params]);

  const handleCreate = () => { form.resetFields(); setModalOpen(true); };
  const handleSubmit = async () => {
    await fulfillmentAPI.create(await form.validateFields());
    message.success('履约单创建成功');
    setModalOpen(false);
    fetchData();
  };

  const handleTracking = (record) => {
    setCurrent(record);
    trackForm.resetFields();
    trackForm.setFieldsValue({ trackingNumber: record.trackingNumber, carrierName: record.carrierName });
    setTrackModalOpen(true);
  };

  const handleTrackingSubmit = async () => {
    const vals = await trackForm.validateFields();
    await fulfillmentAPI.updateTracking(current.id, vals);
    message.success('物流信息更新成功');
    setTrackModalOpen(false);
    fetchData();
  };

  const handleUpdateStatus = async (id, status) => {
    await fulfillmentAPI.updateStatus(id, status);
    message.success('状态更新成功');
    fetchData();
  };

  const columns = [
    { title: '履约单号', dataIndex: 'fulfillmentNo', width: 160 },
    { title: '订单号', dataIndex: 'orderNo', width: 150 },
    { title: '类型', dataIndex: 'type', width: 80 },
    { title: '承运商', dataIndex: 'carrierName', width: 100 },
    { title: '运单号', dataIndex: 'trackingNumber', width: 140 },
    {
      title: '状态', dataIndex: 'status', width: 90,
      render: (s) => <Tag color={statusMap[s]?.color}>{statusMap[s]?.text || s}</Tag>,
    },
    { title: '预计送达', dataIndex: 'estimatedDelivery', width: 120,
      render: (v) => v ? new Date(v).toLocaleDateString() : '-' },
    {
      title: '操作', width: 220,
      render: (_, r) => (
        <Space>
          <Button type="link" size="small" onClick={() => handleTracking(r)}>物流</Button>
          <Select size="small" defaultValue={r.status} style={{ width: 100 }}
            onChange={(s) => handleUpdateStatus(r.id, s)} options={[
              { label: '已发货', value: 'SHIPPED' }, { label: '运输中', value: 'IN_TRANSIT' },
              { label: '已送达', value: 'DELIVERED' }, { label: '已签收', value: 'SIGNED' },
            ]} />
        </Space>
      ),
    },
  ];

  return (
    <div>
      <Card title="🚚 履约管理" extra={
        <Button type="primary" icon={<PlusOutlined />} onClick={handleCreate}>新建履约单</Button>
      } style={{ borderRadius: 12 }}>
        <Table columns={columns} dataSource={data.records} rowKey="id"
          loading={loading} size="middle"
          pagination={{
            current: params.page, pageSize: params.size, total: data.total,
            onChange: (p, s) => setParams({ ...params, page: p, size: s }),
            showSizeChanger: true, showTotal: (t) => `共 ${t} 条`,
          }} />
      </Card>

      <Modal title="新建履约单" open={modalOpen}
        onCancel={() => setModalOpen(false)} onOk={handleSubmit} destroyOnClose>
        <Form form={form} layout="vertical" style={{ marginTop: 16 }}>
          <Form.Item name="orderNo" label="关联订单号" rules={[{ required: true }]}>
            <Input placeholder="请输入订单号" />
          </Form.Item>
          <Form.Item name="originAddress" label="发货地址">
            <Input.TextArea rows={2} />
          </Form.Item>
          <Form.Item name="destinationAddress" label="收货地址" rules={[{ required: true }]}>
            <Input.TextArea rows={2} />
          </Form.Item>
        </Form>
      </Modal>

      <Modal title="更新物流信息" open={trackModalOpen}
        onCancel={() => setTrackModalOpen(false)} onOk={handleTrackingSubmit}>
        <Form form={trackForm} layout="vertical" style={{ marginTop: 16 }}>
          <Form.Item name="carrierName" label="承运商">
            <Select options={[
              { label: '顺丰速运', value: '顺丰速运' }, { label: '京东物流', value: '京东物流' },
              { label: '中通快递', value: '中通快递' }, { label: '圆通速递', value: '圆通速递' },
            ]} />
          </Form.Item>
          <Form.Item name="trackingNumber" label="运单号" rules={[{ required: true }]}>
            <Input placeholder="请输入运单号" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}
