from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.db.models import Document


class DocumentRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_document(
        self,
        filename: str,
        file_type: str,
        file_path: str,
        raw_text: Optional[str] = None,
        cleaned_text: Optional[str] = None,
        metadata_json: Optional[dict] = None,
    ) -> Document:
        document = Document(
            filename=filename,
            file_type=file_type,
            file_path=file_path,
            raw_text=raw_text,
            cleaned_text=cleaned_text,
            metadata_json=metadata_json,
        )
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        return document

    def get_by_id(self, document_id: UUID) -> Optional[Document]:
        stmt = select(Document).where(Document.id == document_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def list_documents(self) -> List[Document]:
        stmt = select(Document).order_by(Document.created_at.desc())
        return list(self.db.execute(stmt).scalars().all())

    def delete_document(self, document_id: UUID) -> bool:
        document = self.get_by_id(document_id)
        if not document:
            return False

        self.db.delete(document)
        self.db.commit()
        return True

    def update_texts(
        self,
        document_id: UUID,
        raw_text: Optional[str] = None,
        cleaned_text: Optional[str] = None,
        metadata_json: Optional[dict] = None,
    ) -> Optional[Document]:
        document = self.get_by_id(document_id)
        if not document:
            return None

        if raw_text is not None:
            document.raw_text = raw_text
        if cleaned_text is not None:
            document.cleaned_text = cleaned_text
        if metadata_json is not None:
            document.metadata_json = metadata_json

        self.db.commit()
        self.db.refresh(document)
        return document