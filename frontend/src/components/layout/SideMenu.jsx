import React from 'react';
import { Menu } from 'antd';
import {
  DashboardOutlined, SettingOutlined, ShoppingCartOutlined,
  InboxOutlined, ScheduleOutlined, CarOutlined, TeamOutlined,
  BarChartOutlined, RobotOutlined, BookOutlined,
} from '@ant-design/icons';

const iconMap = {
  DashboardOutlined: <DashboardOutlined />,
  SettingOutlined: <SettingOutlined />,
  ShoppingCartOutlined: <ShoppingCartOutlined />,
  InboxOutlined: <InboxOutlined />,
  ScheduleOutlined: <ScheduleOutlined />,
  CarOutlined: <CarOutlined />,
  TeamOutlined: <TeamOutlined />,
  BarChartOutlined: <BarChartOutlined />,
  RobotOutlined: <RobotOutlined />,
  BookOutlined: <BookOutlined />,
};

function renderItems(items) {
  return items.map((item) => ({
    key: item.key,
    icon: iconMap[item.icon] || null,
    label: item.label,
    children: item.children ? renderItems(item.children) : undefined,
  }));
}

export default function SideMenu({ items, selectedKey, onClick, collapsed }) {
  // 计算 defaultOpenKeys
  const defaultOpenKeys = items
    .filter((i) => i.children && selectedKey?.startsWith(i.key))
    .map((i) => i.key);

  return (
    <Menu
      theme="dark"
      mode="inline"
      selectedKeys={[selectedKey]}
      defaultOpenKeys={defaultOpenKeys}
      onClick={onClick}
      items={renderItems(items)}
      style={{
        padding: '8px',
        borderRight: 0,
        marginTop: 4,
      }}
    />
  );
}
