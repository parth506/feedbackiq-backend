from typing import List, Optional
from pydantic import BaseModel, Field

class SearchQueryDTO(BaseModel):
    query: str = Field(..., example="dashboard")

class SearchResultDTO(BaseModel):
    id: str = Field(..., example="679a1234567890abcdef1234")
    sentiment: str = Field(..., example="positive")
    comment: str = Field(..., example="Great dashboard loading speed.")
    created_at: str = Field(..., example="2026-07-30T10:00:00Z")
