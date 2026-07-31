from typing import Optional
from pydantic import BaseModel, Field

class ForecastPointDTO(BaseModel):
    date: str = Field(..., example="Aug 01")
    actualFeedback: Optional[int] = Field(default=None, example=510)
    predictedFeedback: int = Field(..., example=512)
    lowerBound: int = Field(..., example=490)
    upperBound: int = Field(..., example=535)
    predictedRating: float = Field(..., example=4.45)
    predictedChurnRate: float = Field(..., example=1.2)
