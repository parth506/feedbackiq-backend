"""
Custom exception classes for FeedbackIQ.
"""
from fastapi import status


class FeedbackIQException(Exception):
    """Base application exception."""

    def __init__(
        self,
        message: str = "An unexpected error occurred.",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
    ) -> None:
        self.message = message
        self.status_code = status_code
        super().__init__(message)


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
    """Business-level validation error."""

    def __init__(self, message: str = "Validation failed.") -> None:
        super().__init__(message=message, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


class UnauthorizedException(FeedbackIQException):
    """Unauthorized access."""

    def __init__(self, message: str = "Authentication required.") -> None:
        super().__init__(message=message, status_code=status.HTTP_401_UNAUTHORIZED)


class ForbiddenException(FeedbackIQException):
    """Forbidden access."""

    def __init__(self, message: str = "You do not have permission to perform this action.") -> None:
        super().__init__(message=message, status_code=status.HTTP_403_FORBIDDEN)
