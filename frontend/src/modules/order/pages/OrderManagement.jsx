import { useState } from 'react';
import { Table, Button, Space, Tag, Modal, Form, Input, Select, InputNumber, Descriptions, Popconfirm, message } from 'antd';
import { PlusOutlined, EyeOutlined } from '@ant-design/icons';
import { orderAPI } from '@/services/api';
import { useTable, useModal } from '@/hooks';
import { usePersistedState } from '@/hooks/usePersistedState';
import { PageHeader, FormModal } from '@/components/common';

const statusMap = {
  PENDING: { color: 'default', text: '待处理' },
  CONFIRMED: { color: 'blue', text: '已确认' },
  DISPATCHING: { color: 'orange', text: '调度中' },
  SHIPPING: { color: 'purple', text: '运输中' },
  DELIVERED: { color: 'green', text: '已送达' },
  CANCELLED: { color: 'red', text: '已取消' },
};

export default function OrderManagement() {
  const [keyword, setKeyword] = usePersistedState('order_keyword', '');
  const [statusFilter, setStatusFilter] = useState('');
  const [detailOpen, setDetailOpen] = useState(false);
  const [detail, setDetail] = useState(null);
  const { data, loading, pagination, handleChange, refresh } = useTable(orderAPI.list, { page: 1, size: 20 });
  const { visible, form, show, hide, confirm } = useModal();

  const handleCreate = () => show(null);

  const handleSubmit = async (values) => {
    await orderAPI.create(values);
    message.success('订单创建成功');
    refresh();
  };

  const handleCancel = async (id) => {
    await orderAPI.cancel(id);
    message.success('订单已取消');
    refresh();
  };

  const showDetail = async (record) => {
    try {
      setDetail(await orderAPI.getById(record.id));
    } catch (e) {
      setDetail(record);
    }
    setDetailOpen(true);
  };

  const columns = [
    { title: '订单号', dataIndex: 'orderNo', width: 160 },
    { title: '客户', dataIndex: 'customerName', width: 120 },
    { title: '商品', dataIndex: 'productName', width: 120 },
    { title: '数量', dataIndex: 'quantity', width: 80 },
    { title: '金额', dataIndex: 'totalAmount', width: 100, render: (v) => v ? `¥${v}` : '-' },
    { title: '状态', dataIndex: 'status', width: 100, render: (s) => <Tag color={statusMap[s]?.color}>{statusMap[s]?.text || s}</Tag> },
    { title: '仓库', dataIndex: 'warehouseName', width: 100 },
    {
      title: '操作', width: 180,
      render: (_, record) => (
        <Space>
          <Button type="link" size="small" icon={<EyeOutlined />} onClick={() => showDetail(record)}>详情</Button>
          {(record.status === 'PENDING' || record.status === 'CONFIRMED') && (
            <Popconfirm title="确认取消？" onConfirm={() => handleCancel(record.id)}>
              <Button type="link" danger size="small">取消</Button>
            </Popconfirm>
          )}
        </Space>
      ),
    },
  ];

  return (
    <div>
      <PageHeader
        title="订单管理"
        breadcrumb={[{ title: '订单管理' }]}
        extra={
          <Space>
            <Select defaultValue="" style={{ width: 120 }} onChange={setStatusFilter} options={[
              { label: '全部状态', value: '' }, { label: '待处理', value: 'PENDING' },
              { label: '运输中', value: 'SHIPPING' }, { label: '已送达', value: 'DELIVERED' },
              { label: '已取消', value: 'CANCELLED' },
            ]} />
            <Input.Search placeholder="搜索客户" allowClear value={keyword} onChange={(e) => setKeyword(e.target.value)}
              onSearch={refresh} style={{ width: 200 }} />
            <Button type="primary" icon={<PlusOutlined />} onClick={handleCreate}>新建订单</Button>
          </Space>
        }
      />

      <Table columns={columns} dataSource={data} rowKey="id" loading={loading} size="middle"
        pagination={{ current: pagination.current, pageSize: pagination.pageSize, total: pagination.total,
          onChange: handleChange, showSizeChanger: true, showTotal: (t) => `共 ${t} 条`,
        }} />

      <FormModal visible={visible} title="新建订单" onCancel={hide} onOk={(values) => confirm(() => handleSubmit(values))} form={form} width={600}>
        <FormModal.Item name="customerName" label="客户名称" rules={[{ required: true }]}>
          <Input placeholder="请输入客户名称" />
        </FormModal.Item>
        <FormModal.Item name="productName" label="商品名称" rules={[{ required: true }]}>
          <Input placeholder="请输入商品名称" />
        </FormModal.Item>
        <Space size={16}>
          <FormModal.Item name="quantity" label="数量" rules={[{ required: true }]}>
            <InputNumber min={1} placeholder="数量" />
          </FormModal.Item>
          <FormModal.Item name="unitPrice" label="单价">
            <InputNumber min={0} placeholder="单价" style={{ width: 160 }} />
          </FormModal.Item>
        </Space>
        <FormModal.Item name="warehouseName" label="发货仓库">
          <Select options={[
            { label: '北京仓', value: '北京仓' }, { label: '上海仓', value: '上海仓' },
            { label: '广州仓', value: '广州仓' }, { label: '成都仓', value: '成都仓' },
          ]} />
        </FormModal.Item>
        <FormModal.Item name="shippingAddress" label="收货地址">
          <Input.TextArea rows={2} placeholder="请输入收货地址" />
        </FormModal.Item>
        <FormModal.Item name="remark" label="备注">
          <Input.TextArea rows={2} placeholder="备注信息" />
        </FormModal.Item>
      </FormModal>

      <Modal title="订单详情" open={detailOpen} onCancel={() => setDetailOpen(false)} footer={null} width={640}>
        {detail && (
          <Descriptions bordered column={2} size="small" style={{ marginTop: 16 }}>
            <Descriptions.Item label="订单号">{detail.orderNo}</Descriptions.Item>
            <Descriptions.Item label="状态"><Tag color={statusMap[detail.status]?.color}>{statusMap[detail.status]?.text || detail.status}</Tag></Descriptions.Item>
            <Descriptions.Item label="客户">{detail.customerName}</Descriptions.Item>
            <Descriptions.Item label="商品">{detail.productName}</Descriptions.Item>
            <Descriptions.Item label="数量">{detail.quantity}</Descriptions.Item>
            <Descriptions.Item label="金额">¥{detail.totalAmount}</Descriptions.Item>
            <Descriptions.Item label="仓库">{detail.warehouseName}</Descriptions.Item>
            <Descriptions.Item label="地址" span={2}>{detail.shippingAddress}</Descriptions.Item>
            <Descriptions.Item label="备注" span={2}>{detail.remark || '-'}</Descriptions.Item>
          </Descriptions>
        )}
      </Modal>
    </div>
  );
}