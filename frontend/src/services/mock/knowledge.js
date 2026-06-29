const r = () => Math.random();

export const mockKnowledgeData = {
  stats: () => ({
    totalDocuments: 156,
    totalCollections: 8,
    totalVectors: 12580,
    avgChunkSize: 320,
    lastUpdated: new Date().toISOString(),
  }),
  listCollections: () => [
    { id: 'inventory-strategy', name: '库存策略', docCount: 25, description: '库存管理相关策略文档' },
    { id: 'scheduling-rules', name: '调度规则', docCount: 38, description: '调度决策规则文档' },
    { id: 'demand-prediction', name: '需求预测', docCount: 30, description: '需求预测模型与方法' },
    { id: 'risk-rules', name: '风险规则', docCount: 22, description: '供应链风险评估规则' },
    { id: 'cost-optimization', name: '成本优化', docCount: 18, description: '成本优化策略文档' },
    { id: 'supplier-management', name: '供应商管理', docCount: 12, description: '供应商评估与管理' },
    { id: 'order-process', name: '订单流程', docCount: 8, description: '订单处理流程文档' },
    { id: 'quality-control', name: '质量控制', docCount: 3, description: '质量控制标准文档' },
  ],
  search: ({ data }) => ({
    documents: [
      { id: 1, content: `搜索结果1：关于 "${data.query}" 的详细信息...`, score: +(0.85 + r() * 0.1).toFixed(3), category: '库存策略' },
      { id: 2, content: `搜索结果2：关于 "${data.query}" 的补充说明...`, score: +(0.75 + r() * 0.1).toFixed(3), category: '调度规则' },
      { id: 3, content: `搜索结果3：关于 "${data.query}" 的相关文档...`, score: +(0.65 + r() * 0.1).toFixed(3), category: '需求预测' },
    ],
    total: 3,
  }),
  hybridSearch: ({ data }) => ({
    documents: [
      { id: 1, content: `混合搜索结果1：关于 "${data.query}" 的综合信息...`, score: +(0.9 + r() * 0.08).toFixed(3), category: '库存策略', source: 'vector' },
      { id: 2, content: `混合搜索结果2：关于 "${data.query}" 的详细文档...`, score: +(0.82 + r() * 0.08).toFixed(3), category: '调度规则', source: 'keyword' },
      { id: 3, content: `混合搜索结果3：关于 "${data.query}" 的相关资料...`, score: +(0.76 + r() * 0.08).toFixed(3), category: '风险规则', source: 'vector' },
      { id: 4, content: `混合搜索结果4：关于 "${data.query}" 的补充内容...`, score: +(0.7 + r() * 0.08).toFixed(3), category: '成本优化', source: 'keyword' },
    ],
    total: 4,
  }),
  categorySearch: ({ data }) => ({
    documents: [
      { id: 1, content: `分类搜索结果1：${data.category} 类别下关于 "${data.query}" 的信息...`, score: +(0.8 + r() * 0.15).toFixed(3), category: data.category },
      { id: 2, content: `分类搜索结果2：${data.category} 类别下关于 "${data.query}" 的详细说明...`, score: +(0.72 + r() * 0.15).toFixed(3), category: data.category },
    ],
    total: 2,
  }),
  ragQuery: ({ data }) => ({
    answer: `基于知识库分析，关于 "${data.query}" 的回答：\n\n1. 核心结论：根据现有知识库内容，该问题涉及库存策略和调度规则两个核心领域。\n\n2. 详细分析：系统推荐参考相关的库存优化文档和调度决策规则，综合考虑成本和效率因素。\n\n3. 建议方案：建议采用AI辅助决策Agent进行综合评估，生成最优方案。`,
    retrievalCount: 5,
    totalTimeMs: Math.floor(800 + r() * 500),
    sources: [
      { id: 1, title: '库存策略文档', relevance: +(0.9 + r() * 0.08).toFixed(2) },
      { id: 2, title: '调度规则手册', relevance: +(0.85 + r() * 0.08).toFixed(2) },
      { id: 3, title: '成本优化指南', relevance: +(0.78 + r() * 0.08).toFixed(2) },
    ],
  }),
  rerank: ({ data }) => ({
    documents: data.documents?.map((doc, i) => ({
      ...doc,
      score: +(0.6 + i * 0.1 + r() * 0.1).toFixed(3),
    })) || [],
  }),
  embed: ({ data }) => ({
    vectors: Array(data.texts?.length || 1).fill(null).map(() => 
      Array(1024).fill(null).map(() => +(Math.random() * 2 - 1).toFixed(6))
    ),
  }),
  searchDecisions: ({ data }) => ({
    decisions: [
      { id: 1, scenario: data.scenario, description: `场景 "${data.scenario}" 的决策方案1：建议采用优先级调度策略...`, confidence: +(0.85 + r() * 0.1).toFixed(2) },
      { id: 2, scenario: data.scenario, description: `场景 "${data.scenario}" 的决策方案2：建议考虑备选供应商方案...`, confidence: +(0.78 + r() * 0.1).toFixed(2) },
    ],
    total: 2,
  }),
  searchRules: ({ data }) => ({
    rules: [
      { id: 1, name: `规则1：${data.query} 相关规则`, condition: '当库存低于安全阈值时', action: '自动触发补货提醒', priority: 'high' },
      { id: 2, name: `规则2：${data.query} 处理规则`, condition: '当订单延迟超过24小时', action: '升级为紧急处理', priority: 'medium' },
    ],
    total: 2,
  }),
  initDefault: () => ({ success: true, message: '默认知识库初始化完成', docsAdded: 45 }),
  addDocument: ({ data }) => ({ success: true, documentId: `doc_${Date.now()}`, message: '文档入库成功' }),
  addDocuments: ({ data }) => ({ success: true, count: data.documents?.length || 1, message: '批量文档入库成功' }),
  deleteDocument: ({ params }) => ({ success: true, message: '文档删除成功' }),
};