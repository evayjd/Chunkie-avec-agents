from fastapi import APIRouter

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


def build_registry() -> ToolRegistry:
    registry = ToolRegistry()
    registry.register(RagSearchTool())
    registry.register(AnswerTool())
    registry.register(DocumentSummaryTool())
    registry.register(DocumentCompareTool())
    registry.register(RoastTool())
    return registry


@router.post("/agent")
def agent_query(req: AgentRequest):
    registry = build_registry()
    executor = AgentExecutor(registry)
    agent = Agent(registry, executor)

    result = agent.run(
        question=req.question,
        method=req.method,
        top_k=req.top_k,
        document_ids=req.document_ids
    )

    return result