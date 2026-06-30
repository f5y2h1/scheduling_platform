"""
Three-Tier Memory Architecture for Xuni Scheduling Platform

Layer 1 - Working Memory:  LangGraph State + PostgresSaver Checkpointer
Layer 2 - Short-term Memory: ContextManager + Redis + PostgreSQL
Layer 3 - Long-term Memory:  PostgreSQL (profiles) + Qdrant (semantic search)
"""

from .memory_manager import MemoryManager, memory_manager
from .short_term import ShortTermMemory
from .long_term import LongTermMemory

__all__ = [
    "MemoryManager",
    "memory_manager",
    "ShortTermMemory",
    "LongTermMemory",
]
