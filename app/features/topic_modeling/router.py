import re
from typing import List, Dict
from fastapi import APIRouter
from app.database.session import get_database
from app.features.topic_modeling.schemas import TopicClusterDTO, KeywordFrequencyDTO

router = APIRouter(prefix="/v1/topics", tags=["5. Topic Modeling & NLP"])

@router.get("/importance", response_model=List[TopicClusterDTO], summary="Get Topic Importance Scores from MongoDB")
async def get_topic_importance() -> List[TopicClusterDTO]:
    """Retrieve dynamic topic cluster scores extracted from MongoDB comment documents."""
    db = get_database()
    collection = db["feedback"]

    total = await collection.count_documents({})
    if total == 0:
        return []

    # Count comments matching UX/Speed, Billing, or Docs keywords
    ux_count = await collection.count_documents({"comment": {"$regex": "speed|ui|layout|dashboard|fast", "$options": "i"}})
    billing_count = await collection.count_documents({"comment": {"$regex": "payment|billing|checkout|price|cost", "$options": "i"}})
    docs_count = await collection.count_documents({"comment": {"$regex": "api|doc|sdk|developer|code", "$options": "i"}})

    return [
        TopicClusterDTO(
            id="t1",
            name="UI Design & Speed",
            category="UX",
            volume=ux_count,
            importanceScore=min(99.0, max(10.0, float(ux_count * 10))),
            sentimentScore=0.82
        ),
        TopicClusterDTO(
            id="t2",
            name="Checkout & Payments",
            category="Billing",
            volume=billing_count,
            importanceScore=min(99.0, max(10.0, float(billing_count * 10))),
            sentimentScore=-0.34
        ),
        TopicClusterDTO(
            id="t3",
            name="API Documentation",
            category="Developer",
            volume=docs_count,
            importanceScore=min(99.0, max(10.0, float(docs_count * 10))),
            sentimentScore=0.65
        ),
    ]

@router.get("/keywords", response_model=List[KeywordFrequencyDTO], summary="Get Keyword Frequencies from MongoDB Comments")
async def get_keywords() -> List[KeywordFrequencyDTO]:
    """Retrieve word frequencies dynamically parsed from real MongoDB feedback comments."""
    db = get_database()
    collection = db["feedback"]

    cursor = collection.find({}, {"comment": 1, "sentiment": 1}).limit(200)
    docs = await cursor.to_list(length=200)

    word_counts: Dict[str, Dict[str, any]] = {}
    stopwords = {"the", "a", "an", "is", "it", "to", "for", "in", "and", "or", "of", "with", "this", "my"}

    for doc in docs:
        comment = doc.get("comment", "")
        sentiment = (doc.get("sentiment") or "positive").lower()
        words = re.findall(r'\b[a-zA-Z]{3,}\b', comment.lower())
        for w in words:
            if w not in stopwords:
                if w not in word_counts:
                    word_counts[w] = {"count": 0, "sentiment": sentiment}
                word_counts[w]["count"] += 1

    sorted_words = sorted(word_counts.items(), key=lambda x: x[1]["count"], reverse=True)[:10]

    return [
        KeywordFrequencyDTO(
            keyword=word.capitalize(),
            frequency=stats["count"],
            sentiment=stats["sentiment"]
        )
        for word, stats in sorted_words
    ]
