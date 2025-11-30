"""Main API router combining all v1 endpoints."""

from fastapi import APIRouter

from app.api.v1.funds import router as funds_router
from app.api.v1.health import router as health_router
from app.api.v1.query import router as query_router

api_router = APIRouter()

api_router.include_router(health_router)
api_router.include_router(query_router)
api_router.include_router(funds_router)
