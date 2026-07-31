from typing import List
from pydantic import BaseModel, Field

class EmotionScoreDTO(BaseModel):
    emotion: str = Field(..., example="Joy")
    score: float = Field(..., example=48.0)
    percentage: float = Field(..., example=48.0)
    color: str = Field(..., example="#10b981")

class SentimentEvolutionDTO(BaseModel):
    date: str = Field(..., example="Jul 30")
    sentimentIndex: float = Field(..., example=0.68)
    positiveRatio: float = Field(..., example=0.78)
