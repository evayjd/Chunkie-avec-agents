"""Chat / grounded QA endpoints."""

import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import traceback
from app.db.session import get_db
from app.core.exceptions import ConversationNotFoundError
from app.schemas.message import ChatRequest, ChatResponse
from app.schemas.conversation import ConversationOut, ConversationListResponse
from app.services.chat_service import ChatService
from app.repositories.conversation import ConversationRepository

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest, db: AsyncSession = Depends(get_db)):
    svc = ChatService(db)
    try:
        return await svc.chat(request)
    except ConversationNotFoundError:
        raise HTTPException(status_code=404, detail="对话不存在")
    except Exception as exc:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/conversations", response_model=ConversationListResponse)
async def list_conversations(
    skip: int = 0, limit: int = 50, db: AsyncSession = Depends(get_db)
):
    repo = ConversationRepository(db)
    conversations = await repo.list_all(skip=skip, limit=limit)
    return ConversationListResponse(
        conversations=[ConversationOut.model_validate(c) for c in conversations],
        total=len(conversations),
    )


@router.delete("/conversations/{conv_id}", status_code=204)
async def delete_conversation(
    conv_id: uuid.UUID, db: AsyncSession = Depends(get_db)
):
    repo = ConversationRepository(db)
    deleted = await repo.delete(conv_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="对话不存在")
