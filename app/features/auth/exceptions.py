from fastapi import status
from app.exceptions.exceptions import FeedbackIQException

class InvalidCredentialsException(FeedbackIQException):
    def __init__(self, message: str = "Invalid email or password.") -> None:
        super().__init__(message=message, status_code=status.HTTP_401_UNAUTHORIZED)

class TokenExpiredException(FeedbackIQException):
    def __init__(self, message: str = "Authentication token has expired.") -> None:
        super().__init__(message=message, status_code=status.HTTP_401_UNAUTHORIZED)
