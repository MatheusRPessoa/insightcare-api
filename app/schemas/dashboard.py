from pydantic import BaseModel, Field


class DashboardSummaryResponse(BaseModel):
    total_interactions: int = Field(ge=0)
    analyzed_interactions: int = Field(ge=0)
    pending_interactions: int = Field(ge=0)

    risk_distribution: dict[str, int]
    sentiment_distribution: dict[str, int]
    intent_distribution: dict[str, int]
