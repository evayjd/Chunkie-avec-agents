from typing import List
from sentence_transformers import SentenceTransformer

from backend.core.config import settings


class Embedder:
    """
    Embedding module

    Responsibility:
    text -> embedding vector

    Supports:
    - batch embedding
    - query embedding
    """

    def __init__(self):

        # load local embedding model
        self.model = SentenceTransformer(settings.EMBEDDING_MODEL)

    # --------------------------------------------------
    # 批量batch embedding
    # --------------------------------------------------

    def embed_texts(self, texts: List[str]) -> List[List[float]]:

        if not texts:
            return []

        vectors = self.model.encode(
            texts,
            normalize_embeddings=True
        )

        return vectors.tolist()

    # --------------------------------------------------
    # query embedding
    # --------------------------------------------------

    def embed_query(self, query: str) -> List[float]:

        vector = self.model.encode(
            query,
            normalize_embeddings=True
        )

        return vector.tolist()