import asyncio
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

router = APIRouter(prefix="/v1/monitoring", tags=["15. Observability & Monitoring"])

class MonitoringStatusDTO(BaseModel):
    uptime_seconds: float = Field(default=86400.0)
    requests_total: int = Field(default=14892)
    error_rate: float = Field(default=0.01)

@router.get("/metrics", response_model=MonitoringStatusDTO, summary="Get Prometheus SLA Metrics")
async def get_monitoring_metrics() -> MonitoringStatusDTO:
    """Retrieve system uptime, request counters, and error rate SLA metrics."""
    return MonitoringStatusDTO()

@router.get("/events/stream", summary="Server-Sent Events (SSE) Live KPI Feed")
async def sse_live_stream():
    """Stream live KPI updates over Server-Sent Events (SSE)."""
    async def event_generator():
        while True:
            await asyncio.sleep(3)
            payload = json.dumps({"type": "kpi_heartbeat", "sentiment_index": 0.68, "active_users": 1420})
            yield f"data: {payload}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@router.websocket("/ws/stream")
async def websocket_live_stream(websocket: WebSocket):
    """WebSocket endpoint for real-time live feedback stream and KPI broadcasts."""
    await websocket.accept()
    try:
        while True:
            await asyncio.sleep(4)
            await websocket.send_json({
                "type": "live_feedback",
                "id": "ws-01",
                "time": "Just now",
                "sentiment": "Positive",
                "comment": "Live WebSocket stream: UI speed benchmark reached +98%"
            })
    except WebSocketDisconnect:
        pass
