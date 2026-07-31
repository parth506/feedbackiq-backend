from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter(prefix="/v1/organizations", tags=["11. Organizations"])

class OrgDTO(BaseModel):
    id: str = Field(default="org_global_01")
    name: str = Field(default="FeedbackIQ Enterprise Global")
    tier: str = Field(default="Enterprise AI Tier")

@router.get("/current", response_model=OrgDTO, summary="Get Organization Details")
async def get_current_org() -> OrgDTO:
    """Get active organization profile details."""
    return OrgDTO()
