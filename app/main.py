from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.dashboard import router as dashboard_router
from app.api.routes.health import router as health_router
from app.api.routes.interactions import router as interactions_router

app = FastAPI(
    title="InsightCare AI API",
    description="API para análise inteligente de atendimentos em saúde",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

app.include_router(health_router, prefix="/api/v1")
app.include_router(interactions_router, prefix="/api/v1")
app.include_router(dashboard_router, prefix="/api/v1")
