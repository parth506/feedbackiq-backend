from typing import List
from fastapi import APIRouter
from app.database.session import get_database
from app.features.sentiment.schemas import EmotionScoreDTO, SentimentEvolutionDTO

router = APIRouter(prefix="/v1/sentiment", tags=["4. Sentiment Intelligence"])

@router.get("/emotions", response_model=List[EmotionScoreDTO], summary="Get Emotion Radar Scores from MongoDB")
async def get_emotions() -> List[EmotionScoreDTO]:
    """Retrieve emotion breakdown computed from real MongoDB feedback collection."""
    db = get_database()
    collection = db["feedback"]

    total = await collection.count_documents({})
    if total == 0:
        return [
            EmotionScoreDTO(emotion="Joy", score=0.0, percentage=0.0, color="#10b981"),
            EmotionScoreDTO(emotion="Trust", score=0.0, percentage=0.0, color="#3b82f6"),
            EmotionScoreDTO(emotion="Surprise", score=0.0, percentage=0.0, color="#8b5cf6"),
            EmotionScoreDTO(emotion="Frustration", score=0.0, percentage=0.0, color="#f59e0b"),
            EmotionScoreDTO(emotion="Anger", score=0.0, percentage=0.0, color="#ef4444"),
        ]

    pos = await collection.count_documents({"sentiment": "positive"})
    neu = await collection.count_documents({"sentiment": "neutral"})
    neg = await collection.count_documents({"sentiment": "negative"})

    pos_pct = round((pos / total) * 100, 1)
    neu_pct = round((neu / total) * 100, 1)
    neg_pct = round((neg / total) * 100, 1)

    return [
        EmotionScoreDTO(emotion="Joy", score=pos_pct, percentage=pos_pct, color="#10b981"),
        EmotionScoreDTO(emotion="Trust", score=round(pos_pct * 0.5, 1), percentage=round(pos_pct * 0.5, 1), color="#3b82f6"),
        EmotionScoreDTO(emotion="Surprise", score=neu_pct, percentage=neu_pct, color="#8b5cf6"),
        EmotionScoreDTO(emotion="Frustration", score=round(neg_pct * 0.7, 1), percentage=round(neg_pct * 0.7, 1), color="#f59e0b"),
        EmotionScoreDTO(emotion="Anger", score=round(neg_pct * 0.3, 1), percentage=round(neg_pct * 0.3, 1), color="#ef4444"),
    ]

@router.get("/evolution", response_model=List[SentimentEvolutionDTO], summary="Get Sentiment Evolution Timeline from MongoDB")
async def get_evolution() -> List[SentimentEvolutionDTO]:
    """Retrieve historical sentiment evolution trend computed from MongoDB documents."""
    db = get_database()
    collection = db["feedback"]

    pipeline = [
        {
            "$group": {
                "_id": {
                    "$dateToString": {
                        "format": "%Y-%m-%d",
                        "date": "$created_at"
                    }
                },
                "total": {"$sum": 1},
                "positive": {
                    "$sum": {"$cond": [{"$eq": [{"$toLower": "$sentiment"}, "positive"]}, 1, 0]}
                },
            }
        },
        {"$sort": {"_id": 1}},
    ]

    cursor = collection.aggregate(pipeline)
    docs = await cursor.to_list(length=100)

    result: List[SentimentEvolutionDTO] = []
    for d in docs:
        tot = d.get("total", 1)
        pos = d.get("positive", 0)
        ratio = round(pos / tot, 2) if tot > 0 else 0.0
        result.append(
            SentimentEvolutionDTO(
                date=d.get("_id") or "Today",
                sentimentIndex=round((ratio * 2) - 1, 2), # Normalized -1.0 to +1.0 index
                positiveRatio=ratio,
            )
        )
    return result
