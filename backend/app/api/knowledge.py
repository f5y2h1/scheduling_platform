"""知识库管理 API - 工程化版本"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from app.models.user import User
from app.schemas.common import ApiResponse
from app.utils.auth import get_current_user
from app.services.ai.bailian_client import bailian_client
from app.services.rag.qdrant_store import qdrant_store
from app.services.rag.knowledge_base import kb_service
from app.services.rag.rag_service import rag_service
from app.services.rag.retriever import advanced_retriever, RetrievalConfig
from app.core.logger import logger

router = APIRouter()


# ===================== 统计信息 =====================
@router.get("/stats")
async def get_stats(_: User = Depends(get_current_user)):
    """获取知识库统计信息"""
    stats = kb_service.get_stats()
    return ApiResponse.ok(stats)


@router.get("/collections")
async def list_collections(_: User = Depends(get_current_user)):
    """列出所有集合"""
    return ApiResponse.ok(qdrant_store.list_collections())


# ===================== 文档管理（工程化版本） =====================
@router.get("/documents")
async def list_documents(
    category: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    _: User = Depends(get_current_user),
):
    """列出所有文档（按doc_id去重）"""
    documents = kb_service.list_documents(category)
    total = len(documents)
    start = (page - 1) * page_size
    end = start + page_size
    return ApiResponse.ok({
        "documents": documents[start:end],
        "total": total,
        "page": page,
        "page_size": page_size,
    })


@router.post("/documents")
async def add_document(body: dict, _: User = Depends(get_current_user)):
    """添加文档（简化接口）"""
    result = kb_service.add_document(
        title=body.get("title", ""),
        content=body.get("content", ""),
        category=body.get("category", "通用"),
        tags=body.get("tags", []),
        source=body.get("source", ""),
    )
    return ApiResponse.ok(message=result)


@router.post("/documents/advanced")
async def add_document_advanced(body: dict, _: User = Depends(get_current_user)):
    """高级文档入库（工程化流程）"""
    result = kb_service.add_document_advanced(
        title=body.get("title", ""),
        content=body.get("content", ""),
        category=body.get("category", "通用"),
        tags=body.get("tags", []),
        source=body.get("source", ""),
        doc_id=body.get("doc_id", ""),
    )
    return ApiResponse.ok(result, message=result.get("message", "入库成功"))


@router.post("/documents/batch")
async def add_documents(body: dict, _: User = Depends(get_current_user)):
    """批量添加文档"""
    documents = body.get("documents", [])
    collection = body.get("collection", "xuni_knowledge_base")
    count = kb_service.add_documents(collection, documents)
    return ApiResponse.ok({"count": count}, message=f"批量入库: {count} 篇")


@router.get("/documents/{doc_id}/chunks")
async def get_document_chunks(doc_id: str, _: User = Depends(get_current_user)):
    """获取文档的所有块"""
    chunks = kb_service.get_document_chunks(doc_id)
    return ApiResponse.ok({
        "doc_id": doc_id,
        "chunks": chunks,
        "count": len(chunks),
    })


@router.delete("/documents/{doc_id}")
async def delete_document(doc_id: str, _: User = Depends(get_current_user)):
    """删除文档（删除所有关联块）"""
    count = kb_service.delete_document(doc_id)
    return ApiResponse.ok({"deleted": count}, message=f"已删除 {count} 个块")


@router.post("/init-default")
async def init_default():
    """初始化默认知识库"""
    await kb_service.init_defaults()
    return ApiResponse.ok(message="默认知识库初始化完成")


# ===================== 检索（工程化版本） =====================
@router.post("/search")
async def semantic_search(body: dict, _: User = Depends(get_current_user)):
    """语义检索"""
    query = body.get("query", "")
    top_k = body.get("top_k", 5)
    results = kb_service.semantic_search(query, top_k)
    return ApiResponse.ok(results)


@router.post("/search/hybrid")
async def hybrid_search(body: dict, _: User = Depends(get_current_user)):
    """混合检索"""
    query = body.get("query", "")
    top_k = body.get("top_k", 5)
    results = kb_service.hybrid_search(query, top_k)
    return ApiResponse.ok(results)


@router.post("/search/category")
async def category_search(body: dict, _: User = Depends(get_current_user)):
    """分类检索"""
    query = body.get("query", "")
    category = body.get("category", "")
    top_k = body.get("top_k", 5)
    results = kb_service.category_search(query, category, top_k)
    return ApiResponse.ok(results)


@router.post("/search/quality")
async def quality_search(body: dict, _: User = Depends(get_current_user)):
    """按质量评分检索"""
    query = body.get("query", "")
    min_quality = body.get("min_quality", 0.7)
    top_k = body.get("top_k", 5)
    results = kb_service.search_by_quality(query, min_quality, top_k)
    return ApiResponse.ok(results)


@router.post("/search/advanced")
async def advanced_search(body: dict, _: User = Depends(get_current_user)):
    """高级检索（使用混合检索器）"""
    query = body.get("query", "")
    strategy = body.get("strategy", "hybrid")  # hybrid/semantic/keyword/filtered
    top_k = body.get("top_k", 5)
    filters = body.get("filters")  # {"field": "category", "value": "库存策略"}

    config = RetrievalConfig(final_top_k=top_k)
    documents = await advanced_retriever.retrieve_with_strategy(
        query,
        strategy=strategy,
        filters=filters,
    )

    results = [
        {
            "id": doc.id,
            "score": doc.score,
            "title": doc.title,
            "category": doc.category,
            "content": doc.content[:500],
            "retrieval_type": doc.retrieval_type,
            "chunk_type": doc.chunk_type,
            "quality_score": doc.metadata.get("quality_score", 1.0),
        }
        for doc in documents
    ]

    return ApiResponse.ok({
        "query": query,
        "strategy": strategy,
        "results": results,
        "count": len(results),
    })


# ===================== 决策历史 =====================
@router.post("/decisions")
async def record_decision(body: dict, _: User = Depends(get_current_user)):
    """记录AI决策"""
    kb_service.record_decision(
        scenario=body.get("scenario", ""),
        decision=body.get("decision", ""),
        result=body.get("result", ""),
        metadata=body.get("metadata"),
    )
    return ApiResponse.ok(message="决策已记录")


@router.post("/decisions/search")
async def search_decisions(body: dict, _: User = Depends(get_current_user)):
    """检索相似历史决策"""
    scenario = body.get("scenario", "")
    top_k = body.get("top_k", 3)
    results = kb_service.recall_decisions(scenario, top_k)
    return ApiResponse.ok(results)


# ===================== 业务规则 =====================
@router.post("/rules")
async def add_rule(body: dict, _: User = Depends(get_current_user)):
    """录入业务规则"""
    kb_service.add_rule(
        rule_name=body.get("rule_name", ""),
        rule_content=body.get("rule_content", ""),
        rule_type=body.get("rule_type", ""),
        priority=body.get("priority", "中"),
    )
    return ApiResponse.ok(message="规则已录入")


@router.post("/rules/search")
async def search_rules(body: dict, _: User = Depends(get_current_user)):
    """检索相关业务规则"""
    query = body.get("query", "")
    top_k = body.get("top_k", 5)
    results = kb_service.recall_rules(query, top_k)
    return ApiResponse.ok(results)


# ===================== RAG问答（工程化版本） =====================
@router.post("/rag/query")
async def rag_query(body: dict, _: User = Depends(get_current_user)):
    """标准RAG问答"""
    query = body.get("query", "")
    model = body.get("model")
    top_k = body.get("top_k", 5)
    strategy = body.get("strategy", "hybrid")

    response = await rag_service.rag_query(
        query=query,
        model=model,
        top_k=top_k,
        strategy=strategy,
    )

    return ApiResponse.ok({
        "query": response.query,
        "answer": response.answer,
        "sources": response.sources,
        "retrieval_count": response.retrieval_count,
        "retrieval_time_ms": response.retrieval_time_ms,
        "generation_time_ms": response.generation_time_ms,
        "total_time_ms": response.total_time_ms,
        "confidence": response.confidence,
        "retrieval_strategy": response.retrieval_strategy,
        "has_knowledge_support": response.has_knowledge_support,
    })


@router.post("/rag/query-with-intent")
async def rag_query_with_intent(body: dict, _: User = Depends(get_current_user)):
    """带意图识别的RAG问答"""
    query = body.get("query", "")
    intent = body.get("intent", "general")  # general/formula/decision/rule/history
    model = body.get("model")

    response = await rag_service.query_with_intent(
        query=query,
        intent=intent,
        model=model,
    )

    return ApiResponse.ok({
        "query": response.query,
        "answer": response.answer,
        "sources": response.sources,
        "intent": intent,
        "confidence": response.confidence,
        "total_time_ms": response.total_time_ms,
    })


@router.post("/rag/explain")
async def rag_explain(body: dict, _: User = Depends(get_current_user)):
    """答案解释生成"""
    query = body.get("query", "")
    answer = body.get("answer", "")
    sources = body.get("sources", [])

    explanation = await rag_service.explain_answer(query, answer, sources)
    return ApiResponse.ok({"explanation": explanation})


@router.post("/rag/rerank")
async def rerank(body: dict, _: User = Depends(get_current_user)):
    """重排序（兼容旧接口）"""
    query = body.get("query", "")
    documents = body.get("documents", [])
    top_k = body.get("top_k", 3)
    # 使用 advanced_retriever 的 LLM 重排序
    results = await advanced_retriever._llm_rerank(documents, query)
    return ApiResponse.ok(results[:top_k])


# ===================== Embedding =====================
@router.post("/embed")
async def embed_text(body: dict, _: User = Depends(get_current_user)):
    """文本向量化"""
    text = body.get("text")
    texts = body.get("texts")
    if text:
        vector = bailian_client.embed(text)
        return ApiResponse.ok({"vector": vector, "dimension": len(vector)})
    elif texts:
        vectors = bailian_client.embed_batch(texts)
        return ApiResponse.ok({"vectors": vectors, "count": len(vectors)})
    raise HTTPException(status_code=400, detail="请提供text或texts参数")


# ===================== 健康检查 =====================
@router.get("/health")
async def health_check():
    """知识库健康检查"""
    try:
        collections = qdrant_store.list_collections()
        total_count = sum(qdrant_store.get_count(c) for c in collections)
        return ApiResponse.ok({
            "status": "healthy",
            "collections": len(collections),
            "total_vectors": total_count,
            "backend": "qdrant",
        })
    except Exception as e:
        logger.error(f"[健康检查] 失败: {e}")
        return ApiResponse.ok({
            "status": "unhealthy",
            "error": str(e),
        })