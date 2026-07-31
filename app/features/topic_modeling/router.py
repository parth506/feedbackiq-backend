from typing import List
from fastapi import APIRouter
from app.features.topic_modeling.schemas import TopicClusterDTO, KeywordFrequencyDTO

router = APIRouter(prefix="/v1/topics", tags=["5. Topic Modeling & NLP"])

@router.get("/importance", response_model=List[TopicClusterDTO], summary="Get Topic Importance Scores")
async def get_topic_importance() -> List[TopicClusterDTO]:
    """Retrieve unsupervised NLP topic cluster ranking."""
    return [
        TopicClusterDTO(id="t1", name="UI Design & Speed", category="UX", volume=3420, importanceScore=92.0, sentimentScore=0.82),
        TopicClusterDTO(id="t2", name="Checkout & Payments", category="Billing", volume=2150, importanceScore=88.0, sentimentScore=-0.34),
        TopicClusterDTO(id="t3", name="API Documentation", category="Developer", volume=1890, importanceScore=85.0, sentimentScore=0.65),
    ]

@router.get("/keywords", response_model=List[KeywordFrequencyDTO], summary="Get TF-IDF Keyword Cloud Frequency")
async def get_keywords() -> List[KeywordFrequencyDTO]:
    """Retrieve TF-IDF weighted keyword frequencies."""
    return [
        KeywordFrequencyDTO(keyword="UI Speed", frequency=98, sentiment="positive"),
        KeywordFrequencyDTO(keyword="Checkout", frequency=88, sentiment="negative"),
        KeywordFrequencyDTO(keyword="API Docs", frequency=82, sentiment="positive"),
    ]
