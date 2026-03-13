"""Unit tests for document chunker."""
import pytest
from app.pipelines.chunker import sliding_window_chunks


def test_basic_chunking():
    text = " ".join([f"word{i}" for i in range(200)])
    chunks = sliding_window_chunks(text, chunk_size=50, overlap=10, min_length=10, max_length=1000)
    assert len(chunks) > 1
    assert all("text" in c for c in chunks)
    assert all("chunk_index" in c for c in chunks)


def test_short_text():
    text = "这是一段很短的文本用于测试。"
    chunks = sliding_window_chunks(text, chunk_size=50, overlap=5, min_length=5, max_length=200)
    assert len(chunks) >= 1


def test_overlap_creates_more_chunks():
    text = " ".join([f"word{i}" for i in range(100)])
    chunks_no_overlap = sliding_window_chunks(text, chunk_size=20, overlap=0, min_length=5, max_length=500)
    chunks_with_overlap = sliding_window_chunks(text, chunk_size=20, overlap=10, min_length=5, max_length=500)
    assert len(chunks_with_overlap) >= len(chunks_no_overlap)


def test_chunk_indices_sequential():
    text = " ".join([f"word{i}" for i in range(150)])
    chunks = sliding_window_chunks(text, chunk_size=30, overlap=5, min_length=5, max_length=500)
    indices = [c["chunk_index"] for c in chunks]
    assert indices == list(range(len(chunks)))
