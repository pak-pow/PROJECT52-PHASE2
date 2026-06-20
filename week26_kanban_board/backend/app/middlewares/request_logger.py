"""
request_logger.py
Per-request logger middleware.
Registers before/after request hooks on the Flask app.

Output format:
  <-- 200  GET    /api/boards          (3ms)
  <-- 201  POST   /api/columns/1/cards (8ms)
"""

import time
from flask import request  # type: ignore


def register_logger(app):
    """Attach before/after request hooks to *app*."""

    @app.before_request
    def _start_timer():
        request._start_time = time.perf_counter()

    @app.after_request
    def _log_request(response):
        duration_ms = (time.perf_counter() - request._start_time) * 1000
        app.logger.info(
            "<-- %s  %-6s %-45s (%dms)",
            response.status_code,
            request.method,
            request.path,
            duration_ms,
        )
        return response
