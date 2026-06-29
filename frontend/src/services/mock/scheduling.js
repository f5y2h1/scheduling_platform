const r = () => Math.random();

export const mockSchedulingData = {
  list: (params = {}) => {
    const page = params.page || 1;
    const size = params.size || 20;
    const records = [];
    const statuses = ['PENDING', 'AI_SUGGESTED', 'APPROVED', 'EXECUTING', 'COMPLETED', 'REJECTED'];
    const types = ['DISPATCH', 'REPLENISHMENT', 'TRANSFER'];
    const warehouses = ['北京仓', '上海仓', '广州仓', '成都仓', '武汉仓', '西安仓'];
    for (let i = 0; i < size; i++) {
      const id = (page - 1) * size + i + 1;
      const status = statuses[Math.floor(r() * statuses.length)];
      records.push({
        id,
        taskNo: `SCH${Date.now().toString().slice(-6)}${id.toString().padStart(4, '0')}`,
        orderNo: `ORD${Date.now().toString().slice(-6)}${(id + 100).toString().padStart(4, '0')}`,
        productName: `商品${['A', 'B', 'C', 'D'][Math.floor(r() * 4)]}-${id}`,
        taskType: types[Math.floor(r() * types.length)],
        status: status,
        quantity: Math.floor(100 + r() * 900),
        fromWarehouseName: warehouses[Math.floor(r() * warehouses.length)],
        toWarehouseName: warehouses[Math.floor(r() * warehouses.length)],
        aiModelUsed: status === 'AI_SUGGESTED' || status === 'APPROVED' ? 'qwen-plus' : null,
        createdAt: new Date(Date.now() - r() * 7 * 24 * 60 * 60 * 1000).toISOString(),
      });
    }
    return { records, total: 80, page, size, totalPages: 4 };
  },
  getById: (id) => ({
    id,
    taskNo: `SCH${Date.now().toString().slice(-6)}${id.toString().padStart(4, '0')}`,
    orderNo: `ORD${Date.now().toString().slice(-6)}${(id + 100).toString().padStart(4, '0')}`,
    productName: '商品A-' + id,
    taskType: 'DISPATCH',
    status: 'PENDING',
    quantity: 500,
    fromWarehouseName: '北京仓',
    toWarehouseName: '上海仓',
    aiModelUsed: null,
    aiSuggestion: '基于AI分析，建议采用路线B，预计节省成本15%，运输时间缩短20%。同时建议增加备选仓库方案以应对潜在风险。',
    createdAt: new Date(Date.now() - r() * 3 * 24 * 60 * 60 * 1000).toISOString(),
  }),
};