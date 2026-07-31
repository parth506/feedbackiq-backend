from typing import List
from fastapi import APIRouter
from app.features.analytics.schemas import TimeSeriesPointDTO, CategoryMetricDTO

router = APIRouter(prefix="/v1/analytics", tags=["3. Analytics & Time Series"])

@router.get("/time-series", response_model=List[TimeSeriesPointDTO], summary="Get Time Series Analytics")
async def get_time_series() -> List[TimeSeriesPointDTO]:
    """Retrieve time-series trends, moving averages, and sentiment seasonality."""
    return [
        TimeSeriesPointDTO(date="Jul 01", totalVolume=420, positive=280, neutral=90, negative=50, movingAverage=410.0),
        TimeSeriesPointDTO(date="Jul 15", totalVolume=490, positive=330, neutral=115, negative=45, movingAverage=485.0),
        TimeSeriesPointDTO(date="Jul 30", totalVolume=630, positive=450, neutral=125, negative=55, movingAverage=560.0),
    ]

@router.get("/categories", response_model=List[CategoryMetricDTO], summary="Get Category & Department Analytics")
async def get_categories() -> List[CategoryMetricDTO]:
    """Retrieve department feedback closure SLA metrics."""
    return [
        CategoryMetricDTO(department="Product & UX", total=4500, resolved=4320, unresolved=180, satisfactionScore=4.6),
        CategoryMetricDTO(department="Billing & Sales", total=3200, resolved=3010, unresolved=190, satisfactionScore=4.1),
        CategoryMetricDTO(department="Customer Care", total=2600, resolved=2540, unresolved=60, satisfactionScore=4.8),
    ]
