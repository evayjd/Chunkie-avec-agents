"""Unit tests for text utilities."""
import pytest
from app.utils.text import (
    normalize_whitespace,
    truncate,
    count_tokens_approx,
    clean_text,
)


def test_normalize_whitespace():
    assert normalize_whitespace("  hello   world  ") == "hello world"
    assert normalize_whitespace("a\tb\nc") == "a b c"


def test_truncate():
    assert truncate("hello world", 5) == "hell…"
    assert truncate("hi", 10) == "hi"


def test_count_tokens_approx():
    text = "a" * 400  # 400 chars → ~100 tokens
    assert count_tokens_approx(text) == 100


def test_clean_text():
    text = "hello\x00world\x07"
    result = clean_text(text)
    assert "\x00" not in result
    assert "hello" in result
    assert "world" in result
