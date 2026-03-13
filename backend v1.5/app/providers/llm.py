"""OpenAI-compatible LLM provider (Ollama / local endpoint)."""
 
import structlog
from openai import AsyncOpenAI, APIConnectionError, APIStatusError

from app.config.settings import get_settings
from app.core.exceptions import LLMError
from app.providers.base import BaseLLMProvider

logger = structlog.get_logger(__name__)


class LocalCompatibleLLMProvider(BaseLLMProvider):
    """Calls any OpenAI-compatible endpoint (default: Ollama)."""

    def __init__(self) -> None:
        s = get_settings()
        self._client = AsyncOpenAI(
            base_url=str(s.llm_base_url),
            api_key=s.llm_api_key,
            timeout=s.llm_timeout_seconds,
            max_retries=s.llm_max_retries,
        )
        self._model = s.llm_model
        self._fallback = s.llm_fallback_model
        self._temperature = s.llm_temperature
        self._max_tokens = s.llm_max_tokens

    async def chat_completion(
        self,
        messages: list[dict[str, str]],
        temperature: float | None = None,
        max_tokens: int | None = None,
        **kwargs,
    ) -> str:
        temp = temperature if temperature is not None else self._temperature
        tokens = max_tokens if max_tokens is not None else self._max_tokens
        for model in (self._model, self._fallback):
            try:
                resp = await self._client.chat.completions.create(
                    model=model,
                    messages=messages,  # type: ignore[arg-type]
                    temperature=temp,
                    max_tokens=tokens,
                    **kwargs,
                )
                return resp.choices[0].message.content or ""
            except APIStatusError as exc:
                logger.warning("llm_api_error", model=model, status=exc.status_code)
                if model == self._fallback:
                    raise LLMError(f"LLM API error: {exc}") from exc
            except APIConnectionError as exc:
                logger.error("llm_connection_error", model=model, error=str(exc))
                if model == self._fallback:
                    raise LLMError(f"LLM connection error: {exc}") from exc
        raise LLMError("All LLM models failed")

    async def health_check(self) -> bool:
        try:
            await self._client.models.list()
            return True
        except Exception:
            return False


def get_llm_provider() -> BaseLLMProvider:
    return LocalCompatibleLLMProvider()
