"""
Unit tests for SearchService.
Tests input validation and delegation to repository.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock

from app.services.search_service import SearchService
from app.exceptions.exceptions import SearchException
from app.repositories.feedback import FeedbackRepository


def make_service(docs=None):
    repo = MagicMock(spec=FeedbackRepository)
    repo.search = AsyncMock(return_value=docs or [
        {"_id": "abc", "sentiment": "positive", "comment": "Great", "created_at": None}
    ])
    return SearchService(repository=repo)


@pytest.mark.asyncio
async def test_search_returns_results():
    service = make_service()
    results = await service.search_comments("great")
    assert len(results) == 1
    assert results[0].sentiment == "positive"


@pytest.mark.asyncio
async def test_search_empty_query_raises():
    service = make_service()
    with pytest.raises(SearchException):
        await service.search_comments("   ")


@pytest.mark.asyncio
async def test_search_long_query_raises():
    service = make_service()
    with pytest.raises(SearchException):
        await service.search_comments("x" * 201)


@pytest.mark.asyncio
async def test_search_caps_limit_at_max():
    repo = MagicMock(spec=FeedbackRepository)
    repo.search = AsyncMock(return_value=[])
    service = SearchService(repository=repo)
    await service.search_comments("test", limit=9999)
    # Actual limit passed should be capped at MAX_SEARCH_RESULTS
    call_limit = repo.search.call_args[1]["limit"] if repo.search.call_args[1] else repo.search.call_args[0][1]
    assert call_limit <= 50
