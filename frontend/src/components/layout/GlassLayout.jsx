/**
 * Xuni v3.0 - Modern Tech Layout
 * 深蓝渐变 + 粒子背景 + 流畅动效 + 发光边框
 */
import React, { useState, useMemo } from 'react';
import {
  Layout, Menu, Avatar, Dropdown, Badge, Tag, Space,
  Modal, Descriptions, message, Tooltip, Button,
} from 'antd';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import {
  DashboardOutlined, SettingOutlined, ShoppingCartOutlined,
  InboxOutlined, ScheduleOutlined, CarOutlined, TeamOutlined,
  BarChartOutlined, RobotOutlined, BookOutlined, UserOutlined,
  LogoutOutlined, BellOutlined, MenuFoldOutlined, MenuUnfoldOutlined,
  ThunderboltOutlined, ExperimentOutlined,
  ApiOutlined, SafetyOutlined,
} from '@ant-design/icons';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuthStore } from '@/store/authStore';
import TechBackground from '@/components/common/TechBackground';

const { Header, Sider, Content } = Layout;

// ==================== 菜单配置 ====================

const menuItems = [
  {
    key: '/dashboard', icon: <DashboardOutlined />, label: '仪表盘',
    badge: null,
  },
  {
    key: '/orders', icon: <ShoppingCartOutlined />, label: '订单管理',
    badge: null,
  },
  {
    key: '/inventory', icon: <InboxOutlined />, label: '库存管理',
    badge: null,
  },
  {
    key: '/scheduling', icon: <ScheduleOutlined />, label: '调度中心',
    badge: null,
  },
  {
    key: '/fulfillment', icon: <CarOutlined />, label: '履约管理',
    badge: null,
  },
  {
    key: '/suppliers', icon: <TeamOutlined />, label: '供应商管理',
    badge: null,
  },
  {
    key: '/reports', icon: <BarChartOutlined />, label: '数据报表',
    badge: null,
  },
  {
    key: '/ai', icon: <RobotOutlined />, label: 'AI 智能服务',
    badge: <Tag color="cyan" style={{ fontSize: 10, lineHeight: '16px', marginLeft: 6 }}>AI</Tag>,
    children: [
      { key: '/ai-dashboard', icon: <ThunderboltOutlined />, label: 'AI 智能看板' },
      { key: '/ai-workflow', icon: <ExperimentOutlined />, label: 'Agent 工作流编排' },
      { key: '/knowledge', icon: <BookOutlined />, label: 'RAG 知识库' },
    ],
  },
  {
    key: '/system', icon: <SettingOutlined />, label: '系统管理',
    badge: null,
    children: [
      { key: '/system/users', icon: <UserOutlined />, label: '用户管理' },
    ],
  },
];

// ==================== 侧边栏 Logo ====================

function SideLogo({ collapsed }) {
  return (
    <div style={{
      height: 72, display: 'flex', alignItems: 'center',
      justifyContent: collapsed ? 'center' : 'flex-start',
      padding: collapsed ? 0 : '0 22px',
      borderBottom: '1px solid rgba(255,255,255,0.06)',
      gap: 10,
    }}>
      <motion.div
        whileHover={{ scale: 1.08, rotate: 5 }}
        style={{
          width: 40, height: 40, borderRadius: 12,
          background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #a855f7 100%)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          boxShadow: '0 0 20px rgba(99,102,241,0.45)',
          fontSize: 18, flexShrink: 0,
        }}
      >
        <ApiOutlined style={{ color: '#fff' }} />
      </motion.div>
      <AnimatePresence>
        {!collapsed && (
          <motion.div
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -10 }}
            transition={{ duration: 0.2 }}
          >
            <div style={{ color: '#e2e8f0', fontSize: 19, fontWeight: 800, letterSpacing: 2, lineHeight: 1.2 }}>
              XUNI
            </div>
            <div style={{ color: 'rgba(148,163,184,0.7)', fontSize: 10, letterSpacing: 1 }}>
              智能调度平台
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

// ==================== 主组件 ====================

export default function GlassLayout() {
  const [collapsed, setCollapsed] = useState(false);
  const [profileOpen, setProfileOpen] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const { userInfo, logout } = useAuthStore();

  const selectedKeys = (() => {
    const p = location.pathname;
    if (p === '/ai-dashboard') return ['/ai-dashboard'];
    if (p === '/ai-workflow') return ['/ai-workflow'];
    if (p === '/knowledge') return ['/knowledge'];
    if (p === '/system/users') return ['/system/users'];
    return [p];
  })();

  const defaultOpenKeys = (() => {
    const p = location.pathname;
    const keys = [];
    if (p.startsWith('/ai')) keys.push('/ai');
    if (p.startsWith('/system')) keys.push('/system');
    return keys;
  })();

  const displayName = userInfo?.realName || userInfo?.username || '管理员';
  const displayRole = userInfo?.role || 'ADMIN';
  const roleMap = { ADMIN: '系统管理员', MANAGER: '部门经理', OPERATOR: '操作员', USER: '普通用户' };
  const roleLabel = roleMap[displayRole] || displayRole;
  const avatarLetter = displayName[0] || '管';

  const handleUserMenu = ({ key }) => {
    if (key === 'profile') setProfileOpen(true);
    else if (key === 'logout') logout();
  };

  const userMenuItems = useMemo(() => [
    { key: 'profile', icon: <UserOutlined />, label: '个人中心' },
    { type: 'divider' },
    { key: 'logout', icon: <LogoutOutlined />, label: '退出登录', danger: true },
  ], []);

  // 当前页标题
  const findLabel = (items, key) => {
    for (const item of items) {
      if (item.key === key) return item.label;
      if (item.children) {
        const found = findLabel(item.children, key);
        if (found) return found;
      }
    }
    return null;
  };
  const currentLabel = findLabel(menuItems, selectedKeys[0]) || '';

  return (
    <Layout style={{ minHeight: '100vh', background: '#0a0e27' }}>
      {/* ========== 侧边栏 ========== */}
      <Sider
        collapsible collapsed={collapsed} onCollapse={setCollapsed}
        width={252} collapsedWidth={72} trigger={null}
        style={{
          position: 'fixed', left: 0, top: 0, bottom: 0, zIndex: 100,
          background: 'linear-gradient(180deg, #0f1235 0%, #131740 50%, #0f1235 100%)',
          borderRight: '1px solid rgba(99,102,241,0.12)',
          boxShadow: '8px 0 40px rgba(0,0,0,0.35)',
          overflow: 'hidden',
        }}
      >
        <SideLogo collapsed={collapsed} />

        {/* 发光分割线 */}
        <div style={{
          height: 1, margin: '0 16px',
          background: 'linear-gradient(90deg, transparent, rgba(99,102,241,0.4), transparent)',
        }} />

        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={selectedKeys}
          defaultOpenKeys={defaultOpenKeys}
          onClick={({ key }) => navigate(key)}
          items={menuItems}
          inlineCollapsed={collapsed}
          style={{
            background: 'transparent', borderRight: 0,
            marginTop: 12, padding: '0 8px',
            fontWeight: 500,
          }}
        />

        {/* 底部信息 */}
        <div style={{
          position: 'absolute', bottom: 72, left: 0, right: 0,
          padding: collapsed ? '0 8px' : '0 20px',
        }}>
          {!collapsed && (
            <div style={{
              padding: '12px 16px', borderRadius: 12,
              background: 'linear-gradient(135deg, rgba(99,102,241,0.12), rgba(139,92,246,0.08))',
              border: '1px solid rgba(99,102,241,0.15)',
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6 }}>
                <SafetyOutlined style={{ color: '#818cf8', fontSize: 13 }} />
                <span style={{ color: '#94a3b8', fontSize: 11 }}>系统状态</span>
                <Tag color="green" style={{ fontSize: 10, lineHeight: '14px', margin: 0 }}>运行中</Tag>
              </div>
              <div style={{ fontSize: 10, color: '#64748b' }}>
                PostgreSQL · Redis · Qdrant
              </div>
            </div>
          )}
        </div>

        {/* 折叠按钮 */}
        <motion.div
          whileHover={{ scale: 1.05, backgroundColor: 'rgba(99,102,241,0.25)' }}
          onClick={() => setCollapsed(!collapsed)}
          style={{
            position: 'absolute', bottom: 16, left: '50%', transform: 'translateX(-50%)',
            width: collapsed ? 40 : 'calc(100% - 32px)', height: 40, borderRadius: 10,
            background: 'rgba(255,255,255,0.06)', backdropFilter: 'blur(10px)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            cursor: 'pointer', transition: 'all 0.3s ease',
            color: '#94a3b8', fontSize: 15, border: '1px solid rgba(255,255,255,0.06)',
          }}
        >
          {collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
        </motion.div>
      </Sider>

      {/* ========== 主区域 ========== */}
      <Layout style={{
        marginLeft: collapsed ? 72 : 252,
        transition: 'margin-left 0.3s cubic-bezier(0.4,0,0.2,1)',
        background: 'transparent',
        position: 'relative',
        minHeight: '100vh',
      }}>
        {/* 粒子背景 */}
        <div style={{ position: 'fixed', inset: 0, zIndex: 0, pointerEvents: 'none' }}>
          <TechBackground particleColor="99,102,241" count={50} />
        </div>

        {/* 顶部导航 */}
        <Header style={{
          position: 'sticky', top: 0, zIndex: 99, padding: '0 28px',
          background: 'rgba(15,18,53,0.88)', backdropFilter: 'blur(24px)',
          borderBottom: '1px solid rgba(99,102,241,0.12)',
          boxShadow: '0 4px 30px rgba(0,0,0,0.25)',
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
          height: 64,
        }}>
          {/* 左侧 breadcrumb */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <div style={{
              width: 4, height: 20, borderRadius: 2,
              background: 'linear-gradient(180deg, #6366f1, #a855f7)',
            }} />
            <span style={{ color: '#64748b', fontSize: 13 }}>Xuni</span>
            {currentLabel && (
              <>
                <span style={{ color: 'rgba(100,116,139,0.4)' }}>/</span>
                <span style={{ color: '#e2e8f0', fontSize: 14, fontWeight: 600 }}>
                  {currentLabel}
                </span>
              </>
            )}
          </div>

          {/* 右侧操作区 */}
          <Space size={24}>
            <Tooltip title="通知中心">
              <motion.div whileHover={{ scale: 1.1 }} whileTap={{ scale: 0.95 }}>
                <Badge count={0} size="small" overflowCount={99}>
                  <BellOutlined
                    style={{ fontSize: 18, color: '#94a3b8', cursor: 'pointer' }}
                    onClick={() => message.info('暂无新通知')}
                  />
                </Badge>
              </motion.div>
            </Tooltip>

            <Dropdown menu={{ items: userMenuItems, onClick: handleUserMenu }} placement="bottomRight">
              <Space style={{ cursor: 'pointer' }}>
                <motion.div whileHover={{ scale: 1.05 }}>
                  <Avatar
                    size={36}
                    style={{
                      background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
                      boxShadow: '0 0 12px rgba(99,102,241,0.4)',
                    }}
                  >
                    {avatarLetter}
                  </Avatar>
                </motion.div>
                <div style={{ lineHeight: 1.3 }}>
                  <div style={{ fontSize: 14, fontWeight: 600, color: '#e2e8f0' }}>
                    {displayName}
                  </div>
                  <div style={{ fontSize: 11, color: '#64748b' }}>{roleLabel}</div>
                </div>
              </Space>
            </Dropdown>
          </Space>
        </Header>

        {/* 内容区 */}
        <Content style={{
          padding: 24,
          minHeight: 'calc(100vh - 64px - 52px)',
          position: 'relative', zIndex: 1,
        }}>
          <motion.div
            key={location.pathname}
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.25, ease: 'easeOut' }}
            style={{
              background: 'rgba(15,18,53,0.72)',
              backdropFilter: 'blur(20px)',
              borderRadius: 20,
              border: '1px solid rgba(99,102,241,0.1)',
              boxShadow: '0 8px 40px rgba(0,0,0,0.3)',
              padding: 24,
              minHeight: 'calc(100vh - 64px - 120px)',
            }}
          >
            <Outlet />
          </motion.div>
        </Content>

        {/* 底部 */}
        <div style={{
          textAlign: 'center', padding: '14px 24px',
          color: '#475569', fontSize: 11,
          borderTop: '1px solid rgba(99,102,241,0.08)',
          position: 'relative', zIndex: 1,
        }}>
          <Space size={12}>
            <Tag color="purple" style={{
              background: 'rgba(139,92,246,0.15)',
              border: '1px solid rgba(139,92,246,0.25)',
              color: '#a78bfa',
            }}>v3.0</Tag>
            <span style={{ color: '#475569' }}>Xuni Scheduling Platform © 2026</span>
            <span style={{ color: 'rgba(71,85,105,0.3)' }}>|</span>
            <span style={{ color: '#475569' }}>企业级智能调度 · 三层记忆 AI Agent</span>
          </Space>
        </div>
      </Layout>

      {/* ========== 个人中心弹窗 ========== */}
      <Modal
        title={<span style={{ color: '#e2e8f0' }}>个人中心</span>}
        open={profileOpen}
        onCancel={() => setProfileOpen(false)}
        footer={null}
        width={480}
        styles={{
          content: {
            background: '#131740',
            borderRadius: 16,
            border: '1px solid rgba(99,102,241,0.2)',
          },
          header: { background: 'transparent', borderBottom: '1px solid rgba(99,102,241,0.1)' },
          body: { background: 'transparent' },
        }}
      >
        <Descriptions column={1} bordered size="small" style={{ marginTop: 16 }}>
          <Descriptions.Item label={<span style={{ color: '#94a3b8' }}>用户名</span>}>
            <span style={{ color: '#e2e8f0' }}>{displayName}</span>
          </Descriptions.Item>
          <Descriptions.Item label={<span style={{ color: '#94a3b8' }}>角色</span>}>
            <Tag color="blue">{roleLabel}</Tag>
          </Descriptions.Item>
          <Descriptions.Item label={<span style={{ color: '#94a3b8' }}>邮箱</span>}>
            <span style={{ color: '#e2e8f0' }}>{userInfo?.email || '-'}</span>
          </Descriptions.Item>
          <Descriptions.Item label={<span style={{ color: '#94a3b8' }}>手机号</span>}>
            <span style={{ color: '#e2e8f0' }}>{userInfo?.phone || '-'}</span>
          </Descriptions.Item>
        </Descriptions>
        <div style={{ marginTop: 20, textAlign: 'right' }}>
          <Space>
            <Button onClick={() => setProfileOpen(false)}>关闭</Button>
            <Button type="primary" danger onClick={() => { setProfileOpen(false); logout(); }}>
              <LogoutOutlined /> 退出登录
            </Button>
          </Space>
        </div>
      </Modal>
    </Layout>
  );
}
