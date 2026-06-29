const r = () => Math.random();

export const mockSupplierData = {
  list: (params = {}) => {
    const page = params.page || 1;
    const size = params.size || 20;
    const records = [];
    const statuses = ['ACTIVE', 'INACTIVE', 'SUSPENDED'];
    const industries = ['电子产品', '食品饮料', '服装鞋帽', '日用品', '原材料'];
    for (let i = 0; i < size; i++) {
      const id = (page - 1) * size + i + 1;
      records.push({
        id,
        supplierCode: `SUP${id.toString().padStart(6, '0')}`,
        name: `供应商${['A', 'B', 'C', 'D'][Math.floor(r() * 4)]}-${id}`,
        contactName: ['张经理', '李总', '王老板', '赵先生'][Math.floor(r() * 4)],
        contactPhone: `139${Math.floor(100000000 + r() * 900000000)}`,
        industry: industries[Math.floor(r() * industries.length)],
        rating: +(3 + r() * 2).toFixed(1),
        status: statuses[Math.floor(r() * statuses.length)],
        createdAt: new Date(Date.now() - r() * 90 * 24 * 60 * 60 * 1000).toISOString(),
      });
    }
    return { records, total: 60, page, size, totalPages: 3 };
  },
};