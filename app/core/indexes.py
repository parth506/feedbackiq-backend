"""
MongoDB Index Management.

Defines and ensures all required indexes exist on startup.
Calling ensure_indexes() is idempotent — safe to run on every boot.

Index strategy:
  feedback.created_at DESC  → powers all "latest N" and time-series queries
  feedback.sentiment        → powers count_documents({sentiment: ...}) filters
  feedback.comment TEXT     → powers $text full-text search (replaces regex scan)

To add indexes for a new collection, create a new async function following the
same pattern and add a call in ensure_indexes().
"""
import logging
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ASCENDING, DESCENDING, TEXT, IndexModel

logger = logging.getLogger(__name__)


async def _ensure_feedback_indexes(db: AsyncIOMotorDatabase) -> None:
    """Create indexes on the 'feedback' collection if they do not already exist."""
    collection = db["feedback"]

    indexes = [
        # Supports: find_latest(), time-series aggregations, SSE/WS latest feed
        IndexModel([("created_at", DESCENDING)], name="idx_feedback_created_at_desc"),

        # Supports: count_documents({"sentiment": ...}) → used in dashboard, analytics, sentiment
        IndexModel([("sentiment", ASCENDING)], name="idx_feedback_sentiment"),

        # Compound: sentiment + created_at → powers dashboard aggregation pipeline efficiently
        IndexModel(
            [("sentiment", ASCENDING), ("created_at", DESCENDING)],
            name="idx_feedback_sentiment_created_at",
        ),

        # Full-text index: supports $text search as a faster alternative to $regex
        # Note: only one text index allowed per collection
        IndexModel([("comment", TEXT)], name="idx_feedback_comment_text"),
    ]

    try:
        result = await collection.create_indexes(indexes)
        logger.info("Feedback indexes ensured: %s", result)
    except Exception as exc:
        # Non-fatal: indexes failing to create degrade performance but not correctness.
        logger.warning("Could not create feedback indexes: %s", exc)


async def ensure_indexes(db: AsyncIOMotorDatabase) -> None:
    """
    Entry point called during application lifespan startup.
    Add calls here for each new collection that needs indexes.
    """
    logger.info("Ensuring MongoDB indexes...")
    await _ensure_feedback_indexes(db)
    logger.info("MongoDB indexes ready.")
