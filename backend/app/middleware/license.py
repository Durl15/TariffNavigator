import os
import httpx
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

LICENSE_ADMIN_URL = os.environ.get("LICENSE_ADMIN_URL", "https://app-access.up.railway.app")

SKIP_PATHS = [
    "/api/v1/auth",
    "/api/v1/webhooks",
    "/health",
    "/api/v1/health",
    "/pricing",
    "/app",
    "/",
    "/docs",
    "/openapi.json",
]

class LicenseMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        if any(path.startswith(skip) for skip in SKIP_PATHS):
            return await call_next(request)
        api_key = request.headers.get("X-Api-Key")
        if not api_key:
            return JSONResponse(
                status_code=403,
                content={"detail": "No license key provided. Contact DJ AI to get access."}
            )
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                r = await client.get(
                    f"{LICENSE_ADMIN_URL}/admin/licenses/",
                    headers={"x-admin-key": os.environ.get("LICENSE_ADMIN_KEY", "")}
                )
                if r.status_code == 200:
                    licenses = r.json()
                    valid = any(
                        l["api_key"] == api_key and l["status"] == "active"
                        for l in licenses
                    )
                    if valid:
                        return await call_next(request)
        except Exception:
            pass
        return JSONResponse(
            status_code=403,
            content={"detail": "License invalid, expired, or revoked."}
        )
