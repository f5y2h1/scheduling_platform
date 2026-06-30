import { Card, Space } from 'antd';
import { ArrowUpOutlined, ArrowDownOutlined } from '@ant-design/icons';
import { motion } from 'framer-motion';
import AnimatedCounter from './AnimatedCounter';

/**
 * StatCard — animated metric card with glow hover effect
 */
export default function StatCard({
  title, value = 0, suffix, prefix,
  trend, trendType = 'up', icon, color = '#6366f1',
  delay = 0,
}) {
  const TrendIcon = trendType === 'up' ? ArrowUpOutlined : ArrowDownOutlined;
  const trendColor = trendType === 'up' ? '#34d399' : '#f87171';

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay, ease: 'easeOut' }}
      whileHover={{ y: -3, transition: { duration: 0.15 } }}
    >
      <Card
        hoverable
        style={{
          borderRadius: 16,
          background: 'rgba(15,18,53,0.7)',
          backdropFilter: 'blur(12px)',
          border: `1px solid ${color}20`,
          boxShadow: '0 4px 20px rgba(0,0,0,0.2)',
          transition: 'all 0.25s ease',
          overflow: 'hidden',
          position: 'relative',
        }}
        styles={{ body: { padding: '22px 20px' } }}
        onMouseEnter={(e) => {
          e.currentTarget.style.borderColor = `${color}50`;
          e.currentTarget.style.boxShadow = `0 0 28px ${color}20, 0 8px 32px rgba(0,0,0,0.3)`;
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.borderColor = `${color}20`;
          e.currentTarget.style.boxShadow = '0 4px 20px rgba(0,0,0,0.2)';
        }}
      >
        {/* 顶部发光条 */}
        <div style={{
          position: 'absolute', top: 0, left: 0, right: 0,
          height: 2, background: `linear-gradient(90deg, ${color}60, ${color}10)`,
        }} />

        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          <span style={{ color: '#94a3b8', fontSize: 12, fontWeight: 500, letterSpacing: 0.5 }}>
            {title}
          </span>
          <Space align="center" style={{ width: '100%', justifyContent: 'space-between' }}>
            <div>
              <div style={{ fontSize: 28, fontWeight: 800, color: '#e2e8f0', lineHeight: 1.1 }}>
                {prefix}
                <AnimatedCounter value={value} duration={1.5} />
                {suffix && (
                  <span style={{ fontSize: 14, color: '#94a3b8', marginLeft: 3, fontWeight: 500 }}>
                    {suffix}
                  </span>
                )}
              </div>
              {trend !== undefined && (
                <Space size={4} style={{ marginTop: 6 }}>
                  <TrendIcon style={{ color: trendColor, fontSize: 12 }} />
                  <span style={{ color: trendColor, fontSize: 12, fontWeight: 600 }}>
                    {trend}
                  </span>
                </Space>
              )}
            </div>
            {icon && (
              <motion.div
                whileHover={{ rotate: 8, scale: 1.08 }}
                style={{
                  width: 52, height: 52, borderRadius: 14,
                  background: `${color}15`,
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  fontSize: 22, color,
                  border: `1px solid ${color}25`,
                }}
              >
                {icon}
              </motion.div>
            )}
          </Space>
        </Space>
      </Card>
    </motion.div>
  );
}
