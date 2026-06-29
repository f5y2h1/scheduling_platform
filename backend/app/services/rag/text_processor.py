"""
文本预处理和智能分块模块
工程化 RAG 流程的第一步：文档清洗 → 结构解析 → 智能分块 → 质量控制
"""
import re
import uuid
import hashlib
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime

from app.core.logger import logger


@dataclass
class ChunkConfig:
    """分块配置"""
    chunk_size: int = 800          # 目标块大小
    chunk_overlap: int = 100       # 重叠窗口
    min_chunk_size: int = 100      # 最小块大小（过滤过短的块）
    max_chunk_size: int = 1500     # 最大块大小（超长块需要切分）
    respect_boundaries: bool = True # 是否尊重语义边界
    enable_dedup: bool = True      # 是否启用去重


@dataclass
class TextChunk:
    """文本块数据结构"""
    chunk_id: str                  # 唯一标识
    content: str                   # 块内容
    index: int                     # 块索引
    parent_doc_id: str             # 父文档ID
    parent_title: str              # 父文档标题
    chunk_type: str = "paragraph"  # 块类型: paragraph/heading/list/table
    start_char: int = 0            # 在原文中的起始位置
    end_char: int = 0              # 在原文中的结束位置
    metadata: dict = field(default_factory=dict)  # 额外元数据
    hash: str = ""                 # 内容哈希（用于去重）
    quality_score: float = 1.0     # 质量评分


class TextProcessor:
    """文本预处理和智能分块"""

    # 语义边界标记
    BOUNDARY_MARKERS = {
        "heading": re.compile(r"^#{1,6}\s+.+$|^【.+】$|^第[一二三四五六七八九十\d]+[章节条款]"),
        "paragraph": re.compile(r"\n\n+"),
        "list_item": re.compile(r"^\s*[-*•]\s+|^\s*\d+[\.\)]\s+"),
        "table_row": re.compile(r"^\|.+\|$"),
    }

    def __init__(self, config: ChunkConfig = None):
        self.config = config or ChunkConfig()

    def process_document(
        self,
        content: str,
        doc_id: str = "",
        title: str = "",
        metadata: dict = None,
    ) -> list[TextChunk]:
        """
        完整文档处理流程：
        1. 文本清洗
        2. 结构解析
        3. 智能分块
        4. 质量控制
        """
        # Step 1: 文本清洗
        cleaned = self._clean_text(content)

        # Step 2: 结构解析
        segments = self._parse_structure(cleaned)

        # Step 3: 智能分块
        raw_chunks = self._smart_chunk(segments, doc_id, title)

        # Step 4: 质量控制
        quality_chunks = self._quality_control(raw_chunks)

        # 添加元数据
        for chunk in quality_chunks:
            chunk.metadata = {**(metadata or {}), "processed_at": datetime.now().isoformat()}

        logger.info(
            f"[TextProcessor] 文档处理完成: doc_id={doc_id}, "
            f"segments={len(segments)}, raw_chunks={len(raw_chunks)}, "
            f"quality_chunks={len(quality_chunks)}"
        )

        return quality_chunks

    def _clean_text(self, text: str) -> str:
        """文本清洗"""
        # 去除多余空白
        text = re.sub(r"[ \t]+", " ", text)
        # 去除多余换行（保留段落分隔）
        text = re.sub(r"\n{3,}", "\n\n", text)
        # 去除行首行尾空白
        text = "\n".join(line.strip() for line in text.split("\n"))
        # 去除不可见字符
        text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", text)
        return text.strip()

    def _parse_structure(self, text: str) -> list[dict]:
        """解析文档结构"""
        segments = []
        lines = text.split("\n")
        current_para = []
        current_type = "paragraph"
        char_pos = 0

        for line in lines:
            line = line.strip()
            if not line:
                if current_para:
                    content = "\n".join(current_para)
                    segments.append({
                        "type": current_type,
                        "content": content,
                        "start": char_pos - len(content),
                        "end": char_pos,
                    })
                    current_para = []
                char_pos += 1
                continue

            # 检测结构类型
            if self.BOUNDARY_MARKERS["heading"].match(line):
                # 先保存当前段落
                if current_para:
                    content = "\n".join(current_para)
                    segments.append({
                        "type": current_type,
                        "content": content,
                        "start": char_pos - len(content),
                        "end": char_pos,
                    })
                    current_para = []
                # 标题单独作为segment
                segments.append({
                    "type": "heading",
                    "content": line,
                    "start": char_pos,
                    "end": char_pos + len(line),
                })
                current_type = "paragraph"
            elif self.BOUNDARY_MARKERS["list_item"].match(line):
                current_type = "list"
                current_para.append(line)
            elif self.BOUNDARY_MARKERS["table_row"].match(line):
                current_type = "table"
                current_para.append(line)
            else:
                if current_type != "paragraph" and current_para:
                    # 切换回段落类型前保存
                    content = "\n".join(current_para)
                    segments.append({
                        "type": current_type,
                        "content": content,
                        "start": char_pos - len(content),
                        "end": char_pos,
                    })
                    current_para = []
                current_type = "paragraph"
                current_para.append(line)

            char_pos += len(line) + 1

        # 保存最后一个段落
        if current_para:
            content = "\n".join(current_para)
            segments.append({
                "type": current_type,
                "content": content,
                "start": char_pos - len(content),
                "end": char_pos,
            })

        return segments

    def _smart_chunk(
        self,
        segments: list[dict],
        doc_id: str,
        title: str,
    ) -> list[TextChunk]:
        """智能分块策略"""
        chunks = []
        current_content = ""
        current_type = "paragraph"
        current_start = 0
        chunk_idx = 0

        for seg in segments:
            seg_content = seg["content"]
            seg_type = seg["type"]

            # 标题作为独立块的起始标记
            if seg_type == "heading":
                # 先保存当前累积的内容
                if current_content.strip():
                    chunks.append(self._create_chunk(
                        content=current_content.strip(),
                        index=chunk_idx,
                        doc_id=doc_id,
                        title=title,
                        chunk_type=current_type,
                        start=current_start,
                        end=current_start + len(current_content),
                    ))
                    chunk_idx += 1
                    # 重叠窗口
                    overlap_text = self._get_overlap(current_content)
                    current_content = overlap_text
                    current_start = seg["start"] - len(overlap_text)
                else:
                    current_start = seg["start"]

                # 标题内容追加
                current_content = f"{current_content}\n{seg_content}" if current_content else seg_content
                current_type = "heading"

            else:
                # 检查是否会超出最大块大小
                combined_len = len(current_content) + len(seg_content) + 1

                if combined_len > self.config.max_chunk_size and current_content.strip():
                    # 保存当前块
                    chunks.append(self._create_chunk(
                        content=current_content.strip(),
                        index=chunk_idx,
                        doc_id=doc_id,
                        title=title,
                        chunk_type=current_type,
                        start=current_start,
                        end=current_start + len(current_content),
                    ))
                    chunk_idx += 1
                    # 重叠窗口
                    overlap_text = self._get_overlap(current_content)
                    current_content = overlap_text
                    current_start = seg["start"] - len(overlap_text)

                # 追加内容
                current_content = f"{current_content}\n{seg_content}" if current_content else seg_content

                # 如果单段内容过长，需要强制切分
                if len(seg_content) > self.config.max_chunk_size:
                    sub_chunks = self._split_long_segment(
                        seg_content, seg_type, chunk_idx, doc_id, title, seg["start"]
                    )
                    chunks.extend(sub_chunks)
                    chunk_idx += len(sub_chunks)
                    current_content = ""
                    current_start = seg["end"]

        # 保存最后的内容
        if current_content.strip():
            chunks.append(self._create_chunk(
                content=current_content.strip(),
                index=chunk_idx,
                doc_id=doc_id,
                title=title,
                chunk_type=current_type,
                start=current_start,
                end=current_start + len(current_content),
            ))

        return chunks

    def _split_long_segment(
        self,
        content: str,
        seg_type: str,
        start_idx: int,
        doc_id: str,
        title: str,
        start_char: int,
    ) -> list[TextChunk]:
        """切分过长的段落"""
        chunks = []
        sentences = self._split_sentences(content)
        current = ""
        idx = start_idx

        for sent in sentences:
            if len(current) + len(sent) > self.config.chunk_size and current.strip():
                chunks.append(self._create_chunk(
                    content=current.strip(),
                    index=idx,
                    doc_id=doc_id,
                    title=title,
                    chunk_type=seg_type,
                    start=start_char,
                    end=start_char + len(current),
                ))
                idx += 1
                start_char += len(current)
                overlap = self._get_overlap(current)
                current = overlap

            current = f"{current} {sent}" if current else sent

        if current.strip():
            chunks.append(self._create_chunk(
                content=current.strip(),
                index=idx,
                doc_id=doc_id,
                title=title,
                chunk_type=seg_type,
                start=start_char,
                end=start_char + len(current),
            ))

        return chunks

    def _split_sentences(self, text: str) -> list[str]:
        """句子切分"""
        # 中文句子切分
        pattern = re.compile(r"[。！？；\n]+")
        sentences = []
        last_end = 0

        for match in pattern.finditer(text):
            sent = text[last_end:match.end()].strip()
            if sent:
                sentences.append(sent)
            last_end = match.end()

        if last_end < len(text):
            remaining = text[last_end:].strip()
            if remaining:
                sentences.append(remaining)

        return sentences

    def _get_overlap(self, text: str) -> str:
        """获取重叠窗口文本"""
        if not text or len(text) <= self.config.chunk_overlap:
            return ""
        # 从末尾取重叠部分，尽量在句子边界处
        overlap_text = text[-self.config.chunk_overlap:]
        # 找到第一个句子分隔符
        first_sentence_end = re.search(r"[。！？\n]", overlap_text)
        if first_sentence_end:
            return overlap_text[first_sentence_end.end():]
        return overlap_text

    def _create_chunk(
        self,
        content: str,
        index: int,
        doc_id: str,
        title: str,
        chunk_type: str,
        start: int,
        end: int,
    ) -> TextChunk:
        """创建块对象"""
        return TextChunk(
            chunk_id=str(uuid.uuid4()),
            content=content,
            index=index,
            parent_doc_id=doc_id,
            parent_title=title,
            chunk_type=chunk_type,
            start_char=start,
            end_char=end,
            hash=self._compute_hash(content),
            quality_score=self._compute_quality(content),
        )

    def _compute_hash(self, content: str) -> str:
        """计算内容哈希"""
        return hashlib.md5(content.encode()).hexdigest()[:16]

    def _compute_quality(self, content: str) -> float:
        """计算块质量评分"""
        score = 1.0

        # 长度评分
        len_score = 1.0
        if len(content) < self.config.min_chunk_size:
            len_score = 0.5
        elif len(content) > self.config.max_chunk_size:
            len_score = 0.7
        score *= len_score

        # 信息密度评分（排除过多空白）
        blank_ratio = len(re.findall(r"\s+", content)) / len(content) if content else 0
        density_score = 1.0 - min(blank_ratio * 2, 0.5)
        score *= density_score

        # 完整性评分（是否以完整句子结尾）
        if not re.search(r"[。！？\.\!\?]$", content.strip()):
            score *= 0.9

        return round(score, 3)

    def _quality_control(self, chunks: list[TextChunk]) -> list[TextChunk]:
        """质量控制：过滤低质量块 + 去重"""
        result = []

        # 过滤
        for chunk in chunks:
            # 过滤过短的块
            if len(chunk.content) < self.config.min_chunk_size:
                logger.debug(f"[质量控制] 过滤过短块: len={len(chunk.content)}, hash={chunk.hash}")
                continue
            # 过滤低质量块
            if chunk.quality_score < 0.5:
                logger.debug(f"[质量控制] 过滤低质量块: score={chunk.quality_score}, hash={chunk.hash}")
                continue
            result.append(chunk)

        # 去重
        if self.config.enable_dedup:
            seen_hashes = set()
            deduped = []
            for chunk in result:
                if chunk.hash in seen_hashes:
                    logger.debug(f"[质量控制] 去重块: hash={chunk.hash}")
                    continue
                seen_hashes.add(chunk.hash)
                deduped.append(chunk)
            result = deduped

        return result


text_processor = TextProcessor()