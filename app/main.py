from fastapi import FastAPI

from app.api.routes.health import router as health_router
from app.api.routes.interactions import router as interactions_router

app = FastAPI(
    title="InsightCare AI API",
    description="API para análise inteligente de atendimentos em saúde",
    version="0.1.0",
)

app.include_router(health_router, prefix="/api/v1")
app.include_router(interactions_router, prefix="/api/v1")