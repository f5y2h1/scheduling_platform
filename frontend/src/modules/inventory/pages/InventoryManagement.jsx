import { useState, useEffect } from 'react';
import { Table, Button, Space, Tag, Alert, message, Input } from 'antd';
import { PlusOutlined, ArrowUpOutlined, ArrowDownOutlined } from '@ant-design/icons';
import { inventoryAPI } from '@/services/api';
import { useTable, useModal } from '@/hooks';
import { PageHeader, FormModal } from '@/components/common';

const statusMap = {
  NORMAL: { color: 'green', text: '正常' },
  LOW: { color: 'orange', text: '低库存' },
  OUT_OF_STOCK: { color: 'red', text: '缺货' },
  OVERSTOCK: { color: 'purple', text: '过剩' },
};

export default function InventoryManagement() {
  const [keyword, setKeyword] = useState('');
  const [alerts, setAlerts] = useState([]);
  const { data, loading, pagination, handleChange, refresh } = useTable(inventoryAPI.list, { page: 1, size: 20 });
  const { visible, form, show, hide, confirm } = useModal();

  useEffect(() => {
    inventoryAPI.alerts().then(setAlerts);
  }, [refresh]);

  const handleCreate = () => show(null);

  const handleSubmit = async (values) => {
    values.safetyStock = values.safetyStock || Math.floor((values.quantity || 0) * 0.3);
    await inventoryAPI.create(values);
    message.success('库存记录创建成功');
    refresh();
  };

  const handleStockIn = async (record) => {
    const qty = parseInt(prompt('入库数量:'), 10);
    if (qty && qty > 0) {
      await inventoryAPI.stockIn(record.id, qty);
      message.success(`入库 ${qty} 件`);
      refresh();
    }
  };

  const handleStockOut = async (record) => {
    const qty = parseInt(prompt('出库数量:'), 10);
    if (qty && qty > 0) {
      try {
        await inventoryAPI.stockOut(record.id, qty);
        message.success(`出库 ${qty} 件`);
        refresh();
      } catch (e) { /* handled by interceptor */ }
    }
  };

  const columns = [
    { title: '商品', dataIndex: 'productName', width: 140 },
    { title: 'SKU', dataIndex: 'skuCode', width: 100 },
    { title: '仓库', dataIndex: 'warehouseName', width: 100 },
    { title: '库存量', dataIndex: 'quantity', width: 100, render: (v) => <span style={{ fontWeight: 600 }}>{v}</span> },
    { title: '安全库存', dataIndex: 'safetyStock', width: 100 },
    { title: '锁定', dataIndex: 'lockedQuantity', width: 80 },
    { title: '可用', dataIndex: 'availableQuantity', width: 80,
      render: (v, r) => (
        <span style={{ color: v <= 0 ? '#ef4444' : v <= r.safetyStock ? '#f59e0b' : '#10b981', fontWeight: 600 }}>{v}</span>
      ),
    },
    { title: '状态', dataIndex: 'status', width: 90, render: (s) => <Tag color={statusMap[s]?.color}>{statusMap[s]?.text || s}</Tag> },
    {
      title: '操作', width: 160,
      render: (_, record) => (
        <Space>
          <Button type="link" size="small" icon={<ArrowDownOutlined />} onClick={() => handleStockIn(record)}>入库</Button>
          <Button type="link" size="small" icon={<ArrowUpOutlined />} disabled={record.availableQuantity <= 0} onClick={() => handleStockOut(record)}>出库</Button>
        </Space>
      ),
    },
  ];

  return (
    <div>
      {alerts.length > 0 && (
        <Alert type="warning" showIcon closable
          message={`库存预警：${alerts.length} 个SKU库存不足，请及时补货！`}
          style={{ marginBottom: 16, borderRadius: 10 }} />
      )}

      <PageHeader
        title="库存管理"
        breadcrumb={[{ title: '库存管理' }]}
        extra={
          <Space>
            <Input.Search placeholder="搜索商品" allowClear value={keyword} onChange={(e) => setKeyword(e.target.value)}
              onSearch={refresh} style={{ width: 200 }} />
            <Button type="primary" icon={<PlusOutlined />} onClick={handleCreate}>新增记录</Button>
          </Space>
        }
      />

      <Table columns={columns} dataSource={data} rowKey="id" loading={loading} size="middle"
        pagination={{ current: pagination.current, pageSize: pagination.pageSize, total: pagination.total,
          onChange: handleChange, showSizeChanger: true, showTotal: (t) => `共 ${t} 条`,
        }} />

      <FormModal visible={visible} title="新增库存记录" onCancel={hide} onOk={(values) => confirm(() => handleSubmit(values))} form={form}>
        <FormModal.Item name="productName" label="商品名称" rules={[{ required: true }]}>
          <Input placeholder="请输入商品名称" />
        </FormModal.Item>
        <FormModal.Item name="skuCode" label="SKU编码">
          <Input placeholder="SKU编码" />
        </FormModal.Item>
        <FormModal.Item name="warehouseName" label="仓库">
          <Input placeholder="仓库名称" />
        </FormModal.Item>
        <Space size={16}>
          <FormModal.Item name="quantity" label="库存数量" rules={[{ required: true }]}>
            <Input placeholder="数量" />
          </FormModal.Item>
          <FormModal.Item name="safetyStock" label="安全库存">
            <Input placeholder="安全库存" />
          </FormModal.Item>
        </Space>
      </FormModal>
    </div>
  );
}