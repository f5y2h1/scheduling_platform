import { Button, Space, Dropdown, Menu } from 'antd';
import { EditOutlined, DeleteOutlined, MoreOutlined, EyeOutlined } from '@ant-design/icons';

export default function ActionButtons({
  onEdit,
  onDelete,
  onView,
  actions = [],
  showEdit = true,
  showDelete = true,
  showView = false,
}) {
  const menuItems = [
    showView && { key: 'view', label: '查看', icon: <EyeOutlined /> },
    showEdit && { key: 'edit', label: '编辑', icon: <EditOutlined /> },
    showDelete && { key: 'delete', label: '删除', icon: <DeleteOutlined /> },
    ...actions.map((action) => ({
      key: action.key,
      label: action.label,
      icon: action.icon,
    })),
  ].filter(Boolean);

  if (menuItems.length === 0) return null;
  if (menuItems.length <= 2) {
    return (
      <Space>
        {showView && <Button type="text" onClick={onView}><EyeOutlined /></Button>}
        {showEdit && <Button type="text" onClick={onEdit}><EditOutlined /></Button>}
        {showDelete && <Button type="text" danger onClick={onDelete}><DeleteOutlined /></Button>}
        {actions.map((action) => (
          <Button key={action.key} type="text" onClick={action.onClick}>
            {action.icon}
          </Button>
        ))}
      </Space>
    );
  }

  return (
    <Dropdown
      menu={{
        items: menuItems,
        onClick: ({ key }) => {
          if (key === 'edit') onEdit();
          if (key === 'delete') onDelete();
          if (key === 'view') onView();
          const customAction = actions.find((a) => a.key === key);
          if (customAction) customAction.onClick();
        },
      }}
    >
      <Button type="text"><MoreOutlined /></Button>
    </Dropdown>
  );
}