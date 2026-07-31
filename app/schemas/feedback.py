"""
Pydantic schemas for Feedback requests and responses.
"""
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class SentimentEnum(str, Enum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"


class CreateFeedbackRequest(BaseModel):
    """Schema for submitting new feedback."""
    sentiment: SentimentEnum = Field(
        ...,
        description="Feedback sentiment. Allowed values: positive, neutral, negative",
        examples=["positive"]
    )
    comment: Optional[str] = Field(
        default="",
        max_length=1000,
        description="Optional feedback comment (max 1000 characters)",
        examples=["Great dashboard"]
    )


class FeedbackActionResponse(BaseModel):
    """Standard success response for feedback creation."""
    success: bool = Field(default=True, examples=[True])
    message: str = Field(default="Feedback submitted successfully", examples=["Feedback submitted successfully"])


class FeedbackItemResponse(BaseModel):
    """Individual feedback item schema."""
    id: Optional[str] = Field(default=None, description="MongoDB Document ID", examples=["679a1234567890abcdef1234"])
    sentiment: str = Field(..., description="Sentiment category", examples=["positive"])
    comment: Optional[str] = Field(default="", description="Feedback comment text", examples=["Great dashboard"])
    created_at: str = Field(..., description="Creation ISO timestamp", examples=["2026-07-30T10:00:00Z"])


class DashboardStatsResponse(BaseModel):
    """Schema for dashboard statistics API."""
    total_feedback: int = Field(..., description="Total feedback count", examples=[120])
    positive: int = Field(..., description="Positive feedback count", examples=[70])
    neutral: int = Field(..., description="Neutral feedback count", examples=[25])
    negative: int = Field(..., description="Negative feedback count", examples=[25])
    latest_feedback: List[FeedbackItemResponse] = Field(
        default_factory=list,
        description="Top 10 latest submitted feedbacks"
    )
