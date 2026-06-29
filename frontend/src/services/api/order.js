import request from '../smartRequest';

export const orderAPI = {
  list: (params) => request.get('/orders', { params }),
  getById: (id) => request.get(`/orders/${id}`),
  create: (data) => request.post('/orders', data),
  update: (id, data) => request.put(`/orders/${id}`, data),
  updateStatus: (id, status) => request.put(`/orders/${id}/status`, { status }),
  cancel: (id) => request.post(`/orders/${id}/cancel`),
  stats: () => request.get('/orders/stats'),
};