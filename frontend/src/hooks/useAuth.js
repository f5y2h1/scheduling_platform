import { useState, useEffect, useCallback } from 'react';
import { authAPI } from '@/services/api';

export function useAuth() {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const storedToken = localStorage.getItem('accessToken');
    const storedUser = localStorage.getItem('userInfo');
    if (storedToken) {
      setToken(storedToken);
    }
    if (storedUser) {
      try {
        setUser(JSON.parse(storedUser));
      } catch (e) {
        localStorage.removeItem('userInfo');
      }
    }
    setLoading(false);
  }, []);

  const login = useCallback(async (data) => {
    const result = await authAPI.login(data);
    const { accessToken, refreshToken, user: userInfo } = result;
    localStorage.setItem('accessToken', accessToken);
    localStorage.setItem('refreshToken', refreshToken);
    localStorage.setItem('userInfo', JSON.stringify(userInfo));
    setToken(accessToken);
    setUser(userInfo);
    return result;
  }, []);

  const logout = useCallback(async () => {
    try {
      await authAPI.logout();
    } catch (e) {
      console.error('Logout failed:', e);
    }
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('userInfo');
    setToken(null);
    setUser(null);
  }, []);

  const register = useCallback(async (data) => {
    const result = await authAPI.register(data);
    return result;
  }, []);

  return {
    user,
    token,
    loading,
    login,
    logout,
    register,
    isAuthenticated: !!token,
  };
}