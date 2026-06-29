"""AI 智能服务 API"""
import uuid
from typing import AsyncGenerator

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from app.models.user import User
from app.schemas.common import ApiResponse
from app.utils.auth import get_current_user
from app.services.ai.agent_orchestrator import orchestrator
from app.services.ai.bailian_client import bailian_client, context_manager
from app.services.langgraph.workflow import (
    run_workflow,
    get_session_history,
    list_sessions,
    delete_session,
    get_available_tools,
)

router = APIRouter()


@router.get("/models")
async def get_models(_: User = Depends(get_current_user)):
    return ApiResponse.ok(orchestrator.get_models())


@router.get("/agents")
async def get_agents(_: User = Depends(get_current_user)):
    return ApiResponse.ok(orchestrator.get_agents())


@router.post("/chat")
async def chat(body: dict, _: User = Depends(get_current_user)):
    from app.services.ai.bailian_client import bailian_client
    model = body.get("model")
    messages = [{"role": "user", "content": body.get("message", "")}]
    if body.get("system_prompt"):
        messages.insert(0, {"role": "system", "content": body["system_prompt"]})
    resp = bailian_client.chat(messages, model=model)
    return ApiResponse.ok(resp)


@router.post("/agent/{agent_id}")
async def invoke_agent(agent_id: str, body: dict, _: User = Depends(get_current_user)):
    model = body.get("model")
    query = body.get("query", "")
    result = await orchestrator.invoke_agent(agent_id, model, query)
    return ApiResponse.ok(result)


@router.post("/pipeline")
async def run_pipeline(body: dict, _: User = Depends(get_current_user)):
    model = body.get("model")
    query = body.get("query", "")
    result = await orchestrator.run_pipeline(model, query)
    return ApiResponse.ok(result)


@router.post("/parallel")
async def invoke_parallel(body: dict, _: User = Depends(get_current_user)):
    model = body.get("model")
    queries = body.get("queries", {})
    result = await orchestrator.invoke_parallel(model, queries)
    return ApiResponse.ok(result)


@router.post("/workflow/scheduling")
async def run_scheduling_workflow(body: dict, _: User = Depends(get_current_user)):
    model = body.get("model")
    query = body.get("query", "")
    session_id = body.get("session_id")
    result = await run_workflow(query, model=model, session_id=session_id)
    return ApiResponse.ok(result)


# ==================== 记忆系统 API ====================

@router.get("/sessions")
async def get_sessions(_: User = Depends(get_current_user)):
    """获取所有会话列表"""
    sessions = await list_sessions()
    return ApiResponse.ok(sessions)


@router.get("/sessions/{session_id}")
async def get_session(session_id: str, _: User = Depends(get_current_user)):
    """获取指定会话历史"""
    history = await get_session_history(session_id)
    if not history:
        return ApiResponse.error(message="会话不存在", code=404)
    return ApiResponse.ok(history)


@router.delete("/sessions/{session_id}")
async def remove_session(session_id: str, _: User = Depends(get_current_user)):
    """删除会话记录"""
    success = await delete_session(session_id)
    if not success:
        return ApiResponse.error(message="删除失败", code=500)
    return ApiResponse.ok(None, message="删除成功")


# ==================== 工具系统 API ====================

@router.get("/tools")
async def get_tools(_: User = Depends(get_current_user)):
    """获取所有可用工具列表"""
    tools = get_available_tools()
    return ApiResponse.ok(tools)


# ==================== 聊天接口 API ====================

@router.post("/chat/stream")
async def chat_stream(body: dict, _: User = Depends(get_current_user)):
    """流式聊天接口 - 支持多模态（文本+图片）"""
    from app.core.logger import logger

    session_id = body.get("session_id") or str(uuid.uuid4())
    query = body.get("message", "")
    model = body.get("model")
    image = body.get("image")

    logger.info(f"[聊天流式] 收到请求: session_id={session_id}, query={query[:50]}, model={model}, has_image={bool(image)}")

    if not query.strip() and not image:
        raise HTTPException(status_code=400, detail="消息内容不能为空")

    async def generate() -> AsyncGenerator[str, None]:
        messages = context_manager.build_messages(session_id, query, image)

        logger.info(f"[聊天流式] 构建消息完成: messages={len(messages)}条")

        try:
            full_response = ""
            chunk_count = 0

            async for chunk in bailian_client.streaming_chat(messages, model=model):
                full_response += chunk
                chunk_count += 1
                yield f"data: {chunk}\n\n"

            logger.info(f"[聊天流式] 生成完成: total_chunks={chunk_count}, total_len={len(full_response)}")

            context_manager.add_message(session_id, "user", query, image)
            context_manager.add_message(session_id, "assistant", full_response)

            yield f"data: [END]\n\n"
        except Exception as e:
            logger.error(f"[聊天流式] 生成异常: {type(e).__name__}: {str(e)}", exc_info=True)
            yield f"data: [ERROR]{str(e)}[/ERROR]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


@router.post("/chat/context")
async def get_chat_context(body: dict, _: User = Depends(get_current_user)):
    """获取聊天上下文"""
    session_id = body.get("session_id")
    if not session_id:
        return ApiResponse.ok([])
    
    history = context_manager.get_history(session_id)
    return ApiResponse.ok(history)


@router.delete("/chat/context/{session_id}")
async def clear_chat_context(session_id: str, _: User = Depends(get_current_user)):
    """清除聊天上下文"""
    context_manager.clear_history(session_id)
    return ApiResponse.ok(None, message="上下文已清除")


# ==================== 文件上传 API ====================

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
        raise HTTPException(status_code=500, detail=f"文件上传失败: {str(e)}")


# ==================== 多模态 API ====================

@router.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...), _: User = Depends(get_current_user)):
    """
    语音转文字 - 使用 qwen3.5-omni-plus 全模态模型
    支持 wav/mp3/m4a 等音频格式
    """
    import base64

    # 读取音频文件并转为 base64
    audio_data = await file.read()
    audio_base64 = base64.b64encode(audio_data).decode("utf-8")

    # 根据文件扩展名确定 MIME 类型
    ext = file.filename.split(".")[-1].lower() if file.filename else "wav"
    mime_types = {
        "wav": "audio/wav",
        "mp3": "audio/mpeg",
        "m4a": "audio/mp4",
        "ogg": "audio/ogg",
        "flac": "audio/flac",
    }
    mime_type = mime_types.get(ext, "audio/wav")
    audio_url = f"data:{mime_type};base64,{audio_base64}"

    # 调用多模态模型进行语音转文字
    text = bailian_client.transcribe_audio(audio_url)

    if not text:
        raise HTTPException(status_code=500, detail="语音转文字失败")

    return ApiResponse.ok({
        "text": text,
        "filename": file.filename,
    })


@router.post("/analyze-image")
async def analyze_image(file: UploadFile = File(...), prompt: str = "请描述这张图片的内容。", _: User = Depends(get_current_user)):
    """
    图片解析 - 使用 qwen3.5-omni-plus 全模态模型
    支持 jpg/png/gif 等图片格式
    """
    import base64

    # 读取图片文件并转为 base64
    image_data = await file.read()
    image_base64 = base64.b64encode(image_data).decode("utf-8")

    # 根据文件扩展名确定 MIME 类型
    ext = file.filename.split(".")[-1].lower() if file.filename else "jpg"
    mime_types = {
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "png": "image/png",
        "gif": "image/gif",
        "webp": "image/webp",
        "bmp": "image/bmp",
    }
    mime_type = mime_types.get(ext, "image/jpeg")
    image_url = f"data:{mime_type};base64,{image_base64}"

    # 调用多模态模型进行图片解析
    result = bailian_client.analyze_image(image_url, prompt)

    if not result:
        raise HTTPException(status_code=500, detail="图片解析失败")

    return ApiResponse.ok({
        "analysis": result,
        "filename": file.filename,
    })
