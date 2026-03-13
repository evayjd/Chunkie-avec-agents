"""文件职责：人格标签 Schema"""
from pydantic import BaseModel, Field


class PersonaTagRequest(BaseModel):
    document_ids: list[str] | None = None
    language: str = Field(default="zh")


class PersonaTagsResponse(BaseModel):
    tags: list[dict]
    dimension_scores: dict[str, float]
