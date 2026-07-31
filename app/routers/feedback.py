"""
Feedback Router — Handles API endpoints for feedback submission, dashboard stats, and search.
"""
from typing import List
from fastapi import APIRouter, Depends, Query, status

from app.dependencies.feedback import get_feedback_service
from app.schemas.feedback import (
    CreateFeedbackRequest,
    FeedbackActionResponse,
    DashboardStatsResponse,
    FeedbackItemResponse,
    KPIMetricsResponse,
)
from app.services.feedback import FeedbackService

router = APIRouter(tags=["Feedback & Dashboard"])


@router.post(
    "/feedback",
    response_model=FeedbackActionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Store a new feedback",
    description="Stores new feedback entry in MongoDB and invalidates Redis dashboard stats cache.",
    responses={
        201: {
            "description": "Feedback submitted successfully",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "Feedback submitted successfully"
                    }
                }
            },
        },
        422: {
            "description": "Validation error (e.g. invalid sentiment)",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Request validation failed.",
                        "errors": [{"loc": ["body", "sentiment"], "msg": "Input should be 'positive', 'neutral' or 'negative'"}],
                        "success": False
                    }
                }
            },
        },
    },
)
async def create_feedback(
    request: CreateFeedbackRequest,
    service: FeedbackService = Depends(get_feedback_service),
) -> FeedbackActionResponse:
    """Store a new feedback entry."""
    return await service.create_feedback(request)


@router.get(
    "/dashboard",
    response_model=DashboardStatsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get dashboard statistics",
    description="Returns aggregate feedback counts and top 10 latest feedbacks. Reads from Redis cache when available, falling back to MongoDB.",
    responses={
        200: {
            "description": "Dashboard statistics data",
            "content": {
                "application/json": {
                    "example": {
                        "total_feedback": 120,
                        "positive": 70,
                        "neutral": 25,
                        "negative": 25,
                        "latest_feedback": [
                            {
                                "id": "679a1234567890abcdef1234",
                                "sentiment": "positive",
                                "comment": "Great dashboard layout",
                                "created_at": "2026-07-30T10:00:00Z"
                            }
                        ]
                    }
                }
            },
        }
    },
)
async def get_dashboard_stats(
    service: FeedbackService = Depends(get_feedback_service),
) -> DashboardStatsResponse:
    """Return aggregate statistics and latest feedbacks."""
    return await service.dashboard_stats()


@router.get(
    "/v1/dashboard/kpis",
    response_model=KPIMetricsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get live executive KPIs",
    description="Returns aggregate KPI metrics computed live from MongoDB.",
)
async def get_dashboard_kpis(
    service: FeedbackService = Depends(get_feedback_service),
) -> KPIMetricsResponse:
    """Return live calculated executive KPIs."""
    return await service.get_kpi_metrics()



@router.get(
    "/search",
    response_model=List[FeedbackItemResponse],
    status_code=status.HTTP_200_OK,
    summary="Search comments",
    description="Case-insensitive keyword search inside feedback comments.",
    responses={
        200: {
            "description": "List of matching feedback documents",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": "679a1234567890abcdef1234",
                            "sentiment": "positive",
                            "comment": "Great dashboard layout",
                            "created_at": "2026-07-30T10:00:00Z"
                        }
                    ]
                }
            },
        }
    },
)
async def search_feedback(
    q: str = Query(..., description="Keyword query string to search inside comments", example="dashboard"),
    service: FeedbackService = Depends(get_feedback_service),
) -> List[FeedbackItemResponse]:
    """Search feedback comments by keyword."""
    return await service.search_feedback(q)
