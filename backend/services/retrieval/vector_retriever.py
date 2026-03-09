from typing import List, Optional
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.orm import Session
from backend.services.retrieval.base_retriever import BaseRetriever

from backend.services.ingestion.embedding.embedder import Embedder


class VectorRetriever(BaseRetriever):
    """
    向量检索模块
    """

    def __init__(self, db: Session):
        self.db = db
        self.embedder = Embedder()

    # --------------------------------------------------
    # vector search
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

        sql = """
        SELECT
            id,
            document_id,
            chunk_index,
            content,
            page_start,
            page_end,
            section,
            embedding <=> CAST(:query_vector AS vector) AS distance
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

        for i, r in enumerate(rows, start=1):
            results.append({
                "citation_id": i,
                "chunk_id": str(r.id),
                "doc_id": str(r.document_id),
                "chunk_index": r.chunk_index,
                "content": r.content,
                "page_start": r.page_start,
                "page_end": r.page_end,
                "section": r.section,
            })

        return results

    # --------------------------------------------------
    # helper
    # --------------------------------------------------

    def _vector_to_pg(self, vector: List[float]) -> str:
        """
        将 Python list[float] 转成 pgvector 可接受的字符串格式:
        [0.1,0.2,0.3]
        """
        return "[" + ",".join(str(float(x)) for x in vector) + "]"