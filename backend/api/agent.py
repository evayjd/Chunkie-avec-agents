from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.schemas.request_models import AgentRequest
from backend.services.agent.agent import Agent
from backend.services.agent.tool_registry import ToolRegistry
from backend.services.agent.agent_executor import AgentExecutor

from backend.services.agent.tools.rag_search_tool import RagSearchTool
from backend.services.agent.tools.answer_tool import AnswerTool
from backend.services.agent.tools.document_summary_tool import DocumentSummaryTool
from backend.services.agent.tools.document_compare_tool import DocumentCompareTool
from backend.services.agent.tools.roast_tool import RoastTool

router = APIRouter()


def build_registry(db: Session) -> ToolRegistry:
    registry = ToolRegistry()
    registry.register(RagSearchTool(db))
    registry.register(AnswerTool(db))
    registry.register(DocumentSummaryTool(db))
    registry.register(DocumentCompareTool(db))
    registry.register(RoastTool(db))
    return registry


@router.post("/agent")
def agent_query(
    req: AgentRequest,
    db: Session = Depends(get_db),
):
    registry = build_registry(db)
    executor = AgentExecutor(registry)
    agent = Agent(registry, executor)

    result = agent.run(
        question=req.question,
        method=req.method,
        top_k=req.top_k,
        document_ids=req.document_ids,
        target_id=req.target_id,
        style_preference=req.style_preference,
    )

    return result