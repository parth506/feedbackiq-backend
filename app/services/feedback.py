"""
Feedback Service — Business logic layer for feedback operations.

Responsibilities:
  - Create feedback (with cache invalidation)
  - Compute and cache dashboard statistics
  - Search feedback by keyword

Design decisions:
  - Injects CacheService instead of calling RedisManager directly.
  - Uses FeedbackRepository.get_dashboard_aggregated() — one Mongo round-trip.
  - Document-to-schema mapping is centralized in _to_feedback_item().
"""
import logging
from datetime import datetime, timezone
from typing import List

from app.core.constants import CACHE_KEY_DASHBOARD, DASHBOARD_LATEST_FEEDBACK_LIMIT
from app.config.settings import get_settings
from app.repositories.feedback import FeedbackRepository
from app.schemas.feedback import (
    CreateFeedbackRequest,
    FeedbackActionResponse,
    FeedbackItemResponse,
    DashboardStatsResponse,
)
from app.services.cache_service import CacheService

logger = logging.getLogger(__name__)
settings = get_settings()


def _doc_to_feedback_item(doc: dict) -> FeedbackItemResponse:
    """Map a raw MongoDB document dict to a FeedbackItemResponse schema."""
    created_at = doc.get("created_at")
    if isinstance(created_at, datetime):
        created_at_str = created_at.isoformat()
    else:
        created_at_str = str(created_at) if created_at else datetime.now(timezone.utc).isoformat()

    return FeedbackItemResponse(
        id=str(doc.get("_id", "")),
        sentiment=doc.get("sentiment", ""),
        comment=doc.get("comment", ""),
        created_at=created_at_str,
    )


class FeedbackService:
    """Service managing business rules, aggregation, and caching for Feedback."""

    def __init__(self, repository: FeedbackRepository, cache: CacheService) -> None:
        self.repository = repository
        self.cache = cache

    async def create_feedback(self, data: CreateFeedbackRequest) -> FeedbackActionResponse:
        """
        Create a feedback entry and invalidate all dashboard and analytics cache keys.
        """
        doc = {
            "sentiment": data.sentiment.value.lower(),
            "comment": data.comment.strip() if data.comment else "",
            "created_at": datetime.now(timezone.utc),
        }
        await self.repository.create(doc)

        # Invalidate dashboard cache so next request recomputes from MongoDB
        await self.cache.delete(CACHE_KEY_DASHBOARD)
        logger.info("Invalidated cache key '%s' after feedback creation.", CACHE_KEY_DASHBOARD)

        return FeedbackActionResponse(
            success=True,
            message="Feedback submitted successfully",
        )

    async def dashboard_stats(self) -> DashboardStatsResponse:
        """
        Return dashboard statistics using cache-aside pattern.
        Uses a single MongoDB aggregation pipeline (one round-trip).
        """
        async def _compute() -> dict:
            logger.info("Computing dashboard stats from MongoDB...")
            agg = await self.repository.get_dashboard_aggregated()

            latest_items = [_doc_to_feedback_item(doc) for doc in agg.get("latest", [])]

            return {
                "total_feedback": agg["total"],
                "positive": agg["positive"],
                "neutral": agg["neutral"],
                "negative": agg["negative"],
                "latest_feedback": [item.model_dump() for item in latest_items],
            }

        data = await self.cache.get_or_set(
            key=CACHE_KEY_DASHBOARD,
            factory=_compute,
            ttl=settings.CACHE_TTL_DASHBOARD,
        )

        return DashboardStatsResponse(**data)

    async def search_feedback(self, query_str: str, limit: int = 20) -> List[FeedbackItemResponse]:
        """
        Search feedback comments by keyword.
        Returns latest N results when query is empty.
        """
        if not query_str or not query_str.strip():
            docs = await self.repository.find_latest(limit=limit)
        else:
            docs = await self.repository.search(query_str.strip(), limit=limit)

        return [_doc_to_feedback_item(doc) for doc in docs]
