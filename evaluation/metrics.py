from typing import List


def keyword_score(answer: str, keywords: List[str]) -> float:

    if not answer:
        return 0.0

    answer_lower = answer.lower()

    hits = 0

    for k in keywords:

        if k.lower() in answer_lower:
            hits += 1

    return hits / len(keywords)


def citation_score(citations):

    if not citations:
        return 0.0

    return min(len(citations) / 5, 1.0)