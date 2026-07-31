"""
AI Insights Router — Thin delegate. All logic in AIInsightsService.
"""
from typing import List
from fastapi import APIRouter, Depends

from app.dependencies.feedback import get_ai_service
from app.features.ai_insights.schemas import AIInsightDTO, AISummaryDTO
from app.services.ai_service import AIInsightsService

router = APIRouter(prefix="/v1/ai-insights", tags=["6. AI Executive Insights"])


@router.get(
    "/summary",
    response_model=AISummaryDTO,
    summary="Get AI Executive Summary",
    description="Natural language executive summary computed from live MongoDB feedback. Cached 10 minutes.",
)
async def get_summary(
    service: AIInsightsService = Depends(get_ai_service),
) -> AISummaryDTO:
    """Return AI-generated executive summary from feedback analytics."""
    return await service.get_executive_summary()


@router.get(
    "/recommendations",
    response_model=List[AIInsightDTO],
    summary="Get Prioritized Risk Alerts",
    description="AI risk alerts derived from negative MongoDB feedback records. Cached 10 minutes.",
)
async def get_recommendations(
    service: AIInsightsService = Depends(get_ai_service),
) -> List[AIInsightDTO]:
    """Return prioritized AI risk recommendations from negative feedback."""
    return await service.get_risk_recommendations()
