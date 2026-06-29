"""
知识库管理服务 - 工程化版本
文档管理 → 智能分块 → 向量化 → Qdrant存储 → 多策略检索
"""
import uuid
from datetime import datetime

from app.core.config import settings
from app.core.logger import logger
from app.services.ai.bailian_client import bailian_client
from app.services.rag.qdrant_store import qdrant_store
from app.services.rag.text_processor import text_processor, TextChunk, ChunkConfig


class KnowledgeBaseService:
    """知识库 CRUD + 检索"""

    COL_KNOWLEDGE = settings.KNOWLEDGE_COLLECTION
    COL_DECISIONS = settings.DECISION_COLLECTION
    COL_RULES = settings.RULES_COLLECTION

    # ===================== 文档管理（工程化版本） =====================

    def add_document_advanced(
        self,
        title: str,
        content: str,
        category: str = "通用",
        tags: list[str] | None = None,
        source: str = "",
        doc_id: str = "",
        chunk_config: ChunkConfig = None,
    ) -> dict:
        """
        高级文档入库（工程化流程）
        1. 智能分块（使用 text_processor）
        2. 向量化（批量处理）
        3. 元数据增强
        4. 入库存储
        """
        doc_id = doc_id or f"doc-{uuid.uuid4().hex[:12]}"

        # Step 1: 智能分块
        config = chunk_config or ChunkConfig()
        chunks = text_processor.process_document(
            content=content,
            doc_id=doc_id,
            title=title,
            metadata={
                "category": category,
                "tags": ",".join(tags) if tags else "",
                "source": source,
            },
        )

        if not chunks:
            logger.warning(f"[文档入库] 分块结果为空: title={title}")
            return {"doc_id": doc_id, "chunks": 0, "message": "文档内容无法分块"}

        # Step 2: 批量向量化（同步执行，确保完成）
        texts = [c.content for c in chunks]
        vectors = bailian_client.embed_batch(texts)

        if not vectors or len(vectors) != len(chunks):
            logger.error(f"[文档入库] 向量化失败: title={title}, chunks={len(chunks)}, vectors={len(vectors) if vectors else 0}")
            return {"doc_id": doc_id, "chunks": 0, "message": "向量化失败，请检查API密钥和网络"}

        # Step 3: 构建入库点
        points = []
        for i, (chunk, vector) in enumerate(zip(chunks, vectors)):
            points.append({
                "id": chunk.chunk_id,
                "vector": vector,
                "payload": {
                    "doc_id": doc_id,
                    "title": title,
                    "content": chunk.content,
                    "full_content": content,
                    "category": category,
                    "tags": ",".join(tags) if tags else "",
                    "source": source,
                    "chunk_id": chunk.chunk_id,
                    "chunk_index": chunk.index,
                    "total_chunks": len(chunks),
                    "chunk_type": chunk.chunk_type,
                    "chunk_hash": chunk.hash,
                    "quality_score": chunk.quality_score,
                    "start_char": chunk.start_char,
                    "end_char": chunk.end_char,
                    "created_at": datetime.now().isoformat(),
                },
            })

        # Step 4: 入库存储（同步执行，wait=True确保完成）
        qdrant_store.upsert_batch(self.COL_KNOWLEDGE, points)

        # 验证写入结果
        verify_count = qdrant_store.get_count(self.COL_KNOWLEDGE)
        logger.info(
            f"[文档入库] 完成: doc_id={doc_id}, title={title}, "
            f"category={category}, chunks={len(chunks)}, "
            f"avg_quality={sum(c.quality_score for c in chunks) / len(chunks):.2f}, "
            f"verify_count={verify_count}"
        )

        return {
            "doc_id": doc_id,
            "chunks": len(chunks),
            "chunk_ids": [c.chunk_id for c in chunks],
            "avg_quality": round(sum(c.quality_score for c in chunks) / len(chunks), 3),
            "message": f"文档入库成功，共 {len(chunks)} 个块",
        }

    def add_document(self, title: str, content: str, category: str = "通用",
                     tags: list[str] | None = None, source: str = "") -> str:
        """简化版文档入库（兼容旧接口）"""
        result = self.add_document_advanced(title, content, category, tags, source)
        return result.get("message", "入库失败")

    def add_documents(self, collection: str, documents: list[dict]) -> int:
        """批量添加文档"""
        success_count = 0
        for doc in documents:
            try:
                self.add_document_advanced(
                    title=doc.get("title", ""),
                    content=doc.get("content", ""),
                    category=doc.get("category", "通用"),
                    tags=doc.get("tags"),
                    source=doc.get("source", ""),
                )
                success_count += 1
            except Exception as e:
                logger.error(f"[批量入库] 失败: {e}")
        return success_count

    def delete_document(self, doc_id: str) -> int:
        """删除文档（删除所有关联块）"""
        count = qdrant_store.delete_by_filter(
            self.COL_KNOWLEDGE,
            filter_field="doc_id",
            filter_value=doc_id,
        )
        logger.info(f"[文档删除] doc_id={doc_id}, deleted={count}")
        return count

    def list_documents(self, category: str = None) -> list[dict]:
        """列出所有文档（按doc_id去重，返回完整内容）"""
        all_chunks = qdrant_store.scroll(self.COL_KNOWLEDGE, limit=1000)
        doc_map = {}

        for chunk in all_chunks:
            payload = chunk.get("payload", {})
            doc_id = payload.get("doc_id")

            if doc_id not in doc_map:
                doc_map[doc_id] = {
                    "doc_id": doc_id,
                    "title": payload.get("title", ""),
                    "category": payload.get("category", ""),
                    "tags": payload.get("tags", "").split(",") if payload.get("tags") else [],
                    "source": payload.get("source", ""),
                    "full_content": payload.get("full_content", ""),
                    "created_at": payload.get("created_at", ""),
                    "chunk_count": 0,
                    "avg_quality": [],
                }

            doc_map[doc_id]["chunk_count"] += 1
            if "quality_score" in payload:
                doc_map[doc_id]["avg_quality"].append(payload["quality_score"])

        for doc in doc_map.values():
            if doc["avg_quality"]:
                doc["avg_quality"] = round(sum(doc["avg_quality"]) / len(doc["avg_quality"]), 3)
            else:
                doc["avg_quality"] = 0.0

        documents = list(doc_map.values())

        if category:
            documents = [d for d in documents if d["category"] == category]

        documents.sort(key=lambda x: x["created_at"], reverse=True)
        return documents

    def get_document_chunks(self, doc_id: str) -> list[dict]:
        """获取文档的所有块"""
        return qdrant_store.scroll_with_filter(
            self.COL_KNOWLEDGE,
            filter_field="doc_id",
            filter_value=doc_id,
            limit=100,
        )

    # ===================== 检索（使用新 retriever） =====================

    def semantic_search(self, query: str, top_k: int = 5) -> list[dict]:
        """语义检索"""
        qv = bailian_client.embed(query)
        return qdrant_store.search(self.COL_KNOWLEDGE, qv, top_k, settings.SIMILARITY_THRESHOLD)

    def category_search(self, query: str, category: str, top_k: int = 5) -> list[dict]:
        """分类检索"""
        qv = bailian_client.embed(query)
        return qdrant_store.search_with_filter(
            self.COL_KNOWLEDGE, qv, top_k, settings.SIMILARITY_THRESHOLD,
            filter_field="category", filter_value=category,
        )

    def hybrid_search(self, query: str, top_k: int = 5) -> list[dict]:
        """混合检索（语义 + 关键词）"""
        qv = bailian_client.embed(query)
        results = qdrant_store.search(self.COL_KNOWLEDGE, qv, top_k * 2, settings.SIMILARITY_THRESHOLD)

        # 去重 + 排序
        seen = set()
        deduped = []
        for r in sorted(results, key=lambda x: x.get("score", 0), reverse=True):
            rid = str(r.get("id"))
            if rid not in seen:
                seen.add(rid)
                deduped.append(r)

        return deduped[:top_k]

    def search_by_quality(
        self,
        query: str,
        min_quality: float = 0.7,
        top_k: int = 5,
    ) -> list[dict]:
        """按质量评分检索（过滤低质量块）"""
        results = self.semantic_search(query, top_k * 2)
        filtered = [
            r for r in results
            if r.get("payload", {}).get("quality_score", 1.0) >= min_quality
        ]
        return filtered[:top_k]

    # ===================== 决策历史 =====================

    def record_decision(
        self,
        scenario: str,
        decision: str,
        result: str,
        metadata: dict | None = None,
    ):
        """记录AI决策"""
        text = f"场景: {scenario}\n决策: {decision}\n结果: {result}"
        vector = bailian_client.embed(text)
        qdrant_store.upsert(
            self.COL_DECISIONS,
            f"DEC-{uuid.uuid4().hex[:12]}",
            vector,
            {
                "scenario": scenario,
                "decision": decision,
                "result": result,
                "recorded_at": datetime.now().isoformat(),
                **(metadata or {}),
            },
        )
        logger.info(f"[决策记录] scenario={scenario[:50]}")

    def recall_decisions(self, scenario: str, top_k: int = 3) -> list[dict]:
        """检索相似历史决策"""
        qv = bailian_client.embed(scenario)
        return qdrant_store.search(self.COL_DECISIONS, qv, top_k, 0.75)

    # ===================== 业务规则 =====================

    def add_rule(
        self,
        rule_name: str,
        rule_content: str,
        rule_type: str = "",
        priority: str = "中",
    ):
        """录入业务规则"""
        vector = bailian_client.embed(f"{rule_name}: {rule_content}")
        qdrant_store.upsert(
            self.COL_RULES,
            f"RULE-{uuid.uuid4().hex[:12]}",
            vector,
            {
                "rule_name": rule_name,
                "content": rule_content,
                "rule_type": rule_type,
                "priority": priority,
                "created_at": datetime.now().isoformat(),
            },
        )
        logger.info(f"[规则录入] rule_name={rule_name}")

    def recall_rules(self, query: str, top_k: int = 5) -> list[dict]:
        """检索相关业务规则"""
        qv = bailian_client.embed(query)
        return qdrant_store.search(self.COL_RULES, qv, top_k, 0.6)

    # ===================== 统计信息 =====================

    def get_stats(self) -> dict:
        """获取知识库统计"""
        knowledge_count = qdrant_store.get_count(self.COL_KNOWLEDGE)
        decision_count = qdrant_store.get_count(self.COL_DECISIONS)
        rule_count = qdrant_store.get_count(self.COL_RULES)
        return {
            "knowledge_count": knowledge_count,
            "decision_count": decision_count,
            "rule_count": rule_count,
            "total_vectors": knowledge_count + decision_count + rule_count,
            "collections": qdrant_store.list_collections(),
        }

    # ===================== 初始化 =====================

    async def init_defaults(self):
        """初始化默认知识库"""
        count = qdrant_store.get_count(self.COL_KNOWLEDGE)
        if count > 0:
            logger.info(f"[初始化] 知识库已有 {count} 条记录，跳过")
            return

        logger.info("[初始化] 开始初始化默认知识库...")
        defaults = [
            {
                "title": "安全库存计算规则",
                "category": "库存策略",
                "content": """## 安全库存公式
安全库存 SS = Z × σ × √LT

### 参数说明
- Z值（服务水平系数）：
  - 95%服务水平 → Z=1.65
  - 97.5%服务水平 → Z=1.96
  - 99%服务水平 → Z=2.33

### 分类管理策略
- A类商品：安全库存覆盖2周需求
- B类商品：安全库存覆盖4周需求
- C类商品：安全库存覆盖6周需求

### EOQ经济订货量
EOQ = √(2DS/H)
- D: 年需求量
- S: 单次订货成本
- H: 单位持有成本""",
                "tags": ["安全库存", "公式", "库存策略"],
                "source": "供应链最佳实践",
            },
            {
                "title": "调度决策优先级规则",
                "category": "调度规则",
                "content": """## 调度优先级矩阵

### 时效优先原则
1. 承诺时效订单优先处理
2. 覆盖率低于3天的商品优先
3. VIP客户订单优先

### 成本优化原则
1. 同向订单合并发货
2. 满载率最大化
3. 减少中转环节

### 库存均衡原则
1. 避免单仓过度消耗
2. 考虑区域库存分布
3. 动态调整配送路径

### 客户分级
- VIP客户：最高优先级，专人跟进
- 大客户：优先调度，提前预警
- 普通客户：标准流程""",
                "tags": ["调度", "优先级", "决策规则"],
                "source": "运营手册",
            },
            {
                "title": "风险预警触发条件",
                "category": "风险规则",
                "content": """## 风险预警等级

### 红色预警（紧急）
- 库存周转天数 > 90天 → 过剩预警
- 覆盖率 < 7天 → 缺货预警
- 履约延迟 > 24小时 → 客户通知

### 黄色预警（关注）
- 覆盖率 7-14天 → 库存预警
- 供应商准时率 < 90% → 备选评估
- 日单量 > 日均200% → 运力预警

### 应急预案
- 极端天气 → 提前72小时应急方案
- 供应商中断 → 紧急备选供应商激活
- 系统故障 → 手工调度备份流程""",
                "tags": ["预警", "风险管理", "应急预案"],
                "source": "风险管理手册",
            },
            {
                "title": "成本优化参考策略",
                "category": "成本优化",
                "content": """## 成本结构分析

### 运输成本（40-60%）
- 合并批次可降低15-25%
- 回程配货减少空驶
- 路径优化减少里程

### 仓储成本（20-30%）
- 优化仓库配置可降10-20%
- 自动化设备提升效率
- 库位优化减少搬运

### 人力成本（10-15%）
- 批量处理减少投入
- 自动化决策降低人工
- 培训提升效率

### 盈亏平衡点
盈亏平衡点 = 固定成本 / (单价 - 单位变动成本)""",
                "tags": ["成本", "优化", "财务"],
                "source": "财务分析报告",
            },
            {
                "title": "需求预测季节性规律",
                "category": "需求预测",
                "content": """## 季度需求规律

### Q1季度（1-3月）
- 春节前后波动剧烈
- 节前2周销量高峰
- 节后恢复期2-3周

### Q2季度（4-6月）
- 618大促期间激增
- 5月底开始备货
- 6月中旬高峰

### Q3季度（7-9月）
- 暑期淡季调整
- 开学季小高峰
- 中秋备货期

### Q4季度（10-12月）
- 双11大促增幅30-50%
- 双12延续高峰
- 年终备货期
- 新品首月销量=预测值60-80%

### 促销期规律
- 同品类促销期间增2-5倍
- 需提前2周备货""",
                "tags": ["季节性", "预测", "促销"],
                "source": "历年数据分析",
            },
        ]

        for doc in defaults:
            self.add_document_advanced(**doc)

        logger.info(f"[初始化] 默认知识库完成，共 {len(defaults)} 篇文档")


kb_service = KnowledgeBaseService()