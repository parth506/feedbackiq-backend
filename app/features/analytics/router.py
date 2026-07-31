"""
Analytics Router — Thin delegate. All logic in AnalyticsService.
"""
from typing import List
from fastapi import APIRouter, Depends

from app.dependencies.feedback import get_analytics_service
from app.features.analytics.schemas import (
    TimeSeriesPointDTO,
    CategoryMetricDTO,
    RatingsResponse,
    GeographicRegionDTO,
    CustomerClusterPointDTO,
    MLResponseDTO,
    CorrelationMetricDTO,
)
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/v1/analytics", tags=["3. Analytics & Time Series"])


@router.get(
    "/time-series",
    response_model=List[TimeSeriesPointDTO],
    summary="Get Time Series Analytics",
    description="Daily feedback volume and sentiment breakdown. Cached 5 minutes.",
)
async def get_time_series(
    service: AnalyticsService = Depends(get_analytics_service),
) -> List[TimeSeriesPointDTO]:
    """Return daily time-series analytics from MongoDB."""
    return await service.get_time_series()


@router.get(
    "/categories",
    response_model=List[CategoryMetricDTO],
    summary="Get Category & Department Analytics",
    description="Per-department feedback distribution metrics. Cached 5 minutes.",
)
async def get_categories(
    service: AnalyticsService = Depends(get_analytics_service),
) -> List[CategoryMetricDTO]:
    """Return category-level feedback distribution metrics."""
    return await service.get_category_metrics()


@router.get(
    "/ratings",
    response_model=RatingsResponse,
    summary="Get Ratings and Length Distribution Analytics",
    description="Live ratings spread and review length density computed from MongoDB.",
)
async def get_ratings(
    service: AnalyticsService = Depends(get_analytics_service),
) -> RatingsResponse:
    """Return ratings spread and review length density."""
    return await service.get_ratings_distribution()


@router.get(
    "/geo",
    response_model=List[GeographicRegionDTO],
    summary="Get Geographical Analytics",
)
async def get_geo(
    service: AnalyticsService = Depends(get_analytics_service),
) -> List[GeographicRegionDTO]:
    return await service.get_geo_regions()


@router.get(
    "/segmentation",
    response_model=List[CustomerClusterPointDTO],
    summary="Get Customer Segmentation Clusters",
)
async def get_segmentation(
    service: AnalyticsService = Depends(get_analytics_service),
) -> List[CustomerClusterPointDTO]:
    return await service.get_customer_clusters()


@router.get(
    "/ml",
    response_model=MLResponseDTO,
    summary="Get ML SHAP Feature Importance & Evaluation",
)
async def get_ml(
    service: AnalyticsService = Depends(get_analytics_service),
) -> MLResponseDTO:
    return await service.get_ml_insights()


@router.get(
    "/correlations",
    response_model=List[CorrelationMetricDTO],
    summary="Get Feature Correlation Matrix",
)
async def get_correlations(
    service: AnalyticsService = Depends(get_analytics_service),
) -> List[CorrelationMetricDTO]:
    return await service.get_correlations()


