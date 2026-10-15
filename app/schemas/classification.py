from uuid import UUID

from pydantic import BaseModel, Field


class ClassificationResponse(BaseModel):
    interaction_id: UUID
    intent: str
    confidence: float = Field(ge=0, le=1)
    model: str
