"""Chunk repository — stores and retrieves document chunks with embeddings."""
 
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from pgvector.sqlalchemy import Vector

from app.models.chunk import Chunk


class ChunkRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def bulk_create(self, chunks: list[dict]) -> list[Chunk]:
        objs = [Chunk(**c) for c in chunks]
        self._db.add_all(objs)
        await self._db.flush()
        return objs

    async def get_by_document(self, doc_id: str) -> list[Chunk]:
        result = await self._db.execute(
            select(Chunk)
            .where(Chunk.document_id == doc_id)
            .order_by(Chunk.chunk_index)
        )
        return list(result.scalars().all())

    async def delete_by_document(self, doc_id: str) -> int:
        result = await self._db.execute(
            delete(Chunk).where(Chunk.document_id == doc_id)
        )
        return result.rowcount  # type: ignore[return-value]

    async def similarity_search(
        self,
        query_vector: list[float],
        document_ids: list[str] | None,
        top_k: int = 20,
    ) -> list[Chunk]:
        """Cosine similarity search via pgvector."""
        stmt = select(Chunk).order_by(
            Chunk.embedding.cosine_distance(query_vector)
        )
        if document_ids:
            stmt = stmt.where(Chunk.document_id.in_(document_ids))
        stmt = stmt.limit(top_k)
        result = await self._db.execute(stmt)
        return list(result.scalars().all())

    async def similarity_search_with_scores(
        self,
        query_vector: list[float],
        document_ids: list[str] | None,
        top_k: int = 20,
    ) -> list[tuple[Chunk, float]]:
        """Cosine similarity search via pgvector, returns (chunk, similarity) pairs.

        pgvector cosine_distance = 1 - cosine_similarity, so similarity = 1 - distance.
        For normalized embeddings the range is [0, 1].
        """
        cosine_dist = Chunk.embedding.cosine_distance(query_vector).label("_dist")
        stmt = select(Chunk, cosine_dist).order_by(cosine_dist)
        if document_ids:
            stmt = stmt.where(Chunk.document_id.in_(document_ids))
        stmt = stmt.limit(top_k)
        result = await self._db.execute(stmt)
        rows = result.all()
        return [(row[0], float(1.0 - row[1])) for row in rows]

    async def count_by_document(self, doc_id: str) -> int:
        from sqlalchemy import func
        result = await self._db.execute(
            select(func.count()).select_from(Chunk).where(Chunk.document_id == doc_id)
        )
        return result.scalar_one()
