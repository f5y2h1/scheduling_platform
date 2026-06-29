export const mockAiData = {
  getModels: () => [
    { id: 'qwen-plus', name: '通义千问-Plus', description: '高性能，适用于日常对话场景' },
    { id: 'qwen-max', name: '通义千问-Max', description: '超强能力，适用于复杂场景' },
    { id: 'qwen-turbo', name: '通义千问-Turbo', description: '极速响应，适用于简单任务' },
    { id: 'qwen2.5-72b-instruct', name: '通义千问2.5-72B', description: '72B参数指令微调模型' },
    { id: 'qwen2.5-32b-instruct', name: '通义千问2.5-32B', description: '32B参数指令微调模型' },
    { id: 'qwen2.5-14b-instruct', name: '通义千问2.5-14B', description: '14B参数指令微调模型' },
    { id: 'qwen2.5-7b-instruct', name: '通义千问2.5-7B', description: '7B参数指令微调模型，轻量快速' },
  ],
  getAgents: () => [
    { id: 'demand-prediction', name: '需求预测', description: '基于历史数据预测未来需求', status: 'active' },
    { id: 'inventory-optimization', name: '库存优化', description: '优化库存水平，降低成本', status: 'active' },
    { id: 'scheduling-decision', name: '调度决策', description: '智能调度方案生成', status: 'active' },
    { id: 'cost-optimization', name: '成本优化', description: '降低供应链成本', status: 'active' },
    { id: 'risk-control', name: '风险控制', description: '识别和预警供应链风险', status: 'active' },
    { id: 'execution-control', name: '执行管控', description: '监控和控制执行过程', status: 'active' },
  ],
  chat: (data) => ({ reply: `AI 响应: ${data.message} 的分析结果...`, tokens: 128 }),
};