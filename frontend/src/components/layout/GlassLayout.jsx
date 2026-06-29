/**
 * 现代化布局组件 - Glassmorphism 风格
 * 特点：毛玻璃效果、渐变背景、浮动卡片、流畅动画
 */
import React, { useState } from 'react';
import { Layout, Menu, Avatar, Dropdown, Badge, Tag, Space } from 'antd';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import {
  DashboardOutlined, SettingOutlined, ShoppingCartOutlined,
  InboxOutlined, ScheduleOutlined, CarOutlined, TeamOutlined,
  BarChartOutlined, RobotOutlined, BookOutlined, UserOutlined,
  LogoutOutlined, BellOutlined, MenuFoldOutlined, MenuUnfoldOutlined,
  ThunderboltOutlined,ExperimentOutlined,
} from '@ant-design/icons';

const { Header, Sider, Content } = Layout;

const menuItems = [
  { key: '/dashboard', icon: <DashboardOutlined />, label: '仪表盘' },
  { key: '/orders', icon: <ShoppingCartOutlined />, label: '订单管理' },
  { key: '/inventory', icon: <InboxOutlined />, label: '库存管理' },
  { key: '/scheduling', icon: <ScheduleOutlined />, label: '调度中心' },
  { key: '/fulfillment', icon: <CarOutlined />, label: '履约管理' },
  { key: '/suppliers', icon: <TeamOutlined />, label: '供应商管理' },
  { key: '/reports', icon: <BarChartOutlined />, label: '数据报表' },
  {
    key: '/ai',
    icon: <RobotOutlined />,
    label: 'AI智能服务',
    children: [
      { key: '/ai-dashboard', icon: <ThunderboltOutlined />, label: 'AI 智能看板' },
      { key: '/ai-workflow', icon: <ExperimentOutlined />, label: 'Agent 工作流编排' },
      { key: '/knowledge', icon: <BookOutlined />, label: 'RAG 知识库' },
    ],
  },
  {
    key: '/system',
    icon: <SettingOutlined />,
    label: '系统管理',
    children: [
      { key: '/system/users', icon: <UserOutlined />, label: '用户管理' },
    ],
  },
];

const userMenuItems = [
  { key: 'profile', icon: <UserOutlined />, label: '个人中心' },
  { type: 'divider' },
  { key: 'logout', icon: <LogoutOutlined />, label: '退出登录', danger: true },
];

export default function GlassLayout() {
  const [collapsed, setCollapsed] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  const getSelectedKeys = () => {
    const path = location.pathname;
    if (path === '/ai-dashboard') return ['/ai-dashboard'];
    if (path === '/ai-workflow') return ['/ai-workflow'];
    if (path === '/knowledge') return ['/knowledge'];
    if (path === '/system/users') return ['/system/users'];
    return [path];
  };

  const getOpenKeys = () => {
    const path = location.pathname;
    const openKeys = [];
    if (path.startsWith('/ai')) openKeys.push('/ai');
    if (path.startsWith('/system')) openKeys.push('/system');
    return openKeys;
  };

  const getSelectedSubKeys = () => {
    const path = location.pathname;
    if (path === '/ai-dashboard') return ['/ai-dashboard'];
    if (path === '/ai-workflow') return ['/ai-workflow'];
    if (path === '/knowledge') return ['/knowledge'];
    return [];
  };

  return (
    <Layout style={{ minHeight: '100vh', background: '#f0f2f5' }}>
      {/* 侧边栏 - 毛玻璃效果 */}
      <Sider
        collapsible
        collapsed={collapsed}
        onCollapse={setCollapsed}
        width={260}
        collapsedWidth={80}
        trigger={null}
        style={{
          position: 'fixed',
          left: 0,
          top: 0,
          bottom: 0,
          zIndex: 100,
          background: 'linear-gradient(180deg, #1e1b4b 0%, #312e81 50%, #1e1b4b 100%)',
          boxShadow: '4px 0 20px rgba(0, 0, 0, 0.15)',
          overflow: 'hidden',
        }}
      >
        {/* Logo 区域 */}
        <div style={{
          height: 72,
          display: 'flex',
          alignItems: 'center',
          justifyContent: collapsed ? 'center' : 'flex-start',
          padding: collapsed ? 0 : '0 20px',
          borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
          transition: 'all 0.3s ease',
        }}>
          <div style={{
            width: 40,
            height: 40,
            borderRadius: 12,
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: 20,
            boxShadow: '0 4px 15px rgba(102, 126, 234, 0.4)',
          }}>
            🚀
          </div>
          {!collapsed && (
            <div style={{ marginLeft: 12 }}>
              <div style={{ color: '#fff', fontSize: 18, fontWeight: 700, letterSpacing: 1 }}>
                XUNI
              </div>
              <div style={{ color: 'rgba(255,255,255,0.5)', fontSize: 11 }}>
                智能调度平台
              </div>
            </div>
          )}
        </div>

        {/* 菜单 */}
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={getSelectedKeys()}
          defaultOpenKeys={getOpenKeys()}
          onClick={({ key }) => navigate(key)}
          items={menuItems}
          style={{
            background: 'transparent',
            borderRight: 0,
            marginTop: 16,
            padding: '0 8px',
          }}
          inlineCollapsed={collapsed}
        />

        {/* 折叠按钮 */}
        <div
          onClick={() => setCollapsed(!collapsed)}
          style={{
            position: 'absolute',
            bottom: 20,
            left: '50%',
            transform: 'translateX(-50%)',
            width: collapsed ? 40 : 'calc(100% - 32px)',
            height: 40,
            borderRadius: 10,
            background: 'rgba(255, 255, 255, 0.1)',
            backdropFilter: 'blur(10px)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            cursor: 'pointer',
            transition: 'all 0.3s ease',
            color: '#fff',
            fontSize: 16,
          }}
        >
          {collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
        </div>
      </Sider>

      <Layout style={{ marginLeft: collapsed ? 80 : 260, transition: 'margin-left 0.3s ease' }}>
        {/* 顶部导航栏 */}
        <Header style={{
          position: 'sticky',
          top: 0,
          zIndex: 99,
          padding: '0 24px',
          background: 'rgba(255, 255, 255, 0.85)',
          backdropFilter: 'blur(20px)',
          boxShadow: '0 2px 20px rgba(0, 0, 0, 0.06)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          height: 64,
        }}>
          {/* 面包屑区域 */}
          <div style={{ fontSize: 14, color: '#666' }}>
            <span style={{ color: '#999' }}>首页</span>
            {location.pathname !== '/dashboard' && location.pathname !== '/' && (
              <>
                <span style={{ margin: '0 8px', color: '#d9d9d9' }}>/</span>
                <span style={{ color: '#1e1b4b', fontWeight: 500 }}>
                  {menuItems.find(item => item.key === '/' + location.pathname.split('/')[1])?.label || '当前页面'}
                </span>
              </>
            )}
          </div>

          {/* 右侧用户区域 */}
          <Space size={20}>
            <Badge count={3} size="small">
              <BellOutlined style={{ fontSize: 18, color: '#666', cursor: 'pointer' }} />
            </Badge>

            <Dropdown menu={{
              items: userMenuItems,
              onClick: ({ key }) => {
                if (key === 'logout') {
                  navigate('/login');
                }
              }
            }} placement="bottomRight">
              <Space style={{ cursor: 'pointer' }}>
                <Avatar size={36} style={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
                  管
                </Avatar>
                <div style={{ lineHeight: 1.3 }}>
                  <div style={{ fontSize: 14, fontWeight: 500, color: '#1e1b4b' }}>管理员</div>
                  <div style={{ fontSize: 11, color: '#999' }}>系统管理员</div>
                </div>
              </Space>
            </Dropdown>
          </Space>
        </Header>

        {/* 主内容区 */}
        <Content style={{
          padding: 24,
          minHeight: 'calc(100vh - 64px - 48px)',
          background: 'transparent',
        }}>
          <div style={{
            background: '#fff',
            borderRadius: 16,
            boxShadow: '0 4px 20px rgba(0, 0, 0, 0.05)',
            padding: 24,
            minHeight: 'calc(100vh - 64px - 96px)',
          }}>
            <Outlet />
          </div>
        </Content>

        {/* 底部版权 */}
        <div style={{
          textAlign: 'center',
          padding: '16px 24px',
          color: '#999',
          fontSize: 12,
          borderTop: '1px solid rgba(0,0,0,0.05)',
        }}>
          <Space>
            <Tag color="purple">v2.0</Tag>
            <span>Xuni Scheduling Platform © 2026</span>
            <span>|</span>
            <span>供应链智能调度平台</span>
          </Space>
        </div>
      </Layout>
    </Layout>
  );
}
