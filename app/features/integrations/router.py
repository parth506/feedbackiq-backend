from typing import List
from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter(prefix="/v1/integrations", tags=["16. Webhooks & Integrations"])

class IntegrationDTO(BaseModel):
    name: str = Field(default="Slack Alert Webhook")
    status: str = Field(default="connected")

@router.get("", response_model=List[IntegrationDTO], summary="List Active Webhook Integrations")
async def list_integrations() -> List[IntegrationDTO]:
    """List active third-party webhook integrations (Slack, Teams, Jira)."""
    return [IntegrationDTO()]
