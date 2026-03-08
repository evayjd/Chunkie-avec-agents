from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel


class UploadResponse(BaseModel):
    document_id: str
    filename: str
    status: str


class CitationItem(BaseModel):
    citation_id: int
    doc_id: str
    chunk_id: str
    chunk_index: int
    page_start: Optional[int] = None
    page_end: Optional[int] = None
    section: Optional[str] = None
    snippet: Optional[str] = None


class AskResponse(BaseModel):
    answer: str
    citations: List[CitationItem]


class DocumentItem(BaseModel):
    doc_id: str
    filename: str
    file_type: str
    uploaded_at: datetime


class DocumentsResponse(BaseModel):
    documents: List[DocumentItem]


class RoastResponse(BaseModel):
    persona_name: str
    core_traits: List[str]
    tags: List[str]
    scores: Dict[str, float]
    roast_text: str