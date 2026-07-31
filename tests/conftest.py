"""
Test configuration and shared fixtures for FeedbackIQ backend tests.

Provides:
  - mock_cache: CacheService with all methods mocked (always cache miss → forces DB calls)
  - mock_repository: FeedbackRepository with core methods mocked
  - test_app: FastAPI app with dependency overrides applied
  - async_client: HTTPX AsyncClient for integration tests
"""
import pytest
from unittest.mock import AsyncMock, MagicMock
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.dependencies.feedback import (
    get_feedback_service,
    get_analytics_service,
    get_sentiment_service,
    get_topic_service,
    get_ai_service,
    get_search_service,
    get_monitoring_service,
    get_feedback_repository,
)
from app.services.cache_service import CacheService
from app.repositories.feedback import FeedbackRepository
from app.services.monitoring_service import MonitoringService


@pytest.fixture
def mock_cache() -> CacheService:
    """CacheService mock — always returns cache miss, set/delete are no-ops."""
    cache = MagicMock(spec=CacheService)
    cache.get = AsyncMock(return_value=None)           # always miss
    cache.set = AsyncMock(return_value=True)
    cache.delete = AsyncMock(return_value=1)
    async def _get_or_set(key, factory, ttl=None):
        return await factory()
    cache.get_or_set = AsyncMock(side_effect=_get_or_set)
    return cache


@pytest.fixture
def mock_repository() -> FeedbackRepository:
    """FeedbackRepository mock with sensible default return values."""
    repo = MagicMock(spec=FeedbackRepository)
    repo.create = AsyncMock(return_value={"_id": "test_id_123", "sentiment": "positive", "comment": "test", "created_at": None})
    repo.count = AsyncMock(return_value=10)
    repo.find_latest = AsyncMock(return_value=[
        {"_id": "abc123", "sentiment": "positive", "comment": "Great product!", "created_at": None}
    ])
    repo.search = AsyncMock(return_value=[
        {"_id": "abc123", "sentiment": "positive", "comment": "Great product!", "created_at": None}
    ])
    repo.aggregate = AsyncMock(return_value=[
        {"_id": "positive", "count": 7},
        {"_id": "neutral", "count": 2},
        {"_id": "negative", "count": 1},
    ])
    repo.get_dashboard_aggregated = AsyncMock(return_value={
        "total": 10, "positive": 7, "neutral": 2, "negative": 1,
        "latest": [{"_id": "abc123", "sentiment": "positive", "comment": "test", "created_at": None}]
    })
    repo.find = AsyncMock(return_value=[
        {"_id": "abc123", "sentiment": "positive", "comment": "test", "created_at": None}
    ])
    return repo


@pytest.fixture
def mock_monitoring_service() -> MonitoringService:
    """MonitoringService mock with fixed metric values."""
    svc = MagicMock(spec=MonitoringService)
    svc.get_metrics = MagicMock(return_value={
        "uptime_seconds": 3600.0,
        "requests_total": 100,
        "error_rate": 0.01,
    })
    return svc


@pytest.fixture
async def async_client(mock_repository, mock_cache, mock_monitoring_service):
    """
    HTTPX AsyncClient with all service dependencies overridden to use mocks.
    """
    from app.services.feedback import FeedbackService
    from app.services.analytics_service import AnalyticsService
    from app.services.sentiment_service import SentimentService
    from app.services.topic_service import TopicModelingService
    from app.services.ai_service import AIInsightsService
    from app.services.search_service import SearchService

    app.dependency_overrides[get_feedback_repository] = lambda: mock_repository
    app.dependency_overrides[get_feedback_service] = lambda: FeedbackService(mock_repository, mock_cache)
    app.dependency_overrides[get_analytics_service] = lambda: AnalyticsService(mock_repository, mock_cache)
    app.dependency_overrides[get_sentiment_service] = lambda: SentimentService(mock_repository, mock_cache)
    app.dependency_overrides[get_topic_service] = lambda: TopicModelingService(mock_repository, mock_cache)
    app.dependency_overrides[get_ai_service] = lambda: AIInsightsService(mock_repository, mock_cache)
    app.dependency_overrides[get_search_service] = lambda: SearchService(mock_repository)
    app.dependency_overrides[get_monitoring_service] = lambda: mock_monitoring_service

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()
