
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.interaction import (
    InteractionCreate,
    InteractionResponse,
)
from app.services.interaction import InteractionService


router = APIRouter(prefix="/interactions", tags=["Interactions"])

DbSession = Annotated[Session, Depends(get_db)]


@router.post(
    "",
    response_model=InteractionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_interaction(
    data: InteractionCreate,
    db: DbSession,
) -> InteractionResponse:
    service = InteractionService(db)
    return service.create(data)


@router.get("", response_model=list[InteractionResponse])
def list_interactions(
    db: DbSession,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> list[InteractionResponse]:
    service = InteractionService(db)
    return service.list_all(skip, limit)


@router.get("/{interaction_id}", response_model=InteractionResponse)
def get_interaction(
    interaction_id: UUID,
    db: DbSession,
) -> InteractionResponse:
    service = InteractionService(db)
    return service.get_by_id(interaction_id)


@router.delete(
    "/{interaction_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_interaction(
    interaction_id: UUID,
    db: DbSession,
) -> None:
    service = InteractionService(db)
    service.delete(interaction_id)
