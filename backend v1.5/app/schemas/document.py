"""文件职责：文档相关 Pydantic Schema"""
from datetime import datetime
from pydantic import BaseModel, Field


class DocumentUploadResponse(BaseModel):
    document_id: str
    filename: str
    status: str
    message: str


class DocumentOut(BaseModel):
    id: str
    filename: str
    display_name: str
    file_type: str
    file_size_bytes: int
    status: str
    language: str | None
    total_chunks: int
    error_message: str | None
    description: str | None
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}


class DocumentUpdateRequest(BaseModel):
    display_name: str | None = Field(None, max_length=500)
    description: str | None = None


class DocumentListResponse(BaseModel):
    documents: list[DocumentOut]
    total: int
