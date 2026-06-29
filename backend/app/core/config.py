"""
应用配置中心
从环境变量 / .env 文件加载配置
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # ---- 服务 ----
    HOST: str = "0.0.0.0"
    PORT: int = 8080
    DEBUG: bool = True

    # ---- 数据库 ----
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "scheduling_platform"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    @property
    def DATABASE_URL_SYNC(self) -> str:
        return (
            f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    # ---- Redis ----
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = ""

    # ---- Qdrant ----
    QDRANT_HOST: str = "localhost"
    QDRANT_REST_PORT: int = 6333

    # ---- 阿里云百炼 ----
    BAILIAN_API_KEY: str = "your-api-key-here"

    # LLM 模型配置
    LLM_MODELS: list = [
        "qwen3.5-omni-plus",
    ]
    LLM_DEFAULT_MODEL: str = "qwen3.5-omni-plus"
    LLM_MAX_TOKENS: int = 4096
    LLM_TEMPERATURE: float = 0.7

    # 多模态模型配置（语音转文字、图片解析）
    MULTIMODAL_MODEL: str = "qwen3.5-omni-plus"

    # Embedding 模型
    EMBEDDING_MODEL: str = "text-embedding-v2"
    VECTOR_SIZE: int = 1536

    # ---- JWT ----
    JWT_SECRET: str = "xuni-scheduling-platform-secret-key-2026"
    JWT_EXPIRATION: int = 86400       # 24小时
    JWT_REFRESH_EXPIRATION: int = 604800  # 7天

    # ---- 知识库 ----
    KNOWLEDGE_COLLECTION: str = "xuni_knowledge_base"
    DECISION_COLLECTION: str = "xuni_decision_history"
    RULES_COLLECTION: str = "xuni_business_rules"
    SEARCH_TOP_K: int = 5
    SIMILARITY_THRESHOLD: float = 0.7

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",  # 忽略 PYTHONUNBUFFERED 等未在Settings中定义的环境变量
    }


settings = Settings()
