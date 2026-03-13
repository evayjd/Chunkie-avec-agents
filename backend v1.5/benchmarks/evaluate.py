"""Evaluation runner: load fixtures, run retrieval, compute metrics."""
 
import asyncio
import json
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from benchmarks.metrics import compute_all_metrics


async def run_evaluation(fixture_path: str, top_k: int = 5) -> dict:
    """Run evaluation on a fixture file."""
    from app.db.session import async_session_factory
    from app.pipelines.retrieval import run_retrieval_pipeline

    fixture = json.loads(Path(fixture_path).read_text())
    results = []

    async with async_session_factory() as db:
        for case in fixture:
            query = case["query"]
            relevant_ids = set(case.get("relevant_chunk_ids", []))

            chunks, timing = await run_retrieval_pipeline(db, query)
            retrieved_ids = [c["chunk_id"] for c in chunks]

            metrics = compute_all_metrics(relevant_ids, retrieved_ids, k=top_k)
            results.append(
                {
                    "query": query,
                    "metrics": metrics,
                    "timing_ms": timing.get("total", 0) * 1000,
                }
            )

    # Aggregate
    agg: dict[str, list[float]] = {}
    for r in results:
        for k, v in r["metrics"].items():
            agg.setdefault(k, []).append(v)

    summary = {k: sum(v) / len(v) for k, v in agg.items()}
    return {"summary": summary, "details": results, "n_queries": len(results)}


if __name__ == "__main__":
    fixture = sys.argv[1] if len(sys.argv) > 1 else "benchmarks/data/sample_queries.json"
    result = asyncio.run(run_evaluation(fixture))
    print(json.dumps(result, ensure_ascii=False, indent=2))
