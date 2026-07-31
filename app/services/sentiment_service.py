"""
Sentiment Service — Business logic for emotion radar and sentiment evolution.

Replaces direct MongoDB calls in features/sentiment/router.py.

Performance improvement:
  - get_emotion_radar(): was 3 separate count_documents calls → now 1 $group pipeline
  - get_evolution_timeline(): unchanged pipeline, now cached
"""
import logging
from typing import List

from app.config.settings import get_settings
from app.core.constants import (
    CACHE_KEY_SENTIMENT_EMOTIONS,
    CACHE_KEY_SENTIMENT_EVOLUTION,
)
from app.features.sentiment.schemas import EmotionScoreDTO, SentimentEvolutionDTO, SentimentRadarResponse
from app.repositories.feedback import FeedbackRepository
from app.services.cache_service import CacheService

logger = logging.getLogger(__name__)
settings = get_settings()

_EMPTY_EMOTIONS = [
    EmotionScoreDTO(emotion="Joy", score=0.0, percentage=0.0, color="#10b981"),
    EmotionScoreDTO(emotion="Trust", score=0.0, percentage=0.0, color="#3b82f6"),
    EmotionScoreDTO(emotion="Surprise", score=0.0, percentage=0.0, color="#8b5cf6"),
    EmotionScoreDTO(emotion="Frustration", score=0.0, percentage=0.0, color="#f59e0b"),
    EmotionScoreDTO(emotion="Anger", score=0.0, percentage=0.0, color="#ef4444"),
]


class SentimentService:
    """Service for sentiment intelligence: emotion breakdown and evolution timeline."""

    def __init__(self, repository: FeedbackRepository, cache: CacheService) -> None:
        self.repository = repository
        self.cache = cache

    async def get_emotion_radar(self) -> List[EmotionScoreDTO]:
        """
        Compute emotion radar scores from feedback sentiment distribution.
        Uses a single $group pipeline instead of 3 count_documents calls.
        """
        async def _compute() -> list:
            pipeline = [
                {
                    "$group": {
                        "_id": {"$toLower": "$sentiment"},
                        "count": {"$sum": 1},
                    }
                }
            ]
            docs = await self.repository.aggregate(pipeline)

            counts = {d["_id"]: d["count"] for d in docs if d.get("_id")}
            total = sum(counts.values())

            if total == 0:
                return [e.model_dump() for e in _EMPTY_EMOTIONS]

            pos = counts.get("positive", 0)
            neu = counts.get("neutral", 0)
            neg = counts.get("negative", 0)

            pos_pct = round((pos / total) * 100, 1)
            neu_pct = round((neu / total) * 100, 1)
            neg_pct = round((neg / total) * 100, 1)

            return [
                EmotionScoreDTO(emotion="Joy", score=pos_pct, percentage=pos_pct, color="#10b981").model_dump(),
                EmotionScoreDTO(emotion="Trust", score=round(pos_pct * 0.5, 1), percentage=round(pos_pct * 0.5, 1), color="#3b82f6").model_dump(),
                EmotionScoreDTO(emotion="Surprise", score=neu_pct, percentage=neu_pct, color="#8b5cf6").model_dump(),
                EmotionScoreDTO(emotion="Frustration", score=round(neg_pct * 0.7, 1), percentage=round(neg_pct * 0.7, 1), color="#f59e0b").model_dump(),
                EmotionScoreDTO(emotion="Anger", score=round(neg_pct * 0.3, 1), percentage=round(neg_pct * 0.3, 1), color="#ef4444").model_dump(),
            ]

        data = await self.cache.get_or_set(
            key=CACHE_KEY_SENTIMENT_EMOTIONS,
            factory=_compute,
            ttl=settings.CACHE_TTL_SENTIMENT,
        )
        return [EmotionScoreDTO(**d) for d in data]

    async def get_evolution_timeline(self) -> List[SentimentEvolutionDTO]:
        """Retrieve historical sentiment evolution computed from daily feedback groups."""
        async def _compute() -> list:
            pipeline = [
                {
                    "$group": {
                        "_id": {
                            "$dateToString": {"format": "%Y-%m-%d", "date": "$created_at"}
                        },
                        "total": {"$sum": 1},
                        "positive": {
                            "$sum": {"$cond": [{"$eq": [{"$toLower": "$sentiment"}, "positive"]}, 1, 0]}
                        },
                    }
                },
                {"$sort": {"_id": 1}},
            ]
            docs = await self.repository.aggregate(pipeline)

            result = []
            for d in docs:
                tot = d.get("total", 1)
                pos = d.get("positive", 0)
                ratio = round(pos / tot, 2) if tot > 0 else 0.0
                result.append(SentimentEvolutionDTO(
                    date=d.get("_id") or "Today",
                    sentimentIndex=round((ratio * 2) - 1, 2),
                    positiveRatio=ratio,
                ).model_dump())
            return result

        data = await self.cache.get_or_set(
            key=CACHE_KEY_SENTIMENT_EVOLUTION,
            factory=_compute,
            ttl=settings.CACHE_TTL_SENTIMENT,
        )
        return [SentimentEvolutionDTO(**d) for d in data]

    async def get_emotion_radar_response(self) -> SentimentRadarResponse:
        """Combine emotion radar scores and evolution timeline in one response."""
        emotions = await self.get_emotion_radar()
        timeline = await self.get_evolution_timeline()
        return SentimentRadarResponse(emotions=emotions, timeSeries=timeline)

