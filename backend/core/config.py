from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App
    APP_NAME: str = "rag-app"
    APP_ENV: str = "dev"
    DEBUG: bool = True

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Database
    DATABASE_URL: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/rag_db"

    # File storage
    UPLOAD_DIR: str = "uploads"

    # Models (local)
    EMBEDDING_MODEL: str = "BAAI/bge-small-en"
    CHAT_MODEL: str = "llama3.1:8b"

    # Vector dimension (must match embedding model)
    VECTOR_DIM: int = 384

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()