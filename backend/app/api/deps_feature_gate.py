"""
Feature Gate Dependencies - Module 3 Phase 3
Dependencies for enforcing subscription feature access and quota limits
"""
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.models.organization import Organization
from app.core.subscription_features import Feature, has_feature, get_quota_limit


def require_feature(required_feature: Feature):
    """
    Dependency factory for feature gating based on subscription plan.

    Checks if user's organization has access to the specified feature.
    Returns 403 with upgrade prompt if feature not available.

    Usage:
        @router.post("", dependencies=[Depends(require_feature(Feature.WATCHLISTS))])
        async def create_watchlist(...):
            pass

    Args:
        required_feature: Feature enum value to check access for

    Returns:
        Dependency function that validates feature access

    Raises:
        HTTPException 400: User not part of organization
        HTTPException 403: Feature not available in current plan
    """
    async def feature_checker(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
    ) -> User:
        if not current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User not part of organization"
            )

        # Get organization
        org = await db.get(Organization, current_user.organization_id)

        if not org:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Organization not found"
            )

        # Check if organization has access to feature
        if not has_feature(org.plan, required_feature):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "feature_not_available",
                    "message": f"{required_feature.value.replace('_', ' ').title()} is not available in your current plan",
                    "feature": required_feature.value,
                    "current_plan": org.plan,
                    "upgrade_url": "/pricing",
                    "required_plans": ["pro", "enterprise"] if required_feature != Feature.API_ACCESS else ["enterprise"]
                }
            )

        return current_user

    return feature_checker


async def check_watchlist_limit(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Check if user can create another watchlist based on plan limits.

    Plan limits:
    - Free: 1 watchlist
    - Pro: 10 watchlists
    - Enterprise: Unlimited (999999)

    Raises:
        HTTPException 403: Watchlist limit exceeded for current plan
    """
    from app.models.watchlist import Watchlist

    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not part of organization"
        )

    # Get organization and plan
    org = await db.get(Organization, current_user.organization_id)

    if not org:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization not found"
        )

    # Count existing watchlists for this user
    stmt = select(func.count(Watchlist.id)).where(
        Watchlist.user_id == current_user.id
    )
    result = await db.execute(stmt)
    current_count = result.scalar() or 0

    # Get limit for current plan
    limit = get_quota_limit(org.plan, "watchlists")

    # Check if limit exceeded
    if current_count >= limit:
        # Determine which plans allow more watchlists
        required_plan = "Pro" if org.plan == "free" else "Enterprise"

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "watchlist_limit_exceeded",
                "message": f"You have reached your plan limit of {limit} watchlist{'s' if limit != 1 else ''}",
                "current_count": current_count,
                "limit": limit,
                "current_plan": org.plan,
                "upgrade_to": required_plan.lower(),
                "upgrade_url": "/pricing"
            }
        )

    return current_user


async def check_calculation_quota(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Check if organization has remaining calculation quota for the month.

    Plan limits:
    - Free: 100 calculations/month
    - Pro: 1,000 calculations/month
    - Enterprise: 10,000 calculations/month

    Raises:
        HTTPException 403: Monthly calculation quota exceeded
    """
    from app.models.organization import OrganizationQuotaUsage
    from datetime import datetime

    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not part of organization"
        )

    # Get organization
    org = await db.get(Organization, current_user.organization_id)

    if not org:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization not found"
        )

    # Get current month's quota usage
    current_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    stmt = select(OrganizationQuotaUsage).where(
        OrganizationQuotaUsage.organization_id == org.id,
        OrganizationQuotaUsage.month_start == current_month
    )
    result = await db.execute(stmt)
    quota_usage = result.scalar_one_or_none()

    # Get current usage
    current_usage = quota_usage.calculations_used if quota_usage else 0

    # Get limit for current plan
    limit = get_quota_limit(org.plan, "calculations_per_month")

    # Check if quota exceeded
    if current_usage >= limit:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "calculation_quota_exceeded",
                "message": f"You have used all {limit} calculations for this month",
                "current_usage": current_usage,
                "limit": limit,
                "current_plan": org.plan,
                "resets_on": (current_month.replace(month=current_month.month + 1) if current_month.month < 12
                             else current_month.replace(year=current_month.year + 1, month=1)).isoformat(),
                "upgrade_url": "/pricing"
            }
        )

    return current_user


async def check_saved_calculations_limit(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Check if user can save another calculation based on plan limits.

    Plan limits:
    - Free: 10 saved calculations
    - Pro: 100 saved calculations
    - Enterprise: Unlimited (999999)

    Raises:
        HTTPException 403: Saved calculations limit exceeded
    """
    from app.models.calculation import Calculation

    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not part of organization"
        )

    # Get organization
    org = await db.get(Organization, current_user.organization_id)

    if not org:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization not found"
        )

    # Count saved calculations for this user
    stmt = select(func.count(Calculation.id)).where(
        Calculation.user_id == current_user.id
    )
    result = await db.execute(stmt)
    current_count = result.scalar() or 0

    # Get limit for current plan
    limit = get_quota_limit(org.plan, "saved_calculations")

    # Check if limit exceeded
    if current_count >= limit:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "saved_calculations_limit_exceeded",
                "message": f"You have reached your plan limit of {limit} saved calculations",
                "current_count": current_count,
                "limit": limit,
                "current_plan": org.plan,
                "upgrade_url": "/pricing"
            }
        )

    return current_user
