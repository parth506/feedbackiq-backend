"""
AI Insights Service — Business logic for executive summaries and risk recommendations.

Replaces direct MongoDB calls in features/ai_insights/router.py.

Architecture note:
  - Injects LLMProviderInterface (see core/interfaces.py).
  - Currently uses RuleBasedProvider — swap with OpenAI/Anthropic without changing the router.
  - All MongoDB queries use the repository, not direct collection access.
"""
import logging
from typing import List, Protocol

from app.config.settings import get_settings
from app.core.constants import (
    CACHE_KEY_AI_RECOMMENDATIONS,
    CACHE_KEY_AI_SUMMARY,
)
from app.features.ai_insights.schemas import AIInsightDTO, AISummaryDTO
from app.repositories.feedback import FeedbackRepository
from app.services.cache_service import CacheService

logger = logging.getLogger(__name__)
settings = get_settings()


class AIInsightsService:
    """Service for AI-driven executive summaries and prioritized risk alerts."""

    def __init__(self, repository: FeedbackRepository, cache: CacheService) -> None:
        self.repository = repository
        self.cache = cache

    async def get_executive_summary(self) -> AISummaryDTO:
        """
        Generate an executive summary based on live MongoDB feedback metrics.
        Cached to avoid re-computing on every request.
        """
        empty = AISummaryDTO(
            headline="Database Initializing...",
            summary="Awaiting live customer feedback entries in MongoDB Atlas cluster.",
            keyOpportunities=[],
            riskCount=0,
        )

        async def _compute() -> dict:
            pipeline = [
                {
                    "$group": {
                        "_id": None,
                        "total": {"$sum": 1},
                        "positive": {
                            "$sum": {"$cond": [{"$eq": [{"$toLower": "$sentiment"}, "positive"]}, 1, 0]}
                        },
                        "negative": {
                            "$sum": {"$cond": [{"$eq": [{"$toLower": "$sentiment"}, "negative"]}, 1, 0]}
                        },
                    }
                }
            ]
            docs = await self.repository.aggregate(pipeline)
            if not docs or docs[0].get("total", 0) == 0:
                return empty.model_dump()

            d = docs[0]
            total = d["total"]
            pos = d.get("positive", 0)
            neg = d.get("negative", 0)

            pos_pct = round((pos / total) * 100, 1)
            sentiment_index = round((pos - neg) / total, 2)

            return AISummaryDTO(
                headline=f"Feedback Sentiment Index: {sentiment_index:+.2f} ({pos_pct}% Positive)",
                summary=(
                    f"Analysis of {total} feedback records indicates {pos_pct}% positive sentiment. "
                    f"Total positive: {pos}, total negative: {neg}."
                ),
                keyOpportunities=["Improve user onboarding flow", "Monitor checkout payment friction"],
                riskCount=neg,
            ).model_dump()

        data = await self.cache.get_or_set(
            key=CACHE_KEY_AI_SUMMARY,
            factory=_compute,
            ttl=settings.CACHE_TTL_AI_INSIGHTS,
        )
        return AISummaryDTO(**data)

    async def get_risk_recommendations(self) -> List[AIInsightDTO]:
        """
        Generate prioritized risk alerts from the latest negative feedback records.
        Cached with AI insights TTL.
        """
        async def _compute() -> list:
            neg_docs = await self.repository.find(
                filter_query={"sentiment": "negative"},
                limit=5,
            )

            if not neg_docs:
                return [
                    AIInsightDTO(
                        id="sys-1",
                        title="System Operational — No Critical Alerts",
                        category="status",
                        severity="success",
                        description="Zero negative feedback documents currently flagged in MongoDB Atlas.",
                        impactScore=100,
                        suggestedAction="Maintain current SLA response standards.",
                        affectedUsersCount=0,
                        timestamp="Now",
                    ).model_dump()
                ]

            insights = []
            for idx, doc in enumerate(neg_docs):
                comment = doc.get("comment", "Negative feedback reported.")
                insights.append(AIInsightDTO(
                    id=f"neg-{idx + 1}",
                    title=f"Critical Issue #{idx + 1}: {comment[:30]}...",
                    category="root_cause",
                    severity="critical" if idx == 0 else "warning",
                    description=f"Negative feedback: '{comment}'",
                    impactScore=max(50, 95 - (idx * 10)),
                    suggestedAction="Investigate logs and contact customer account.",
                    affectedUsersCount=1,
                    timestamp="Recent",
                ).model_dump())
            return insights

        data = await self.cache.get_or_set(
            key=CACHE_KEY_AI_RECOMMENDATIONS,
            factory=_compute,
            ttl=settings.CACHE_TTL_AI_INSIGHTS,
        )
        return [AIInsightDTO(**d) for d in data]
