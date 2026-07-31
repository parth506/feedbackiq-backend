"""
Topic Modeling Service — Business logic for topic clusters and keyword frequency.

Replaces direct MongoDB calls in features/topic_modeling/router.py.

Performance improvement:
  - Topic importance: 3 separate count_documents → 1 $facet pipeline
  - Keywords: Python word counting on fetched docs — kept as-is (regex approach
    is acceptable at this scale; can be replaced with $text aggregation later)
"""
import logging
import re
from typing import Dict, List

from app.config.settings import get_settings
from app.core.constants import (
    CACHE_KEY_TOPICS_IMPORTANCE,
    CACHE_KEY_TOPICS_KEYWORDS,
    TOPIC_MIN_WORD_LENGTH,
    TOPIC_SCAN_LIMIT,
    TOPIC_STOPWORDS,
    TOPIC_TOP_KEYWORDS,
)
from app.features.topic_modeling.schemas import KeywordFrequencyDTO, TopicClusterDTO
from app.repositories.feedback import FeedbackRepository
from app.services.cache_service import CacheService

logger = logging.getLogger(__name__)
settings = get_settings()


class TopicModelingService:
    """Service for topic cluster scoring and keyword frequency analysis."""

    def __init__(self, repository: FeedbackRepository, cache: CacheService) -> None:
        self.repository = repository
        self.cache = cache

    async def get_topic_importance(self) -> List[TopicClusterDTO]:
        """
        Compute topic importance scores from MongoDB feedback comments.
        Uses a single $facet pipeline to count UX, Billing, and Developer keywords.
        """
        async def _compute() -> list:
            total = await self.repository.count()
            if total == 0:
                return []

            pipeline = [
                {
                    "$facet": {
                        "ux": [
                            {"$match": {"comment": {"$regex": r"speed|ui|layout|dashboard|fast", "$options": "i"}}},
                            {"$count": "n"},
                        ],
                        "billing": [
                            {"$match": {"comment": {"$regex": r"payment|billing|checkout|price|cost", "$options": "i"}}},
                            {"$count": "n"},
                        ],
                        "docs": [
                            {"$match": {"comment": {"$regex": r"api|doc|sdk|developer|code", "$options": "i"}}},
                            {"$count": "n"},
                        ],
                    }
                }
            ]
            results = await self.repository.aggregate(pipeline)
            if not results:
                return []

            data = results[0]
            ux_count = data["ux"][0]["n"] if data["ux"] else 0
            billing_count = data["billing"][0]["n"] if data["billing"] else 0
            docs_count = data["docs"][0]["n"] if data["docs"] else 0

            return [
                TopicClusterDTO(
                    id="t1", name="UI Design & Speed", category="UX",
                    volume=ux_count,
                    importanceScore=min(99.0, max(10.0, float(ux_count * 10))),
                    sentimentScore=0.82,
                ).model_dump(),
                TopicClusterDTO(
                    id="t2", name="Checkout & Payments", category="Billing",
                    volume=billing_count,
                    importanceScore=min(99.0, max(10.0, float(billing_count * 10))),
                    sentimentScore=-0.34,
                ).model_dump(),
                TopicClusterDTO(
                    id="t3", name="API Documentation", category="Developer",
                    volume=docs_count,
                    importanceScore=min(99.0, max(10.0, float(docs_count * 10))),
                    sentimentScore=0.65,
                ).model_dump(),
            ]

        data = await self.cache.get_or_set(
            key=CACHE_KEY_TOPICS_IMPORTANCE,
            factory=_compute,
            ttl=settings.CACHE_TTL_TOPICS,
        )
        return [TopicClusterDTO(**d) for d in data]

    async def get_keyword_frequencies(self) -> List[KeywordFrequencyDTO]:
        """
        Extract and count the top N keywords from recent feedback comments.
        Filters stopwords, minimum word length, and returns most frequent.
        """
        async def _compute() -> list:
            docs = await self.repository.find(
                projection={"comment": 1, "sentiment": 1},
                limit=TOPIC_SCAN_LIMIT,
            )

            word_counts: Dict[str, Dict] = {}
            for doc in docs:
                comment = doc.get("comment", "")
                sentiment = (doc.get("sentiment") or "positive").lower()
                words = re.findall(r'\b[a-zA-Z]{%d,}\b' % TOPIC_MIN_WORD_LENGTH, comment.lower())
                for word in words:
                    if word not in TOPIC_STOPWORDS:
                        if word not in word_counts:
                            word_counts[word] = {"count": 0, "sentiment": sentiment}
                        word_counts[word]["count"] += 1

            top_words = sorted(word_counts.items(), key=lambda x: x[1]["count"], reverse=True)[:TOPIC_TOP_KEYWORDS]

            return [
                KeywordFrequencyDTO(
                    keyword=word.capitalize(),
                    frequency=stats["count"],
                    sentiment=stats["sentiment"],
                ).model_dump()
                for word, stats in top_words
            ]

        data = await self.cache.get_or_set(
            key=CACHE_KEY_TOPICS_KEYWORDS,
            factory=_compute,
            ttl=settings.CACHE_TTL_TOPICS,
        )
        return [KeywordFrequencyDTO(**d) for d in data]
