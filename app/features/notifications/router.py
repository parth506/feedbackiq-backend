from typing import List
from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter(prefix="/v1/notifications", tags=["13. Notifications"])

class NotificationDTO(BaseModel):
    id: str = Field(default="notif_101")
    title: str = Field(default="Checkout Friction Detected")
    read: bool = Field(default=False)

@router.get("", response_model=List[NotificationDTO], summary="List AI System Alerts & Notifications")
async def list_notifications() -> List[NotificationDTO]:
    """List system alert notifications."""
    return [NotificationDTO()]
