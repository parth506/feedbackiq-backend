"""
Monitoring Router — Thin delegate. Metrics from MonitoringService.
SSE and WebSocket endpoints now stream real MongoDB feedback.
"""
import asyncio
import json
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse

from app.dependencies.feedback import get_monitoring_service, get_feedback_repository
from app.features.monitoring.schemas import MonitoringStatusDTO
from app.repositories.feedback import FeedbackRepository
from app.services.monitoring_service import MonitoringService
from app.core.constants import (
    MONITORING_SSE_INTERVAL_SECONDS,
    MONITORING_WS_INTERVAL_SECONDS,
)

router = APIRouter(prefix="/v1/monitoring", tags=["15. Observability & Monitoring"])
logger = logging.getLogger(__name__)


@router.get(
    "/metrics",
    response_model=MonitoringStatusDTO,
    summary="Get Real-Time SLA Metrics",
    description="Returns actual uptime, total request count, and error rate since last startup.",
)
async def get_monitoring_metrics(
    service: MonitoringService = Depends(get_monitoring_service),
) -> MonitoringStatusDTO:
    """Return real system observability metrics."""
    metrics = service.get_metrics()
    return MonitoringStatusDTO(**metrics)


@router.get(
    "/events/stream",
    summary="Server-Sent Events — Live Feedback Feed",
    description="Streams the latest feedback document from MongoDB every 3 seconds via SSE.",
)
async def sse_live_stream(
    repository: FeedbackRepository = Depends(get_feedback_repository),
):
    """Stream live feedback updates over Server-Sent Events."""
    async def event_generator():
        while True:
            await asyncio.sleep(MONITORING_SSE_INTERVAL_SECONDS)
            try:
                docs = await repository.find_latest(limit=1)
                if docs:
                    doc = docs[0]
                    created_at = doc.get("created_at")
                    payload = json.dumps({
                        "type": "live_feedback",
                        "id": str(doc.get("_id", "")),
                        "sentiment": doc.get("sentiment", ""),
                        "comment": (doc.get("comment") or "")[:120],
                        "created_at": created_at.isoformat() if hasattr(created_at, "isoformat") else str(created_at),
                        "ts": datetime.now(timezone.utc).isoformat(),
                    })
                else:
                    payload = json.dumps({"type": "heartbeat", "ts": datetime.now(timezone.utc).isoformat()})
                yield f"data: {payload}\n\n"
            except Exception as exc:
                logger.warning("SSE stream error: %s", exc)
                yield f"data: {json.dumps({'type': 'error', 'msg': 'stream error'})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.websocket("/ws/stream")
async def websocket_live_stream(
    websocket: WebSocket,
    repository: FeedbackRepository = Depends(get_feedback_repository),
):
    """WebSocket endpoint — streams the latest real feedback from MongoDB."""
    await websocket.accept()
    try:
        while True:
            await asyncio.sleep(MONITORING_WS_INTERVAL_SECONDS)
            docs = await repository.find_latest(limit=1)
            if docs:
                doc = docs[0]
                created_at = doc.get("created_at")
                await websocket.send_json({
                    "type": "live_feedback",
                    "id": str(doc.get("_id", "")),
                    "sentiment": doc.get("sentiment", ""),
                    "comment": (doc.get("comment") or "")[:120],
                    "created_at": created_at.isoformat() if hasattr(created_at, "isoformat") else str(created_at),
                    "ts": datetime.now(timezone.utc).isoformat(),
                })
            else:
                await websocket.send_json({"type": "heartbeat", "ts": datetime.now(timezone.utc).isoformat()})
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected.")
    except Exception as exc:
        logger.warning("WebSocket stream error: %s", exc)
