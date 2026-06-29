import request from '../smartRequest';

export const reportAPI = {
  getDashboard: () => request.get('/reports/dashboard'),
  getOrderTrend: (days) => request.get('/reports/order-trend', { params: { days } }),
  getInventoryOverview: () => request.get('/reports/inventory-overview'),
  getSchedulingEfficiency: () => request.get('/reports/scheduling-efficiency'),
  getAiUsage: () => request.get('/reports/ai-usage'),
  export: (type) => request.get(`/reports/export/${type}`),
};