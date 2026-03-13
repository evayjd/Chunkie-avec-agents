"""OpenAI-compatible embedding provider."""
 
import asyncio
import structlog
from openai import AsyncOpenAI

from app.config.settings import get_settings
from app.core.exceptions import EmbeddingError
from app.providers.base import BaseEmbeddingProvider

logger = structlog.get_logger(__name__)


class LocalCompatibleEmbeddingProvider(BaseEmbeddingProvider):
    def __init__(self) -> None:
        s = get_settings()
        self._client = AsyncOpenAI(
            base_url=str(s.embedding_base_url),
            api_key=s.embedding_api_key,
            timeout=s.embedding_timeout_seconds,
        )
        self._model = s.embedding_model
        self._batch_size = s.embedding_batch_size
        self._dim = s.embedding_dimension

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        results: list[list[float]] = []
        for i in range(0, len(texts), self._batch_size):
            batch = texts[i : i + self._batch_size]
            try:
                resp = await self._client.embeddings.create(
                    model=self._model, input=batch
                )
                results.extend(item.embedding for item in resp.data)
            except Exception as exc:
                logger.error("embedding_error", batch_start=i, error=str(exc))
                raise EmbeddingError(f"Embedding failed: {exc}") from exc
        return results

    async def embed_query(self, text: str) -> list[float]:
        vecs = await self.embed_texts([text])
        return vecs[0]

    async def health_check(self) -> bool:
        try:
            await self.embed_query("ping")
            return True
        except Exception:
            return False


def get_embedding_provider() -> BaseEmbeddingProvider:
    return LocalCompatibleEmbeddingProvider()
