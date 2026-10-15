from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.interaction import Interaction
from app.schemas.interaction import InteractionCreate


class InteractionRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, data: InteractionCreate) -> Interaction:
        interaction = Interaction(
            protocol=f"IC-{uuid4().hex[:12].upper()}",
            channel=data.channel.value,
            transcript=data.transcript,
        )

        self.db.add(interaction)
        self.db.commit()
        self.db.refresh(interaction)

        return interaction

    def list_all(
        self,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Interaction]:
        statement = (
            select(Interaction)
            .order_by(
                Interaction.created_at.desc(),
                Interaction.id.desc(),
            )
            .offset(skip)
            .limit(limit)
        )

        return list(self.db.scalars(statement).all())

    def get_by_id(self, interaction_id: UUID) -> Interaction | None:
        return self.db.get(Interaction, interaction_id)

    def delete(self, interaction: Interaction) -> None:
        self.db.delete(interaction)
        self.db.commit()
