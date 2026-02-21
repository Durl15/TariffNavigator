"""
Webhook Endpoints - Module 3 Phase 2
Handles Stripe webhook events for subscription management
"""
from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import stripe
import logging

from app.db.session import async_session
from app.core.config import settings
from app.services.webhook_service import WebhookService

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


@router.post("/stripe")
async def stripe_webhook(request: Request):
    """
    Handle Stripe webhook events.

    Critical events handled:
    - customer.subscription.created: New subscription
    - customer.subscription.updated: Plan changes, renewals
    - customer.subscription.deleted: Cancellation
    - invoice.paid: Successful payment
    - invoice.payment_failed: Failed payment

    Security: Verifies webhook signature to prevent spoofing
    """
    # Get raw body for signature verification
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')

    if not sig_header:
        logger.warning("Webhook received without signature header")
        raise HTTPException(status_code=400, detail="Missing signature header")

    # Verify webhook signature
    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        logger.error(f"Invalid webhook payload: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Invalid webhook signature: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid signature")

    # Log webhook event
    logger.info(f"Received webhook event: {event.type} (id: {event.id})")

    # Process webhook event
    async with async_session() as db:
        service = WebhookService(db)
        try:
            await service.handle_event(event)
            logger.info(f"Successfully processed webhook {event.type}")
        except Exception as e:
            logger.error(f"Error processing webhook {event.type}: {str(e)}", exc_info=True)
            # Don't raise exception - Stripe will retry failed webhooks
            # Return 200 to acknowledge receipt but log the error

    return {"status": "success", "event_type": event.type}
