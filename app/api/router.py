"""
API package — central router aggregator.
"""
from fastapi import APIRouter

from app.routers.health import router as health_router
from app.routers.feedback import router as feedback_router

api_router = APIRouter()

# Health and core endpoints (/, /health, /ping)
api_router.include_router(health_router)

# API endpoints (/api/feedback, /api/dashboard, /api/search)
api_router.include_router(feedback_router, prefix="/api")
