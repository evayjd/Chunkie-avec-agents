"""Document repository — async CRUD."""
 
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document
from app.core.constants import DocumentStatus


class DocumentRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def create(self, **kwargs) -> Document:
        doc = Document(**kwargs)
        self._db.add(doc)
        await self._db.flush()
        await self._db.refresh(doc)
        return doc

    async def get(self, doc_id: str) -> Document | None:
        result = await self._db.execute(select(Document).where(Document.id == doc_id))
        return result.scalar_one_or_none()

    async def list_all(self, skip: int = 0, limit: int = 50) -> list[Document]:
        result = await self._db.execute(
            select(Document).order_by(Document.created_at.desc()).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def update_status(
        self, doc_id: str, status: DocumentStatus, error: str | None = None
    ) -> None:
        doc = await self.get(doc_id)
        if doc:
            doc.status = status
            if error:
                doc.error_message = error
            await self._db.flush()

    async def delete(self, doc_id: str) -> bool:
        doc = await self.get(doc_id)
        if not doc:
            return False
        await self._db.delete(doc)
        await self._db.flush()
        return True

    async def count(self) -> int:
        result = await self._db.execute(select(func.count()).select_from(Document))
        return result.scalar_one()
