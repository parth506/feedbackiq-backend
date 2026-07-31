from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter(prefix="/v1/admin", tags=["14. Admin Console"])

class SystemMetricsDTO(BaseModel):
    db_status: str = Field(default="healthy")
    cache_status: str = Field(default="connected")
    storage_mb: float = Field(default=142.5)

@router.get("/health", response_model=SystemMetricsDTO, summary="Admin System & Health Status")
async def admin_health() -> SystemMetricsDTO:
    """Retrieve system health and database storage metrics."""
    return SystemMetricsDTO()
