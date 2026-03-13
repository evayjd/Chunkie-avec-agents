"""MCP server exposing 6 PersonaKB tools."""
 
import uuid
import json
import structlog
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from app.config.settings import get_settings
from app.db.session import async_session_factory

logger = structlog.get_logger(__name__)

app = Server("personakb-mcp")


@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="list_documents",
            description="列出所有已上传的文档",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="search_user_corpus",
            description="在用户文档语料库中进行语义搜索",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "top_k": {"type": "integer", "default": 5},
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="ask_grounded_question",
            description="基于文档内容回答问题，附带引用来源",
            inputSchema={
                "type": "object",
                "properties": {
                    "question": {"type": "string"},
                    "language": {"type": "string", "default": "zh"},
                },
                "required": ["question"],
            },
        ),
        Tool(
            name="generate_roast_profile",
            description="生成用户人格分析（Roast）",
            inputSchema={
                "type": "object",
                "properties": {"language": {"type": "string", "default": "zh"}},
                "required": [],
            },
        ),
        Tool(
            name="get_citation_snippet",
            description="获取指定块的引用片段",
            inputSchema={
                "type": "object",
                "properties": {"chunk_id": {"type": "string"}},
                "required": ["chunk_id"],
            },
        ),
        Tool(
            name="get_persona_tags",
            description="获取用户人格标签列表",
            inputSchema={
                "type": "object",
                "properties": {"language": {"type": "string", "default": "zh"}},
                "required": [],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    async with async_session_factory() as db:
        if name == "list_documents":
            from app.repositories.document import DocumentRepository
            repo = DocumentRepository(db)
            docs = await repo.list_all(limit=50)
            result = [{"id": str(d.id), "filename": d.filename, "status": d.status} for d in docs]
            return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False))]

        elif name == "search_user_corpus":
            from app.pipelines.retrieval import run_retrieval_pipeline
            query = arguments["query"]
            chunks, _ = await run_retrieval_pipeline(db, query)
            result = [{"text": c["text"], "score": c["score"], "citation_number": c["citation_number"]} for c in chunks]
            return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False))]

        elif name == "ask_grounded_question":
            from app.services.chat_service import ChatService
            from app.schemas.message import ChatRequest
            svc = ChatService(db)
            req = ChatRequest(query=arguments["question"], language=arguments.get("language", "zh"))
            resp = await svc.chat(req)
            return [TextContent(type="text", text=resp.answer)]

        elif name == "generate_roast_profile":
            from app.services.roast_service import RoastService
            svc = RoastService(db)
            profile = await svc.generate_roast(language=arguments.get("language", "zh"))
            return [TextContent(type="text", text=profile.roast_text)]

        elif name == "get_citation_snippet":
            from app.repositories.chunk import ChunkRepository
            repo = ChunkRepository(db)
            chunk_id = uuid.UUID(arguments["chunk_id"])
            # Simple lookup
            from sqlalchemy import select
            from app.models.chunk import Chunk
            result = await db.execute(select(Chunk).where(Chunk.id == chunk_id))
            chunk = result.scalar_one_or_none()
            if chunk:
                return [TextContent(type="text", text=chunk.content[:300])]
            return [TextContent(type="text", text="未找到该片段")]

        elif name == "get_persona_tags":
            from app.services.roast_service import RoastService
            svc = RoastService(db)
            profile = await svc.generate_roast(language=arguments.get("language", "zh"))
            tags = [t.model_dump() for t in profile.persona_tags]
            return [TextContent(type="text", text=json.dumps(tags, ensure_ascii=False))]

        else:
            return [TextContent(type="text", text=f"未知工具: {name}")]


async def run_mcp_server() -> None:
    s = get_settings()
    logger.info("mcp_server_start", name=s.mcp_server_name, version=s.mcp_server_version)
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())
