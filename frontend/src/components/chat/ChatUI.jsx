import React, { useState, useRef, useEffect, useCallback, useLayoutEffect } from 'react';
import { Button, Input, Avatar, Tooltip, message, Spin, Image, Modal } from 'antd';
import {
  SendOutlined, AudioOutlined, PauseCircleOutlined,
  PictureOutlined, PaperClipOutlined,
  UserOutlined, RobotOutlined,
  ClearOutlined, ClockCircleOutlined, SettingOutlined,
} from '@ant-design/icons';
import { aiAPI } from '@/services/api';
import { usePersistedState } from '@/hooks/usePersistedState';

const { TextArea } = Input;

const CHAT_STORAGE_KEY = 'xuni_chat_history';
const SESSION_STORAGE_KEY = 'xuni_current_session';
const HISTORY_STORAGE_KEY = 'xuni_chat_history_records';

function loadMessagesFromStorage(sessionId) {
  try {
    const stored = localStorage.getItem(CHAT_STORAGE_KEY);
    if (stored) {
      const data = JSON.parse(stored);
      return data[sessionId] || [];
    }
  } catch (e) {
    console.error('[ChatUI] 加载消息失败:', e);
  }
  return [];
}

function saveMessagesToStorage(sessionId, messages) {
  try {
    const stored = localStorage.getItem(CHAT_STORAGE_KEY);
    const data = stored ? JSON.parse(stored) : {};
    data[sessionId] = messages;
    localStorage.setItem(CHAT_STORAGE_KEY, JSON.stringify(data));
  } catch (e) {
    console.error('[ChatUI] 保存消息失败:', e);
  }
}

function loadHistoryRecords() {
  try {
    const stored = localStorage.getItem(HISTORY_STORAGE_KEY);
    if (stored) {
      return JSON.parse(stored);
    }
  } catch (e) {
    console.error('[ChatUI] 加载历史记录失败:', e);
  }
  return [];
}

function saveHistoryRecord(sessionId, messages) {
  try {
    const records = loadHistoryRecords();
    const existingIndex = records.findIndex(r => r.sessionId === sessionId);
    
    const firstMsg = messages.find(m => m.role === 'user');
    const lastMsg = messages[messages.length - 1];
    
    const record = {
      sessionId,
      title: firstMsg?.content?.substring(0, 30) || '无标题对话',
      date: new Date().toLocaleDateString('zh-CN'),
      time: new Date().toLocaleTimeString('zh-CN'),
      messageCount: messages.length,
      lastUpdate: Date.now(),
    };
    
    if (existingIndex >= 0) {
      records[existingIndex] = record;
    } else {
      records.unshift(record);
    }
    
    localStorage.setItem(HISTORY_STORAGE_KEY, JSON.stringify(records));
    return records;
  } catch (e) {
    console.error('[ChatUI] 保存历史记录失败:', e);
    return [];
  }
}

function deleteHistoryRecord(sessionId) {
  try {
    const records = loadHistoryRecords().filter(r => r.sessionId !== sessionId);
    localStorage.setItem(HISTORY_STORAGE_KEY, JSON.stringify(records));
    
    const chatData = JSON.parse(localStorage.getItem(CHAT_STORAGE_KEY) || '{}');
    delete chatData[sessionId];
    localStorage.setItem(CHAT_STORAGE_KEY, JSON.stringify(chatData));
    
    return records;
  } catch (e) {
    console.error('[ChatUI] 删除历史记录失败:', e);
    return [];
  }
}

export default function ChatUI({ onWorkflowRequest, sessionId, setSessionId }) {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = usePersistedState('chat_input_value', '');
  const [isRecording, setIsRecording] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const [showImagePreview, setShowImagePreview] = useState(false);
  const [previewImage, setPreviewImage] = useState('');
  const [imageBase64, setImageBase64] = useState('');
  const [uploading, setUploading] = useState(false);
  const [recordingStatus, setRecordingStatus] = useState('');
  
  const messagesEndRef = useRef(null);
  const messagesContainerRef = useRef(null);
  const recognitionRef = useRef(null);
  const fileInputRef = useRef(null);
  
  useEffect(() => {
    const savedSessionId = localStorage.getItem(SESSION_STORAGE_KEY);
    const initialSessionId = sessionId || savedSessionId || `chat_${Date.now()}`;
    if (!sessionId) setSessionId(initialSessionId);
    const savedMessages = loadMessagesFromStorage(initialSessionId);
    if (savedMessages.length > 0) setMessages(savedMessages);
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    if (sessionId) {
      saveMessagesToStorage(sessionId, messages);
      localStorage.setItem(SESSION_STORAGE_KEY, sessionId);
    }
  }, [sessionId, messages]);

  useEffect(() => {
    if (messages.length > 0 && sessionId) saveHistoryRecord(sessionId, messages);
  }, [messages, sessionId]);

  const scrollToBottom = useCallback(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, []);
  
  useLayoutEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);
  
  useEffect(() => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      
      const createRecognition = () => {
        const recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = true;
        recognition.lang = 'zh-CN';
        
        recognition.onstart = () => {
          setRecordingStatus('正在录入...');
          console.log('[ChatUI] 语音识别已启动');
        };
        
        recognition.onresult = (event) => {
          let interimTranscript = '';
          let finalTranscript = '';
          
          for (let i = event.resultIndex; i < event.results.length; ++i) {
            if (event.results[i].isFinal) {
              finalTranscript += event.results[i][0].transcript;
            } else {
              interimTranscript += event.results[i][0].transcript;
            }
          }
          
          if (finalTranscript) {
            setInputValue(prev => prev + finalTranscript);
            setRecordingStatus('正在录入...');
          } else if (interimTranscript) {
            setRecordingStatus('正在录入...');
          }
        };
        
        recognition.onerror = (event) => {
          console.error('语音识别错误:', event.error);
          setIsRecording(false);
          setRecordingStatus('');
          
          if (event.error === 'not-allowed') {
            message.warning('请允许浏览器访问麦克风');
          } else if (event.error === 'no-speech') {
            message.info('未检测到语音，请重试');
          } else if (event.error === 'network') {
            message.warning('网络连接不稳定，请检查网络后重试');
          } else if (event.error === 'aborted') {
            console.warn('语音识别被中止');
          } else {
            message.error(`语音识别出错: ${event.error}`);
          }
        };
        
        recognition.onend = () => {
          setRecordingStatus('');
          if (isRecording) {
            console.log('[ChatUI] 语音识别自动重启');
            try {
              recognition.start();
            } catch (e) {
              console.error('重启语音识别失败:', e);
              setIsRecording(false);
            }
          }
        };
        
        return recognition;
      };
      
      recognitionRef.current = createRecognition();
      
      return () => {
        if (recognitionRef.current) {
          recognitionRef.current.abort();
          recognitionRef.current = null;
        }
        setIsRecording(false);
        setRecordingStatus('');
      };
    }
  }, []);
  
  const handleSend = async () => {
    if (!inputValue.trim() && !previewImage) return;

    const userMessage = {
      id: Date.now(),
      role: 'user',
      content: inputValue.trim() || `[图片]`,
      image: previewImage || null,
      imageBase64: imageBase64 || null,
      timestamp: new Date().toLocaleTimeString(),
      date: new Date().toLocaleDateString('zh-CN'),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setPreviewImage('');
    setImageBase64('');
    setIsTyping(true);

    const newSessionId = sessionId || `chat_${Date.now()}`;
    if (!sessionId) setSessionId(newSessionId);

    const assistantMessageId = Date.now() + 1;

    try {
      const result = await aiAPI.chat({
        session_id: newSessionId,
        message: userMessage.content,
        image: imageBase64,
        smart: true,
      });

      const { content, toolCalls } = result;

      const newMessages = [];

      if (toolCalls && toolCalls.length > 0) {
        for (let i = 0; i < toolCalls.length; i++) {
          const tc = toolCalls[i];
          newMessages.push({
            id: assistantMessageId + i * 10,
            role: 'tool',
            toolName: tc.tool,
            arguments: tc.arguments,
            result: tc.result,
            timestamp: new Date().toLocaleTimeString(),
            date: new Date().toLocaleDateString('zh-CN'),
          });
        }
      }

      newMessages.push({
        id: assistantMessageId,
        role: 'assistant',
        content: content || '抱歉，我暂时无法回答这个问题。',
        timestamp: new Date().toLocaleTimeString(),
        date: new Date().toLocaleDateString('zh-CN'),
      });

      setMessages(prev => [...prev, ...newMessages]);
      setIsTyping(false);

      if (content.includes('调度') ||
          content.includes('需求预测') ||
          content.includes('库存优化')) {
        setTimeout(() => {
          message.info('检测到调度需求，可点击下方按钮触发工作流');
        }, 1000);
      }

    } catch (error) {
      console.error('[ChatUI] 聊天错误:', error);
      setIsTyping(false);
      message.error('聊天失败，请重试');

      setMessages(prev => {
        const hasAssistantMsg = prev.some(msg => msg.id === assistantMessageId);
        if (hasAssistantMsg) {
          return prev.map(msg =>
            msg.id === assistantMessageId
              ? { ...msg, content: `抱歉，聊天服务暂时不可用。错误：${error.message}` }
              : msg
          );
        }
        return [...prev, {
          id: assistantMessageId,
          role: 'assistant',
          content: `抱歉，聊天服务暂时不可用。错误：${error.message}`,
          timestamp: new Date().toLocaleTimeString(),
          date: new Date().toLocaleDateString('zh-CN'),
        }];
      });
    }
  };
  
  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };
  
  const toggleRecording = () => {
    if (!recognitionRef.current) {
      message.warning('您的浏览器不支持语音识别，请使用最新版 Chrome 或 Edge 浏览器');
      return;
    }
    
    if (isRecording) {
      try {
        recognitionRef.current.stop();
        setIsRecording(false);
        setRecordingStatus('');
        message.success('录音已结束');
      } catch (e) {
        console.error('停止录音失败:', e);
        setIsRecording(false);
        setRecordingStatus('');
      }
    } else {
      try {
        recognitionRef.current.start();
        setIsRecording(true);
        setRecordingStatus('正在录入...');
        message.info('开始录音，请说话');
      } catch (e) {
        console.error('启动录音失败:', e);
        if (e.name === 'NotAllowedError') {
          message.warning('请在浏览器设置中允许访问麦克风');
        } else {
          message.error(`启动录音失败: ${e.message}`);
        }
      }
    }
  };
  
  const handleImageUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (!file.type.startsWith('image/')) {
      message.warning('请上传图片文件');
      return;
    }

    setUploading(true);

    try {
      const base64 = await new Promise((resolve) => {
        const reader = new FileReader();
        reader.onloadend = () => resolve(reader.result);
        reader.readAsDataURL(file);
      });
      setImageBase64(base64);

      const imageUrl = URL.createObjectURL(file);
      setPreviewImage(imageUrl);

      setShowImagePreview(true);
    } catch (error) {
      message.error('图片处理失败');
    } finally {
      setUploading(false);
      e.target.value = '';
    }
  };
  
  const handleClear = () => {
    setInputValue('');
    setPreviewImage('');
  };
  
  const handleClearHistory = () => {
    Modal.confirm({
      title: '清空对话',
      content: '确定要清空当前对话吗？对话将被保存到历史记录中。',
      onOk: () => {
        if (sessionId) {
          saveHistoryRecord(sessionId, messages);
          // (history saved to localStorage for sidebar panel)
        }
        setMessages([]);
        const newSessionId = `chat_${Date.now()}`;
        setSessionId(newSessionId);
        message.success('对话已清空并保存到历史记录');
      },
    });
  };
  
  const handleStartWorkflow = () => {
    if (onWorkflowRequest) {
      onWorkflowRequest(inputValue.trim() || '请制定调度方案');
    }
  };
  
  const formatMessage = (content) => {
    return content.split('\n').map((line, index) => (
      <span key={index}>
        {line || '\u00A0'}
        <br />
      </span>
    ));
  };
  
  const renderDateDivider = (date, index, messages) => {
    if (index === 0) return null;
    const prevMsg = messages[index - 1];
    if (prevMsg?.date === date) return null;
    
    return (
      <div style={{
        textAlign: 'center',
        margin: '16px 0',
      }}>
        <span style={{
          padding: '4px 12px',
          background: '#e2e8f0',
          borderRadius: 12,
          fontSize: 12,
          color: '#64748b',
        }}>
          <ClockCircleOutlined style={{ marginRight: 4 }} />
          {date}
        </span>
      </div>
    );
  };
  
  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      height: '100%',
      background: '#f8fafc',
      borderRadius: 16,
      overflow: 'hidden',
      boxShadow: '0 8px 32px rgba(0, 0, 0, 0.06)',
    }}>
      {/* 头部工具栏 */}
      <div style={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '16px 24px',
      background: '#fff',
      borderBottom: '1px solid #e2e8f0',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
        <div style={{
          width: 56,
          height: 56,
          borderRadius: 16,
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          boxShadow: '0 8px 24px rgba(102, 126, 234, 0.35)',
        }}>
          <RobotOutlined style={{ fontSize: 28, color: '#fff' }} />
        </div>
        <div>
          <div style={{ fontSize: 18, fontWeight: 700, color: '#e2e8f0' }}>供应链智能助手</div>
          <div style={{ fontSize: 13, color: '#94a3b8', marginTop: 4 }}>
            {sessionId ? `会话: ${sessionId.slice(0, 8)}...` : '新会话'}
          </div>
        </div>
      </div>
        
        {messages.length > 0 && (
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <Tooltip title="清空当前对话">
              <Button
                icon={<ClearOutlined />}
                size="small"
                danger
                style={{ borderRadius: 8 }}
                onClick={handleClearHistory}
              >
                清空
              </Button>
            </Tooltip>
          </div>
        )}
      </div>
      
      {/* 聊天区域 */}
      <div
        ref={messagesContainerRef}
        style={{
          flex: 1,
          overflowY: 'auto',
          padding: 24,
          display: 'flex',
          flexDirection: 'column',
          gap: 16,
          minHeight: 0,
        }}
        className="chat-messages-container"
      >
        {messages.length === 0 ? (
          <div style={{
            flex: 1,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#64748b',
          }}>
            <div style={{
              width: 80,
              height: 80,
              borderRadius: 40,
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              marginBottom: 16,
            }}>
              <RobotOutlined style={{ fontSize: 36, color: '#fff' }} />
            </div>
            <p style={{ fontSize: 16, fontWeight: 500, margin: 0 }}>供应链智能助手</p>
            <p style={{ fontSize: 13, marginTop: 8, textAlign: 'center', maxWidth: 300 }}>
              您好！我可以帮您解答供应链管理相关问题，或为您制定智能调度方案。
            </p>
            <div style={{ marginTop: 20, display: 'flex', gap: 8 }}>
              <Button size="small" ghost style={{ color: '#e2e8f0' }} onClick={() => setInputValue('什么是供应链调度？')}>
                什么是供应链调度？
              </Button>
              <Button size="small" ghost style={{ color: '#e2e8f0' }} onClick={() => setInputValue('帮我制定库存优化方案')}>
                帮我制定库存优化方案
              </Button>
            </div>
          </div>
        ) : (
          messages.map((msg, index) => (
            <React.Fragment key={msg.id}>
              {renderDateDivider(msg.date, index, messages)}
              {msg.role === 'tool' ? (
                <div
                  style={{
                    padding: '8px 0',
                    display: 'flex',
                    justifyContent: 'center',
                  }}
                >
                  <div
                    style={{
                      width: '75%',
                      padding: '12px 16px',
                      borderRadius: 12,
                      background: '#f0fdf4',
                      border: '1px solid #bbf7d0',
                      fontSize: 13,
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
                      <SettingOutlined style={{ color: '#10b981', fontSize: 16 }} />
                      <span style={{ fontWeight: 600, color: '#059669' }}>调用工具: {msg.toolName}</span>
                    </div>
                    {msg.arguments && Object.keys(msg.arguments).length > 0 && (
                      <div style={{ marginBottom: 8, paddingLeft: 24 }}>
                        <span style={{ color: '#64748b', fontSize: 12 }}>参数:</span>
                        <pre style={{ 
                          margin: '4px 0 0 0', 
                          padding: '8px', 
                          background: '#f8fafc', 
                          borderRadius: 6,
                          fontSize: 12,
                          overflowX: 'auto',
                          color: '#374151'
                        }}>
                          {JSON.stringify(msg.arguments, null, 2)}
                        </pre>
                      </div>
                    )}
                    <div style={{ paddingLeft: 24 }}>
                      <span style={{ color: '#64748b', fontSize: 12 }}>结果:</span>
                      <pre style={{ 
                        margin: '4px 0 0 0', 
                        padding: '8px', 
                        background: '#f8fafc', 
                        borderRadius: 6,
                        fontSize: 12,
                        overflowX: 'auto',
                        maxHeight: 200,
                        overflowY: 'auto',
                        color: '#374151'
                      }}>
                        {JSON.stringify(msg.result, null, 2)}
                      </pre>
                    </div>
                  </div>
                </div>
              ) : (
                <div
                  style={{
                    display: 'flex',
                    flexDirection: msg.role === 'user' ? 'row-reverse' : 'row',
                    gap: 12,
                    alignItems: 'flex-start',
                  }}
                >
                  <Avatar
                    icon={msg.role === 'user' ? <UserOutlined /> : <RobotOutlined />}
                    style={{
                      background: msg.role === 'user' 
                        ? 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)'
                        : '#14b8a6',
                      width: 40,
                      height: 40,
                      flexShrink: 0,
                      border: '2px solid #fff',
                      boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)',
                    }}
                  />
                  <div style={{ maxWidth: '75%', minWidth: 0 }}>
                    <div
                      style={{
                        padding: '14px 18px',
                        borderRadius: msg.role === 'user' 
                          ? '18px 18px 6px 18px'
                          : '18px 18px 18px 6px',
                        background: msg.role === 'user'
                          ? 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)'
                          : '#fff',
                        color: msg.role === 'user' ? '#fff' : '#1e293b',
                        boxShadow: msg.role === 'user'
                          ? '0 4px 12px rgba(99, 102, 241, 0.3)'
                          : '0 2px 8px rgba(0, 0, 0, 0.06)',
                        fontSize: 14,
                        lineHeight: 1.65,
                      }}
                    >
                      {msg.image ? (
                        <Image
                          src={msg.image}
                          style={{ maxWidth: '100%', borderRadius: 8 }}
                          onClick={() => {
                            setPreviewImage(msg.image);
                            setShowImagePreview(true);
                          }}
                        />
                      ) : (
                        formatMessage(msg.content)
                      )}
                    </div>
                    <div
                      style={{
                        fontSize: 11,
                        color: '#64748b',
                        marginTop: 4,
                        textAlign: msg.role === 'user' ? 'right' : 'left',
                        padding: '0 4px',
                      }}
                    >
                      {msg.timestamp}
                    </div>
                  </div>
                </div>
              )}
            </React.Fragment>
          ))
        )}
        
        {isTyping && (
          <div style={{ display: 'flex', gap: 12 }}>
            <Avatar
              icon={<RobotOutlined />}
              style={{ background: '#10b981', width: 40, height: 40, flexShrink: 0 }}
            />
            <div
              style={{
                padding: '12px 16px',
                borderRadius: '16px 16px 16px 4px',
                background: '#fff',
                boxShadow: '0 2px 8px rgba(0, 0, 0, 0.08)',
              }}
            >
              <Spin size="small" />
              <span style={{ marginLeft: 8, color: '#64748b', fontSize: 14 }}>正在思考...</span>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>
      
      {/* 输入区域 */}
      <div style={{
        background: '#fff',
        padding: 16,
        borderTop: '1px solid #e2e8f0',
        boxShadow: '0 -4px 16px rgba(0, 0, 0, 0.04)',
        flexShrink: 0,
      }}>
        {previewImage && (
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: 8,
            padding: 8,
            background: '#fafbfc',
            borderRadius: 8,
            marginBottom: 12,
          }}>
            <Image
              src={previewImage}
              width={60}
              height={60}
              style={{ borderRadius: 8, objectFit: 'cover' }}
            />
            <span style={{ fontSize: 13, color: '#94a3b8' }}>已添加图片</span>
            <Button
              type="text"
              danger
              icon={<ClearOutlined />}
              onClick={() => setPreviewImage('')}
            />
          </div>
        )}
        
        <div style={{ display: 'flex', gap: 12 }}>
          <div style={{ flex: 1, position: 'relative' }}>
            <TextArea
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={handleKeyPress}
              placeholder="输入消息，按 Enter 发送，Shift+Enter 换行..."
              rows={2}
              style={{
                borderRadius: 12,
                resize: 'vertical',
                minHeight: 80,
                maxHeight: 200,
                fontSize: 14,
              }}
            />
          </div>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            <div style={{ display: 'flex', gap: 4, alignItems: 'center' }}>
              <Tooltip title="图片上传">
                <Button
                  icon={<PictureOutlined />}
                  onClick={() => fileInputRef.current?.click()}
                  disabled={uploading}
                  style={{ borderRadius: 10 }}
                />
              </Tooltip>
              <Tooltip title={isRecording ? '停止录音' : '语音输入'}>
                <Button
                  icon={isRecording ? <PauseCircleOutlined /> : <AudioOutlined />}
                  onClick={toggleRecording}
                  type={isRecording ? 'primary' : 'default'}
                  danger={isRecording}
                  style={{ borderRadius: 10 }}
                />
              </Tooltip>
              {isRecording && (
                <span style={{ fontSize: 12, color: '#ef4444', fontWeight: 500 }}>
                  🎤 {recordingStatus}
                </span>
              )}
            </div>
            
            <div style={{ display: 'flex', gap: 4 }}>
              <Button
                icon={<SendOutlined />}
                type="primary"
                onClick={handleSend}
                disabled={!inputValue.trim() && !previewImage}
                style={{ borderRadius: 10 }}
              >
                发送
              </Button>
            </div>
          </div>
        </div>
        
        {(messages.length > 0 || inputValue.trim()) && (
          <div style={{
            marginTop: 12,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            paddingTop: 12,
            borderTop: '1px dashed #eee',
          }}>
            <span style={{ fontSize: 12, color: '#64748b' }}>
              💡 如果需要制定完整的调度方案，请点击下方按钮
            </span>
            <Button
                type="primary"
                icon={<PaperClipOutlined />}
                onClick={handleStartWorkflow}
                style={{
                  borderRadius: 8,
                  background: 'linear-gradient(135deg, #f59e0b 0%, #ef4444 100%)',
                  border: 'none',
                }}
              >
                触发调度工作流
              </Button>
          </div>
        )}
        
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          onChange={handleImageUpload}
          style={{ display: 'none' }}
        />
      </div>
      
      <Modal
        open={showImagePreview}
        footer={null}
        onCancel={() => setShowImagePreview(false)}
        width={600}
      >
        <Image
          src={previewImage}
          style={{ width: '100%' }}
        />
      </Modal>
    </div>
  );
}