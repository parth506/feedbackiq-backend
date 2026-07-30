"""
Models package — MongoDB document models.
"""
from datetime import datetime, timezone
from typing import Optional, Annotated

from bson import ObjectId
from pydantic import BaseModel, Field, BeforeValidator


# Custom type for MongoDB ObjectId
def validate_object_id(v) -> ObjectId:
    if isinstance(v, ObjectId):
        return v
    if isinstance(v, str) and ObjectId.is_valid(v):
        return ObjectId(v)
    raise ValueError(f"Invalid ObjectId: {v}")


PyObjectId = Annotated[ObjectId, BeforeValidator(validate_object_id)]


class BaseDocument(BaseModel):
    """Base Pydantic model for MongoDB documents."""

    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str},
    }


from app.models.feedback import FeedbackModel, SentimentType

__all__ = ["PyObjectId", "BaseDocument", "FeedbackModel", "SentimentType"]
