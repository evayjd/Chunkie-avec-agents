from typing import List
from uuid import UUID

from sqlalchemy.orm import Session

from backend.db.repositories.chunk_repo import ChunkRepository


class VectorIndexer:
    """
    向量索引模块

    职责：
    将 chunk + embedding 写入数据库
    """

    def __init__(self, db: Session):

        self.db = db
        self.chunk_repo = ChunkRepository(db)

    # --------------------------------------------------
    # 写入 chunk
    # --------------------------------------------------

    def index_chunks(
        self,
        document_id: UUID,
        chunks: List[dict],
        embeddings: List[List[float]]
    ):

        chunk_records = []

        for chunk, vector in zip(chunks, embeddings):

            record = {
                "id": UUID(chunk["chunk_id"]),
                "document_id": document_id,
                "chunk_index": chunk["chunk_index"],
                "content": chunk["content"],
                "page_start": chunk.get("page_start"),
                "page_end": chunk.get("page_end"),
                "section": chunk.get("section"),
                "metadata_json": chunk.get("metadata"),
                "embedding": vector
            }

            chunk_records.append(record)

        self.chunk_repo.create_chunks(chunk_records)