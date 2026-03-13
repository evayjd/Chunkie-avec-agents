"""文件职责：评估 Schema"""
from datetime import datetime
from pydantic import BaseModel, Field


class EvalRunRequest(BaseModel):
    run_name: str
    benchmark_file: str
    top_k: int = Field(default=5)


class EvalMetricsSummary(BaseModel):
    recall_at_k: float
    precision_at_k: float
    mrr: float
    ndcg_at_k: float
    hit_rate: float
    total_queries: int
    top_k: int


class EvalRunOut(BaseModel):
    id: str
    run_name: str
    status: str
    total_queries: int
    metrics: dict
    created_at: datetime
    model_config = {"from_attributes": True}
