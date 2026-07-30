"""
Health & core routers — GET /, GET /health, GET /ping
"""
import logging

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.config.settings import get_settings
from app.database.session import get_database
from app.cache.client import get_redis

logger = logging.getLogger(__name__)
settings = get_settings()

router = APIRouter(tags=["Health & Core"])


@router.get(
    "/",
    summary="Root Endpoint",
    description="API root endpoint returning system welcome message and documentation links.",
    responses={
        200: {
            "description": "API Root Welcome",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Welcome to FeedbackIQ API",
                        "version": "0.1.0",
                        "docs": "/docs"
                    }
                }
            },
        }
    },
)
async def root() -> dict:
    """API root — confirms the service is running."""
    return {
        "message": f"Welcome to {settings.APP_NAME} API",
        "version": settings.APP_VERSION,
        "docs": "/docs",
    }


@router.get(
    "/ping",
    summary="Ping Endpoint",
    description="Lightweight liveness ping check.",
    responses={
        200: {
            "description": "Ping Response",
            "content": {
                "application/json": {
                    "example": {"ping": "pong"}
                }
            },
        }
    },
)
async def ping() -> dict:
    """Lightweight liveness check."""
    return {"ping": "pong"}


@router.get(
    "/health",
    summary="Health Check Endpoint",
    description="Deep health check verifying connection status to MongoDB and Redis.",
    responses={
        200: {
            "description": "All services healthy",
            "content": {
                "application/json": {
                    "example": {
                        "status": "ok",
                        "app": "FeedbackIQ",
                        "version": "0.1.0",
                        "mongo": "connected",
                        "redis": "connected"
                    }
                }
            },
        },
        503: {
            "description": "Service degraded",
            "content": {
                "application/json": {
                    "example": {
                        "status": "degraded",
                        "app": "FeedbackIQ",
                        "version": "0.1.0",
                        "mongo": "connected",
                        "redis": "unavailable"
                    }
                }
            },
        },
    },
)
async def health_check() -> JSONResponse:
    """
    Deep health check — verifies MongoDB and Redis connectivity.
    Returns HTTP 200 when all systems are healthy, 503 otherwise.
    """
    status_dict: dict = {"status": "ok", "app": settings.APP_NAME, "version": settings.APP_VERSION}
    http_status = 200

    # MongoDB
    try:
        db = get_database()
        await db.command("ping")
        status_dict["mongo"] = "connected"
    except Exception as exc:
        logger.warning("Health check — MongoDB error: %s", exc)
        status_dict["mongo"] = "unavailable"
        status_dict["status"] = "degraded"
        http_status = 503

    # Redis
    try:
        redis_client = get_redis()
        if redis_client is not None:
            await redis_client.ping()
            status_dict["redis"] = "connected"
        else:
            status_dict["redis"] = "unavailable"
    except Exception as exc:
        logger.warning("Health check — Redis error: %s", exc)
        status_dict["redis"] = "unavailable"

    return JSONResponse(content=status_dict, status_code=http_status)
