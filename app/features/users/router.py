from typing import List
from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter(prefix="/v1/users", tags=["10. Users Management"])

class UserProfileDTO(BaseModel):
    id: str = Field(default="user_admin_101")
    name: str = Field(default="Parth Architect")
    email: str = Field(default="admin@feedbackiq.ai")
    role: str = Field(default="admin")

@router.get("", response_model=List[UserProfileDTO], summary="List Enterprise Team Members")
async def list_users() -> List[UserProfileDTO]:
    """List team members and user roles."""
    return [UserProfileDTO()]
