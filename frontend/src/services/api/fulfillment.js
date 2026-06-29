import request from '../smartRequest';

export const fulfillmentAPI = {
  list: (params) => request.get('/fulfillment', { params }),
  getById: (id) => request.get(`/fulfillment/${id}`),
  create: (data) => request.post('/fulfillment', data),
  updateStatus: (id, status) => request.put(`/fulfillment/${id}/status`, { status }),
  updateTracking: (id, data) => request.put(`/fulfillment/${id}/tracking`, data),
  stats: () => request.get('/fulfillment/stats'),
};