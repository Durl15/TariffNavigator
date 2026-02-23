"""
Subscription Service - Module 3 Phase 4
Centralized business logic for subscription management
"""
import stripe
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from decimal import Decimal

from app.models.subscription import Subscription, Payment, SubscriptionStatus
from app.models.organization import Organization
from app.models.rate_limit import OrganizationQuotaUsage
from app.models.watchlist import Watchlist
from app.models.calculation import Calculation
from app.core.config import settings
from app.core.subscription_features import get_quota_limit, get_plan_quotas

logger = logging.getLogger(__name__)

# Initialize Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


class SubscriptionService:
    """Service for managing subscriptions and billing"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_subscription_by_org_id(self, organization_id: str) -> Optional[Subscription]:
        """
        Get subscription for an organization.

        Args:
            organization_id: Organization ID

        Returns:
            Subscription object or None
        """
        stmt = select(Subscription).where(Subscription.organization_id == organization_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_usage_statistics(self, organization_id: str) -> Dict[str, Any]:
        """
        Calculate usage statistics for an organization.

        Returns current usage vs limits for all quota types:
        - Calculations (monthly)
        - Watchlists (total)
        - Saved calculations (total)

        Args:
            organization_id: Organization ID

        Returns:
            Dict with usage stats, percentages, and warnings
        """
        org = await self.db.get(Organization, organization_id)
        if not org:
            raise ValueError("Organization not found")

        plan = org.plan
        quotas = get_plan_quotas(plan)

        # Get current month for calculation quota
        current_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        next_month = (current_month + timedelta(days=32)).replace(day=1)

        # 1. Calculations usage (monthly)
        stmt = select(OrganizationQuotaUsage).where(
            OrganizationQuotaUsage.organization_id == organization_id,
            OrganizationQuotaUsage.month_start == current_month
        )
        result = await self.db.execute(stmt)
        quota_usage = result.scalar_one_or_none()

        calculations_used = quota_usage.calculations_used if quota_usage else 0
        calculations_limit = quotas.get('calculations_per_month', 0)
        calculations_percentage = (calculations_used / calculations_limit * 100) if calculations_limit > 0 else 0

        # 2. Watchlists usage
        stmt = select(func.count(Watchlist.id)).where(
            Watchlist.user_id.in_(
                select(Organization.id).where(Organization.id == organization_id)
            )
        )
        # Actually, watchlists are per user, let me fix this
        # Get all users in org and count their watchlists
        from app.models.user import User

        stmt = select(func.count(Watchlist.id)).join(
            User, Watchlist.user_id == User.id
        ).where(User.organization_id == organization_id)
        result = await self.db.execute(stmt)
        watchlists_used = result.scalar() or 0
        watchlists_limit = quotas.get('watchlists', 0)
        watchlists_percentage = (watchlists_used / watchlists_limit * 100) if watchlists_limit > 0 and watchlists_limit < 999999 else 0

        # 3. Saved calculations usage
        stmt = select(func.count(Calculation.id)).join(
            User, Calculation.user_id == User.id
        ).where(User.organization_id == organization_id)
        result = await self.db.execute(stmt)
        saved_calcs_used = result.scalar() or 0
        saved_calcs_limit = quotas.get('saved_calculations', 0)
        saved_calcs_percentage = (saved_calcs_used / saved_calcs_limit * 100) if saved_calcs_limit > 0 and saved_calcs_limit < 999999 else 0

        # Calculate days until reset
        days_until_reset = (next_month - datetime.utcnow()).days

        return {
            "plan": plan,
            "calculations": {
                "used": calculations_used,
                "limit": calculations_limit,
                "percentage": round(calculations_percentage, 1),
                "warning": calculations_percentage >= 80,
                "exceeded": calculations_used >= calculations_limit,
                "resets_in_days": days_until_reset,
                "reset_date": next_month.isoformat()
            },
            "watchlists": {
                "used": watchlists_used,
                "limit": watchlists_limit,
                "percentage": round(watchlists_percentage, 1),
                "warning": watchlists_percentage >= 80,
                "exceeded": watchlists_used >= watchlists_limit,
                "unlimited": watchlists_limit >= 999999
            },
            "saved_calculations": {
                "used": saved_calcs_used,
                "limit": saved_calcs_limit,
                "percentage": round(saved_calcs_percentage, 1),
                "warning": saved_calcs_percentage >= 80,
                "exceeded": saved_calcs_used >= saved_calcs_limit,
                "unlimited": saved_calcs_limit >= 999999
            }
        }

    async def upgrade_plan(self, organization_id: str, new_plan: str) -> Dict[str, Any]:
        """
        Upgrade subscription plan (e.g., pro → enterprise).

        Creates new Stripe checkout session with proration.

        Args:
            organization_id: Organization ID
            new_plan: Target plan ('enterprise')

        Returns:
            Dict with checkout URL or error

        Raises:
            ValueError: If upgrade not allowed
        """
        org = await self.db.get(Organization, organization_id)
        if not org:
            raise ValueError("Organization not found")

        current_plan = org.plan

        # Validate upgrade path
        if current_plan == 'free' and new_plan in ['pro', 'enterprise']:
            # Free → Pro/Enterprise: Use regular checkout
            return await self._create_checkout_session(org, new_plan)
        elif current_plan == 'pro' and new_plan == 'enterprise':
            # Pro → Enterprise: Upgrade existing subscription
            return await self._upgrade_existing_subscription(org, new_plan)
        elif current_plan == new_plan:
            raise ValueError(f"Already on {new_plan} plan")
        else:
            raise ValueError(f"Cannot upgrade from {current_plan} to {new_plan}")

    async def _create_checkout_session(self, org: Organization, plan: str) -> Dict[str, Any]:
        """Create new Stripe checkout session"""
        # Get or create Stripe customer
        if not org.stripe_customer_id:
            customer = stripe.Customer.create(
                email=org.name,  # Would need user email here
                name=org.name,
                metadata={
                    "organization_id": org.id,
                    "organization_name": org.name
                }
            )
            org.stripe_customer_id = customer.id
            await self.db.commit()

        # Select price ID
        price_id = (
            settings.STRIPE_PRICE_ID_PRO if plan == 'pro'
            else settings.STRIPE_PRICE_ID_ENTERPRISE
        )

        if not price_id:
            raise ValueError(f"Price ID for {plan} not configured")

        # Create checkout session
        session = stripe.checkout.Session.create(
            customer=org.stripe_customer_id,
            payment_method_types=['card'],
            line_items=[{'price': price_id, 'quantity': 1}],
            mode='subscription',
            success_url=f"{settings.FRONTEND_URL}/subscription/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{settings.FRONTEND_URL}/billing",
            metadata={
                "organization_id": org.id,
                "plan": plan
            }
        )

        return {
            "checkout_url": session.url,
            "session_id": session.id
        }

    async def _upgrade_existing_subscription(self, org: Organization, new_plan: str) -> Dict[str, Any]:
        """Upgrade existing subscription with proration"""
        subscription = await self.get_subscription_by_org_id(org.id)

        if not subscription:
            raise ValueError("No active subscription found")

        # Get new price ID
        price_id = settings.STRIPE_PRICE_ID_ENTERPRISE if new_plan == 'enterprise' else None

        if not price_id:
            raise ValueError(f"Price ID for {new_plan} not configured")

        try:
            # Retrieve current Stripe subscription
            stripe_sub = stripe.Subscription.retrieve(subscription.stripe_subscription_id)

            # Update subscription with proration
            updated_sub = stripe.Subscription.modify(
                subscription.stripe_subscription_id,
                items=[{
                    'id': stripe_sub['items']['data'][0].id,
                    'price': price_id,
                }],
                proration_behavior='always_invoice',  # Create invoice for prorated amount
            )

            # Update database
            subscription.stripe_price_id = price_id
            subscription.plan = new_plan
            org.plan = new_plan

            # Update quotas
            if new_plan == 'enterprise':
                org.max_calculations_per_month = 10000

            await self.db.commit()

            logger.info(f"Upgraded subscription {subscription.id} to {new_plan}")

            return {
                "success": True,
                "message": f"Successfully upgraded to {new_plan}",
                "subscription": subscription.to_dict()
            }

        except stripe.error.StripeError as e:
            logger.error(f"Stripe error upgrading subscription: {str(e)}")
            raise ValueError(f"Payment provider error: {str(e)}")

    async def cancel_subscription(
        self,
        organization_id: str,
        immediate: bool = False
    ) -> Dict[str, Any]:
        """
        Cancel subscription.

        Args:
            organization_id: Organization ID
            immediate: Cancel immediately vs at period end

        Returns:
            Updated subscription details
        """
        subscription = await self.get_subscription_by_org_id(organization_id)

        if not subscription:
            raise ValueError("No active subscription found")

        try:
            if immediate:
                stripe_sub = stripe.Subscription.delete(subscription.stripe_subscription_id)
                subscription.status = SubscriptionStatus.CANCELED
                subscription.canceled_at = datetime.utcnow()

                # Downgrade organization
                org = await self.db.get(Organization, organization_id)
                org.plan = 'free'
                org.subscription_status = 'canceled'
                org.max_calculations_per_month = 100

                message = "Subscription canceled immediately"
            else:
                stripe_sub = stripe.Subscription.modify(
                    subscription.stripe_subscription_id,
                    cancel_at_period_end=True
                )
                subscription.cancel_at_period_end = True

                message = "Subscription will cancel at end of billing period"

            await self.db.commit()

            logger.info(f"Canceled subscription {subscription.id} (immediate={immediate})")

            return {
                "subscription": subscription.to_dict(),
                "message": message
            }

        except stripe.error.StripeError as e:
            logger.error(f"Stripe error canceling subscription: {str(e)}")
            raise ValueError(f"Payment provider error: {str(e)}")

    async def get_revenue_summary(self) -> Dict[str, Any]:
        """
        Calculate revenue metrics (admin only).

        Returns:
            MRR, total revenue, active subscriptions count
        """
        # Count active subscriptions
        stmt = select(func.count(Subscription.id)).where(
            Subscription.status == SubscriptionStatus.ACTIVE
        )
        result = await self.db.execute(stmt)
        active_subs = result.scalar() or 0

        # Calculate MRR from active subscriptions
        stmt = select(Subscription).where(Subscription.status == SubscriptionStatus.ACTIVE)
        result = await self.db.execute(stmt)
        subscriptions = result.scalars().all()

        mrr = Decimal('0')
        for sub in subscriptions:
            if sub.plan == 'pro':
                mrr += Decimal('49.00')
            elif sub.plan == 'enterprise':
                mrr += Decimal('199.00')

        # Calculate total revenue from payments
        stmt = select(func.sum(Payment.amount)).where(Payment.status == 'paid')
        result = await self.db.execute(stmt)
        total_revenue = result.scalar() or Decimal('0')

        # Get current month revenue
        current_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        stmt = select(func.sum(Payment.amount)).where(
            Payment.status == 'paid',
            Payment.created_at >= current_month
        )
        result = await self.db.execute(stmt)
        month_revenue = result.scalar() or Decimal('0')

        return {
            "mrr": float(mrr),
            "total_revenue": float(total_revenue),
            "month_revenue": float(month_revenue),
            "active_subscriptions": active_subs,
            "currency": "USD"
        }
