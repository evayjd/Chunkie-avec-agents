import os
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.core.config import settings
from backend.schemas.response_models import UploadResponse
from backend.services.ingestion.pipeline import IngestionPipeline

router = APIRouter()

ALLOWED_EXTENSIONS = {".pdf", ".txt", ".md", ".html", ".htm", ".docx"}
MAX_FILE_SIZE_MB = 50
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024


@router.post("/upload", response_model=UploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # 文件名与扩展名校验
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided.")

    # 防止路径遍历攻击（同时兼容 Windows 反斜杠路径）
    safe_name = os.path.basename(file.filename.replace("\\", "/"))
    if not safe_name:
        raise HTTPException(status_code=400, detail="Invalid filename.")

    ext = os.path.splitext(safe_name)[-1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported file type '{ext}'. Allowed: {sorted(ALLOWED_EXTENSIONS)}"
        )

    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    file_id = str(uuid4())
    file_path = os.path.join(settings.UPLOAD_DIR, f"{file_id}_{safe_name}")

    # 流式写文件并同步校验大小
    size_written = 0
    try:
        with open(file_path, "wb") as buffer:
            while True:
                chunk = await file.read(1024 * 1024)  # 1 MB chunks
                if not chunk:
                    break
                size_written += len(chunk)
                if size_written > MAX_FILE_SIZE_BYTES:
                    buffer.close()
                    os.remove(file_path)
                    raise HTTPException(
                        status_code=413,
                        detail=f"File too large. Maximum allowed size is {MAX_FILE_SIZE_MB} MB."
                    )
                buffer.write(chunk)
    except HTTPException:
        raise
    except Exception as exc:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Failed to save file: {exc}")

    # 修复 Bug 1：pipeline 失败时清理已保存的磁盘文件，避免孤立文件残留
    try:
        pipeline = IngestionPipeline(db)
        document_id = pipeline.ingest(file_path)
    except Exception as exc:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Ingestion pipeline failed: {exc}")

    return UploadResponse(
        document_id=str(document_id),
        filename=file.filename,
        status="processed"
    )
