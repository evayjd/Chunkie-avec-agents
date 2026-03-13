from typing import List, Optional
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.orm import Session

from backend.services.retrieval.base_retriever import BaseRetriever
from backend.services.ingestion.embedding.embedder import get_embedder


class HybridRetriever(BaseRetriever):
    """
    Hybrid Retrieval — 升级版
    Vector search + Keyword search，通过 RRF 融合排名。

    升级内容：
    1. RRF rank 修正为 1-indexed（原代码 rank 从 0 开始，现改为 rank+1）。
    2. 新增 alpha 权重参数（默认 0.7 向量 / 0.3 关键词），在 RRF 分数上乘以权重，
       让向量检索结果在融合后更具主导性，同时保留关键词对精确名词的贡献。
    """

    def __init__(self, db: Session, alpha: float = 0.7):
        self.db = db
        self.embedder = get_embedder()
        self.rrf_k = 60
        # alpha: 向量检索权重；(1-alpha): 关键词检索权重
        self.alpha = max(0.0, min(1.0, alpha))

    # --------------------------------------------------
    # vector search
    # --------------------------------------------------

    def vector_search(
        self,
        query_vector: List[float],
        document_ids: Optional[List[str]],
        top_k: int,
    ) -> List[dict]:

        sql = """
        SELECT
            id,
            document_id,
            chunk_index,
            content,
            page_start,
            page_end,
            section,
            embedding <=> CAST(:query_vector AS vector) AS score
        FROM chunks
        """

        params: dict = {
            "query_vector": self._vector_to_pg(query_vector),
            "top_k": top_k,
        }

        uuid_doc_ids = self._parse_doc_ids(document_ids)
        if uuid_doc_ids:
            sql += " WHERE document_id = ANY(:doc_ids)"
            params["doc_ids"] = uuid_doc_ids

        sql += """
        ORDER BY embedding <=> CAST(:query_vector AS vector)
        LIMIT :top_k
        """

        rows = self.db.execute(text(sql), params).fetchall()

        return [
            {
                "chunk_id": str(r.id),
                "doc_id": str(r.document_id),
                "chunk_index": r.chunk_index,
                "content": r.content,
                "page_start": r.page_start,
                "page_end": r.page_end,
                "section": r.section,
                "rank": rank,
            }
            for rank, r in enumerate(rows)
        ]

    # --------------------------------------------------
    # keyword search
    # --------------------------------------------------

    def keyword_search(
        self,
        question: str,
        document_ids: Optional[List[str]],
        top_k: int,
    ) -> List[dict]:

        sql = """
        SELECT
            id,
            document_id,
            chunk_index,
            content,
            page_start,
            page_end,
            section,
            ts_rank(tsv, plainto_tsquery('simple', :query)) AS score
        FROM chunks
        WHERE tsv @@ plainto_tsquery('simple', :query)
        """

        params: dict = {"query": question, "top_k": top_k}

        uuid_doc_ids = self._parse_doc_ids(document_ids)
        if uuid_doc_ids:
            sql += " AND document_id = ANY(:doc_ids)"
            params["doc_ids"] = uuid_doc_ids

        sql += """
        ORDER BY score DESC
        LIMIT :top_k
        """

        rows = self.db.execute(text(sql), params).fetchall()

        return [
            {
                "chunk_id": str(r.id),
                "doc_id": str(r.document_id),
                "chunk_index": r.chunk_index,
                "content": r.content,
                "page_start": r.page_start,
                "page_end": r.page_end,
                "section": r.section,
                "rank": rank,
            }
            for rank, r in enumerate(rows)
        ]

    # --------------------------------------------------
    # RRF fusion（修正 rank 索引 + alpha 权重）
    # --------------------------------------------------

    def fuse_results(
        self,
        vector_results: List[dict],
        keyword_results: List[dict],
    ) -> List[dict]:
        scores: dict = {}

        def add_score(results: List[dict], weight: float) -> None:
            for r in results:
                key = r["chunk_id"]
                rank = r["rank"]
                # 修复 Bug 3：rank 从 0 开始，RRF 标准公式需 +1 变为 1-indexed
                rrf_score = weight / (self.rrf_k + rank + 1)
                if key not in scores:
                    scores[key] = {"score": 0.0, "data": r}
                scores[key]["score"] += rrf_score

        add_score(vector_results, self.alpha)
        add_score(keyword_results, 1.0 - self.alpha)

        fused = sorted(scores.values(), key=lambda x: x["score"], reverse=True)
        return [f["data"] for f in fused]

    # --------------------------------------------------
    # main retrieve
    # --------------------------------------------------

    def retrieve(
        self,
        question: str,
        document_ids: Optional[List[str]] = None,
        top_k: int = 5,
    ) -> List[dict]:

        if not question or not question.strip():
            return []

        top_k = max(1, top_k)

        query_vector = self.embedder.embed_query(question)

        vector_results = self.vector_search(query_vector, document_ids, top_k * 2)
        keyword_results = self.keyword_search(question, document_ids, top_k * 2)

        fused = self.fuse_results(vector_results, keyword_results)
        final = fused[:top_k]

        return [
            {
                "citation_id": i,
                "chunk_id": r["chunk_id"],
                "doc_id": r["doc_id"],
                "chunk_index": r["chunk_index"],
                "content": r["content"],
                "page_start": r["page_start"],
                "page_end": r["page_end"],
                "section": r["section"],
            }
            for i, r in enumerate(final, start=1)
        ]

    # --------------------------------------------------
    # helpers
    # --------------------------------------------------

    def _vector_to_pg(self, vector: List[float]) -> str:
        return "[" + ",".join(str(float(x)) for x in vector) + "]"

    def _parse_doc_ids(self, document_ids: Optional[List[str]]) -> List[UUID]:
        if not document_ids:
            return []
        result = []
        for doc_id in document_ids:
            try:
                result.append(UUID(str(doc_id)))
            except Exception:
                continue
        return result
