from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class UploadResponse(BaseModel):
    document_id: str
    filename: str
    status: str


class CitationItem(BaseModel):
    citation_id: int
    doc_id: Optional[str] = None
    chunk_id: Optional[str] = None
    chunk_index: Optional[int] = None
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
    """
    Roast 接口的统一返回结构。
    """

    query: str
    method: str
    persona: Dict[str, Any]
    scores: Dict[str, Any]
    tags: List[str]
    contradictions: List[str]
    roast_text: str
    citations: List[CitationItem]
    retrieval_count: int