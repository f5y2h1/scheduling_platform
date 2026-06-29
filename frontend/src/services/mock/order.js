const r = () => Math.random();

export const mockOrderData = {
  list: (params = {}) => {
    const page = params.page || 1;
    const size = params.size || 20;
    const records = [];
    const statuses = ['PENDING', 'CONFIRMED', 'PROCESSING', 'SHIPPED', 'DELIVERED', 'CANCELLED'];
    const types = ['B2C', 'B2B', 'RETURN'];
    for (let i = 0; i < size; i++) {
      const id = (page - 1) * size + i + 1;
      records.push({
        id,
        orderNo: `ORD${Date.now().toString().slice(-6)}${id.toString().padStart(4, '0')}`,
        customerName: ['张三', '李四', '王五', '赵六'][Math.floor(r() * 4)],
        totalAmount: +(100 + r() * 9900).toFixed(2),
        status: statuses[Math.floor(r() * statuses.length)],
        orderType: types[Math.floor(r() * types.length)],
        createdAt: new Date(Date.now() - r() * 7 * 24 * 60 * 60 * 1000).toISOString(),
      });
    }
    return { records, total: 100, page, size, totalPages: 5 };
  },
  getById: (id) => ({
    id,
    orderNo: `ORD${Date.now().toString().slice(-6)}${id.toString().padStart(4, '0')}`,
    customerName: '张三',
    customerPhone: '138****8888',
    customerAddress: '北京市朝阳区某某街道123号',
    totalAmount: 1288.50,
    status: 'PROCESSING',
    orderType: 'B2C',
    items: [
      { name: '产品A', sku: 'SKU001', quantity: 2, price: 299.00 },
      { name: '产品B', sku: 'SKU002', quantity: 1, price: 690.50 },
    ],
    createdAt: new Date(Date.now() - r() * 3 * 24 * 60 * 60 * 1000).toISOString(),
  }),
  stats: () => ({ totalToday: 128, pendingCount: 25, completedRate: 93.2, trend: '+8.5%' }),
};