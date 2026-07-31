from typing import List
from fastapi import APIRouter, Query
from app.database.session import get_database
from app.features.search.schemas import SearchResultDTO

router = APIRouter(prefix="/v1/search", tags=["8. Search & Discovery"])

@router.get("/comments", response_model=List[SearchResultDTO], summary="Search Feedback Comments in MongoDB")
async def search_comments(q: str = Query(..., description="Query string to search in MongoDB comments", examples=["dashboard"])) -> List[SearchResultDTO]:
    """Perform case-insensitive regex search directly against MongoDB feedback comments."""
    db = get_database()
    collection = db["feedback"]

    regex_query = {"comment": {"$regex": q, "$options": "i"}}
    cursor = collection.find(regex_query).sort("created_at", -1).limit(50)
    docs = await cursor.to_list(length=50)

    return [
        SearchResultDTO(
            id=str(doc["_id"]),
            sentiment=doc.get("sentiment", "positive"),
            comment=doc.get("comment", ""),
            created_at=doc.get("created_at").isoformat() if doc.get("created_at") else ""
        )
        for doc in docs
    ]
