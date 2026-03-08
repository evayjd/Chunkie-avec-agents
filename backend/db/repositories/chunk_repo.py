from typing import List, Optional
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from backend.db.models import Chunk


class ChunkRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_chunks(self, chunks_data: List[dict]) -> List[Chunk]:
        chunks = [Chunk(**item) for item in chunks_data]
        self.db.add_all(chunks)
        self.db.commit()

        for chunk in chunks:
            self.db.refresh(chunk)

        return chunks

    def list_by_document_id(self, document_id: UUID) -> List[Chunk]:
        stmt = (
            select(Chunk)
            .where(Chunk.document_id == document_id)
            .order_by(Chunk.chunk_index.asc())
        )
        return list(self.db.execute(stmt).scalars().all())

    def delete_by_document_id(self, document_id: UUID) -> int:
        stmt = delete(Chunk).where(Chunk.document_id == document_id)
        result = self.db.execute(stmt)
        self.db.commit()
        return result.rowcount or 0

    def get_by_id(self, chunk_id: UUID) -> Optional[Chunk]:
        stmt = select(Chunk).where(Chunk.id == chunk_id)
        return self.db.execute(stmt).scalar_one_or_none()