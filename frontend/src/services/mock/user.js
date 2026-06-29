const r = () => Math.random();

export const mockUserData = {
  list: (params = {}) => {
    const page = params.page || 1;
    const size = params.size || 20;
    const records = [];
    const roles = ['ADMIN', 'MANAGER', 'OPERATOR', 'USER'];
    const names = ['张三', '李四', '王五', '赵六', '钱七', '孙八', '周九', '吴十'];
    for (let i = 0; i < size; i++) {
      const id = (page - 1) * size + i + 1;
      records.push({
        id,
        username: `user${id}`,
        realName: names[Math.floor(r() * names.length)] + id,
        email: `user${id}@example.com`,
        phone: `138${Math.floor(100000000 + r() * 900000000)}`,
        role: roles[Math.floor(r() * roles.length)],
        status: Math.random() > 0.1 ? 1 : 0,
        lastLogin: new Date(Date.now() - r() * 30 * 24 * 60 * 60 * 1000).toISOString(),
        createdAt: new Date(Date.now() - r() * 90 * 24 * 60 * 60 * 1000).toISOString(),
      });
    }
    return { records, total: 80, page, size, totalPages: 4 };
  },
  getRoles: () => [
    { code: 'ADMIN', name: '系统管理员' },
    { code: 'MANAGER', name: '部门经理' },
    { code: 'OPERATOR', name: '操作员' },
    { code: 'USER', name: '普通用户' },
  ],
};