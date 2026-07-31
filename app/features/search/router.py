"""
Search Router — Thin delegate. All logic in SearchService.
Supports pagination via limit + offset query parameters.
"""
from typing import List
from fastapi import APIRouter, Depends, Query

from app.dependencies.feedback import get_search_service
from app.features.search.schemas import SearchResultDTO
from app.services.search_service import SearchService
from app.core.constants import DEFAULT_PAGE_SIZE, MAX_SEARCH_RESULTS

router = APIRouter(prefix="/v1/search", tags=["8. Search & Discovery"])


@router.get(
    "/comments",
    response_model=List[SearchResultDTO],
    summary="Search Feedback Comments",
    description="Case-insensitive keyword search in MongoDB feedback comments with pagination.",
)
async def search_comments(
    q: str = Query(..., min_length=1, max_length=200, description="Search keyword"),
    limit: int = Query(default=DEFAULT_PAGE_SIZE, ge=1, le=MAX_SEARCH_RESULTS, description="Results per page"),
    offset: int = Query(default=0, ge=0, description="Number of results to skip"),
    service: SearchService = Depends(get_search_service),
) -> List[SearchResultDTO]:
    """Search feedback comments by keyword with optional pagination."""
    return await service.search_comments(query=q, limit=limit, offset=offset)
