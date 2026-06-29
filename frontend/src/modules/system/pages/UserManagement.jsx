import { useState } from 'react';
import { Table, Button, Space, Tag, Popconfirm, message, Input, Select } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import { userAPI } from '@/services/api';
import { useTable, useModal } from '@/hooks';
import { PageHeader, FormModal } from '@/components/common';

const roleMap = {
  ADMIN: { color: 'red', text: '管理员' },
  MANAGER: { color: 'blue', text: '经理' },
  OPERATOR: { color: 'green', text: '操作员' },
  USER: { color: 'default', text: '用户' },
};

export default function UserManagement() {
  const [keyword, setKeyword] = useState('');
  const { data, loading, pagination, handleChange, refresh } = useTable(userAPI.list, { page: 1, size: 20 });
  const { visible, editingId, form, show, hide, confirm } = useModal({ role: 'USER', status: 1 });

  const handleCreate = () => {
    show(null, { role: 'USER', status: 1 });
  };

  const handleEdit = (record) => {
    show(record.id, record);
  };

  const handleSubmit = async (values, id) => {
    if (id) {
      await userAPI.update(id, values);
      message.success('更新成功');
    } else {
      await userAPI.create(values);
      message.success('创建成功');
    }
    refresh();
  };

  const handleDelete = async (id) => {
    await userAPI.delete(id);
    message.success('删除成功');
    refresh();
  };

  const handleSearch = () => {
    refresh();
  };

  const columns = [
    { title: 'ID', dataIndex: 'id', width: 80 },
    { title: '用户名', dataIndex: 'username' },
    { title: '真实姓名', dataIndex: 'realName' },
    { title: '角色', dataIndex: 'role', render: (r) => <Tag color={roleMap[r]?.color}>{roleMap[r]?.text || r}</Tag> },
    { title: '状态', dataIndex: 'status', render: (s) => <Tag color={s === 1 ? 'green' : 'red'}>{s === 1 ? '正常' : '禁用'}</Tag> },
    { title: '邮箱', dataIndex: 'email' },
    { title: '手机', dataIndex: 'phone' },
    {
      title: '操作', width: 160,
      render: (_, record) => (
        <Space>
          <Button type="link" size="small" onClick={() => handleEdit(record)}>编辑</Button>
          <Popconfirm title="确认删除？" onConfirm={() => handleDelete(record.id)}>
            <Button type="link" danger size="small">删除</Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <PageHeader
        title="用户管理"
        breadcrumb={[{ title: '系统管理' }, { title: '用户管理' }]}
        extra={
          <Space>
            <Input.Search
              placeholder="搜索用户"
              allowClear
              value={keyword}
              onChange={(e) => setKeyword(e.target.value)}
              onSearch={handleSearch}
              style={{ width: 220 }}
            />
            <Button type="primary" icon={<PlusOutlined />} onClick={handleCreate}>新增用户</Button>
          </Space>
        }
      />

      <Table
        columns={columns}
        dataSource={data}
        rowKey="id"
        loading={loading}
        size="middle"
        pagination={{
          current: pagination.current,
          pageSize: pagination.pageSize,
          total: pagination.total,
          onChange: handleChange,
          showSizeChanger: true,
          showTotal: (t) => `共 ${t} 条`,
        }}
      />

      <FormModal
        visible={visible}
        title={editingId ? '编辑用户' : '新增用户'}
        onCancel={hide}
        onOk={(values) => confirm(() => handleSubmit(values, editingId))}
        form={form}
        width={520}
      >
        <FormModal.Item name="username" label="用户名" rules={[{ required: true }]}>
          <Input placeholder="请输入用户名" disabled={!!editingId} />
        </FormModal.Item>
        {!editingId && (
          <FormModal.Item name="password" label="密码" rules={[{ required: true, min: 6 }]}>
            <Input.Password placeholder="请输入密码" />
          </FormModal.Item>
        )}
        <FormModal.Item name="realName" label="真实姓名" rules={[{ required: true }]}>
          <Input placeholder="请输入真实姓名" />
        </FormModal.Item>
        <FormModal.Item name="email" label="邮箱">
          <Input placeholder="请输入邮箱" />
        </FormModal.Item>
        <FormModal.Item name="phone" label="手机号">
          <Input placeholder="请输入手机号" />
        </FormModal.Item>
        <FormModal.Item name="role" label="角色" rules={[{ required: true }]}>
          <Select options={[
            { label: '管理员', value: 'ADMIN' },
            { label: '经理', value: 'MANAGER' },
            { label: '操作员', value: 'OPERATOR' },
            { label: '用户', value: 'USER' },
          ]} />
        </FormModal.Item>
      </FormModal>
    </div>
  );
}