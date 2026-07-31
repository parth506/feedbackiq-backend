from typing import List
from pydantic import BaseModel, Field

class TopicClusterDTO(BaseModel):
    id: str = Field(..., example="t1")
    name: str = Field(..., example="UI Design & Speed")
    category: str = Field(..., example="UX")
    volume: int = Field(..., example=3420)
    importanceScore: float = Field(..., example=92.0)
    sentimentScore: float = Field(..., example=0.82)

class KeywordFrequencyDTO(BaseModel):
    keyword: str = Field(..., example="UI Speed")
    frequency: int = Field(..., example=98)
    sentiment: str = Field(..., example="positive")
