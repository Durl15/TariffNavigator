"""
Webhook Service - Module 3 Phase 2
Processes Stripe webhook events and updates database
"""
import stripe
import logging
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid

from app.models.subscription import Subscription, Payment, SubscriptionStatus
from app.models.organization import Organization
from app.models.user import User
from app.services.email_service import email_service

logger = logging.getLogger(__name__)


class WebhookService:
    """
    Processes Stripe webhook events.
    Handles subscription lifecycle and payment events.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def handle_event(self, event: stripe.Event):
        """
        Route webhook events to appropriate handlers.

        Args:
            event: Stripe Event object
        """
        handlers = {
            'customer.subscription.created': self.handle_subscription_created,
            'customer.subscription.updated': self.handle_subscription_updated,
            'customer.subscription.deleted': self.handle_subscription_deleted,
            'invoice.paid': self.handle_invoice_paid,
            'invoice.payment_failed': self.handle_payment_failed,
        }

        handler = handlers.get(event.type)
        if handler:
            await handler(event.data.object)
        else:
            logger.info(f"No handler for event type: {event.type}")

    async def handle_subscription_created(self, stripe_subscription):
        """
        Handle new subscription creation.

        Creates Subscription record and updates Organization.
        """
        org_id = stripe_subscription.metadata.get('organization_id')
        plan = stripe_subscription.metadata.get('plan')

        if not org_id or not plan:
            logger.error(f"Missing metadata in subscription {stripe_subscription.id}")
            return

        # Check if subscription already exists
        stmt = select(Subscription).where(
            Subscription.stripe_subscription_id == stripe_subscription.id
        )
        result = await self.db.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing:
            logger.warning(f"Subscription {stripe_subscription.id} already exists")
            return

        # Create Subscription record
        subscription = Subscription(
            id=str(uuid.uuid4()),
            organization_id=org_id,
            stripe_customer_id=stripe_subscription.customer,
            stripe_subscription_id=stripe_subscription.id,
            stripe_price_id=stripe_subscription.items.data[0].price.id,
            status=SubscriptionStatus.ACTIVE,
            plan=plan,
            current_period_start=datetime.fromtimestamp(stripe_subscription.current_period_start),
            current_period_end=datetime.fromtimestamp(stripe_subscription.current_period_end),
            cancel_at_period_end=stripe_subscription.cancel_at_period_end,
            trial_end=datetime.fromtimestamp(stripe_subscription.trial_end) if stripe_subscription.trial_end else None
        )

        self.db.add(subscription)

        # Update organization
        org = await self.db.get(Organization, org_id)
        if org:
            org.plan = plan
            org.subscription_status = 'active'

            # Update quotas based on plan
            if plan == 'pro':
                org.max_calculations_per_month = 1000
            elif plan == 'enterprise':
                org.max_calculations_per_month = 10000

        await self.db.commit()

        logger.info(f"Created subscription {subscription.id} for org {org_id}, plan {plan}")

        # Send welcome email to organization admin
        try:
            # Get organization admin user
            stmt = select(User).where(
                User.organization_id == org_id,
                User.role.in_(['admin', 'superadmin'])
            ).limit(1)
            result = await self.db.execute(stmt)
            admin_user = result.scalar_one_or_none()

            if admin_user and admin_user.email:
                calculations_limit = 1000 if plan == 'pro' else 10000
                next_billing = subscription.current_period_end.strftime('%B %d, %Y')

                await email_service.send_subscription_created_email(
                    to_email=admin_user.email,
                    user_name=admin_user.full_name or admin_user.email,
                    plan=plan,
                    organization_name=org.name,
                    next_billing_date=next_billing,
                    calculations_limit=calculations_limit
                )
                logger.info(f"Sent subscription created email to {admin_user.email}")
        except Exception as e:
            # Don't fail webhook if email fails
            logger.error(f"Failed to send subscription created email: {str(e)}")

    async def handle_subscription_updated(self, stripe_subscription):
        """
        Handle subscription updates (plan changes, renewals).

        Updates Subscription record and Organization plan.
        """
        # Get existing subscription
        subscription = await self.get_subscription_by_stripe_id(stripe_subscription.id)

        if not subscription:
            logger.error(f"Subscription {stripe_subscription.id} not found in database")
            return

        # Update subscription fields
        subscription.status = self._map_stripe_status(stripe_subscription.status)
        subscription.current_period_start = datetime.fromtimestamp(stripe_subscription.current_period_start)
        subscription.current_period_end = datetime.fromtimestamp(stripe_subscription.current_period_end)
        subscription.cancel_at_period_end = stripe_subscription.cancel_at_period_end

        if stripe_subscription.canceled_at:
            subscription.canceled_at = datetime.fromtimestamp(stripe_subscription.canceled_at)

        # Check for plan change
        new_price_id = stripe_subscription.items.data[0].price.id
        if new_price_id != subscription.stripe_price_id:
            subscription.stripe_price_id = new_price_id
            # Could determine plan from price_id or metadata
            logger.info(f"Plan changed for subscription {subscription.id}")

        # Update organization status
        org = subscription.organization
        if org:
            org.subscription_status = subscription.status.value if hasattr(subscription.status, 'value') else subscription.status

        await self.db.commit()

        logger.info(f"Updated subscription {subscription.id}, status: {subscription.status}")

    async def handle_subscription_deleted(self, stripe_subscription):
        """
        Handle subscription cancellation.

        Downgrades organization to free plan.
        """
        subscription = await self.get_subscription_by_stripe_id(stripe_subscription.id)

        if not subscription:
            logger.error(f"Subscription {stripe_subscription.id} not found")
            return

        # Update subscription
        subscription.status = SubscriptionStatus.CANCELED
        subscription.canceled_at = datetime.utcnow()

        # Downgrade organization to free plan
        org = subscription.organization
        if org:
            org.plan = 'free'
            org.subscription_status = 'canceled'
            org.max_calculations_per_month = 100  # Free tier limit

        await self.db.commit()

        logger.info(f"Subscription {subscription.id} canceled, org downgraded to free")

        # Send cancellation confirmation email
        try:
            stmt = select(User).where(
                User.organization_id == subscription.organization_id,
                User.role.in_(['admin', 'superadmin'])
            ).limit(1)
            result = await self.db.execute(stmt)
            admin_user = result.scalar_one_or_none()

            if admin_user and admin_user.email:
                access_until = subscription.current_period_end.strftime('%B %d, %Y') if subscription.current_period_end else "now"

                await email_service.send_subscription_canceled_email(
                    to_email=admin_user.email,
                    user_name=admin_user.full_name or admin_user.email,
                    plan=subscription.plan,
                    access_until=access_until
                )
                logger.info(f"Sent subscription canceled email to {admin_user.email}")
        except Exception as e:
            logger.error(f"Failed to send subscription canceled email: {str(e)}")

    async def handle_invoice_paid(self, invoice):
        """
        Handle successful payment.

        Creates Payment record and updates subscription status.
        """
        if not invoice.subscription:
            logger.info(f"Invoice {invoice.id} not related to subscription, skipping")
            return

        # Get subscription
        subscription = await self.get_subscription_by_stripe_id(invoice.subscription)

        if not subscription:
            logger.error(f"Subscription {invoice.subscription} not found for invoice {invoice.id}")
            return

        # Create Payment record
        payment = Payment(
            id=str(uuid.uuid4()),
            subscription_id=subscription.id,
            stripe_invoice_id=invoice.id,
            stripe_charge_id=invoice.charge,
            stripe_payment_intent_id=invoice.payment_intent,
            amount=invoice.amount_paid / 100,  # Convert cents to dollars
            currency=invoice.currency.upper(),
            status='paid',
            billing_reason=invoice.billing_reason,
            invoice_pdf_url=invoice.invoice_pdf,
            paid_at=datetime.fromtimestamp(invoice.status_transitions.paid_at) if invoice.status_transitions.paid_at else None,
            created_at=datetime.fromtimestamp(invoice.created)
        )

        self.db.add(payment)

        # Update subscription status to active
        subscription.status = SubscriptionStatus.ACTIVE

        # Update organization
        org = subscription.organization
        if org:
            org.subscription_status = 'active'

        await self.db.commit()

        logger.info(f"Recorded payment {payment.id} for subscription {subscription.id}, amount: ${payment.amount}")

    async def handle_payment_failed(self, invoice):
        """
        Handle failed payment.

        Updates subscription status to past_due and sends notification.
        """
        if not invoice.subscription:
            return

        subscription = await self.get_subscription_by_stripe_id(invoice.subscription)

        if not subscription:
            logger.error(f"Subscription {invoice.subscription} not found")
            return

        # Update subscription status
        subscription.status = SubscriptionStatus.PAST_DUE

        # Update organization
        org = subscription.organization
        if org:
            org.subscription_status = 'past_due'

            # After 3 failed attempts, suspend organization
            if invoice.attempt_count >= 3:
                org.status = 'suspended'
                logger.warning(f"Organization {org.id} suspended after {invoice.attempt_count} failed payments")

        await self.db.commit()

        logger.warning(f"Payment failed for subscription {subscription.id}, attempt {invoice.attempt_count}")

        # Send payment failed email
        try:
            stmt = select(User).where(
                User.organization_id == subscription.organization_id,
                User.role.in_(['admin', 'superadmin'])
            ).limit(1)
            result = await self.db.execute(stmt)
            admin_user = result.scalar_one_or_none()

            if admin_user and admin_user.email:
                amount = invoice.amount_due / 100  # Convert cents to dollars
                billing_date = datetime.fromtimestamp(invoice.created).strftime('%B %d, %Y')

                await email_service.send_payment_failed_email(
                    to_email=admin_user.email,
                    user_name=admin_user.full_name or admin_user.email,
                    plan=subscription.plan,
                    amount=amount,
                    attempt_count=invoice.attempt_count,
                    billing_date=billing_date
                )
                logger.info(f"Sent payment failed email to {admin_user.email}")
        except Exception as e:
            logger.error(f"Failed to send payment failed email: {str(e)}")

    async def get_subscription_by_stripe_id(self, stripe_subscription_id: str) -> Subscription:
        """
        Get subscription by Stripe subscription ID.

        Args:
            stripe_subscription_id: Stripe subscription ID

        Returns:
            Subscription object or None
        """
        stmt = select(Subscription).where(
            Subscription.stripe_subscription_id == stripe_subscription_id
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    def _map_stripe_status(self, stripe_status: str) -> SubscriptionStatus:
        """
        Map Stripe subscription status to our enum.

        Args:
            stripe_status: Stripe status string

        Returns:
            SubscriptionStatus enum value
        """
        status_map = {
            'active': SubscriptionStatus.ACTIVE,
            'canceled': SubscriptionStatus.CANCELED,
            'past_due': SubscriptionStatus.PAST_DUE,
            'unpaid': SubscriptionStatus.UNPAID,
            'trialing': SubscriptionStatus.TRIALING,
        }
        return status_map.get(stripe_status, SubscriptionStatus.ACTIVE)
