"""
request_logger.py
Simple per-request logger middleware.
Registers before/after request hooks on the Flask app.

Output format:
  --> GET  /api/recipes
  <-- 200  GET  /api/recipes  (4ms)
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
        # Skip logging static file / upload serving to keep noise low
        if not request.path.startswith('/uploads'):
            app.logger.info(
                "<-- %s  %-6s %-40s (%dms)",
                response.status_code,
                request.method,
                request.path,
                duration_ms,
            )
        return response
