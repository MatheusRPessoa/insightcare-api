from uuid import UUID

from sqlalchemy.orm import Session

from app.models.interaction import Interaction
from app.repositories.interaction_analysis import (
    InteractionAnalysisRepository,
)
from app.schemas.analysis import InteractionAnalysisResponse


class InteractionAnalysisService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repository = InteractionAnalysisRepository(db)

    def save(
        self,
        interaction: Interaction,
        data: InteractionAnalysisResponse,
    ) -> InteractionAnalysisResponse:
        if interaction.id != data.interaction_id:
            raise ValueError("A análise não pertence ao atendimento")

        try:
            analysis = self.repository.save(data)

            status_type = type(interaction.status)

            interaction.status = (
                status_type.ANALYZED if hasattr(status_type, "ANALYZED") else "ANALYZED"
            )

            self.db.add(interaction)
            self.db.commit()
            self.db.refresh(analysis)

        except Exception:
            self.db.rollback()
            raise

        return self.to_response(analysis)

    def get_by_interaction_id(
        self,
        interaction_id: UUID,
    ) -> InteractionAnalysisResponse | None:
        analysis = self.repository.get_by_interaction_id(interaction_id)

        if analysis is None:
            return None

        return self.to_response(analysis)

    @staticmethod
    def to_response(analysis) -> InteractionAnalysisResponse:
        return InteractionAnalysisResponse(
            interaction_id=analysis.interaction_id,
            intent=analysis.intent,
            confidence=analysis.confidence,
            sentiment=analysis.sentiment,
            risk_level=analysis.risk_level,
            summary=analysis.summary,
            detected_signals=analysis.detected_signals,
            evidence=analysis.evidence,
            recommended_action=analysis.recommended_action,
            classification_model=analysis.classification_model,
            generative_model=analysis.generative_model,
        )
