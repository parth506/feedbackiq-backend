from typing import List
from fastapi import APIRouter
from app.database.session import get_database
from app.features.ai_insights.schemas import AIInsightDTO, AISummaryDTO

router = APIRouter(prefix="/v1/ai-insights", tags=["6. AI Executive Insights"])

@router.get("/summary", response_model=AISummaryDTO, summary="Get Dynamic AI Executive Summary from MongoDB")
async def get_summary() -> AISummaryDTO:
    """Retrieve natural language executive summary computed from live MongoDB feedback records."""
    db = get_database()
    if db is None:
        return AISummaryDTO(
            headline="Database Initializing...",
            summary="Awaiting live customer feedback entries in MongoDB Atlas cluster.",
            keyOpportunities=[],
            riskCount=0,
        )

    try:
        collection = db["feedback"]
        total = await collection.count_documents({})
        pos = await collection.count_documents({"sentiment": "positive"})
        neg = await collection.count_documents({"sentiment": "negative"})

        pos_pct = round((pos / total) * 100, 1) if total > 0 else 0.0
        sentiment_index = round(((pos - neg) / total), 2) if total > 0 else 0.0

        headline = f"Feedback Sentiment Index: {sentiment_index:+.2f} ({pos_pct}% Positive)"
        summary_text = (
            f"Database analytics over {total} feedback records indicate {pos_pct}% positive sentiment. "
            f"Total positive: {pos}, total negative: {neg}."
        )

        return AISummaryDTO(
            headline=headline,
            summary=summary_text,
            keyOpportunities=["Improve user onboarding flow", "Monitor checkout payment friction"],
            riskCount=neg,
        )
    except Exception:
        return AISummaryDTO(
            headline="Database Initializing...",
            summary="Awaiting live customer feedback entries in MongoDB Atlas cluster.",
            keyOpportunities=[],
            riskCount=0,
        )

@router.get("/recommendations", response_model=List[AIInsightDTO], summary="Get Prioritized Risk Alerts from MongoDB")
async def get_recommendations() -> List[AIInsightDTO]:
    """Retrieve AI risk alerts derived from negative MongoDB feedback comments."""
    db = get_database()
    if db is None:
        return []

    try:
        collection = db["feedback"]
        neg_docs = await collection.find({"sentiment": "negative"}).sort("created_at", -1).limit(5).to_list(length=5)

        insights: List[AIInsightDTO] = []
        for idx, doc in enumerate(neg_docs):
            comment = doc.get("comment", "Negative feedback reported.")
            insights.append(
                AIInsightDTO(
                    id=f"neg-{idx+1}",
                    title=f"Critical Issue #{idx+1}: {comment[:30]}...",
                    category="root_cause",
                    severity="critical" if idx == 0 else "warning",
                    description=f"Negative feedback comment recorded in MongoDB: '{comment}'",
                    impactScore=max(50, 95 - (idx * 10)),
                    suggestedAction="Investigate logs and contact customer account.",
                    affectedUsersCount=1,
                    timestamp="Recent",
                )
            )

        if not insights:
            insights.append(
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
                )
            )

        return insights
    except Exception:
        return []
