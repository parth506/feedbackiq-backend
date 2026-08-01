"""
API package — Central Router Aggregator.
Includes /api/v1 versioned feature routes and core unversioned endpoints.
"""
from fastapi import APIRouter

# Health & Unversioned
from app.routers.health import router as health_router
from app.routers.feedback import router as feedback_router

# Versioned Feature Routers (/api/v1)
from app.features.auth.router import router as auth_v1_router
from app.features.analytics.router import router as analytics_v1_router
from app.features.sentiment.router import router as sentiment_v1_router
from app.features.topic_modeling.router import router as topics_v1_router
from app.features.ai_insights.router import router as insights_v1_router
from app.features.predictions.router import router as predictions_v1_router
from app.features.search.router import router as search_v1_router
from app.features.reports.router import router as reports_v1_router
from app.features.users.router import router as users_v1_router
from app.features.organizations.router import router as org_v1_router
from app.features.uploads.router import router as uploads_v1_router
from app.features.notifications.router import router as notifications_v1_router
from app.features.admin.router import router as admin_v1_router
from app.features.monitoring.router import router as monitoring_v1_router
from app.features.integrations.router import router as integrations_v1_router

api_router = APIRouter()

# ── Health & Root (/ , /health, /ping) ────────────────────────────────────────
api_router.include_router(health_router)

# ── Base API compatibility (/api/feedback, /api/dashboard, /api/search) ────────
api_router.include_router(feedback_router, prefix="/api")

# ── Versioned Feature APIs (/api/v1/...) ──────────────────────────────────────
v1_router = APIRouter(prefix="/api")
v1_router.include_router(auth_v1_router)
v1_router.include_router(analytics_v1_router)
v1_router.include_router(sentiment_v1_router)
v1_router.include_router(topics_v1_router)
v1_router.include_router(insights_v1_router)
v1_router.include_router(predictions_v1_router)
v1_router.include_router(search_v1_router)
v1_router.include_router(reports_v1_router)
v1_router.include_router(users_v1_router)
v1_router.include_router(org_v1_router)
v1_router.include_router(uploads_v1_router)
v1_router.include_router(notifications_v1_router)
v1_router.include_router(admin_v1_router)
v1_router.include_router(monitoring_v1_router)
v1_router.include_router(integrations_v1_router)

api_router.include_router(v1_router)
