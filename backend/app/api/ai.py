"""
AI 智能服务 API - v3.0 企业级记忆架构
集成三层记忆体系：工作记忆 + 短期记忆 + 长期记忆
"""
import uuid
import json
from typing import AsyncGenerator

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from app.models.user import User
from app.schemas.common import ApiResponse
from app.utils.auth import get_current_user
from app.services.ai.agent_orchestrator import orchestrator
from app.services.ai.bailian_client import bailian_client
from app.services.langgraph.workflow import (
    run_workflow,
    get_session_history as get_workflow_session,
    list_sessions as list_workflow_sessions,
    delete_session as delete_workflow_session,
    get_available_tools,
)
from app.services.memory.memory_manager import memory_manager
from app.core.config import settings
from app.core.logger import logger

router = APIRouter()


# ==================== AI 健康检查 ====================

@router.get("/health")
async def ai_health_check():
    """检查 AI 服务是否可用（API 密钥验证）"""
    import asyncio
    try:
        status = await asyncio.to_thread(bailian_client.validate_api_key)
    except Exception as e:
        status = {"valid": False, "message": str(e)}
    return ApiResponse.ok(status)


# ==================== 模型与 Agent 信息 ====================

@router.get("/models")
async def get_models(_: User = Depends(get_current_user)):
    return ApiResponse.ok(orchestrator.get_models())


@router.get("/agents")
async def get_agents(_: User = Depends(get_current_user)):
    return ApiResponse.ok(orchestrator.get_agents())


# ==================== 基础对话 ====================

@router.post("/chat")
async def chat(body: dict, _: User = Depends(get_current_user)):
    """基础对话接口"""
    if body.get("smart"):
        return await smart_chat_internal(body, _)

    model = body.get("model")
    messages = [{"role": "user", "content": body.get("message", "")}]
    if body.get("system_prompt"):
        messages.insert(0, {"role": "system", "content": body["system_prompt"]})
    resp = bailian_client.chat(messages, model=model)
    return ApiResponse.ok(resp)


# ==================== Agent 编排 ====================

@router.post("/agent/{agent_id}")
async def invoke_agent(agent_id: str, body: dict, _: User = Depends(get_current_user)):
    """调用单个 Agent"""
    model = body.get("model")
    query = body.get("query", "")
    result = await orchestrator.invoke_agent(agent_id, model, query)

    # 记录执行经验到长期记忆
    await memory_manager.record_execution(
        session_id=body.get("session_id", ""),
        agent_name=agent_id,
        query=query,
        result=result.get("result", ""),
        duration_ms=result.get("elapsed", 0),
    )

    return ApiResponse.ok(result)


@router.post("/pipeline")
async def run_pipeline(body: dict, _: User = Depends(get_current_user)):
    """Agent 流水线"""
    model = body.get("model")
    query = body.get("query", "")
    result = await orchestrator.run_pipeline(model, query)
    return ApiResponse.ok(result)


@router.post("/parallel")
async def invoke_parallel(body: dict, _: User = Depends(get_current_user)):
    """并行 Agent 调用"""
    model = body.get("model")
    queries = body.get("queries", {})
    result = await orchestrator.invoke_parallel(model, queries)
    return ApiResponse.ok(result)


# ==================== LangGraph 工作流 ====================

@router.post("/workflow/scheduling")
async def run_scheduling_workflow(body: dict, _: User = Depends(get_current_user)):
    """运行调度工作流（工作记忆层）"""
    model = body.get("model")
    query = body.get("query", "")
    session_id = body.get("session_id")
    result = await run_workflow(query, model=model, session_id=session_id)
    return ApiResponse.ok(result)


# ==================== 三层记忆体系 API ====================

@router.get("/memory/summary")
async def get_memory_summary(_: User = Depends(get_current_user)):
    """获取记忆系统完整概览"""
    summary = await memory_manager.get_memory_summary()
    return ApiResponse.ok(summary)


@router.get("/sessions")
async def get_sessions(_: User = Depends(get_current_user)):
    """获取所有会话列表（短期记忆 + 工作记忆）"""
    chat_sessions = await memory_manager.list_sessions()
    workflow_sessions = await list_workflow_sessions()
    return ApiResponse.ok({
        "chat_sessions": chat_sessions,
        "workflow_sessions": workflow_sessions,
    })


@router.get("/sessions/{session_id}")
async def get_session(session_id: str, _: User = Depends(get_current_user)):
    """获取会话详情（含完整历史消息）"""
    session = await memory_manager.get_session(session_id)
    if not session:
        # 尝试工作记忆
        wf_session = await get_workflow_session(session_id)
        if wf_session:
            return ApiResponse.ok(wf_session)
        return ApiResponse.error(message="会话不存在", code=404)
    return ApiResponse.ok(session)


@router.delete("/sessions/{session_id}")
async def remove_session(session_id: str, _: User = Depends(get_current_user)):
    """删除会话（同时清除短期记忆和工作记忆）"""
    await memory_manager.delete_session(session_id)
    await delete_workflow_session(session_id)
    return ApiResponse.ok(None, message="会话已删除")


# ==================== 智能聊天（集成记忆系统）====================

@router.post("/chat/smart")
async def smart_chat_endpoint(body: dict, user: User = Depends(get_current_user)):
    """智能聊天接口 - 集成三层记忆体系"""
    return await smart_chat_internal(body, user)


async def smart_chat_internal(body: dict, user: User):
    """智能聊天核心 - 支持工具调用 + 记忆管理 + 数据库 CRUD"""
    from app.services.langgraph.tools import get_all_tools

    session_id = body.get("session_id") or str(uuid.uuid4())
    query = body.get("message", "")
    model = body.get("model")
    image = body.get("image")

    logger.info(f"[智能聊天] session={session_id}, query={query[:50]}, model={model}")

    if not query.strip() and not image:
        return ApiResponse.error(message="消息内容不能为空")

    try:
        tools = get_all_tools()

        tools_definition = [{
            "name": t.name,
            "description": t.description,
            "args_schema": t.args_schema.schema() if hasattr(t, 'args_schema') else {},
        } for t in tools]

        all_tool_calls = []
        max_rounds = 5

        history = await memory_manager.get_history(session_id)

        messages = [{
            "role": "system",
            "content": (
                "你是 Xuni 供应链智能调度助手，拥有对数据库的完整操作权限。\n\n"
                "## 能力范围\n"
                "1. **数据查询**：库存列表/详情/统计、订单列表/统计、供应商列表\n"
                "2. **入库操作**：stock_in_operation(inv_id, quantity) — 增加库存\n"
                "3. **出库操作**：stock_out_operation(inv_id, quantity) — 减少库存\n"
                "4. **创建订单**：create_order_operation(customer_name, product_name, quantity, warehouse_name, shipping_address, unit_price?, remark?)\n"
                "5. **更新订单**：update_order_status_operation(order_id, new_status) — PENDING/CONFIRMED/SHIPPED/DELIVERED/CANCELLED\n"
                "6. **取消订单**：cancel_order_operation(order_id)\n\n"
                "## 规则\n"
                "- 用户要求查询/增/删/改数据时，必须先调用对应工具执行操作\n"
                "- 工具返回格式为 {success, data, message, total}\n"
                "- 基于工具返回的真实数据总结回答，绝不编造\n"
                "- 如果操作失败(success=false)，向用户说明原因\n"
                "- 纯对话问题可直接回答"
            ),
        }]

        for msg in history:
            messages.append({
                "role": msg["role"],
                "content": msg["content"],
            })

        messages.append({"role": "user", "content": query})

        # 工具调用循环
        for round_idx in range(max_rounds):
            logger.info(f"[智能聊天] 第 {round_idx + 1} 轮")

            response = bailian_client.chat(
                messages=messages,
                model=model,
                temperature=0.1,
                max_tokens=2048,
                tools=tools_definition,
            )

            if not response.get("success"):
                error_msg = response.get("error_message", "") or response.get("content", "未知错误")
                if "InvalidApiKey" in error_msg or "Invalid API-key" in error_msg:
                    error_msg = "API密钥无效，请检查 backend/.env 中的 BAILIAN_API_KEY"
                elif "401" in error_msg:
                    error_msg = "认证失败，请检查API密钥配置"
                logger.error(f"[智能聊天] 调用失败: {error_msg}")
                return ApiResponse.error(message=error_msg)

            content = response.get("content", "")
            tool_calls = response.get("tool_calls", [])
            raw_tool_calls = response.get("raw_tool_calls")  # 原始格式用于回传

            if not tool_calls:
                final_content = content.strip() or "抱歉，我暂时无法回答这个问题。"
                await memory_manager.add_message(session_id, "user", query, image,
                                                  user_id=user.id if user else None)
                await memory_manager.add_message(session_id, "assistant", final_content,
                                                  user_id=user.id if user else None)
                return ApiResponse.ok({
                    "content": final_content,
                    "tool_calls": all_tool_calls,
                    "session_id": session_id,
                })

            # 执行工具调用
            for tc in tool_calls:
                tool_name = tc.get("name")
                arguments = tc.get("arguments", {})
                call_id = tc.get("id", f"call_{tool_name}_{round_idx}")

                if not tool_name:
                    continue

                exec_tool = next((t for t in tools if t.name == tool_name), None)
                if exec_tool is None:
                    tool_result = {"success": False, "message": f"工具 {tool_name} 不存在"}
                else:
                    try:
                        if hasattr(exec_tool, 'ainvoke'):
                            tool_result = await exec_tool.ainvoke(arguments)
                        elif callable(exec_tool):
                            tool_result = await exec_tool(**arguments)
                        else:
                            tool_result = {"success": False, "message": "工具不可调用"}
                    except Exception as e:
                        tool_result = {"success": False, "message": str(e)}

                all_tool_calls.append({
                    "tool": tool_name,
                    "arguments": arguments,
                    "result": tool_result,
                })

                # 构建 assistant tool_call 消息（使用 function 包装格式）
                tc_entry = {
                    "type": "function",
                    "function": {
                        "name": tool_name,
                        "arguments": json.dumps(arguments, ensure_ascii=False),
                    },
                }
                if call_id:
                    tc_entry["id"] = call_id

                # 优先使用原始 raw_tool_calls 回传
                assistant_msg = {
                    "role": "assistant",
                    "content": "",
                    "tool_calls": [tc_entry],
                }
                if raw_tool_calls:
                    assistant_msg["_raw_tool_calls"] = raw_tool_calls

                messages.append(assistant_msg)

                # 构建 tool 结果消息
                messages.append({
                    "role": "tool",
                    "content": json.dumps(tool_result, ensure_ascii=False),
                    "tool_call_id": call_id,
                    "name": tool_name,
                })

        # 最后一轮总结
        final_response = bailian_client.chat(messages, model=model, temperature=0.1, max_tokens=2048)
        final_content = (final_response.get("content", "") or "抱歉，我无法完成此操作。").strip()

        await memory_manager.add_message(session_id, "user", query, image,
                                          user_id=user.id if user else None)
        await memory_manager.add_message(session_id, "assistant", final_content,
                                          user_id=user.id if user else None)

        return ApiResponse.ok({
            "content": final_content,
            "tool_calls": all_tool_calls,
            "session_id": session_id,
        })

    except Exception as e:
        logger.error(f"[智能聊天] 异常: {e}", exc_info=True)
        return ApiResponse.error(message=f"智能聊天异常: {str(e)}")


# ==================== 流式对话 ====================

@router.post("/chat/stream")
async def chat_stream(body: dict, user: User = Depends(get_current_user)):
    """流式聊天 - 支持多模态 + 记忆管理"""
    session_id = body.get("session_id") or str(uuid.uuid4())
    query = body.get("message", "")
    model = body.get("model")
    image = body.get("image")

    logger.info(f"[流式] session={session_id}, query={query[:50]}, image={bool(image)}")

    if not query.strip() and not image:
        raise HTTPException(status_code=400, detail="消息内容不能为空")

    async def generate() -> AsyncGenerator[str, None]:
        # 从记忆系统构建上下文
        messages = await memory_manager.build_context(session_id, query, image)

        try:
            full_response = ""
            chunk_count = 0
            async for chunk in bailian_client.streaming_chat(messages, model=model):
                full_response += chunk
                chunk_count += 1
                yield f"data: {chunk}\n\n"

            logger.info(f"[流式] 完成: chunks={chunk_count}, len={len(full_response)}")

            # 保存到记忆系统
            await memory_manager.add_message(session_id, "user", query, image,
                                              user_id=user.id if user else None)
            await memory_manager.add_message(session_id, "assistant", full_response,
                                              user_id=user.id if user else None)

            yield f"data: [END]\n\n"
        except Exception as e:
            logger.error(f"[流式] 异常: {e}", exc_info=True)
            yield f"data: [ERROR]{str(e)}[/ERROR]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


# ==================== 聊天上下文管理 ====================

@router.post("/chat/context")
async def get_chat_context(body: dict, _: User = Depends(get_current_user)):
    """获取聊天上下文（短期记忆）"""
    session_id = body.get("session_id")
    if not session_id:
        return ApiResponse.ok([])
    history = await memory_manager.get_history(session_id)
    return ApiResponse.ok(history)


@router.delete("/chat/context/{session_id}")
async def clear_chat_context(session_id: str, _: User = Depends(get_current_user)):
    """清除聊天上下文"""
    await memory_manager.clear_history(session_id)
    return ApiResponse.ok(None, message="上下文已清除")


# ==================== 长期记忆：用户偏好 ====================

@router.get("/memory/preferences")
async def get_preferences(user: User = Depends(get_current_user)):
    """获取当前用户的偏好设置"""
    prefs = await memory_manager.get_user_preferences(user.id)
    return ApiResponse.ok(prefs)


@router.put("/memory/preferences")
async def save_preferences(body: dict, user: User = Depends(get_current_user)):
    """保存用户偏好设置"""
    success = await memory_manager.save_user_preferences(user.id, body)
    if success:
        return ApiResponse.ok(None, message="偏好已保存")
    return ApiResponse.error(message="保存失败")


# ==================== 长期记忆：经验检索 ====================

@router.post("/memory/search")
async def search_experiences(body: dict, _: User = Depends(get_current_user)):
    """语义检索历史执行经验"""
    query = body.get("query", "")
    top_k = body.get("top_k", 5)
    if not query:
        return ApiResponse.error(message="查询内容不能为空")
    results = await memory_manager.recall_experiences(query, top_k)
    return ApiResponse.ok(results)


@router.post("/memory/recommend")
async def get_recommendations(body: dict, user: User = Depends(get_current_user)):
    """基于用户画像和历史的个性化推荐"""
    query = body.get("query", "")
    if not query:
        return ApiResponse.error(message="查询内容不能为空")
    recs = await memory_manager.get_recommendations(user.id, query)
    return ApiResponse.ok(recs)


# ==================== 工具系统 ====================

@router.get("/tools")
async def get_tools(_: User = Depends(get_current_user)):
    """获取所有可用工具列表"""
    tools = get_available_tools()
    return ApiResponse.ok(tools)


# ==================== 文件上传与多模态 ====================

@router.post("/upload")
async def upload_file(file: UploadFile = File(...), _: User = Depends(get_current_user)):
    """上传文件"""
    import os
    upload_dir = os.path.join(os.path.dirname(__file__), "..", "..", "uploads")
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, file.filename)
    try:
        with open(file_path, "wb") as f:
            f.write(await file.read())
        return ApiResponse.ok({
            "filename": file.filename,
            "size": os.path.getsize(file_path),
            "url": f"/uploads/{file.filename}",
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"上传失败: {e}")


@router.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...), _: User = Depends(get_current_user)):
    """语音转文字 - qwen3.5-omni-plus 全模态模型"""
    import base64
    audio_data = await file.read()
    audio_base64 = base64.b64encode(audio_data).decode("utf-8")
    ext = file.filename.split(".")[-1].lower() if file.filename else "wav"
    mime_map = {"wav": "audio/wav", "mp3": "audio/mpeg", "m4a": "audio/mp4",
                "ogg": "audio/ogg", "flac": "audio/flac"}
    audio_url = f"data:{mime_map.get(ext, 'audio/wav')};base64,{audio_base64}"
    text = bailian_client.transcribe_audio(audio_url)
    if not text:
        raise HTTPException(status_code=500, detail="语音转文字失败")
    return ApiResponse.ok({"text": text, "filename": file.filename})


@router.post("/analyze-image")
async def analyze_image(file: UploadFile = File(...),
                        prompt: str = "请描述这张图片的内容。",
                        _: User = Depends(get_current_user)):
    """图片解析 - qwen3.5-omni-plus 全模态模型"""
    import base64
    image_data = await file.read()
    image_base64 = base64.b64encode(image_data).decode("utf-8")
    ext = file.filename.split(".")[-1].lower() if file.filename else "jpg"
    mime_map = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png",
                "gif": "image/gif", "webp": "image/webp", "bmp": "image/bmp"}
    image_url = f"data:{mime_map.get(ext, 'image/jpeg')};base64,{image_base64}"
    result = bailian_client.analyze_image(image_url, prompt)
    if not result:
        raise HTTPException(status_code=500, detail="图片解析失败")
    return ApiResponse.ok({"analysis": result, "filename": file.filename})
