"""
Centralized logging configuration for FeedbackIQ.

In production (APP_ENV=production), emits structured JSON suitable for
log aggregation (Datadog, CloudWatch, GCP Logging, etc.).

In development, emits human-readable formatted output.

Correlation IDs are propagated via a contextvars.ContextVar so every
log line produced within a single request automatically includes the
same request trace ID.
"""
import json
import logging
import sys
from contextvars import ContextVar
from datetime import datetime, timezone

from app.config.settings import get_settings

# ── Correlation ID context variable ───────────────────────────────────────────
# Set by CorrelationIDMiddleware at request entry; read by CorrelationFilter.
correlation_id_ctx: ContextVar[str] = ContextVar("correlation_id", default="-")

settings = get_settings()


# ── JSON Formatter ─────────────────────────────────────────────────────────────
class JSONFormatter(logging.Formatter):
    """
    Emits each log record as a single-line JSON object.
    Fields: ts, level, logger, corr_id, message, exc_info (optional)
    """

    def format(self, record: logging.LogRecord) -> str:  # type: ignore[override]
        log_entry: dict = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "corr_id": correlation_id_ctx.get("-"),
            "message": record.getMessage(),
        }
        if record.exc_info:
            log_entry["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(log_entry, ensure_ascii=False)


# ── Human-readable Formatter ───────────────────────────────────────────────────
class ReadableFormatter(logging.Formatter):
    """
    Emits human-friendly lines for local development.
    Format: timestamp | level | logger | [corr_id] | message
    """

    def format(self, record: logging.LogRecord) -> str:  # type: ignore[override]
        corr = correlation_id_ctx.get("-")
        record.corr_id = corr
        return super().format(record)


# ── Correlation Filter ─────────────────────────────────────────────────────────
class CorrelationFilter(logging.Filter):
    """Injects corr_id attribute into every log record from contextvars."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.corr_id = correlation_id_ctx.get("-")
        return True


# ── Public Setup Function ──────────────────────────────────────────────────────
def setup_logging() -> None:
    """Configure root logger. Called once at application startup."""
    log_level = logging.DEBUG if settings.DEBUG else logging.INFO
    is_prod = settings.is_production

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.addFilter(CorrelationFilter())

    if is_prod:
        stdout_handler.setFormatter(JSONFormatter())
    else:
        formatter = ReadableFormatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | [%(corr_id)s] | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        stdout_handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    # Remove existing handlers to prevent duplicate logs on re-import
    root_logger.handlers = []
    root_logger.addHandler(stdout_handler)

    # Silence noisy third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)
    logging.getLogger("motor").setLevel(logging.WARNING)
    logging.getLogger("pymongo").setLevel(logging.WARNING)
