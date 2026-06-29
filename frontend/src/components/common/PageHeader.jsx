import { Typography, Button, Space, Breadcrumb } from 'antd';

const { Title } = Typography;

export default function PageHeader({ title, breadcrumb = [], extra }) {
  return (
    <div style={{ marginBottom: 24 }}>
      <Breadcrumb items={breadcrumb} style={{ marginBottom: 16 }} />
      <Space justify="space-between" style={{ width: '100%' }}>
        <Title level={3} style={{ margin: 0, color: '#1a2b3c' }}>
          {title}
        </Title>
        {extra}
      </Space>
    </div>
  );
}