from typing import List, Optional
from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, description="User question")
    document_ids: Optional[List[str]] = Field(
        default=None,
        description="Optional document ids for retrieval filtering"
    )
    top_k: int = Field(default=5, ge=1, le=50)
    method: str = Field(default="vector", description="Retriever method")


class RoastRequest(BaseModel):
    document_ids: Optional[List[str]] = None
    user_text: Optional[str] = None


class AgentRequest(BaseModel):
    question: str = Field(..., min_length=1)
    method: str = Field(default="hybrid")
    top_k: int = Field(default=5, ge=1, le=20)
    document_ids: Optional[List[str]] = None