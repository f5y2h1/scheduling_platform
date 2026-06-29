"""
检索增强模块
工程化 RAG 流程第二步：多路召回 → 混合检索 → 重排序 → 父文档增强
"""
import re
import math
import asyncio
from dataclasses import dataclass, field
from collections import Counter
from typing import Optional

from app.core.config import settings
from app.core.logger import logger
from app.services.ai.bailian_client import bailian_client
from app.services.rag.qdrant_store import qdrant_store


@dataclass
class RetrievalConfig:
    """检索配置"""
    semantic_top_k: int = 10         # 语义检索召回数
    keyword_top_k: int = 10          # 关键词检索召回数
    final_top_k: int = 5             # 最终返回数
    rerank_strategy: str = "hybrid"  # 重排序策略: hybrid/diversity/llm
    enable_parent_doc: bool = True   # 是否启用父文档增强
    diversity_threshold: float = 0.7 # 多样性阈值（去重相似文档）
    min_score_threshold: float = 0.5 # 最低分数阈值


@dataclass
class RetrievedDocument:
    """检索结果文档"""
    id: str
    score: float
    content: str
    title: str = ""
    category: str = ""
    source: str = ""
    chunk_index: int = 0
    total_chunks: int = 1
    parent_doc_id: str = ""
    chunk_type: str = "paragraph"
    retrieval_type: str = "semantic"  # semantic/keyword/hybrid
    parent_content: str = ""          # 父文档完整内容（增强后）
    metadata: dict = field(default_factory=dict)


class KeywordRetriever:
    """BM25 关键词检索器（简化实现）"""

    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.doc_freqs: dict[str, Counter] = {}  # 文档词频
        self.corpus_freqs: Counter = Counter()   # 全局词频
        self.doc_lens: dict[str, int] = {}       # 文档长度
        self.avgdl: float = 0                    # 平均文档长度
        self.N: int = 0                          # 文档总数

    def tokenize(self, text: str) -> list[str]:
        """分词"""
        # 中文分词：按字符 + 常用词
        text = text.lower()
        # 提取中文字符和英文单词
        tokens = re.findall(r"[a-z]+|[0-9]+|[\u4e00-\u9fa5]", text)
        return tokens

    def build_index(self, documents: list[dict]):
        """构建索引"""
        self.N = len(documents)
        total_len = 0

        for doc in documents:
            doc_id = str(doc.get("id"))
            content = doc.get("payload", {}).get("content", "")
            tokens = self.tokenize(content)

            self.doc_freqs[doc_id] = Counter(tokens)
            self.doc_lens[doc_id] = len(tokens)
            total_len += len(tokens)

            self.corpus_freqs.update(tokens)

        self.avgdl = total_len / self.N if self.N > 0 else 0

    def compute_bm25_score(self, query_tokens: list[str], doc_id: str) -> float:
        """计算 BM25 分数"""
        score = 0
        dl = self.doc_lens.get(doc_id, 0)
        if dl == 0:
            return 0

        doc_tf = self.doc_freqs.get(doc_id, Counter())

        for term in query_tokens:
            tf = doc_tf.get(term, 0)
            if tf == 0:
                continue

            # IDF 计算
            df = self.corpus_freqs.get(term, 0)
            idf = math.log((self.N - df + 0.5) / (df + 0.5) + 1)

            # BM25 公式
            numerator = tf * (self.k1 + 1)
            denominator = tf + self.k1 * (1 - self.b + self.b * dl / self.avgdl)
            score += idf * numerator / denominator

        return score

    def search(self, query: str, documents: list[dict], top_k: int = 10) -> list[dict]:
        """关键词检索"""
        query_tokens = self.tokenize(query)
        self.build_index(documents)

        scores = []
        for doc in documents:
            doc_id = str(doc.get("id"))
            bm25_score = self.compute_bm25_score(query_tokens, doc_id)
            if bm25_score > 0:
                doc_copy = doc.copy()
                doc_copy["keyword_score"] = bm25_score
                scores.append(doc_copy)

        scores.sort(key=lambda x: x.get("keyword_score", 0), reverse=True)
        return scores[:top_k]


class HybridRetriever:
    """混合检索器：语义 + 关键词"""

    def __init__(self, config: RetrievalConfig = None):
        self.config = config or RetrievalConfig()
        self.keyword_retriever = KeywordRetriever()

    async def retrieve(
        self,
        query: str,
        collection: str = settings.KNOWLEDGE_COLLECTION,
    ) -> list[RetrievedDocument]:
        """混合检索"""
        loop = asyncio.get_event_loop()

        # 1. 语义检索
        semantic_task = loop.run_in_executor(
            None,
            lambda: self._semantic_search(query, collection)
        )

        # 2. 关键词检索（需要先获取所有文档用于索引）
        keyword_task = loop.run_in_executor(
            None,
            lambda: self._keyword_search(query, collection)
        )

        semantic_results, keyword_results = await asyncio.gather(
            semantic_task, keyword_task, return_exceptions=True
        )

        if isinstance(semantic_results, Exception):
            logger.error(f"[混合检索] 语义检索失败: {semantic_results}")
            semantic_results = []
        if isinstance(keyword_results, Exception):
            logger.error(f"[混合检索] 关键词检索失败: {keyword_results}")
            keyword_results = []

        # 3. 融合排序
        merged = self._merge_results(semantic_results, keyword_results)

        # 4. 重排序
        reranked = self._rerank(merged, query)

        # 5. 父文档增强
        if self.config.enable_parent_doc:
            reranked = self._parent_doc_enhancement(reranked)

        return reranked[:self.config.final_top_k]

    def _semantic_search(self, query: str, collection: str) -> list[dict]:
        """语义向量检索"""
        query_vector = bailian_client.embed(query)
        results = qdrant_store.search(
            collection,
            query_vector,
            self.config.semantic_top_k,
            settings.SIMILARITY_THRESHOLD,
        )
        for r in results:
            r["semantic_score"] = r.get("score", 0)
        return results

    def _keyword_search(self, query: str, collection: str) -> list[dict]:
        """关键词检索"""
        # 获取足够多的文档用于关键词索引
        all_docs = qdrant_store.scroll(collection, limit=1000)
        if not all_docs:
            return []
        return self.keyword_retriever.search(query, all_docs, self.config.keyword_top_k)

    def _merge_results(
        self,
        semantic_results: list[dict],
        keyword_results: list[dict],
    ) -> list[dict]:
        """融合语义和关键词结果"""
        # 使用 RRF (Reciprocal Rank Fusion) 算法
        rrf_k = 60  # RRF 参数
        merged_scores: dict[str, dict] = {}

        # 处理语义检索结果
        for rank, doc in enumerate(semantic_results):
            doc_id = str(doc.get("id"))
            rrf_score = 1 / (rrf_k + rank + 1)
            if doc_id not in merged_scores:
                merged_scores[doc_id] = doc.copy()
                merged_scores[doc_id]["rrf_score"] = 0
            merged_scores[doc_id]["rrf_score"] += rrf_score

        # 处理关键词检索结果
        for rank, doc in enumerate(keyword_results):
            doc_id = str(doc.get("id"))
            rrf_score = 1 / (rrf_k + rank + 1)
            if doc_id not in merged_scores:
                merged_scores[doc_id] = doc.copy()
                merged_scores[doc_id]["rrf_score"] = 0
            merged_scores[doc_id]["rrf_score"] += rrf_score

        # 按融合分数排序
        merged = list(merged_scores.values())
        merged.sort(key=lambda x: x.get("rrf_score", 0), reverse=True)

        # 计算综合分数
        for doc in merged:
            sem_score = doc.get("semantic_score", 0)
            kw_score = doc.get("keyword_score", 0)
            rrf_score = doc.get("rrf_score", 0)
            # 综合分数：RRF分数归一化后与原始分数加权
            doc["hybrid_score"] = round(
                0.4 * sem_score + 0.3 * kw_score / 10 + 0.3 * rrf_score * 10, 4
            )

        return merged

    def _rerank(self, documents: list[dict], query: str) -> list[RetrievedDocument]:
        """重排序"""
        if self.config.rerank_strategy == "diversity":
            documents = self._diversity_rerank(documents)
        elif self.config.rerank_strategy == "llm":
            documents = self._llm_rerank(documents, query)
        # hybrid 策略已经在 _merge_results 中完成

        # 转换为 RetrievedDocument 对象
        results = []
        for doc in documents:
            payload = doc.get("payload", {})
            score = doc.get("hybrid_score", doc.get("score", 0))

            if score < self.config.min_score_threshold:
                continue

            results.append(RetrievedDocument(
                id=str(doc.get("id")),
                score=score,
                content=payload.get("content", ""),
                title=payload.get("title", ""),
                category=payload.get("category", ""),
                source=payload.get("source", ""),
                chunk_index=payload.get("chunk_index", 0),
                total_chunks=payload.get("total_chunks", 1),
                parent_doc_id=payload.get("parent_doc_id", ""),
                chunk_type=payload.get("chunk_type", "paragraph"),
                retrieval_type=doc.get("retrieval_type", "hybrid"),
                metadata=payload,
            ))

        return results

    def _diversity_rerank(self, documents: list[dict]) -> list[dict]:
        """多样性重排序"""
        if len(documents) <= self.config.final_top_k:
            return documents

        selected = []
        remaining = documents.copy()

        # 选择分数最高的作为起点
        selected.append(remaining.pop(0))

        while len(selected) < self.config.final_top_k and remaining:
            # 选择与已选文档最不相似的
            best_idx = 0
            best_div_score = 0

            for i, doc in enumerate(remaining):
                # 计算与已选文档的平均距离（基于分数差异）
                div_score = sum(
                    abs(doc.get("hybrid_score", 0) - s.get("hybrid_score", 0))
                    for s in selected
                ) / len(selected)

                # 加上文档自身分数权重
                total_score = 0.5 * doc.get("hybrid_score", 0) + 0.5 * div_score

                if total_score > best_div_score:
                    best_div_score = total_score
                    best_idx = i

            selected.append(remaining.pop(best_idx))

        return selected

    def _llm_rerank(self, documents: list[dict], query: str) -> list[dict]:
        """LLM 重排序"""
        if len(documents) <= 3:
            return documents

        # 构建评分 prompt
        doc_summaries = []
        for i, doc in enumerate(documents[:10]):
            content = doc.get("payload", {}).get("content", "")[:150]
            doc_summaries.append(f"[{i}] {doc.get('title', '未知')}: {content}...")

        prompt = f"""请对以下文档与查询「{query}」的相关性进行评分（1-10分）。

文档列表：
{chr(10).join(doc_summaries)}

输出格式要求：
- 每行输出一个评分：序号|分数
- 例如：0|8 表示第0号文档评分8分
- 只输出评分行，不要输出其他内容"""

        try:
            result = bailian_client.simple_chat(
                "你是文档相关性评分助手，请严格按照格式输出评分。",
                prompt
            )

            # 解析评分
            scores = {}
            for line in result.split("\n"):
                parts = re.findall(r"\d+", line)
                if len(parts) >= 2:
                    idx, score = int(parts[0]), int(parts[1])
                    if 0 <= idx < len(documents) and 1 <= score <= 10:
                        scores[idx] = score / 10.0

            # 更新分数并排序
            for i, doc in enumerate(documents):
                if i in scores:
                    doc["llm_score"] = scores[i]
                    doc["hybrid_score"] = scores[i]

            documents.sort(key=lambda x: x.get("hybrid_score", 0), reverse=True)

        except Exception as e:
            logger.warning(f"[LLM重排序] 失败: {e}")

        return documents

    def _parent_doc_enhancement(self, documents: list[RetrievedDocument]) -> list[RetrievedDocument]:
        """父文档增强"""
        for doc in documents:
            # 如果有完整文档内容，直接使用
            full_content = doc.metadata.get("full_content", "")
            if full_content and len(full_content) <= 2000:
                doc.parent_content = full_content
            else:
                # 否则尝试获取相邻块
                doc.parent_content = self._get_adjacent_chunks(doc)

        return documents

    def _get_adjacent_chunks(self, doc: RetrievedDocument) -> str:
        """获取相邻块内容"""
        if not doc.parent_doc_id:
            return doc.content

        # 简化：直接返回当前块内容
        # 完整实现需要从向量库中查询相邻块
        return doc.content


class AdvancedRetriever:
    """高级检索器：支持多策略"""

    def __init__(self, config: RetrievalConfig = None):
        self.config = config or RetrievalConfig()
        self.hybrid_retriever = HybridRetriever(config)

    async def retrieve_with_strategy(
        self,
        query: str,
        strategy: str = "hybrid",
        collection: str = settings.KNOWLEDGE_COLLECTION,
        filters: dict = None,
    ) -> list[RetrievedDocument]:
        """多策略检索"""
        if strategy == "semantic":
            return await self._semantic_only(query, collection)
        elif strategy == "keyword":
            return await self._keyword_only(query, collection)
        elif strategy == "hybrid":
            return await self.hybrid_retriever.retrieve(query, collection)
        elif strategy == "filtered":
            return await self._filtered_search(query, collection, filters)
        else:
            return await self.hybrid_retriever.retrieve(query, collection)

    async def _semantic_only(self, query: str, collection: str) -> list[RetrievedDocument]:
        """纯语义检索"""
        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(
            None,
            lambda: qdrant_store.search(
                collection,
                bailian_client.embed(query),
                self.config.final_top_k,
                settings.SIMILARITY_THRESHOLD,
            )
        )

        return [
            RetrievedDocument(
                id=str(r.get("id")),
                score=r.get("score", 0),
                content=r.get("payload", {}).get("content", ""),
                title=r.get("payload", {}).get("title", ""),
                category=r.get("payload", {}).get("category", ""),
                retrieval_type="semantic",
                metadata=r.get("payload", {}),
            )
            for r in results
        ]

    async def _keyword_only(self, query: str, collection: str) -> list[RetrievedDocument]:
        """纯关键词检索"""
        loop = asyncio.get_event_loop()
        all_docs = await loop.run_in_executor(
            None,
            lambda: qdrant_store.scroll(collection, limit=1000)
        )

        keyword_retriever = KeywordRetriever()
        results = keyword_retriever.search(query, all_docs, self.config.final_top_k)

        return [
            RetrievedDocument(
                id=str(r.get("id")),
                score=r.get("keyword_score", 0) / 10,
                content=r.get("payload", {}).get("content", ""),
                title=r.get("payload", {}).get("title", ""),
                category=r.get("payload", {}).get("category", ""),
                retrieval_type="keyword",
                metadata=r.get("payload", {}),
            )
            for r in results
        ]

    async def _filtered_search(
        self,
        query: str,
        collection: str,
        filters: dict,
    ) -> list[RetrievedDocument]:
        """带过滤条件的检索"""
        loop = asyncio.get_event_loop()

        filter_field = filters.get("field", "category")
        filter_value = filters.get("value", "")

        results = await loop.run_in_executor(
            None,
            lambda: qdrant_store.search_with_filter(
                collection,
                bailian_client.embed(query),
                self.config.final_top_k,
                settings.SIMILARITY_THRESHOLD,
                filter_field=filter_field,
                filter_value=filter_value,
            )
        )

        return [
            RetrievedDocument(
                id=str(r.get("id")),
                score=r.get("score", 0),
                content=r.get("payload", {}).get("content", ""),
                title=r.get("payload", {}).get("title", ""),
                category=r.get("payload", {}).get("category", ""),
                retrieval_type="filtered",
                metadata=r.get("payload", {}),
            )
            for r in results
        ]


# 默认检索器实例
default_config = RetrievalConfig()
advanced_retriever = AdvancedRetriever(default_config)
hybrid_retriever = HybridRetriever(default_config)