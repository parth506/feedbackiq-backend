"""
Database dependency provider.
Wraps get_database() as a FastAPI Depends-compatible function.
"""
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.database.session import get_database


def get_db() -> Optional[AsyncIOMotorDatabase]:
    """Provide the active Motor database instance."""
    return get_database()
