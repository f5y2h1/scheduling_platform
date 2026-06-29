"""
Qdrant 向量数据库服务
封装 Qdrant REST API
"""
import uuid
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels
from qdrant_client.http.exceptions import UnexpectedResponse

from app.core.config import settings
from app.core.logger import logger


class QdrantVectorStore:
    """Qdrant 向量存储与检索"""

    def __init__(self):
        self.client = QdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_REST_PORT)

    def ensure_collection(self, name: str):
        """确保集合存在"""
        try:
            self.client.get_collection(name)
        except (UnexpectedResponse, Exception):
            logger.info(f"创建集合: {name}")
            self.client.create_collection(
                collection_name=name,
                vectors_config=qmodels.VectorParams(
                    size=settings.VECTOR_SIZE,
                    distance=qmodels.Distance.COSINE,
                ),
            )

    def upsert(self, collection: str, point_id: str, vector: list[float], payload: dict):
        """写入单条"""
        self.ensure_collection(collection)
        self.client.upsert(
            collection_name=collection,
            points=[qmodels.PointStruct(id=point_id, vector=vector, payload=payload)],
            wait=True,
        )

    def upsert_batch(self, collection: str, points: list[dict]):
        """批量写入"""
        self.ensure_collection(collection)
        pts = []
        for p in points:
            pts.append(qmodels.PointStruct(
                id=p["id"], vector=p["vector"], payload=p.get("payload", {}),
            ))
        self.client.upsert(collection_name=collection, points=pts, wait=True)
        logger.debug(f"批量写入: collection={collection}, count={len(pts)}")

    def search(
        self, collection: str, query_vector: list[float],
        top_k: int = 5, score_threshold: float = 0.7,
    ) -> list[dict]:
        """语义向量检索"""
        self.ensure_collection(collection)
        results = self.client.search(
            collection_name=collection,
            query_vector=query_vector,
            limit=top_k,
            score_threshold=score_threshold,
            with_payload=True,
        )
        return [{"id": r.id, "score": r.score, "payload": r.payload or {}} for r in results]

    def search_with_filter(
        self, collection: str, query_vector: list[float],
        top_k: int = 5, score_threshold: float = 0.7, filter_field: str = "", filter_value: str = "",
    ) -> list[dict]:
        """带过滤的向量检索"""
        self.ensure_collection(collection)
        qfilter = qmodels.Filter(
            must=[qmodels.FieldCondition(key=filter_field, match=qmodels.MatchValue(value=filter_value))]
        )
        results = self.client.search(
            collection_name=collection,
            query_vector=query_vector,
            limit=top_k,
            score_threshold=score_threshold,
            query_filter=qfilter,
            with_payload=True,
        )
        return [{"id": r.id, "score": r.score, "payload": r.payload or {}} for r in results]

    def delete_point(self, collection: str, point_id: str):
        self.client.delete(collection_name=collection, points_selector=[point_id])

    def delete_by_filter(self, collection: str, filter_field: str, filter_value: str) -> int:
        """按过滤器删除点"""
        self.ensure_collection(collection)
        qfilter = qmodels.Filter(
            must=[qmodels.FieldCondition(key=filter_field, match=qmodels.MatchValue(value=filter_value))]
        )
        # 先获取数量
        count_before = self.get_count(collection)
        self.client.delete(collection_name=collection, points_selector=qmodels.FilterSelector(filter=qfilter))
        count_after = self.get_count(collection)
        return count_before - count_after

    def scroll(self, collection: str, limit: int = 100) -> list[dict]:
        """滚动获取所有点"""
        self.ensure_collection(collection)
        try:
            results, _ = self.client.scroll(
                collection_name=collection,
                limit=limit,
                with_payload=True,
                with_vectors=False,
            )
            return [{"id": r.id, "payload": r.payload or {}} for r in results]
        except Exception as e:
            logger.error(f"[scroll] 失败: {e}")
            return []

    def scroll_with_filter(
        self,
        collection: str,
        filter_field: str,
        filter_value: str,
        limit: int = 100,
    ) -> list[dict]:
        """带过滤器的滚动获取"""
        self.ensure_collection(collection)
        qfilter = qmodels.Filter(
            must=[qmodels.FieldCondition(key=filter_field, match=qmodels.MatchValue(value=filter_value))]
        )
        try:
            results, _ = self.client.scroll(
                collection_name=collection,
                limit=limit,
                with_payload=True,
                with_vectors=False,
                query_filter=qfilter,
            )
            return [{"id": r.id, "payload": r.payload or {}} for r in results]
        except Exception as e:
            logger.error(f"[scroll_with_filter] 失败: {e}")
            return []

    def get_count(self, collection: str) -> int:
        try:
            info = self.client.count(collection_name=collection)
            return info.count
        except Exception:
            return 0

    def list_collections(self) -> list[str]:
        try:
            cols = self.client.get_collections()
            return [c.name for c in cols.collections]
        except Exception:
            return []


# 全局单例
qdrant_store = QdrantVectorStore()
