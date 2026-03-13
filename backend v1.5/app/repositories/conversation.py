"""Conversation and Message repositories."""
 
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.conversation import Conversation
from app.models.message import Message


class ConversationRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def create(self, user_id: str, title: str = "新对话", language: str = "zh") -> Conversation:
        conv = Conversation(user_id=user_id, title=title, language=language)
        self._db.add(conv)
        await self._db.flush()
        await self._db.refresh(conv)
        return conv

    async def get(self, conv_id: uuid.UUID) -> Conversation | None:
        result = await self._db.execute(
            select(Conversation).where(Conversation.id == conv_id)
        )
        return result.scalar_one_or_none()

    async def list_all(self, skip: int = 0, limit: int = 50) -> list[Conversation]:
        result = await self._db.execute(
            select(Conversation)
            .order_by(Conversation.updated_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_messages(self, conv_id: uuid.UUID) -> list[Message]:
        result = await self._db.execute(
            select(Message)
            .where(Message.conversation_id == conv_id)
            .order_by(Message.created_at)
        )
        return list(result.scalars().all())

    async def delete(self, conv_id: uuid.UUID) -> bool:
        conv = await self.get(conv_id)
        if not conv:
            return False
        await self._db.delete(conv)
        await self._db.flush()
        return True


class MessageRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def create(self, **kwargs) -> Message:
        msg = Message(**kwargs)
        self._db.add(msg)
        await self._db.flush()
        await self._db.refresh(msg)
        return msg
