"""Language detection utilities."""
 
import structlog
from langdetect import detect, LangDetectException

from app.config.settings import get_settings

logger = structlog.get_logger(__name__)

_LANG_MAP = {"zh-cn": "zh", "zh-tw": "zh", "zh": "zh", "en": "en", "fr": "fr"}


def detect_language(text: str) -> str:
    """Detect language; return 'zh' | 'en' | 'fr', default to settings default."""
    s = get_settings()
    default = s.default_language

    if not text or len(text.strip()) < 10:
        return default

    try:
        raw = detect(text[:500])
        lang = _LANG_MAP.get(raw)

        if lang is None:
            return default

        return lang

    except LangDetectException:
        logger.debug("lang_detect_failed", text_preview=text[:50])
        return default
