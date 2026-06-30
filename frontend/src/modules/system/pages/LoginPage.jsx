import React, { useState } from 'react';
import { Form, Input, Button, Card, Typography, message } from 'antd';
import { UserOutlined, LockOutlined, ThunderboltOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useAuthStore } from '@/store/authStore';
import TechBackground from '@/components/common/TechBackground';

const { Title, Text } = Typography;

export default function LoginPage() {
  const [loading, setLoading] = useState(false);
  const login = useAuthStore((s) => s.login);
  const navigate = useNavigate();

  const onFinish = async (values) => {
    setLoading(true);
    const success = await login(values.username, values.password);
    setLoading(false);
    if (success) navigate('/dashboard', { replace: true });
  };

  return (
    <div style={{
      minHeight: '100vh', display: 'flex',
      alignItems: 'center', justifyContent: 'center',
      background: 'linear-gradient(135deg, #0a0e27 0%, #131740 40%, #0f1235 100%)',
      padding: 20, position: 'relative', overflow: 'hidden',
    }}>
      <TechBackground particleColor="99,102,241" count={80} />

      <motion.div
        initial={{ opacity: 0, y: 30, scale: 0.97 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        transition={{ duration: 0.6, ease: 'easeOut' }}
      >
        <Card
          style={{
            width: 420, borderRadius: 20,
            background: 'rgba(15,18,53,0.75)',
            backdropFilter: 'blur(24px)',
            border: '1px solid rgba(99,102,241,0.15)',
            boxShadow: '0 20px 80px rgba(0,0,0,0.5), 0 0 60px rgba(99,102,241,0.08)',
            position: 'relative', zIndex: 1, overflow: 'hidden',
          }}
          styles={{ body: { padding: '44px 40px' } }}
        >
          {/* 发光顶线 */}
          <div style={{
            position: 'absolute', top: 0, left: 0, right: 0,
            height: 2,
            background: 'linear-gradient(90deg, #6366f1, #a855f7, #6366f1)',
          }} />

          <div style={{ textAlign: 'center', marginBottom: 40 }}>
            <motion.div
              whileHover={{ scale: 1.06, rotate: 5 }}
              style={{
                width: 64, height: 64, borderRadius: 18,
                background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #a855f7 100%)',
                display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
                boxShadow: '0 0 32px rgba(99,102,241,0.45)',
                marginBottom: 18, fontSize: 28,
              }}
            >
              <ThunderboltOutlined style={{ color: '#fff' }} />
            </motion.div>
            <Title level={2} style={{ margin: 0, color: '#e2e8f0', fontWeight: 800, letterSpacing: 1 }}>
              XUNI
            </Title>
            <Text style={{ color: '#64748b', fontSize: 13, letterSpacing: 0.5 }}>
              企业级供应链智能调度平台
            </Text>
          </div>

          <Form onFinish={onFinish} size="large" autoComplete="off">
            <Form.Item name="username" rules={[{ required: true, message: '请输入用户名' }]}>
              <Input
                prefix={<UserOutlined style={{ color: '#6366f1' }} />}
                placeholder="用户名"
                style={{
                  borderRadius: 12, height: 48,
                  background: 'rgba(15,18,53,0.6)',
                  border: '1px solid rgba(99,102,241,0.2)',
                  color: '#e2e8f0',
                }}
              />
            </Form.Item>
            <Form.Item name="password" rules={[{ required: true, message: '请输入密码' }]}>
              <Input.Password
                prefix={<LockOutlined style={{ color: '#6366f1' }} />}
                placeholder="密码"
                style={{
                  borderRadius: 12, height: 48,
                  background: 'rgba(15,18,53,0.6)',
                  border: '1px solid rgba(99,102,241,0.2)',
                  color: '#e2e8f0',
                }}
              />
            </Form.Item>
            <Form.Item style={{ marginBottom: 12 }}>
              <motion.div whileHover={{ scale: 1.01 }} whileTap={{ scale: 0.98 }}>
                <Button
                  type="primary" htmlType="submit" block loading={loading}
                  style={{
                    height: 48, borderRadius: 12, fontSize: 15, fontWeight: 600,
                    background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
                    border: 'none',
                    boxShadow: '0 4px 20px rgba(99,102,241,0.4)',
                    marginTop: 8,
                  }}
                >
                  登 录
                </Button>
              </motion.div>
            </Form.Item>
          </Form>

          <div style={{ textAlign: 'center', marginTop: 16 }}>
            <Text style={{ color: '#475569', fontSize: 12 }}>
              默认账号: admin / admin123
            </Text>
          </div>
        </Card>
      </motion.div>

      {/* 底部光晕 */}
      <div style={{
        position: 'absolute', bottom: -80, left: '50%', transform: 'translateX(-50%)',
        width: 500, height: 200, borderRadius: '50%',
        background: 'radial-gradient(ellipse, rgba(99,102,241,0.12), transparent)',
        pointerEvents: 'none',
      }} />
    </div>
  );
}
