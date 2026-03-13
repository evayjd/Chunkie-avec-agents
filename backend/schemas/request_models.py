from typing import List, Optional

from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, description="用户问题")
    document_ids: Optional[List[str]] = Field(
        default=None,
        description="可选的文档过滤列表"
    )
    top_k: int = Field(default=5, ge=1, le=50, description="召回数量")
    method: str = Field(
        default="vector",
        description="检索方法：vector / hybrid / rerank"
    )


class RoastRequest(BaseModel):
    query: str = Field(..., min_length=1, description="用于 roast 检索与分析的查询")
    document_ids: Optional[List[str]] = Field(
        default=None,
        description="可选的文档过滤列表"
    )
    top_k: int = Field(default=6, ge=1, le=20, description="roast 检索召回条数")
    method: str = Field(
        default="rerank",
        description="检索方法：vector / hybrid / rerank"
    )
    style_preference: Optional[str] = Field(
        default="sharp_witty",
        min_length=1,
        description="roast 风格偏好"
    )
    target_id: Optional[str] = Field(
        default=None,
        description="目标文档 id；若为空则由 document_ids 推断"
    )


class AgentRequest(BaseModel):
    question: str = Field(..., min_length=1)
    method: str = Field(default="hybrid")
    top_k: int = Field(default=5, ge=1, le=20)
    document_ids: Optional[List[str]] = None
    target_id: Optional[str] = None
    style_preference: Optional[str] = Field(default="sharp_witty")