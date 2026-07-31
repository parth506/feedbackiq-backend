"""
Cache Service — Abstraction layer over RedisManager.

Responsibilities:
  - Read, write, delete cache entries
  - TTL management
  - Cache-aside pattern via get_or_set()
  - Namespaced key construction
  - Graceful degradation when Redis is unavailable

Design decisions:
  - Services NEVER call RedisManager directly — they inject CacheService.
  - All failures are logged at WARNING and return None/False (non-fatal).
  - get_or_set() implements the cache-aside pattern to reduce boilerplate in services.
  - JSON serialization/deserialization is handled here, not in services.
"""
import json
import logging
from typing import Any, Callable, Coroutine, Optional, TypeVar

from app.cache.client import RedisManager

logger = logging.getLogger(__name__)

T = TypeVar("T")


class CacheService:
    """
    High-level cache service wrapping RedisManager.
    Injected into services via FastAPI Depends — never instantiated manually.
    """

    async def get(self, key: str) -> Optional[Any]:
        """
        Retrieve and JSON-deserialize a cached value.
        Returns None if the key is missing or Redis is unavailable.
        """
        raw = await RedisManager.get(key)
        if raw is None:
            logger.debug("Cache MISS: %s", key)
            return None
        try:
            value = json.loads(raw)
            logger.debug("Cache HIT: %s", key)
            return value
        except (json.JSONDecodeError, TypeError) as exc:
            logger.warning("Cache deserialization error for key '%s': %s", key, exc)
            return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        JSON-serialize and store a value in Redis with optional TTL (seconds).
        Returns False if Redis is unavailable or serialization fails.
        """
        try:
            serialized = json.dumps(value, default=str)
        except (TypeError, ValueError) as exc:
            logger.warning("Cache serialization error for key '%s': %s", key, exc)
            return False

        success = await RedisManager.set(key, serialized, ex=ttl)
        if success:
            logger.debug("Cache SET: %s (TTL=%s)", key, ttl)
        return bool(success)

    async def delete(self, *keys: str) -> int:
        """Delete one or more cache keys. Returns count of deleted keys."""
        if not keys:
            return 0
        deleted = await RedisManager.delete(*keys)
        logger.debug("Cache DELETE: %s (deleted=%d)", keys, deleted)
        return deleted

    async def get_or_set(
        self,
        key: str,
        factory: Callable[[], Coroutine[Any, Any, T]],
        ttl: Optional[int] = None,
    ) -> T:
        """
        Cache-aside pattern:
          1. Try to return a cached value.
          2. On cache miss, call factory() to compute the value.
          3. Store the result in cache with TTL.
          4. Return the computed value.

        The factory must be an async callable returning a JSON-serializable object.
        If Redis is unavailable, factory() is called on every invocation (graceful degradation).
        """
        cached = await self.get(key)
        if cached is not None:
            return cached  # type: ignore[return-value]

        value = await factory()

        # Attempt to cache — failure is non-fatal
        if value is not None:
            await self.set(key, value, ttl=ttl)

        return value

    async def invalidate_pattern(self, pattern: str) -> None:
        """
        Delete all keys matching a glob pattern.
        WARNING: Uses SCAN — safe for production but avoid on very large keyspaces.
        """
        redis = RedisManager.get_client()
        if redis is None:
            return
        try:
            async for key in redis.scan_iter(match=pattern):
                await redis.delete(key)
            logger.info("Cache invalidated pattern: %s", pattern)
        except Exception as exc:
            logger.warning("Cache pattern invalidation failed for '%s': %s", pattern, exc)
