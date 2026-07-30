"""
MongoDB session management using Motor (async driver).
"""
import logging
from typing import Optional
import certifi

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.config.settings import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()


class DatabaseManager:
    """Singleton connection pool manager for MongoDB."""
    _client: Optional[AsyncIOMotorClient] = None
    _database: Optional[AsyncIOMotorDatabase] = None

    @classmethod
    async def connect(cls) -> None:
        """Initialize Motor client with connection pooling and verify connectivity."""
        if cls._client is None:
            logger.info("Connecting to MongoDB...")
            client_kwargs = {
                "maxPoolSize": settings.MONGO_MAX_POOL_SIZE,
                "minPoolSize": settings.MONGO_MIN_POOL_SIZE,
            }
            # Use certifi CA certificates for SSL/TLS connections (e.g. MongoDB Atlas)
            if (
                "mongodb+srv://" in settings.MONGO_URI
                or "tls=true" in settings.MONGO_URI.lower()
                or "ssl=true" in settings.MONGO_URI.lower()
            ):
                client_kwargs["tlsCAFile"] = certifi.where()

            cls._client = AsyncIOMotorClient(
                settings.MONGO_URI,
                **client_kwargs
            )
            cls._database = cls._client[settings.db_name]
            # Verify connectivity via ping
            await cls._client.admin.command("ping")
            logger.info(
                "MongoDB connected — database: %s (Pool: min=%d, max=%d)",
                settings.db_name,
                settings.MONGO_MIN_POOL_SIZE,
                settings.MONGO_MAX_POOL_SIZE
            )

    @classmethod
    async def disconnect(cls) -> None:
        """Close Motor client pool."""
        if cls._client is not None:
            cls._client.close()
            cls._client = None
            cls._database = None
            logger.info("MongoDB disconnected.")

    @classmethod
    def get_db(cls) -> AsyncIOMotorDatabase:
        """Return the active database instance."""
        if cls._database is None:
            raise RuntimeError("Database is not initialized. Call DatabaseManager.connect() first.")
        return cls._database


async def connect_db() -> None:
    await DatabaseManager.connect()


async def disconnect_db() -> None:
    await DatabaseManager.disconnect()


def get_database() -> AsyncIOMotorDatabase:
    return DatabaseManager.get_db()
