import json
import requests
from datetime import datetime
from pathlib import Path

from metrics import keyword_score, citation_score


API_URL = "http://localhost:8000/ask"

BASE_DIR = Path(__file__).parent
DATASET_PATH = BASE_DIR / "dataset.json"
RESULT_DIR = BASE_DIR / "results"


def save_results(results):

    RESULT_DIR.mkdir(parents=True, exist_ok=True)

    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")

    output_file = RESULT_DIR / f"run_{run_id}.json"

    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)

    print("Benchmark saved:", output_file)


def run():

    if not DATASET_PATH.exists():
        raise FileNotFoundError(f"Dataset not found: {DATASET_PATH}")

    with open(DATASET_PATH) as f:
        dataset = json.load(f)

    scores = []
    details = []

    for item in dataset:

        question = item["question"]

        res = requests.post(
            API_URL,
            json={
                "question": question,
                "document_ids": None,
                "top_k": 5
            },
            timeout=60
        )

        if res.status_code != 200:
            print("API ERROR:", res.status_code)
            print(res.text)
            continue

        data = res.json()

        answer = data.get("answer", "")
        citations = data.get("citations", [])

        k_score = keyword_score(answer, item["expected_keywords"])
        c_score = citation_score(citations)

        total = (k_score * 0.7) + (c_score * 0.3)

        scores.append(total)

        details.append({
            "question": question,
            "answer": answer,
            "keyword_score": k_score,
            "citation_score": c_score,
            "total_score": total
        })

        print("Q:", question)
        print("Score:", total)
        print()

    avg = sum(scores) / len(scores) if scores else 0

    print("FINAL SCORE:", avg)

    results = {
        "run_time": datetime.now().isoformat(),
        "dataset_size": len(dataset),
        "average_score": avg,
        "details": details
    }

    save_results(results)


if __name__ == "__main__":
    run()