from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.db.repositories.document_repo import DocumentRepository
from backend.schemas.response_models import DocumentsResponse


router = APIRouter()


@router.get("/documents", response_model=DocumentsResponse)
def list_documents(db: Session = Depends(get_db)):

    repo = DocumentRepository(db)

    docs = repo.list_documents()

    results = []

    for d in docs:

        results.append({
            "doc_id": str(d.id),
            "filename": d.filename,
            "file_type": d.file_type,
            "uploaded_at": d.created_at
        })

    return DocumentsResponse(documents=results)