from typing import List


# --------------------------------------------------
# Retrieval Metrics
# --------------------------------------------------

def precision_at_k(
    retrieved_ids: List[str],
    relevant_ids: List[str],
    k: int
) -> float:
    """
    Precision@K
    top-k 结果中有多少是 relevant
    """

    if k == 0:
        return 0.0

    retrieved_k = retrieved_ids[:k]

    hits = sum(
        1 for r in retrieved_k
        if r in relevant_ids
    )

    return hits / k


def recall_at_k(
    retrieved_ids: List[str],
    relevant_ids: List[str],
    k: int
) -> float:
    """
    Recall@K
    relevant 文档有多少被召回
    """

    if not relevant_ids:
        return 0.0

    retrieved_k = retrieved_ids[:k]

    hits = sum(
        1 for r in relevant_ids
        if r in retrieved_k
    )

    return hits / len(relevant_ids)


def hit_rate(
    retrieved_ids: List[str],
    relevant_ids: List[str]
) -> float:
    """
    Hit Rate
    是否至少命中一个 relevant
    """

    for r in relevant_ids:
        if r in retrieved_ids:
            return 1.0

    return 0.0


def mrr(
    retrieved_ids: List[str],
    relevant_ids: List[str]
) -> float:
    """
    Mean Reciprocal Rank
    第一条 relevant 文档排名
    """

    for i, doc_id in enumerate(retrieved_ids):

        if doc_id in relevant_ids:
            return 1 / (i + 1)

    return 0.0


# --------------------------------------------------
# Generation Metrics
# --------------------------------------------------

def keyword_score(
    answer: str,
    keywords: List[str]
) -> float:
    """
    Answer correctness
    判断回答是否包含关键概念
    """

    if not answer:
        return 0.0

    answer_lower = answer.lower()

    hits = sum(
        1 for k in keywords
        if k.lower() in answer_lower
    )

    return hits / len(keywords)


def citation_score(
    citations,
    ideal_citations: int = 5
) -> float:
    """
    Citation completeness
    """

    if not citations:
        return 0.0

    return min(len(citations) / ideal_citations, 1.0)


# --------------------------------------------------
# Combined RAG Score
# --------------------------------------------------

def rag_score(
    answer: str,
    keywords: List[str],
    citations
) -> float:
    """
    综合RAG评分
    """

    k_score = keyword_score(answer, keywords)

    c_score = citation_score(citations)

    return (k_score * 0.7) + (c_score * 0.3)