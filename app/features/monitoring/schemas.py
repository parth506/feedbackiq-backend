"""
Monitoring Schemas — DTOs for system observability metrics.
"""
from pydantic import BaseModel, Field


class MonitoringStatusDTO(BaseModel):
    """Real-time system SLA metrics response."""
    uptime_seconds: float = Field(..., description="Seconds since process startup")
    requests_total: int = Field(..., description="Total HTTP requests processed")
    error_rate: float = Field(..., description="Fraction of requests that resulted in 5xx errors (0.0–1.0)")
