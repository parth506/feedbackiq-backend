from typing import List
from pydantic import BaseModel, Field

class AIInsightDTO(BaseModel):
    id: str = Field(..., example="ai-1")
    title: str = Field(..., example="Payment Checkout Friction Identified")
    category: str = Field(..., example="root_cause")
    severity: str = Field(..., example="warning")
    description: str = Field(..., example="14% drop in billing sentiment due to 3D Secure WebKit mobile timeout.")
    impactScore: int = Field(..., example=89)
    suggestedAction: str = Field(..., example="Deploy hotfix for WebKit iframe event listener.")
    affectedUsersCount: int = Field(..., example=1420)
    timestamp: str = Field(..., example="10 mins ago")

class AISummaryDTO(BaseModel):
    headline: str = Field(..., example="Strong positive overall sentiment (+0.68 Index)")
    summary: str = Field(..., example="Overall feedback sentiment remains strong at +0.68 Index (78% Positive). Localized checkout friction detected.")
    keyOpportunities: List[str] = Field(default_factory=list)
    riskCount: int = Field(..., example=1)
