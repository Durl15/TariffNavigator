from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.db.base_class import Base


class RateLimit(Base):
    """
    Sliding window rate limiting tracker.
    Stores request counts per identifier (IP or user_id) within time windows.
    """
    __tablename__ = "rate_limits"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    identifier = Column(String(100), nullable=False, index=True)  # IP address or user_id
    identifier_type = Column(String(10), nullable=False, index=True)  # 'ip' or 'user'
    request_count = Column(Integer, nullable=False, default=1)
    window_start = Column(DateTime(timezone=True), nullable=False, index=True)
    window_end = Column(DateTime(timezone=True), nullable=False)
    endpoint = Column(String(255), nullable=True)  # Optional: track per-endpoint
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    # Composite index for fast rate limit checks
    __table_args__ = (
        Index('idx_rate_limit_lookup', 'identifier', 'identifier_type', 'window_start'),
    )

    def __repr__(self):
        return f"<RateLimit {self.identifier_type}:{self.identifier} - {self.request_count} requests>"


class OrganizationQuotaUsage(Base):
    """
    Monthly calculation quota tracking per organization.
    Tracks how many calculations an organization has used in the current month.
    """
    __tablename__ = "organization_quota_usage"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = Column(String(36), ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False, index=True)
    year_month = Column(String(7), nullable=False, index=True)  # Format: "2024-03"
    calculation_count = Column(Integer, nullable=False, default=0)
    quota_limit = Column(Integer, nullable=False)  # Snapshot from Organization.max_calculations_per_month
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=datetime.utcnow, nullable=True)

    # Relationship
    organization = relationship("Organization", back_populates="quota_usage")

    # Unique constraint: one record per organization per month
    __table_args__ = (
        Index('idx_quota_lookup', 'organization_id', 'year_month'),
        {'extend_existing': True}  # Allow redefinition with constraints
    )

    def __repr__(self):
        return f"<OrganizationQuotaUsage org={self.organization_id} {self.year_month}: {self.calculation_count}/{self.quota_limit}>"

    @property
    def percentage_used(self) -> float:
        """Calculate percentage of quota used"""
        if self.quota_limit == 0:
            return 0.0
        return (self.calculation_count / self.quota_limit) * 100

    @property
    def is_exceeded(self) -> bool:
        """Check if quota is exceeded"""
        return self.calculation_count >= self.quota_limit

    @property
    def remaining(self) -> int:
        """Get remaining quota"""
        return max(0, self.quota_limit - self.calculation_count)


class RateLimitViolation(Base):
    """
    Log of rate limit violations for security monitoring and analytics.
    Tracks when and how users exceed rate limits.
    """
    __tablename__ = "rate_limit_violations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    identifier = Column(String(100), nullable=False, index=True)  # IP, user_id, or org_id
    identifier_type = Column(String(10), nullable=False, index=True)  # 'ip', 'user', 'organization'
    user_id = Column(String(36), ForeignKey('users.id', ondelete='SET NULL'), nullable=True, index=True)
    violation_type = Column(String(20), nullable=False, index=True)  # 'ip_rate', 'user_rate', 'quota'
    attempted_count = Column(Integer, nullable=False)  # Number of requests attempted
    limit = Column(Integer, nullable=False)  # The limit that was exceeded
    endpoint = Column(String(255), nullable=True)  # The endpoint being accessed
    user_agent = Column(String(500), nullable=True)  # Browser/client info
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False, index=True)

    def __repr__(self):
        return f"<RateLimitViolation {self.violation_type} - {self.identifier} ({self.attempted_count}/{self.limit})>"

    def to_dict(self):
        return {
            "id": self.id,
            "identifier": self.identifier,
            "identifier_type": self.identifier_type,
            "user_id": self.user_id,
            "violation_type": self.violation_type,
            "attempted_count": self.attempted_count,
            "limit": self.limit,
            "endpoint": self.endpoint,
            "user_agent": self.user_agent,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
