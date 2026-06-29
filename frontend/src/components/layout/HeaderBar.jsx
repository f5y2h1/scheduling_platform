import React from 'react';
import { Layout, Dropdown, Avatar, Space, Badge, theme } from 'antd';
import {
  UserOutlined, LogoutOutlined, BellOutlined,
  SettingOutlined, KeyOutlined,
} from '@ant-design/icons';
import { useAuthStore } from '@/store/authStore';

const { Header } = Layout;

export default function HeaderBar() {
  const { userInfo, logout } = useAuthStore();
  const { token } = theme.useToken();

  const userMenu = {
    items: [
      { key: 'profile', icon: <UserOutlined />, label: '个人中心' },
      { key: 'settings', icon: <SettingOutlined />, label: '系统设置' },
      { key: 'password', icon: <KeyOutlined />, label: '修改密码' },
      { type: 'divider' },
      { key: 'logout', icon: <LogoutOutlined />, label: '退出登录', danger: true },
    ],
    onClick: ({ key }) => {
      if (key === 'logout') logout();
    },
  };

  return (
    <Header style={{
      background: token.colorBgContainer,
      padding: '0 24px',
      display: 'flex',
      justifyContent: 'flex-end',
      alignItems: 'center',
      boxShadow: '0 1px 4px rgba(0,0,0,0.04)',
      position: 'sticky',
      top: 0,
      zIndex: 99,
      height: 56,
    }}>
      <Space size={24}>
        <Badge count={5} size="small">
          <BellOutlined style={{ fontSize: 18, cursor: 'pointer', color: '#666' }} />
        </Badge>
        <Dropdown menu={userMenu} placement="bottomRight">
          <Space style={{ cursor: 'pointer' }}>
            <Avatar
              size={34}
              icon={<UserOutlined />}
              style={{ backgroundColor: token.colorPrimary }}
            />
            <span style={{ fontWeight: 500, color: '#333' }}>
              {userInfo?.realName || userInfo?.username || '管理员'}
            </span>
          </Space>
        </Dropdown>
      </Space>
    </Header>
  );
}
