from sqlalchemy import Column, String, Boolean, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.db.base_class import Base


class Watchlist(Base):
    """
    User-defined watchlists for monitoring tariff changes.
    Tracks specific HS codes and countries of interest.
    """
    __tablename__ = "watchlists"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)

    # Metadata
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    # Watch criteria (JSON arrays for flexibility)
    hs_codes = Column(JSON, nullable=True)  # ["8703.23", "8471.30"]
    countries = Column(JSON, nullable=True)  # ["CN", "MX", "CA"]

    # Alert preferences
    alert_preferences = Column(JSON, nullable=True)  # {email: true, digest: 'daily'}

    # Status
    is_active = Column(Boolean, default=True, index=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=datetime.utcnow, nullable=True)

    # Relationships
    user = relationship("User", back_populates="watchlists")

    def __repr__(self):
        return f"<Watchlist {self.id}: {self.name} (active={self.is_active})>"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "hs_codes": self.hs_codes or [],
            "countries": self.countries or [],
            "alert_preferences": self.alert_preferences,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def matches_change(self, hs_code: str, country: str) -> bool:
        """
        Check if this watchlist should be alerted for a given change.
        """
        hs_match = not self.hs_codes or hs_code in self.hs_codes
        country_match = not self.countries or country in self.countries
        return self.is_active and hs_match and country_match
