
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.interaction import Interaction
from app.repositories.interaction import InteractionRepository
from app.schemas.interaction import InteractionCreate


class InteractionService:
    def __init__(self, db: Session) -> None:
        self.repository = InteractionRepository(db)

    def create(self, data: InteractionCreate) -> Interaction:
        return self.repository.create(data)

    def list_all(
        self,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Interaction]:
        return self.repository.list_all(skip, limit)

    def get_by_id(self, interaction_id: UUID) -> Interaction:
        interaction = self.repository.get_by_id(interaction_id)

        if interaction is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interaction not found",
            )

        return interaction

    def delete(self, interaction_id: UUID) -> None:
        interaction = self.get_by_id(interaction_id)
        self.repository.delete(interaction)
