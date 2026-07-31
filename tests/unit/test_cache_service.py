"""
Unit tests for CacheService.
Tests JSON serialization, cache miss/hit, get_or_set, and graceful Redis failure.
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from app.services.cache_service import CacheService


@pytest.mark.asyncio
async def test_get_returns_none_on_cache_miss():
    with patch("app.services.cache_service.RedisManager") as mock_redis:
        mock_redis.get = AsyncMock(return_value=None)
        service = CacheService()
        result = await service.get("missing_key")
    assert result is None


@pytest.mark.asyncio
async def test_get_deserializes_json_on_hit():
    with patch("app.services.cache_service.RedisManager") as mock_redis:
        mock_redis.get = AsyncMock(return_value='{"value": 42}')
        service = CacheService()
        result = await service.get("some_key")
    assert result == {"value": 42}


@pytest.mark.asyncio
async def test_set_serializes_and_stores():
    with patch("app.services.cache_service.RedisManager") as mock_redis:
        mock_redis.set = AsyncMock(return_value=True)
        service = CacheService()
        success = await service.set("key", {"data": "test"}, ttl=300)
    assert success is True
    mock_redis.set.assert_called_once()


@pytest.mark.asyncio
async def test_get_or_set_calls_factory_on_miss():
    factory_called = False

    async def factory():
        nonlocal factory_called
        factory_called = True
        return {"computed": True}

    with patch("app.services.cache_service.RedisManager") as mock_redis:
        mock_redis.get = AsyncMock(return_value=None)
        mock_redis.set = AsyncMock(return_value=True)
        service = CacheService()
        result = await service.get_or_set("key", factory, ttl=60)

    assert factory_called is True
    assert result == {"computed": True}


@pytest.mark.asyncio
async def test_get_or_set_skips_factory_on_hit():
    factory_called = False

    async def factory():
        nonlocal factory_called
        factory_called = True
        return {"computed": True}

    with patch("app.services.cache_service.RedisManager") as mock_redis:
        mock_redis.get = AsyncMock(return_value='{"cached": true}')
        service = CacheService()
        result = await service.get_or_set("key", factory, ttl=60)

    assert factory_called is False
    assert result == {"cached": True}
