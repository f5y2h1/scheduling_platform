const r = () => Math.random();

export const mockInventoryData = {
  list: (params = {}) => {
    const page = params.page || 1;
    const size = params.size || 20;
    const records = [];
    const statuses = ['NORMAL', 'LOW', 'OUT_OF_STOCK'];
    const warehouses = ['北京仓', '上海仓', '广州仓', '成都仓'];
    for (let i = 0; i < size; i++) {
      const id = (page - 1) * size + i + 1;
      const stock = Math.floor(r() * 500);
      records.push({
        id,
        sku: `SKU${id.toString().padStart(6, '0')}`,
        productName: `商品${['A', 'B', 'C', 'D'][Math.floor(r() * 4)]}-${id}`,
        category: ['电子产品', '食品饮料', '服装鞋帽', '日用品'][Math.floor(r() * 4)],
        warehouse: warehouses[Math.floor(r() * warehouses.length)],
        quantity: stock,
        minStock: 50,
        maxStock: 300,
        status: stock === 0 ? 'OUT_OF_STOCK' : stock < 50 ? 'LOW' : 'NORMAL',
        unit: '件',
        lastUpdated: new Date(Date.now() - r() * 7 * 24 * 60 * 60 * 1000).toISOString(),
      });
    }
    return { records, total: 156, page, size, totalPages: 8 };
  },
  alerts: () => ({
    lowStock: [
      { id: 1, sku: 'SKU001001', productName: '商品A-1001', warehouse: '北京仓', quantity: 25, minStock: 50 },
      { id: 2, sku: 'SKU001023', productName: '商品B-1023', warehouse: '上海仓', quantity: 18, minStock: 50 },
    ],
    outOfStock: [
      { id: 3, sku: 'SKU001056', productName: '商品C-1056', warehouse: '广州仓', quantity: 0, minStock: 50 },
    ],
  }),
  stats: () => ({ totalSkus: 1568, lowStockCount: 12, outOfStockCount: 3, turnoverRate: 9.2 }),
};