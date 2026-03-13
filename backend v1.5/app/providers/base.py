"""Provider base classes for LLM, Embedding, and Reranker."""
 
from abc import ABC, abstractmethod
from typing import Any


class BaseLLMProvider(ABC):
    """Abstract base for LLM providers."""

    @abstractmethod
    async def chat_completion(
        self,
        messages: list[dict[str, str]],
        temperature: float | None = None,
        max_tokens: int | None = None,
        **kwargs: Any,
    ) -> str:
        """Return assistant message content."""

    @abstractmethod
    async def health_check(self) -> bool:
        """Return True if provider is reachable."""


class BaseEmbeddingProvider(ABC):
    """Abstract base for embedding providers."""

    @abstractmethod
    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Return embedding vectors for each text."""

    @abstractmethod
    async def embed_query(self, text: str) -> list[float]:
        """Return embedding vector for a single query."""

    @abstractmethod
    async def health_check(self) -> bool:
        """Return True if provider is reachable."""


class BaseRerankerProvider(ABC):
    """Abstract base for reranker providers."""

    @abstractmethod
    async def rerank(
        self,
        query: str,
        documents: list[str],
        top_n: int | None = None,
    ) -> list[dict[str, Any]]:
        """Return reranked documents with scores."""

    @abstractmethod
    async def health_check(self) -> bool:
        """Return True if provider is reachable."""
