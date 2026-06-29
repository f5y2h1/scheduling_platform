"""
阿里云百炼 API 客户端（Python SDK）
封装 LLM 对话、Embedding 调用、流式响应
使用 qwen3.5-omni-plus 全模态模型
"""
import time
import json
from typing import AsyncGenerator, List, Dict, Any

from dashscope import MultiModalConversation
from dashscope.embeddings import TextEmbedding

from app.core.config import settings
from app.core.logger import logger


class BailianClient:
    """百炼 API 统一封装"""

    MODELS = [
        {"id": "qwen3.5-omni-plus", "name": "通义千问3.5-Omni-Plus", "description": "全模态模型，支持对话、语音转文字、图片解析"},
    ]

    def get_models(self) -> list[dict]:
        return self.MODELS
    
    def _convert_to_multimodal_format(self, messages: list[dict]) -> list[dict]:
        """将标准消息格式转换为多模态格式（支持文本+图片）"""
        return [
            {
                "role": m.get("role", "user"),
                "content": self._build_multimodal_content(m.get("content", ""), m.get("image"))
            }
            for m in messages
        ]
    
    def _build_multimodal_content(self, content: str, image: str = None) -> list[dict]:
        """构建多模态消息内容（支持文本+图片）"""
        parts = []
        if image:
            parts.append({"image": image})
        if content and content.strip():
            parts.append({"text": content.strip()})
        return parts if parts else [{"text": ""}]
    
    def _convert_tools_for_model(self, tools: List[Dict]) -> List[Dict]:
        """将工具列表转换为模型可识别的格式"""
        formatted_tools = []
        for tool in tools:
            formatted_tool = {
                "name": tool.get("name", ""),
                "description": tool.get("description", ""),
            }
            if tool.get("args_schema"):
                formatted_tool["parameters"] = tool["args_schema"]
            formatted_tools.append(formatted_tool)
        return formatted_tools
    
    def _convert_to_tools_format(self, tools: List[Dict]) -> List[Dict]:
        """将工具列表转换为百炼API需要的格式"""
        formatted_tools = []
        for tool in tools:
            schema = tool.get("args_schema", {})
            parameters = {}
            if schema:
                properties = schema.get("properties", {})
                required = schema.get("required", [])
                parameters = {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                }
            
            formatted_tool = {
                "tool_name": tool.get("name", ""),
                "tool_description": tool.get("description", ""),
                "parameters": parameters,
            }
            formatted_tools.append(formatted_tool)
        return formatted_tools
    
    def _parse_tool_calls(self, tool_calls_data) -> List[Dict]:
        """解析模型返回的工具调用"""
        tool_calls = []
        
        if isinstance(tool_calls_data, list):
            for tc in tool_calls_data:
                tool_call = {}
                if isinstance(tc, dict):
                    tool_call["name"] = tc.get("name") or tc.get("tool_name")
                    tool_call["arguments"] = tc.get("arguments") or tc.get("params") or {}
                else:
                    tool_call["name"] = getattr(tc, "name", None) or getattr(tc, "tool_name", None)
                    tool_call["arguments"] = getattr(tc, "arguments", None) or getattr(tc, "params", None) or {}
                
                if tool_call["name"]:
                    tool_calls.append(tool_call)
        
        return tool_calls

    # ===================== LLM 对话 =====================

    def chat(
        self,
        messages: list[dict],
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        tools: List[Dict] = None,
    ) -> dict:
        """同步对话 — 使用 MultiModalConversation.call()（支持 Function Calling）"""
        temp = temperature if temperature is not None else settings.LLM_TEMPERATURE
        max_tok = max_tokens or settings.LLM_MAX_TOKENS
        current_model = model or settings.LLM_DEFAULT_MODEL

        msgs = self._convert_to_multimodal_format(messages)

        try:
            t0 = time.time()
            
            call_kwargs = {
                "api_key": settings.BAILIAN_API_KEY,
                "model": current_model,
                "messages": msgs,
                "temperature": temp,
                "max_tokens": max_tok,
            }
            
            if tools and len(tools) > 0:
                call_kwargs["tools"] = self._convert_to_tools_format(tools)

            response = MultiModalConversation.call(**call_kwargs)
            elapsed = time.time() - t0

            content = ""
            tool_calls = []
            if response.status_code == 200:
                output = response.output
                choices = None
                if output is not None:
                    choices = getattr(output, "choices", None)
                    if choices is None and isinstance(output, dict):
                        choices = output.get("choices")

                if choices and len(choices) > 0:
                    msg = choices[0]
                    msg_obj = getattr(msg, "message", None)
                    if msg_obj is None and isinstance(msg, dict):
                        msg_obj = msg.get("message")
                    if msg_obj is not None:
                        content_data = getattr(msg_obj, "content", None)
                        if content_data is None and isinstance(msg_obj, dict):
                            content_data = msg_obj.get("content") or ""
                        
                        if isinstance(content_data, list):
                            text_parts = []
                            for item in content_data:
                                if isinstance(item, dict) and "text" in item:
                                    text_parts.append(item["text"])
                                elif isinstance(item, str):
                                    text_parts.append(item)
                            content = "".join(text_parts)
                        else:
                            content = str(content_data)
                        
                        tool_calls_data = getattr(msg_obj, "tool_calls", None)
                        if tool_calls_data is None and isinstance(msg_obj, dict):
                            tool_calls_data = msg_obj.get("tool_calls")
                        
                        if tool_calls_data:
                            tool_calls = self._parse_tool_calls(tool_calls_data)

            total_tokens = 0
            if response.usage:
                total_tokens = getattr(response.usage, "total_tokens", 0)
                if total_tokens == 0 and isinstance(response.usage, dict):
                    total_tokens = response.usage.get("total_tokens", 0)

            logger.info(
                f"LLM调用: model={current_model}, tokens={total_tokens}, time={elapsed:.2f}s, tool_calls={len(tool_calls)}"
            )

            return {
                "success": True,
                "content": content,
                "model": current_model,
                "total_tokens": total_tokens,
                "response_time": round(elapsed, 3),
                "tool_calls": tool_calls,
            }

        except Exception as e:
            logger.error(f"LLM调用异常: model={current_model}, error={str(e)}")
            return {
                "success": False,
                "content": "",
                "model": current_model,
                "total_tokens": 0,
                "response_time": 0,
            }

    def simple_chat(
        self, system_prompt: str, user_message: str, model: str | None = None,
    ) -> str:
        """单轮对话快捷方法"""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_message},
        ]
        return self.chat(messages, model=model).get("content", "")

    # ===================== Embedding 向量化 =====================

    def embed(self, text: str) -> list[float]:
        """单文本向量化 → list[float]"""
        results = self.embed_batch([text])
        return results[0] if results else []

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """批量文本向量化 → list[list[float]]"""
        if not texts:
            return []

        response = TextEmbedding.call(
            api_key=settings.BAILIAN_API_KEY,
            model=settings.EMBEDDING_MODEL,
            input=texts,
        )

        vectors: list[list[float]] = []

        # 兼容 dashscope 不同版本：output 可能是对象也可能是 dict
        if response.status_code == 200:
            output = response.output
            embeddings = None

            if output is not None:
                # 优先对象属性访问，兼容 dict 访问
                embeddings = getattr(output, "embeddings", None)
                if embeddings is None and isinstance(output, dict):
                    embeddings = output.get("embeddings")

            if embeddings:
                for emb in embeddings:
                    # 同样兼容 emb.embedding / emb["embedding"]
                    vec = getattr(emb, "embedding", None)
                    if vec is None and isinstance(emb, dict):
                        vec = emb.get("embedding")
                    if vec:
                        vectors.append(vec)

        total_tokens = 0
        if response.usage:
            total_tokens = getattr(response.usage, "total_tokens", 0)
            if total_tokens == 0 and isinstance(response.usage, dict):
                total_tokens = response.usage.get("total_tokens", 0)

        logger.debug(
            "Embedding: %d texts → %d vectors, tokens=%d",
            len(texts), len(vectors), total_tokens,
        )
        return vectors

    def _streaming_chat_sync(
        self,
        messages: list[dict],
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ):
        """同步流式对话 - 内部使用"""
        temp = temperature if temperature is not None else settings.LLM_TEMPERATURE
        max_tok = max_tokens or settings.LLM_MAX_TOKENS
        current_model = model or settings.LLM_DEFAULT_MODEL

        msgs = self._convert_to_multimodal_format(messages)

        try:
            t0 = time.time()
            response = MultiModalConversation.call(
                api_key=settings.BAILIAN_API_KEY,
                model=current_model,
                messages=msgs,
                temperature=temp,
                max_tokens=max_tok,
                stream=True,
            )

            full_content = ""
            results = []

            for chunk in response:
                if chunk.status_code == 200:
                    output = chunk.output
                    if output:
                        if len(results) == 0:
                            logger.info(f"[调试] 第一个流式chunk: output={output}")
                        choices = getattr(output, "choices", None)
                        if choices is None and isinstance(output, dict):
                            choices = output.get("choices")

                        if choices and len(choices) > 0:
                            msg = choices[0]
                            msg_obj = getattr(msg, "message", None)
                            if msg_obj is None and isinstance(msg, dict):
                                msg_obj = msg.get("message")

                            if msg_obj is not None:
                                content_data = getattr(msg_obj, "content", None)
                                if content_data is None and isinstance(msg_obj, dict):
                                    content_data = msg_obj.get("content")
                                
                                if content_data is None:
                                    delta = getattr(msg_obj, "delta", None)
                                    if delta is None and isinstance(msg_obj, dict):
                                        delta = msg_obj.get("delta", {})
                                    if delta:
                                        content_data = getattr(delta, "content", None)
                                        if content_data is None and isinstance(delta, dict):
                                            content_data = delta.get("content")

                                text = ""
                                if isinstance(content_data, list):
                                    for item in content_data:
                                        if isinstance(item, dict) and "text" in item:
                                            text += item["text"]
                                        elif isinstance(item, str):
                                            text += item
                                elif isinstance(content_data, str):
                                    text = content_data
                                elif isinstance(content_data, dict):
                                    text = content_data.get("text", "")

                                if text:
                                    full_content += text
                                    results.append(text)

            elapsed = time.time() - t0
            logger.info(
                f"LLM流式调用: model={current_model}, content_len={len(full_content)}, time={elapsed:.2f}s, chunks={len(results)}"
            )

            return results

        except Exception as e:
            logger.error(f"LLM流式调用异常: model={current_model}, error={str(e)}")
            return []

    # ===================== 多模态处理 =====================

    def transcribe_audio(self, audio_url: str) -> str:
        """
        语音转文字 - 使用 qwen3.5-omni-plus 全模态模型
        :param audio_url: 音频文件URL或base64编码
        :return: 转录文本
        """
        try:
            from dashscope import MultiModalConversation

            messages = [
                {
                    "role": "user",
                    "content": [
                        {"audio": audio_url},
                        {"text": "请将这段音频转录为文字，只输出转录结果，不要添加任何解释。"}
                    ]
                }
            ]

            response = MultiModalConversation.call(
                api_key=settings.BAILIAN_API_KEY,
                model=settings.MULTIMODAL_MODEL,
                messages=messages,
            )

            if response.status_code == 200:
                output = response.output
                choices = getattr(output, "choices", None)
                if choices is None and isinstance(output, dict):
                    choices = output.get("choices")

                if choices and len(choices) > 0:
                    msg = choices[0].get("message", choices[0])
                    content = msg.get("content", "") if isinstance(msg, dict) else getattr(msg, "content", "")
                    logger.info("语音转文字成功: len=%d", len(content))
                    return content

            logger.error("语音转文字失败: status=%s", response.status_code)
            return ""

        except Exception as e:
            logger.error("语音转文字异常: %s", e)
            return ""

    def analyze_image(self, image_url: str, prompt: str = "请描述这张图片的内容。") -> str:
        """
        图片解析 - 使用 qwen3.5-omni-plus 全模态模型
        :param image_url: 图片URL或base64编码
        :param prompt: 分析提示词
        :return: 分析结果文本
        """
        try:
            from dashscope import MultiModalConversation

            messages = [
                {
                    "role": "user",
                    "content": [
                        {"image": image_url},
                        {"text": prompt}
                    ]
                }
            ]

            response = MultiModalConversation.call(
                api_key=settings.BAILIAN_API_KEY,
                model=settings.MULTIMODAL_MODEL,
                messages=messages,
            )

            if response.status_code == 200:
                output = response.output
                choices = getattr(output, "choices", None)
                if choices is None and isinstance(output, dict):
                    choices = output.get("choices")

                if choices and len(choices) > 0:
                    msg = choices[0].get("message", choices[0])
                    content = msg.get("content", "") if isinstance(msg, dict) else getattr(msg, "content", "")
                    logger.info("图片解析成功: len=%d", len(content))
                    return content

            logger.error("图片解析失败: status=%s", response.status_code)
            return ""

        except Exception as e:
            logger.error("图片解析异常: %s", e)
            return ""

    async def streaming_chat(
        self,
        messages: list[dict],
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> AsyncGenerator[str, None]:
        """异步流式对话"""
        import asyncio
        
        results = await asyncio.to_thread(
            self._streaming_chat_sync,
            messages, model, temperature, max_tokens
        )
        
        for text in results:
            yield text


class ContextManager:
    """聊天上下文管理器"""
    
    MAX_HISTORY_ROUNDS = 10
    MAX_TOTAL_TOKENS = 4000
    COMPRESS_THRESHOLD = 5
    
    def __init__(self):
        self.conversations: Dict[str, List[Dict[str, Any]]] = {}
    
    def get_history(self, session_id: str) -> List[Dict[str, Any]]:
        return self.conversations.get(session_id, [])
    
    def add_message(self, session_id: str, role: str, content: str, image: str = None):
        if session_id not in self.conversations:
            self.conversations[session_id] = []
        
        self.conversations[session_id].append({
            "role": role,
            "content": content,
            "image": image,
            "timestamp": time.time(),
        })
        
        self._compress_history(session_id)
    
    def _compress_history(self, session_id: str):
        history = self.conversations.get(session_id, [])
        
        if len(history) <= self.MAX_HISTORY_ROUNDS:
            return
        
        compressed = []
        if len(history) > self.COMPRESS_THRESHOLD:
            old_messages = history[:-self.COMPRESS_THRESHOLD]
            summary = self._generate_summary(old_messages)
            compressed.append({
                "role": "system",
                "content": f"【对话摘要】{summary}",
                "is_summary": True,
            })
        
        compressed.extend(history[-self.COMPRESS_THRESHOLD:])
        self.conversations[session_id] = compressed
    
    def _generate_summary(self, messages: List[Dict[str, Any]]) -> str:
        try:
            user_content = "\n".join([m["content"] for m in messages if m["role"] == "user"])
            assistant_content = "\n".join([m["content"] for m in messages if m["role"] == "assistant"])
            
            summary_prompt = f"""请用简短的中文概括以下对话内容：

用户说：
{user_content[:500]}

助手回复：
{assistant_content[:500]}

摘要："""
            
            summary = bailian_client.simple_chat(
                system_prompt="你是一个对话摘要助手，请用简洁的语言概括对话要点。",
                user_message=summary_prompt,
                model="qwen3.5-omni-plus",
            )
            return summary[:200]
        except Exception as e:
            logger.error(f"生成摘要失败: {e}")
            return "历史对话较多，已压缩"
    
    def build_messages(self, session_id: str, current_query: str, image: str = None) -> List[Dict[str, Any]]:
        history = self.get_history(session_id)
        messages = []
        
        system_prompt = {
            "role": "system",
            "content": "你是一个供应链调度智能助手，具备图片理解能力。你的任务是：\n"
                       "1. 当用户上传图片时，先分析图片内容是否与供应链管理、需求预测、库存优化、调度决策、物流运输、采购管理等主题相关。\n"
                       "2. 如果图片内容与供应链相关（如流程图、数据图表、物流单据、库存照片、运输场景等），请结合图片内容进行专业分析和回答。\n"
                       "3. 如果图片内容与供应链无关（如风景、人物、日常物品等），请正常回答用户的问题，不要强行关联供应链主题。\n"
                       "4. 当用户提出调度需求时，识别并提示用户使用工作流功能。\n"
                       "5. 请根据图片内容和用户问题，提供准确、有用的回答。"
        }
        messages.append(system_prompt)
        
        for msg in history:
            messages.append({
                "role": msg["role"],
                "content": msg["content"],
                "image": msg.get("image"),
            })
        
        messages.append({
            "role": "user",
            "content": current_query,
            "image": image,
        })
        
        return messages
    
    def clear_history(self, session_id: str):
        if session_id in self.conversations:
            del self.conversations[session_id]


# 全局单例
bailian_client = BailianClient()
context_manager = ContextManager()
