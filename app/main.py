"""
FeedbackIQ — Application Entry Point
"""

from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.settings import get_settings
from app.utils.logging import setup_logging

# Initialize logging
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
    """Application startup/shutdown lifecycle."""

    # Startup
    try:
        await connect_db()
        logger.info("✅ MongoDB Connected")
    except Exception as exc:
        logger.exception("❌ Failed to connect to MongoDB: %s", exc)

    try:
        await connect_redis()
        logger.info("✅ Redis Connected")
    except Exception as exc:
        logger.warning(
            "⚠️ Redis unavailable. Running without cache. %s",
            exc,
        )

    yield

    # Shutdown
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
        description="FeedbackIQ API",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # ==========================================================================
    # CORS
    # ==========================================================================

    allowed_origins = [
        "http://localhost:3000",
        "http://localhost:5173",
        "https://feediq2.netlify.app",
    ]

    application.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
    )

    # ==========================================================================
    # Middleware
    # ==========================================================================

    application.add_middleware(RequestTimingMiddleware)
    application.add_middleware(RequestLoggingMiddleware)

    # ==========================================================================
    # Exception Handlers
    # ==========================================================================

    register_exception_handlers(application)

    # ==========================================================================
    # Routes
    # ==========================================================================

    application.include_router(api_router)

    @application.get("/")
    async def root():
        return {
            "message": "FeedbackIQ Backend Running 🚀",
            "docs": "/docs",
        }

    return application


app = create_app()