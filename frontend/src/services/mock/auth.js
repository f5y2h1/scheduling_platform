export const mockAuthData = {
  login: ({ username, password }) => {
    if (username === 'admin' && password === 'admin123') {
      return {
        accessToken: 'mock_token_' + Date.now(),
        refreshToken: 'mock_refresh_' + Date.now(),
        userInfo: {
          id: 1,
          username: 'admin',
          realName: '管理员',
          role: 'ADMIN',
          department: '技术部',
        },
      };
    }
    return { error: '用户名或密码错误' };
  },
  register: ({ username, password, realName }) => ({
    success: true,
    message: '注册成功',
    userId: Date.now(),
  }),
  refresh: () => ({
    accessToken: 'mock_token_' + Date.now(),
    refreshToken: 'mock_refresh_' + Date.now(),
  }),
};