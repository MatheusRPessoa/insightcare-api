from sqlalchemy.orm import Session

from app.repositories.dashboard import DashboardRepository
from app.schemas.dashboard import DashboardSummaryResponse


class DashboardService:
    def __init__(self, db: Session) -> None:
        self.repository = DashboardRepository(db)

    def get_summary(self) -> DashboardSummaryResponse:
        total = self.repository.count_interactions()
        statuses = self.repository.count_by_status()

        risk = self.repository.count_by_risk()
        sentiment = self.repository.count_by_sentiment()
        intent = self.repository.count_by_intent()

        return DashboardSummaryResponse(
            total_interactions=total,
            analyzed_interactions=statuses.get("ANALYZED", 0),
            pending_interactions=statuses.get("PENDING", 0),
            risk_distribution={
                "LOW": risk.get("LOW", 0),
                "MEDIUM": risk.get("MEDIUM", 0),
                "HIGH": risk.get("HIGH", 0),
            },
            sentiment_distribution={
                "POSITIVE": sentiment.get("POSITIVE", 0),
                "NEUTRAL": sentiment.get("NEUTRAL", 0),
                "NEGATIVE": sentiment.get("NEGATIVE", 0),
            },
            intent_distribution=intent,
        )
