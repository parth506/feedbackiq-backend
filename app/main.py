"""
FeedbackIQ — Application Entry Point
"""
from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.settings import get_settings
from app.utils.logging import setup_logging

# Initialize logging configuration
setup_logging()
logger = logging.getLogger(__name__)

from app.database.session import connect_db, disconnect_db
from app.cache.client import connect_redis, disconnect_redis
from app.middleware.logging import RequestLoggingMiddleware
from app.middleware.timing import RequestTimingMiddleware
from app.exceptions.handlers import register_exception_handlers
from app.api.router import api_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application resources across startup and shutdown."""
    # Startup: MongoDB & Redis connection
    try:
        await connect_db()
    except Exception as exc:
        logger.error("Failed to connect to MongoDB at startup: %s", exc)

    try:
        await connect_redis()
    except Exception as exc:
        logger.warning("Failed to connect to Redis at startup: %s. Continuing in MongoDB fallback mode.", exc)

    yield

    # Shutdown: MongoDB & Redis disconnection
    try:
        await disconnect_db()
    except Exception as exc:
        logger.warning("Error disconnecting MongoDB: %s", exc)

    try:
        await disconnect_redis()
    except Exception as exc:
        logger.warning("Error disconnecting Redis: %s", exc)


def create_app() -> FastAPI:
    """FastAPI Application Factory."""
    application = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="FeedbackIQ — Production-ready Intelligent Feedback Management Platform API",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # ── CORS Middleware ────────────────────────────────────────────────────────
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Custom Middleware ─────────────────────────────────────────────────────
    application.add_middleware(RequestTimingMiddleware)
    application.add_middleware(RequestLoggingMiddleware)

    # ── Exception Handlers ────────────────────────────────────────────────────
    register_exception_handlers(application)

    # ── Routers ───────────────────────────────────────────────────────────────
    application.include_router(api_router)

    return application


app = create_app()
