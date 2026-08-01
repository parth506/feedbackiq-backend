"""
API package — Minimal Router Aggregator.
Only includes: health, feedback/dashboard, and auth.
"""
from fastapi import APIRouter

from app.routers.health import router as health_router
from app.routers.feedback import router as feedback_router
from app.features.auth.router import router as auth_v1_router

api_router = APIRouter()

# Health check endpoints
api_router.include_router(health_router)

# Feedback + dashboard endpoints (/api/feedback, /api/dashboard)
api_router.include_router(feedback_router, prefix="/api")

# Auth endpoints (/api/v1/auth/login, /api/v1/auth/register, /api/v1/auth/me)
api_router.include_router(auth_v1_router, prefix="/api")
