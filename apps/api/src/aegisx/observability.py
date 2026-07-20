import logging
import sys
import time
from collections import Counter
from collections.abc import Awaitable, Callable
from uuid import uuid4

import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


def configure_logging() -> None:
    logging.basicConfig(format="%(message)s", stream=sys.stdout, level=logging.INFO)
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            structlog.processors.add_log_level,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
    )


class RequestTelemetryMiddleware(BaseHTTPMiddleware):
    counters: Counter[str] = Counter()

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        request_id = request.headers.get("x-request-id", str(uuid4()))[:128]
        correlation_id = request.headers.get("x-correlation-id", request_id)[:128]
        started = time.perf_counter()
        structlog.contextvars.bind_contextvars(request_id=request_id, correlation_id=correlation_id)
        try:
            response = await call_next(request)
            self.counters[f"http_{response.status_code}"] += 1
            return response
        finally:
            structlog.get_logger().info(
                "http_request",
                method=request.method,
                path=request.url.path,
                duration_ms=round((time.perf_counter() - started) * 1000, 2),
            )
            structlog.contextvars.clear_contextvars()
