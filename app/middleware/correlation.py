"""
Correlation ID Middleware.

Injects a unique X-Correlation-ID into every request/response cycle.
The ID is:
  1. Read from the incoming X-Correlation-ID request header (if provided by upstream proxy/client).
  2. Generated as a UUID4 if absent.

The ID is stored in a ContextVar so it is automatically picked up by all
log formatters within the same async request context without explicit passing.
"""
import logging
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.constants import LOG_CORRELATION_ID_HEADER
from app.utils.logging import correlation_id_ctx

logger = logging.getLogger(__name__)


class CorrelationIDMiddleware(BaseHTTPMiddleware):
    """
    Sets X-Correlation-ID header on every request and response.
    Binds the ID to the request-scoped ContextVar for log propagation.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        # Use existing header from client/proxy, or generate a fresh UUID
        corr_id = request.headers.get(LOG_CORRELATION_ID_HEADER) or str(uuid.uuid4())

        # Bind to ContextVar — all loggers in this request will read it
        token = correlation_id_ctx.set(corr_id)

        try:
            response: Response = await call_next(request)
        finally:
            # Always reset ContextVar to avoid bleed-over across requests
            correlation_id_ctx.reset(token)

        # Echo the correlation ID back in the response header
        response.headers[LOG_CORRELATION_ID_HEADER] = corr_id
        return response
