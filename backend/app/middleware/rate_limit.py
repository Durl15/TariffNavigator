"""
Rate Limiting Middleware
IP-based rate limiting applied to all requests before authentication.
"""
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response, JSONResponse
from datetime import datetime, timedelta
from typing import Optional

from app.services.rate_limiter import RateLimiterService
from app.db.session import async_session
from app.core.rate_limit_config import IP_RATE_LIMITS, RATE_LIMIT_WINDOW_SECONDS


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Global IP-based rate limiting middleware.

    Applied to ALL requests before authentication to protect against:
    - Anonymous abuse
    - DoS attacks
    - API scraping

    Limits:
    - 100 requests per minute per IP address

    Skips:
    - Health checks
    - Documentation endpoints
    - OpenAPI schema
    """

    # Paths to skip rate limiting (health checks, docs)
    SKIP_PATHS = [
        '/health',
        '/docs',
        '/redoc',
        '/openapi.json',
        '/favicon.ico'
    ]

    # IP rate limit from config
    IP_RATE_LIMIT = IP_RATE_LIMITS["global"]

    async def dispatch(self, request: Request, call_next) -> Response:
        """
        Process request and apply IP-based rate limiting.

        Returns:
            - 429 Too Many Requests if limit exceeded
            - Normal response with rate limit headers if allowed
        """

        # Skip rate limiting for certain paths
        if any(request.url.path.startswith(path) for path in self.SKIP_PATHS):
            return await call_next(request)

        # Skip rate limiting for CORS preflight requests (OPTIONS method)
        if request.method == "OPTIONS":
            return await call_next(request)

        # Get client IP address
        client_ip = self._get_client_ip(request)

        # Check rate limit using async database session
        async with async_session() as db:
            try:
                rate_limiter = RateLimiterService()

                # Check if IP is within rate limit
                is_allowed, remaining, reset_time = await rate_limiter.check_rate_limit(
                    db=db,
                    identifier=client_ip,
                    identifier_type='ip',
                    limit=self.IP_RATE_LIMIT,
                    window_seconds=RATE_LIMIT_WINDOW_SECONDS
                )

                if not is_allowed:
                    # Log violation
                    await rate_limiter.log_violation(
                        db=db,
                        identifier=client_ip,
                        identifier_type='ip',
                        violation_type='ip_rate',
                        attempted_count=self.IP_RATE_LIMIT + 1,
                        limit=self.IP_RATE_LIMIT,
                        endpoint=request.url.path,
                        user_agent=request.headers.get('user-agent')
                    )

                    # Calculate retry_after in seconds
                    retry_after = max(1, int((reset_time - datetime.utcnow()).total_seconds()))

                    # Return 429 Too Many Requests
                    return JSONResponse(
                        status_code=429,
                        content={
                            "detail": "Too many requests. Please try again later.",
                            "error": "rate_limit_exceeded",
                            "limit": self.IP_RATE_LIMIT,
                            "window_seconds": RATE_LIMIT_WINDOW_SECONDS,
                            "retry_after": retry_after
                        },
                        headers={
                            "X-RateLimit-Limit": str(self.IP_RATE_LIMIT),
                            "X-RateLimit-Remaining": "0",
                            "X-RateLimit-Reset": str(int(reset_time.timestamp())),
                            "Retry-After": str(retry_after)
                        }
                    )

                # Request allowed - process it
                response = await call_next(request)

                # Add rate limit headers to response
                response.headers["X-RateLimit-Limit"] = str(self.IP_RATE_LIMIT)
                response.headers["X-RateLimit-Remaining"] = str(remaining)
                response.headers["X-RateLimit-Reset"] = str(int(reset_time.timestamp()))

                return response

            except Exception as e:
                # Don't fail the request if rate limiting has an error
                # Log the error and allow the request through
                print(f"Rate limiting error: {e}")
                # Process request normally
                return await call_next(request)

    def _get_client_ip(self, request: Request) -> str:
        """
        Get client IP address from request.
        Handles proxied requests via X-Forwarded-For header.

        Args:
            request: FastAPI request object

        Returns:
            Client IP address as string
        """
        # Check for proxy headers first (Cloudflare, nginx, etc.)
        forwarded_for = request.headers.get('x-forwarded-for')
        if forwarded_for:
            # X-Forwarded-For can contain multiple IPs, take the first one (client IP)
            return forwarded_for.split(',')[0].strip()

        # Check for other common proxy headers
        real_ip = request.headers.get('x-real-ip')
        if real_ip:
            return real_ip

        # Fall back to direct client IP
        if request.client:
            return request.client.host

        # Should never happen, but fallback to unknown
        return 'unknown'
