import json
from pathlib import Path
from backend.services.retrieval.retriever_factory import get_retriever
from backend.core.retrieval_config import RETRIEVAL_METHOD
from backend.core.database import SessionLocal

from evaluation.metrics import recall_at_k
from backend.core.retrieval_config import RETRIEVAL_METHOD

DATASET = "evaluation/dataset.json"


RESULT_FILE = f"evaluation/results/{RETRIEVAL_METHOD}_benchmark_results.json"

METHOD = RETRIEVAL_METHOD


def run():

    with open(DATASET) as f:
        dataset = json.load(f)

    db = SessionLocal()

    retriever = get_retriever(METHOD, db)

    scores = []

    for item in dataset:

        chunks = retriever.retrieve(
            question=item["question"],
            top_k=5
        )

        retrieved_ids = [
            c["chunk_id"] for c in chunks
        ]

        relevant_ids = item["relevant_chunk_ids"]

        score = recall_at_k(
            retrieved_ids,
            relevant_ids,
            5
        )

        scores.append(score)

    result = {

        "benchmark_score": sum(scores)/len(scores)

    }

    Path("evaluation/results").mkdir(exist_ok=True)

    with open(RESULT_FILE, "w") as f:
        json.dump(result, f, indent=2)

    print(result)


if __name__ == "__main__":

    run()