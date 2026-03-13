"""
文件职责：数据库 ORM 基类定义
"""
import uuid
from datetime import datetime, timezone
from uuid import UUID
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def generate_uuid() -> str:
    return str(uuid.uuid4())


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, server_default=func.now(), nullable=False, comment="创建时间（UTC）")
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, server_default=func.now(), nullable=False, comment="最后更新时间（UTC）")


class BaseModel(Base, TimestampMixin):
    __abstract__ = True
    id:Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )