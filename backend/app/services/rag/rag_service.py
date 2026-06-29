"""
RAG 检索增强生成服务 - 工程化版本
完整流程：问题理解 → 多路召回 → 重排序 → 上下文构建 → 增强生成 → 答案引用
"""
import time
import asyncio
from dataclasses import dataclass, field
from typing import Optional

from app.core.config import settings
from app.core.logger import logger
from app.services.ai.bailian_client import bailian_client
from app.services.rag.retriever import advanced_retriever, RetrievedDocument, RetrievalConfig
from app.services.rag.knowledge_base import kb_service


# ===================== 提示词模板 =====================

RAG_PROMPT_TEMPLATE = """你是一位专业的供应链调度智能助手，具备深厚的供应链管理、库存优化、调度决策等专业知识。

## 你的任务
基于提供的知识库参考内容，回答用户的问题。请遵循以下原则：

1. **准确性优先**：优先使用知识库中的确切信息，如果知识库内容与问题相关度高，请直接引用。
2. **补充扩展**：如果知识库信息不足，可以结合专业知识进行补充，但要明确标注"补充说明"。
3. **诚实原则**：如果问题超出你的专业领域或知识库完全没有相关信息，请诚实告知用户。
4. **引用规范**：在回答中使用 [来源N] 标记引用的具体来源，便于用户追溯。

## 知识库参考内容
{context}

## 用户问题
{query}

## 回答要求
- 结构清晰，使用分段或列表组织答案
- 每个关键论点标注引用来源 [来源N]
- 如果有计算公式，请完整展示
- 如果有决策建议，请说明依据
"""

NO_CONTEXT_PROMPT = """你是一位专业的供应链调度智能助手。

用户问题：{query}

知识库中没有找到直接相关的参考内容。请基于你的专业知识回答，并在回答开头说明：
"以下回答基于专业知识，建议查阅具体业务文档获取更准确信息。"
"""


@dataclass
class RAGResponse:
    """RAG 响应结果"""
    query: str = ""
    answer: str = ""
    sources: list[dict] = field(default_factory=list)
    retrieval_count: int = 0
    retrieval_time_ms: float = 0
    generation_time_ms: float = 0
    total_time_ms: float = 0
    confidence: float = 0.0  # 置信度评分
    retrieval_strategy: str = "hybrid"
    has_knowledge_support: bool = False


@dataclass
class SourceReference:
    """来源引用"""
    source_id: int
    title: str
    category: str
    content_snippet: str  # 内容片段（用于展示）
    relevance_score: float
    retrieval_type: str


class RAGService:
    """工程化 RAG 服务"""

    def __init__(self):
        self.retriever = advanced_retriever

    async def rag_query(
        self,
        query: str,
        model: str | None = None,
        top_k: int = 5,
        strategy: str = "hybrid",
        filters: dict = None,
    ) -> RAGResponse:
        """
        标准 RAG 流程
        1. 问题预处理
        2. 多路召回
        3. 重排序
        4. 上下文构建
        5. 增强生成
        6. 答案后处理
        """
        t0 = time.time()

        # Step 1: 问题预处理（可选：问题扩展、意图识别）
        processed_query = self._preprocess_query(query)

        # Step 2-3: 多路召回 + 重排序
        config = RetrievalConfig(final_top_k=top_k)
        self.retriever.config = config

        documents = await self.retriever.retrieve_with_strategy(
            processed_query,
            strategy=strategy,
            filters=filters,
        )
        t1 = time.time()

        # Step 4: 上下文构建
        context, source_refs = self._build_context_with_sources(documents)

        # Step 5: 增强生成
        answer = await self._generate_answer(
            query=query,
            context=context,
            model=model,
            has_context=len(documents) > 0,
        )
        t2 = time.time()

        # Step 6: 答案后处理
        processed_answer, confidence = self._postprocess_answer(
            answer=answer,
            documents=documents,
            source_refs=source_refs,
        )

        # 构建响应
        sources = [
            {
                "id": i,
                "title": ref.title,
                "category": ref.category,
                "score": round(ref.relevance_score, 3),
                "snippet": ref.content_snippet[:200],
                "type": ref.retrieval_type,
            }
            for i, ref in enumerate(source_refs)
        ]

        return RAGResponse(
            query=query,
            answer=processed_answer,
            sources=sources,
            retrieval_count=len(documents),
            retrieval_time_ms=round((t1 - t0) * 1000),
            generation_time_ms=round((t2 - t1) * 1000),
            total_time_ms=round((t2 - t0) * 1000),
            confidence=confidence,
            retrieval_strategy=strategy,
            has_knowledge_support=len(documents) > 0,
        )

    def _preprocess_query(self, query: str) -> str:
        """问题预处理"""
        # 去除多余空白
        query = query.strip()
        # 可选：问题扩展（添加同义词、相关词）
        # 简化版本：直接返回原问题
        return query

    def _build_context_with_sources(
        self,
        documents: list[RetrievedDocument],
    ) -> tuple[str, list[SourceReference]]:
        """构建上下文并生成来源引用"""
        if not documents:
            return "", []

        context_parts = []
        source_refs = []

        for i, doc in enumerate(documents):
            # 上下文构建
            context_parts.append(
                f"### 来源 [{i + 1}] (相关度: {doc.score:.2f})\n"
                f"**标题**: {doc.title}\n"
                f"**分类**: {doc.category}\n"
                f"**内容**: {doc.content}\n"
            )

            # 来源引用
            source_refs.append(SourceReference(
                source_id=i + 1,
                title=doc.title,
                category=doc.category,
                content_snippet=doc.content[:300],
                relevance_score=doc.score,
                retrieval_type=doc.retrieval_type,
            ))

        context = "\n---\n".join(context_parts)
        return context, source_refs

    async def _generate_answer(
        self,
        query: str,
        context: str,
        model: str | None,
        has_context: bool,
    ) -> str:
        """生成答案"""
        loop = asyncio.get_event_loop()

        if has_context:
            prompt = RAG_PROMPT_TEMPLATE.format(context=context, query=query)
            system_prompt = "你是一位专业的供应链调度智能助手，请严格按照要求回答。"
        else:
            prompt = NO_CONTEXT_PROMPT.format(query=query)
            system_prompt = "你是一位专业的供应链调度智能助手。"

        answer = await loop.run_in_executor(
            None,
            lambda: bailian_client.simple_chat(system_prompt, prompt, model=model)
        )

        return answer

    def _postprocess_answer(
        self,
        answer: str,
        documents: list[RetrievedDocument],
        source_refs: list[SourceReference],
    ) -> tuple[str, float]:
        """
        答案后处理
        1. 引用标记验证
        2. 置信度计算
        """
        # 验证引用标记
        cited_sources = set()
        for ref in source_refs:
            pattern = f"[来源{ref.source_id}]"
            if pattern in answer:
                cited_sources.add(ref.source_id)

        # 计算置信度
        confidence = self._compute_confidence(
            answer=answer,
            documents=documents,
            cited_sources=cited_sources,
        )

        # 如果答案中没有引用标记但有关联文档，添加引用提示
        if documents and not cited_sources:
            answer = self._add_source_hints(answer, source_refs)

        return answer, confidence

    def _compute_confidence(
        self,
        answer: str,
        documents: list[RetrievedDocument],
        cited_sources: set[int],
    ) -> float:
        """计算置信度"""
        if not documents:
            return 0.3  # 无知识库支持，低置信度

        # 基础置信度：检索文档的平均相关性
        avg_relevance = sum(d.score for d in documents) / len(documents)

        # 引用覆盖率：实际引用的文档比例
        citation_ratio = len(cited_sources) / len(documents) if documents else 0

        # 答案完整性：答案长度是否足够
        length_score = min(len(answer) / 200, 1.0)

        # 综合置信度
        confidence = (
            0.4 * avg_relevance +
            0.3 * citation_ratio +
            0.2 * length_score +
            0.1 * (1 if documents else 0)
        )

        return round(min(confidence, 1.0), 2)

    def _add_source_hints(
        self,
        answer: str,
        source_refs: list[SourceReference],
    ) -> str:
        """添加来源提示"""
        if not source_refs:
            return answer

        hints = "\n\n---\n**参考来源**:\n"
        for ref in source_refs[:3]:
            hints += f"- [{ref.title}] (分类: {ref.category}, 相关度: {ref.relevance_score:.0%})\n"

        return answer + hints

    # ===================== 高级功能 =====================

    async def query_with_intent(
        self,
        query: str,
        intent: str = "general",
        model: str | None = None,
    ) -> RAGResponse:
        """带意图识别的查询"""
        # 根据意图选择检索策略
        strategy_map = {
            "general": "hybrid",
            "formula": "keyword",      # 公式查询适合关键词检索
            "decision": "hybrid",
            "rule": "keyword",         # 规则查询适合关键词检索
            "history": "semantic",     # 历史决策适合语义检索
        }
        strategy = strategy_map.get(intent, "hybrid")

        return await self.rag_query(query, model, strategy=strategy)

    async def multi_turn_query(
        self,
        queries: list[str],
        model: str | None = None,
    ) -> list[RAGResponse]:
        """多轮连续查询"""
        results = []
        for query in queries:
            result = await self.rag_query(query, model)
            results.append(result)
        return results

    async def explain_answer(
        self,
        query: str,
        answer: str,
        sources: list[dict],
    ) -> str:
        """答案解释生成"""
        explanation_prompt = f"""请解释以下答案的推导过程和依据：

问题：{query}
答案：{answer}
参考来源数：{len(sources)}

请说明：
1. 答案的主要依据是哪些来源
2. 如何从参考内容得出结论
3. 是否有补充的专业知识"""

        return bailian_client.simple_chat(
            "你是答案解释助手。",
            explanation_prompt,
        )


# 全局实例
rag_service = RAGService()