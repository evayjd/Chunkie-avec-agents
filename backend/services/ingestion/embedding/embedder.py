from typing import List, Optional

from sentence_transformers import SentenceTransformer

from backend.core.config import settings

# ---------------------------------------------------------------------------
# Singleton：整个进程只加载一次 embedding 模型，避免重复占用内存和 GPU
# ---------------------------------------------------------------------------
_embedder_instance: Optional["Embedder"] = None


def get_embedder() -> "Embedder":
    global _embedder_instance
    if _embedder_instance is None:
        _embedder_instance = Embedder()
    return _embedder_instance


class Embedder:
    """
    Embedding module

    Responsibility:
    text -> embedding vector

    Supports:
    - batch embedding
    - query embedding

    推荐通过 get_embedder() 获取单例，不要直接实例化。
    """

    def __init__(self):
        # load local embedding model
        self.model = SentenceTransformer(settings.EMBEDDING_MODEL)

    # --------------------------------------------------
    # 批量 batch embedding
    # --------------------------------------------------

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []

        # 过滤空字符串，保留原始索引对应关系
        non_empty = [(i, t) for i, t in enumerate(texts) if t and t.strip()]
        if not non_empty:
            return [[] for _ in texts]

        indices, valid_texts = zip(*non_empty)
        vectors = self.model.encode(
            list(valid_texts),
            normalize_embeddings=True,
            batch_size=64,
            show_progress_bar=False,
        )

        result: List[List[float]] = [[] for _ in texts]
        for idx, vec in zip(indices, vectors):
            result[idx] = vec.tolist()

        return result

    # --------------------------------------------------
    # query embedding
    # --------------------------------------------------

    def embed_query(self, query: str) -> List[float]:
        vector = self.model.encode(
            query,
            normalize_embeddings=True,
        )
        return vector.tolist()
