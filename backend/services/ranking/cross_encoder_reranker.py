from typing import List, Optional

from sentence_transformers import CrossEncoder

# ---------------------------------------------------------------------------
# Singleton：整个进程只加载一次 cross-encoder 模型
# ---------------------------------------------------------------------------
_reranker_instance: Optional["CrossEncoderReranker"] = None


def get_reranker() -> "CrossEncoderReranker":
    global _reranker_instance
    if _reranker_instance is None:
        _reranker_instance = CrossEncoderReranker()
    return _reranker_instance


class CrossEncoderReranker:
    """
    Cross-encoder 精排模块。

    推荐通过 get_reranker() 获取单例，不要直接实例化。
    """

    def __init__(self):
        self.model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

    def rerank(self, question: str, docs: List[dict]) -> List[dict]:
        if not docs:
            return docs

        pairs = [(question, d.get("content", "")) for d in docs]
        scores = self.model.predict(pairs)

        for doc, score in zip(docs, scores):
            doc["rerank_score"] = float(score)

        docs.sort(key=lambda x: x["rerank_score"], reverse=True)

        # 重新分配 citation_id（按新排名）
        for i, doc in enumerate(docs, start=1):
            doc["citation_id"] = i

        return docs
