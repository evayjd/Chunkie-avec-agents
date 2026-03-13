import math
from typing import List, Optional

from backend.services.retrieval.base_retriever import BaseRetriever
from backend.services.ranking.cross_encoder_reranker import get_reranker


class RerankRetriever(BaseRetriever):
    """
    Rerank Retriever — 升级版

    升级内容：
    在 cross-encoder 重排之后，增加 MMR（Maximum Marginal Relevance）多样性过滤。
    MMR 在保持相关性的同时减少结果中的冗余，适合文档内容有重叠时提升覆盖面。

    参数：
    - mmr_lambda: 相关性 vs 多样性权衡系数（默认 0.7，越高越倾向相关性）
    - mmr_candidate_k: 从 rerank 结果中取前 N 个作为 MMR 候选池
    """

    def __init__(self, base_retriever, mmr_lambda: float = 0.7, mmr_candidate_k: int = 20):
        self.base_retriever = base_retriever
        self.reranker = get_reranker()
        self.mmr_lambda = mmr_lambda
        self.mmr_candidate_k = mmr_candidate_k

    # --------------------------------------------------
    # token-level Jaccard 相似度（轻量级，无需额外依赖）
    # --------------------------------------------------

    @staticmethod
    def _token_set(text: str) -> set:
        return set(re.split(r"\W+", text.lower())) - {""} if text else set()

    @staticmethod
    def _jaccard(a: set, b: set) -> float:
        if not a or not b:
            return 0.0
        return len(a & b) / len(a | b)

    # --------------------------------------------------
    # MMR re-ranking
    # --------------------------------------------------

    def _mmr(self, docs: List[dict], top_k: int) -> List[dict]:
        """
        MMR 选择：每次从候选池中选出与已选集合最不相似、且与 query 最相关的文档。
        这里用 reranker 给出的列表位置作为相关性代理（位置越靠前相关性越高）。
        """
        if not docs or top_k <= 0:
            return []

        n = len(docs)
        # 相关性分数：归一化为 [0, 1]，位置越靠前分数越高
        relevance = {i: 1.0 - i / n for i in range(n)}

        token_sets = [self._token_set(d.get("content", "")) for d in docs]

        selected_indices: List[int] = []
        candidate_indices = list(range(n))

        while len(selected_indices) < top_k and candidate_indices:
            best_idx = None
            best_score = -math.inf

            for idx in candidate_indices:
                rel = relevance[idx]

                # 与已选集合中最相似的文档的相似度（冗余惩罚）
                if selected_indices:
                    max_sim = max(
                        self._jaccard(token_sets[idx], token_sets[s])
                        for s in selected_indices
                    )
                else:
                    max_sim = 0.0

                mmr_score = self.mmr_lambda * rel - (1.0 - self.mmr_lambda) * max_sim

                if mmr_score > best_score:
                    best_score = mmr_score
                    best_idx = idx

            if best_idx is None:
                break

            selected_indices.append(best_idx)
            candidate_indices.remove(best_idx)

        # 按选取顺序重新编号 citation_id
        results = []
        for new_i, orig_i in enumerate(selected_indices, start=1):
            doc = dict(docs[orig_i])
            doc["citation_id"] = new_i
            results.append(doc)

        return results

    # --------------------------------------------------
    # retrieve
    # --------------------------------------------------

    def retrieve(
        self,
        question: str,
        document_ids: Optional[List[str]] = None,
        top_k: int = 5,
    ) -> List[dict]:

        # 从 base retriever 取更多候选
        candidate_k = max(self.mmr_candidate_k, top_k * 3)
        docs = self.base_retriever.retrieve(question, document_ids, top_k=candidate_k)

        # cross-encoder 重排
        docs = self.reranker.rerank(question, docs)

        # MMR 多样性过滤，从重排结果的前 mmr_candidate_k 中选 top_k
        candidates = docs[:self.mmr_candidate_k]
        return self._mmr(candidates, top_k)


# 延迟导入避免循环依赖
import re  # noqa: E402
