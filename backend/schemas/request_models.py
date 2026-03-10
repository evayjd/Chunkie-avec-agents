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
    """
    Roast API 的正式请求结构。

    统一成和 roast_pipeline / roast_tool / agent 注入逻辑一致的契约：
    - query：必填，检索与画像分析的查询语句
    - document_ids：可选，限定在哪些文档中做 roast
    - top_k：检索召回条数
    - method：检索方法
    - style_preference：可选，先保留，当前 pipeline 不强依赖，但接口层接住，便于后续扩展
    """
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
        default=None,
        description="可选的 roast 风格偏好"
    )


class AgentRequest(BaseModel):
    question: str = Field(..., min_length=1)
    method: str = Field(default="hybrid")
    top_k: int = Field(default=5, ge=1, le=20)
    document_ids: Optional[List[str]] = None