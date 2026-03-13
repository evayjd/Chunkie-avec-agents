"""Text processing utilities."""
 
import re
import unicodedata


def normalize_whitespace(text: str) -> str:
    """Collapse multiple whitespace chars into a single space."""
    return re.sub(r"\s+", " ", text).strip()


def truncate(text: str, max_chars: int, suffix: str = "…") -> str:
    if len(text) <= max_chars:
        return text
    return text[: max_chars - len(suffix)] + suffix


def extract_snippet(
    text: str,
    start: int,
    end: int,
    context_chars: int = 100,
    max_length: int = 300,
) -> str:
    """Extract a snippet around [start, end] with context."""
    s = max(0, start - context_chars)
    e = min(len(text), end + context_chars)
    snippet = text[s:e].strip()
    return truncate(snippet, max_length)


def count_tokens_approx(text: str) -> int:
    """Approximate token count (4 chars per token heuristic)."""
    return max(1, len(text) // 4)


def normalize_unicode(text: str) -> str:
    return unicodedata.normalize("NFC", text)


def clean_text(text: str) -> str:
    text = normalize_unicode(text)
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)
    text = normalize_whitespace(text)
    return text
