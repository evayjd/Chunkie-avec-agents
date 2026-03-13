"""
文件职责：数据库异步会话管理
"""

from collections.abc import AsyncGenerator
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy import text

from app.config import get_settings
from app.core.logging import get_logger
from app.db.base import Base   # 👈 必须导入

logger = get_logger(__name__)


def create_engine_and_session(database_url: str | None = None) -> tuple[Any, Any]:
    settings = get_settings()
    url = database_url or settings.database_url

    engine = create_async_engine(
        url,
        pool_size=settings.database_pool_size,
        max_overflow=settings.database_max_overflow,
        echo=settings.database_echo,
    )

    session_factory = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )

    return engine, session_factory


_engine, _session_factory = create_engine_and_session()
async_session_factory = _session_factory


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with _session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# 注册 ORM models（非常重要）— import package triggers __init__.py which loads all models
import app.models  # noqa: F401


async def init_db() -> None:
    async with _engine.begin() as conn:
        # 创建 pgvector
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        logger.info("pgvector 扩展已初始化")

        # 👇 创建所有 ORM 表
        await conn.run_sync(Base.metadata.create_all)


def get_engine():
    return _engine