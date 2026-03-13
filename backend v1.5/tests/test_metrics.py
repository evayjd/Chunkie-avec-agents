"""Unit tests for evaluation metrics."""
import pytest
from benchmarks.metrics import (
    recall_at_k,
    precision_at_k,
    mrr,
    ndcg_at_k,
    hit_rate,
    compute_all_metrics,
)


def test_recall_perfect():
    assert recall_at_k({"a", "b"}, ["a", "b", "c"], 3) == 1.0


def test_recall_partial():
    assert recall_at_k({"a", "b", "c"}, ["a", "x", "y"], 3) == pytest.approx(1/3)


def test_precision_at_k():
    assert precision_at_k({"a", "b"}, ["a", "x", "b", "y"], 2) == 0.5


def test_mrr_first_hit():
    assert mrr({"a"}, ["a", "b", "c"]) == 1.0


def test_mrr_second_hit():
    assert mrr({"b"}, ["a", "b", "c"]) == pytest.approx(0.5)


def test_hit_rate():
    assert hit_rate({"c"}, ["a", "b", "c"], k=3) == 1.0
    assert hit_rate({"d"}, ["a", "b", "c"], k=3) == 0.0


def test_ndcg_perfect():
    score = ndcg_at_k({"a", "b"}, ["a", "b", "c"], k=3)
    assert score > 0.9


def test_compute_all_metrics():
    metrics = compute_all_metrics({"a", "b"}, ["a", "x", "b"], k=3)
    assert "recall@3" in metrics
    assert "precision@3" in metrics
    assert "mrr" in metrics
    assert "ndcg@3" in metrics
    assert "hit_rate@3" in metrics
