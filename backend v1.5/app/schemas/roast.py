"""文件职责：Roast 人格分析 Schema"""
from datetime import datetime
from pydantic import BaseModel, Field
from app.schemas.citation import CitationOut


class RoastRequest(BaseModel):
    document_ids: list[str] | None = None
    language: str = Field(default="zh")
    tone: str = Field(default="playful")


class PersonaTagOut(BaseModel):
    tag: str
    label: str
    confidence: float
    evidence_snippet: str
    citation_number: int | None = None


class DimensionScoreOut(BaseModel):
    dimension: str
    label: str
    score: float
    evidence: str


class RoastProfileOut(BaseModel):
    id: str
    roast_text: str
    dimension_scores: list[DimensionScoreOut]
    persona_tags: list[PersonaTagOut]
    citations: list[CitationOut]
    language: str
    tone: str
    created_at: datetime
    model_config = {"from_attributes": True}
