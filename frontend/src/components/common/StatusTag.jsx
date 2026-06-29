import { Tag } from 'antd';

const statusMap = {
  pending: { label: '待处理', color: 'default' },
  processing: { label: '处理中', color: 'processing' },
  shipped: { label: '已发货', color: 'blue' },
  delivered: { label: '已送达', color: 'success' },
  cancelled: { label: '已取消', color: 'error' },
  in_transit: { label: '运输中', color: 'processing' },
  signed: { label: '已签收', color: 'success' },
  active: { label: '正常', color: 'success' },
  inactive: { label: '禁用', color: 'error' },
  normal: { label: '正常', color: 'success' },
  warning: { label: '预警', color: 'warning' },
  high_risk: { label: '高风险', color: 'error' },
  approved: { label: '已审批', color: 'success' },
  rejected: { label: '已拒绝', color: 'error' },
};

export default function StatusTag({ status, customMap }) {
  const map = customMap || statusMap;
  const config = map[status?.toLowerCase()] || { label: status, color: 'default' };

  return (
    <Tag color={config.color} style={{ borderRadius: 4, fontSize: 12 }}>
      {config.label}
    </Tag>
  );
}