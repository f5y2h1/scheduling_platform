import request from '../smartRequest';

export const authAPI = {
  login: (data) => request.post('/auth/login', data),
  register: (data) => request.post('/auth/register', data),
  refresh: (refreshToken) => request.post('/auth/refresh', { refresh_token: refreshToken }),
  logout: () => request.post('/auth/logout'),
};