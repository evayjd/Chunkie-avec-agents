"""
文件职责：统一配置管理中心
所有超参数、服务 URL、模型配置均在此集中声明。
"""

from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")
    app_name: str = Field(default="PersonaKB")
    app_env: Literal["development", "production", "test"] = Field(default="development")
    app_secret_key: str = Field(default="change-me-in-production")
    app_debug: bool = Field(default=True)
    app_version: str = Field(default="0.1.0")
    backend_host: str = Field(default="0.0.0.0")
    backend_port: int = Field(default=8000)
    frontend_origin: str = Field(default="http://localhost:5137")
    backend_base_url: str = Field(default="http://localhost:8000")
    api_prefix: str = Field(default="/api/v1")


class DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    database_url: str = Field(default="postgresql+asyncpg://dyj@localhost:5432/chunkiebase")
    database_pool_size: int = Field(default=10)
    database_max_overflow: int = Field(default=20)
    database_echo: bool = Field(default=False)


class StorageSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    storage_path: str = Field(default="./storage/uploads")
    upload_max_size_mb: int = Field(default=50)
    allowed_file_types: str = Field(default="pdf,md,txt,docx")

    @property
    def allowed_types_list(self) -> list[str]:
        return [t.strip().lower() for t in self.allowed_file_types.split(",")]

    @property
    def upload_max_size_bytes(self) -> int:
        return self.upload_max_size_mb * 1024 * 1024


class LLMSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    llm_provider: str = Field(default="local_compatible")
    llm_base_url: str = Field(default="http://localhost:11434/v1")
    llm_api_key: str = Field(default="ollama")
    llm_model: str = Field(default="qwen2.5:7b")
    llm_fallback_model: str = Field(default="llama3.1:8b")
    llm_temperature: float = Field(default=0.1)
    llm_max_tokens: int = Field(default=4096)
    llm_timeout_seconds: int = Field(default=120)
    llm_max_retries: int = Field(default=3)


class EmbeddingSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    embedding_provider: str = Field(default="local_compatible")
    embedding_base_url: str = Field(default="http://localhost:11434/v1")
    embedding_api_key: str = Field(default="ollama")
    embedding_model: str = Field(default="nomic-embed-text")
    embedding_dimension: int = Field(default=768)
    embedding_batch_size: int = Field(default=32)
    embedding_timeout_seconds: int = Field(default=60)


class RerankerSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    reranker_provider: str = Field(default="local_compatible")
    reranker_base_url: str = Field(default="http://localhost:11434/v1")
    reranker_api_key: str = Field(default="ollama")
    reranker_model: str = Field(default="bge-reranker-v2-m3")
    reranker_top_n: int = Field(default=5)
    reranker_timeout_seconds: int = Field(default=30)
    reranker_enabled: bool = Field(default=True)


class ChunkingSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    chunk_size: int = Field(default=512)
    chunk_overlap: int = Field(default=64)
    chunk_strategy: Literal["sliding_window", "heading_aware", "semantic"] = Field(default="sliding_window")
    chunk_min_length: int = Field(default=50)
    chunk_max_length: int = Field(default=1024)


class RetrievalSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    retrieval_dense_top_k: int = Field(default=20)
    retrieval_sparse_top_k: int = Field(default=20)
    retrieval_fusion_top_k: int = Field(default=15)
    retrieval_final_top_k: int = Field(default=5)
    retrieval_dense_weight: float = Field(default=0.7)
    retrieval_sparse_weight: float = Field(default=0.3)
    retrieval_rrf_k: int = Field(default=60)
    retrieval_similarity_threshold: float = Field(default=0.3)
    retrieval_max_context_tokens: int = Field(default=3000)
    retrieval_query_expansion_enabled: bool = Field(default=False)

    @field_validator("retrieval_dense_weight")
    @classmethod
    def validate_weights(cls, v: float) -> float:
        if not 0.0 <= v <= 1.0:
            raise ValueError("retrieval_dense_weight 必须在 [0, 1] 范围内")
        return v


class CitationSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    citation_snippet_max_length: int = Field(default=300)
    citation_inline_enabled: bool = Field(default=True)
    citation_min_confidence: float = Field(default=0.3)


class RoastSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    roast_tone: Literal["playful", "savage", "gentle"] = Field(default="playful")
    roast_max_length: int = Field(default=1000)
    persona_score_min: int = Field(default=0)
    persona_score_max: int = Field(default=100)
    persona_confidence_threshold: float = Field(default=0.3)


class MultilingualSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    default_language: str = Field(default="zh")
    supported_languages: str = Field(default="zh,en,fr")
    language_detect_confidence: float = Field(default=0.7)

    @property
    def supported_languages_list(self) -> list[str]:
        return [lang.strip() for lang in self.supported_languages.split(",")]


class MCPSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    mcp_enabled: bool = Field(default=True)
    mcp_server_name: str = Field(default="personakb-mcp")
    mcp_server_version: str = Field(default="0.1.0")
    mcp_port: int = Field(default=8001)


class LoggingSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    log_level: str = Field(default="INFO")
    log_format: Literal["json", "text"] = Field(default="text")
    log_file_path: str = Field(default="./logs/personakb.log")


class EvalSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    eval_output_dir: str = Field(default="./benchmarks/results")
    eval_default_top_k: int = Field(default=5)
    eval_metrics: str = Field(default="recall,precision,mrr,ndcg,hit_rate")


class Settings(
    AppSettings, DatabaseSettings, StorageSettings, LLMSettings,
    EmbeddingSettings, RerankerSettings, ChunkingSettings, RetrievalSettings,
    CitationSettings, RoastSettings, MultilingualSettings, MCPSettings,
    LoggingSettings, EvalSettings,
):
    """统一配置类：合并所有子配置。"""
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """获取单例配置实例（LRU 缓存）"""
    return Settings()
