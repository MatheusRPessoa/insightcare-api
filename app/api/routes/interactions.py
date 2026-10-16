from typing import Annotated
from uuid import UUID

from botocore.exceptions import BotoCoreError, ClientError
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.schemas.analysis import InteractionAnalysisResponse
from app.schemas.classification import ClassificationResponse
from app.schemas.interaction import (
    InteractionCreate,
    InteractionResponse,
)
from app.services.bedrock_analysis import (
    BedrockAnalysisError,
    BedrockAnalysisService,
)
from app.services.interaction import InteractionService
from app.services.interaction_analysis import InteractionAnalysisService
from app.services.ml_classifier import MLClassifierService

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


@router.post(
    "/{interaction_id}/classify",
    response_model=ClassificationResponse,
)
def classify_interaction(
    interaction_id: UUID,
    db: DbSession,
) -> ClassificationResponse:
    interaction_service = InteractionService(db)

    interaction = interaction_service.get_by_id(interaction_id)

    classifier = MLClassifierService()

    try:
        result = classifier.classify(interaction.transcript)
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=503,
            detail="Modelo de ML não disponível",
        ) from exc

    return ClassificationResponse(
        interaction_id=interaction.id,
        **result,
    )


@router.post(
    "/{interaction_id}/analyze",
    response_model=InteractionAnalysisResponse,
)
def analyze_interaction(
    interaction_id: UUID,
    db: DbSession,
) -> InteractionAnalysisResponse:
    interaction_service = InteractionService(db)

    interaction = interaction_service.get_by_id(interaction_id)

    classifier = MLClassifierService()
    analyzer = BedrockAnalysisService()

    try:
        ml_result = classifier.classify(interaction.transcript)

        llm_result = analyzer.analyze(interaction.transcript)

    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=503,
            detail="Modelo de classificação indisponível",
        ) from exc

    except BedrockAnalysisError as exc:
        raise HTTPException(
            status_code=502,
            detail="O modelo generativo retornou uma análise inválida",
        ) from exc

    except (BotoCoreError, ClientError) as exc:
        raise HTTPException(
            status_code=503,
            detail="Serviço de IA generativa indisponível",
        ) from exc

    result = InteractionAnalysisResponse(
        interaction_id=interaction.id,
        intent=ml_result["intent"],
        confidence=ml_result["confidence"],
        classification_model=ml_result["model"],
        generative_model=settings.bedrock_model_id,
        **llm_result.model_dump(),
    )

    analysis_service = InteractionAnalysisService(db)

    return analysis_service.save(
        interaction=interaction,
        data=result,
    )


@router.get(
    "/{interaction_id}/analysis",
    response_model=InteractionAnalysisResponse,
)
def get_interaction_analysis(
    interaction_id: UUID,
    db: DbSession,
) -> InteractionAnalysisResponse:
    interaction_service = InteractionService(db)
    interaction_service.get_by_id(interaction_id)

    analysis_service = InteractionAnalysisService(db)

    analysis = analysis_service.get_by_interaction_id(interaction_id)

    if analysis is None:
        raise HTTPException(
            status_code=404,
            detail="Análise não encontrada",
        )

    return analysis
