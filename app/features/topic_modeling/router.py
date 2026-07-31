"""
Topic Modeling Router — Thin delegate. All logic in TopicModelingService.
"""
from typing import List
from fastapi import APIRouter, Depends

from app.dependencies.feedback import get_topic_service
from app.features.topic_modeling.schemas import TopicClusterDTO, KeywordFrequencyDTO
from app.services.topic_service import TopicModelingService

router = APIRouter(prefix="/v1/topics", tags=["5. Topic Modeling & NLP"])


@router.get(
    "/importance",
    response_model=List[TopicClusterDTO],
    summary="Get Topic Importance Scores",
    description="Topic cluster scores extracted from MongoDB comment documents. Cached 10 minutes.",
)
async def get_topic_importance(
    service: TopicModelingService = Depends(get_topic_service),
) -> List[TopicClusterDTO]:
    """Return dynamic topic cluster importance scores."""
    return await service.get_topic_importance()


@router.get(
    "/keywords",
    response_model=List[KeywordFrequencyDTO],
    summary="Get Keyword Frequencies",
    description="Top keyword frequencies parsed from real MongoDB feedback comments. Cached 10 minutes.",
)
async def get_keywords(
    service: TopicModelingService = Depends(get_topic_service),
) -> List[KeywordFrequencyDTO]:
    """Return top keyword frequency counts from feedback comments."""
    return await service.get_keyword_frequencies()
