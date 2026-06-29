import { authAPI } from './api/auth';
import { userAPI } from './api/user';
import { orderAPI } from './api/order';
import { inventoryAPI } from './api/inventory';
import { schedulingAPI } from './api/scheduling';
import { fulfillmentAPI } from './api/fulfillment';
import { supplierAPI } from './api/supplier';
import { aiAPI } from './api/ai';
import { reportAPI } from './api/report';
import { knowledgeAPI } from './api/knowledge';

export {
  authAPI,
  userAPI,
  orderAPI,
  inventoryAPI,
  schedulingAPI,
  fulfillmentAPI,
  supplierAPI,
  aiAPI,
  reportAPI,
  knowledgeAPI,
};

export default {
  auth: authAPI,
  user: userAPI,
  order: orderAPI,
  inventory: inventoryAPI,
  scheduling: schedulingAPI,
  fulfillment: fulfillmentAPI,
  supplier: supplierAPI,
  ai: aiAPI,
  report: reportAPI,
  knowledge: knowledgeAPI,
};