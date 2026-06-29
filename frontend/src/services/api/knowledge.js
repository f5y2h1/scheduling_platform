import request from '../smartRequest';

export const knowledgeAPI = {
  getStats: () => request.get('/knowledge/stats'),
  listCollections: () => request.get('/knowledge/collections'),
  addDocument: (data) => request.post('/knowledge/documents', data),
  addDocuments: (data) => request.post('/knowledge/documents/batch', data),
  search: (data) => request.post('/knowledge/search', data),
  hybridSearch: (data) => request.post('/knowledge/search/hybrid', data),
  categorySearch: (data) => request.post('/knowledge/search/category', data),
  ragQuery: (data) => request.post('/knowledge/rag/query', data),
  rerank: (data) => request.post('/knowledge/rag/rerank', data),
  embed: (data) => request.post('/knowledge/embed', data),
  searchDecisions: (data) => request.post('/knowledge/decisions/search', data),
  searchRules: (data) => request.post('/knowledge/rules/search', data),
  initDefault: () => request.post('/knowledge/init-default'),
  deleteDocument: (id, collection) => request.delete(`/knowledge/documents/${id}`, { params: { collection } }),
};