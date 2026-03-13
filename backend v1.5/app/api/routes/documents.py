"""Document upload/list/delete endpoints."""
 
import uuid
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.core.exceptions import (
    DocumentNotFoundError,
    UnsupportedFileTypeError,
    FileSizeExceededError,
)
from app.schemas.document import DocumentOut, DocumentListResponse
from app.services.document_service import DocumentService

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/", response_model=DocumentOut, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    svc = DocumentService(db)
    try:
        doc = await svc.upload_document(file)
        return DocumentOut.model_validate(doc)
    except UnsupportedFileTypeError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except FileSizeExceededError as exc:
        raise HTTPException(status_code=413, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/", response_model=DocumentListResponse)
async def list_documents(
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
):
    svc = DocumentService(db)
    docs = await svc.list_documents(skip=skip, limit=limit)
    return DocumentListResponse(
    documents=[DocumentOut.model_validate(d) for d in docs],
    total=len(docs),
)



@router.get("/{doc_id}", response_model=DocumentOut)
async def get_document(doc_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    svc = DocumentService(db)
    try:
        doc = await svc.get_document(doc_id)
        return DocumentOut.model_validate(doc)
    except DocumentNotFoundError:
        raise HTTPException(status_code=404, detail="文档不存在")


@router.delete("/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(doc_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    svc = DocumentService(db)
    try:
        await svc.delete_document(doc_id)
    except DocumentNotFoundError:
        raise HTTPException(status_code=404, detail="文档不存在")
