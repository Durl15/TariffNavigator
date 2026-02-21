"""
Stripe Service - Module 3 Phase 1
Basic Stripe API wrapper for customer and subscription management
"""
import stripe
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)


class StripeService:
    """
    Wrapper for Stripe API operations.
    Centralizes Stripe SDK calls for better error handling and logging.
    """

    def __init__(self):
        """Initialize Stripe API with secret key"""
        stripe.api_key = settings.STRIPE_SECRET_KEY
        if not stripe.api_key:
            logger.warning("STRIPE_SECRET_KEY not set - Stripe functionality will not work")

    def create_customer(self, email: str, organization_id: str, name: str = None) -> stripe.Customer:
        """
        Create a Stripe customer.

        Args:
            email: Customer email address
            organization_id: Organization ID for metadata
            name: Optional customer name

        Returns:
            Stripe Customer object
        """
        try:
            customer_data = {
                "email": email,
                "metadata": {"organization_id": organization_id}
            }
            if name:
                customer_data["name"] = name

            customer = stripe.Customer.create(**customer_data)
            logger.info(f"Created Stripe customer {customer.id} for organization {organization_id}")
            return customer

        except stripe.error.StripeError as e:
            logger.error(f"Stripe error creating customer: {str(e)}")
            raise

    def create_subscription(
        self,
        customer_id: str,
        price_id: str,
        metadata: dict = None
    ) -> stripe.Subscription:
        """
        Create a Stripe subscription.

        Args:
            customer_id: Stripe customer ID
            price_id: Stripe price ID
            metadata: Optional metadata dictionary

        Returns:
            Stripe Subscription object
        """
        try:
            subscription_data = {
                "customer": customer_id,
                "items": [{"price": price_id}],
                "payment_behavior": "default_incomplete",
                "expand": ["latest_invoice.payment_intent"]
            }

            if metadata:
                subscription_data["metadata"] = metadata

            subscription = stripe.Subscription.create(**subscription_data)
            logger.info(f"Created Stripe subscription {subscription.id} for customer {customer_id}")
            return subscription

        except stripe.error.StripeError as e:
            logger.error(f"Stripe error creating subscription: {str(e)}")
            raise

    def cancel_subscription(
        self,
        subscription_id: str,
        immediately: bool = False
    ) -> stripe.Subscription:
        """
        Cancel a Stripe subscription.

        Args:
            subscription_id: Stripe subscription ID
            immediately: If True, cancel immediately. If False, cancel at period end.

        Returns:
            Stripe Subscription object
        """
        try:
            if immediately:
                subscription = stripe.Subscription.delete(subscription_id)
                logger.info(f"Immediately canceled subscription {subscription_id}")
            else:
                subscription = stripe.Subscription.modify(
                    subscription_id,
                    cancel_at_period_end=True
                )
                logger.info(f"Scheduled subscription {subscription_id} for cancellation at period end")

            return subscription

        except stripe.error.StripeError as e:
            logger.error(f"Stripe error canceling subscription: {str(e)}")
            raise

    def retrieve_subscription(self, subscription_id: str) -> stripe.Subscription:
        """
        Retrieve a Stripe subscription.

        Args:
            subscription_id: Stripe subscription ID

        Returns:
            Stripe Subscription object
        """
        try:
            subscription = stripe.Subscription.retrieve(subscription_id)
            return subscription

        except stripe.error.StripeError as e:
            logger.error(f"Stripe error retrieving subscription: {str(e)}")
            raise

    def update_subscription(
        self,
        subscription_id: str,
        price_id: str = None,
        metadata: dict = None
    ) -> stripe.Subscription:
        """
        Update a Stripe subscription (e.g., change plan).

        Args:
            subscription_id: Stripe subscription ID
            price_id: New price ID (for plan changes)
            metadata: Optional metadata to update

        Returns:
            Stripe Subscription object
        """
        try:
            update_data = {}

            if price_id:
                # Get current subscription to get item ID
                sub = stripe.Subscription.retrieve(subscription_id)
                item_id = sub['items']['data'][0].id
                update_data['items'] = [{
                    'id': item_id,
                    'price': price_id,
                }]

            if metadata:
                update_data['metadata'] = metadata

            subscription = stripe.Subscription.modify(subscription_id, **update_data)
            logger.info(f"Updated subscription {subscription_id}")
            return subscription

        except stripe.error.StripeError as e:
            logger.error(f"Stripe error updating subscription: {str(e)}")
            raise

    def test_connection(self) -> bool:
        """
        Test Stripe API connection.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            # Try to list customers (limited to 1 for efficiency)
            stripe.Customer.list(limit=1)
            logger.info("Stripe API connection successful")
            return True

        except stripe.error.AuthenticationError:
            logger.error("Stripe authentication failed - check API key")
            return False
        except stripe.error.StripeError as e:
            logger.error(f"Stripe connection test failed: {str(e)}")
            return False


# Global instance
stripe_service = StripeService()
