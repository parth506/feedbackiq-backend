"""
FastAPI dependency providers for all Repositories and Services.

Dependency graph:
  get_db()  ──► get_feedback_repository()
  get_cache_service()  ──┐
                          ├──► get_feedback_service()
  get_feedback_repository() ──┘

  get_feedback_repository() + get_cache_service()
    ──► get_analytics_service()
    ──► get_sentiment_service()
    ──► get_topic_service()
    ──► get_ai_service()

  get_feedback_repository()
    ──► get_search_service()

  (no deps)
    ──► get_monitoring_service()
"""
from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.dependencies.db import get_db
from app.dependencies.cache import get_cache_service
from app.repositories.feedback import FeedbackRepository
from app.services.feedback import FeedbackService
from app.services.cache_service import CacheService
from app.services.analytics_service import AnalyticsService
from app.services.sentiment_service import SentimentService
from app.services.topic_service import TopicModelingService
from app.services.ai_service import AIInsightsService
from app.services.search_service import SearchService
from app.services.monitoring_service import MonitoringService


# ── Repository ────────────────────────────────────────────────────────────────

def get_feedback_repository(
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> FeedbackRepository:
    """Provide a FeedbackRepository bound to the active Motor database."""
    return FeedbackRepository(db=db)


# ── Core Services ──────────────────────────────────────────────────────────────

def get_feedback_service(
    repository: FeedbackRepository = Depends(get_feedback_repository),
    cache: CacheService = Depends(get_cache_service),
) -> FeedbackService:
    """Provide FeedbackService with injected repository and cache."""
    return FeedbackService(repository=repository, cache=cache)


def get_analytics_service(
    repository: FeedbackRepository = Depends(get_feedback_repository),
    cache: CacheService = Depends(get_cache_service),
) -> AnalyticsService:
    """Provide AnalyticsService with injected repository and cache."""
    return AnalyticsService(repository=repository, cache=cache)


def get_sentiment_service(
    repository: FeedbackRepository = Depends(get_feedback_repository),
    cache: CacheService = Depends(get_cache_service),
) -> SentimentService:
    """Provide SentimentService with injected repository and cache."""
    return SentimentService(repository=repository, cache=cache)


def get_topic_service(
    repository: FeedbackRepository = Depends(get_feedback_repository),
    cache: CacheService = Depends(get_cache_service),
) -> TopicModelingService:
    """Provide TopicModelingService with injected repository and cache."""
    return TopicModelingService(repository=repository, cache=cache)


def get_ai_service(
    repository: FeedbackRepository = Depends(get_feedback_repository),
    cache: CacheService = Depends(get_cache_service),
) -> AIInsightsService:
    """Provide AIInsightsService with injected repository and cache."""
    return AIInsightsService(repository=repository, cache=cache)


def get_search_service(
    repository: FeedbackRepository = Depends(get_feedback_repository),
) -> SearchService:
    """Provide SearchService with injected repository (no cache — search results not cached)."""
    return SearchService(repository=repository)


def get_monitoring_service() -> MonitoringService:
    """Provide MonitoringService (stateless process-scoped counters)."""
    return MonitoringService()
