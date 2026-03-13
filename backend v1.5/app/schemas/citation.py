"""文件职责：引用 Pydantic Schema"""
from pydantic import BaseModel, Field


class CitationOut(BaseModel):
    citation_number: int
    document_id: str
    document_name: str
    chunk_id: str
    snippet: str
    page_number: int | None = None
    section_title: str | None = None
    similarity_score: float
    rerank_score: float | None = None
    language: str
    confidence: float
