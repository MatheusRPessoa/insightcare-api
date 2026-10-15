import enum
import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, Enum, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class InteractionChannel(str, enum.Enum):
    CHAT = "CHAT"
    PHONE = "PHONE"
    EMAIL = "EMAIL"


class InteractionStatus(str, enum.Enum):
    PENDING = "PENDING"
    ANALYZED = "ANALYZED"


class Interaction(Base):
    __tablename__ = "interactions"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )

    protocol: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False,
    )

    channel: Mapped[InteractionChannel] = mapped_column(
        Enum(InteractionChannel),
        nullable=False,
    )

    transcript: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    status: Mapped[InteractionStatus] = mapped_column(
        Enum(InteractionStatus),
        default=InteractionStatus.PENDING,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )
