const r = () => Math.random();

export const mockFulfillmentData = {
  list: (params = {}) => {
    const page = params.page || 1;
    const size = params.size || 20;
    const records = [];
    const statuses = ['PENDING', 'PICKING', 'PACKED', 'SHIPPED', 'IN_TRANSIT', 'DELIVERED', 'SIGNED'];
    const carriers = ['顺丰速运', '中通快递', '圆通速递', '京东物流', 'EMS'];
    const types = ['B2C', 'B2B', 'RETURN'];
    for (let i = 0; i < size; i++) {
      const id = (page - 1) * size + i + 1;
      records.push({
        id,
        fulfillmentNo: `FUL${Date.now().toString().slice(-6)}${id.toString().padStart(4, '0')}`,
        orderNo: `ORD${Date.now().toString().slice(-6)}${(id + 100).toString().padStart(4, '0')}`,
        type: types[Math.floor(r() * types.length)],
        status: statuses[Math.floor(r() * statuses.length)],
        carrierName: carriers[Math.floor(r() * carriers.length)],
        trackingNumber: `${['SF', 'ZT', 'YT', 'JD', 'EMS'][Math.floor(r() * 5)]}${Math.floor(1000000000000 + r() * 9000000000000)}`,
        estimatedDelivery: new Date(Date.now() + r() * 3 * 24 * 60 * 60 * 1000).toISOString(),
        actualDelivery: Math.random() > 0.5 ? new Date(Date.now() - r() * 2 * 24 * 60 * 60 * 1000).toISOString() : null,
        createdAt: new Date(Date.now() - r() * 5 * 24 * 60 * 60 * 1000).toISOString(),
      });
    }
    return { records, total: 120, page, size, totalPages: 6 };
  },
  getById: (id) => ({
    id,
    fulfillmentNo: `FUL${Date.now().toString().slice(-6)}${id.toString().padStart(4, '0')}`,
    orderNo: `ORD${Date.now().toString().slice(-6)}${(id + 100).toString().padStart(4, '0')}`,
    status: 'IN_TRANSIT',
    carrier: '顺丰',
    trackingNo: 'SF1234567890123',
    estimatedDelivery: new Date(Date.now() + r() * 2 * 24 * 60 * 60 * 1000).toISOString(),
    actualDelivery: null,
    origin: '北京市朝阳区',
    destination: '上海市浦东新区',
    items: [
      { name: '产品A', sku: 'SKU001', quantity: 2 },
      { name: '产品B', sku: 'SKU002', quantity: 1 },
    ],
    trackingHistory: [
      { time: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(), status: '已揽收', location: '北京市朝阳区网点' },
      { time: new Date(Date.now() - 12 * 60 * 60 * 1000).toISOString(), status: '运输中', location: '北京转运中心' },
      { time: new Date(Date.now() - 6 * 60 * 60 * 1000).toISOString(), status: '运输中', location: '济南转运中心' },
    ],
    createdAt: new Date(Date.now() - r() * 2 * 24 * 60 * 60 * 1000).toISOString(),
  }),
  stats: () => ({ totalToday: 85, inTransit: 42, delivered: 38, failed: 5, avgDeliveryHours: 28.5 }),
};