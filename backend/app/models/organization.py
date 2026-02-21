from sqlalchemy import Column, String, Integer, Boolean, DateTime, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.db.base_class import Base


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    slug = Column(String(100), nullable=False, unique=True, index=True)
    plan = Column(String(50), nullable=False, default='free')  # free, pro, enterprise
    status = Column(String(50), nullable=False, default='active', index=True)  # active, suspended, deleted
    max_users = Column(Integer, nullable=False, default=5)
    max_calculations_per_month = Column(Integer, nullable=False, default=100)
    settings = Column(JSON, nullable=True)  # Custom organization settings

    # Stripe integration (Module 3)
    stripe_customer_id = Column(String(255), nullable=True, unique=True, index=True)
    subscription_status = Column(String(20), nullable=True, index=True)  # Cache of subscription status

    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=datetime.utcnow, nullable=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)  # Soft delete

    # Relationships
    quota_usage = relationship("OrganizationQuotaUsage", back_populates="organization", cascade="all, delete-orphan")
    subscription = relationship("Subscription", back_populates="organization", uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Organization {self.name} ({self.plan})>"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "slug": self.slug,
            "plan": self.plan,
            "status": self.status,
            "max_users": self.max_users,
            "max_calculations_per_month": self.max_calculations_per_month,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
