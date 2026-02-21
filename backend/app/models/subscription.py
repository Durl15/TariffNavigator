"""
Subscription and Payment Models - Module 3
Tracks organization subscriptions and payment history
"""
from sqlalchemy import Column, String, Numeric, Boolean, DateTime, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum
from app.db.base_class import Base


class SubscriptionStatus(str, enum.Enum):
    """Subscription status enum matching Stripe statuses"""
    ACTIVE = "active"
    CANCELED = "canceled"
    PAST_DUE = "past_due"
    UNPAID = "unpaid"
    TRIALING = "trialing"


class Subscription(Base):
    """
    Organization subscription tracking.
    Maps to Stripe Subscription object.
    One subscription per organization.
    """
    __tablename__ = "subscriptions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = Column(
        String(36),
        ForeignKey('organizations.id', ondelete='CASCADE'),
        nullable=False,
        unique=True,  # One subscription per organization
        index=True
    )

    # Stripe IDs
    stripe_customer_id = Column(String(255), nullable=False, index=True)
    stripe_subscription_id = Column(String(255), nullable=False, unique=True, index=True)
    stripe_price_id = Column(String(255), nullable=False)

    # Subscription details
    status = Column(Enum(SubscriptionStatus), nullable=False, index=True)
    plan = Column(String(50), nullable=False)  # 'pro', 'enterprise'
    current_period_start = Column(DateTime(timezone=True), nullable=False)
    current_period_end = Column(DateTime(timezone=True), nullable=False)
    cancel_at_period_end = Column(Boolean, default=False, nullable=False)
    canceled_at = Column(DateTime(timezone=True), nullable=True)
    trial_end = Column(DateTime(timezone=True), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=datetime.utcnow, nullable=True)

    # Relationships
    organization = relationship("Organization", back_populates="subscription")
    payments = relationship("Payment", back_populates="subscription", cascade="all, delete-orphan")

    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "organization_id": self.organization_id,
            "stripe_customer_id": self.stripe_customer_id,
            "stripe_subscription_id": self.stripe_subscription_id,
            "status": self.status.value if isinstance(self.status, SubscriptionStatus) else self.status,
            "plan": self.plan,
            "current_period_start": self.current_period_start.isoformat() if self.current_period_start else None,
            "current_period_end": self.current_period_end.isoformat() if self.current_period_end else None,
            "cancel_at_period_end": self.cancel_at_period_end,
            "canceled_at": self.canceled_at.isoformat() if self.canceled_at else None,
            "trial_end": self.trial_end.isoformat() if self.trial_end else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Payment(Base):
    """
    Payment history for subscriptions.
    Maps to Stripe Invoice/Charge objects.
    Tracks all payment attempts and successful payments.
    """
    __tablename__ = "payments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    subscription_id = Column(
        String(36),
        ForeignKey('subscriptions.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )

    # Stripe IDs
    stripe_invoice_id = Column(String(255), nullable=True, index=True)
    stripe_charge_id = Column(String(255), nullable=True, index=True)
    stripe_payment_intent_id = Column(String(255), nullable=True, index=True)

    # Payment details
    amount = Column(Numeric(10, 2), nullable=False)  # Amount in dollars
    currency = Column(String(3), nullable=False, default='USD')
    status = Column(String(20), nullable=False, index=True)  # 'paid', 'failed', 'pending'

    # Metadata
    billing_reason = Column(String(50), nullable=True)  # 'subscription_create', 'subscription_cycle'
    invoice_pdf_url = Column(Text, nullable=True)

    # Timestamps
    paid_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    subscription = relationship("Subscription", back_populates="payments")

    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "subscription_id": self.subscription_id,
            "stripe_invoice_id": self.stripe_invoice_id,
            "stripe_charge_id": self.stripe_charge_id,
            "amount": float(self.amount) if self.amount else 0,
            "currency": self.currency,
            "status": self.status,
            "billing_reason": self.billing_reason,
            "invoice_pdf_url": self.invoice_pdf_url,
            "paid_at": self.paid_at.isoformat() if self.paid_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
