"""文件职责：消息 Schema"""
from datetime import datetime
from pydantic import BaseModel, Field
from app.schemas.citation import CitationOut
from uuid import UUID


class ChatRequest(BaseModel):
    query: str = Field(min_length=1, max_length=2000)
    conversation_id: UUID | None = None
    document_ids: list[UUID] | None = None
    language: str = Field(default="zh")


class ChatResponse(BaseModel):
    answer: str
    citations: list[CitationOut] = Field(default_factory=list)
    conversation_id: UUID
    message_id: UUID
    is_grounded: bool
    retrieval_metadata: dict = Field(default_factory=dict)


class MessageOut(BaseModel):
    id: str
    role: str
    content: str
    citations: list[CitationOut] = []
    created_at: datetime
    model_config = {"from_attributes": True}
