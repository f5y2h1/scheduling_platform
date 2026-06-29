import axios from 'axios';
import { message } from 'antd';

// Mock 数据已禁用 - 所有请求将直接发送到后端

const toCamel = (s) => s.replace(/_([a-z])/g, (_, c) => c.toUpperCase());

const camelize = (obj) => {
  if (obj === null || obj === undefined) return obj;
  if (Array.isArray(obj)) return obj.map(camelize);
  if (typeof obj === 'object' && obj.constructor === Object) {
    const out = {};
    for (const [k, v] of Object.entries(obj)) {
      out[toCamel(k)] = camelize(v);
    }
    return out;
  }
  return obj;
};

const isNetworkError = (error) => {
  if (!error.response && (error.message === 'Network Error' || error.code === 'ERR_NETWORK' || error.code === 'ECONNREFUSED')) {
    return true;
  }
  if (error.response && (error.response.status === 502 || error.response.status === 504)) {
    return true;
  }
  if (error.response && typeof error.response.data === 'string' && error.response.data.startsWith('<')) {
    return true;
  }
  return false;
};

const axiosInstance = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
});

axiosInstance.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('accessToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

axiosInstance.interceptors.response.use(
  (response) => {
    if (response.status === 502 || response.status === 504) {
      return Promise.reject({
        response: response,
        isProxyError: true,
      });
    }
    const data = response.data;
    if (data && typeof data === 'object') {
      if ('code' in data) {
        const { code, message: msg, data: result } = data;
        if (code === 200 || code === 0) {
          return camelize(result);
        }
        if (code !== 502 && code !== 504) {
          message.error(msg || '请求失败');
        }
        return Promise.reject(new Error(msg));
      }
      return camelize(data);
    }
    return data;
  },
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('accessToken');
      localStorage.removeItem('refreshToken');
      localStorage.removeItem('userInfo');
      window.location.href = '/login';
    }
    const msg = error.response?.data?.message || error.message || '网络错误';
    if (isNetworkError(error)) {
      message.error('后端服务未启动，请确保后端服务正在运行 (http://localhost:8080)');
    } else if (error.response && error.response.status !== 404) {
      message.error(msg);
    }
    return Promise.reject(error);
  }
);

const smartRequest = {
  get: async (url, config = {}) => {
    return axiosInstance.get(url, config);
  },
  post: async (url, data = {}, config = {}) => {
    if (config.responseType === 'stream') {
      const token = localStorage.getItem('accessToken');
      const headers = {
        'Content-Type': 'application/json',
        ...config.headers,
      };
      if (token) {
        headers.Authorization = `Bearer ${token}`;
      }
      return fetch('/api' + url, {
        method: 'POST',
        headers: headers,
        body: typeof data === 'string' ? data : JSON.stringify(data),
      });
    }
    return axiosInstance.post(url, data, config);
  },
  put: async (url, data = {}, config = {}) => {
    return axiosInstance.put(url, data, config);
  },
  delete: async (url, config = {}) => {
    return axiosInstance.delete(url, config);
  },
  checkBackend: async () => {
    try {
      await axiosInstance.get('/health');
      return true;
    } catch {
      message.error('后端服务未启动，请确保后端服务正在运行 (http://localhost:8080)');
      return false;
    }
  },
};

export default smartRequest;