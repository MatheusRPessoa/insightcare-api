from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.interaction import (
    InteractionChannel,
    InteractionStatus,
)


class InteractionCreate(BaseModel):
    channel: InteractionChannel
    transcript: str = Field(
        min_length=10,
        max_length=20000,
    )


class InteractionUpdate(BaseModel):
    transcript: str = Field(min_length=10)


class InteractionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    protocol: str
    channel: InteractionChannel
    transcript: str
    status: InteractionStatus
    created_at: datetime
    updated_at: datetime
