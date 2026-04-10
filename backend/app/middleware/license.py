import os
import httpx
import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

LICENSE_ADMIN_URL = os.environ.get("LICENSE_ADMIN_URL", "https://app-access.up.railway.app")
LICENSE_ADMIN_KEY = os.environ.get("LICENSE_ADMIN_KEY", "")
CACHE_TTL = 300  # 5 minutes

SKIP_PATHS = [
    "/api/v1/auth",
    "/api/v1/webhooks",
    "/api/v1/health",
    "/health",
    "/pricing",
    "/app",
    "/",
    "/docs",
    "/openapi.json",
    "/redoc",
]

_cache: dict = {}
_cache_time: float = 0


async def fetch_licenses() -> list:
    global _cache, _cache_time
    now = time.time()
    if _cache and (now - _cache_time) < CACHE_TTL:
        return _cache
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.get(
                f"{LICENSE_ADMIN_URL}/admin/licenses/",
                headers={"x-admin-key": LICENSE_ADMIN_KEY}
            )
            if r.status_code == 200:
                _cache = r.json()
                _cache_time = now
                return _cache
    except Exception:
        pass
    return _cache


class LicenseMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        if any(path.startswith(skip) for skip in SKIP_PATHS):
            return await call_next(request)

        api_key = request.headers.get("X-Api-Key")
        if not api_key:
            return JSONResponse(
                status_code=403,
                content={"detail": "No license key provided. Contact DJ AI Business Consultant to get access."}
            )

        licenses = await fetch_licenses()

        if not licenses:
            return await call_next(request)

        valid = any(
            l.get("api_key") == api_key and l.get("status") == "active"
            for l in licenses
        )

        if valid:
            return await call_next(request)

        return JSONResponse(
            status_code=403,
            content={"detail": "License invalid, expired, or revoked. Contact don@djaibc.com to renew."}
        )
