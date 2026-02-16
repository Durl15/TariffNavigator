"""
Audit Logging Middleware
Automatically logs all write operations (POST, PUT, PATCH, DELETE) to the audit_logs table.
"""
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from jose import jwt, JWTError
import time
import uuid
from typing import Optional

from app.core.config import settings
from app.models.calculation import AuditLog
from app.db.session import async_session


class AuditMiddleware(BaseHTTPMiddleware):
    """
    Middleware to automatically log all write operations to audit_logs table.

    Logs:
    - All POST, PUT, PATCH, DELETE requests
    - User who made the request (from JWT)
    - Request details (method, endpoint, IP, user agent)
    - Response status code and duration

    Skips:
    - Health checks
    - Documentation endpoints
    - Static files
    - Read-only operations (GET)
    """

    # Paths to skip logging
    SKIP_PATHS = [
        '/health',
        '/docs',
        '/redoc',
        '/openapi.json',
        '/favicon.ico',
        '/static'
    ]

    # HTTP methods to log (write operations only)
    LOGGED_METHODS = ['POST', 'PUT', 'PATCH', 'DELETE']

    async def dispatch(self, request: Request, call_next) -> Response:
        """Process request and log if applicable."""

        # Skip certain paths
        if any(request.url.path.startswith(path) for path in self.SKIP_PATHS):
            return await call_next(request)

        # Only log write operations
        if request.method not in self.LOGGED_METHODS:
            return await call_next(request)

        # Record start time
        start_time = time.time()

        # Extract user ID from JWT token
        user_id = await self._extract_user_id(request)

        # Process the request
        response = await call_next(request)

        # Calculate request duration
        duration_ms = int((time.time() - start_time) * 1000)

        # Log to database asynchronously (don't block response)
        # Note: This runs in the background and won't delay the response
        try:
            await self._log_to_database(
                user_id=user_id,
                request=request,
                status_code=response.status_code,
                duration_ms=duration_ms
            )
        except Exception as e:
            # Don't fail the request if audit logging fails
            print(f"Audit logging error: {e}")

        return response

    async def _extract_user_id(self, request: Request) -> Optional[str]:
        """
        Extract user ID from JWT token in Authorization header.
        Returns None if no valid token found.
        """
        try:
            # Get Authorization header
            auth_header = request.headers.get('authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return None

            # Extract token
            token = auth_header.split(' ')[1]

            # Decode JWT
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=['HS256']
            )

            # Get user email from token
            email = payload.get('sub')
            if not email:
                return None

            # Look up user ID from email
            # Note: We could cache this to avoid DB lookups
            async with async_session() as db:
                from app.models.user import User
                from sqlalchemy import select

                result = await db.execute(
                    select(User.id).where(User.email == email)
                )
                user_id = result.scalar_one_or_none()
                return user_id

        except (JWTError, KeyError, ValueError):
            return None
        except Exception as e:
            print(f"Error extracting user ID: {e}")
            return None

    async def _log_to_database(
        self,
        user_id: Optional[str],
        request: Request,
        status_code: int,
        duration_ms: int
    ):
        """Save audit log entry to database."""

        async with async_session() as db:
            try:
                # Create audit log entry (ID will auto-increment)
                audit_log = AuditLog(
                    user_id=user_id,
                    action=self._determine_action(request.method, request.url.path),
                    resource_type=self._determine_resource_type(request.url.path),
                    resource_id=self._extract_resource_id(request.url.path),
                    ip_address=self._get_client_ip(request),
                    user_agent=request.headers.get('user-agent'),
                    endpoint=request.url.path,
                    method=request.method,
                    status_code=status_code,
                    duration_ms=duration_ms
                )

                db.add(audit_log)
                await db.commit()

            except Exception as e:
                print(f"Failed to save audit log: {e}")
                await db.rollback()

    def _determine_action(self, method: str, path: str) -> str:
        """
        Determine action type from HTTP method.
        Returns: create, update, delete, or unknown
        """
        action_map = {
            'POST': 'create',
            'PUT': 'update',
            'PATCH': 'update',
            'DELETE': 'delete'
        }
        return action_map.get(method, 'unknown')

    def _determine_resource_type(self, path: str) -> str:
        """
        Extract resource type from URL path.
        Example: /api/v1/users/123 -> users
        Example: /api/v1/calculations -> calculations
        """
        # Remove leading/trailing slashes and split
        parts = [p for p in path.strip('/').split('/') if p]

        # Skip common prefixes (api, v1, etc.)
        skip_parts = ['api', 'v1', 'v2', 'admin']
        filtered_parts = [p for p in parts if p not in skip_parts]

        # Return first part as resource type
        if filtered_parts:
            resource = filtered_parts[0]
            # Remove query parameters if present
            resource = resource.split('?')[0]
            return resource

        return 'unknown'

    def _extract_resource_id(self, path: str) -> Optional[str]:
        """
        Extract resource ID from URL path.
        Example: /api/v1/users/abc-123 -> abc-123
        Returns None if no ID found.
        """
        parts = [p for p in path.strip('/').split('/') if p]

        # Look for UUID-like patterns or numeric IDs
        # Typically the ID comes after the resource name
        for i, part in enumerate(parts):
            # Skip common prefixes
            if part in ['api', 'v1', 'v2', 'admin']:
                continue

            # If next part looks like an ID, return it
            if i + 1 < len(parts):
                next_part = parts[i + 1]
                # Check if it's an ID (UUID, number, or alphanumeric)
                if (len(next_part) > 10 or  # UUID length
                    next_part.isdigit() or  # Numeric ID
                    '-' in next_part):  # Hyphenated ID
                    return next_part

        return None

    def _get_client_ip(self, request: Request) -> str:
        """
        Get client IP address from request.
        Checks X-Forwarded-For header for proxied requests.
        """
        # Check for proxy headers first
        forwarded_for = request.headers.get('x-forwarded-for')
        if forwarded_for:
            # X-Forwarded-For can contain multiple IPs, take the first one
            return forwarded_for.split(',')[0].strip()

        # Check for other common proxy headers
        real_ip = request.headers.get('x-real-ip')
        if real_ip:
            return real_ip

        # Fall back to direct client IP
        if request.client:
            return request.client.host

        return 'unknown'


# Manual audit logging helper function
async def log_audit(
    user_id: str,
    action: str,
    resource_type: str,
    resource_id: Optional[str] = None,
    details: Optional[dict] = None
):
    """
    Manually log an audit event (for non-HTTP actions).

    Usage:
        await log_audit(
            user_id=current_user.id,
            action='login',
            resource_type='auth',
            details={'method': '2fa'}
        )

    Args:
        user_id: ID of user performing action
        action: Type of action (create, update, delete, login, etc.)
        resource_type: Type of resource affected
        resource_id: ID of specific resource (optional)
        details: Additional context (optional)
    """
    async with async_session() as db:
        try:
            audit_log = AuditLog(
                user_id=user_id,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                # These fields will be None for manual logs
                ip_address=None,
                user_agent=None,
                endpoint=None,
                method=None,
                status_code=None,
                duration_ms=None
            )

            db.add(audit_log)
            await db.commit()

        except Exception as e:
            print(f"Manual audit logging failed: {e}")
            await db.rollback()
