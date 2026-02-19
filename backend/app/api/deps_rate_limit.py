"""
Rate Limit Dependencies

FastAPI dependencies for user-based rate limiting and organization quota enforcement.
"""
from fastapi import Request, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from datetime import datetime, timedelta
import uuid
from typing import Optional

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.models.organization import Organization
from app.models.rate_limit import OrganizationQuotaUsage
from app.services.rate_limiter import RateLimiterService
from app.core.rate_limit_config import USER_RATE_LIMITS_BY_ROLE, RATE_LIMIT_WINDOW_SECONDS


async def check_user_rate_limit(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Check user-based rate limit (tiered by role).
    Apply this dependency to authenticated endpoints.

    Rate Limits by Role:
    - viewer: 50 requests/minute
    - user: 100 requests/minute
    - admin: 500 requests/minute
    - superadmin: unlimited (bypassed)

    Args:
        request: FastAPI request object
        current_user: Authenticated user from JWT
        db: Database session

    Raises:
        HTTPException: 429 if rate limit exceeded

    Side Effects:
        Stores rate limit info in request.state for response headers
    """

    # Superadmins bypass rate limits
    if current_user.is_superuser:
        # Still store headers showing unlimited access
        request.state.user_rate_limit = {
            "limit": 999999,
            "remaining": 999999,
            "reset": datetime.utcnow() + timedelta(seconds=RATE_LIMIT_WINDOW_SECONDS)
        }
        return

    # Get rate limit for user's role
    limit = USER_RATE_LIMITS_BY_ROLE.get(current_user.role, USER_RATE_LIMITS_BY_ROLE["user"])

    # Check rate limit
    rate_limiter = RateLimiterService()
    is_allowed, remaining, reset_time = await rate_limiter.check_rate_limit(
        db=db,
        identifier=current_user.id,
        identifier_type='user',
        limit=limit,
        window_seconds=RATE_LIMIT_WINDOW_SECONDS
    )

    if not is_allowed:
        # Log violation
        await rate_limiter.log_violation(
            db=db,
            identifier=current_user.id,
            identifier_type='user',
            violation_type='user_rate',
            attempted_count=limit + 1,
            limit=limit,
            endpoint=request.url.path,
            user_id=current_user.id,
            user_agent=request.headers.get('user-agent')
        )

        # Calculate retry_after
        retry_after = max(1, int((reset_time - datetime.utcnow()).total_seconds()))

        # Raise 429 error
        raise HTTPException(
            status_code=429,
            detail={
                "error": "rate_limit_exceeded",
                "message": f"Rate limit exceeded for {current_user.role} role. Limit: {limit} requests/minute.",
                "limit": limit,
                "window_seconds": RATE_LIMIT_WINDOW_SECONDS,
                "retry_after": retry_after,
                "reset_at": reset_time.isoformat()
            },
            headers={
                "X-RateLimit-Limit": str(limit),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(int(reset_time.timestamp())),
                "Retry-After": str(retry_after)
            }
        )

    # Store rate limit info in request state for response headers
    request.state.user_rate_limit = {
        "limit": limit,
        "remaining": remaining,
        "reset": reset_time
    }


async def check_calculation_quota(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Check monthly calculation quota for organization.
    Apply ONLY to calculation endpoints (POST /calculate, POST /save).

    Quota Limits by Plan:
    - free: 100 calculations/month
    - pro: 1000 calculations/month
    - enterprise: 10000 calculations/month

    Individual users (no organization): No quota limit

    Args:
        request: FastAPI request object
        current_user: Authenticated user from JWT
        db: Database session

    Raises:
        HTTPException: 429 if monthly quota exceeded

    Side Effects:
        - Increments quota counter if allowed
        - Stores quota info in request.state for response headers
    """

    # Individual users without organization have no quota limit
    if not current_user.organization_id:
        # Still store headers showing no limit
        request.state.quota_info = {
            "limit": 999999,
            "remaining": 999999,
            "reset": _get_next_month_start()
        }
        return

    # Get organization
    org = await db.get(Organization, current_user.organization_id)
    if not org:
        raise HTTPException(
            status_code=400,
            detail="Organization not found"
        )

    # Get current month in YYYY-MM format
    current_month = datetime.utcnow().strftime("%Y-%m")

    # Query for existing quota usage record
    stmt = select(OrganizationQuotaUsage).where(
        and_(
            OrganizationQuotaUsage.organization_id == org.id,
            OrganizationQuotaUsage.year_month == current_month
        )
    )
    result = await db.execute(stmt)
    quota_usage = result.scalar_one_or_none()

    # Create quota record if doesn't exist
    if not quota_usage:
        quota_usage = OrganizationQuotaUsage(
            id=str(uuid.uuid4()),
            organization_id=org.id,
            year_month=current_month,
            calculation_count=0,
            quota_limit=org.max_calculations_per_month
        )
        db.add(quota_usage)
        await db.commit()
        await db.refresh(quota_usage)

    # Check if quota exceeded
    if quota_usage.calculation_count >= quota_usage.quota_limit:
        # Log violation
        rate_limiter = RateLimiterService()
        await rate_limiter.log_violation(
            db=db,
            identifier=str(org.id),
            identifier_type='organization',
            violation_type='quota',
            attempted_count=quota_usage.calculation_count + 1,
            limit=quota_usage.quota_limit,
            endpoint=request.url.path,
            user_id=current_user.id,
            user_agent=request.headers.get('user-agent')
        )

        # Calculate reset time (first day of next month)
        reset_time = _get_next_month_start()

        # Raise 429 error
        raise HTTPException(
            status_code=429,
            detail={
                "error": "quota_exceeded",
                "message": f"Monthly calculation quota exceeded. Limit: {quota_usage.quota_limit} calculations/month.",
                "quota_limit": quota_usage.quota_limit,
                "quota_used": quota_usage.calculation_count,
                "quota_remaining": 0,
                "reset_at": reset_time.isoformat(),
                "organization_plan": org.plan,
                "upgrade_message": "Consider upgrading your plan for higher quotas."
            },
            headers={
                "X-Quota-Limit": str(quota_usage.quota_limit),
                "X-Quota-Remaining": "0",
                "X-Quota-Reset": str(int(reset_time.timestamp())),
            }
        )

    # Increment quota counter (allowed)
    quota_usage.calculation_count += 1
    quota_usage.updated_at = datetime.utcnow()
    await db.commit()

    # Store quota info for response headers
    remaining = quota_usage.quota_limit - quota_usage.calculation_count
    request.state.quota_info = {
        "limit": quota_usage.quota_limit,
        "remaining": remaining,
        "reset": _get_next_month_start()
    }


def _get_next_month_start() -> datetime:
    """
    Calculate the start of next month (midnight on the 1st).

    Returns:
        datetime: First moment of next month
    """
    now = datetime.utcnow()

    # Calculate next month
    if now.month == 12:
        # December -> January next year
        next_month = datetime(now.year + 1, 1, 1, 0, 0, 0)
    else:
        # Any other month
        next_month = datetime(now.year, now.month + 1, 1, 0, 0, 0)

    return next_month


# Optional: Dependency for checking both user rate limit AND quota
# Use this on calculation endpoints for convenience
async def check_user_rate_and_quota(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Combined dependency that checks both user rate limit and organization quota.
    Convenient for calculation endpoints.

    Equivalent to:
        dependencies=[Depends(check_user_rate_limit), Depends(check_calculation_quota)]

    Args:
        request: FastAPI request object
        current_user: Authenticated user
        db: Database session

    Raises:
        HTTPException: 429 if either limit exceeded
    """
    # Check user rate limit first (faster)
    await check_user_rate_limit(request, current_user, db)

    # Then check quota
    await check_calculation_quota(request, current_user, db)
