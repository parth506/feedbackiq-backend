"""
Unit tests for FeedbackService.
All MongoDB and Redis dependencies are mocked.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timezone

from app.services.feedback import FeedbackService
from app.schemas.feedback import CreateFeedbackRequest, SentimentEnum


@pytest.mark.asyncio
async def test_create_feedback_returns_success(mock_repository, mock_cache):
    service = FeedbackService(repository=mock_repository, cache=mock_cache)
    request = CreateFeedbackRequest(sentiment=SentimentEnum.POSITIVE, comment="Excellent UX!")
    result = await service.create_feedback(request)

    assert result.success is True
    assert "successfully" in result.message
    mock_repository.create.assert_called_once()
    mock_cache.delete.assert_called_once()


@pytest.mark.asyncio
async def test_create_feedback_strips_comment_whitespace(mock_repository, mock_cache):
    service = FeedbackService(repository=mock_repository, cache=mock_cache)
    request = CreateFeedbackRequest(sentiment=SentimentEnum.NEGATIVE, comment="  bad UX  ")
    await service.create_feedback(request)

    call_args = mock_repository.create.call_args[0][0]
    assert call_args["comment"] == "bad UX"


@pytest.mark.asyncio
async def test_dashboard_stats_uses_cache_miss_then_computes(mock_repository, mock_cache):
    """When cache misses, dashboard_stats should call get_dashboard_aggregated."""
    service = FeedbackService(repository=mock_repository, cache=mock_cache)
    result = await service.dashboard_stats()

    assert result.total_feedback == 10
    assert result.positive == 7
    assert result.neutral == 2
    assert result.negative == 1
    mock_repository.get_dashboard_aggregated.assert_called_once()


@pytest.mark.asyncio
async def test_search_feedback_returns_results(mock_repository, mock_cache):
    service = FeedbackService(repository=mock_repository, cache=mock_cache)
    results = await service.search_feedback("Great")

    assert len(results) == 1
    assert results[0].sentiment == "positive"
    mock_repository.search.assert_called_once_with("Great", limit=20)


@pytest.mark.asyncio
async def test_search_feedback_empty_query_returns_latest(mock_repository, mock_cache):
    service = FeedbackService(repository=mock_repository, cache=mock_cache)
    results = await service.search_feedback("")

    mock_repository.find_latest.assert_called_once()
    mock_repository.search.assert_not_called()
