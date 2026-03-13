"""RAG evaluation metrics: Recall@K, Precision@K, MRR, NDCG, Hit Rate."""
 
import math
from typing import Any


def recall_at_k(relevant: set[str], retrieved: list[str], k: int) -> float:
    if not relevant:
        return 0.0
    hits = sum(1 for r in retrieved[:k] if r in relevant)
    return hits / len(relevant)


def precision_at_k(relevant: set[str], retrieved: list[str], k: int) -> float:
    if k == 0:
        return 0.0
    hits = sum(1 for r in retrieved[:k] if r in relevant)
    return hits / k


def mrr(relevant: set[str], retrieved: list[str]) -> float:
    for rank, item in enumerate(retrieved, start=1):
        if item in relevant:
            return 1.0 / rank
    return 0.0


def ndcg_at_k(relevant: set[str], retrieved: list[str], k: int) -> float:
    def dcg(items: list[str], k: int) -> float:
        return sum(
            (1 if item in relevant else 0) / math.log2(i + 2)
            for i, item in enumerate(items[:k])
        )

    actual = dcg(retrieved, k)
    ideal_items = list(relevant)[:k]
    ideal = dcg(ideal_items, k)
    return actual / ideal if ideal > 0 else 0.0


def hit_rate(relevant: set[str], retrieved: list[str], k: int) -> float:
    return 1.0 if any(r in relevant for r in retrieved[:k]) else 0.0


def compute_all_metrics(
    relevant: set[str], retrieved: list[str], k: int = 5
) -> dict[str, float]:
    return {
        f"recall@{k}": recall_at_k(relevant, retrieved, k),
        f"precision@{k}": precision_at_k(relevant, retrieved, k),
        "mrr": mrr(relevant, retrieved),
        f"ndcg@{k}": ndcg_at_k(relevant, retrieved, k),
        f"hit_rate@{k}": hit_rate(relevant, retrieved, k),
    }
