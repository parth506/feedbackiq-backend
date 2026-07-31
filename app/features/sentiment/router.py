from typing import List
from fastapi import APIRouter
from app.features.sentiment.schemas import EmotionScoreDTO, SentimentEvolutionDTO

router = APIRouter(prefix="/v1/sentiment", tags=["4. Sentiment Intelligence"])

@router.get("/emotions", response_model=List[EmotionScoreDTO], summary="Get 6-Factor Emotion Radar Scores")
async def get_emotions() -> List[EmotionScoreDTO]:
    """Retrieve 6-factor psychological emotion distribution breakdown."""
    return [
        EmotionScoreDTO(emotion="Joy", score=48.0, percentage=48.0, color="#10b981"),
        EmotionScoreDTO(emotion="Trust", score=24.0, percentage=24.0, color="#3b82f6"),
        EmotionScoreDTO(emotion="Surprise", score=12.0, percentage=12.0, color="#8b5cf6"),
        EmotionScoreDTO(emotion="Frustration", score=9.0, percentage=9.0, color="#f59e0b"),
        EmotionScoreDTO(emotion="Anger", score=4.0, percentage=4.0, color="#ef4444"),
    ]

@router.get("/evolution", response_model=List[SentimentEvolutionDTO], summary="Get Sentiment Evolution Timeline")
async def get_evolution() -> List[SentimentEvolutionDTO]:
    """Retrieve historical sentiment evolution trend line."""
    return [
        SentimentEvolutionDTO(date="Jul 01", sentimentIndex=0.55, positiveRatio=0.68),
        SentimentEvolutionDTO(date="Jul 15", sentimentIndex=0.62, positiveRatio=0.72),
        SentimentEvolutionDTO(date="Jul 30", sentimentIndex=0.68, positiveRatio=0.78),
    ]
