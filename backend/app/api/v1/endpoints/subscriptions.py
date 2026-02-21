"""
Subscription Management Endpoints - Module 3 Phase 2/4
Handles Stripe Checkout, subscription management, and billing
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
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

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


@router.post("/checkout/create-session")
async def create_checkout_session(
    plan: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Create Stripe Checkout session for subscription upgrade.
    Requires admin role (only org admins can manage subscriptions).

    Args:
        plan: 'pro' or 'enterprise'

    Returns:
        checkout_url: Stripe Checkout URL to redirect user to
    """
    # Validate plan
    if plan not in ['pro', 'enterprise']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid plan. Must be 'pro' or 'enterprise'"
        )

    # Check if user has organization
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must be part of an organization to subscribe"
        )

    # Get organization
    org = await db.get(Organization, current_user.organization_id)
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )

    # Check if already has active subscription
    if org.subscription_status == 'active':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization already has an active subscription. Use upgrade endpoint to change plans."
        )

    try:
        # Get or create Stripe customer
        if not org.stripe_customer_id:
            customer = stripe.Customer.create(
                email=current_user.email,
                name=org.name,
                metadata={
                    "organization_id": org.id,
                    "organization_name": org.name
                }
            )
            org.stripe_customer_id = customer.id
            await db.commit()
            logger.info(f"Created Stripe customer {customer.id} for org {org.id}")

        # Select price ID based on plan
        price_id = (
            settings.STRIPE_PRICE_ID_PRO if plan == 'pro'
            else settings.STRIPE_PRICE_ID_ENTERPRISE
        )

        if not price_id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Price ID for {plan} plan not configured"
            )

        # Create Stripe Checkout session
        session = stripe.checkout.Session.create(
            customer=org.stripe_customer_id,
            payment_method_types=['card'],
            line_items=[{
                'price': price_id,
                'quantity': 1,
            }],
            mode='subscription',
            success_url=f"{settings.FRONTEND_URL}/subscription/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{settings.FRONTEND_URL}/pricing",
            metadata={
                "organization_id": org.id,
                "plan": plan
            }
        )

        logger.info(f"Created checkout session {session.id} for org {org.id}, plan {plan}")

        return {
            "checkout_url": session.url,
            "session_id": session.id
        }

    except stripe.error.StripeError as e:
        logger.error(f"Stripe error creating checkout session: {str(e)}")
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
