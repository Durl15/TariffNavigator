"""
Subscription Management Endpoints - Module 3 Phase 2/4
Handles Stripe Checkout, subscription management, and billing
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi import Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
import stripe
import logging

from app.api.deps import get_current_user, get_current_admin_user, get_db
from app.models.user import User
from app.models.organization import Organization
from app.models.subscription import Subscription, Payment
from app.services.subscription_service import SubscriptionService
from app.core.config import settings

# Map plan name → (price_id_setting, role_name, display_name)
PLAN_CONFIG = {
    "pro":         ("STRIPE_PRICE_ID_PRO",         "pro",         "Pro"),
    "enterprise":  ("STRIPE_PRICE_ID_ENTERPRISE",  "enterprise",  "Enterprise"),
    "consultant":  ("STRIPE_PRICE_ID_CONSULTANT",  "consultant",  "Consultant"),
}

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


@router.post("/checkout/create-session")
async def create_checkout_session(
    plan: str = Body(..., embed=True),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a Stripe Checkout session for any authenticated user.
    Works for both individual users (no org) and org members.
    plan: 'pro' | 'enterprise' | 'consultant'
    """
    if plan not in PLAN_CONFIG:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid plan '{plan}'. Must be one of: {', '.join(PLAN_CONFIG)}"
        )

    price_attr, _, display = PLAN_CONFIG[plan]
    price_id = getattr(settings, price_attr, "")
    if not price_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Price ID for {display} plan not configured on the server."
        )

    if not settings.STRIPE_SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Stripe is not configured. Contact support@tariffnavigator.com to upgrade."
        )

    try:
        # ── Org-based subscription ──────────────────────────────────────────
        if current_user.organization_id:
            org = await db.get(Organization, current_user.organization_id)
            if not org:
                raise HTTPException(status_code=404, detail="Organization not found")

            if not org.stripe_customer_id:
                customer = stripe.Customer.create(
                    email=current_user.email,
                    name=org.name,
                    metadata={"organization_id": org.id},
                )
                org.stripe_customer_id = customer.id
                await db.commit()

            session = stripe.checkout.Session.create(
                customer=org.stripe_customer_id,
                payment_method_types=["card"],
                line_items=[{"price": price_id, "quantity": 1}],
                mode="subscription",
                success_url=f"{settings.FRONTEND_URL}/subscription/success?session_id={{CHECKOUT_SESSION_ID}}&plan={plan}",
                cancel_url=f"{settings.FRONTEND_URL}/pricing",
                metadata={"organization_id": org.id, "plan": plan},
            )

        # ── Individual user subscription ────────────────────────────────────
        else:
            # Use user's stripe_customer_id stored in preferences, or create one
            prefs = current_user.preferences or {}
            stripe_customer_id = prefs.get("stripe_customer_id")

            if not stripe_customer_id:
                customer = stripe.Customer.create(
                    email=current_user.email,
                    name=current_user.full_name or current_user.email,
                    metadata={"user_id": current_user.id},
                )
                stripe_customer_id = customer.id
                prefs["stripe_customer_id"] = stripe_customer_id
                current_user.preferences = prefs
                await db.commit()

            session = stripe.checkout.Session.create(
                customer=stripe_customer_id,
                payment_method_types=["card"],
                line_items=[{"price": price_id, "quantity": 1}],
                mode="subscription",
                success_url=f"{settings.FRONTEND_URL}/subscription/success?session_id={{CHECKOUT_SESSION_ID}}&plan={plan}",
                cancel_url=f"{settings.FRONTEND_URL}/pricing",
                metadata={"user_id": current_user.id, "plan": plan},
            )

        logger.info("Created checkout session %s for user %s plan=%s", session.id, current_user.id, plan)
        return {"checkout_url": session.url, "session_id": session.id}

    except stripe.error.StripeError as e:
        logger.error("Stripe error creating checkout session: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Payment provider error: {str(e)}"
        )


@router.get("/current")
async def get_current_subscription(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get current subscription details for user's organization.

    Returns:
        Subscription details or null if no subscription
    """
    if not current_user.organization_id:
        return {"subscription": None}

    org = await db.get(Organization, current_user.organization_id)
    if not org:
        return {"subscription": None}

    # Get subscription if exists
    stmt = select(Subscription).where(Subscription.organization_id == org.id)
    result = await db.execute(stmt)
    subscription = result.scalar_one_or_none()

    if not subscription:
        return {
            "subscription": None,
            "plan": org.plan,
            "status": "free"
        }

    return {
        "subscription": subscription.to_dict(),
        "plan": org.plan,
        "status": subscription.status.value if hasattr(subscription.status, 'value') else subscription.status
    }


@router.post("/cancel")
async def cancel_subscription(
    immediate: bool = Query(False, description="Cancel immediately vs at period end"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Cancel subscription (admin only).

    Args:
        immediate: If True, cancel now. If False, cancel at period end (default).

    Returns:
        Updated subscription details
    """
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must be part of an organization"
        )

    # Get subscription
    stmt = select(Subscription).where(Subscription.organization_id == current_user.organization_id)
    result = await db.execute(stmt)
    subscription = result.scalar_one_or_none()

    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active subscription found"
        )

    try:
        # Cancel in Stripe
        if immediate:
            stripe_sub = stripe.Subscription.delete(subscription.stripe_subscription_id)
            logger.info(f"Immediately canceled subscription {subscription.id}")
        else:
            stripe_sub = stripe.Subscription.modify(
                subscription.stripe_subscription_id,
                cancel_at_period_end=True
            )
            logger.info(f"Scheduled subscription {subscription.id} for cancellation at period end")

        # Update database
        subscription.cancel_at_period_end = stripe_sub.cancel_at_period_end
        if immediate:
            subscription.status = 'canceled'
            subscription.canceled_at = stripe_sub.canceled_at

            # Update organization
            org = await db.get(Organization, current_user.organization_id)
            org.plan = 'free'
            org.subscription_status = 'canceled'

        await db.commit()

        return {
            "subscription": subscription.to_dict(),
            "message": "Subscription canceled immediately" if immediate else "Subscription will cancel at end of billing period"
        }

    except stripe.error.StripeError as e:
        logger.error(f"Stripe error canceling subscription: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Payment provider error: {str(e)}"
        )


@router.get("/billing-portal")
async def get_billing_portal_url(
    return_url: str = Query(..., description="URL to return to after portal session"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Generate Stripe Billing Portal URL (admin only).
    Allows customers to manage payment methods, view invoices, cancel subscription.

    Args:
        return_url: URL to redirect back to after portal session

    Returns:
        url: Stripe Billing Portal URL
    """
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must be part of an organization"
        )

    org = await db.get(Organization, current_user.organization_id)
    if not org or not org.stripe_customer_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization does not have a Stripe customer account"
        )

    try:
        session = stripe.billing_portal.Session.create(
            customer=org.stripe_customer_id,
            return_url=return_url
        )

        logger.info(f"Created billing portal session for org {org.id}")

        return {"url": session.url}

    except stripe.error.StripeError as e:
        logger.error(f"Stripe error creating billing portal: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Payment provider error: {str(e)}"
        )


@router.get("/invoices")
async def list_invoices(
    limit: int = Query(20, ge=1, le=100, description="Number of invoices to return"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    List payment history / invoices for organization (admin only).

    Args:
        limit: Maximum number of invoices to return (1-100)

    Returns:
        List of payment records
    """
    if not current_user.organization_id:
        return {"invoices": [], "total": 0}

    # Get organization's subscription
    stmt = select(Subscription).where(Subscription.organization_id == current_user.organization_id)
    result = await db.execute(stmt)
    subscription = result.scalar_one_or_none()

    if not subscription:
        return {"invoices": [], "total": 0}

    # Get payments
    from sqlalchemy import desc, func

    # Get total count
    count_stmt = select(func.count(Payment.id)).where(Payment.subscription_id == subscription.id)
    count_result = await db.execute(count_stmt)
    total = count_result.scalar()

    # Get payments
    stmt = select(Payment).where(
        Payment.subscription_id == subscription.id
    ).order_by(desc(Payment.created_at)).limit(limit)

    result = await db.execute(stmt)
    payments = result.scalars().all()

    return {
        "invoices": [p.to_dict() for p in payments],
        "total": total
    }


@router.get("/usage")
async def get_usage_statistics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get usage statistics for current organization.

    Returns current usage vs limits for:
    - Monthly calculations
    - Watchlists
    - Saved calculations

    Available to all authenticated users.
    """
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must be part of an organization"
        )

    service = SubscriptionService(db)

    try:
        stats = await service.get_usage_statistics(current_user.organization_id)
        return stats

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error getting usage statistics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve usage statistics"
        )


@router.post("/upgrade")
async def upgrade_subscription(
    new_plan: str = Query(..., description="Target plan to upgrade to"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Upgrade subscription plan (admin only).

    Supports:
    - Free → Pro
    - Free → Enterprise
    - Pro → Enterprise (with proration)

    Args:
        new_plan: Target plan ('pro' or 'enterprise')

    Returns:
        checkout_url for new subscriptions, or success message for upgrades
    """
    if new_plan not in ['pro', 'enterprise']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid plan. Must be 'pro' or 'enterprise'"
        )

    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must be part of an organization"
        )

    service = SubscriptionService(db)

    try:
        result = await service.upgrade_plan(current_user.organization_id, new_plan)

        return result

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error upgrading subscription: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upgrade subscription: {str(e)}"
        )
