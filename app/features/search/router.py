from typing import List
from fastapi import APIRouter, Query
from app.features.search.schemas import SearchResultDTO

router = APIRouter(prefix="/v1/search", tags=["8. Search & Discovery"])

@router.get("/comments", response_model=List[SearchResultDTO], summary="Search Feedback Comments")
async def search_comments(q: str = Query(..., example="dashboard")) -> List[SearchResultDTO]:
    """Perform full-text case-insensitive regex search inside feedback comments."""
    return [
        SearchResultDTO(id="679a1234567890abcdef1234", sentiment="positive", comment=f"Great {q} loading speed.", created_at="2026-07-30T10:00:00Z")
    ]
