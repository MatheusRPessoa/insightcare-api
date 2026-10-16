from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.dashboard import DashboardSummaryResponse
from app.services.dashboard import DashboardService

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)

DbSession = Annotated[Session, Depends(get_db)]


@router.get(
    "/summary",
    response_model=DashboardSummaryResponse,
)
def get_dashboard_summary(
    db: DbSession,
) -> DashboardSummaryResponse:
    service = DashboardService(db)
    return service.get_summary()
