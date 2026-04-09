"""Security middleware: rate limiting, security headers, request audit logging."""

import logging
import time
from collections import defaultdict
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Rate Limiter (in-memory; use Redis in production for multi-instance)
# ---------------------------------------------------------------------------
class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Per-IP rate limiting.
    - Auth endpoints: 10 requests / 60 seconds
    - General API:   100 requests / 60 seconds
    """

    def __init__(self, app, auth_limit: int = 10, general_limit: int = 100, window: int = 60):
        super().__init__(app)
        self.auth_limit = auth_limit
        self.general_limit = general_limit
        self.window = window
        self._hits: dict[str, list[float]] = defaultdict(list)

    def _clean_window(self, key: str, now: float) -> list[float]:
        cutoff = now - self.window
        self._hits[key] = [t for t in self._hits[key] if t > cutoff]
        return self._hits[key]

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "unknown"
        now = time.time()
        path = request.url.path

        is_auth = "/auth/" in path
        key = f"{client_ip}:{'auth' if is_auth else 'api'}"
        limit = self.auth_limit if is_auth else self.general_limit

        hits = self._clean_window(key, now)
        if len(hits) >= limit:
            logger.warning("Rate limit exceeded for %s on %s", client_ip, path)
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests. Please try again later."},
                headers={"Retry-After": str(self.window)},
            )

        self._hits[key].append(now)
        return await call_next(request)


# ---------------------------------------------------------------------------
# Security Headers
# ---------------------------------------------------------------------------
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self'; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data:; "
            "connect-src 'self'"
        )
        if not request.url.path.startswith("/api/docs"):
            response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains; preload"
        return response


# ---------------------------------------------------------------------------
# Audit Logger — logs every mutating request
# ---------------------------------------------------------------------------
class AuditLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.time()
        response: Response = await call_next(request)
        duration_ms = round((time.time() - start) * 1000, 1)

        client_ip = request.client.host if request.client else "unknown"
        method = request.method
        path = request.url.path
        status_code = response.status_code

        if method in ("POST", "PUT", "PATCH", "DELETE"):
            logger.info(
                "AUDIT method=%s path=%s status=%s ip=%s duration_ms=%s",
                method, path, status_code, client_ip, duration_ms,
            )

        if status_code >= 400:
            log_fn = logger.warning if status_code < 500 else logger.error
            log_fn(
                "HTTP %s method=%s path=%s ip=%s duration_ms=%s",
                status_code, method, path, client_ip, duration_ms,
            )

        return response
