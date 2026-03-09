import json
from pathlib import Path
from backend.core.retrieval_config import RETRIEVAL_METHOD

from backend.services.retrieval.retriever_factory import get_retriever
from backend.core.retrieval_config import RETRIEVAL_METHOD
from backend.core.database import SessionLocal

from evaluation.metrics import (
    precision_at_k,
    recall_at_k,
    hit_rate,
    mrr
)


DATASET = "evaluation/dataset.json"

RESULT_FILE = f"evaluation/results/{RETRIEVAL_METHOD}_retrieval_results.json"
METHOD = RETRIEVAL_METHOD

def run():

    with open(DATASET) as f:
        dataset = json.load(f)

    db = SessionLocal()

    retriever = get_retriever(METHOD, db)

    p_scores = []
    r_scores = []
    hr_scores = []
    mrr_scores = []

    for item in dataset:

        chunks = retriever.retrieve(
            question=item["question"],
            top_k=5
        )

        retrieved_ids = [
            c["chunk_id"] for c in chunks
        ]

        relevant_ids = item["relevant_chunk_ids"]

        p_scores.append(
            precision_at_k(retrieved_ids, relevant_ids, 5)
        )

        r_scores.append(
            recall_at_k(retrieved_ids, relevant_ids, 5)
        )

        hr_scores.append(
            hit_rate(retrieved_ids, relevant_ids)
        )

        mrr_scores.append(
            mrr(retrieved_ids, relevant_ids)
        )

    results = {

        "precision@5": sum(p_scores)/len(p_scores),
        "recall@5": sum(r_scores)/len(r_scores),
        "hit_rate": sum(hr_scores)/len(hr_scores),
        "mrr": sum(mrr_scores)/len(mrr_scores)

    }

    Path("evaluation/results").mkdir(exist_ok=True)

    with open(RESULT_FILE, "w") as f:
        json.dump(results, f, indent=2)

    print(results)


if __name__ == "__main__":
    run()