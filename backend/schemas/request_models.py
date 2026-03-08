from typing import List, Optional
from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, description="User question")
    document_ids: Optional[List[str]] = Field(
        default=None,
        description="Optional document ids for retrieval filtering"
    )
    top_k: int = Field(default=5, ge=1, le=20)


class RoastRequest(BaseModel):
    document_ids: Optional[List[str]] = None
    user_text: Optional[str] = None