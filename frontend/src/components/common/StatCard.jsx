import { Card, Typography, Space } from 'antd';
import { ArrowUpOutlined, ArrowDownOutlined } from '@ant-design/icons';

const { Title, Text } = Typography;

export default function StatCard({ title, value, unit, trend, trendType = 'up', icon, color = '#4f46e5' }) {
  const TrendIcon = trendType === 'up' ? ArrowUpOutlined : ArrowDownOutlined;
  const trendColor = trendType === 'up' ? '#10b981' : '#ef4444';

  return (
    <Card
      hoverable
      style={{ borderRadius: 12, boxShadow: '0 2px 8px rgba(0,0,0,0.06)' }}
    >
      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        <Text type="secondary">{title}</Text>
        <Space align="center" style={{ width: '100%', justifyContent: 'space-between' }}>
          <div>
            <Title level={3} style={{ margin: 0, color: '#1a2b3c' }}>
              {value}
              {unit && <Text type="secondary" style={{ fontSize: 16, marginLeft: 4 }}>{unit}</Text>}
            </Title>
            {trend !== undefined && (
              <Space align="center" style={{ marginTop: 4 }}>
                <TrendIcon style={{ color: trendColor, fontSize: 14 }} />
                <Text style={{ color: trendColor, fontSize: 13 }}>{trend}</Text>
              </Space>
            )}
          </div>
          {icon && (
            <div
              style={{
                width: 56,
                height: 56,
                borderRadius: 12,
                backgroundColor: `${color}15`,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              {icon}
            </div>
          )}
        </Space>
      </Space>
    </Card>
  );
}