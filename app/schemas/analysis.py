from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field


class Sentiment(str, Enum):
    POSITIVE = "POSITIVE"
    NEUTRAL = "NEUTRAL"
    NEGATIVE = "NEGATIVE"


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class AnalysisResult(BaseModel):
    summary: str = Field(min_length=1)
    sentiment: Sentiment
    risk_level: RiskLevel
    detected_signals: list[str]
    evidence: list[str]
    recommended_action: str = Field(min_length=1)

class InteractionAnalysisResponse(AnalysisResult):
    interaction_id: UUID
    intent: str
    confidence: float = Field(ge=0, le=1)
    classification_model: str
    generative_model: str
