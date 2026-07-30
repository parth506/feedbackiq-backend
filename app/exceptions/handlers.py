"""
Global exception handlers registered on the FastAPI app.
"""
import logging

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pymongo.errors import PyMongoError
from redis.exceptions import RedisError

from app.exceptions.exceptions import FeedbackIQException

logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    """Attach all exception handlers to the given FastAPI app."""

    @app.exception_handler(FeedbackIQException)
    async def feedbackiq_exception_handler(
        request: Request, exc: FeedbackIQException
    ) -> JSONResponse:
        logger.warning("FeedbackIQException handled: %s (Status: %d)", exc.message, exc.status_code)
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message, "success": False},
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        logger.warning("Validation error: %s", exc.errors())
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "detail": "Request validation failed.",
                "errors": exc.errors(),
                "success": False
            },
        )

    @app.exception_handler(PyMongoError)
    async def database_exception_handler(
        request: Request, exc: PyMongoError
    ) -> JSONResponse:
        logger.error("Database error occurred: %s", str(exc), exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Database service error occurred.", "success": False},
        )

    @app.exception_handler(RedisError)
    async def redis_exception_handler(
        request: Request, exc: RedisError
    ) -> JSONResponse:
        logger.error("Cache/Redis error occurred: %s", str(exc), exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Cache service error occurred.", "success": False},
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        logger.exception("Unhandled exception: %s", exc)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error.", "success": False},
        )

