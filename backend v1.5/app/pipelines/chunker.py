"""Sliding-window chunker with overlap."""
 
import structlog
from app.config.settings import get_settings
from app.utils.text import clean_text, count_tokens_approx

logger = structlog.get_logger(__name__)


def sliding_window_chunks(
    text: str,
    chunk_size: int,
    overlap: int,
    min_length: int,
    max_length: int,
) -> list[dict]:
    """Split text into overlapping chunks. Returns list of chunk dicts."""
    text = clean_text(text)
    words = text.split()
    chunks = []
    i = 0
    char_cursor = 0

    while i < len(words):
        chunk_words = words[i : i + chunk_size]
        chunk_text = " ".join(chunk_words)

        if len(chunk_text) < min_length and i + chunk_size >= len(words):
            # Last small chunk — merge with previous if exists
            if chunks:
                chunks[-1]["text"] += " " + chunk_text
            break

        if len(chunk_text) > max_length:
            chunk_text = chunk_text[:max_length]

        char_start = text.find(chunk_text, char_cursor)
        char_end = char_start + len(chunk_text) if char_start != -1 else -1

        chunks.append(
            {
                "text": chunk_text,
                "char_start": max(0, char_start),
                "char_end": max(0, char_end),
                "token_count": count_tokens_approx(chunk_text),
                "chunk_index": len(chunks),
            }
        )
        if char_start != -1:
            char_cursor = char_start

        step = max(1, chunk_size - overlap)
        i += step

    return chunks


def chunk_document(text: str) -> list[dict]:
    s = get_settings()
    return sliding_window_chunks(
        text,
        chunk_size=s.chunk_size,
        overlap=s.chunk_overlap,
        min_length=s.chunk_min_length,
        max_length=s.chunk_max_length,
    )
