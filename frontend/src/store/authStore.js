import { create } from 'zustand';
import { authAPI } from '@/services/api';
import { message } from 'antd';

export const useAuthStore = create((set, get) => ({
  token: localStorage.getItem('accessToken') || null,
  refreshToken: localStorage.getItem('refreshToken') || null,
  userInfo: JSON.parse(localStorage.getItem('userInfo') || 'null'),

  isLoggedIn: () => !!get().token,

  login: async (username, password) => {
    try {
      const res = await authAPI.login({ username, password });
      // 拦截器已将 snake_case 转为 camelCase
      const { accessToken, refreshToken, user } = res;
      localStorage.setItem('accessToken', accessToken);
      localStorage.setItem('refreshToken', refreshToken);
      localStorage.setItem('userInfo', JSON.stringify(user));
      set({ token: accessToken, refreshToken, userInfo: user });
      message.success(`欢迎回来，${user.realName || user.username}！`);
      return true;
    } catch (e) {
      return false;
    }
  },

  logout: async () => {
    try {
      await authAPI.logout();
    } catch (e) { /* ignore */ }
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('userInfo');
    set({ token: null, refreshToken: null, userInfo: null });
    window.location.href = '/login';
  },

  refreshTokenFn: async () => {
    const rt = get().refreshToken;
    if (!rt) return false;
    try {
      const res = await authAPI.refresh(rt);
      const { accessToken, refreshToken } = res;
      localStorage.setItem('accessToken', accessToken);
      localStorage.setItem('refreshToken', refreshToken);
      set({ token: accessToken, refreshToken });
      return true;
    } catch {
      get().logout();
      return false;
    }
  },
}));
