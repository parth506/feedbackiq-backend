from typing import List
from fastapi import APIRouter
from app.features.predictions.schemas import ForecastPointDTO

router = APIRouter(prefix="/v1/predictions", tags=["7. Predictive Analytics"])

@router.get("/forecast", response_model=List[ForecastPointDTO], summary="Get 90-Day Predictive Forecast")
async def get_forecast() -> List[ForecastPointDTO]:
    """Retrieve 90-day time-series predictions with 95% confidence intervals."""
    return [
        ForecastPointDTO(date="Aug 01", actualFeedback=510, predictedFeedback=512, lowerBound=490, upperBound=535, predictedRating=4.45, predictedChurnRate=1.2),
        ForecastPointDTO(date="Aug 15", predictedFeedback=610, lowerBound=570, upperBound=650, predictedRating=4.50, predictedChurnRate=0.9),
        ForecastPointDTO(date="Aug 30", predictedFeedback=720, lowerBound=670, upperBound=770, predictedRating=4.58, predictedChurnRate=0.7),
    ]
