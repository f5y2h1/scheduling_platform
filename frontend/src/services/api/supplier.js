import request from '../smartRequest';

export const supplierAPI = {
  list: (params) => request.get('/suppliers', { params }),
  getById: (id) => request.get(`/suppliers/${id}`),
  create: (data) => request.post('/suppliers', data),
  update: (id, data) => request.put(`/suppliers/${id}`, data),
  updateStatus: (id, status) => request.put(`/suppliers/${id}/status`, { status }),
};