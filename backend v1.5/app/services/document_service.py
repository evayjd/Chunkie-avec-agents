"""Document management service."""
 
import uuid
import asyncio
import hashlib
import structlog
from pathlib import Path
from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import get_settings
from app.core.constants import DocumentStatus, FileType
from app.core.exceptions import (
    UnsupportedFileTypeError,
    FileSizeExceededError,
    DocumentNotFoundError,
)
from app.models.document import Document
from app.models.user import User
from app.repositories.document import DocumentRepository
from app.pipelines.ingestion import run_ingestion_pipeline
from app.utils.language import detect_language

logger = structlog.get_logger(__name__)


class DocumentService:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db
        self._doc_repo = DocumentRepository(db)

    async def _get_or_create_default_user(self) :
        result = await self._db.execute(select(User).limit(1))
        user = result.scalar_one_or_none()
        if user:
            return user.id
        user = User(username="default", display_name="默认用户")
        self._db.add(user)
        await self._db.flush()
        await self._db.refresh(user)
        return user.id

    async def upload_document(self, file: UploadFile) -> Document:
        s = get_settings()
        filename = file.filename or "unknown"
        ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        allowed = [ft.value for ft in FileType]
        if ext not in allowed:
            raise UnsupportedFileTypeError(
                file_type=ext,
                supported=allowed
            )

        content = await file.read()
        size_mb = len(content) / (1024 * 1024)

        if size_mb > s.upload_max_size_mb:
            raise FileSizeExceededError(
                size_mb=size_mb,
                max_mb=s.upload_max_size_mb
            )

        # Detect language from first 500 chars
        preview = content[:500].decode("utf-8", errors="ignore")
        lang = detect_language(preview)

        # Save file to disk
        storage_dir = Path(s.storage_path)
        storage_dir.mkdir(parents=True, exist_ok=True)
        file_stem = str(uuid.uuid4())
        storage_path = str(storage_dir / f"{file_stem}_{filename}")
        Path(storage_path).write_bytes(content)

        content_hash = hashlib.sha256(content).hexdigest()
        user_id = await self._get_or_create_default_user()

        doc = await self._doc_repo.create(
            filename=filename,
            display_name=filename,
            file_type=FileType(ext).value,
            file_size_bytes=len(content),
            storage_path=storage_path,
            status=DocumentStatus.PENDING,
            language=lang,
            content_hash=content_hash,
            user_id=user_id,
        )
        await self._db.commit()

        # Run ingestion in background
        asyncio.create_task(self._ingest(str(doc.id), filename, content))
        return doc

    async def _ingest(
        self, doc_id: str, filename: str, content: bytes
    ) -> None:
        from app.db.session import async_session_factory
        async with async_session_factory() as db:
            async with db.begin():
                await run_ingestion_pipeline(db, doc_id, filename, content)

    async def get_document(self, doc_id: uuid.UUID) -> Document:
        doc = await self._doc_repo.get(str(doc_id))
        if not doc:
            raise DocumentNotFoundError(str(doc_id))
        return doc

    async def list_documents(self, skip: int = 0, limit: int = 50) -> list[Document]:
        return await self._doc_repo.list_all(skip=skip, limit=limit)

    async def delete_document(self, doc_id: uuid.UUID) -> None:
        from app.repositories.chunk import ChunkRepository
        chunk_repo = ChunkRepository(self._db)
        await chunk_repo.delete_by_document(str(doc_id))
        deleted = await self._doc_repo.delete(str(doc_id))
        if not deleted:
            raise DocumentNotFoundError(str(doc_id))
        await self._db.commit()
