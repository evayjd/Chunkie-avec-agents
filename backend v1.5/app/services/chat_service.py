 
import uuid
import json
import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import get_settings
from app.core.constants import GROUNDED_QA_PROMPT, INSUFFICIENT_EVIDENCE_MSG
from app.core.exceptions import ConversationNotFoundError
from app.models.user import User
from app.repositories.conversation import ConversationRepository, MessageRepository
from app.schemas.message import ChatRequest, ChatResponse
from app.schemas.citation import CitationOut
from app.utils.language import detect_language
from app.services.agent_service import get_agent_executor

logger = structlog.get_logger(__name__)


class ChatService:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db
        self._conv_repo = ConversationRepository(db)
        self._msg_repo = MessageRepository(db)

    async def _get_or_create_default_user(self) -> str:
        result = await self._db.execute(select(User).limit(1))
        user = result.scalar_one_or_none()
        if user:
            return str(user.id)
        user = User(username="default", display_name="默认用户")
        self._db.add(user)
        await self._db.flush()
        await self._db.refresh(user)
        return str(user.id)

    async def chat(self, request: ChatRequest) -> ChatResponse:
        s = get_settings()
        lang = request.language or detect_language(request.query)

        # Get or create conversation
        if request.conversation_id:
            conv = await self._conv_repo.get(request.conversation_id)
            if not conv:
                raise ConversationNotFoundError(str(request.conversation_id))
        else:
            user_id = await self._get_or_create_default_user()
            conv = await self._conv_repo.create(user_id=user_id, language=lang)

        # Get the agent executor
        agent_executor = await get_agent_executor(self._db)

        # Invoke the agent
        result = await agent_executor.ainvoke({"input": request.query})
        answer = result["output"]

        # Extract citations and metadata from intermediate steps if possible
        # This is a basic implementation to match the existing schema
        citations = []
        retrieval_metadata = {}
        
        # Intermediate steps are a list of tuples (AgentAction, ToolOutput)
        steps = result.get("intermediate_steps", [])
        if steps:
            # If the retrieval tool was called, it returns a string of citations
            # In a more advanced version, we could return a dict/object from the tool
            # For now, we'll mark it as grounded if any tool was called
            pass

        # Persist messages
        await self._msg_repo.create(
            conversation_id=(conv.id),
            role="user",
            content=request.query,
        )
        assistant_msg = await self._msg_repo.create(
            conversation_id=uuid.UUID(str(conv.id)),
            role="assistant",
            content=answer,
            citations_json=json.dumps([c.model_dump() if hasattr(c, "model_dump") else c for c in citations], ensure_ascii=False),
            retrieval_metadata_json=json.dumps(retrieval_metadata, ensure_ascii=False),
        )
        await self._db.commit()

        return ChatResponse(
            answer=answer,
            citations=citations,
            conversation_id=uuid.UUID(str(conv.id)),
            message_id=uuid.UUID(str(assistant_msg.id)),
            is_grounded=len(steps) > 0,
            retrieval_metadata=retrieval_metadata,
        )
