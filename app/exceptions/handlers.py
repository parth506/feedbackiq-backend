"""
Global exception handlers registered on the FastAPI app.

All handlers:
  - Include X-Correlation-ID in the response body for traceability.
  - Log at appropriate severity (warning vs. error).
  - Never leak internal stack traces to the client.
"""
import logging

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pymongo.errors import PyMongoError
from redis.exceptions import RedisError

from app.core.constants import LOG_CORRELATION_ID_HEADER
from app.exceptions.exceptions import (
    AnalyticsException,
    CacheException,
    DatabaseException,
    FeedbackIQException,
    SearchException,
)
from app.utils.logging import correlation_id_ctx

logger = logging.getLogger(__name__)


def _corr_id() -> str:
    """Return the active correlation ID (or '-' if outside a request context)."""
    return correlation_id_ctx.get("-")


def register_exception_handlers(app: FastAPI) -> None:
    """Attach all exception handlers to the given FastAPI app instance."""

    # ── Domain base exception ──────────────────────────────────────────────────
    @app.exception_handler(FeedbackIQException)
    async def feedbackiq_exception_handler(
        request: Request, exc: FeedbackIQException
    ) -> JSONResponse:
        corr = _corr_id()
        logger.warning(
            "FeedbackIQException [%s]: %s (HTTP %d)",
            corr, exc.message, exc.status_code,
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message, "success": False, "corr_id": corr},
            headers={LOG_CORRELATION_ID_HEADER: corr},
        )

    # ── Pydantic request validation ────────────────────────────────────────────
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        corr = _corr_id()
        logger.warning("Validation error [%s]: %s", corr, exc.errors())
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "detail": "Request validation failed.",
                "errors": exc.errors(),
                "success": False,
                "corr_id": corr,
            },
            headers={LOG_CORRELATION_ID_HEADER: corr},
        )

    # ── MongoDB errors ─────────────────────────────────────────────────────────
    @app.exception_handler(PyMongoError)
    async def database_exception_handler(
        request: Request, exc: PyMongoError
    ) -> JSONResponse:
        corr = _corr_id()
        logger.error("MongoDB error [%s]: %s", corr, str(exc), exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"detail": "Database service temporarily unavailable.", "success": False, "corr_id": corr},
            headers={LOG_CORRELATION_ID_HEADER: corr},
        )

    # ── Redis errors ───────────────────────────────────────────────────────────
    @app.exception_handler(RedisError)
    async def redis_exception_handler(
        request: Request, exc: RedisError
    ) -> JSONResponse:
        corr = _corr_id()
        logger.error("Redis error [%s]: %s", corr, str(exc), exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"detail": "Cache service temporarily unavailable.", "success": False, "corr_id": corr},
            headers={LOG_CORRELATION_ID_HEADER: corr},
        )

    # ── DatabaseException (domain-level wrapper) ───────────────────────────────
    @app.exception_handler(DatabaseException)
    async def domain_database_exception_handler(
        request: Request, exc: DatabaseException
    ) -> JSONResponse:
        corr = _corr_id()
        logger.error("DatabaseException [%s]: %s", corr, exc.message, exc_info=True)
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message, "success": False, "corr_id": corr},
            headers={LOG_CORRELATION_ID_HEADER: corr},
        )

    # ── CacheException (non-fatal — logged at WARNING) ─────────────────────────
    @app.exception_handler(CacheException)
    async def domain_cache_exception_handler(
        request: Request, exc: CacheException
    ) -> JSONResponse:
        corr = _corr_id()
        logger.warning("CacheException [%s]: %s", corr, exc.message)
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message, "success": False, "corr_id": corr},
            headers={LOG_CORRELATION_ID_HEADER: corr},
        )

    # ── AnalyticsException ─────────────────────────────────────────────────────
    @app.exception_handler(AnalyticsException)
    async def analytics_exception_handler(
        request: Request, exc: AnalyticsException
    ) -> JSONResponse:
        corr = _corr_id()
        logger.error("AnalyticsException [%s]: %s", corr, exc.message, exc_info=True)
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message, "success": False, "corr_id": corr},
            headers={LOG_CORRELATION_ID_HEADER: corr},
        )

    # ── SearchException ────────────────────────────────────────────────────────
    @app.exception_handler(SearchException)
    async def search_exception_handler(
        request: Request, exc: SearchException
    ) -> JSONResponse:
        corr = _corr_id()
        logger.warning("SearchException [%s]: %s", corr, exc.message)
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message, "success": False, "corr_id": corr},
            headers={LOG_CORRELATION_ID_HEADER: corr},
        )

    # ── Catch-all ─────────────────────────────────────────────────────────────
    @app.exception_handler(Exception)
    async def generic_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        corr = _corr_id()
        logger.exception("Unhandled exception [%s]: %s", corr, exc)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error.", "success": False, "corr_id": corr},
            headers={LOG_CORRELATION_ID_HEADER: corr},
        )
