"""
Monitoring Service — Real system observability metrics.

Replaces the hardcoded dummy values in features/monitoring/router.py.

Tracks:
  - uptime_seconds: since app startup
  - requests_total: incremented by CorrelationIDMiddleware context
  - error_rate: rolling ratio of 5xx responses (simplified via AtomicCounters)

Architecture:
  - Module-level counters (process-scoped, resets on restart).
  - For multi-process/multi-instance production, swap with Redis counters.
"""
import logging
import time
from typing import Optional

logger = logging.getLogger(__name__)

# ── Process-scoped atomic counters ────────────────────────────────────────────
# These are simple integers safe for single-process uvicorn.
# For multi-worker setups, use Redis INCR instead.
_start_time: float = time.monotonic()
_requests_total: int = 0
_errors_total: int = 0


def record_request() -> None:
    """Increment the total request counter. Called from middleware."""
    global _requests_total
    _requests_total += 1


def record_error() -> None:
    """Increment the error counter. Called from exception handlers on 5xx."""
    global _errors_total
    _errors_total += 1


class MonitoringService:
    """Provides real-time system observability metrics."""

    def get_uptime_seconds(self) -> float:
        """Return seconds since the process started."""
        return round(time.monotonic() - _start_time, 2)

    def get_requests_total(self) -> int:
        """Return total HTTP requests processed since startup."""
        return _requests_total

    def get_error_rate(self) -> float:
        """
        Return the error rate as a fraction (0.0–1.0).
        Returns 0.0 when no requests have been recorded.
        """
        if _requests_total == 0:
            return 0.0
        return round(_errors_total / _requests_total, 4)

    def get_metrics(self) -> dict:
        """Return all metrics as a single dict."""
        return {
            "uptime_seconds": self.get_uptime_seconds(),
            "requests_total": self.get_requests_total(),
            "error_rate": self.get_error_rate(),
        }
