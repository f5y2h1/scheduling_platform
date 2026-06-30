import React, { useState } from 'react';
import { Layout } from 'antd';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import SideMenu from './SideMenu';
import HeaderBar from './HeaderBar';

const { Content, Sider } = Layout;

export default function MainLayout({ children }) {
  const [collapsed, setCollapsed] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  const menuItems = [
    { key: '/dashboard', icon: 'DashboardOutlined', label: '仪表盘' },
    { key: '/system', icon: 'SettingOutlined', label: '系统管理', children: [
        { key: '/system/users', label: '用户管理' },
      ]
    },
    { key: '/orders', icon: 'ShoppingCartOutlined', label: '订单管理' },
    { key: '/inventory', icon: 'InboxOutlined', label: '库存管理' },
    { key: '/scheduling', icon: 'ScheduleOutlined', label: '调度中心' },
    { key: '/fulfillment', icon: 'CarOutlined', label: '履约管理' },
    { key: '/suppliers', icon: 'TeamOutlined', label: '供应商管理' },
    { key: '/reports', icon: 'BarChartOutlined', label: '数据报表' },
    { key: '/ai', icon: 'RobotOutlined', label: 'AI智能服务', children: [
        { key: '/ai-dashboard', label: 'AI 智能看板' },
        { key: '/ai-workflow', label: 'Agent 工作流编排' },
        { key: '/knowledge', label: 'RAG 知识库' },
      ]
    },
  ];

  const getSelectedKey = () => {
    const path = location.pathname;
    if (path.startsWith('/system')) return '/system';
    if (path.startsWith('/ai')) return '/ai';
    return path;
  };

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider
        collapsible
        collapsed={collapsed}
        onCollapse={setCollapsed}
        width={240}
        style={{
          overflow: 'auto',
          height: '100vh',
          position: 'fixed',
          left: 0,
          top: 0,
          bottom: 0,
          zIndex: 100,
          boxShadow: '2px 0 8px rgba(0,0,0,0.06)',
        }}
      >
        <div style={{
          height: 64,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: '#fff',
          fontSize: collapsed ? 16 : 20,
          fontWeight: 700,
          borderBottom: '1px solid rgba(255,255,255,0.1)',
          letterSpacing: 2,
        }}>
          {collapsed ? '🚀' : '🚀 XUNI'}
        </div>
        <SideMenu
          items={menuItems}
          selectedKey={getSelectedKey()}
          onClick={({ key }) => navigate(key)}
          collapsed={collapsed}
        />
      </Sider>
      <Layout style={{ marginLeft: collapsed ? 80 : 240, transition: 'margin-left 0.2s' }}>
        <HeaderBar />
        <Content style={{ margin: 20, minHeight: 280 }}>
          {children || <Outlet />}
        </Content>
        <div style={{
          textAlign: 'center',
          padding: '12px 20px',
          color: '#64748b',
          fontSize: 12,
          borderTop: '1px solid #f0f0f0',
        }}>
          Xuni Scheduling Platform v1.0.0 ©2026 | 供应链智能调度平台
        </div>
      </Layout>
    </Layout>
  );
}
