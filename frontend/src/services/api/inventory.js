import request from '../smartRequest';

export const inventoryAPI = {
  list: (params) => request.get('/inventory', { params }),
  getById: (id) => request.get(`/inventory/${id}`),
  create: (data) => request.post('/inventory', data),
  update: (id, data) => request.put(`/inventory/${id}`, data),
  stockIn: (id, quantity) => request.post(`/inventory/${id}/stock-in`, { quantity }),
  stockOut: (id, quantity) => request.post(`/inventory/${id}/stock-out`, { quantity }),
  alerts: () => request.get('/inventory/alerts'),
  stats: () => request.get('/inventory/stats'),
};