"""
应用配置中心
从 .env 文件 + 环境变量加载配置
优先级：环境变量 > .env 文件 > 默认值
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# 加载 backend/.env 文件（若存在）
_env_path = Path(__file__).resolve().parent.parent.parent / ".env"
if _env_path.exists():
    load_dotenv(_env_path, override=False)

from pydantic import BaseModel, Field


class Settings(BaseModel):
    HOST: str = Field(default="0.0.0.0")
    PORT: int = Field(default=8000)
    DEBUG: bool = Field(default=True)

    DB_HOST: str = Field(default="localhost")
    DB_PORT: int = Field(default=5432)
    DB_NAME: str = Field(default="scheduling_platform")
    DB_USER: str = Field(default="postgres")
    DB_PASSWORD: str = Field(default="postgres")

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

    REDIS_HOST: str = Field(default="localhost")
    REDIS_PORT: int = Field(default=6379)
    REDIS_PASSWORD: str = Field(default="")

    QDRANT_HOST: str = Field(default="localhost")
    QDRANT_REST_PORT: int = Field(default=6333)

    BAILIAN_API_KEY: str = Field(default="your-api-key-here")

    LLM_MODELS: list = Field(default=["qwen3.5-omni-plus"])
    LLM_DEFAULT_MODEL: str = Field(default="qwen3.5-omni-plus")
    LLM_MAX_TOKENS: int = Field(default=4096)
    LLM_TEMPERATURE: float = Field(default=0.7)

    MULTIMODAL_MODEL: str = Field(default="qwen3.5-omni-plus")

    EMBEDDING_MODEL: str = Field(default="text-embedding-v2")
    VECTOR_SIZE: int = Field(default=1536)

    JWT_SECRET: str = Field(default="xuni-scheduling-platform-secret-key-2026")
    JWT_EXPIRATION: int = Field(default=86400)
    JWT_REFRESH_EXPIRATION: int = Field(default=604800)

    KNOWLEDGE_COLLECTION: str = Field(default="xuni_knowledge_base")
    DECISION_COLLECTION: str = Field(default="xuni_decision_history")
    RULES_COLLECTION: str = Field(default="xuni_business_rules")
    SEARCH_TOP_K: int = Field(default=5)
    SIMILARITY_THRESHOLD: float = Field(default=0.7)


def get_settings() -> Settings:
    env_vars = {}
    for field_name, field_info in Settings.model_fields.items():
        env_value = os.getenv(field_name)
        if env_value is not None:
            field_type = field_info.annotation
            if field_type is bool:
                env_vars[field_name] = env_value.lower() == "true"
            elif field_type is int:
                env_vars[field_name] = int(env_value)
            elif field_type is float:
                env_vars[field_name] = float(env_value)
            elif field_type is list:
                env_vars[field_name] = env_value.split(",")
            else:
                env_vars[field_name] = env_value
    return Settings(**env_vars)


settings = get_settings()
