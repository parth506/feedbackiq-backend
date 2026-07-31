"""
Custom exception classes for FeedbackIQ.

Hierarchy:
  FeedbackIQException (base)
    ├── NotFoundException
    ├── ConflictException
    ├── ValidationException
    ├── UnauthorizedException
    ├── ForbiddenException
    ├── DatabaseException        ← Phase 1 addition
    ├── CacheException           ← Phase 1 addition
    ├── AnalyticsException       ← Phase 1 addition
    └── SearchException          ← Phase 1 addition

Design decisions:
  - All exceptions carry `status_code` so handlers need zero logic.
  - DatabaseException and CacheException are 503 — service is degraded.
  - AnalyticsException is 500 — unexpected aggregation failure.
  - SearchException is 400 — invalid search input is a client error.
"""
from fastapi import status


class FeedbackIQException(Exception):
    """Base application exception. All domain exceptions inherit from this."""

    def __init__(
        self,
        message: str = "An unexpected error occurred.",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
    ) -> None:
        self.message = message
        self.status_code = status_code
        super().__init__(message)


# ── HTTP 4xx ──────────────────────────────────────────────────────────────────

class NotFoundException(FeedbackIQException):
    """Resource not found."""

    def __init__(self, resource: str = "Resource", resource_id: str = "") -> None:
        detail = f"{resource} '{resource_id}' not found." if resource_id else f"{resource} not found."
        super().__init__(message=detail, status_code=status.HTTP_404_NOT_FOUND)


class ConflictException(FeedbackIQException):
    """Resource conflict (e.g., duplicate)."""

    def __init__(self, message: str = "Resource already exists.") -> None:
        super().__init__(message=message, status_code=status.HTTP_409_CONFLICT)


class ValidationException(FeedbackIQException):
    """Business-level validation error (distinct from Pydantic's RequestValidationError)."""

    def __init__(self, message: str = "Validation failed.") -> None:
        super().__init__(message=message, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


class UnauthorizedException(FeedbackIQException):
    """Unauthorized access — missing or invalid authentication."""

    def __init__(self, message: str = "Authentication required.") -> None:
        super().__init__(message=message, status_code=status.HTTP_401_UNAUTHORIZED)


class ForbiddenException(FeedbackIQException):
    """Forbidden — authenticated but insufficient permissions."""

    def __init__(self, message: str = "You do not have permission to perform this action.") -> None:
        super().__init__(message=message, status_code=status.HTTP_403_FORBIDDEN)


class SearchException(FeedbackIQException):
    """
    Invalid or unsupported search request (client error).
    Examples: empty query, query too long, disallowed characters.
    """

    def __init__(self, message: str = "Invalid search query.") -> None:
        super().__init__(message=message, status_code=status.HTTP_400_BAD_REQUEST)


# ── HTTP 5xx ──────────────────────────────────────────────────────────────────

class DatabaseException(FeedbackIQException):
    """
    Unexpected MongoDB failure — wraps PyMongoError for domain isolation.
    Returns 503 so clients know the service is temporarily degraded.
    """

    def __init__(self, message: str = "Database service error.", operation: str = "") -> None:
        detail = f"Database error during '{operation}'." if operation else message
        super().__init__(message=detail, status_code=status.HTTP_503_SERVICE_UNAVAILABLE)


class CacheException(FeedbackIQException):
    """
    Redis failure — wraps redis.exceptions.RedisError.
    Non-fatal by design: callers should fall back to DB, not raise.
    """

    def __init__(self, message: str = "Cache service error.", key: str = "") -> None:
        detail = f"Cache error for key '{key}'." if key else message
        super().__init__(message=detail, status_code=status.HTTP_503_SERVICE_UNAVAILABLE)


class AnalyticsException(FeedbackIQException):
    """
    Failed analytics computation — unexpected aggregation pipeline error.
    Returns 500 Internal Server Error.
    """

    def __init__(self, message: str = "Analytics computation failed.", metric: str = "") -> None:
        detail = f"Analytics error computing '{metric}'." if metric else message
        super().__init__(message=detail, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
