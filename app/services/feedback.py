"""
Feedback Service — Business logic layer.
"""
from datetime import datetime, timezone
import json
import logging
from typing import List

from app.cache.client import RedisManager
from app.repositories.feedback import FeedbackRepository
from app.schemas.feedback import (
    CreateFeedbackRequest,
    FeedbackActionResponse,
    FeedbackItemResponse,
    DashboardStatsResponse,
)

logger = logging.getLogger(__name__)

CACHE_KEY_DASHBOARD = "dashboard_stats"
CACHE_EXPIRATION_SECONDS = 300  # 5 minutes


class FeedbackService:
    """Service managing business rules, aggregation, and caching for Feedback."""

    def __init__(self, repository: FeedbackRepository) -> None:
        self.repository = repository

    async def create_feedback(self, data: CreateFeedbackRequest) -> FeedbackActionResponse:
        """Create feedback and invalidate dashboard stats cache in Redis."""
        doc = {
            "sentiment": data.sentiment.value.lower(),
            "comment": data.comment.strip() if data.comment else "",
            "created_at": datetime.now(timezone.utc),
        }
        await self.repository.create(doc)

        # Invalidate dashboard cache in Redis
        try:
            await RedisManager.delete(CACHE_KEY_DASHBOARD)
            logger.info("Invalidated Redis cache key '%s'", CACHE_KEY_DASHBOARD)
        except Exception as exc:
            logger.warning("Failed to invalidate Redis cache: %s", exc)

        return FeedbackActionResponse(
            success=True,
            message="Feedback submitted successfully"
        )

    async def dashboard_stats(self) -> DashboardStatsResponse:
        """
        Get dashboard statistics.
        1. Check Redis cache first.
        2. If cached, return cached stats.
        3. Else calculate from MongoDB, store in Redis, and return.
        """
        # 1. Check Redis Cache
        try:
            cached_data_str = await RedisManager.get(CACHE_KEY_DASHBOARD)
            if cached_data_str:
                logger.info("Serving dashboard stats from Redis cache.")
                cached_dict = json.loads(cached_data_str)
                return DashboardStatsResponse(**cached_dict)
        except Exception as exc:
            logger.warning("Error fetching dashboard stats from Redis: %s", exc)

        # 2. Compute stats directly from MongoDB
        logger.info("Calculating dashboard stats from MongoDB...")
        total = await self.repository.count()
        positive = await self.repository.count({"sentiment": "positive"})
        neutral = await self.repository.count({"sentiment": "neutral"})
        negative = await self.repository.count({"sentiment": "negative"})
        latest_docs = await self.repository.find_latest(limit=10)

        latest_feedback: List[FeedbackItemResponse] = []
        for doc in latest_docs:
            created_at = doc.get("created_at")
            if isinstance(created_at, datetime):
                created_at_str = created_at.isoformat()
            else:
                created_at_str = str(created_at) if created_at else datetime.now(timezone.utc).isoformat()

            latest_feedback.append(
                FeedbackItemResponse(
                    id=str(doc.get("_id", "")),
                    sentiment=doc.get("sentiment", ""),
                    comment=doc.get("comment", ""),
                    created_at=created_at_str,
                )
            )

        response_dict = {
            "total_feedback": total,
            "positive": positive,
            "neutral": neutral,
            "negative": negative,
            "latest_feedback": [item.model_dump() for item in latest_feedback],
        }

        # 3. Cache the calculated result in Redis
        try:
            await RedisManager.set(
                CACHE_KEY_DASHBOARD,
                json.dumps(response_dict),
                ex=CACHE_EXPIRATION_SECONDS
            )
            logger.info("Cached dashboard stats in Redis for %d seconds.", CACHE_EXPIRATION_SECONDS)
        except Exception as exc:
            logger.warning("Failed to store dashboard stats in Redis: %s", exc)

        return DashboardStatsResponse(**response_dict)

    async def search_feedback(self, query_str: str) -> List[FeedbackItemResponse]:
        """Search feedback comments by keyword."""
        if not query_str:
            docs = await self.repository.find_latest(limit=20)
        else:
            docs = await self.repository.search(query_str)

        results: List[FeedbackItemResponse] = []
        for doc in docs:
            created_at = doc.get("created_at")
            if isinstance(created_at, datetime):
                created_at_str = created_at.isoformat()
            else:
                created_at_str = str(created_at) if created_at else datetime.now(timezone.utc).isoformat()

            results.append(
                FeedbackItemResponse(
                    id=str(doc.get("_id", "")),
                    sentiment=doc.get("sentiment", ""),
                    comment=doc.get("comment", ""),
                    created_at=created_at_str,
                )
            )
        return results
