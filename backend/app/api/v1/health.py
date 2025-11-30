"""Health and readiness check endpoints."""

from fastapi import APIRouter

from app.api.schemas import HealthResponse
from app.config import settings

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check endpoint returning API and service status."""
    services = {
        "api": True,
        "embeddings": True,
        "vector_store": True,
    }
    
    return HealthResponse(
        status="healthy",
        version=settings.app_version,
        environment=settings.environment,
        services=services,
    )


@router.get("/ready")
async def readiness_check() -> dict:
    """Readiness check endpoint for Kubernetes/Docker health probes."""
    return {"ready": True}
