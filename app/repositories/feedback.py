"""
Feedback Repository — Data access layer for MongoDB feedback collection.
"""
from datetime import datetime, timezone
import logging
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection

logger = logging.getLogger(__name__)


class FeedbackRepository:
    """Repository handling all MongoDB operations for the feedback collection."""

    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self.db = db
        self.collection: AsyncIOMotorCollection = db["feedback"]

    async def create(self, feedback_data: dict) -> dict:
        """Create a new feedback document in MongoDB."""
        if "created_at" not in feedback_data or feedback_data["created_at"] is None:
            feedback_data["created_at"] = datetime.now(timezone.utc)
        
        result = await self.collection.insert_one(feedback_data)
        feedback_data["_id"] = str(result.inserted_id)
        logger.info("Inserted feedback document with ID: %s", feedback_data["_id"])
        return feedback_data

    async def count(self, filter_query: Optional[dict] = None) -> int:
        """Count total feedback documents matching optional filter query."""
        query = filter_query or {}
        return await self.collection.count_documents(query)

    async def find_latest(self, limit: int = 10) -> List[dict]:
        """Find the latest N feedback documents sorted by created_at descending."""
        cursor = self.collection.find().sort("created_at", -1).limit(limit)
        docs = await cursor.to_list(length=limit)
        for doc in docs:
            doc["_id"] = str(doc["_id"])
        return docs

    async def find_by_sentiment(self, sentiment: str) -> List[dict]:
        """Find feedback documents by sentiment category."""
        cursor = self.collection.find({"sentiment": sentiment.lower()}).sort("created_at", -1)
        docs = await cursor.to_list(length=100)
        for doc in docs:
            doc["_id"] = str(doc["_id"])
        return docs

    async def search(self, query_str: str) -> List[dict]:
        """Search feedback comments using case-insensitive regex matching."""
        regex_query = {"comment": {"$regex": query_str, "$options": "i"}}
        cursor = self.collection.find(regex_query).sort("created_at", -1)
        docs = await cursor.to_list(length=100)
        for doc in docs:
            doc["_id"] = str(doc["_id"])
        return docs
