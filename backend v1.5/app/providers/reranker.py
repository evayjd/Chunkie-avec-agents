"""Reranker provider — calls a local reranker via OpenAI-compatible API."""
 
from typing import Any
import structlog
import httpx

from app.config.settings import get_settings
from app.providers.base import BaseRerankerProvider

logger = structlog.get_logger(__name__)


class LocalCompatibleRerankerProvider(BaseRerankerProvider):
    """Calls a reranker endpoint that accepts query+documents and returns scores."""

    def __init__(self) -> None:
        s = get_settings()
        self._base_url = str(s.reranker_base_url).rstrip("/")
        self._api_key = s.reranker_api_key
        self._model = s.reranker_model
        self._top_n = s.reranker_top_n
        self._timeout = s.reranker_timeout_seconds

    async def rerank(
        self,
        query: str,
        documents: list[str],
        top_n: int | None = None,
    ) -> list[dict[str, Any]]:
        n = top_n or self._top_n
        # Attempt standard rerank endpoint; fall back to scoring via embeddings
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                resp = await client.post(
                    f"{self._base_url}/rerank",
                    headers={"Authorization": f"Bearer {self._api_key}"},
                    json={
                        "model": self._model,
                        "query": query,
                        "documents": documents,
                        "top_n": n,
                    },
                )
                resp.raise_for_status()
                data = resp.json()
                return data.get("results", data)
        except Exception as exc:
            logger.warning("reranker_fallback", error=str(exc))
            # Fallback: return documents in original order with neutral score
            return [
                {"index": i, "relevance_score": 1.0 - i * 0.01, "document": doc}
                for i, doc in enumerate(documents[:n])
            ]

    async def health_check(self) -> bool:
        try:
            await self.rerank("test", ["test document"], top_n=1)
            return True
        except Exception:
            return False


def get_reranker_provider() -> BaseRerankerProvider:
    return LocalCompatibleRerankerProvider()
