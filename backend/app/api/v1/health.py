"""
Qonfido RAG - Health Check Endpoints
=====================================
Health and status check endpoints.
"""

from fastapi import APIRouter

from app.api.schemas import HealthResponse
from app.config import settings

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Health check endpoint.
    
    Returns the health status of the API and its dependencies.
    """
    # Check services (can be expanded to actually check connections)
    services = {
        "api": True,
        "embeddings": True,  # Will be updated when service is initialized
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
    """
    Readiness check endpoint.
    
    Returns whether the service is ready to accept traffic.
    """
    return {"ready": True}
