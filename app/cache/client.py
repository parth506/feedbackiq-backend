"""
Redis client management using the redis-py async client.
"""
import logging
from typing import Any, Optional

import redis.asyncio as aioredis

from app.config.settings import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()


class RedisManager:
    """Redis Connection and Commands Manager with graceful error fallback."""
    _redis: Optional[aioredis.Redis] = None

    @classmethod
    async def connect(cls) -> None:
        """Initialize async Redis client and verify connectivity."""
        if cls._redis is None:
            try:
                if settings.REDIS_URL:
                    url = settings.REDIS_URL.strip()
                    if not (url.startswith("redis://") or url.startswith("rediss://") or url.startswith("unix://")):
                        url = f"redis://{url}"
                    logger.info("Connecting to Redis via REDIS_URL...")
                    cls._redis = aioredis.from_url(
                        url,
                        decode_responses=True,
                        socket_connect_timeout=5,
                    )
                elif settings.REDIS_HOST and settings.REDIS_PORT:
                    logger.info(
                        "Connecting to Redis at %s:%s ...", settings.REDIS_HOST, settings.REDIS_PORT
                    )
                    cls._redis = aioredis.Redis(
                        host=settings.REDIS_HOST,
                        port=settings.REDIS_PORT,
                        db=settings.REDIS_DB,
                        password=settings.REDIS_PASSWORD or None,
                        decode_responses=True,
                        socket_connect_timeout=5,
                    )
                else:
                    logger.info("Redis not configured. Running without cache.")
                    return

                await cls._redis.ping()
                logger.info("Redis connected successfully.")
            except Exception as exc:
                logger.warning("Redis connection failed: %s. Cache will be disabled.", exc)
                cls._redis = None

    @classmethod
    async def disconnect(cls) -> None:
        """Close Redis client."""
        if cls._redis is not None:
            try:
                await cls._redis.aclose()
            except Exception as exc:
                logger.warning("Error closing Redis client: %s", exc)
            cls._redis = None
            logger.info("Redis disconnected.")

    @classmethod
    def get_client(cls) -> Optional[aioredis.Redis]:
        """Return the active Redis client instance or None if unavailable."""
        return cls._redis

    @classmethod
    async def get(cls, key: str) -> Optional[Any]:
        """Get the value of a key. Returns None if Redis is unavailable or key not found."""
        if cls._redis is None:
            return None
        try:
            return await cls._redis.get(key)
        except Exception as exc:
            logger.warning("Redis get error for key '%s': %s", key, exc)
            return None

    @classmethod
    async def set(cls, key: str, value: Any, ex: Optional[int] = None) -> bool:
        """Set string value of a key with optional expiration. Returns False if Redis fails."""
        if cls._redis is None:
            return False
        try:
            return await cls._redis.set(key, value, ex=ex)
        except Exception as exc:
            logger.warning("Redis set error for key '%s': %s", key, exc)
            return False

    @classmethod
    async def delete(cls, *keys: str) -> int:
        """Delete one or more keys. Returns count deleted or 0 if Redis fails."""
        if cls._redis is None or not keys:
            return 0
        try:
            return await cls._redis.delete(*keys)
        except Exception as exc:
            logger.warning("Redis delete error for keys '%s': %s", keys, exc)
            return 0

    @classmethod
    async def exists(cls, *keys: str) -> int:
        """Check if one or more keys exist. Returns count or 0 if Redis fails."""
        if cls._redis is None or not keys:
            return 0
        try:
            return await cls._redis.exists(*keys)
        except Exception as exc:
            logger.warning("Redis exists error for keys '%s': %s", keys, exc)
            return 0


async def connect_redis() -> None:
    await RedisManager.connect()


async def disconnect_redis() -> None:
    await RedisManager.disconnect()


def get_redis() -> Optional[aioredis.Redis]:
    return RedisManager.get_client()
