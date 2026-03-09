import json
import requests
from pathlib import Path
from backend.core.retrieval_config import RETRIEVAL_METHOD
from evaluation.metrics import keyword_score, citation_score

API_URL = "http://localhost:8000/ask"

DATASET = "evaluation/dataset.json"

RESULT_FILE = "evaluation/results/generation_results.json"





# 根据 method 自动生成文件名
RESULT_FILE = f"evaluation/results/{RETRIEVAL_METHOD}_generation_results.json"

def run():

    with open(DATASET) as f:

        dataset = json.load(f)

    answer_scores = []
    citation_scores = []

    for item in dataset:

        res = requests.post(
            API_URL,
            json={
                "question": item["question"],
                "top_k": 5
            }
        )

        data = res.json()

        answer = data["answer"]

        citations = data["citations"]

        answer_scores.append(
            keyword_score(
                answer,
                item["expected_keywords"]
            )
        )

        citation_scores.append(
            citation_score(citations)
        )

    results = {

        "answer_score": sum(answer_scores)/len(answer_scores),
        "citation_score": sum(citation_scores)/len(citation_scores)

    }

    Path("evaluation/results").mkdir(exist_ok=True)

    with open(RESULT_FILE, "w") as f:

        json.dump(results, f, indent=2)

    print(results)


if __name__ == "__main__":

    run()