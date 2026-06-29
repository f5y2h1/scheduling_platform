import request from '../smartRequest';

export const userAPI = {
  list: (params) => request.get('/users', { params }),
  getById: (id) => request.get(`/users/${id}`),
  create: (data) => request.post('/users', data),
  update: (id, data) => request.put(`/users/${id}`, data),
  delete: (id) => request.delete(`/users/${id}`),
  updateStatus: (id, status) => request.put(`/users/${id}/status`, { status }),
  getRoles: () => request.get('/users/roles/list'),
};