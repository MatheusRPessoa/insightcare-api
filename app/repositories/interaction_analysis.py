from uuid import UUID

from sqlalchemy.orm import Session

from app.models.interaction_analysis import InteractionAnalysis
from app.schemas.analysis import InteractionAnalysisResponse


class InteractionAnalysisRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_interaction_id(
        self,
        interaction_id: UUID,
    ) -> InteractionAnalysis | None:
        return (
            self.db.query(InteractionAnalysis)
            .filter(InteractionAnalysis.interaction_id == interaction_id)
            .one_or_none()
        )

    def save(
        self,
        data: InteractionAnalysisResponse,
    ) -> InteractionAnalysis:
        analysis = self.get_by_interaction_id(data.interaction_id)

        values = data.model_dump(
            exclude={"interaction_id"},
            mode="json",
        )

        if analysis is None:
            analysis = InteractionAnalysis(
                interaction_id=data.interaction_id,
                **values,
            )
            self.db.add(analysis)
        else:
            for field, value in values.items():
                setattr(analysis, field, value)

        self.db.flush()

        return analysis
