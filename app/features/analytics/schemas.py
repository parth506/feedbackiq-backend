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

class RatingHistogramItemDTO(BaseModel):
    rating: int
    count: int

class LengthDistributionItemDTO(BaseModel):
    range: str
    count: int

class RatingsResponse(BaseModel):
    ratings: List[RatingHistogramItemDTO]
    lengthDistribution: List[LengthDistributionItemDTO]

class GeographicRegionDTO(BaseModel):
    country: str
    code: str
    totalFeedback: int
    positivePercent: float
    neutralPercent: float
    negativePercent: float
    avgRating: float
    lat: float
    lng: float

class CustomerClusterPointDTO(BaseModel):
    id: str
    customerName: str
    segment: str
    satisfactionScore: float
    age: int
    incomeK: int
    frequency: int
    recencyDays: int
    monetaryValue: float

class MLFeatureImportanceDTO(BaseModel):
    feature: str
    importance: float
    shapValue: float
    impact: str

class ConfusionMatrixDTO(BaseModel):
    tp: int = 1240
    fp: int = 84
    fn: int = 62
    tn: int = 890

class MLModelEvaluationDTO(BaseModel):
    accuracy: float
    precision: float
    recall: float
    f1Score: float
    rocAuc: float
    confusionMatrix: Optional[ConfusionMatrixDTO] = Field(default_factory=ConfusionMatrixDTO)

class MLResponseDTO(BaseModel):
    importance: List[MLFeatureImportanceDTO]
    evaluation: MLModelEvaluationDTO

class CorrelationMetricDTO(BaseModel):
    featureA: str
    featureB: str
    coefficient: float


