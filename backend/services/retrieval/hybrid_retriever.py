from typing import List, Optional
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.orm import Session

from backend.services.retrieval.base_retriever import BaseRetriever
from backend.services.ingestion.embedding.embedder import Embedder


class HybridRetriever(BaseRetriever):
    """
    Hybrid Retrieval
    Vector search + Keyword search
    """

    def __init__(self, db: Session):

        self.db = db
        self.embedder = Embedder()

        # RRF parameter
        self.rrf_k = 60

    # --------------------------------------------------
    # vector search
    # --------------------------------------------------

    def vector_search(
        self,
        query_vector: List[float],
        document_ids: Optional[List[str]],
        top_k: int
    ):

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

        params = {
            "query_vector": self._vector_to_pg(query_vector),
            "top_k": top_k
        }

        uuid_doc_ids: List[UUID] = []
        if document_ids:
            for doc_id in document_ids:
                try:
                    uuid_doc_ids.append(UUID(str(doc_id)))
                except Exception:
                    continue

        if uuid_doc_ids:
            sql += " WHERE document_id = ANY(:doc_ids)"
            params["doc_ids"] = uuid_doc_ids

        sql += """
        ORDER BY embedding <=> CAST(:query_vector AS vector)
        LIMIT :top_k
        """

        rows = self.db.execute(text(sql), params).fetchall()

        results = []

        for rank, r in enumerate(rows):
            results.append({
                "chunk_id": str(r.id),
                "doc_id": str(r.document_id),
                "chunk_index": r.chunk_index,
                "content": r.content,
                "page_start": r.page_start,
                "page_end": r.page_end,
                "section": r.section,
                "rank": rank
            })

        return results

    # --------------------------------------------------
    # keyword search
    # --------------------------------------------------

    def keyword_search(
        self,
        question: str,
        document_ids: Optional[List[str]],
        top_k: int
    ):

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

        params = {
            "query": question,
            "top_k": top_k
        }

        uuid_doc_ids: List[UUID] = []
        if document_ids:
            for doc_id in document_ids:
                try:
                    uuid_doc_ids.append(UUID(str(doc_id)))
                except Exception:
                    continue

        if uuid_doc_ids:
            sql += " AND document_id = ANY(:doc_ids)"
            params["doc_ids"] = uuid_doc_ids

        sql += """
        ORDER BY score DESC
        LIMIT :top_k
        """

        rows = self.db.execute(text(sql), params).fetchall()

        results = []

        for rank, r in enumerate(rows):
            results.append({
                "chunk_id": str(r.id),
                "doc_id": str(r.document_id),
                "chunk_index": r.chunk_index,
                "content": r.content,
                "page_start": r.page_start,
                "page_end": r.page_end,
                "section": r.section,
                "rank": rank
            })

        return results

    # --------------------------------------------------
    # RRF fusion
    # --------------------------------------------------

    def fuse_results(self, vector_results, keyword_results):

        scores = {}

        def add_score(results):

            for r in results:

                key = r["chunk_id"]

                rank = r["rank"]

                score = 1 / (self.rrf_k + rank)

                if key not in scores:
                    scores[key] = {"score": 0, "data": r}

                scores[key]["score"] += score

        add_score(vector_results)
        add_score(keyword_results)

        fused = list(scores.values())

        fused.sort(key=lambda x: x["score"], reverse=True)

        return [f["data"] for f in fused]

    # --------------------------------------------------
    # main retrieve
    # --------------------------------------------------

    def retrieve(
        self,
        question: str,
        document_ids: Optional[List[str]] = None,
        top_k: int = 5
    ) -> List[dict]:

        if not question or not question.strip():
            return []

        if top_k <= 0:
            top_k = 5

        query_vector = self.embedder.embed_query(question)

        vector_results = self.vector_search(
            query_vector,
            document_ids,
            top_k * 2
        )

        keyword_results = self.keyword_search(
            question,
            document_ids,
            top_k * 2
        )

        fused = self.fuse_results(vector_results, keyword_results)

        final = fused[:top_k]

        results = []

        for i, r in enumerate(final, start=1):

            results.append({
                "citation_id": i,
                "chunk_id": r["chunk_id"],
                "doc_id": r["doc_id"],
                "chunk_index": r["chunk_index"],
                "content": r["content"],
                "page_start": r["page_start"],
                "page_end": r["page_end"],
                "section": r["section"]
            })

        return results

    # --------------------------------------------------
    # helper
    # --------------------------------------------------

    def _vector_to_pg(self, vector: List[float]) -> str:
        """
        convert python list to pgvector string
        """
        return "[" + ",".join(str(float(x)) for x in vector) + "]"