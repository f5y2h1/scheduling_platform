import request from '../smartRequest';

export const aiAPI = {
  // 模型和 Agent
  getModels: () => request.get('/ai/models'),
  getAgents: () => request.get('/ai/agents'),
  chat: (data) => request.post('/ai/chat', data),
  invokeAgent: (agentId, data) => request.post(`/ai/agent/${agentId}`, data),
  runPipeline: (data) => request.post('/ai/pipeline', data),
  invokeParallel: (data) => request.post('/ai/parallel', data),

  // LangGraph 工作流
  runWorkflow: (data) => request.post('/ai/workflow/scheduling', data),

  // 三层记忆体系
  getMemorySummary: () => request.get('/ai/memory/summary'),

  // 会话管理（短期记忆）
  getSessions: () => request.get('/ai/sessions'),
  getSession: (sessionId) => request.get(`/ai/sessions/${sessionId}`),
  deleteSession: (sessionId) => request.delete(`/ai/sessions/${sessionId}`),

  // 用户偏好（长期记忆）
  getPreferences: () => request.get('/ai/memory/preferences'),
  savePreferences: (data) => request.put('/ai/memory/preferences', data),

  // 经验检索（长期记忆）
  searchExperiences: (query, topK = 5) =>
    request.post('/ai/memory/search', { query, top_k: topK }),
  getRecommendations: (query) =>
    request.post('/ai/memory/recommend', { query }),

  // 工具系统
  getTools: () => request.get('/ai/tools'),

  // 聊天接口
  chatSmart: (data) => request.post('/ai/chat/smart', data),
  chatStream: (data) => request.post('/ai/chat/stream', data, { responseType: 'stream' }),
  getChatContext: (sessionId) => request.post('/ai/chat/context', { session_id: sessionId }),
  clearChatContext: (sessionId) => request.delete(`/ai/chat/context/${sessionId}`),

  // 文件上传
  uploadFile: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return request.post('/ai/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },

  // 多模态功能（使用 qwen3.5-omni-plus）
  transcribeAudio: (audioFile) => {
    const formData = new FormData();
    formData.append('file', audioFile);
    return request.post('/ai/transcribe', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },

  analyzeImage: (imageFile, prompt = '请描述这张图片的内容。') => {
    const formData = new FormData();
    formData.append('file', imageFile);
    formData.append('prompt', prompt);
    return request.post('/ai/analyze-image', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
};
