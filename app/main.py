"""
FeedbackIQ — Application Entry Point
"""

from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.settings import get_settings
from app.utils.logging import setup_logging

# Initialize logging before any other imports that might log
setup_logging()
logger = logging.getLogger(__name__)

from app.database.session import connect_db, disconnect_db, get_database
from app.cache.client import connect_redis, disconnect_redis
from app.middleware.logging import RequestLoggingMiddleware
from app.middleware.timing import RequestTimingMiddleware
from app.middleware.correlation import CorrelationIDMiddleware
from app.exceptions.handlers import register_exception_handlers
from app.api.router import api_router
from app.core.indexes import ensure_indexes

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup/shutdown lifecycle."""

    # ── Startup ────────────────────────────────────────────────────────────────
    try:
        await connect_db()
        logger.info("✅ MongoDB Connected")
    except Exception as exc:
        logger.exception("❌ Failed to connect to MongoDB: %s", exc)

    # Ensure indexes after DB is connected
    try:
        db = get_database()
        if db is not None:
            await ensure_indexes(db)
    except Exception as exc:
        logger.warning("⚠️  Index creation skipped: %s", exc)

    try:
        await connect_redis()
        logger.info("✅ Redis Connected")
    except Exception as exc:
        logger.warning(
            "⚠️  Redis unavailable. Running without cache. %s",
            exc,
        )

    yield

    # ── Shutdown ───────────────────────────────────────────────────────────────
    try:
        await disconnect_db()
    except Exception as exc:
        logger.warning("MongoDB disconnect error: %s", exc)

    try:
        await disconnect_redis()
    except Exception as exc:
        logger.warning("Redis disconnect error: %s", exc)


def create_app() -> FastAPI:
    """Application Factory."""

    application = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="FeedbackIQ — Enterprise AI Analytics Platform API",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # ── CORS ───────────────────────────────────────────────────────────────────
    # Origins sourced from settings (env var) — not hardcoded here.
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=["X-Correlation-ID", "X-Process-Time"],
    )

    # ── Middleware (innermost → outermost execution order) ────────────────────
    # Order matters: Starlette adds middleware as a stack (last added = first executed).
    # Desired execution order: CorrelationID → Timing → Logging
    application.add_middleware(RequestLoggingMiddleware)
    application.add_middleware(RequestTimingMiddleware)
    application.add_middleware(CorrelationIDMiddleware)

    # ── Exception Handlers ─────────────────────────────────────────────────────
    register_exception_handlers(application)

    # ── Routes ────────────────────────────────────────────────────────────────
    application.include_router(api_router)

    @application.get("/", include_in_schema=False)
    async def root():
        return {
            "message": "FeedbackIQ Backend Running 🚀",
            "docs": "/docs",
        }

    return application


app = create_app()