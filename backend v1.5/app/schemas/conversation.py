"""文件职责：会话 Schema"""
from datetime import datetime
from pydantic import BaseModel, Field


class ConversationCreate(BaseModel):
    title: str = Field(default="新对话", max_length=500)
    language: str = Field(default="zh")


class ConversationOut(BaseModel):
    id: str
    title: str
    language: str
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}

class ConversationListResponse(BaseModel):
    conversations: list[ConversationOut]
    total: int