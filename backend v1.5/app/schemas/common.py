"""文件职责：公共 Pydantic Schema"""
from typing import Generic, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int = Field(description="总记录数")
    page: int = Field(description="当前页")
    page_size: int = Field(description="每页大小")
    has_next: bool = Field(description="是否有下一页")


class ErrorResponse(BaseModel):
    error: str
    message: str
    details: dict = Field(default_factory=dict)


class SuccessResponse(BaseModel):
    success: bool = True
    message: str = ""
