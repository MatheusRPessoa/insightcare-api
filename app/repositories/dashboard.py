from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.interaction import Interaction
from app.models.interaction_analysis import InteractionAnalysis


class DashboardRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def count_interactions(self) -> int:
        statement = select(func.count()).select_from(Interaction)
        return self.db.scalar(statement) or 0

    def count_by_status(self) -> dict[str, int]:
        statement = select(Interaction.status, func.count()).group_by(
            Interaction.status
        )

        result = self.db.execute(statement).all()

        return {
            (status.value if hasattr(status, "value") else str(status)): count
            for status, count in result
        }

    def count_by_risk(self) -> dict[str, int]:
        statement = select(
            InteractionAnalysis.risk_level,
            func.count(),
        ).group_by(InteractionAnalysis.risk_level)

        return dict(self.db.execute(statement).all())

    def count_by_sentiment(self) -> dict[str, int]:
        statement = select(
            InteractionAnalysis.sentiment,
            func.count(),
        ).group_by(InteractionAnalysis.sentiment)

        return dict(self.db.execute(statement).all())

    def count_by_intent(self) -> dict[str, int]:
        statement = select(
            InteractionAnalysis.intent,
            func.count(),
        ).group_by(InteractionAnalysis.intent)

        return dict(self.db.execute(statement).all())
