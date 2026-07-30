"""
FastAPI dependency providers for Repositories and Services.
"""
from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.database.session import get_database
from app.repositories.feedback import FeedbackRepository
from app.services.feedback import FeedbackService


def get_feedback_repository(
    db: AsyncIOMotorDatabase = Depends(get_database)
) -> FeedbackRepository:
    """Provide a FeedbackRepository instance initialized with active MongoDB database."""
    return FeedbackRepository(db=db)


def get_feedback_service(
    repository: FeedbackRepository = Depends(get_feedback_repository)
) -> FeedbackService:
    """Provide a FeedbackService instance initialized with FeedbackRepository."""
    return FeedbackService(repository=repository)
