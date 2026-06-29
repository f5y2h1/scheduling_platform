import request from '../smartRequest';

export const schedulingAPI = {
  list: (params) => request.get('/scheduling', { params }),
  getById: (id) => request.get(`/scheduling/${id}`),
  create: (data) => request.post('/scheduling', data),
  aiSuggest: (id, model) => request.post(`/scheduling/${id}/ai-suggest`, { model }),
  approve: (id, approved, username) => request.post(`/scheduling/${id}/approve`, { approved, username }),
  execute: (id) => request.post(`/scheduling/${id}/execute`),
  complete: (id) => request.post(`/scheduling/${id}/complete`),
};