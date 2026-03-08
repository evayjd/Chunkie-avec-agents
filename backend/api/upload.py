import os
import shutil
from uuid import uuid4

from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.core.config import settings
from backend.schemas.response_models import UploadResponse
from backend.services.ingestion.pipeline import IngestionPipeline

router = APIRouter()


@router.post("/upload", response_model=UploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    file_id = str(uuid4())

    file_path = os.path.join(settings.UPLOAD_DIR, f"{file_id}_{file.filename}")

    with open(file_path, "wb") as buffer:

        shutil.copyfileobj(file.file, buffer)

    pipeline = IngestionPipeline(db)

    document_id = pipeline.ingest(file_path)

    return UploadResponse(
        document_id=str(document_id),
        filename=file.filename,
        status="processed"
    )