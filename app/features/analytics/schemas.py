from typing import List, Optional
from pydantic import BaseModel, Field

class TimeSeriesPointDTO(BaseModel):
    date: str = Field(..., example="2026-07-30")
    totalVolume: int = Field(..., example=630)
    positive: int = Field(..., example=450)
    neutral: int = Field(..., example=125)
    negative: int = Field(..., example=55)
    movingAverage: float = Field(..., example=560.0)

class CategoryMetricDTO(BaseModel):
    department: str = Field(..., example="Product & UX")
    total: int = Field(..., example=4500)
    resolved: int = Field(..., example=4320)
    unresolved: int = Field(..., example=180)
    satisfactionScore: float = Field(..., example=4.6)
