"""
Schemas package — Pydantic v2 request/response DTOs.
"""
from typing import Generic, Optional, TypeVar
from pydantic import BaseModel

T = TypeVar("T")


class BaseResponse(BaseModel):
    """Standard API response envelope."""

    success: bool = True
    message: str = "OK"


class DataResponse(BaseResponse, Generic[T]):
    """Single-item response envelope."""

    data: Optional[T] = None


class PaginatedResponse(BaseResponse, Generic[T]):
    """Paginated list response envelope."""

    data: list[T] = []
    total: int = 0
    page: int = 1
    page_size: int = 20
    total_pages: int = 0


from app.schemas.feedback import (
    SentimentEnum,
    CreateFeedbackRequest,
    FeedbackActionResponse,
    FeedbackItemResponse,
    DashboardStatsResponse,
)

__all__ = [
    "BaseResponse",
    "DataResponse",
    "PaginatedResponse",
    "SentimentEnum",
    "CreateFeedbackRequest",
    "FeedbackActionResponse",
    "FeedbackItemResponse",
    "DashboardStatsResponse",
]
