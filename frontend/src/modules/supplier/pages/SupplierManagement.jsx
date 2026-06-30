import React, { useEffect, useState } from 'react';
import {
  Table, Button, Space, Tag, Modal, Form, Input, Select,
  Card, message, Rate, Descriptions,
} from 'antd';
import { PlusOutlined, EditOutlined, EyeOutlined, SearchOutlined } from '@ant-design/icons';
import { supplierAPI } from '@/services/api';

export default function SupplierManagement() {
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState({ records: [], total: 0 });
  const [modalOpen, setModalOpen] = useState(false);
  const [detailOpen, setDetailOpen] = useState(false);
  const [detail, setDetail] = useState(null);
  const [editing, setEditing] = useState(null);
  const [form] = Form.useForm();
  const [params, setParams] = useState({ page: 1, size: 20 });

  const fetchData = async () => {
    setLoading(true);
    try { setData(await supplierAPI.list(params)); } catch (e) { /* */ }
    setLoading(false);
  };

  useEffect(() => { fetchData(); }, [params]);

  const handleCreate = () => { setEditing(null); form.resetFields(); setModalOpen(true); };
  const handleEdit = (r) => { setEditing(r); form.setFieldsValue(r); setModalOpen(true); };
  const handleSubmit = async () => {
    const vals = await form.validateFields();
    if (editing) {
      await supplierAPI.update(editing.id, vals);
      message.success('更新成功');
    } else {
      await supplierAPI.create(vals);
      message.success('创建成功');
    }
    setModalOpen(false);
    fetchData();
  };

  const showDetail = (r) => { setDetail(r); setDetailOpen(true); };

  const columns = [
    { title: '编号', dataIndex: 'code', width: 100 },
    { title: '名称', dataIndex: 'name', width: 160 },
    { title: '类型', dataIndex: 'type', width: 100 },
    { title: '联系人', dataIndex: 'contactName', width: 100 },
    { title: '电话', dataIndex: 'contactPhone', width: 120 },
    {
      title: '评级', dataIndex: 'rating', width: 160,
      render: (v) => <Rate disabled value={v ? v / 1 : 4} style={{ fontSize: 14 }} />,
    },
    {
      title: '状态', dataIndex: 'status', width: 90,
      render: (s) => <Tag color={s === 'ACTIVE' ? 'green' : s === 'INACTIVE' ? 'default' : 'red'}>
        {s === 'ACTIVE' ? '合作中' : s === 'INACTIVE' ? '暂停' : '黑名单'}
      </Tag>,
    },
    {
      title: '操作', width: 150,
      render: (_, r) => (
        <Space>
          <Button type="link" size="small" icon={<EyeOutlined />} onClick={() => showDetail(r)} />
          <Button type="link" size="small" icon={<EditOutlined />} onClick={() => handleEdit(r)} />
        </Space>
      ),
    },
  ];

  return (
    <div>
      <Card title="🏢 供应商管理" extra={
        <Space>
          <Input.Search placeholder="搜索供应商" style={{ width: 200 }}
            onSearch={(v) => setParams({ ...params, keyword: v, page: 1 })} />
          <Button type="primary" icon={<PlusOutlined />} onClick={handleCreate}>新增供应商</Button>
        </Space>
      } style={{ borderRadius: 12 }}>
        <Table columns={columns} dataSource={data.records} rowKey="id"
          loading={loading} size="middle"
          pagination={{
            current: params.page, pageSize: params.size, total: data.total,
            onChange: (p, s) => setParams({ ...params, page: p, size: s }),
            showSizeChanger: true, showTotal: (t) => `共 ${t} 条`,
          }} />
      </Card>

      <Modal title={editing ? '编辑供应商' : '新增供应商'} open={modalOpen}
        onCancel={() => setModalOpen(false)} onOk={handleSubmit} destroyOnHidden>
        <Form form={form} layout="vertical" style={{ marginTop: 16 }}>
          <Form.Item name="name" label="名称" rules={[{ required: true }]}>
            <Input placeholder="供应商名称" />
          </Form.Item>
          <Form.Item name="code" label="编号">
            <Input placeholder="供应商编号" />
          </Form.Item>
          <Form.Item name="type" label="类型">
            <Select options={[
              { label: '制造商', value: 'MANUFACTURER' },
              { label: '分销商', value: 'DISTRIBUTOR' },
              { label: '批发商', value: 'WHOLESALER' },
              { label: '物流商', value: 'LOGISTICS' },
            ]} />
          </Form.Item>
          <Form.Item name="contactName" label="联系人">
            <Input placeholder="联系人姓名" />
          </Form.Item>
          <Form.Item name="contactPhone" label="联系电话">
            <Input placeholder="联系电话" />
          </Form.Item>
          <Form.Item name="address" label="地址">
            <Input.TextArea rows={2} />
          </Form.Item>
        </Form>
      </Modal>

      <Modal title="供应商详情" open={detailOpen}
        onCancel={() => setDetailOpen(false)} footer={null} width={600}>
        {detail && (
          <Descriptions bordered column={2} size="small" style={{ marginTop: 16 }}>
            <Descriptions.Item label="名称">{detail.name}</Descriptions.Item>
            <Descriptions.Item label="编号">{detail.code}</Descriptions.Item>
            <Descriptions.Item label="类型">{detail.type}</Descriptions.Item>
            <Descriptions.Item label="状态">
              <Tag color={detail.status === 'ACTIVE' ? 'green' : 'red'}>{detail.status}</Tag>
            </Descriptions.Item>
            <Descriptions.Item label="联系人">{detail.contactName}</Descriptions.Item>
            <Descriptions.Item label="电话">{detail.contactPhone}</Descriptions.Item>
            <Descriptions.Item label="邮箱">{detail.contactEmail}</Descriptions.Item>
            <Descriptions.Item label="合作年限">{detail.cooperationYears}年</Descriptions.Item>
            <Descriptions.Item label="地址" span={2}>{detail.address}</Descriptions.Item>
            <Descriptions.Item label="准时交货率">
              {detail.onTimeDeliveryRate ? (detail.onTimeDeliveryRate * 100).toFixed(1) + '%' : '-'}
            </Descriptions.Item>
            <Descriptions.Item label="质量合格率">
              {detail.qualityPassRate ? (detail.qualityPassRate * 100).toFixed(1) + '%' : '-'}
            </Descriptions.Item>
          </Descriptions>
        )}
      </Modal>
    </div>
  );
}
