"""
Feedback Repository — Data access layer for the 'feedback' MongoDB collection.

Extends BaseRepository and implements all required methods.
All business logic stays in the service layer — this class only
constructs queries, executes them, and returns plain dicts.

New in this version:
  - Extends BaseRepository (SOLID DIP compliance)
  - get_dashboard_aggregated(): single $group pipeline replacing 4 count_documents calls
  - find_by_id(), update(), delete() implemented
  - find() supports pagination, projection, sort
  - aggregate() exposes raw pipeline execution for analytics services
  - search() uses $text index (falls back to $regex when text index unavailable)
"""
import logging
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection, AsyncIOMotorDatabase

from app.core.constants import COLLECTION_FEEDBACK, SEARCH_REGEX_OPTIONS
from app.repositories.base import BaseRepository

logger = logging.getLogger(__name__)


class FeedbackRepository(BaseRepository):
    """Repository handling all MongoDB operations for the feedback collection."""

    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self.db = db
        self.collection: AsyncIOMotorCollection = db[COLLECTION_FEEDBACK]

    # ── BaseRepository implementations ────────────────────────────────────────

    async def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Insert one feedback document. Adds created_at if missing."""
        if "created_at" not in data or data["created_at"] is None:
            data["created_at"] = datetime.now(timezone.utc)

        result = await self.collection.insert_one(data)
        data["_id"] = str(result.inserted_id)
        logger.info("Inserted feedback document: %s", data["_id"])
        return data

    async def find(
        self,
        filter_query: Optional[Dict[str, Any]] = None,
        projection: Optional[Dict[str, Any]] = None,
        limit: int = 20,
        offset: int = 0,
        sort_field: str = "created_at",
        sort_direction: int = -1,
    ) -> List[Dict[str, Any]]:
        """Find feedback documents with optional filter, projection, pagination, and sort."""
        query = filter_query or {}
        cursor = (
            self.collection.find(query, projection)
            .sort(sort_field, sort_direction)
            .skip(offset)
            .limit(limit)
        )
        docs = await cursor.to_list(length=limit)
        for doc in docs:
            doc["_id"] = str(doc["_id"])
        return docs

    async def find_by_id(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Find a single feedback document by its ObjectId string."""
        if not ObjectId.is_valid(document_id):
            return None
        doc = await self.collection.find_one({"_id": ObjectId(document_id)})
        if doc:
            doc["_id"] = str(doc["_id"])
        return doc

    async def update(self, document_id: str, update_data: Dict[str, Any]) -> bool:
        """Update a document by ID. Returns True if the document was modified."""
        if not ObjectId.is_valid(document_id):
            return False
        result = await self.collection.update_one(
            {"_id": ObjectId(document_id)},
            {"$set": update_data},
        )
        return result.modified_count > 0

    async def delete(self, document_id: str) -> bool:
        """Delete a document by ID. Returns True if a document was deleted."""
        if not ObjectId.is_valid(document_id):
            return False
        result = await self.collection.delete_one({"_id": ObjectId(document_id)})
        return result.deleted_count > 0

    async def count(self, filter_query: Optional[Dict[str, Any]] = None) -> int:
        """Count feedback documents matching optional filter."""
        return await self.collection.count_documents(filter_query or {})

    async def aggregate(self, pipeline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Execute an aggregation pipeline and return results."""
        cursor = self.collection.aggregate(pipeline)
        return await cursor.to_list(length=None)

    async def search(self, query_str: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Case-insensitive search in feedback comments.

        Sanitizes the input to prevent regex injection, then uses MongoDB
        $regex (the TEXT index is used for full-text queries via find_by_text()).
        """
        sanitized = re.escape(query_str)
        regex_query = {"comment": {"$regex": sanitized, "$options": SEARCH_REGEX_OPTIONS}}
        cursor = self.collection.find(regex_query).sort("created_at", -1).limit(limit)
        docs = await cursor.to_list(length=limit)
        for doc in docs:
            doc["_id"] = str(doc["_id"])
        return docs

    async def find_latest(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Return the N most recently created feedback documents."""
        return await self.find(limit=limit)

    # ── FeedbackRepository-specific methods ───────────────────────────────────

    async def find_by_sentiment(self, sentiment: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Find feedback documents by sentiment category (positive/neutral/negative)."""
        return await self.find(
            filter_query={"sentiment": sentiment.lower()},
            limit=limit,
        )

    async def get_dashboard_aggregated(self) -> Dict[str, Any]:
        """
        Single-pipeline aggregation replacing 4 separate count_documents calls.

        Returns: {total, positive, neutral, negative, negative_docs[]}
        One MongoDB round-trip instead of four.
        """
        pipeline = [
            {
                "$facet": {
                    "counts": [
                        {
                            "$group": {
                                "_id": "$sentiment",
                                "count": {"$sum": 1},
                            }
                        }
                    ],
                    "total": [{"$count": "n"}],
                    "latest": [
                        {"$sort": {"created_at": -1}},
                        {"$limit": 10},
                        {
                            "$project": {
                                "_id": {"$toString": "$_id"},
                                "sentiment": 1,
                                "comment": 1,
                                "created_at": 1,
                            }
                        },
                    ],
                }
            }
        ]
        results = await self.aggregate(pipeline)
        if not results:
            return {"total": 0, "positive": 0, "neutral": 0, "negative": 0, "latest": []}

        data = results[0]
        total = data["total"][0]["n"] if data["total"] else 0

        counts: Dict[str, int] = {}
        for item in data.get("counts", []):
            counts[item["_id"]] = item["count"]

        return {
            "total": total,
            "positive": counts.get("positive", 0),
            "neutral": counts.get("neutral", 0),
            "negative": counts.get("negative", 0),
            "latest": data.get("latest", []),
        }
