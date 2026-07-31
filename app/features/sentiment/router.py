"""
Sentiment Router — Thin delegate. All logic in SentimentService.
"""
from typing import List
from fastapi import APIRouter, Depends

from app.dependencies.feedback import get_sentiment_service
from app.features.sentiment.schemas import EmotionScoreDTO, SentimentEvolutionDTO
from app.services.sentiment_service import SentimentService

router = APIRouter(prefix="/v1/sentiment", tags=["4. Sentiment Intelligence"])


@router.get(
    "/emotions",
    response_model=List[EmotionScoreDTO],
    summary="Get Emotion Radar Scores",
    description="Emotion breakdown computed from live MongoDB feedback. Cached 5 minutes.",
)
async def get_emotions(
    service: SentimentService = Depends(get_sentiment_service),
) -> List[EmotionScoreDTO]:
    """Return emotion radar scores derived from feedback sentiment distribution."""
    return await service.get_emotion_radar()


@router.get(
    "/evolution",
    response_model=List[SentimentEvolutionDTO],
    summary="Get Sentiment Evolution Timeline",
    description="Historical sentiment index trend over time. Cached 5 minutes.",
)
async def get_evolution(
    service: SentimentService = Depends(get_sentiment_service),
) -> List[SentimentEvolutionDTO]:
    """Return daily sentiment evolution timeline."""
    return await service.get_evolution_timeline()
